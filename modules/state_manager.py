from PyQt5.QtCore import QObject, pyqtSignal
from config.config import DEVICE_STATES, DEVICE_NAMES

class StateManager(QObject):
    state_changed = pyqtSignal(str, bool)
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.device_states = DEVICE_STATES.copy()
    
    def get_state(self, device):
        if device in self.device_states:
            return self.device_states[device]
        return False
    
    def set_state(self, device, state):
        if device in self.device_states:
            old_state = self.device_states[device]
            self.device_states[device] = state
            
            if old_state != state:
                device_name = DEVICE_NAMES.get(device, device)
                status = '开启' if state else '关闭'
                self.logger.info(f"设备状态变更: {device_name} -> {status}")
                self.state_changed.emit(device, state)
    
    def toggle_state(self, device):
        if device in self.device_states:
            new_state = not self.device_states[device]
            self.set_state(device, new_state)
            return new_state
        return False
    
    def get_all_states(self):
        return self.device_states.copy()
    
    def reset_all(self):
        for device in self.device_states:
            self.set_state(device, False)
        self.logger.info("所有设备已重置为关闭状态")
