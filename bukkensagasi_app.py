import streamlit as st
import requests
import pandas as pd

# 不動産APIのエンドポイント
API_URL = "https://api.realestateapi.com/v1/properties"

# APIの取得関数
def fetch_properties():
    # 必要なパラメータを指定してAPIを呼び出し
    params = {
        "city": "Tokyo",  # 都市名を指定（例：東京）
        "min_price": 50000,  # 最小価格
        "max_price": 200000,  # 最大価格
        "page": 1  # 1ページ目のデータ
    }
    
    # APIリクエスト
    response = requests.get(API_URL, params=params)
    
    if response.status_code == 200:
        return response.json()  # JSON形式でレスポンスを返す
    else:
        st.error(f"APIリクエストエラー: {response.status_code}")
        return []

# 物件データの取得
property_data = fetch_properties()

# 物件データがある場合、表示
if property_data:
    # 物件情報のDataFrame作成
    df = pd.DataFrame(property_data)
    
    # 物件一覧表示
    st.subheader("物件一覧")
    st.write(f"{len(df)} 件の物件が見つかりました。")
    st.dataframe(df)
else:
    st.write("物件情報は見つかりませんでした。")

