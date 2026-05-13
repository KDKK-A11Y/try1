import os
import sys
from PyQt5.QtMultimedia import QSound

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
    
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