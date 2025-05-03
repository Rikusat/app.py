import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# 駅の緯度経度リスト
station_coords = {
    "東京駅": (35.681236, 139.767125),
    "新宿駅": (35.689487, 139.700302),
    "渋谷駅": (35.658034, 139.701636),
    "上野駅": (35.713768, 139.777254),
    "品川駅": (35.628471, 139.73876),
}

# 駅選択
selected_station = st.selectbox("駅を選択してください", list(station_coords.keys()))

# 家賃フィルター（元のままでOK）
min_rent, max_rent = st.slider("家賃の範囲（円）", 50000, 200000, (80000, 150000))

# データ読み込み（キャッシュ関数のまま）
property_data = load_data()

# フィルター処理
filtered_data = property_data[
    (property_data["家賃"] >= min_rent) & (property_data["家賃"] <= max_rent)
].copy()

# 距離計算
station_latlon = station_coords[selected_station]
filtered_data["距離（km）"] = filtered_data.apply(
    lambda row: geodesic(station_latlon, (row["緯度"], row["経度"])).km,
    axis=1
)

# 距離順にソート
filtered_data = filtered_data.sort_values("距離（km）")

# 地図表示
m = folium.Map(location=station_latlon, zoom_start=12)
folium.Marker(location=station_latlon, popup=f"{selected_station}（基準駅）", icon=folium.Icon(color="red")).add_to(m)

for _, row in filtered_data.iterrows():
    folium.Marker(
        location=(row["緯度"], row["経度"]),
        popup=f"{row['物件名']} - ¥{row['家賃']:,}（{row['距離（km）']:.2f}km）",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

# 表示
st.write("物件一覧（近い順）", filtered_data[["物件名", "住所", "家賃", "距離（km）"]])
st_data = st_folium(m, width=700)
