import os
import sys
import requests
import uuid
import pygame
import time
from config.config import BAIDU_ASR_CONFIG

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self._access_token = None
        self._token_expire_time = 0
        self._temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp_audio')
        os.makedirs(self._temp_dir, exist_ok=True)
        
        pygame.mixer.init()
        
        self._cleanup_old_temp_files()
        
        self.load_sounds()
    
    def _cleanup_old_temp_files(self):
        """清理超过1小时的旧临时文件"""
        try:
            now = time.time()
            for filename in os.listdir(self._temp_dir):
                if filename.startswith('tts_') and filename.endswith('.mp3'):
                    filepath = os.path.join(self._temp_dir, filename)
                    file_mtime = os.path.getmtime(filepath)
                    if now - file_mtime > 3600:
                        os.remove(filepath)
        except Exception as e:
            pass
    
    def load_sounds(self):
        sound_dir = os.path.join(os.path.dirname(__file__), '..', 'sounds')
        os.makedirs(sound_dir, exist_ok=True)
        
        self.sounds['success'] = self.create_tone(800, 100)
        self.sounds['error'] = self.create_tone(300, 200)
        self.sounds['click'] = self.create_tone(600, 50)
        self.sounds['device_on'] = self.create_tone(523, 100)
        self.sounds['device_off'] = self.create_tone(392, 100)
        self.sounds['voice_detected'] = self.create_tone(440, 150)
        self.sounds['gesture_detected'] = self.create_tone(660, 150)
    
    def create_tone(self, frequency, duration):
        try:
            import winsound
            def play_tone():
                winsound.Beep(frequency, duration)
            return play_tone
        except ImportError:
            def play_silent():
                pass
            return play_silent
    
    def play(self, sound_name):
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name]()
            except Exception as e:
                pass
    
    def play_success(self):
        self.play('success')
    
    def play_error(self):
        self.play('error')
    
    def play_click(self):
        self.play('click')
    
    def play_device_on(self):
        self.play('device_on')
    
    def play_device_off(self):
        self.play('device_off')
    
    def play_voice_detected(self):
        self.play('voice_detected')
    
    def play_gesture_detected(self):
        self.play('gesture_detected')
    
    def play_wake(self):
        """播放唤醒提示音"""
        wake_path = os.path.join(os.path.dirname(__file__), '..', 'wake.mp3')
        if os.path.exists(wake_path):
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(wake_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.05)
            except Exception as e:
                pass
        else:
            self.play_voice_detected()
    
    def _get_access_token(self):
        now = time.time()
        if self._access_token and now < self._token_expire_time:
            return self._access_token
        
        api_key = BAIDU_ASR_CONFIG['API_KEY']
        secret_key = BAIDU_ASR_CONFIG['SECRET_KEY']
        
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
        
        try:
            response = requests.post(url, params=params)
            result = response.json()
            
            if 'access_token' in result:
                self._access_token = result['access_token']
                self._token_expire_time = now + result.get('expires_in', 3600) - 60
                return self._access_token
            else:
                return None
        except Exception as e:
            return None
    
    def speak(self, text_list):
        if not text_list or not isinstance(text_list, list):
            return
        
        for text in text_list:
            if not text or not isinstance(text, str):
                continue
            
            self._speak_single(text)
    
    def _speak_single(self, text):
        access_token = self._get_access_token()
        if not access_token:
            return
        
        url = "https://tsn.baidu.com/text2audio"
        
        payload = f'tex={requests.utils.quote(text)}&tok={access_token}&cuid=test_user&ctp=1&lan=zh&spd=5&pit=6&vol=6&per=4115&aue=3'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*'
        }
        
        temp_file = None
        try:
            response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
            
            if 'audio/mp3' in response.headers.get('Content-Type', '') or len(response.content) > 100:
                temp_file = os.path.join(self._temp_dir, f'tts_{uuid.uuid4().hex}.mp3')
                
                with open(temp_file, 'wb') as f:
                    f.write(response.content)
                
                pygame.mixer.music.stop()
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            
        except Exception as e:
            pass
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    pass