import requests
import json
import time
import base64
import os
import uuid
import threading
import re
from datetime import datetime
from config.config import ERNIE_SPEECH_CONFIG, WEATHER_CONFIG, WAKE_WORDS, SCENE_RULES, DEVICE_COMMANDS, BAIDU_ASR_CONFIG, DEEPSEEK_CONFIG, ROOMS, DEVICE_TYPES, DEFAULT_ROOM_DEVICES
from config.prompt_config import SYSTEM_PROMPT, INITIAL_QUESTIONS, SCENE_PROMPTS, EMOTION_RESPONSES, WEATHER_ACTIONS, CONTEXT_TEMPLATE, DEVICE_LIST_TEMPLATE
from modules.deepseek_client import DeepSeekClient
from PyQt5.QtCore import QObject, pyqtSignal

class SmartAssistant(QObject):
    suggestion_ready = pyqtSignal(str, list)
    weather_updated = pyqtSignal(dict)
    intent_detected = pyqtSignal(str, dict)
    speak_ready = pyqtSignal(str)
    command_ready = pyqtSignal(str)  # 新信号：传递解析出的指令
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self._access_token = None
        self._token_expire_time = 0
        self.current_weather = {}
        self.last_suggestions = []
        self.tts_enabled = True
        
        self._deepseek_client = None
        self._use_deepseek = False
        self._init_deepseek()
        
        # 当前房间信息
        self.current_room_id = 'living'
        self.device_manager = None
    
    def set_device_manager(self, device_manager):
        """设置设备管理器"""
        self.device_manager = device_manager
    
    def set_current_room(self, room_id):
        """设置当前房间"""
        self.current_room_id = room_id
        self.logger.info(f"当前房间已更新: {room_id} -> {ROOMS.get(room_id, {}).get('name', room_id)}")
        
    def _get_access_token(self):
        now = time.time()
        if self._access_token and now < self._token_expire_time:
            return self._access_token
        
        url = f"{ERNIE_SPEECH_CONFIG['TOKEN_URL']}?grant_type=client_credentials&client_id={ERNIE_SPEECH_CONFIG['API_KEY']}&client_secret={ERNIE_SPEECH_CONFIG['SECRET_KEY']}"
        
        try:
            response = requests.get(url)
            result = response.json()
            
            if 'access_token' in result:
                self._access_token = result['access_token']
                self._token_expire_time = now + result.get('expires_in', 3600) - 60
                self.logger.info(f"获取百度API Token成功，有效期: {result.get('expires_in', 3600)}秒")
                return self._access_token
            else:
                self.logger.error(f"获取Token失败: {result.get('error_description', '未知错误')}")
                return None
        except Exception as e:
            self.logger.error(f"获取Token异常: {str(e)}")
            return None
    
    def check_wake_word(self, text):
        for wake_word in WAKE_WORDS:
            if wake_word in text:
                self.logger.info(f"检测到唤醒词: {wake_word}")
                return True, wake_word
        return False, None
    
    def extract_command_after_wake(self, text):
        for wake_word in WAKE_WORDS:
            if wake_word in text:
                return text.replace(wake_word, '').strip()
        return text
    
    def query_weather(self):
        try:
            url = "https://wttr.in/Beijing?format=j1"
            response = requests.get(url, timeout=10)
            result = response.json()
            
            if 'current_condition' in result:
                current = result['current_condition'][0]
                tomorrow = result['weather'][0]['mintempC'] + '°C'
                today_high = result['weather'][0]['maxtempC'] + '°C'
                
                self.current_weather = {
                    'temperature': current['temp_C'],
                    'weather': current['weatherDesc'][0]['value'],
                    'wind': current['winddir16Point'] + ' ' + current['windspeedKmph'] + 'km/h',
                    'humidity': current['humidity'],
                    'today_high': today_high,
                    'today_low': tomorrow,
                    'city': '北京'
                }
                self.weather_updated.emit(self.current_weather)
                self.logger.info(f"天气查询成功: {self.current_weather}")
                return self.current_weather
            else:
                self.logger.error(f"天气查询失败: {result}")
                return None
        except Exception as e:
            self.logger.error(f"天气查询异常: {str(e)}")
            return None
    
    def analyze_intent(self, text):
        intents = []
        
        time_keywords = ['时间', '几点', '现在', 'time', 'what time', 'clock', "what's the time"]
        if any(keyword in text.lower() for keyword in time_keywords):
            intents.append(('query_time', '查询时间'))
        
        weather_keywords = ['天气', '温度', '冷', '热', 'weather', 'temperature', 'cold', 'hot', 'warm', 'cool']
        if any(keyword in text.lower() for keyword in weather_keywords):
            intents.append(('query_weather', '查询天气'))
        
        for device, commands in DEVICE_COMMANDS.items():
            for cmd in commands:
                if cmd.lower() in text.lower():
                    intents.append(('control_device', f'控制设备: {device}'))
                    break
        
        if any(keyword in text for keyword in ['建议', '推荐', '帮我', 'suggest', 'recommend', 'help']):
            intents.append(('get_suggestion', '获取建议'))
        
        if intents:
            self.intent_detected.emit(text, {'intents': intents})
        
        return intents
    
    def get_scene_suggestions(self, text):
        suggestions = []
        current_hour = datetime.now().hour
        current_temp = int(self.current_weather.get('temperature', 25))
        
        for scene_id, scene in SCENE_RULES.items():
            triggers = scene.get('trigger', [])
            matched = any(trigger in text for trigger in triggers)
            
            if matched:
                time_range = scene.get('time_range', '')
                time_ok = True
                
                if time_range:
                    start_str, end_str = time_range.split('-')
                    start_hour = int(start_str.split(':')[0])
                    end_hour = int(end_str.split(':')[0])
                    
                    if start_hour < end_hour:
                        time_ok = start_hour <= current_hour < end_hour
                    else:
                        time_ok = current_hour >= start_hour or current_hour < end_hour
                
                condition = scene.get('condition', {})
                cond_ok = True
                
                if 'temperature' in condition:
                    temp_cond = condition['temperature']
                    if 'lt' in temp_cond and current_temp >= temp_cond['lt']:
                        cond_ok = False
                    if 'gt' in temp_cond and current_temp <= temp_cond['gt']:
                        cond_ok = False
                
                if time_ok and cond_ok:
                    suggestions.extend(scene.get('suggestions', []))
        
        if suggestions:
            self.suggestion_ready.emit(text, suggestions)
            self.last_suggestions = suggestions
        
        return suggestions
    
    def get_time_response(self):
        now = datetime.now()
        return f"现在是 {now.strftime('%Y年%m月%d日 %H时%M分')}"
    
    def get_weather_response(self):
        if not self.current_weather:
            self.query_weather()
        
        if self.current_weather:
            w = self.current_weather
            return f"{w['city']}当前天气{w['weather']}，温度{w['temperature']}，湿度{w['humidity']}%，风向{w['wind']}，今日气温{w['today_low']}到{w['today_high']}"
        return "暂时无法获取天气信息"
    
    def process_text(self, text):
        is_wake, wake_word = self.check_wake_word(text)
        
        if is_wake:
            command = self.extract_command_after_wake(text)
            self.logger.info(f"唤醒成功，命令: {command}")
        else:
            command = text
        
        intents = self.analyze_intent(command)
        responses = []
        
        for intent_type, intent_desc in intents:
            if intent_type == 'query_time':
                responses.append(self.get_time_response())
            elif intent_type == 'query_weather':
                responses.append(self.get_weather_response())
            elif intent_type == 'get_suggestion':
                suggestions = self.get_scene_suggestions(command)
                if suggestions:
                    responses.append(f"根据您的需求，我建议：{'、'.join(suggestions)}")
            elif intent_type == 'control_device':
                pass
        
        if not responses:
            suggestions = self.get_scene_suggestions(command)
            if suggestions:
                responses.append(f"我来帮您处理，同时建议：{'、'.join(suggestions)}")
        
        if responses and self.tts_enabled:
            main_response = responses[0]
            self.speak(main_response)
        
        return is_wake, command, responses
    
    def speak(self, text):
        try:
            access_token = self._get_access_token()
            if not access_token:
                self.logger.error("无法获取Token进行语音合成")
                return None
            
            url = f"{ERNIE_SPEECH_CONFIG['TTS_URL']}?tok={access_token}&tex={requests.utils.quote(text)}&per=4115&spd=5&pit=6&vol=6&aue=3&cuid={BAIDU_ASR_CONFIG['CUID']}&lan=zh&ctp=1"
            
            response = requests.get(url)
            
            if response.headers.get('Content-Type') == 'audio/mp3':
                audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_audio')
                os.makedirs(audio_dir, exist_ok=True)
                
                audio_path = os.path.join(audio_dir, f'tts_{uuid.uuid4().hex}.mp3')
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"语音合成成功: {text} -> {audio_path}")
                self.speak_ready.emit(audio_path)
                
                threading.Thread(target=self._cleanup_audio_file, args=(audio_path,), daemon=True).start()
                
                return audio_path
            else:
                self.logger.error(f"语音合成失败: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"语音合成异常: {str(e)}")
            return None
    
    def _cleanup_audio_file(self, audio_path):
        """延迟删除临时音频文件"""
        try:
            time.sleep(5)
            if os.path.exists(audio_path):
                os.remove(audio_path)
                self.logger.info(f"已清理临时音频文件: {audio_path}")
        except Exception as e:
            pass
    
    def set_tts_enabled(self, enabled):
        self.tts_enabled = enabled
    
    def _init_deepseek(self):
        """初始化DeepSeek客户端"""
        try:
            self._deepseek_client = DeepSeekClient(DEEPSEEK_CONFIG['API_KEY'])
            self._deepseek_client.set_system_prompt(SYSTEM_PROMPT)
            self._deepseek_client.response_received.connect(self._on_deepseek_response)
            self._deepseek_client.error_occurred.connect(self._on_deepseek_error)
            self.logger.info("DeepSeek客户端初始化成功")
        except Exception as e:
            self.logger.error(f"DeepSeek客户端初始化失败: {str(e)}")
    
    def get_initial_questions(self):
        """获取初始化问题列表"""
        return INITIAL_QUESTIONS
    
    def detect_emotion(self, text):
        """检测用户情绪并返回(响应, 命令列表)"""
        for emotion, data in EMOTION_RESPONSES.items():
            for keyword in data['keywords']:
                if keyword in text:
                    self.logger.info(f"检测到情绪: {emotion}")
                    return data['response'], data.get('commands', [])
        return None, []
    
    def detect_scene(self, text):
        """检测场景并返回(场景名, 场景数据)"""
        for scene, data in SCENE_PROMPTS.items():
            for trigger in data['trigger']:
                if trigger in text:
                    self.logger.info(f"检测到场景: {scene}")
                    return scene, data
        return None, None
    
    def enable_deepseek(self, enable=True):
        """启用/禁用DeepSeek"""
        self._use_deepseek = enable
        if enable:
            if not self._deepseek_client:
                self._init_deepseek()
            self.logger.info("已启用DeepSeek对话")
        else:
            self.logger.info("已禁用DeepSeek对话")
    
    def _build_context(self):
        """构建当前上下文信息"""
        # 获取房间名称
        room_info = ROOMS.get(self.current_room_id, {})
        room_name = room_info.get('name', self.current_room_id)
        
        # 获取房间设备列表
        room_devices = self._get_room_devices(self.current_room_id)
        
        # 获取当前时间
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        # 获取天气信息
        temp = self.current_weather.get('temperature', '--')
        weather = self.current_weather.get('weather', '未知')
        
        # 构建上下文字符串
        context = CONTEXT_TEMPLATE.format(
            room_name=room_name,
            room_devices=room_devices,
            current_time=current_time,
            temperature=temp,
            weather=weather
        )
        
        return context
    
    def _get_room_devices(self, room_id):
        """获取房间设备列表字符串"""
        devices = []
        
        # 从默认配置获取
        if room_id in DEFAULT_ROOM_DEVICES:
            for device_type in DEFAULT_ROOM_DEVICES[room_id]:
                device_info = DEVICE_TYPES.get(device_type, {})
                device_name = device_info.get('name', device_type)
                devices.append(f"- {device_name}")
        
        # 从设备管理器获取自定义设备
        if self.device_manager:
            custom_devices = self.device_manager.get_room_devices(room_id)
            for device_type in custom_devices:
                device_info = self.device_manager.get_device_info(f"{room_id}_{device_type}")
                if device_info:
                    device_name = device_info.get('device_name', device_type)
                    if f"- {device_name}" not in devices:
                        devices.append(f"- {device_name}")
        
        if not devices:
            return "暂无设备"
        
        return '\n'.join(devices)
    
    def _build_device_list(self):
        """构建所有可用设备列表字符串"""
        device_names = []
        for device_type, device_info in DEVICE_TYPES.items():
            device_names.append(f"- {device_info.get('name', device_type)}")
        return '\n'.join(device_names)
    
    def _build_full_prompt(self):
        """构建完整的系统提示词"""
        context = self._build_context()
        device_list = self._build_device_list()
        
        full_prompt = SYSTEM_PROMPT.format(
            context=context,
            device_list=device_list
        )
        
        return full_prompt
    
    def chat_with_deepseek(self, message):
        """与DeepSeek对话（带动态上下文）"""
        if not self._use_deepseek or not self._deepseek_client:
            self.logger.warning("DeepSeek未启用或未初始化")
            return None
        
        # 更新系统提示词（包含当前上下文）
        full_prompt = self._build_full_prompt()
        self._deepseek_client.set_system_prompt(full_prompt)
        
        self.logger.info(f"正在与DeepSeek对话: {message}")
        self.logger.debug(f"上下文信息已更新")
        
        return self._deepseek_client.chat(message)
    
    def _parse_response(self, response):
        """解析DeepSeek响应，分离回复内容和指令"""
        if '|' in response:
            parts = response.split('|', 1)
            reply_text = parts[0].strip()
            command_text = parts[1].strip() if len(parts) > 1 else ''
        else:
            # 如果没有分隔符，全部作为回复内容
            reply_text = response.strip()
            command_text = ''
        
        return reply_text, command_text
    
    def _parse_commands(self, command_text):
        """解析指令文本，提取设备控制指令"""
        commands = []
        
        if not command_text or command_text == '无':
            return commands
        
        # 按逗号分割指令
        command_parts = command_text.split(',')
        
        # 正则匹配：打开xx 或 关闭xx
        pattern = r'(打开|关闭)([\u4e00-\u9fa5]+)'
        
        for part in command_parts:
            part = part.strip()
            if not part:
                continue
            
            match = re.match(pattern, part)
            if match:
                action = match.group(1)  # '打开' 或 '关闭'
                device_name = match.group(2)  # 设备名称
                commands.append({
                    'action': action,
                    'device_name': device_name
                })
                self.logger.info(f"解析到指令: {action} {device_name}")
            else:
                self.logger.warning(f"无法解析指令: {part}")
        
        return commands
    
    def _on_deepseek_response(self, response):
        """DeepSeek响应回调（包含指令解析）"""
        self.logger.info(f"DeepSeek响应: {response[:100]}...")
        
        # 解析响应
        reply_text, command_text = self._parse_response(response)
        
        # 处理回复内容（语音合成）
        if reply_text and self.tts_enabled:
            self.speak(reply_text)
        
        # 解析并执行指令
        commands = self._parse_commands(command_text)
        if commands:
            # 将指令发送给命令系统执行
            self.command_ready.emit(command_text)
            self.logger.info(f"已发送指令: {command_text}")
    
    def _on_deepseek_error(self, error_msg):
        """DeepSeek错误回调"""
        self.logger.error(f"DeepSeek错误: {error_msg}")