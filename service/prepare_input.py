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
from util.json_utils import sanitize_json

def prepare_ast_input(df):
    """
    FARSITE 확산 모델의 평균 확산 확률을 계산하고, AI 예측에 적합한 JSON 리스트로 변환합니다.
    1. 8방향 확산 확률의 평균값(farsite_prob) 계산
    2. 이상치 및 NaN 제거
    3. numpy 타입 → 기본 파이썬 타입 변환
    4. JSON 직렬화 가능한 안전한 딕셔너리 리스트 반환
    """
    direction_cols = ["P_NW", "P_N", "P_NE", "P_W", "P_E", "P_SW", "P_S", "P_SE"]
    df = df.copy()

    # ✅ 1. 8방향 확산 확률 평균 계산
    df["farsite_prob"] = df[direction_cols].mean(axis=1, skipna=True)

    # ✅ 2. 8방향 컬럼 제거 (AI 모델은 평균값만 받음)
    final = df.drop(columns=direction_cols)

    # ✅ 3. 타입 변환 + 이상치/NaN 처리
    final = final.applymap(lambda x:
        None if pd.isna(x) or x in [-9999, -9999.0]
        else int(x) if isinstance(x, (np.integer, int))
        else float(x) if isinstance(x, (np.floating, float))
        else x
    )

    # ✅ 4. JSON 직렬화 안전 처리
    return sanitize_json(final.to_dict(orient="records"))


