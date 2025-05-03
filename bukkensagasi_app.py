import pandas as pd
import folium
import streamlit as st
from math import radians, sin, cos, sqrt, atan2
import requests
import streamlit.components.v1 as components
import googlemaps

# Google Maps APIキーをStreamlit Secretsから取得
google_maps_api_key = st.secrets["google_maps"]["api_key"]

# Google Maps APIクライアントの設定
gmaps = googlemaps.Client(key=google_maps_api_key)

# Haversineの公式を使用して、2点間の距離を計算
def calculate_distance(lat1, lon1, lat2, lon2):
    # 地球の半径 (km)
    R = 6371.0

    # 緯度経度をラジアンに変換
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # 緯度差と経度差を計算
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # 距離計算
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c  # 距離を計算 (km)
    return distance

# 駅の緯度経度データ（例）
stations = {
    "渋谷駅": {"lat": 35.658034, "lon": 139.701636},
    "新宿駅": {"lat": 35.6895, "lon": 139.6917},
    "池袋駅": {"lat": 35.7333, "lon": 139.7113},
    "東京駅": {"lat": 35.681236, "lon": 139.767125},
    # 他の駅を追加することができます
}

# バス停の緯度経度データ（仮）
bus_stops = {
    "渋谷バス停": {"lat": 35.658500, "lon": 139.701800},
    "新宿バス停": {"lat": 35.6898, "lon": 139.6921},
    "池袋バス停": {"lat": 35.7335, "lon": 139.7118},
    # 他のバス停を追加することができます
}

# Google Maps Directions APIを利用してバス停から駅までのルートを取得
def get_bus_route(start_lat, start_lon, end_lat, end_lon, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_lat},{start_lon}&destination={end_lat},{end_lon}&mode=transit&transit_mode=bus&key={api_key}"
    response = requests.get(url)
    directions = response.json()
    if directions['status'] == 'OK':
        route = directions['routes'][0]
        return route['overview_polyline']['points']
    else:
        return None

# データ読み込み関数
@st.cache_data
def load_data():
    sheet_id = "1bVzMw7TcnzGnqZWS6bjt1K5uopZWXjYWcHeFV3AgehQ"
    sheet_name = "bukken"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(sheet_url)
    df.rename(columns=lambda x: x.strip(), inplace=True)
    return df

# サイドバーに駅選択と家賃フィルタを表示
st.sidebar.title("物件検索")
selected_station = st.sidebar.selectbox("駅を選んでください", list(stations.keys()))

# 選ばれた駅の緯度経度を取得
station_lat = stations[selected_station]["lat"]
station_lon = stations[selected_station]["lon"]

# 家賃スライダー
min_rent, max_rent = st.sidebar.slider(
    "家賃を選んでください",
    min_value=0,
    max_value=500000,
    value=(0, 300000),
    step=5000,
)

# バス停選択
selected_bus_stop = st.sidebar.selectbox("バス停を選んでください", list(bus_stops.keys()))

# バス停の緯度経度を取得
bus_lat = bus_stops[selected_bus_stop]["lat"]
bus_lon = bus_stops[selected_bus_stop]["lon"]

# Google Maps APIキー（ここに自分のAPIキーを設定）
api_key = google_maps_api_key

# バス停から駅までのルートを取得
route_polyline = get_bus_route(bus_lat, bus_lon, station_lat, station_lon, api_key)

# データの読み込み
property_data = load_data()

# 家賃でフィルタリング
filtered_data = property_data[(property_data['家賃'] >= min_rent) & (property_data['家賃'] <= max_rent)]

# 駅との距離を計算して、距離が近い順に並べ替え
filtered_data['駅からの距離'] = filtered_data.apply(
    lambda row: calculate_distance(station_lat, station_lon, row['緯度'], row['経度']),
    axis=1
)

# バス停との距離を計算
filtered_data['バス停からの距離'] = filtered_data.apply(
    lambda row: calculate_distance(bus_lat, bus_lon, row['緯度'], row['経度']),
    axis=1
)

sorted_data = filtered_data.sort_values(by='駅からの距離')

# 地図に物件をマーカーとして追加
m = folium.Map(location=[station_lat, station_lon], zoom_start=14)

# バス停と駅を地図にマーカーとして追加
folium.Marker(
    location=[bus_lat, bus_lon],
    popup=f"{selected_bus_stop} (バス停)",
    icon=folium.Icon(color="green", icon="cloud"),
).add_to(m)

folium.Marker(
    location=[station_lat, station_lon],
    popup=f"{selected_station} (駅)",
    icon=folium.Icon(color="red", icon="cloud"),
).add_to(m)

# バスルートを地図に追加
if route_polyline:
    folium.PolyLine(
        locations=folium.util.decode_polyline(route_polyline),
        color="blue",
        weight=5,
        opacity=0.7,
    ).add_to(m)

# 物件のマーカーを追加
for _, row in sorted_data.iterrows():
    folium.Marker(
        location=(row["緯度"], row["経度"]),
        popup=f"{row['物件名']} - ¥{row['家賃']:,}<br>駅からの距離: {row['駅からの距離']:.2f} km<br>バス停からの距離: {row['バス停からの距離']:.2f} km",
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)

# 地図をStreamlitに表示
st.write("物件の地図（駅とバス停から近い順）")
map_html = m._repr_html_()  # foliumマップをHTML形式に変換
components.html(map_html, height=600)  # StreamlitでHTMLを埋め込む

