import pandas as pd
import folium
import streamlit as st
from math import radians, sin, cos, sqrt, atan2
import requests
import streamlit.components.v1 as components
import googlemaps

# Google Maps APIキー（Secretsから取得）
google_maps_api_key = st.secrets["google_maps"]["api_key"]
gmaps = googlemaps.Client(key=google_maps_api_key)

# Haversine距離計算
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# 駅・バス停データ
stations = {
    "渋谷駅": {"lat": 35.658034, "lon": 139.701636},
    "新宿駅": {"lat": 35.6895, "lon": 139.6917},
    "池袋駅": {"lat": 35.7333, "lon": 139.7113},
    "東京駅": {"lat": 35.681236, "lon": 139.767125},
}

bus_stops = {
    "渋谷バス停": {"lat": 35.6585, "lon": 139.7018},
    "新宿バス停": {"lat": 35.6898, "lon": 139.6921},
    "池袋バス停": {"lat": 35.7335, "lon": 139.7118},
}

# Directions API で公共交通（全体）ルート取得
def get_transit_route(start_lat, start_lon, end_lat, end_lon):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_lat},{start_lon}&destination={end_lat},{end_lon}&mode=transit&key={google_maps_api_key}"
    response = requests.get(url)
    directions = response.json()
    if directions['status'] == 'OK':
        polyline = directions['routes'][0]['overview_polyline']['points']
        return folium.PolyLine(locations=folium.util.decode_polyline(polyline), color="blue", weight=5, opacity=0.7)
    else:
        return None

# データ読み込み
@st.cache_data
def load_data():
    sheet_id = "1bVzMw7TcnzGnqZWS6bjt1K5uopZWXjYWcHeFV3AgehQ"
    sheet_name = "bukken"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(sheet_url)
    df.rename(columns=lambda x: x.strip(), inplace=True)
    return df

# サイドバーUI
st.sidebar.title("物件検索 MaaS")
selected_station = st.sidebar.selectbox("駅を選択", list(stations.keys()))
station_lat = stations[selected_station]['lat']
station_lon = stations[selected_station]['lon']

selected_bus_stop = st.sidebar.selectbox("バス停を選択", list(bus_stops.keys()))
bus_lat = bus_stops[selected_bus_stop]['lat']
bus_lon = bus_stops[selected_bus_stop]['lon']

min_rent, max_rent = st.sidebar.slider("家賃の範囲", 0, 500000, (0, 300000), step=5000)

# 物件データ読み込み
property_data = load_data()

# 家賃で絞り込み
filtered_data = property_data[(property_data['家賃'] >= min_rent) & (property_data['家賃'] <= max_rent)]

# 距離計算
filtered_data['駅からの距離'] = filtered_data.apply(lambda row: calculate_distance(station_lat, station_lon, row['緯度'], row['経度']), axis=1)
filtered_data['バス停からの距離'] = filtered_data.apply(lambda row: calculate_distance(bus_lat, bus_lon, row['緯度'], row['経度']), axis=1)

# ソート
sorted_data = filtered_data.sort_values(by='駅からの距離')

# 地図生成
m = folium.Map(location=[station_lat, station_lon], zoom_start=14)
folium.Marker([station_lat, station_lon], popup=f"{selected_station} (駅)", icon=folium.Icon(color="red")).add_to(m)
folium.Marker([bus_lat, bus_lon], popup=f"{selected_bus_stop} (バス停)", icon=folium.Icon(color="green")).add_to(m)

# バスルート表示
route = get_transit_route(bus_lat, bus_lon, station_lat, station_lon)
if route:
    route.add_to(m)
else:
    st.warning("🚫 バスを含む公共交通ルートが見つかりませんでした。")
    st.markdown(f"[Google マップで確認](https://www.google.com/maps/dir/?api=1&origin={bus_lat},{bus_lon}&destination={station_lat},{station_lon}&travelmode=transit)")

# 物件マーカー
for _, row in sorted_data.iterrows():
    folium.Marker(
        location=(row['緯度'], row['経度']),
        popup=f"{row['物件名']}<br>¥{row['家賃']:,}<br>駅から: {row['駅からの距離']:.2f}km<br>バス停から: {row['バス停からの距離']:.2f}km",
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)

# 地図表示
st.write("### 🚏 駅・バスルートと物件の可視化マップ")
components.html(m._repr_html_(), height=600, scrolling=True)
