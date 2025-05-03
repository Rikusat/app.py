import streamlit as st
import googlemaps
import requests
import folium
from streamlit_folium import folium_static

# Google Maps APIキーを読み込み
api_key = st.secrets["google_maps"]["api_key"]
gmaps = googlemaps.Client(key=api_key)

# 駅やバス停の座標データ（仮データ）
bus_stops = {
    "渋谷バス停": (35.658500, 139.701800),
    "新宿バス停": (35.6898, 139.6921),
    "池袋バス停": (35.7335, 139.7118),
    "東京バス停": (35.681236, 139.767125),
}

# タイトル
st.title("🚌 バス運行ルート表示アプリ")

# サイドバーで出発地と目的地を選択
start = st.sidebar.selectbox("🟢 出発バス停を選んでください", list(bus_stops.keys()))
end = st.sidebar.selectbox("🔴 目的バス停を選んでください", list(bus_stops.keys()))

start_lat, start_lon = bus_stops[start]
end_lat, end_lon = bus_stops[end]

# Google Directions API でバスルート取得
def get_bus_directions(origin_lat, origin_lon, dest_lat, dest_lon, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin_lat},{origin_lon}&destination={dest_lat},{dest_lon}&mode=transit&transit_mode=bus&key={api_key}"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "OK":
        points = data["routes"][0]["overview_polyline"]["points"]
        return points
    else:
        st.error(f"APIエラー: {data.get('error_message', 'ルートが見つかりませんでした')}")
        return None

# ルート取得
polyline = get_bus_directions(start_lat, start_lon, end_lat, end_lon, api_key)

# 地図生成
m = folium.Map(location=[(start_lat + end_lat) / 2, (start_lon + end_lon) / 2], zoom_start=13)

# 出発地と目的地をマップに表示
folium.Marker([start_lat, start_lon], tooltip=f"{start}（出発）", icon=folium.Icon(color='green')).add_to(m)
folium.Marker([end_lat, end_lon], tooltip=f"{end}（目的）", icon=folium.Icon(color='red')).add_to(m)

# ルート線を地図に追加
if polyline:
    folium.PolyLine(
        locations=folium.utilities.decode_polyline(polyline),
        color="blue",
        weight=5,
        opacity=0.7,
        tooltip="🚌 バスルート"
    ).add_to(m)

# 地図を表示
folium_static(m, height=600)
