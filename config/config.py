import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

DEVICE_COMMANDS = {
    'light': ['打开灯', '关闭灯', '开灯', '关灯', '灯开', '灯关'],
    'aircon': ['打开空调', '关闭空调', '开空调', '关空调', '空调开', '空调关'],
    'fan': ['打开风扇', '关闭风扇', '开风扇', '关风扇', '风扇开', '风扇关'],
    'tv': ['打开电视', '关闭电视', '开电视', '关电视', '电视开', '电视关'],
    'curtain': ['打开窗帘', '关闭窗帘', '开窗帘', '关窗帘', '窗帘开', '窗帘关']
}

GESTURE_DEVICE_MAP = {
    'one': 'light',
    'two': 'aircon',
    'three': 'fan',
    'four': 'tv',
    'five': 'curtain'
}

DEVICE_STATES = {
    'light': False,
    'aircon': False,
    'fan': False,
    'tv': False,
    'curtain': False
}

DEVICE_NAMES = {
    'light': '灯',
    'aircon': '空调',
    'fan': '风扇',
    'tv': '电视',
    'curtain': '窗帘'
}

LOG_LEVEL = 'INFO'
VOICE_TIMEOUT = 5
GESTURE_FPS = 30

BAIDU_ASR_CONFIG = {
    'APP_ID': '28101621',
    'API_KEY': 'Gl753XPEl0cbKkSROwLrvYow',
    'SECRET_KEY': 'R6wipYNLt1p85GHLtT5pWMumwlU3wQzx',
    'CUID': 'qfEfpDoItDEFJ5BSccixkL6bQZvJI6b9',
    'URL': 'https://vop.baidu.com/server_api'
}

LANGUAGE_MODELS = {
    'mandarin': {'name': '普通话', 'dev_pid': 1537, 'description': '纯中文识别 - 语音近场识别模型'},
    'english': {'name': '英语', 'dev_pid': 1737, 'description': '英语模型'},
    'cantonese': {'name': '粤语', 'dev_pid': 1637, 'description': '粤语模型'},
    'sichuan': {'name': '四川话', 'dev_pid': 1837, 'description': '四川话模型'}
}

ERNIE_SPEECH_CONFIG = {
    'API_KEY': BAIDU_ASR_CONFIG['API_KEY'],
    'SECRET_KEY': BAIDU_ASR_CONFIG['SECRET_KEY'],
    'TOKEN_URL': 'https://aip.baidubce.com/oauth/2.0/token',
    'ASR_URL': 'https://vop.baidu.com/server_api',
    'NLP_URL': 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/solution/180561',
    'TTS_URL': 'https://tsn.baidu.com/text2audio'
}

WEATHER_CONFIG = {
    'API_KEY': BAIDU_ASR_CONFIG['API_KEY'],
    'URL': 'https://api.map.baidu.com/weather/v1/',
    'AK': BAIDU_ASR_CONFIG['API_KEY'],
    'LOCATION': '北京'
}

WAKE_WORDS = ['小度小度', '管家管家', '智能管家', '你好管家']

SCENE_RULES = {
    'morning': {
        'trigger': ['起床', '早上好', '早安'],
        'suggestions': ['打开窗帘', '打开灯', '播放音乐'],
        'time_range': '06:00-10:00'
    },
    'night': {
        'trigger': ['睡觉', '晚安', '关灯睡觉'],
        'suggestions': ['关闭灯', '关闭电视', '关闭风扇'],
        'time_range': '21:00-06:00'
    },
    'cold': {
        'trigger': ['冷', '太冷了', '有点凉'],
        'suggestions': ['打开空调', '提高温度', '关闭窗户'],
        'condition': {'temperature': {'lt': 20}}
    },
    'hot': {
        'trigger': ['热', '太热了', '有点闷'],
        'suggestions': ['打开空调', '降低温度', '打开风扇'],
        'condition': {'temperature': {'gt': 28}}
    }
}
