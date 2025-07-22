import pandas as pd
import os
from util.geo_utils import haversine

def load_grids_within_radius(lat, lon, radius_km=15):
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
        file_path = os.path.join(DATA_DIR, 'korea_grids_0.01deg.csv')

        print(f"📂 격자 CSV 경로: {file_path}")  # 디버깅용

        df = pd.read_csv(file_path)
        # df = df.head(5)  # ✅ 테스트 중 Render 메모리 초과 방지용
        print(f"✅ 격자 수 5개: {len(df)}")

        filtered = []
        for _, row in df.iterrows():
            dist = haversine(lat, lon, row['center_lat'], row['center_lon'])
            if dist <= radius_km:
                filtered.append(row)

        result_df = pd.DataFrame(filtered)
        print(f"📍 반경 {radius_km}km 내 격자 수: {len(result_df)}")

        if result_df.empty:
            print("⚠️ 필터링 결과가 비어 있음 (빈 격자 DataFrame 반환됨)")

        return result_df

    except FileNotFoundError as fe:
        print(f"❌ CSV 파일을 찾을 수 없습니다: {fe}")
        raise

    except Exception as e:
        print(f"❌ 격자 로딩 중 오류 발생: {e}")
        raise



