import pandas as pd

def filter_non_weather_features(grid_ids: list[int]) -> pd.DataFrame:
    df = pd.read_csv("D:/py/input_data_set_no_weather.csv")
    return df[df['grid_id'].isin(grid_ids)]
