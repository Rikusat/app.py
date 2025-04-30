import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

# ----------------------------
# 仮データの設定
# ----------------------------
data = [
    {"name": "サンプル物件A", "address": "東京都渋谷区渋谷1-1-1", "rent": 120000},
    {"name": "サンプル物件B", "address": "東京都新宿区西新宿2-2-2", "rent": 95000},
    {"name": "サンプル物件C", "address": "東京都品川区大井3-3-3", "rent": 110000},
]

# ----------------------------
# ジオコーディング（緯度経度取得）
# ----------------------------
geolocator = Nominatim(user_agent="real_estate_app")
for d in data:
    location = geolocator.geocode(d["address"])
    if location:
        d["lat"] = location.latitude
        d["lon"] = location.longitude
    else:
        d["lat"], d["lon"] = None, None

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(layout="wide")
st.title("通える物件マップ（デモ）")

station_input = st.text_input("出発地（駅名などを入力）", "東京駅")

# 地図の初期表示位置
start_location = geolocator.geocode(station_input)
if start_location:
    map_center = [start_location.latitude, start_location.longitude]
else:
    st.warning("出発地の位置を取得できませんでした。")
    map_center = [35.681236, 139.767125]  # 東京駅座標

m = folium.Map(location=map_center, zoom_start=12)

# 出発地のマーカー
folium.Marker(
    location=map_center,
    popup=f"出発地：{station_input}",
    icon=folium.Icon(color="blue", icon="train", prefix="fa")
).add_to(m)

# 物件マーカー
for d in data:
    if d["lat"] and d["lon"]:
        popup_text = f"{d['name']}\n家賃: ¥{d['rent']:,}"
        folium.Marker(
            location=[d["lat"], d["lon"]],
            popup=popup_text,
            icon=folium.Icon(color="green", icon="home", prefix="fa")
        ).add_to(m)

# 地図描画
st_data = st_folium(m, width=800, height=600)

# 一覧表示
st.subheader("物件一覧")
st.dataframe(pd.DataFrame(data))

