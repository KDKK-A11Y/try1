import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

# 房间配置
ROOMS = {
    'living': {'name': '客厅', 'icon': '🏠', 'color': '#4a90d9'},
    'bedroom': {'name': '卧室', 'icon': '🛏️', 'color': '#d9654a'},
    'kitchen': {'name': '厨房', 'icon': '🍳', 'color': '#65d94a'},
    'bathroom': {'name': '浴室', 'icon': '🛁', 'color': '#4ad9d9'},
    'study': {'name': '书房', 'icon': '📚', 'color': '#9c4ad9'},
    'garage': {'name': '车库', 'icon': '🚗', 'color': '#666666'}
}

# 设备类型配置
DEVICE_TYPES = {
    # 照明类
    'light': {'name': '灯', 'icon': '💡', 'category': 'lighting', 'power_consumption': 15},
    'rgb_strip': {'name': '灯带', 'icon': '🌈', 'category': 'lighting', 'power_consumption': 20},
    
    # 气候类
    'aircon': {'name': '空调', 'icon': '❄️', 'category': 'climate', 'power_consumption': 1500},
    'fan': {'name': '风扇', 'icon': '🌀', 'category': 'climate', 'power_consumption': 50},
    'heater': {'name': '暖气', 'icon': '🔥', 'category': 'climate', 'power_consumption': 2000},
    'humidifier': {'name': '加湿器', 'icon': '💧', 'category': 'climate', 'power_consumption': 40},
    'dehumidifier': {'name': '除湿机', 'icon': '🍃', 'category': 'climate', 'power_consumption': 300},
    'purifier': {'name': '空气净化器', 'icon': '🌬️', 'category': 'climate', 'power_consumption': 60},
    'air_purifier': {'name': '新风系统', 'icon': '💨', 'category': 'climate', 'power_consumption': 120},
    
    # 娱乐类
    'tv': {'name': '电视', 'icon': '📺', 'category': 'entertainment', 'power_consumption': 100},
    'speaker': {'name': '音响', 'icon': '🔊', 'category': 'entertainment', 'power_consumption': 80},
    'projector': {'name': '投影仪', 'icon': '📽️', 'category': 'entertainment', 'power_consumption': 200},
    
    # 安全类
    'smart_lock': {'name': '智能门锁', 'icon': '🔒', 'category': 'security', 'power_consumption': 5},
    'camera': {'name': '摄像头', 'icon': '📷', 'category': 'security', 'power_consumption': 10},
    'door_sensor': {'name': '门磁传感器', 'icon': '🚪', 'category': 'security', 'power_consumption': 2},
    'motion_sensor': {'name': '人体传感器', 'icon': '👤', 'category': 'security', 'power_consumption': 3},
    'smoke_detector': {'name': '烟雾报警器', 'icon': '🚨', 'category': 'security', 'power_consumption': 1},
    
    # 家电类
    'water_heater': {'name': '热水器', 'icon': '🛁', 'category': 'appliance', 'power_consumption': 1500},
    'oven': {'name': '烤箱', 'icon': '🍞', 'category': 'appliance', 'power_consumption': 2000},
    'microwave': {'name': '微波炉', 'icon': '🧊', 'category': 'appliance', 'power_consumption': 800},
    'refrigerator': {'name': '冰箱', 'icon': '❄️', 'category': 'appliance', 'power_consumption': 150},
    'washing_machine': {'name': '洗衣机', 'icon': '👕', 'category': 'appliance', 'power_consumption': 500},
    'dishwasher': {'name': '洗碗机', 'icon': '🍽️', 'category': 'appliance', 'power_consumption': 1200},
    'coffee_maker': {'name': '咖啡机', 'icon': '☕', 'category': 'appliance', 'power_consumption': 800},
    
    # 清洁类
    'robot_vacuum': {'name': '扫地机器人', 'icon': '🤖', 'category': 'cleaning', 'power_consumption': 80},
    
    # 窗户类
    'curtain': {'name': '窗帘', 'icon': '🪟', 'category': 'window', 'power_consumption': 30},
    
    # 电源类
    'smart_socket': {'name': '智能插座', 'icon': '🔌', 'category': 'power', 'power_consumption': 0},
    
    # 水务类
    'water_valve': {'name': '智能水阀', 'icon': '🚰', 'category': 'water', 'power_consumption': 10}
}

