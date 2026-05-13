import speech_recognition as sr
import pyaudio
import threading
import numpy as np
import time
import base64
import json
import urllib
import requests
from PyQt5.QtCore import QObject, pyqtSignal
from config.config import BAIDU_ASR_CONFIG, LANGUAGE_MODELS
from modules.smart_assistant import SmartAssistant

class VoiceRecognizer(QObject):
    voice_detected = pyqtSignal(str)
    recording_state_changed = pyqtSignal(bool)
    assistant_response = pyqtSignal(list)
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    SILENCE_THRESHOLD = 150
    MIN_AUDIO_DURATION = 0.3
    
    def __init__(self, command_system, logger):
        super().__init__()
        self.command_system = command_system
        self.logger = logger
        
        self._pyaudio_instance = None
        self._stream = None
        self._is_recording = False
        self._audio_frames = []
        self._recording_start_time = 0
        self._min_frames = 0
        self._access_token = None
        self._token_expire_time = 0
        self._current_language = 'mandarin'
        self._current_dev_pid = LANGUAGE_MODELS['mandarin']['dev_pid']
        
        self.smart_assistant = SmartAssistant(logger)
        
        try:
            self._pyaudio_instance = pyaudio.PyAudio()
            self.logger.info("麦克风初始化成功")
        except Exception as e:
            self.logger.error(f"麦克风初始化失败: {str(e)}")
    
    def get_language_list(self):
        return LANGUAGE_MODELS
    
    def set_language(self, language_key):
        if language_key in LANGUAGE_MODELS:
            self._current_language = language_key
            self._current_dev_pid = LANGUAGE_MODELS[language_key]['dev_pid']
            lang_info = LANGUAGE_MODELS[language_key]
            self.logger.info(f"语言切换成功: {lang_info['name']} (dev_pid: {self._current_dev_pid})")
            return True
        else:
            self.logger.error(f"不支持的语言: {language_key}")
            return False
    
    def get_current_language(self):
        return self._current_language, LANGUAGE_MODELS[self._current_language]
    
    def _get_access_token(self):
        now = time.time()
        if self._access_token and now < self._token_expire_time:
            return self._access_token
        
        api_key = BAIDU_ASR_CONFIG['API_KEY']
        secret_key = BAIDU_ASR_CONFIG['SECRET_KEY']
        
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
        
        try:
            response = requests.get(url)
            result = response.json()
            
            if 'access_token' in result:
                self._access_token = result['access_token']
                self._token_expire_time = now + result.get('expires_in', 3600) - 60
                self.logger.info(f"获取百度API Token成功，有效期: {result.get('expires_in', 3600)}秒")
                return self._access_token
            else:
                self.logger.error(f"获取Token失败: {result.get('error_description', '未知错误')}")
                return None
        except Exception as e:
            self.logger.error(f"获取Token异常: {str(e)}")
            return None
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        if self._is_recording:
            self._audio_frames.append(in_data)
        return (in_data, pyaudio.paContinue)
    
    def start_recording(self) -> bool:
        if not self._pyaudio_instance:
            self.logger.error("音频设备不可用")
            return False
        
        if self._is_recording:
            self.logger.warning("已在录音中")
            return False
        
        self._is_recording = True
        self._audio_frames = []
        self._min_frames = int(self.RATE / self.CHUNK * self.MIN_AUDIO_DURATION)
        self._recording_start_time = time.time()
        self.recording_state_changed.emit(True)
        self.logger.info("开始录音...")
        
        try:
            self._stream = self._pyaudio_instance.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
                stream_callback=self._audio_callback
            )
            self._stream.start_stream()
            self.logger.info(f"录音流已启动，采样率: {self.RATE}Hz")
        except Exception as e:
            self.logger.error(f"录音启动失败: {str(e)}")
            self._is_recording = False
            self.recording_state_changed.emit(False)
            return False
        
        return True
    
    def stop_recording(self) -> bool:
        if not self._is_recording:
            return False
        
        recording_duration = time.time() - self._recording_start_time
        self._is_recording = False
        self.logger.info(f"停止录音，录音时长: {recording_duration:.2f}秒，帧数: {len(self._audio_frames)}")
        
        try:
            if self._stream:
                self._stream.stop_stream()
                self._stream.close()
                self._stream = None
            
            if len(self._audio_frames) < self._min_frames:
                self.logger.warning(f"录音帧数太少 ({len(self._audio_frames)})，忽略")
                self.recording_state_changed.emit(False)
                return False
            
            audio_data = b''.join(self._audio_frames)
            self.logger.info(f"音频数据大小: {len(audio_data)} bytes")
            
            processed_audio = self._process_audio_data(audio_data)
            if processed_audio is None:
                self.logger.warning("音频处理失败")
                self.recording_state_changed.emit(False)
                return False
            
            self.logger.info("开始识别...")
            threading.Thread(target=self._process_audio, args=(processed_audio,)).start()
            
        except Exception as e:
            self.logger.error(f"停止录音失败: {str(e)}")
            self.recording_state_changed.emit(False)
            return False
        
        self.recording_state_changed.emit(False)
        return True
    
    def _process_audio_data(self, audio_data):
        try:
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            
            if len(audio_np) < self.RATE * self.MIN_AUDIO_DURATION:
                self.logger.warning(f"音频样本数太少: {len(audio_np)}")
                return None
            
            max_val = np.abs(audio_np).max()
            rms = np.sqrt(np.mean(audio_np.astype(np.float32)**2))
            
            self.logger.info(f"音频分析 - 最大值: {max_val}, RMS: {rms:.2f}")
            
            if max_val < self.SILENCE_THRESHOLD:
                self.logger.warning("音频信号太弱")
                return None
            
            gain = 1.5
            audio_np = np.clip(audio_np * gain, -32768, 32767).astype(np.int16)
            
            processed_data = audio_np.tobytes()
            
            self.logger.info(f"音频处理完成，增强后最大值: {np.abs(audio_np).max()}")
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"音频处理失败: {str(e)}")
            return None
    
    def _process_audio(self, audio_data):
        try:
            self.logger.info("正在识别，请稍候...")
            start_time = time.time()
            
            access_token = self._get_access_token()
            if not access_token:
                self.logger.error("无法获取百度API Token")
                return
            
            speech_base64 = base64.b64encode(audio_data).decode("utf8")
            speech_len = len(audio_data)
            
            payload = json.dumps({
                "format": "pcm",
                "rate": self.RATE,
                "channel": 1,
                "cuid": BAIDU_ASR_CONFIG['CUID'],
                "token": access_token,
                "speech": speech_base64,
                "len": speech_len,
                "dev_pid": self._current_dev_pid
            }, ensure_ascii=False)
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(BAIDU_ASR_CONFIG['URL'], headers=headers, data=payload.encode("utf-8"))
            response.encoding = "utf-8"
            result = response.json()
            
            recognize_time = time.time() - start_time
            
            if result.get('err_no') == 0:
                text = result.get('result', [''])[0]
                if not text or len(text.strip()) == 0:
                    self.logger.warning("识别结果为空")
                    return
                
                self.logger.info(f"百度识别成功! 耗时: {recognize_time:.2f}秒，识别结果: {text}")
                self.voice_detected.emit(text)
                
                is_wake, command, responses = self.smart_assistant.process_text(text)
                
                if responses:
                    self.assistant_response.emit(responses)
                    self.logger.info(f"智能管家响应: {responses}")
                
                device, action = self.command_system.parse_command(text)
                if device:
                    self.logger.info(f"执行命令: 设备={device}, 动作={action}")
                    self.command_system.execute_command(device, action)
                elif not is_wake and not responses:
                    self.logger.warning(f"无法解析指令: {text}")
            else:
                self.logger.error(f"百度识别失败: err_no={result.get('err_no')}, err_msg={result.get('err_msg')}")
                
        except Exception as e:
            self.logger.error(f"音频处理异常: {str(e)}")
    
    def cleanup(self):
        self.logger.info("清理语音识别器资源...")
        if self._stream:
            self._stream.close()
            self._stream = None
        if self._pyaudio_instance:
            self._pyaudio_instance.terminate()
            self._pyaudio_instance = None
        self.logger.info("语音识别器资源已清理")