import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CITIES = {
    "台北": (25.0330, 121.5654),
    "台中": (24.1477, 120.6736),
    "高雄": (22.6273, 120.3014),
}

WEATHER_CODE = {
    0: "晴朗", 1: "大致晴朗", 2: "局部多雲", 3: "陰天",
    45: "霧", 48: "霧凇",
    51: "毛毛雨", 53: "毛毛雨", 55: "毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    80: "陣雨", 81: "陣雨", 82: "強陣雨",
    95: "雷雨", 96: "雷雨冰雹", 99: "強雷雨冰雹"
}

def aqi_level(aqi):
    if aqi <= 50:
        return "良好"
    elif aqi <= 100:
        return "普通"
    elif aqi <= 150:
        return "對敏感族群不健康"
    elif aqi <= 200:
        return "不健康"
    elif aqi <= 300:
        return "非常不健康"
    else:
        return "危害"

def uv_level(uv):
    if uv < 3:
        return "低量級"
    elif uv < 6:
        return "中量級"
    elif uv < 8:
        return "高量級"
    elif uv < 11:
        return "過量級"
    else:
        return "危險級"

def get_weather(city, lat, lon):
    today = datetime.now().strftime("%Y-%m-%d")

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_probability_max,uv_index_max",
        "timezone": "Asia/Taipei",
        "start_date": today,
        "end_date": today
    }

    air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    air_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "us_aqi,pm10,pm2_5",
        "timezone": "Asia/Taipei"
    }

    w = requests.get(weather_url, params=weather_params, timeout=20)
    w.raise_for_status()
    weather = w.json()["daily"]

    a = requests.get(air_url, params=air_params, timeout=20)
    a.raise_for_status()
    air = a.json()["current"]

    code = weather["weather_code"][0]
    uv = weather["uv_index_max"][0]
    aqi = air["us_aqi"]

    return (
        f"📍 {city}\n"
        f"天氣：{WEATHER_CODE.get(code, '未知')}\n"
        f"氣溫：{weather['temperature_2m_min'][0]}°C ~ {weather['temperature_2m_max'][0]}°C\n"
        f"體感：{weather['apparent_temperature_min'][0]}°C ~ {weather['apparent_temperature_max'][0]}°C\n"
        f"降雨機率：{weather['precipitation_probability_max'][0]}%\n"
        f"紫外線：{uv}（{uv_level(uv)}）\n"
        f"空氣品質 AQI：{aqi}（{aqi_level(aqi)}）\n"
        f"PM2.5：{air['pm2_5']} μg/m³\n"
        f"PM10：{air['pm10']} μg/m³"
    )

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()

def main():
    today = datetime.now().strftime("%Y/%m/%d")
    message = [f"🌤 今日天氣預報\n📅 {today}\n⏰ 每天早上 6:00 自動推送\n"]

    for city, (lat, lon) in CITIES.items():
        message.append(get_weather(city, lat, lon))

    send_telegram("\n\n".join(message))

if __name__ == "__main__":
    main()
