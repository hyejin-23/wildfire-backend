import pandas as pd
import os

def filter_non_weather_features(grid_ids: list[int]) -> pd.DataFrame:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
    file_path = os.path.join(DATA_DIR, 'input_data_set_no_weather.csv')

    df = pd.read_csv(file_path)
    return df[df['grid_id'].isin(grid_ids)]


