import pandas as pd
import folium
import streamlit as st
from math import radians, sin, cos, sqrt, atan2
import streamlit.components.v1 as components

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

# データ読み込み関数
@st.cache_data
def load_data():
    sheet_id = "1bVzMw7TcnzGnqZWS6bjt1K5uopZWXjYWcHeFV3AgehQ"
    sheet_name = "bukken"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(sheet_url)
    df.rename(columns=lambda x: x.strip(), inplace=True)
    return df

# ユーザーが選べる駅を表示
selected_station = st.selectbox("駅を選んでください", list(stations.keys()))

# 選ばれた駅の緯度経度を取得
station_lat = stations[selected_station]["lat"]
station_lon = stations[selected_station]["lon"]

# データの読み込み
property_data = load_data()

# 家賃フィルター
min_rent = st.number_input("最小家賃", min_value=0, step=1000)
max_rent = st.number_input("最大家賃", min_value=0, step=1000)

# 家賃でフィルタリング
filtered_data = property_data[(property_data['家賃'] >= min_rent) & (property_data['家賃'] <= max_rent)]

# 駅との距離を計算して、距離が近い順に並べ替え
filtered_data['距離'] = filtered_data.apply(
    lambda row: calculate_distance(station_lat, station_lon, row['緯度'], row['経度']),
    axis=1
)
sorted_data = filtered_data.sort_values(by='距離')

# 地図に物件をマーカーとして追加
m = folium.Map(location=[station_lat, station_lon], zoom_start=14)

# 物件のマーカーを追加
for _, row in sorted_data.iterrows():
    folium.Marker(
        location=(row["緯度"], row["経度"]),
        popup=f"{row['物件名']} - ¥{row['家賃']:,}",
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)

# 地図をStreamlitに表示
st.write("物件の地図（駅を中心に近い順）")
map_html = m._repr_html_()  # foliumマップをHTML形式に変換
components.html(map_html, height=600)  # StreamlitでHTMLを埋め込む
