import httpx
from datetime import datetime
import asyncio  # 호출 간 시간 지연을 위해 필요

# 요청 캐시 저장 딕셔너리
weather_cache = {}

async def get_weather_data(lat: float, lon: float):
    """
    위도, 경도를 받아 Open-Meteo API에서 실시간 날씨 5종 데이터 가져오기 (비동기 버전)
    반환: 딕셔너리(temp_C, wind_speed, wind_deg, humidity, precip_mm)
    """
    # 캐시 키 생성 (소수점 2자리까지 반올림 → 중복 방지)
    key = f"{round(lat, 2)}_{round(lon, 2)}"
    if key in weather_cache:
        return weather_cache[key]  # 캐시된 결과 반환

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
            await asyncio.sleep(2)  # 호출 간 2초 지연 → 429 방지
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
            # ✅ [여기] 시간 비교 전 로그 추가
            print("📆 hourly['time'][0] =", data["hourly"]["time"][0])
            print("🕒 현재 한국시간 =", datetime.now().strftime("%Y-%m-%dT%H:00"))

            times = data["hourly"]["time"]
            if now in times:
                idx = times.index(now)
                humidity = data["hourly"]["relative_humidity_2m"][idx]
                precip_mm = data["hourly"]["precipitation"][idx]

        result = {
            "temp_C": temp_C,
            "wind_speed": wind_speed,
            "wind_deg": wind_deg,
            "humidity": humidity,
            "precip_mm": precip_mm
        }

        weather_cache[key] = result  # 캐시에 저장
        return result

    except Exception as e:
        print(f"날씨 API 오류: {e}")
        return {
            "temp_C": None,
            "wind_speed": None,
            "wind_deg": None,
            "humidity": None,
            "precip_mm": None
        }



