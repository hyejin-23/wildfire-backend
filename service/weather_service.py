import httpx
from datetime import datetime

async def get_weather_data(lat: float, lon: float):
    """
    위도, 경도를 받아 Open-Meteo API에서 실시간 날씨 5종 데이터 가져오기 (비동기 버전)
    반환: 딕셔너리(temp_C, wind_speed, wind_deg, humidity, precip_mm)
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true"
        "&hourly=relative_humidity_2m,precipitation"
        "&timezone=Asia/Seoul"
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        # 현재 날씨 데이터
        current = data.get("current_weather", {})
        temp_C = current.get("temperature")
        wind_speed = current.get("windspeed")
        wind_deg = current.get("winddirection")

        # 현재 시간 기준으로 가장 가까운 시간의 시간별 데이터
        humidity = None
        precip_mm = None
        now = datetime.now().strftime("%Y-%m-%dT%H:00")

        if "hourly" in data:
            times = data["hourly"]["time"]
            if now in times:
                idx = times.index(now)
                humidity = data["hourly"]["relative_humidity_2m"][idx]
                precip_mm = data["hourly"]["precipitation"][idx]

        return {
            "temp_C": temp_C,
            "wind_speed": wind_speed,
            "wind_deg": wind_deg,
            "humidity": humidity,
            "precip_mm": precip_mm
        }

    except Exception as e:
        print(f"날씨 API 오류: {e}")
        return {
            "temp_C": None,
            "wind_speed": None,
            "wind_deg": None,
            "humidity": None,
            "precip_mm": None
        }


