import json
import os
from pathlib import Path
from config.config import ROOMS, DEVICE_TYPES, DEFAULT_ROOM_DEVICES, DEVICE_STATES, DEVICE_NAMES

class DeviceManager:
    """设备管理器 - 管理自定义设备和房间"""
    
    def __init__(self):
        self.config_path = Path("config/device_config.json")
        self.load_config()
    
    def load_config(self):
        """加载设备配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"❌ 加载设备配置失败: {e}")
                self.config = self._create_default_config()
        else:
            self.config = self._create_default_config()
            self.save_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        return {
            'rooms': ROOMS,
            'device_types': DEVICE_TYPES,
            'room_devices': DEFAULT_ROOM_DEVICES,
            'custom_devices': {},
            'custom_rooms': {}
        }
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print("✅ 设备配置已保存")
        except Exception as e:
            print(f"❌ 保存设备配置失败: {e}")
    
    def add_custom_room(self, room_id, name, icon='🏠', color='#666666'):
        """添加自定义房间"""
        if room_id in self.config['rooms']:
            return False, f"房间ID '{room_id}' 已存在"
        
        self.config['rooms'][room_id] = {
            'name': name,
            'icon': icon,
            'color': color
        }
        self.config['custom_rooms'][room_id] = True
        self.config['room_devices'][room_id] = []
        self.save_config()
        return True, f"房间 '{name}' 添加成功"
    
    def remove_room(self, room_id):
        """删除房间"""
        if room_id in self.config['custom_rooms']:
            del self.config['rooms'][room_id]
            del self.config['room_devices'][room_id]
            del self.config['custom_rooms'][room_id]
            self.save_config()
            return True, "房间删除成功"
        return False, "只能删除自定义房间"
    
    def add_device_to_room(self, room_id, device_type):
        """向房间添加设备"""
        if room_id not in self.config['room_devices']:
            return False, "房间不存在"
        
        if device_type not in self.config['device_types']:
            return False, "设备类型不存在"
        
        device_key = f"{room_id}_{device_type}"
        if device_key in self.get_all_devices():
            return False, "该设备已在房间中"
        
        self.config['room_devices'][room_id].append(device_type)
        self.save_config()
        
        room_name = self.config['rooms'][room_id]['name']
        device_name = self.config['device_types'][device_type]['name']
        return True, f"已向 {room_name} 添加 {device_name}"
    
    def remove_device_from_room(self, room_id, device_type):
        """从房间移除设备"""
        if room_id not in self.config['room_devices']:
            return False, "房间不存在"
        
        if device_type not in self.config['room_devices'][room_id]:
            return False, "设备不在该房间中"
        
        self.config['room_devices'][room_id].remove(device_type)
        self.save_config()
        
        room_name = self.config['rooms'][room_id]['name']
        device_name = self.config['device_types'][device_type]['name']
        return True, f"已从 {room_name} 移除 {device_name}"
    
    def add_custom_device_type(self, device_id, name, icon, category='other', power_consumption=0):
        """添加自定义设备类型"""
        if device_id in self.config['device_types']:
            return False, f"设备类型ID '{device_id}' 已存在"
        
        self.config['device_types'][device_id] = {
            'name': name,
            'icon': icon,
            'category': category,
            'power_consumption': power_consumption
        }
        self.config['custom_devices'][device_id] = True
        self.save_config()
        return True, f"设备类型 '{name}' 添加成功"
    
    def remove_custom_device_type(self, device_id):
        """删除自定义设备类型"""
        if device_id not in self.config['custom_devices']:
            return False, "只能删除自定义设备类型"
        
        # 从所有房间中移除该类型设备
        for room_id in list(self.config['room_devices'].keys()):
            if device_id in self.config['room_devices'][room_id]:
                self.config['room_devices'][room_id].remove(device_id)
        
        del self.config['device_types'][device_id]
        del self.config['custom_devices'][device_id]
        self.save_config()
        return True, "设备类型删除成功"
    
    def get_all_rooms(self):
        """获取所有房间"""
        return self.config['rooms']
    
    def get_all_device_types(self):
        """获取所有设备类型"""
        return self.config['device_types']
    
    def get_room_devices(self, room_id):
        """获取房间设备"""
        return self.config['room_devices'].get(room_id, [])
    
    def get_all_devices(self):
        """获取所有设备（房间_设备类型）"""
        devices = []
        for room_id, device_types in self.config['room_devices'].items():
            for device_type in device_types:
                devices.append(f"{room_id}_{device_type}")
        return devices
    
    def get_device_info(self, device_key):
        """获取设备信息"""
        if '_' in device_key:
            room_id, device_type = device_key.split('_', 1)
            if room_id in self.config['rooms'] and device_type in self.config['device_types']:
                return {
                    'room_id': room_id,
                    'room_name': self.config['rooms'][room_id]['name'],
                    'room_icon': self.config['rooms'][room_id]['icon'],
                    'device_type': device_type,
                    'device_name': self.config['device_types'][device_type]['name'],
                    'device_icon': self.config['device_types'][device_type]['icon'],
                    'category': self.config['device_types'][device_type]['category'],
                    'power_consumption': self.config['device_types'][device_type]['power_consumption']
                }
        return None
    
    def get_devices_by_category(self, category):
        """按类别获取设备"""
        devices = []
        for device_key in self.get_all_devices():
            info = self.get_device_info(device_key)
            if info and info['category'] == category:
                devices.append(device_key)
        return devices
    
    def get_custom_rooms(self):
        """获取自定义房间列表"""
        return list(self.config['custom_rooms'].keys())
    
    def get_room_info(self, room_id):
        """获取房间信息"""
        return self.config['rooms'].get(room_id, {})
    
    def get_custom_device_types(self):
        """获取自定义设备类型列表"""
        return list(self.config['custom_devices'].keys())
    
    def get_room_color(self, room_id):
        """获取房间颜色"""
        return self.config['rooms'].get(room_id, {}).get('color', '#666666')
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self._create_default_config()
        self.save_config()
        return True, "已重置为默认配置"
    
    def get_summary(self):
        """获取设备管理摘要"""
        total_rooms = len(self.config['rooms'])
        total_device_types = len(self.config['device_types'])
        total_devices = len(self.get_all_devices())
        custom_rooms = len(self.config['custom_rooms'])
        custom_devices = len(self.config['custom_devices'])
        
        return {
            'total_rooms': total_rooms,
            'total_device_types': total_device_types,
            'total_devices': total_devices,
            'custom_rooms': custom_rooms,
            'custom_devices': custom_devices
        }
