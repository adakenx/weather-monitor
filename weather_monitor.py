#!/usr/bin/env python3
"""
北京天气监控系统
监控未来2天内不适合老人出门的天气，通过Telegram推送通知

监控条件：
1. 温度 > 35°C 或 < -10°C
2. 风力 > 10m/s
3. 中雨及以上
4. 任何降雪
5. 雾霾（AQI > 150）
"""

import requests
from datetime import datetime
from config import (
    OPENWEATHER_API_KEY,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    CITY_ID,
    EXTREME_WEATHER_THRESHOLDS,
)

# 北京坐标（用于空气质量API）
BEIJING_LAT = 39.9042
BEIJING_LON = 116.4074


class WeatherMonitor:
    """天气监控类"""
    
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.thresholds = EXTREME_WEATHER_THRESHOLDS
    
    def get_weather_data(self):
        """获取当前天气数据"""
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "id": CITY_ID,
            "appid": self.api_key,
            "units": "metric",
            "lang": "zh_cn"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[错误] 获取天气数据失败: {e}")
            return None
    
    def get_forecast_data(self):
        """获取天气预报数据（未来5天，每3小时）"""
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "id": CITY_ID,
            "appid": self.api_key,
            "units": "metric",
            "lang": "zh_cn"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[错误] 获取预报数据失败: {e}")
            return None
    
    def get_air_quality(self):
        """获取空气质量数据"""
        url = "https://api.openweathermap.org/data/2.5/air_pollution"
        params = {
            "lat": BEIJING_LAT,
            "lon": BEIJING_LON,
            "appid": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[错误] 获取空气质量数据失败: {e}")
            return None
    
    def calculate_aqi_from_pm25(self, pm25):
        """根据PM2.5计算中国AQI"""
        breakpoints = [
            (0, 35, 0, 50),
            (35, 75, 50, 100),
            (75, 115, 100, 150),
            (115, 150, 150, 200),
            (150, 250, 200, 300),
            (250, 350, 300, 400),
            (350, 500, 400, 500),
        ]
        
        for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
            if bp_lo <= pm25 <= bp_hi:
                aqi = (aqi_hi - aqi_lo) / (bp_hi - bp_lo) * (pm25 - bp_lo) + aqi_lo
                return round(aqi)
        
        if pm25 > 500:
            return 500
        return 0
    
    def format_time_cn(self, dt_txt):
        """将时间格式化为简洁的中文格式"""
        try:
            dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
            hour = dt.hour
            
            if 5 <= hour < 12:
                period = "上午"
            elif 12 <= hour < 18:
                period = "下午"
            else:
                period = "晚间"
            
            return f"{dt.month}/{dt.day} {period}"
        except:
            return dt_txt
    
    def check_weather_alerts(self, weather_data, time_str="当前"):
        """检查单个时间点的天气"""
        alerts = []
        
        if not weather_data:
            return alerts
        
        main = weather_data.get("main", {})
        wind = weather_data.get("wind", {})
        weather = weather_data.get("weather", [{}])[0]
        
        temp = main.get("temp", 0)
        wind_speed = wind.get("speed", 0)
        weather_id = weather.get("id", 0)
        weather_desc = weather.get("description", "")
        
        # 高温
        if temp >= self.thresholds["high_temp"]:
            alerts.append(f"{time_str} 🔥 高温 {temp:.0f}°C")
        
        # 低温
        if temp <= self.thresholds["low_temp"]:
            alerts.append(f"{time_str} ❄️ 低温 {temp:.0f}°C")
        
        # 大风
        if wind_speed >= self.thresholds["high_wind"]:
            alerts.append(f"{time_str} 💨 大风 {wind_speed:.0f}m/s")
        
        # 中雨及以上 (501=中雨, 502+=大雨)
        if self.thresholds.get("moderate_rain") and 501 <= weather_id <= 531:
            alerts.append(f"{time_str} 🌧️ {weather_desc}")
        
        # 任何降雪 (600-622)
        if self.thresholds.get("any_snow") and 600 <= weather_id <= 622:
            alerts.append(f"{time_str} 🌨️ {weather_desc}")
        
        # 雷暴
        if 200 <= weather_id < 300:
            alerts.append(f"{time_str} ⛈️ {weather_desc}")
        
        return alerts
    
    def check_air_quality_alert(self):
        """检查空气质量"""
        air_data = self.get_air_quality()
        if not air_data or "list" not in air_data:
            return None, None
        
        components = air_data["list"][0].get("components", {})
        pm25 = components.get("pm2_5", 0)
        aqi = self.calculate_aqi_from_pm25(pm25)
        
        aqi_limit = self.thresholds.get("aqi_limit", 150)
        if aqi > aqi_limit:
            return f"当前 😷 雾霾 AQI {aqi}", aqi
        
        return None, aqi
    
    def send_telegram_message(self, message):
        """发送Telegram消息"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            print(f"[成功] Telegram消息已发送")
            return True
        except requests.RequestException as e:
            print(f"[错误] Telegram消息发送失败: {e}")
            return False
    
    def format_alert_message(self, alerts):
        """格式化简洁的告警消息"""
        if not alerts:
            return None
        
        # 去重
        unique_alerts = list(dict.fromkeys(alerts))
        
        message = "🚨 <b>北京天气预警</b>\n\n"
        message += "📅 未来2天内不宜外出：\n\n"
        
        for alert in unique_alerts:
            message += f"• {alert}\n"
        
        message += "\n💡 建议今天网上订菜"
        
        return message
    
    def run_once(self):
        """执行一次检查并推送（如有预警）"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检查北京未来2天天气...")
        
        all_alerts = []
        
        # 检查当前天气
        current_weather = self.get_weather_data()
        if current_weather:
            alerts = self.check_weather_alerts(current_weather, "当前")
            all_alerts.extend(alerts)
            
            main = current_weather.get("main", {})
            weather_desc = current_weather.get("weather", [{}])[0].get("description", "")
            print(f"  当前: {weather_desc}, {main.get('temp', 'N/A'):.0f}°C")
        
        # 检查空气质量
        air_alert, aqi = self.check_air_quality_alert()
        if air_alert:
            all_alerts.append(air_alert)
        if aqi:
            print(f"  空气质量: AQI {aqi}")
        
        # 检查未来2天预报（16个时间点，每3小时）
        forecast = self.get_forecast_data()
        if forecast and "list" in forecast:
            for item in forecast["list"][:16]:
                dt_txt = item.get("dt_txt", "")
                time_str = self.format_time_cn(dt_txt)
                alerts = self.check_weather_alerts(item, time_str)
                all_alerts.extend(alerts)
        
        # 发送告警
        if all_alerts:
            message = self.format_alert_message(all_alerts)
            if message:
                print(f"\n⚠️ 发现 {len(set(all_alerts))} 个预警，发送通知...")
                self.send_telegram_message(message)
        else:
            print("\n✅ 未来2天天气良好，无需推送")
        
        return all_alerts


