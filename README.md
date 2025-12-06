# 北京天气监控系统

监控北京天气，当预报出现极端天气时，通过 Telegram 及时推送通知。

## 功能特性

- 🌡️ 实时监控北京天气
- ⚠️ 极端天气自动预警
  - 高温预警（>35°C）
  - 低温预警（<-10°C）
  - 大风预警（>10m/s）
  - 暴雨预警
  - 大雪预警
  - 雷暴、冰冻、大雾等特殊天气
- 📱 Telegram 即时推送
- 🔄 可配置的监控间隔

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API

编辑 `config.py` 文件：

#### 获取 OpenWeatherMap API Key
1. 访问 https://openweathermap.org/api
2. 注册账号（免费）
3. 在 API Keys 页面获取你的 Key

#### 创建 Telegram Bot
1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 获取 Bot Token

#### 获取 Telegram Chat ID
1. 向你的 Bot 发送一条消息
2. 访问 `https://api.telegram.org/bot<你的Token>/getUpdates`
3. 在返回的 JSON 中找到 `chat.id`

### 3. 运行程序

```bash
# 测试连接
python weather_monitor.py test

# 执行一次检查
python weather_monitor.py once

# 持续监控模式
python weather_monitor.py
```

## 配置说明

在 `config.py` 中可以自定义：

```python
# 极端天气阈值
EXTREME_WEATHER_THRESHOLDS = {
    "high_temp": 35,      # 高温预警阈值 (°C)
    "low_temp": -10,      # 低温预警阈值 (°C)
    "high_wind": 10,      # 大风预警阈值 (m/s)
    "heavy_rain": 50,     # 暴雨预警阈值 (mm/3h)
    "heavy_snow": 10,     # 大雪预警阈值 (mm/3h)
}

# 监控间隔（秒）
CHECK_INTERVAL = 3600  # 每小时检查一次
```

## 注意事项

⚠️ **安全提醒**: `config.py` 包含敏感的 API 密钥，已添加到 `.gitignore`，请勿上传到代码仓库！

## 开源协议

MIT License