# 默认房间设备配置
DEFAULT_ROOM_DEVICES = {
    'living': ['light', 'tv', 'speaker', 'aircon', 'curtain', 'purifier'],
    'bedroom': ['light', 'aircon', 'curtain', 'humidifier', 'heater'],
    'kitchen': ['light', 'oven', 'microwave', 'refrigerator', 'coffee_maker', 'smart_socket'],
    'bathroom': ['light', 'water_heater', 'humidifier', 'door_sensor'],
    'study': ['light', 'aircon', 'speaker', 'rgb_strip'],
    'garage': ['light', 'smart_lock', 'camera']
}

# 设备控制命令（中文和英文）
DEVICE_COMMANDS = {
    'light': {
        'on': ['打开灯', '开灯', '灯开', '开灯吧', '开个灯', '灯打开', 'turn on the light', 'light on', 'switch on light', 'open light'],
        'off': ['关闭灯', '关灯', '灯关', '关灯吧', '灯关闭', 'turn off the light', 'light off', 'switch off light', 'close light'],
        'toggle': ['切换灯', '灯切换', 'light toggle']
    },
    'aircon': {
        'on': ['打开空调', '开空调', '空调开', '开空调吧', '空调打开', 'turn on the aircon', 'aircon on', 'turn on ac', 'ac on'],
        'off': ['关闭空调', '关空调', '空调关', '关空调吧', '空调关闭', 'turn off the aircon', 'aircon off', 'turn off ac', 'ac off'],
        'toggle': ['切换空调', '空调切换', 'aircon toggle'],
        'cool': ['制冷', '开制冷', '制冷模式', 'cool mode', 'cooling'],
        'heat': ['制热', '开制热', '制热模式', 'heat mode', 'heating'],
        'auto': ['自动', '自动模式', 'auto mode'],
        'temp_up': ['温度升高', '升温', '调高温度', 'increase temperature', 'temp up'],
        'temp_down': ['温度降低', '降温', '调低温度', 'decrease temperature', 'temp down']
    },
    'fan': {
        'on': ['打开风扇', '开风扇', '风扇开', '开风扇吧', '风扇打开', 'turn on the fan', 'fan on', 'switch on fan'],
        'off': ['关闭风扇', '关风扇', '风扇关', '关风扇吧', '风扇关闭', 'turn off the fan', 'fan off', 'switch off fan'],
        'toggle': ['切换风扇', '风扇切换', 'fan toggle'],
        'speed_up': ['风速加大', '加大风速', 'increase fan speed', 'fan speed up'],
        'speed_down': ['风速减小', '减小风速', 'decrease fan speed', 'fan speed down']
    },
    'tv': {
        'on': ['打开电视', '开电视', '电视开', '开电视吧', '电视打开', 'turn on the tv', 'tv on', 'switch on tv'],
        'off': ['关闭电视', '关电视', '电视关', '关电视吧', '电视关闭', 'turn off the tv', 'tv off', 'switch off tv'],
        'toggle': ['切换电视', '电视切换', 'tv toggle'],
        'volume_up': ['音量加大', '加大音量', 'increase volume', 'volume up'],
        'volume_down': ['音量减小', '减小音量', 'decrease volume', 'volume down'],
        'channel_up': ['换台', '上一台', 'channel up', 'next channel'],
        'channel_down': ['下一台', 'channel down', 'previous channel']
    },
    'curtain': {
        'open': ['打开窗帘', '开窗帘', '窗帘开', '窗帘打开', 'open curtain', 'curtain open'],
        'close': ['关闭窗帘', '关窗帘', '窗帘关', '窗帘关闭', 'close curtain', 'curtain close'],
        'toggle': ['切换窗帘', '窗帘切换', 'curtain toggle'],
        'half': ['半开', '窗帘半开', 'half open', 'curtain half']
    },
    'heater': {
        'on': ['打开暖气', '开暖气', '暖气开', '暖气打开', 'turn on heater', 'heater on'],
        'off': ['关闭暖气', '关暖气', '暖气关', '暖气关闭', 'turn off heater', 'heater off'],
        'toggle': ['切换暖气', '暖气切换', 'heater toggle']
    },
    'humidifier': {
        'on': ['打开加湿器', '开加湿器', '加湿器开', 'humidifier on', 'turn on humidifier'],
        'off': ['关闭加湿器', '关加湿器', '加湿器关', 'humidifier off', 'turn off humidifier'],
        'toggle': ['切换加湿器', 'humidifier toggle']
    },
    'dehumidifier': {
        'on': ['打开除湿机', '开除湿机', '除湿机开', 'dehumidifier on', 'turn on dehumidifier'],
        'off': ['关闭除湿机', '关除湿机', '除湿机关', 'dehumidifier off', 'turn off dehumidifier'],
        'toggle': ['切换除湿机', 'dehumidifier toggle']
    },
    'purifier': {
        'on': ['打开净化器', '开净化器', '净化器开', 'purifier on', 'turn on purifier'],
        'off': ['关闭净化器', '关净化器', '净化器关', 'purifier off', 'turn off purifier'],
        'toggle': ['切换净化器', 'purifier toggle']
    },
    'speaker': {
        'on': ['打开音响', '开音响', '音响开', 'speaker on', 'turn on speaker'],
        'off': ['关闭音响', '关音响', '音响关', 'speaker off', 'turn off speaker'],
        'toggle': ['切换音响', 'speaker toggle'],
        'volume_up': ['音响音量加大', 'increase speaker volume', 'speaker volume up'],
        'volume_down': ['音响音量减小', 'decrease speaker volume', 'speaker volume down']
    },
    'projector': {
        'on': ['打开投影仪', '开投影仪', '投影仪开', 'projector on', 'turn on projector'],
        'off': ['关闭投影仪', '关投影仪', '投影仪关', 'projector off', 'turn off projector'],
        'toggle': ['切换投影仪', 'projector toggle']
    },
    'robot_vacuum': {
        'on': ['开始扫地', '扫地机器人开始', 'start cleaning', 'robot vacuum on'],
        'off': ['停止扫地', '扫地机器人停止', 'stop cleaning', 'robot vacuum off'],
        'return': ['返回充电', '扫地机器人回家', 'return home', 'charge']
    },
    'smart_lock': {
        'lock': ['锁门', '上锁', 'lock door', 'lock'],
        'unlock': ['开门', '解锁', 'unlock door', 'unlock']
    },
    'camera': {
        'on': ['打开摄像头', '开摄像头', 'camera on', 'turn on camera'],
        'off': ['关闭摄像头', '关摄像头', 'camera off', 'turn off camera'],
        'toggle': ['切换摄像头', 'camera toggle'],
        'record': ['开始录像', 'start recording', 'record'],
        'snapshot': ['拍照', 'take photo', 'snapshot']
    },
    'water_heater': {
        'on': ['打开热水器', '开热水器', '热水器开', 'water heater on', 'turn on water heater'],
        'off': ['关闭热水器', '关热水器', '热水器关', 'water heater off', 'turn off water heater'],
        'toggle': ['切换热水器', 'water heater toggle']
    },
    'oven': {
        'on': ['打开烤箱', '开烤箱', '烤箱开', 'oven on', 'turn on oven'],
        'off': ['关闭烤箱', '关烤箱', '烤箱关', 'oven off', 'turn off oven'],
        'toggle': ['切换烤箱', 'oven toggle']
    },
    'microwave': {
        'on': ['打开微波炉', '开微波炉', '微波炉开', 'microwave on', 'turn on microwave'],
        'off': ['关闭微波炉', '关微波炉', '微波炉关', 'microwave off', 'turn off microwave'],
        'toggle': ['切换微波炉', 'microwave toggle']
    },
    'refrigerator': {
        'on': ['打开冰箱', '开冰箱', '冰箱开', 'refrigerator on', 'turn on fridge'],
        'off': ['关闭冰箱', '关冰箱', '冰箱关', 'refrigerator off', 'turn off fridge'],
        'toggle': ['切换冰箱', 'refrigerator toggle']
    },
    'washing_machine': {
        'on': ['打开洗衣机', '开洗衣机', '洗衣机开', 'start washing', 'washing machine on'],
        'off': ['关闭洗衣机', '关洗衣机', '洗衣机关', 'stop washing', 'washing machine off'],
        'toggle': ['切换洗衣机', 'washing machine toggle']
    },
    'dishwasher': {
        'on': ['打开洗碗机', '开洗碗机', '洗碗机开', 'start dishwasher', 'dishwasher on'],
        'off': ['关闭洗碗机', '关洗碗机', '洗碗机关', 'stop dishwasher', 'dishwasher off'],
        'toggle': ['切换洗碗机', 'dishwasher toggle']
    },
    'coffee_maker': {
        'on': ['打开咖啡机', '开咖啡机', '咖啡机开', 'brew coffee', 'coffee maker on'],
        'off': ['关闭咖啡机', '关咖啡机', '咖啡机关', 'coffee maker off'],
        'toggle': ['切换咖啡机', 'coffee maker toggle']
    },
    'air_purifier': {
        'on': ['打开新风系统', '开新风', '新风开', 'air purifier on', 'turn on air purifier'],
        'off': ['关闭新风系统', '关新风', '新风关', 'air purifier off', 'turn off air purifier'],
        'toggle': ['切换新风', 'air purifier toggle']
    },
    'rgb_strip': {
        'on': ['打开灯带', '开灯带', '灯带开', 'rgb strip on', 'turn on rgb'],
        'off': ['关闭灯带', '关灯带', '灯带关', 'rgb strip off', 'turn off rgb'],
        'toggle': ['切换灯带', 'rgb toggle'],
        'color': ['变色', 'change color', 'rgb color']
    },
    'smart_socket': {
        'on': ['打开插座', '开插座', '插座开', 'smart socket on', 'turn on socket'],
        'off': ['关闭插座', '关插座', '插座关', 'smart socket off', 'turn off socket'],
        'toggle': ['切换插座', 'socket toggle']
    },
    'water_valve': {
        'open': ['打开水阀', '开水阀', 'water valve open', 'open valve'],
        'close': ['关闭水阀', '关水阀', 'water valve close', 'close valve']
    }
}