def test_connection():
    """测试API连接"""
    print("=" * 50)
    print("北京天气监控系统 - 连接测试")
    print("=" * 50)
    
    monitor = WeatherMonitor()
    
    # 测试天气API
    print("\n1. 测试天气API...")
    weather = monitor.get_weather_data()
    if weather:
        print("   ✅ 天气API连接成功")
        main = weather.get("main", {})
        wind = weather.get("wind", {})
        weather_desc = weather.get("weather", [{}])[0].get("description", "未知")
        print(f"   当前北京: {weather_desc}, {main.get('temp', 'N/A'):.0f}°C, 风速 {wind.get('speed', 'N/A')} m/s")
    else:
        print("   ❌ 天气API连接失败，请检查API Key")
        return
    
    # 测试空气质量API
    print("\n2. 测试空气质量API...")
    air_alert, aqi = monitor.check_air_quality_alert()
    if aqi is not None:
        print("   ✅ 空气质量API连接成功")
        print(f"   当前AQI: {aqi}")
    else:
        print("   ❌ 空气质量API连接失败")
    
    # 测试Telegram
    print("\n3. 测试Telegram...")
    test_msg = "🔔 北京天气监控测试\n\n连接成功！"
    if monitor.send_telegram_message(test_msg):
        print("   ✅ Telegram连接成功")
    else:
        print("   ❌ Telegram连接失败")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_connection()
        elif sys.argv[1] == "once":
            monitor = WeatherMonitor()
            monitor.run_once()
        else:
            print("用法:")
            print("  python weather_monitor.py test   # 测试API连接")
            print("  python weather_monitor.py once   # 检查天气并推送")
    else:
        # 默认执行一次检查
        monitor = WeatherMonitor()
        monitor.run_once()
