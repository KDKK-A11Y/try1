from PyQt5.QtCore import QObject, pyqtSignal
from config.config import DEVICE_STATES, DEVICE_NAMES

class StateManager(QObject):
    state_changed = pyqtSignal(str, bool)
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.device_states = DEVICE_STATES.copy()
    
    def add_device(self, device_key, device_name=None):
        """动态添加设备到状态管理器"""
        if device_key not in self.device_states:
            self.device_states[device_key] = False
            if device_name and device_key not in DEVICE_NAMES:
                DEVICE_NAMES[device_key] = device_name
            self.logger.info(f"设备已注册: {device_key}")
    
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
        else:
            # 如果设备不存在，先注册再设置状态
            self.add_device(device)
            self.device_states[device] = state
            self.logger.info(f"新设备已添加并设置状态: {device} -> {'开启' if state else '关闭'}")
            self.state_changed.emit(device, state)
    
    def toggle_state(self, device):
        if device in self.device_states:
            new_state = not self.device_states[device]
            self.set_state(device, new_state)
            return new_state
        else:
            # 如果设备不存在，先注册并设置为开启状态
            self.add_device(device)
            self.device_states[device] = True
            self.logger.info(f"新设备已添加并开启: {device}")
            self.state_changed.emit(device, True)
            return True
    
    def get_all_states(self):
        return self.device_states.copy()
    
    def reset_all(self):
        for device in self.device_states:
            self.set_state(device, False)
        self.logger.info("所有设备已重置为关闭状态")
