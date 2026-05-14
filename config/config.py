import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

DEVICE_COMMANDS = {
    'light': ['打开灯', '关闭灯', '开灯', '关灯', '灯开', '灯关', '开灯吧', '关灯吧', '开个灯', '灯打开', '灯关闭',
              'turn on the light', 'turn off the light', 'switch on light', 'switch off light', 'light on', 'light off', 'open light', 'close light'],
    'aircon': ['打开空调', '关闭空调', '开空调', '关空调', '空调开', '空调关', '开空调吧', '关空调吧', '开个空调', '空调打开', '空调关闭',
               'turn on the aircon', 'turn off the aircon', 'aircon on', 'aircon off', 'switch on aircon', 'switch off aircon', 'turn on air conditioning', 'turn off air conditioning', 'ac on', 'ac off'],
    'fan': ['打开风扇', '关闭风扇', '开风扇', '关风扇', '风扇开', '风扇关', '开风扇吧', '关风扇吧', '开个风扇', '风扇打开', '风扇关闭',
            'turn on the fan', 'turn off the fan', 'fan on', 'fan off', 'switch on fan', 'switch off fan', 'open fan', 'close fan'],
    'tv': ['打开电视', '关闭电视', '开电视', '关电视', '电视开', '电视关', '开电视吧', '关电视吧', '开个电视', '电视打开', '电视关闭',
           'turn on the tv', 'turn off the tv', 'tv on', 'tv off', 'switch on tv', 'switch off tv', 'turn on television', 'turn off television'],
    'curtain': ['打开窗帘', '关闭窗帘', '开窗帘', '关窗帘', '窗帘开', '窗帘关', '开窗帘吧', '关窗帘吧', '开个窗帘', '窗帘打开', '窗帘关闭',
                'open curtain', 'close curtain', 'turn on curtain', 'turn off curtain', 'curtain on', 'curtain off'],
    'all_on': ['全部打开', '全部开启', '全部开', '都打开', '都开启', '都开', '打开所有', '开启所有',
               'turn on all', 'turn all on', 'switch on all', 'all on', 'open all'],
    'all_off': ['全部关掉', '全部关闭', '全部关', '都关掉', '都关闭', '都关', '关闭所有', '关掉所有',
                'turn off all', 'turn all off', 'switch off all', 'all off', 'close all', 'shut off all']
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

PORCUPINE_CONFIG = {
    'ACCESS_KEY': '',
    'KEYWORDS': ['computer'],
    'COOLDOWN_SECONDS': 3
}

WEATHER_CONFIG = {
    'URL': 'https://api.map.baidu.com/weather/v1/',
    'AK': 'K82Pmm3n1RQAaHEDyk2AVAt9MlfgrIFZ',
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
