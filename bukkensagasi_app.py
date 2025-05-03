import streamlit as st
import pandas as pd
import folium
import googlemaps
from streamlit_folium import st_folium

# Google Maps APIの設定
gmaps = googlemaps.Client(key=st.secrets["google_maps"]["api_key"])

# ページ設定
st.set_page_config(page_title="通勤時間物件マップ", layout="wide")

# ------------------------------
# サイドバー：ユーザー入力
# ------------------------------
with st.sidebar:
    st.header("🔧 条件を選択")
    station = st.selectbox("出発駅", ["東京駅", "新宿駅", "渋谷駅"])
    max_time = st.slider("最大通勤時間（分）", min_value=10, max_value=60, value=30)

# データ読み込み
@st.cache_data
def load_data():
    sheet_id = "1bVzMw7TcnzGnqZWS6bjt1K5uopZWXjYWcHeFV3AgehQ"
    sheet_name = "bukken1"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    data = pd.read_csv(sheet_url)
    data.rename(columns=lambda x: x.strip(), inplace=True)  # 空白除去
    return data

# 物件データを取得
property_data = load_data()

# 出発駅の緯度経度
station_coords = {
    "東京駅": (35.681236, 139.767125),
    "新宿駅": (35.689634, 139.700582),
    "渋谷駅": (35.658034, 139.701636),
}

# ------------------------------
# メインタイトル
# ------------------------------
st.markdown("## 🚃 通勤時間で探せる物件マップ")
st.markdown("出発駅からの通勤時間をもとに、おすすめの物件をマップと一覧で表示します。")

# ------------------------------
# Foliumマップ作成
# ------------------------------
m = folium.Map(location=station_coords[station], zoom_start=12, control_scale=True)

# マーカー追加（全件）
for _, row in property_data.iterrows():
    folium.Marker(
        location=(row["緯度"], row["経度"]),
        popup=f"{row['物件名']} - ¥{row['家賃']:,}",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

st.write("カラム一覧:", property_data.columns.tolist())

# 物件マーカー（フィルター後）
for idx, row in filtered_data.iterrows():
    folium.Marker(
        location=(row["緯度"], row["経度"]),
        popup=f"{row['物件名']} - ¥{row['家賃']:,}",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

# 地図を表示
st_folium(m, width=700, height=500)

# ------------------------------
# 物件一覧のカード表示
# ------------------------------
st.markdown("### 🏘️ 物件情報")

for _, row in property_data.iterrows():
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

# ------------------------------
# 表形式（必要に応じて）
# ------------------------------
with st.expander("📄 テーブル形式で表示"):
    st.dataframe(property_data[["name", "address", "rent"]])

# データフレームのカラム名を表示
st.write(dummy_data.columns)

# データフレームの最初の数行を表示して内容を確認
st.write(dummy_data.head())

