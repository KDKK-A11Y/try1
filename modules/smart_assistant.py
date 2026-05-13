import requests
import json
import time
from datetime import datetime
from config.config import ERNIE_SPEECH_CONFIG, WEATHER_CONFIG, WAKE_WORDS, SCENE_RULES, DEVICE_COMMANDS
from PyQt5.QtCore import QObject, pyqtSignal

class SmartAssistant(QObject):
    suggestion_ready = pyqtSignal(str, list)
    weather_updated = pyqtSignal(dict)
    intent_detected = pyqtSignal(str, dict)
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self._access_token = None
        self._token_expire_time = 0
        self.current_weather = {}
        self.last_suggestions = []
        
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
            url = f"{WEATHER_CONFIG['URL']}?district_id=110100&data_type=all&ak={WEATHER_CONFIG['AK']}"
            response = requests.get(url)
            result = response.json()
            
            if result.get('status') == 0:
                weather_data = result['result']
                self.current_weather = {
                    'temperature': weather_data['now']['temp'],
                    'weather': weather_data['now']['text'],
                    'wind': weather_data['now']['wind_dir'],
                    'humidity': weather_data['now']['humidity'],
                    'today_high': weather_data['forecasts'][0]['high'],
                    'today_low': weather_data['forecasts'][0]['low'],
                    'city': weather_data['location']['city']
                }
                self.weather_updated.emit(self.current_weather)
                self.logger.info(f"天气查询成功: {self.current_weather}")
                return self.current_weather
            else:
                self.logger.error(f"天气查询失败: {result.get('message', '未知错误')}")
                return None
        except Exception as e:
            self.logger.error(f"天气查询异常: {str(e)}")
            return None
    
    def analyze_intent(self, text):
        intents = []
        
        if any(keyword in text for keyword in ['时间', '几点', '现在']):
            intents.append(('query_time', '查询时间'))
        
        if any(keyword in text for keyword in ['天气', '温度', '冷', '热']):
            intents.append(('query_weather', '查询天气'))
        
        for device, commands in DEVICE_COMMANDS.items():
            for cmd in commands:
                if cmd in text:
                    intents.append(('control_device', f'控制设备: {device}'))
                    break
        
        if any(keyword in text for keyword in ['建议', '推荐', '帮我']):
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
            return f"{w['city']}当前天气{w['weather']}，温度{w['temperature']}度，湿度{w['humidity']}%，风向{w['wind']}，今日气温{w['today_low']}到{w['today_high']}度"
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
        
        return is_wake, command, responses