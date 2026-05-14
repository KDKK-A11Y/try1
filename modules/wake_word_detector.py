import pvporcupine
import pyaudio
import threading
import time
import os
from PyQt5.QtCore import QObject, pyqtSignal
from config.config import PORCUPINE_CONFIG

class WakeWordDetector(QObject):
    wake_word_detected = pyqtSignal(str)
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self._porcupine = None
        self._pa = None
        self._audio_stream = None
        self._is_running = False
        self._detection_lock = threading.Lock()
        self._last_detection_time = 0
        self._cooldown_period = 3
    
    def start(self):
        if self._is_running:
            self.logger.warning("唤醒词检测器已在运行")
            return False
        
        try:
            keywords = PORCUPINE_CONFIG.get('KEYWORDS', ['computer'])
            access_key = PORCUPINE_CONFIG.get('ACCESS_KEY', None)
            
            self.logger.info(f"初始化 Porcupine 唤醒词检测器，关键词: {keywords}")
            
            if access_key:
                self._porcupine = pvporcupine.create(
                    access_key=access_key,
                    keywords=keywords
                )
            else:
                self._porcupine = pvporcupine.create(
                    keyword_paths=self._get_keyword_paths(keywords)
                )
            
            self._pa = pyaudio.PyAudio()
            self._audio_stream = self._pa.open(
                rate=self._porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self._porcupine.frame_length,
                stream_callback=self._audio_callback
            )
            
            self._is_running = True
            self.logger.info("Porcupine 唤醒词检测器已启动")
            
            return True
            
        except Exception as e:
            self.logger.error(f"启动唤醒词检测器失败: {str(e)}")
            self.cleanup()
            return False
    
    def stop(self):
        if not self._is_running:
            return
        
        self._is_running = False
        
        if self._audio_stream:
            try:
                self._audio_stream.stop_stream()
                self._audio_stream.close()
            except:
                pass
            self._audio_stream = None
        
        if self._porcupine:
            try:
                self._porcupine.delete()
            except:
                pass
            self._porcupine = None
        
        if self._pa:
            try:
                self._pa.terminate()
            except:
                pass
            self._pa = None
        
        self.logger.info("Porcupine 唤醒词检测器已停止")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        if not self._is_running or not self._porcupine:
            return (in_data, pyaudio.paAbort)
        
        pcm = pvporcupine.convert_pcm(in_data)
        
        try:
            keyword_index = self._porcupine.process(pcm)
            
            if keyword_index >= 0:
                current_time = time.time()
                
                with self._detection_lock:
                    if current_time - self._last_detection_time >= self._cooldown_period:
                        self._last_detection_time = current_time
                        keywords = PORCUPINE_CONFIG.get('KEYWORDS', ['computer'])
                        detected_keyword = keywords[keyword_index] if keyword_index < len(keywords) else "unknown"
                        
                        self.logger.info(f"检测到唤醒词: {detected_keyword}")
                        self.wake_word_detected.emit(detected_keyword)
        
        except Exception as e:
            self.logger.error(f"唤醒词检测异常: {str(e)}")
        
        return (in_data, pyaudio.paContinue)
    
    def _get_keyword_paths(self, keywords):
        keyword_paths = []
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        
        for keyword in keywords:
            keyword_file = f"{keyword.lower()}_windows.ppn"
            keyword_path = os.path.join(model_dir, keyword_file)
            
            if os.path.exists(keyword_path):
                keyword_paths.append(keyword_path)
            else:
                self.logger.warning(f"未找到关键词模型: {keyword_file}，将使用内置模型")
                keyword_paths.append(None)
        
        return keyword_paths
    
    def cleanup(self):
        self.stop()