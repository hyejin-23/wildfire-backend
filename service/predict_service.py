import pandas as pd
from util.geo_utils import haversine
from repository.feature_repository import filter_non_weather_features
from service.weather_service import get_weather_data
from service.prepare_input import prepare_ast_input
from service.ai_service import send_to_ai_model
import asyncio  #  추가
import os  # 추가
from service.farsite_service import (
    calculate_farsite_probs,
    apply_directional_correction,
    prepare_ast_input,
    load_correction_weights
)
from service.ai_service import send_to_ai_model
import traceback

def load_grids_within_radius(user_lat, user_lon, radius_km=15):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
    csv_path = os.path.join(DATA_DIR, 'korea_grids_0.01deg.csv')

    df = pd.read_csv(csv_path)
    filtered = []

    for _, row in df.iterrows():
        grid_lat = row['center_lat']
        grid_lon = row['center_lon']
        distance = haversine(user_lat, user_lon, grid_lat, grid_lon)

        if distance <= radius_km:
            filtered.append(row)

    return pd.DataFrame(filtered)


# ✅ 날씨 비동기 처리 함수
async def append_weather_to_grids_async(grids_df: pd.DataFrame):
    tasks = [
        get_weather_data(row["center_lat"], row["center_lon"])
        for _, row in grids_df.iterrows()
    ]
    weather_data = await asyncio.gather(*tasks)
    weather_df = pd.DataFrame(weather_data)
    return pd.concat([grids_df.reset_index(drop=True), weather_df], axis=1)


async def process_prediction(lat: float, lon: float):
    print(f"용자 입력 → 위도: {lat}, 경도: {lon}")

    try:
        # 1️⃣ 반경 15km 이내 격자 추출
        grids_df = load_grids_within_radius(lat, lon)
        print(f"추출된 격자 수: {len(grids_df)}")
        if grids_df.empty:
            return {"message": "반경 15km 이내에 격자가 없습니다."}

        # 2️⃣ 지표 데이터 필터링
        grid_ids = grids_df['grid_id'].tolist()
        features_df = filter_non_weather_features(grid_ids)
        print("지표 필터링 완료")

        # 3️⃣ 날씨 데이터 비동기 붙이기
        features_with_weather = await append_weather_to_grids_async(features_df)
        print("날씨 정보 추가 완료")

        # 4️⃣ 확산 확률 계산 → 보정
        df_probs = calculate_farsite_probs(features_with_weather)
        weights = load_correction_weights()
        df_corrected = apply_directional_correction(df_probs, weights)
        print("확산 확률 계산 및 보정 완료")

        # 5️⃣ AI 모델 전송용 JSON 구성 및 전송
        final_json = prepare_ast_input(df_corrected)
        print("AI 예측 요청 JSON 구성 완료")

        try:
            response_code = send_to_ai_model(final_json)
            print(f"예측 서버 응답 코드: {response_code}")
        except Exception as send_err:
            print(f"AI 전송 중 예외 발생: {send_err}")
            response_code = None

        if response_code == 200:
            print("AI 예측 서버 전송 완료")
        else:
            print("예측 전송 실패 또는 응답 없음")

        # 6️⃣ 사용자에게는 일부만 반환
        return {
            "입력 위도": lat,
            "입력 경도": lon,
            "격자 수": len(df_corrected),
            "지표 + 날씨 샘플": df_corrected.head(2).to_dict(orient="records")
        }

    except Exception as e:
        print(f"전체 흐름 중 예외 발생: {e}")
        traceback.print_exc()  # ← 이거 추가!
        return {"error": str(e)}




