# import numpy as np
#
# def prepare_ast_input(df):
#     """
#     FARSITE 확산 모델의 평균 확률 컬럼을 계산하여 JSON 리스트 생성
#     """
#     direction_cols = ["P_NW", "P_N", "P_NE", "P_W", "P_E", "P_SW", "P_S", "P_SE"]
#     df = df.copy()
#     df["farsite_prob"] = df[direction_cols].mean(axis=1)
#
#     final = df.drop(columns=direction_cols)
#
#     # 🔧 numpy 타입을 Python 기본 타입으로 변환
#     final = final.applymap(lambda x:
#                            int(x) if isinstance(x, (np.int64, np.int32))
#                            else float(x) if isinstance(x, (np.float64, np.float32))
#                            else x
#                            )
#
#     # ✅ NaN → None 으로 바꾸기 (JSON 직렬화 가능하도록)
#     final = final.replace({np.nan: None})
#
#     return final.to_dict(orient="records")

import numpy as np
import pandas as pd
import math

def sanitize_json(obj):
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    elif isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json(item) for item in obj]
    else:
        return obj

def prepare_ast_input(df):
    """
    FARSITE 확산 모델의 평균 확률 컬럼을 계산하여 JSON 리스트 생성
    """
    direction_cols = ["P_NW", "P_N", "P_NE", "P_W", "P_E", "P_SW", "P_S", "P_SE"]
    df = df.copy()

    # ✅ 1. 평균 계산 (skipna=True 추가)
    df["farsite_prob"] = df[direction_cols].mean(axis=1, skipna=True)

    # ✅ 2. 8방향 확률 제거
    final = df.drop(columns=direction_cols)

    # ✅ 3. 타입 변환 및 NaN, 이상치 처리
    final = final.applymap(lambda x:
        None if pd.isna(x) or x in [-9999, -9999.0]
        else int(x) if isinstance(x, (np.integer, int))
        else float(x) if isinstance(x, (np.floating, float))
        else x
    )

    # ✅ 4. dict 변환 후 JSON 직렬화 안전하게 sanitize
    return sanitize_json(final.to_dict(orient="records"))


