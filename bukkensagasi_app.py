import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# データ読み込み関数
@st.cache_data
def load_data():
    sheet_id = "1bVzMw7TcnzGnqZWS6bjt1K5uopZWXjYWcHeFV3AgehQ"
    sheet_name = "シート1"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(sheet_url)
    df.rename(columns=lambda x: x.strip(), inplace=True)
    return df

# データ取得
property_data = load_data()

# Sidebar フィルター
st.sidebar.header("検索条件")

# 家賃フィルター
min_rent = int(property_data["家賃"].min())
max_rent = int(property_data["家賃"].max())

rent_range = st.sidebar.slider(
    "家賃の範囲 (円)",
    min_value=min_rent,
    max_value=max_rent,
    value=(min_rent, max_rent),
    step=10000
)

# エリアフィルター（住所に含まれる文字列）
address_options = sorted(property_data["住所"].apply(lambda x: x[:3]).unique())
selected_areas = st.sidebar.multiselect("エリアで絞り込み", address_options, default=address_options)

# フィルター適用
filtered_data = property_data[
    (property_data["家賃"] >= rent_range[0]) &
    (property_data["家賃"] <= rent_range[1]) &
    (property_data["住所"].str[:3].isin(selected_areas))
]

# 地図表示
m = folium.Map(location=[35.681236, 139.767125], zoom_start=12)

# マーカー追加
for _, row in filtered_data.iterrows():
    folium.Marker(
        location=(row["緯度"], row["経度"]),
        popup=f"{row['物件名']} - ¥{row['家賃']:,}",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

# 結果表示
st.subheader("検索結果")
st.write(f"{len(filtered_data)} 件の物件が見つかりました。")
st.dataframe(filtered_data)

# 地図描画
st_folium(m, width=700, height=500)
