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
import pandas as pd  # 혹시 없으면 추가


def prepare_ast_input(df):
    """
    FARSITE 확산 모델의 평균 확률 컬럼을 계산하여 JSON 리스트 생성
    """
    direction_cols = ["P_NW", "P_N", "P_NE", "P_W", "P_E", "P_SW", "P_S", "P_SE"]
    df = df.copy()

    # 🔹 1. farsite_prob 평균 계산
    df["farsite_prob"] = df[direction_cols].mean(axis=1)

    # 🔹 2. 확산 확률 8방향 컬럼 제거
    final = df.drop(columns=direction_cols)

    # 🔹 3. numpy → Python 기본 타입으로 변환 + NaN, 이상치 처리
    final = final.applymap(lambda x:
                           None if pd.isna(x) or x in [-9999, -9999.0]  # ✅ NaN 또는 이상치 처리
                           else int(x) if isinstance(x, (np.integer, int))
                           else float(x) if isinstance(x, (np.floating, float))
                           else x
                           )

    # 🔹 4. 혹시 남아있는 np.nan을 None으로
    final = final.replace({np.nan: None})

    return final.to_dict(orient="records")

