import pandas as pd
import traceback
import numpy as np
import math

from service.ai_service import send_to_ai_model
from util.geo_utils import haversine
from repository.feature_repository import filter_non_weather_features
from service.weather_service import get_weather_data
import asyncio
import os
from service.farsite_service import (
    calculate_farsite_probs,
    apply_directional_correction,
    load_correction_weights, prepare_ast_input
)

def sanitize_json(obj):
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    elif isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json(item) for item in obj]
    else:
        return obj

def load_grids_within_radius(user_lat, user_lon, radius_km=15):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
    csv_path = os.path.join(DATA_DIR, 'korea_grids_0.01deg.csv')

    df = pd.read_csv(csv_path)
    # df = df.head(5)  # 🔥 메모리 초과 방지용 테스트 제한 → # TODO: 배포 시 제거
    filtered = []

    for _, row in df.iterrows():
        grid_lat = row['center_lat']
        grid_lon = row['center_lon']
        distance = haversine(user_lat, user_lon, grid_lat, grid_lon)

        if distance <= radius_km:
            filtered.append(row)

    return pd.DataFrame(filtered)


async def fetch_weather(lat, lon):
    await asyncio.sleep(0.2)  # Render 또는 API 과부하 방지용 짧은 지연
    return await get_weather_data(lat, lon)

async def append_weather_to_grids_async(grids_df: pd.DataFrame):
    # 각 격자에 대해 fetch_weather 호출 준비
    tasks = [
        fetch_weather(row["center_lat"], row["center_lon"])
        for _, row in grids_df.iterrows()
    ]

    # 병렬로 실행
    weather_data = await asyncio.gather(*tasks)

    # 결과 합치기
    weather_df = pd.DataFrame(weather_data)
    return pd.concat([grids_df.reset_index(drop=True), weather_df], axis=1)



async def process_prediction(lat: float, lon: float):
    print(f"🔥 process_prediction 시작: 위도={lat}, 경도={lon}")

    try:
        # 1️⃣ 반경 15km 이내 격자 추출
        print("📍 [STEP 1] 반경 15km 격자 추출 시도")
        grids_df = load_grids_within_radius(lat, lon)
        print(f"✅ 격자 수: {len(grids_df)}")

        if grids_df.empty:
            print("⚠️ 격자 없음, 종료")
            return {"message": "반경 15km 이내에 격자가 없습니다."}

        # 2️⃣ 지표 필터링
        print("📍 [STEP 2] 지표 필터링 시작")
        grid_ids = grids_df['grid_id'].tolist()
        features_df = filter_non_weather_features(grid_ids)
        print("✅ 지표 필터링 완료")

        # 3️⃣ 날씨 붙이기
        print("📍 [STEP 3] 날씨 붙이기 시작")
        features_with_weather = await append_weather_to_grids_async(features_df)
        print("✅ 날씨 추가 완료")

        # 4️⃣ 확산 확률 계산
        print("📍 [STEP 4] 확산 확률 계산 시작")
        df_probs = calculate_farsite_probs(features_with_weather)
        weights = load_correction_weights()
        df_corrected = apply_directional_correction(df_probs, weights)
        print("✅ 확산 확률 계산 완료")

        # 5️⃣ AI 예측 전송
        print("📍 [STEP 5] AI 예측 JSON 구성 시작")
        # ✅ NaN, inf, np.nan → 모두 None 처리
        final_json = prepare_ast_input(df_corrected)
        final_json = sanitize_json(final_json)
        print("📦 전송 JSON 일부:", list(final_json[:1]))  # ✅ 전송 데이터 미리보기

        # ✅ NaN → None 처리 및 numpy 타입 변환 (항상)
        sample_data = prepare_ast_input(df_corrected[:2])

        try:
            print("📡 AI 전송 시도 중...")
            response_code = await send_to_ai_model(final_json)
            print(f"✅ 예측 응답 코드: {response_code}")
        except Exception as send_err:
            print(f"❌ AI 전송 중 예외 발생: {send_err}")

        # 🟢 정상/예외 상관없이 결과 반환
        return {
            "입력 위도": lat,
            "입력 경도": lon,
            "격자 수": len(df_corrected),
            "지표 + 날씨 샘플": sample_data
        }


    except Exception as e:
        print(f"❗ 전체 흐름 중 예외 발생: {e}")
        traceback.print_exc()
        return {"error": str(e)}





