import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# データ読み込み
@st.cache_data
def load_data():
    sheet_id = "1bVzMw7TcnzGnqZWS6bjt1K5uopZWXjYWcHeFV3AgehQ"
    sheet_name = "シート1"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(sheet_url)
    df.rename(columns=lambda x: x.strip(), inplace=True)
    return df

property_data = load_data()
filtered_data = property_data.copy()  # ここで定義しておくと安全

# 地図作成
m = folium.Map(location=[35.681236, 139.767125], zoom_start=12)

# マーカー追加
for _, row in filtered_data.iterrows():
    folium.Marker(
        location=(row["緯度"], row["経度"]),
        popup=f"{row['物件名']} - ¥{row['家賃']:,}",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

# 地図表示
st_folium(m, width=700, height=500)

