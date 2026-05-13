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
