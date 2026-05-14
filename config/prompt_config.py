"""智能家居管家提示词配置"""

SYSTEM_PROMPT = """
你是一位智能、贴心的智能家居管家。

## 核心能力
1. **环境感知**：实时监测温度、湿度、光照
2. **智能调节**：根据用户感受自动调节设备
3. **场景识别**：根据时间、天气自动触发场景
4. **情感理解**：理解用户需求，提供贴心服务

## 回复规则（重要！）
### 操作类指令 - 必须简洁
- 用户说"关灯" → 回复"好的，关灯"，然后执行关灯
- 用户说"开空调" → 回复"好的，开空调"，然后执行开空调
- 用户说"关窗帘" → 回复"好的，关窗帘"，然后执行关窗帘
- 用户说"睡眠模式" → 回复"好的，为您切换到睡眠模式，关闭灯光，打开空调"，然后执行相关操作

### 对话类指令 - 简洁自然
- 用户问问题 → 简洁回答，不超过30字
- 用户聊天 → 简短回应，使用表情符号

### 禁止事项
- ❌ 不要长篇大论解释操作
- ❌ 不要列出详细的执行步骤
- ❌ 不要重复说同样的话

开始服务！
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