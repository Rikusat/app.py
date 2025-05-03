import streamlit as st
import pandas as pd
import googlemaps
import folium
from streamlit_folium import st_folium

# APIキーをStreamlit Secretsから取得
API_KEY = st.secrets["google"]["api_key"]
gmaps = googlemaps.Client(key=API_KEY)

# 出発駅の緯度経度
station_coords = {
    "東京駅": (35.681236, 139.767125),
    "新宿駅": (35.689634, 139.700582),
    "渋谷駅": (35.658034, 139.701636),
}

# 仮の物件データ（緯度経度付き）
dummy_data = pd.DataFrame([
    {"name": "物件A", "address": "千代田区1-1-1", "rent": 120000, "lat": 35.681236, "lon": 139.767125},
    {"name": "物件B", "address": "中央区2-2-2", "rent": 100000, "lat": 35.673343, "lon": 139.770987},
    {"name": "物件C", "address": "新宿区3-3-3", "rent": 90000,  "lat": 35.693825, "lon": 139.703356},
])

# Streamlit ページ設定
st.set_page_config(page_title="通勤時間物件マップ", layout="wide")

# サイドバー：条件入力
with st.sidebar:
    st.header("🔧 条件を選択")
    station = st.selectbox("出発駅", list(station_coords.keys()))
    max_time = st.slider("最大通勤時間（分）", 10, 60, 30)

# 通勤時間を取得してフィルタリング
def is_within_commute(lat, lon):
    try:
        result = gmaps.directions(
            origin=station_coords[station],
            destination=(lat, lon),
            mode="transit",
            departure_time="now"
        )
        duration = result[0]['legs'][0]['duration']['value'] / 60  # 秒→分
        return duration <= max_time
    except Exception as e:
        return False

filtered_data = dummy_data[dummy_data.apply(lambda row: is_within_commute(row["lat"], row["lon"]), axis=1)]

# メインタイトル
st.title("🚃 通勤時間で探せる物件マップ")
st.markdown("出発駅からの通勤時間をもとに、おすすめの物件をマップと一覧で表示します。")

# マップ作成
m = folium.Map(location=station_coords[station], zoom_start=12, control_scale=True)
folium.Marker(
    location=station_coords[station],
    popup=f"出発駅：{station}",
    icon=folium.Icon(color="blue", icon="train", prefix='fa')
).add_to(m)

for _, row in filtered_data.iterrows():
    folium.Marker(
        location=(row["lat"], row["lon"]),
        popup=f'{row["name"]}<br>家賃: ¥{row["rent"]:,}',
        icon=folium.Icon(color="green", icon="home", prefix='fa')
    ).add_to(m)

st_folium(m, width=1000, height=500)

# 物件情報表示
st.subheader("🏘️ 条件に合う物件一覧")
for _, row in filtered_data.iterrows():
    with st.container():
        st.markdown(
            f"""
            <div style="border:1px solid #ccc; border-radius:10px; padding:10px; margin-bottom:10px;">
                <strong>{row['name']}</strong><br>
                📍 {row['address']}<br>
                💰 家賃: ¥{row['rent']:,}
            </div>
            """,
            unsafe_allow_html=True
        )

with st.expander("📄 テーブル形式で表示"):
    st.dataframe(filtered_data[["name", "address", "rent"]])
