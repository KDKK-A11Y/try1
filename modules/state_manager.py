from PyQt5.QtCore import QObject, pyqtSignal
from config.config import DEVICE_STATES, DEVICE_NAMES

class StateManager(QObject):
    state_changed = pyqtSignal(str, bool)
    property_changed = pyqtSignal(str, str, object)
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.device_states = DEVICE_STATES.copy()
        self.device_properties = {}
    
    def add_device(self, device_key, device_name=None):
        """动态添加设备到状态管理器"""
        if device_key not in self.device_states:
            self.device_states[device_key] = False
            if device_name and device_key not in DEVICE_NAMES:
                DEVICE_NAMES[device_key] = device_name
            # 初始化设备属性
            self.device_properties[device_key] = {}
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
            # 重置所有属性
            if device in self.device_properties:
                self.device_properties[device] = {}
        self.logger.info("所有设备已重置为关闭状态")
    
    def get_property(self, device, property_name, default=None):
        """获取设备属性值"""
        if device in self.device_properties:
            return self.device_properties[device].get(property_name, default)
        return default
    
    def set_property(self, device, property_name, value):
        """设置设备属性值"""
        if device not in self.device_properties:
            self.device_properties[device] = {}
        
        old_value = self.device_properties[device].get(property_name)
        self.device_properties[device][property_name] = value
        
        if old_value != value:
            self.logger.info(f"设备属性变更: {device}.{property_name} -> {value}")
            self.property_changed.emit(device, property_name, value)
    
    def get_device_properties(self, device):
        """获取设备所有属性"""
        return self.device_properties.get(device, {}).copy()
    
    def set_device_properties(self, device, properties):
        """批量设置设备属性"""
        if device not in self.device_properties:
            self.device_properties[device] = {}
        
        for prop_name, value in properties.items():
            self.set_property(device, prop_name, value)
    
    def init_device_properties(self, device, controls_config):
        """根据控件配置初始化设备属性默认值"""
        if device not in self.device_properties:
            self.device_properties[device] = {}
        
        for prop_name, config in controls_config.items():
            if 'default' in config:
                if prop_name not in self.device_properties[device]:
                    self.device_properties[device][prop_name] = config['default']