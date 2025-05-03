import pandas as pd
import folium
import streamlit as st
import requests
import googlemaps
import streamlit.components.v1 as components
from math import radians, sin, cos, sqrt, atan2

# Page setup
st.set_page_config(page_title="ぶっけんさくさん　", page_icon="🏘", layout="wide")
st.title("ぶっけんさくさん🏘")

# Google Maps APIキーを取得
google_maps_api_key = st.secrets["google_maps"]["api_key"]
gmaps = googlemaps.Client(key=google_maps_api_key)

# Haversineの公式を使用して、2点間の距離を計算
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  # 距離を計算 (km)

# バス停と駅のサンプルデータ
stations = {
    "渋谷駅": {"lat": 35.658034, "lon": 139.701636},
    "新宿駅": {"lat": 35.6895, "lon": 139.6917},
    "池袋駅": {"lat": 35.7333, "lon": 139.7113},
    "東京駅": {"lat": 35.681236, "lon": 139.767125},
}

bus_stops = {
    "渋谷バス停": {"lat": 35.658500, "lon": 139.701800},
    "新宿バス停": {"lat": 35.6898, "lon": 139.6921},
    "池袋バス停": {"lat": 35.7335, "lon": 139.7118},
}

# データ読み込み関数
@st.cache_data
def load_data():
    sheet_id = "1bVzMw7TcnzGnqZWS6bjt1K5uopZWXjYWcHeFV3AgehQ"
    sheet_name = "bukken"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(sheet_url)
    df.rename(columns=lambda x: x.strip(), inplace=True)
    return df

# 駅とバス停の選択
st.sidebar.title("物件検索")
selected_station = st.sidebar.selectbox("駅を選んでください", list(stations.keys()))
selected_bus_stop = st.sidebar.selectbox("バス停を選んでください", list(bus_stops.keys()))

# 家賃スライダー
min_rent, max_rent = st.sidebar.slider(
    "家賃を選んでください",
    min_value=0,
    max_value=500000,
    value=(0, 300000),
    step=5000,
)

# 選択された駅とバス停の緯度経度
station_lat, station_lon = stations[selected_station]["lat"], stations[selected_station]["lon"]
bus_lat, bus_lon = bus_stops[selected_bus_stop]["lat"], bus_stops[selected_bus_stop]["lon"]

# バス停から駅までのルートをGoogle Maps Directions APIで取得
def get_bus_route(start_lat, start_lon, end_lat, end_lon):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_lat},{start_lon}&destination={end_lat},{end_lon}&mode=transit&transit_mode=bus&key={google_maps_api_key}"
    response = requests.get(url)
    directions = response.json()
    
    if directions['status'] == 'OK' and 'routes' in directions:
        route = directions['routes'][0]
        polyline_points = route['overview_polyline']['points']
        return polyline_points
    else:
        st.error("バスルートの取得に失敗しました。")
        return None

# バスルートを取得
route_polyline = get_bus_route(bus_lat, bus_lon, station_lat, station_lon)

# データの読み込みとフィルタリング
property_data = load_data()
filtered_data = property_data[(property_data['家賃'] >= min_rent) & (property_data['家賃'] <= max_rent)]

# 駅との距離を計算して並べ替え
filtered_data['駅からの距離'] = filtered_data.apply(
    lambda row: calculate_distance(station_lat, station_lon, row['緯度'], row['経度']),
    axis=1
)

# 地図に物件、駅、バス停を表示
m = folium.Map(location=[station_lat, station_lon], zoom_start=14)

# 駅とバス停のマーカーを追加
folium.Marker([station_lat, station_lon], popup=f"{selected_station} (駅)", icon=folium.Icon(color="red", icon="cloud")).add_to(m)
folium.Marker([bus_lat, bus_lon], popup=f"{selected_bus_stop} (バス停)", icon=folium.Icon(color="green", icon="cloud")).add_to(m)

# バスルートを地図に追加
if route_polyline:
    folium.PolyLine(
        locations=folium.util.decode_polyline(route_polyline),
        color="blue",
        weight=5,
        opacity=0.7,
    ).add_to(m)

# 物件のマーカーを追加
for _, row in filtered_data.iterrows():
    folium.Marker(
        location=(row["緯度"], row["経度"]),
        popup=f"{row['物件名']} - ¥{row['家賃']:,}<br>駅からの距離: {row['駅からの距離']:.2f} km",
        icon=folium.Icon(color="blue", icon="home"),
    ).add_to(m)

# 地図を表示
st.write("物件の地図（駅とバス停から近い順）")
map_html = m._repr_html_()
components.html(map_html, height=600)

st.write(f"APIレスポンス: {directions}")
