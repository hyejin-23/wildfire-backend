import pandas as pd
import os
from util.geo_utils import haversine

def load_grids_within_radius(lat, lon, radius_km=15):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
    file_path = os.path.join(DATA_DIR, 'korea_grids_0.01deg.csv')

    df = pd.read_csv(file_path)
    filtered = []

    for _, row in df.iterrows():
        dist = haversine(lat, lon, row['center_lat'], row['center_lon'])
        if dist <= radius_km:
            filtered.append(row)

    return pd.DataFrame(filtered)


