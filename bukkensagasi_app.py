import streamlit as st
import pandas as pd
import folium
import googlemaps
from streamlit_folium import st_folium

# Google Maps APIキー設定
google_maps_api_key = st.secrets["google_maps"]["api_key"]
gmaps = googlemaps.Client(key=google_maps_api_key)

# データ読み込み関数
@st.cache_data
def load_data():
    sheet_id = "1bVzMw7TcnzGnqZWS6bjt1K5uopZWXjYWcHeFV3AgehQ"
    sheet_name = "bukken"
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

# 最寄り駅から物件へのバスルートを表示
def get_bus_route(origin_address, destination_address, api_key):
    directions = gmaps.directions(
        origin=origin_address,
        destination=destination_address,
        mode="transit",
        transit_mode="bus",
        key=api_key
    )
    
    if directions:
        route = directions[0]['legs'][0]
        route_points = route['steps']
        route_polyline = route['overview_polyline']['points']
        return route_points, route_polyline
    return None, None

# バスルートの描画
def draw_route_on_map(route_points, map_obj):
    for step in route_points:
        if "polyline" in step:
            folium.PolyLine(
                locations=folium.PolyLine.decode(step["polyline"]["points"]),
                color="blue",
                weight=5,
                opacity=0.7
            ).add_to(map_obj)

# 物件情報のマーカーを追加
for _, row in filtered_data.iterrows():
    property_name = row["物件名"]
    property_address = row["住所"]
    property_lat = row["緯度"]
    property_lon = row["経度"]
    
    # 最寄り駅の名前を仮に入力
    nearest_station = "渋谷駅"
    
    # バスルート取得
    route_points, route_polyline = get_bus_route(nearest_station, property_address, google_maps_api_key)

    # バスルートが見つかった場合
    if route_points:
        # ルートを地図上に描画
        draw_route_on_map(route_points, m)
    
    # 物件マーカー追加
    folium.Marker(
        location=(property_lat, property_lon),
        popup=f"{property_name} - ¥{row['家賃']:,}",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

# 結果表示
st.subheader("検索結果")
st.write(f"{len(filtered_data)} 件の物件が見つかりました。")
st.dataframe(filtered_data)

# 地図描画
st_folium(m, width=700, height=500)
