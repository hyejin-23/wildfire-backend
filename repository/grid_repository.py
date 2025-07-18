import pandas as pd
from util.geo_utils import haversine

def load_grids_within_radius(lat, lon, radius_km=50):
    df = pd.read_csv("D:/py/korea_grids_0.01deg.csv") # 경로는 프로젝트에 맞게
    filtered = []

    for _, row in df.iterrows():
        dist = haversine(lat, lon, row['center_lat'], row['center_lon'])
        if dist <= radius_km:
            filtered.append(row)

    return pd.DataFrame(filtered)
