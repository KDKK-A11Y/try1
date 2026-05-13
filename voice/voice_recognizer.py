import speech_recognition as sr
from PyQt5.QtCore import QObject, pyqtSignal

class VoiceRecognizer(QObject):
    voice_detected = pyqtSignal(str)
    
    def __init__(self, command_system, logger):
        super().__init__()
        self.command_system = command_system
        self.logger = logger
        self.r = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        
        try:
            self.microphone = sr.Microphone()
            self.logger.info("麦克风初始化成功")
        except Exception as e:
            self.logger.error(f"麦克风初始化失败: {str(e)}")
    
    def start_listening(self):
        if not self.microphone:
            self.logger.error("麦克风不可用")
            return
        
        self.is_listening = True
        self.logger.info("语音识别服务已启动")
        
        while self.is_listening:
            try:
                with self.microphone as source:
                    self.r.adjust_for_ambient_noise(source, duration=0.5)
                    self.logger.debug("正在监听...")
                    
                    audio = self.r.listen(source, timeout=5, phrase_time_limit=5)
                
                text = self.r.recognize_google(audio, language='zh-CN')
                self.logger.info(f"识别到语音: {text}")
                self.voice_detected.emit(text)
                
                device, action = self.command_system.parse_command(text)
                if device:
                    self.command_system.execute_command(device, action)
                else:
                    self.logger.warning(f"无法解析指令: {text}")
                
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                self.logger.warning("无法识别语音内容")
            except sr.RequestError as e:
                self.logger.error(f"语音识别服务请求失败: {str(e)}")
            except Exception as e:
                self.logger.error(f"语音识别异常: {str(e)}")
    
    def stop_listening(self):
        self.is_listening = False
        self.logger.info("语音识别服务已停止")
