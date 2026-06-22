# src/transform.py
import pandas as pd

def parse_wkt_point(coords_str):
    if isinstance(coords_str, str) and coords_str.startswith("Point("):
        try:
            lon_lat = coords_str.replace("Point(", "").replace(")", "").split(" ")
            return float(lon_lat[1]), float(lon_lat[0])
        except (ValueError, IndexError):
            pass
    return None, None

def transform_cities(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    
    df["population"] = pd.to_numeric(df["population"], errors='coerce')
    
    lats, lons = [], []
    for coords in df["coords"]:
        lat, lon = parse_wkt_point(coords)
        lats.append(lat)
        lons.append(lon)
        
    df["latitude"] = lats
    df["longitude"] = lons
    df["latitude"] = pd.to_numeric(df["latitude"], errors='coerce')
    df["longitude"] = pd.to_numeric(df["longitude"], errors='coerce')
    return df

def transform_roads(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df["length"] = pd.to_numeric(df["length"], errors='coerce')
    return df

def transform_evolution(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df["population"] = pd.to_numeric(df["population"], errors='coerce')
    df["year"] = pd.to_datetime(df["year"], errors='coerce').dt.year
    df = df.dropna(subset=["year", "population"])
    df["year"] = df["year"].astype(int)
    df = df.sort_values(by=["cityLabel", "year"])
    return df

def transform_airports(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df["elevation"] = pd.to_numeric(df["elevation"], errors='coerce')
    
    lats, lons = [], []
    for coords in df["coords"]:
        lat, lon = parse_wkt_point(coords)
        lats.append(lat)
        lons.append(lon)
        
    df["latitude"] = lats
    df["longitude"] = lons
    df["latitude"] = pd.to_numeric(df["latitude"], errors='coerce')
    df["longitude"] = pd.to_numeric(df["longitude"], errors='coerce')
    return df

def transform_ports(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
        
    lats, lons = [], []
    for coords in df["coords"]:
        lat, lon = parse_wkt_point(coords)
        lats.append(lat)
        lons.append(lon)
        
    df["latitude"] = lats
    df["longitude"] = lons
    df["latitude"] = pd.to_numeric(df["latitude"], errors='coerce')
    df["longitude"] = pd.to_numeric(df["longitude"], errors='coerce')
    return df

def transform_world_bank(raw_json: list) -> pd.DataFrame:
    if len(raw_json) > 1 and raw_json[1]:
        records = [
            {"year": int(item["date"]), "urban_rate": item["value"]} 
            for item in raw_json[1] 
            if item["value"] is not None
        ]
        return pd.DataFrame(records).sort_values("year")
    return pd.DataFrame()