# 房间控制命令
ROOM_COMMANDS = {
    'all_on': {
        'commands': ['全部打开', '全部开启', '打开所有', 'turn on all', 'all on', 'switch on all']
    },
    'all_off': {
        'commands': ['全部关闭', '全部关掉', '关闭所有', 'turn off all', 'all off', 'switch off all']
    },
    'good_morning': {
        'commands': ['早上好', '早安', 'good morning', 'morning'],
        'actions': [{'device': 'curtain', 'action': 'open'}, {'device': 'light', 'action': 'on'}]
    },
    'good_night': {
        'commands': ['晚安', '睡觉', 'good night', 'night'],
        'actions': [{'device': 'curtain', 'action': 'close'}, {'device': 'light', 'action': 'off'}, {'device': 'tv', 'action': 'off'}]
    },
    'leave_home': {
        'commands': ['出门', '离开家', 'leave home', 'going out'],
        'actions': [{'device': 'light', 'action': 'off'}, {'device': 'tv', 'action': 'off'}, {'device': 'curtain', 'action': 'close'}, {'device': 'smart_lock', 'action': 'lock'}]
    },
    'come_home': {
        'commands': ['回家', '我回来了', 'come home', 'im home'],
        'actions': [{'device': 'light', 'action': 'on'}, {'device': 'smart_lock', 'action': 'unlock'}]
    }
}

