import numpy as np
import pandas as pd

def calculate_farsite_probs(df: pd.DataFrame) -> pd.DataFrame:
    """
    격자별로 8방향(NW~SE)에 대한 확산 확률(P_dir)을 계산하여 DataFrame에 추가.
    """
    # 8방향 설정
    directions = [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)]
    dir_labels = ['P_NW', 'P_N', 'P_NE', 'P_W', 'P_E', 'P_SW', 'P_S', 'P_SE']

    # 고정 파라미터
    sigma = 1.0
    alpha = 0.5
    beta = 0.5
    slope_dir = 135  # 경사 방향 (예시값)

    result_rows = []

    for _, row in df.iterrows():
        wind_dir = row["wind_deg"]
        ros = 0.001 * row["avg_fuelload_pertree_kg"]

        P = []

        for dx, dy in directions:
            d_ij = np.sqrt(dx**2 + dy**2)
            theta_ij = np.degrees(np.arctan2(dy, dx))
            if theta_ij < 0:
                theta_ij += 360

            G = alpha * np.cos(np.radians(theta_ij - wind_dir)) + beta * np.cos(np.radians(theta_ij - slope_dir))
            prob = np.exp(-(d_ij**2) / (sigma**2)) * (1 + G) * ros
            P.append(prob)

        # 정규화
        P = np.array(P)
        P = P / P.sum()

        # 결과 행 구성
        new_row = row.copy()
        for label, p in zip(dir_labels, P):
            new_row[label] = p
        result_rows.append(new_row)

    return pd.DataFrame(result_rows)

def load_correction_weights(csv_path: str) -> dict:
    """
    input_data_farsite_Nan.csv에서 방향별 확산 확률 평균을 기반으로 역가중치 계산
    → 각 방향에 대한 정규화된 보정 가중치를 반환
    """
    df = pd.read_csv(csv_path)

    dir_cols = ['P_NW', 'P_N', 'P_NE', 'P_W', 'P_E', 'P_SW', 'P_S', 'P_SE']
    mean_probs = []

    for col in dir_cols:
        mean_val = df[col].mean(skipna=True)
        mean_probs.append(mean_val)

    # 역비율 계산
    inv_weights = [1 / p if p != 0 else 0 for p in mean_probs]

    # 정규화 (최댓값 기준)
    max_weight = max(inv_weights)
    norm_weights = [w / max_weight for w in inv_weights]

    # 결과를 딕셔너리로 반환
    return {dir_cols[i]: norm_weights[i] for i in range(8)}

def apply_directional_correction(df_probs: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """
    보정 가중치를 적용하여 P_dir 열들을 정규화된 확률로 다시 계산
    """
    dir_cols = ['P_NW', 'P_N', 'P_NE', 'P_W', 'P_E', 'P_SW', 'P_S', 'P_SE']
    df_corrected = df_probs.copy()

    for idx, row in df_corrected.iterrows():
        probs = []
        for col in dir_cols:
            val = row[col]
            weight = weights[col]
            probs.append(val * weight if pd.notna(val) else np.nan)

        # 정규화
        total = np.nansum(probs)
        normalized = [p / total if pd.notna(p) else np.nan for p in probs]

        # 다시 저장
        for i, col in enumerate(dir_cols):
            df_corrected.at[idx, col] = normalized[i]

    return df_corrected

def prepare_ast_input(df: pd.DataFrame) -> list[dict]:
    """
    보정된 확산 확률 DataFrame에서 필요한 21개 항목만 뽑아 JSON 리스트로 구성
    → farsite_prob은 8방향 확산 확률의 평균값
    """
    dir_cols = ['P_NW', 'P_N', 'P_NE', 'P_W', 'P_E', 'P_SW', 'P_S', 'P_SE']

    json_list = []

    for _, row in df.iterrows():
        farsite_prob = np.nanmean([row[dir] for dir in dir_cols])

        grid_data = {
            "grid_id": row["grid_id"],
            "lat_min": row["lat_min"],
            "lat_max": row["lat_max"],
            "lon_min": row["lon_min"],
            "lon_max": row["lon_max"],
            "center_lat": row["center_lat"],
            "center_lon": row["center_lon"],
            "avg_fuelload_pertree_kg": row["avg_fuelload_pertree_kg"],
            "FFMC": row["FFMC"],
            "DMC": row["DMC"],
            "DC": row["DC"],
            "NDVI": row["NDVI"],
            "smap_20250630_filled": row["smap_20250630_filled"],
            "temp_C": row["temp_C"],
            "humidity": row["humidity"],
            "wind_speed": row["wind_speed"],
            "wind_deg": row["wind_deg"],
            "precip_mm": row["precip_mm"],
            "mean_slope": row["mean_slope"],
            "spei_recent_avg": row["spei_recent_avg"],
            "farsite_prob": farsite_prob
        }

        json_list.append(grid_data)

    return json_list

