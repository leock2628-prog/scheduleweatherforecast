import os
import requests
from datetime import datetime

# ===== 從環境變數讀取（GitHub Secrets）=====
# 本機測試時可直接填入，部署後改用 Secrets
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN" )
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID" )
# ==========================================

CITIES = {
    "台北": {"lat": 25.0330, "lon": 121.5654},
    "台中": {"lat": 24.1477, "lon": 120.6736},
    "高雄": {"lat": 22.6273, "lon": 120.3014},
}

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,apparent_temperature_max,precipitation_probability_max",
        "timezone": "Asia/Taipei",
        "forecast_days": 1,
    }
    res = requests.get(url, params=params, timeout=10)
    res.raise_for_status()
    data = res.json()["daily"]
    return {
        "temp_max": data["temperature_2m_max"][0],
        "temp_min": data["temperature_2m_min"][0],
        "feels_like": data["apparent_temperature_max"][0],
        "rain_prob": data["precipitation_probability_max"][0],
    }

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    res = requests.post(url, json=payload, timeout=10)
    res.raise_for_status()

def main():
    today = datetime.now().strftime("%Y/%m/%d")
    lines = [f"🌤 <b>每日天氣預報 {today}</b>\n"]

    for city, coords in CITIES.items():
        w = get_weather(coords["lat"], coords["lon"])
        rain_emoji = "🌧" if w["rain_prob"] >= 50 else "☀️"
        lines.append(
            f"📍 <b>{city}</b>\n"
            f"  🌡 氣溫：{w['temp_min']}°C ~ {w['temp_max']}°C\n"
            f"  🤔 體感：{w['feels_like']}°C\n"
            f"  {rain_emoji} 降雨機率：{w['rain_prob']}%\n"
        )

    send_telegram("\n".join(lines))
    print("✅ 天氣預報已發送")

if __name__ == "__main__":
    main()
