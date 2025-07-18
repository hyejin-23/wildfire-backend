def prepare_ast_input(df):
    """
    FARSITE 확산 모델의 평균 확률 컬럼을 계산하여 JSON 리스트 생성
    """
    direction_cols = ["P_NW", "P_N", "P_NE", "P_W", "P_E", "P_SW", "P_S", "P_SE"]
    df = df.copy()
    df["farsite_prob"] = df[direction_cols].mean(axis=1)

    final = df.drop(columns=direction_cols)
    return final.to_dict(orient="records")
