import requests
import googlemaps
import streamlit as st

# APIキーの設定（Streamlit secretsから取得）
google_maps_api_key = st.secrets["google_maps"]["api_key"]
gmaps = googlemaps.Client(key=google_maps_api_key)

# Google Maps Directions APIを利用してバス停から駅までのルートを取得
def get_bus_route_by_address(origin_address, destination_address, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin_address}&destination={destination_address}&mode=transit&transit_mode=bus&key={api_key}"
    response = requests.get(url)
    directions = response.json()

    if directions['status'] == 'OK':
        route = directions['routes'][0]
        return route['overview_polyline']['points']
    else:
        return None

# サイドバーに駅選択と家賃フィルタを表示
st.sidebar.title("物件検索")
selected_station = st.sidebar.selectbox("駅を選んでください", ["渋谷駅", "新宿駅", "池袋駅", "東京駅"])

# 選ばれた駅に対応する住所（今回は例として）
station_addresses = {
    "渋谷駅": "Shibuya Station, Tokyo",
    "新宿駅": "Shinjuku Station, Tokyo",
    "池袋駅": "Ikebukuro Station, Tokyo",
    "東京駅": "Tokyo Station, Tokyo"
}

# 住所を選んだ駅に基づいて取得
origin_address = station_addresses[selected_station]

# バス停選択
selected_bus_stop = st.sidebar.selectbox("バス停を選んでください", ["渋谷バス停", "新宿バス停", "池袋バス停"])

# バス停に対応する住所（仮）
bus_stop_addresses = {
    "渋谷バス停": "Shibuya Bus Stop, Tokyo",
    "新宿バス停": "Shinjuku Bus Stop, Tokyo",
    "池袋バス停": "Ikebukuro Bus Stop, Tokyo"
}

# バス停の住所を選択に基づいて取得
destination_address = bus_stop_addresses[selected_bus_stop]

# バスルートを取得
route_polyline = get_bus_route_by_address(origin_address, destination_address, google_maps_api_key)

# 結果を表示
if route_polyline:
    st.write(f"駅: {selected_station} から {selected_bus_stop} までのバスルートが取得できました！")
else:
    st.write("指定された駅とバス停の間でバスルートが見つかりませんでした。")
