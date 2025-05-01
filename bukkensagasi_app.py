import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="通勤時間物件マップ", layout="wide")

st.title("🚃 通勤時間で探せる物件マップ")

# 出発駅の選択（ダミー）
station = st.selectbox("出発駅を選択してください", ["東京駅", "新宿駅", "渋谷駅"])
max_time = st.slider("通勤時間（分）", min_value=10, max_value=60, value=30)

# 仮の物件データ（緯度経度付き）
dummy_data = pd.DataFrame([
    {"name": "物件A", "address": "千代田区1-1-1", "rent": 120000, "lat": 35.681236, "lon": 139.767125},
    {"name": "物件B", "address": "中央区2-2-2", "rent": 100000, "lat": 35.673343, "lon": 139.770987},
    {"name": "物件C", "address": "新宿区3-3-3", "rent": 90000,  "lat": 35.693825, "lon": 139.703356},
])

# 出発駅の緯度経度（仮）
station_coords = {
    "東京駅": (35.681236, 139.767125),
    "新宿駅": (35.689634, 139.700582),
    "渋谷駅": (35.658034, 139.701636),
}

# Foliumマップの作成
m = folium.Map(location=station_coords[station], zoom_start=12)

# 出発地マーカー
folium.Marker(
    location=station_coords[station],
    popup=f"出発駅：{station}",
    icon=folium.Icon(color="blue")
).add_to(m)

# 物件マーカー
for _, row in dummy_data.iterrows():
    folium.Marker(
        location=(row["lat"], row["lon"]),
        popup=f'{row["name"]}<br>家賃: ¥{row["rent"]:,}',
        icon=folium.Icon(color="green")
    ).add_to(m)

# 地図表示
st_folium(m, width=700, height=500)

# テーブル表示
st.subheader("物件一覧")
st.dataframe(dummy_data[["name", "address", "rent"]])