# 手势映射
GESTURE_DEVICE_MAP = {
    'one': 'light',
    'two': 'aircon',
    'three': 'fan',
    'four': 'tv',
    'five': 'curtain',
    'six': 'speaker',
    'seven': 'purifier',
    'eight': 'smart_lock'
}

# 初始设备状态
DEVICE_STATES = {}

# 设备名称显示
DEVICE_NAMES = {}

# 初始化设备状态和名称
for room_id, devices in DEFAULT_ROOM_DEVICES.items():
    for device_type in devices:
        device_key = f"{room_id}_{device_type}"
        DEVICE_STATES[device_key] = False
        DEVICE_NAMES[device_key] = f"{ROOMS[room_id]['name']}{DEVICE_TYPES[device_type]['name']}"

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

WAKE_WORDS = ['小度小度', '管家管家', '智能管家', '你好管家', 'Hey Assistant', 'Hello Assistant']

SCENE_RULES = {
    'morning': {
        'trigger': ['起床', '早上好', '早安', 'good morning'],
        'suggestions': ['打开窗帘', '打开灯', '播放音乐'],
        'time_range': '06:00-10:00'
    },
    'night': {
        'trigger': ['睡觉', '晚安', 'good night'],
        'suggestions': ['关闭灯', '关闭电视', '关闭风扇'],
        'time_range': '21:00-06:00'
    },
    'cold': {
        'trigger': ['冷', '太冷了', '有点凉', 'cold'],
        'suggestions': ['打开空调', '提高温度', '关闭窗户'],
        'condition': {'temperature': {'lt': 20}}
    },
    'hot': {
        'trigger': ['热', '太热了', '有点闷', 'hot'],
        'suggestions': ['打开空调', '降低温度', '打开风扇'],
        'condition': {'temperature': {'gt': 28}}
    },
    'air_quality': {
        'trigger': ['空气不好', '雾霾', '空气质量差'],
        'suggestions': ['打开净化器', '打开新风系统'],
        'condition': {'air_quality': {'gt': 150}}
    }
}

DEEPSEEK_CONFIG = {
    'API_KEY': 'sk-2a6c01cbefab4dd2af34c35336fb74c9',
    'MODEL': 'deepseek-v4-pro',
    'SYSTEM_PROMPT': '你是一个智能管家助手，精通中文和英文，善于理解用户意图并提供友好、专业的回答。'
}
