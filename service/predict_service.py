import pandas as pd
from util.geo_utils import haversine
from repository.feature_repository import filter_non_weather_features
from service.weather_service import get_weather_data
from service.prepare_input import prepare_ast_input
from service.ai_service import send_to_ai_model
import asyncio  #  추가

def load_grids_within_radius(user_lat, user_lon, radius_km=15):
    csv_path = "D:/py/korea_grids_0.01deg.csv"
    df = pd.read_csv(csv_path)

    filtered = []

    for _, row in df.iterrows():
        grid_lat = row['center_lat']
        grid_lon = row['center_lon']
        distance = haversine(user_lat, user_lon, grid_lat, grid_lon)

        if distance <= radius_km:
            filtered.append(row)

    return pd.DataFrame(filtered)

# ✅ 비동기 날씨 붙이기
async def append_weather_to_grids_async(grids_df):
    tasks = [
        get_weather_data(row["center_lat"], row["center_lon"])
        for _, row in grids_df.iterrows()
    ]
    weather_data = await asyncio.gather(*tasks)

    weather_df = pd.DataFrame(weather_data)
    return pd.concat([grids_df.reset_index(drop=True), weather_df], axis=1)

# ✅ 최종 예측 처리 함수도 async로!
async def process_prediction(lat: float, lon: float):
    print(f"사용자 입력 위치 → 위도: {lat}, 경도: {lon}")

    try:
        grids_df = load_grids_within_radius(lat, lon)

        if grids_df.empty:
            return {"message": "반경 15km 이내에 격자가 없습니다."}

        grid_ids = grids_df['grid_id'].tolist()
        features_df = filter_non_weather_features(grid_ids)

        # ✅ 비동기 날씨 붙이기
        features_with_weather = await append_weather_to_grids_async(features_df)

        # ✅ 컬럼 순서 정리
        desired_columns = [
            "grid_id", "lat_min", "lat_max", "lon_min", "lon_max",
            "center_lat", "center_lon",
            "avg_fuelload_pertree_kg", "FFMC", "DMC", "DC", "NDVI", "smap_20250630_filled",
            "temp_C", "humidity", "wind_speed", "wind_deg", "precip_mm",
            "mean_slope", "spei_recent_avg"
        ]
        features_with_weather = features_with_weather[desired_columns]

        # ✅ JSON 생성 및 AI 예측 모델로 전송
        final_json = prepare_ast_input(features_with_weather)
        response_code = send_to_ai_model(final_json)

        if response_code == 200:
            print("AI 예측 서버 전송 완료!")
        else:
            print("전송 실패")

        # ✅ 사용자에게는 샘플만 반환
        return {
            "입력 위도": lat,
            "입력 경도": lon,
            "격자 수": len(features_with_weather),
            "지표 + 날씨 샘플": features_with_weather.head(2).to_dict(orient="records")
        }

    except Exception as e:
        return {"error": str(e)}



