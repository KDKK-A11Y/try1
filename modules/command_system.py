from config.config import DEVICE_COMMANDS, DEVICE_NAMES, GESTURE_DEVICE_MAP

class CommandSystem:
    def __init__(self, state_manager, logger):
        self.state_manager = state_manager
        self.logger = logger
        self.command_history = []
        self.gesture_device_map = GESTURE_DEVICE_MAP

    def parse_command(self, command_text):
        command_text = command_text.strip().lower()
        
        for device, commands in DEVICE_COMMANDS.items():
            for cmd in commands:
                if cmd.lower() in command_text:
                    if device == 'all_on':
                        return ('all', 'on')
                    elif device == 'all_off':
                        return ('all', 'off')
                    else:
                        action = 'on' if any(keyword in cmd.lower() for keyword in ['open', 'turn on', '开', '打开', '开']) else 'off'
                        return (device, action)
        
        return (None, None)

    def execute_command(self, device, action):
        if device is None:
            self.logger.warning(f"无法识别指令: {device} {action}")
            return False
        
        if device == 'all':
            devices = ['light', 'aircon', 'fan', 'tv', 'curtain']
            success_count = 0
            for dev in devices:
                if action == 'on':
                    self.state_manager.set_state(dev, True)
                elif action == 'off':
                    self.state_manager.set_state(dev, False)
                success_count += 1
            self.logger.info(f"全部设备{action}成功: {success_count}个设备")
            return success_count > 0
        elif action == 'on':
            self.state_manager.set_state(device, True)
            result = True
        elif action == 'off':
            self.state_manager.set_state(device, False)
            result = True
        elif action == 'toggle':
            self.state_manager.toggle_state(device)
            result = True
        else:
            self.logger.error(f"未知操作: {action}")
            result = False

        if result:
            device_name = DEVICE_NAMES.get(device, device)
            self.command_history.append({
                'device': device_name,
                'action': action,
                'success': result
            })
            self.logger.info(f"指令执行成功: {device_name} {action}")

        return result

    def execute_gesture_command(self, gesture_type):
        if gesture_type in self.gesture_device_map:
            device = self.gesture_device_map[gesture_type]
            current_state = self.state_manager.get_state(device)
            action = 'off' if current_state else 'on'
            return self.execute_command(device, action)

        return False

    def get_active_device(self):
        states = self.state_manager.get_all_states()
        for device, state in states.items():
            if state:
                return device
        return 'light'

    def get_history(self, limit=10):
        return self.command_history[-limit:]

    def clear_history(self):
        self.command_history = []
        self.logger.info("指令历史已清空")