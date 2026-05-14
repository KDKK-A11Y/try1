import os
import numpy as np
import pyaudio
import wave
import threading
import time
import base64
import json
import requests
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal
from config.config import BAIDU_ASR_CONFIG

class VoiceprintRecognizer(QObject):
    recording_started = pyqtSignal(int, int)  # (current_round, total_rounds)
    recording_finished = pyqtSignal(int, int)
    registration_finished = pyqtSignal(bool, str)
    recognition_finished = pyqtSignal(bool, str, float)
    round_verified = pyqtSignal(int, bool, str)  # (round, success, message)
    
    def __init__(self):
        super().__init__()
        self.voiceprints = {}
        self.voiceprint_dir = Path("voiceprints")
        self.voiceprint_dir.mkdir(exist_ok=True)
        
        # 录音参数
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1024
        self.RECORD_DURATION = 3  # 每次录音3秒
        self.REGISTRATION_ROUNDS = 3  # 需要成功录制3次
        
        self._pyaudio = None
        self._current_user_id = None
        self._is_running = False
        
        # 百度语音识别配置（从配置文件读取）
        self._access_token = None
        self._token_expire_time = 0
        self.BAIDU_URL = BAIDU_ASR_CONFIG['URL']
        self.API_KEY = BAIDU_ASR_CONFIG['API_KEY']
        self.SECRET_KEY = BAIDU_ASR_CONFIG['SECRET_KEY']
        self.CUID = BAIDU_ASR_CONFIG['CUID']
        
        print(f"📋 声纹识别器初始化，使用百度API Key: {self.API_KEY[:8]}...")
        
    def _get_access_token(self):
        """获取百度API Token"""
        now = time.time()
        if self._access_token and now < self._token_expire_time:
            return self._access_token
        
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.API_KEY}&client_secret={self.SECRET_KEY}"
        
        try:
            response = requests.get(url, timeout=5)
            result = response.json()
            
            if 'access_token' in result:
                self._access_token = result['access_token']
                self._token_expire_time = now + result.get('expires_in', 3600) - 60
                print(f"✅ 获取百度API Token成功")
                return self._access_token
            else:
                error_msg = result.get('error_description', '未知错误')
                print(f"❌ 获取Token失败: {error_msg}")
                return None
        except Exception as e:
            print(f"❌ 获取Token异常: {e}")
            return None
    
    def _recognize_with_baidu(self, audio_data):
        """调用百度语音识别"""
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        try:
            speech_base64 = base64.b64encode(audio_data).decode("utf8")
            speech_len = len(audio_data)
            
            payload = json.dumps({
                "format": "pcm",
                "rate": self.RATE,
                "channel": 1,
                "cuid": self.CUID,
                "token": access_token,
                "speech": speech_base64,
                "len": speech_len,
                "dev_pid": 1537  # 普通话
            }, ensure_ascii=False)
            
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            response = requests.post(self.BAIDU_URL, headers=headers, data=payload.encode("utf-8"), timeout=10)
            result = response.json()
            
            if result.get('err_no') == 0:
                text = result.get('result', [''])[0]
                print(f"🔊 百度识别结果: {text}")
                return text
            else:
                print(f"❌ 百度识别失败: {result.get('err_msg')}")
                return None
                
        except Exception as e:
            print(f"❌ 百度识别异常: {e}")
            return None
    
    def _check_wake_word(self, text):
        """检查是否是"管家管家" """
        if not text:
            return False
        
        text = text.strip()
        wake_words = ["管家管家", "管家 管家", "管家管家。", "管家管家！", "管家管家，"]
        
        for wake_word in wake_words:
            if wake_word in text or text in wake_word:
                return True
        
        return False
    
    def init_audio(self):
        """初始化音频设备"""
        if not self._pyaudio:
            self._pyaudio = pyaudio.PyAudio()
            print("🎧 音频设备初始化成功")
    
    def record_audio(self, duration=None, save_path=None):
        """录制音频"""
        if duration is None:
            duration = self.RECORD_DURATION
            
        self.init_audio()
        frames = []
        
        try:
            stream = self._pyaudio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            print(f"⏱️ 正在录音 {duration} 秒...")
            for _ in range(int(self.RATE / self.CHUNK * duration)):
                data = stream.read(self.CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            print("🔇 录音结束")
            
            audio_data = b''.join(frames)
            
            if save_path:
                wf = wave.open(save_path, 'wb')
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self._pyaudio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(audio_data)
                wf.close()
            
            return True, audio_data
        except Exception as e:
            print(f"❌ 录音失败: {e}")
            return False, None
    
    def extract_mfcc_features(self, audio_data_list):
        """从多段音频数据提取MFCC特征（提高准确度）"""
        try:
            import librosa
            
            all_features = []
            
            for audio_data in audio_data_list:
                # 将字节数据转换为numpy数组
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # 提取MFCC特征
                mfccs = librosa.feature.mfcc(
                    y=audio_np,
                    sr=self.RATE,
                    n_mfcc=13,
                    n_fft=512,
                    hop_length=256
                )
                
                # 计算均值和标准差作为特征
                mfcc_mean = np.mean(mfccs, axis=1)
                mfcc_std = np.std(mfccs, axis=1)
                
                feature = np.concatenate([mfcc_mean, mfcc_std])
                all_features.append(feature)
            
            # 合并多次录音的特征
            merged_feature = np.mean(all_features, axis=0)
            print(f"✅ 合并 {len(audio_data_list)} 段录音特征，维度: {len(merged_feature)}")
            return merged_feature
        
        except Exception as e:
            print(f"❌ MFCC提取失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def calculate_similarity(self, feature1, feature2):
        """计算余弦相似度"""
        if feature1 is None or feature2 is None:
            return 0.0
        
        try:
            dot_product = np.dot(feature1, feature2)
            norm1 = np.linalg.norm(feature1)
            norm2 = np.linalg.norm(feature2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return similarity
        
        except Exception as e:
            print(f"❌ 相似度计算失败: {e}")
            return 0.0
    
    def register_voiceprint_async(self, user_id):
        """异步注册声纹（录制多次并验证）"""
        if self._is_running:
            print("⚠️ 正在处理中，请稍候")
            return
            
        self._current_user_id = user_id
        self._is_running = True
        thread = threading.Thread(target=self._register_voiceprint_thread, daemon=True)
        thread.start()
    
    def _register_voiceprint_thread(self):
        """后台线程执行声纹注册（成功录制3次后一起提取特征）"""
        audio_data_list = []  # 保存所有成功录制的音频
        
        try:
            # 循环直到成功录制3次
            while len(audio_data_list) < self.REGISTRATION_ROUNDS:
                current_round = len(audio_data_list) + 1
                print(f"\n===== 第 {current_round}/{self.REGISTRATION_ROUNDS} 次录制 =====")
                self.recording_started.emit(current_round, self.REGISTRATION_ROUNDS)
                
                # 录制音频
                success, audio_data = self.record_audio(duration=self.RECORD_DURATION)
                
                if not success:
                    self.recording_finished.emit(current_round, self.REGISTRATION_ROUNDS)
                    self.round_verified.emit(current_round, False, "录音失败，请重试")
                    time.sleep(0.5)  # 等待0.5秒后重试
                    continue  # 重新录制当前轮
                
                self.recording_finished.emit(current_round, self.REGISTRATION_ROUNDS)
                
                # 使用百度识别确认是否说的是"管家管家"
                print("🔍 正在识别语音内容...")
                text = self._recognize_with_baidu(audio_data)
                
                if text is None:
                    self.round_verified.emit(current_round, False, "语音识别失败，请重试")
                    time.sleep(0.5)
                    continue  # 重新录制当前轮
                
                # 检查是否是"管家管家"
                if not self._check_wake_word(text):
                    self.round_verified.emit(current_round, False, f"未识别到'管家管家'，识别结果: {text}，请重试")
                    time.sleep(0.5)
                    continue  # 重新录制当前轮
                
                # 当前轮成功，保存音频数据
                audio_data_list.append(audio_data)
                self.round_verified.emit(current_round, True, "录制成功！")
                print(f"✅ 第 {current_round} 次录制成功")
            
            # 完成所有录制，现在一起提取声纹特征
            print(f"\n===== 注册结果 =====")
            print(f"成功录制: {len(audio_data_list)} 次")
            print("🔊 正在合并音频并提取声纹特征...")
            
            # 将3段音频一起提取特征（提高准确度）
            merged_feature = self.extract_mfcc_features(audio_data_list)
            
            if merged_feature is None:
                self.registration_finished.emit(False, "声纹特征提取失败")
                return
            
            # 保存声纹
            self.voiceprints[self._current_user_id] = merged_feature
            np.save(self.voiceprint_dir / f"{self._current_user_id}.npy", merged_feature)
            print(f"✅ 声纹注册成功，用户: {self._current_user_id}")
            self.registration_finished.emit(True, f"声纹注册成功！已成功录制 {len(audio_data_list)} 次")
                
        except Exception as e:
            print(f"❌ 注册过程异常: {e}")
            import traceback
            traceback.print_exc()
            self.registration_finished.emit(False, f"注册异常: {str(e)}")
            
        finally:
            self._is_running = False
    
    def recognize_async(self):
        """异步识别声纹"""
        if self._is_running:
            print("⚠️ 正在处理中，请稍候")
            return
            
        self._is_running = True
        thread = threading.Thread(target=self._recognize_thread, daemon=True)
        thread.start()
    
    def _recognize_thread(self):
        """后台线程执行声纹识别"""
        try:
            print("\n===== 声纹识别 =====")
            self.recording_started.emit(1, 1)
            
            # 录制音频
            success, audio_data = self.record_audio(duration=self.RECORD_DURATION)
            
            if not success:
                self.recording_finished.emit(1, 1)
                self._is_running = False
                self.recognition_finished.emit(False, "", 0.0)
                return
            
            self.recording_finished.emit(1, 1)
            
            # 使用百度识别确认是否说的是"管家管家"
            print("🔍 正在识别语音内容...")
            text = self._recognize_with_baidu(audio_data)
            
            if text is None:
                print("❌ 百度语音识别失败")
                self.recognition_finished.emit(False, "", 0.0)
                self._is_running = False
                return
            
            # 检查是否是"管家管家"
            if not self._check_wake_word(text):
                print(f"❌ 未识别到'管家管家'，识别结果: {text}")
                self.recognition_finished.emit(False, "", 0.0)
                self._is_running = False
                return
            
            print("✅ 识别到'管家管家'，开始声纹比对...")
            
            # 提取声纹特征
            feature = self.extract_mfcc_features([audio_data])
            if feature is None:
                print("❌ 特征提取失败")
                self.recognition_finished.emit(False, "", 0.0)
                self._is_running = False
                return
            
            print("🔍 正在比对声纹...")
            if not self.voiceprints:
                print("❌ 没有已注册的声纹")
                self.recognition_finished.emit(False, "", 0.0)
                self._is_running = False
                return
            
            best_match = None
            best_score = 0.0
            
            for user_id, registered_feature in self.voiceprints.items():
                similarity = self.calculate_similarity(feature, registered_feature)
                print(f"   用户 {user_id}: 相似度 = {similarity:.4f}")
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = user_id
            
            # 设置阈值
            threshold = 0.65
            print(f"\n📊 最高相似度: {best_score:.4f}, 阈值: {threshold}")
            
            if best_score >= threshold and best_match:
                print(f"✅ 识别成功: {best_match}")
                self.recognition_finished.emit(True, best_match, best_score)
            else:
                print(f"❌ 识别失败")
                self.recognition_finished.emit(False, "", best_score)
                
        except Exception as e:
            print(f"❌ 识别过程异常: {e}")
            import traceback
            traceback.print_exc()
            self.recognition_finished.emit(False, "", 0.0)
            
        finally:
            self._is_running = False
    
    def load_voiceprints(self):
        """加载已保存的声纹"""
        try:
            for file in self.voiceprint_dir.glob("*.npy"):
                user_id = file.stem
                feature = np.load(file)
                self.voiceprints[user_id] = feature
            print(f"📥 已加载 {len(self.voiceprints)} 个声纹")
        except Exception as e:
            print(f"❌ 加载声纹失败: {e}")
    
    def get_registered_users(self):
        """获取已注册的用户列表"""
        return list(self.voiceprints.keys())
    
    def cleanup(self):
        """清理资源"""
        if self._pyaudio:
            self._pyaudio.terminate()
            print("🔌 音频设备已关闭")
