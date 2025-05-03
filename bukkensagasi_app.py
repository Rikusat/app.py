import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

# secrets.tomlからAPIキーを取得
api_key = st.secrets["realestateapi"]["api_key"]

# APIキーを使用した処理
st.write(f"取得したAPIキー: {api_key}")

# APIから物件情報を取得する関数
def get_properties(api_key):
    url = f"https://api.example.com/properties?api_key={api_key}"  # APIのURLを変更
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data["properties"])
    else:
        st.error(f"API呼び出し失敗: {response.status_code}")
        return pd.DataFrame()

# 物件データをAPIから取得
property_data = get_properties(api_key)

# データが取得できた場合、物件情報を表示
if not property_data.empty:
    st.subheader("物件情報")

    # Sidebar フィルター
    st.sidebar.header("検索条件")

    # 家賃フィルター
    min_rent = int(property_data["rent"].min())
    max_rent = int(property_data["rent"].max())

    rent_range = st.sidebar.slider(
        "家賃の範囲 (円)",
        min_value=min_rent,
        max_value=max_rent,
        value=(min_rent, max_rent),
        step=10000
    )

    # フィルター適用
    filtered_data = property_data[
        (property_data["rent"] >= rent_range[0]) & 
        (property_data["rent"] <= rent_range[1])
    ]

    # 結果表示
    st.write(f"{len(filtered_data)} 件の物件が見つかりました。")
    st.dataframe(filtered_data)

    # 地図表示
    m = folium.Map(location=[35.681236, 139.767125], zoom_start=12)

    # マーカー追加
    for _, row in filtered_data.iterrows():
        folium.Marker(
            location=(row["latitude"], row["longitude"]),
            popup=f"{row['name']} - ¥{row['rent']:,}",
            icon=folium.Icon(color="blue", icon="home", prefix="fa")
        ).add_to(m)

    # 地図描画
    st_folium(m, width=700, height=500)
else:
    st.write("物件データが取得できませんでした。")

import time
import requests

def get_properties(api_key, retries=3, delay=2):
    url = f"https://api.example.com/properties?api_key={api_key}"
    
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # HTTPエラーステータスを確認
            return response.json()  # 成功した場合、JSONデータを返す
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                st.warning(f"接続エラーが発生しました。{delay}秒後に再試行します...")
                time.sleep(delay)  # リトライまでの待機時間
            else:
                st.error(f"エラーが発生しました: {e}")
                return None  # 最後のリトライでも失敗した場合はNoneを返す

# APIから物件情報を取得
property_data = get_properties(api_key)

if property_data:
    # データ処理・表示のコード
    st.write(property_data)
else:
    st.write("物件情報の取得に失敗しました。")

