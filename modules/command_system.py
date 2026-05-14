from config.config import DEVICE_COMMANDS, DEVICE_NAMES, GESTURE_DEVICE_MAP, ROOM_COMMANDS, ROOMS, DEFAULT_ROOM_DEVICES
import re

class CommandSystem:
    def __init__(self, state_manager, logger, device_manager=None):
        self.state_manager = state_manager
        self.logger = logger
        self.device_manager = device_manager
        self.command_history = []
        self.gesture_device_map = GESTURE_DEVICE_MAP
        
    def parse_command(self, command_text):
        """解析命令文本，返回(设备类型, 动作, 房间ID)"""
        command_text = command_text.strip().lower()
        
        # 检查场景命令
        for scene, config in ROOM_COMMANDS.items():
            for cmd in config['commands']:
                if cmd.lower() in command_text:
                    return ('scene', scene, None)
        
        # 检查房间特定命令
        target_room = None
        for room_id, room_info in ROOMS.items():
            room_name = room_info['name']
            if room_name in command_text or room_id in command_text:
                target_room = room_id
                break
        
        # 检查设备命令
        for device_type, actions in DEVICE_COMMANDS.items():
            for action, commands in actions.items():
                for cmd in commands:
                    if cmd.lower() in command_text:
                        return (device_type, action, target_room)
        
        # 检查全部命令
        for action in ['all_on', 'all_off']:
            if action in command_text:
                action_type = 'on' if action == 'all_on' else 'off'
                return ('all', action_type, target_room)
        
        return (None, None, None)
    
    def execute_command(self, device_type, action, room_id=None):
        """执行命令"""
        if device_type is None:
            self.logger.warning(f"无法识别指令")
            return False, "无法识别指令"
        
        # 场景命令
        if device_type == 'scene':
            return self._execute_scene_command(action)
        
        # 全部设备命令
        if device_type == 'all':
            return self._execute_all_command(action, room_id)
        
        # 单个设备命令
        return self._execute_device_command(device_type, action, room_id)
    
    def _execute_scene_command(self, scene_name):
        """执行场景命令"""
        if scene_name not in ROOM_COMMANDS:
            return False, f"未知场景: {scene_name}"
        
        scene_config = ROOM_COMMANDS[scene_name]
        actions = scene_config.get('actions', [])
        
        success_count = 0
        for action_item in actions:
            device_type = action_item['device']
            action = action_item['action']
            try:
                # 在所有房间执行场景动作
                for room_id in DEFAULT_ROOM_DEVICES.keys():
                    if device_type in DEFAULT_ROOM_DEVICES[room_id]:
                        device_key = f"{room_id}_{device_type}"
                        if action == 'on':
                            self.state_manager.set_state(device_key, True)
                        elif action == 'off':
                            self.state_manager.set_state(device_key, False)
                        elif action == 'open':
                            self.state_manager.set_state(device_key, True)
                        elif action == 'close':
                            self.state_manager.set_state(device_key, False)
                        elif action == 'lock':
                            self.state_manager.set_state(device_key, True)
                        elif action == 'unlock':
                            self.state_manager.set_state(device_key, False)
                        success_count += 1
            except Exception as e:
                self.logger.error(f"场景动作执行失败: {e}")
        
        scene_name_cn = {
            'good_morning': '早上好',
            'good_night': '晚安',
            'leave_home': '出门',
            'come_home': '回家'
        }.get(scene_name, scene_name)
        
        self.command_history.append({
            'device': scene_name_cn,
            'action': '场景执行',
            'success': success_count > 0
        })
        
        if success_count > 0:
            self.logger.info(f"场景执行成功: {scene_name_cn}")
            return True, f"{scene_name_cn}场景已执行"
        else:
            return False, "场景执行失败"
    
    def _execute_all_command(self, action, room_id=None):
        """执行全部设备命令"""
        devices = []
        
        if room_id:
            # 只控制指定房间的设备
            if room_id in DEFAULT_ROOM_DEVICES:
                for device_type in DEFAULT_ROOM_DEVICES[room_id]:
                    devices.append(f"{room_id}_{device_type}")
            room_name = ROOMS.get(room_id, {}).get('name', room_id)
        else:
            # 控制所有房间的设备
            for room, room_devices in DEFAULT_ROOM_DEVICES.items():
                for device_type in room_devices:
                    devices.append(f"{room}_{device_type}")
            room_name = '所有房间'
        
        success_count = 0
        for device_key in devices:
            try:
                if action == 'on':
                    self.state_manager.set_state(device_key, True)
                elif action == 'off':
                    self.state_manager.set_state(device_key, False)
                success_count += 1
            except Exception as e:
                self.logger.error(f"设备控制失败 {device_key}: {e}")
        
        action_text = '打开' if action == 'on' else '关闭'
        self.command_history.append({
            'device': room_name,
            'action': f'全部{action_text}',
            'success': success_count > 0
        })
        
        if success_count > 0:
            self.logger.info(f"{room_name}全部设备{action_text}成功: {success_count}个设备")
            return True, f"{room_name}的{success_count}个设备已{action_text}"
        else:
            return False, "未找到可控制的设备"
    
    def _execute_device_command(self, device_type, action, room_id=None):
        """执行单个设备命令"""
        devices_to_control = []
        
        if room_id:
            # 只控制指定房间的设备
            if room_id in DEFAULT_ROOM_DEVICES and device_type in DEFAULT_ROOM_DEVICES[room_id]:
                devices_to_control.append(f"{room_id}_{device_type}")
            else:
                return False, f"{ROOMS.get(room_id, {}).get('name', room_id)}没有{DEVICE_NAMES.get(device_type, device_type)}"
        else:
            # 控制所有房间中的该类型设备
            for room, room_devices in DEFAULT_ROOM_DEVICES.items():
                if device_type in room_devices:
                    devices_to_control.append(f"{room}_{device_type}")
            
            if not devices_to_control:
                return False, f"未找到{DEVICE_NAMES.get(device_type, device_type)}设备"
        
        success_count = 0
        device_name = DEVICE_NAMES.get(device_type, device_type)
        
        for device_key in devices_to_control:
            try:
                if action == 'on':
                    self.state_manager.set_state(device_key, True)
                elif action == 'off':
                    self.state_manager.set_state(device_key, False)
                elif action == 'toggle':
                    self.state_manager.toggle_state(device_key)
                elif action == 'open':  # 窗帘、水阀等
                    self.state_manager.set_state(device_key, True)
                elif action == 'close':  # 窗帘、水阀等
                    self.state_manager.set_state(device_key, False)
                elif action == 'lock':  # 门锁
                    self.state_manager.set_state(device_key, True)
                elif action == 'unlock':  # 门锁
                    self.state_manager.set_state(device_key, False)
                else:
                    # 其他动作（如调节温度、音量等）
                    self.state_manager.set_state(device_key, True)
                    self.logger.info(f"设备 {device_key} {action}")
                
                success_count += 1
            except Exception as e:
                self.logger.error(f"设备控制失败 {device_key}: {e}")
        
        action_text = self._get_action_text(action)
        self.command_history.append({
            'device': device_name,
            'action': action_text,
            'success': success_count > 0
        })
        
        if success_count > 0:
            if room_id:
                room_name = ROOMS.get(room_id, {}).get('name', room_id)
                msg = f"{room_name}的{device_name}已{action_text}"
            else:
                msg = f"{success_count}个{device_name}已{action_text}"
            
            self.logger.info(f"指令执行成功: {device_name} {action_text}")
            return True, msg
        else:
            return False, "设备控制失败"
    
    def _get_action_text(self, action):
        """获取动作的中文描述"""
        action_map = {
            'on': '打开',
            'off': '关闭',
            'toggle': '切换',
            'open': '打开',
            'close': '关闭',
            'lock': '上锁',
            'unlock': '解锁',
            'cool': '制冷模式',
            'heat': '制热模式',
            'auto': '自动模式',
            'temp_up': '温度升高',
            'temp_down': '温度降低',
            'speed_up': '风速加大',
            'speed_down': '风速减小',
            'volume_up': '音量加大',
            'volume_down': '音量减小',
            'channel_up': '上一台',
            'channel_down': '下一台',
            'half': '半开',
            'record': '开始录像',
            'snapshot': '拍照',
            'return': '返回充电'
        }
        return action_map.get(action, action)
    
    def execute_gesture_command(self, gesture_type):
        """执行手势命令"""
        if gesture_type in self.gesture_device_map:
            device_type = self.gesture_device_map[gesture_type]
            
            # 查找第一个有该设备的房间
            for room_id, devices in DEFAULT_ROOM_DEVICES.items():
                if device_type in devices:
                    device_key = f"{room_id}_{device_type}"
                    current_state = self.state_manager.get_state(device_key)
                    action = 'off' if current_state else 'on'
                    return self._execute_device_command(device_type, action, room_id)
        
        return False, "未识别的手势"
    
    def get_active_device(self):
        """获取一个活跃设备"""
        states = self.state_manager.get_all_states()
        for device, state in states.items():
            if state:
                return device
        return 'living_light'
    
    def get_history(self, limit=10):
        """获取命令历史"""
        return self.command_history[-limit:]
    
    def clear_history(self):
        """清空命令历史"""
        self.command_history = []
        self.logger.info("指令历史已清空")
    
    def get_supported_commands(self):
        """获取支持的所有命令"""
        commands = []
        for device_type, actions in DEVICE_COMMANDS.items():
            for action, cmd_list in actions.items():
                for cmd in cmd_list:
                    commands.append({
                        'device': device_type,
                        'action': action,
                        'command': cmd
                    })
        return commands
