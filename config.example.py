# 配置文件示例
# 复制此文件为 config.py 并填入你的API密钥
# 注意: config.py 已在 .gitignore 中，不会上传到Git

# OpenWeatherMap API配置
# 免费注册获取: https://openweathermap.org/api
OPENWEATHER_API_KEY = "your_openweather_api_key_here"

# Telegram Bot配置
# 创建Bot: 在Telegram中搜索 @BotFather，发送 /newbot
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token_here"
# 获取Chat ID: 向你的bot发送消息，然后访问 https://api.telegram.org/bot<TOKEN>/getUpdates
TELEGRAM_CHAT_ID = "your_chat_id_here"

# 北京城市配置
CITY_NAME = "Beijing"
CITY_ID = 1816670  # OpenWeatherMap的北京城市ID

# 极端天气阈值配置
EXTREME_WEATHER_THRESHOLDS = {
    "high_temp": 35,      # 高温预警阈值 (°C)
    "low_temp": -10,      # 低温预警阈值 (°C)
    "high_wind": 10,      # 大风预警阈值 (m/s)
    "heavy_rain": 50,     # 暴雨预警阈值 (mm/3h)
    "heavy_snow": 10,     # 大雪预警阈值 (mm/3h)
}

# 监控间隔（秒）
CHECK_INTERVAL = 3600  # 默认每小时检查一次

