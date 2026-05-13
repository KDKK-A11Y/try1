import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from modules.command_system import CommandSystem
from modules.state_manager import StateManager
from modules.sound_manager import SoundManager
from voice.voice_recognizer import VoiceRecognizer
from gesture.gesture_recognizer import GestureRecognizer
from modules.logger import Logger

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread

def main():
    app = QApplication(sys.argv)
    
    logger = Logger()
    state_manager = StateManager(logger)
    command_system = CommandSystem(state_manager, logger)
    sound_manager = SoundManager()
    
    voice_recognizer = VoiceRecognizer(command_system, logger)
    gesture_recognizer = GestureRecognizer(command_system, logger)
    
    main_window = MainWindow(state_manager, command_system, voice_recognizer, gesture_recognizer, logger, sound_manager)
    
    voice_thread = QThread()
    voice_recognizer.moveToThread(voice_thread)
    voice_thread.started.connect(voice_recognizer.start_listening)
    
    gesture_thread = QThread()
    gesture_recognizer.moveToThread(gesture_thread)
    gesture_thread.started.connect(gesture_recognizer.start_recognizing)
    
    voice_thread.start()
    gesture_thread.start()
    
    main_window.show()
    
    def cleanup():
        voice_recognizer.stop_listening()
        gesture_recognizer.stop_recognizing()
        voice_thread.quit()
        voice_thread.wait()
        gesture_thread.quit()
        gesture_thread.wait()
    
    app.aboutToQuit.connect(cleanup)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()