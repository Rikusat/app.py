import requests
import googlemaps
import streamlit as st

# Google Maps APIキーを取得
google_maps_api_key = st.secrets["google_maps"]["api_key"]
gmaps = googlemaps.Client(key=google_maps_api_key)

# 住所を使ってバスルートを取得
def get_bus_route_by_address(origin_address, destination_address, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin_address}&destination={destination_address}&mode=transit&transit_mode=bus&key={api_key}"
    response = requests.get(url)
    directions = response.json()
    if directions['status'] == 'OK':
        route = directions['routes'][0]
        return route['overview_polyline']['points']
    else:
        return None

# スプレッドシートから物件データを読み込む
@st.cache_data
def load_data():
    sheet_id = "1bVzMw7TcnzGnqZWS6bjt1K5uopZWXjYWcHeFV3AgehQ"
    sheet_name = "bukken"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(sheet_url)
    df.rename(columns=lambda x: x.strip(), inplace=True)
    return df

# スプレッドシートデータの読み込み
property_data = load_data()

# サイドバーに物件情報を表示
st.sidebar.title("物件検索")
selected_property = st.sidebar.selectbox("物件を選んでください", property_data['物件名'].tolist())

# 選ばれた物件の情報を取得
selected_property_data = property_data[property_data['物件名'] == selected_property].iloc[0]
property_address = selected_property_data['住所']
property_lat = selected_property_data['緯度']
property_lon = selected_property_data['経度']

# 最寄り駅の住所
station_address = st.sidebar.text_input("最寄り駅を入力してください", "渋谷駅")

# バスルートを取得
route_polyline = get_bus_route_by_address(station_address, property_address, google_maps_api_key)

# バスルートの表示
if route_polyline:
    st.write(f"物件「{selected_property}」の最寄り駅「{station_address}」からバスルートを取得しました！")
else:
    st.write("指定された駅と物件間でバスルートが見つかりませんでした。")


