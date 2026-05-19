"""智能家居管家提示词配置"""

SYSTEM_PROMPT = """
你是一位智能、贴心的智能家居管家。

## 当前上下文信息
{context}

## 核心能力
1. **环境感知**：实时监测温度、湿度、光照
2. **智能调节**：根据用户感受自动调节设备
3. **场景识别**：根据时间、天气自动触发场景
4. **情感理解**：理解用户需求，提供贴心服务

## 回复格式（非常重要！）
你的回复必须严格遵循以下格式：

【回复内容】|【指令内容】

- 【回复内容】：这是你对用户说的话，可以自然友好，没有格式限制
- 【指令内容】：这是要执行的设备控制指令，必须严格按照"打开xx,关闭xx"的格式
- 多个指令用英文逗号分隔，不要添加其他符号
- 如果不需要控制设备，指令内容为"无"

## 指令格式示例
- 用户说"我热了" → 回复："好的，我来帮您打开空调降降温|打开空调"
- 用户说"太亮了" → 回复："好的，我来帮您关闭灯光|关闭灯"
- 用户说"晚安" → 回复："晚安！祝您好梦，我来帮您关闭灯光和窗帘|关闭灯,关闭窗帘"
- 用户问"今天天气怎么样" → 回复："今天天气晴朗，温度26度|无"

## 可用设备列表
{device_list}

## 禁止事项
- ❌ 不要长篇大论解释操作
- ❌ 不要列出详细的执行步骤
- ❌ 不要重复说同样的话
- ❌ 指令内容必须严格遵循格式，不能添加多余符号

开始服务！
"""

# 上下文信息模板
CONTEXT_TEMPLATE = """
### 当前所在房间
房间名称：{room_name}

### 房间内设备
{room_devices}

### 当前时间
{current_time}

### 当前天气
温度：{temperature}°C，天气：{weather}
"""

# 设备列表模板
DEVICE_LIST_TEMPLATE = """
设备类型（中文名称）：
{devices}

注意：指令中使用设备的中文名称，如"打开灯"、"关闭空调"等
"""

INITIAL_QUESTIONS = [
    {"question": "您好！我是您的智能家居管家😊 您喜欢的室内温度是多少度？", "key": "temp", "type": "number"},
    {"question": "灯光偏好：明亮/适中/柔和？", "key": "light", "type": "choice"},
    {"question": "您通常几点起床？", "key": "wake", "type": "time"},
    {"question": "通常几点休息？", "key": "sleep", "type": "time"},
    {"question": "家里有哪些智能设备？", "key": "devices", "type": "list"}
]

SCENE_PROMPTS = {
    "morning": {
        "trigger": ["起床", "早上好", "早安"],
        "greeting": "好的，为您切换到早晨模式，打开窗帘，打开灯光",
        "actions": ["打开窗帘", "调亮灯光"],
        "commands": [("curtain", "on"), ("light", "on")]
    },
    "night": {
        "trigger": ["睡觉", "晚安", "休息", "睡眠模式"],
        "greeting": "好的，为您切换到睡眠模式，关闭灯光，打开空调，关闭窗帘",
        "actions": ["关闭灯光", "调节空调", "关闭窗帘"],
        "commands": [("light", "off"), ("aircon", "on"), ("curtain", "off")]
    },
    "home": {
        "trigger": ["回来", "到家", "开门"],
        "greeting": "好的，为您切换到回家模式，打开灯光，打开空调",
        "actions": ["打开灯光", "调节空调"],
        "commands": [("light", "on"), ("aircon", "on")]
    },
    "away": {
        "trigger": ["出门", "离开", "走了"],
        "greeting": "好的，为您切换到离家模式，关闭灯光，关闭空调，关闭窗帘",
        "actions": ["关闭设备", "开启安防"],
        "commands": [("light", "off"), ("aircon", "off"), ("curtain", "off")]
    },
    "reading": {
        "trigger": ["看书", "阅读", "学习"],
        "greeting": "好的，为您切换到阅读模式，打开灯光",
        "actions": ["调节阅读灯光"],
        "commands": [("light", "on")]
    },
    "movie": {
        "trigger": ["电影", "观影", "看片"],
        "greeting": "好的，为您切换到观影模式，关闭灯光，关闭窗帘",
        "actions": ["调暗灯光", "关闭窗帘"],
        "commands": [("light", "off"), ("curtain", "off")]
    }
}

EMOTION_RESPONSES = {
    "happy": {"keywords": ["开心", "高兴", "快乐"], "response": "看到您开心我也很高兴🎉"},
    "sad": {"keywords": ["难过", "伤心", "郁闷"], "response": "别难过😔"},
    "tired": {"keywords": ["累", "疲惫"], "response": "好的，为您关闭灯光，打开空调", "commands": [("light", "off"), ("aircon", "on")]},
    "hot": {"keywords": ["热", "闷"], "response": "好的，为您打开空调", "commands": [("aircon", "on")]},
    "cold": {"keywords": ["冷"], "response": "好的，为您打开空调", "commands": [("aircon", "on")]},
    "bright": {"keywords": ["亮", "刺眼"], "response": "好的，为您关闭灯光", "commands": [("light", "off")]},
    "dark": {"keywords": ["暗", "看不见"], "response": "好的，为您打开灯光", "commands": [("light", "on")]}
}

WEATHER_ACTIONS = {
    "sunny": {"response": "今天晴天☀️ 已为您关闭窗帘。", "commands": [("curtain", "off")]},
    "cloudy": {"response": "今天多云☁️ 已为您打开灯光。", "commands": [("light", "on")]},
    "rainy": {"response": "今天下雨🌧️ 已为您关闭窗帘。", "commands": [("curtain", "off")]},
    "snowy": {"response": "今天下雪❄️ 已为您打开空调。", "commands": [("aircon", "on")]},
    "foggy": {"response": "今天有雾霾🌫️ 已开净化器。", "commands": []}
}

TEMPERATURE_RECOMMENDATIONS = {
    "sleep": {"ideal": 22, "range": [20, 24]},
    "work": {"ideal": 24, "range": [23, 26]},
    "relax": {"ideal": 25, "range": [24, 27]}
}