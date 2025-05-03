import requests
import streamlit as st

api_key = st.secrets["google_maps"]["api_key"]
origin = "35.6895,139.6917"  # 新宿駅
destination = "35.658034,139.701636"  # 渋谷駅

url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=transit&transit_mode=bus&key={api_key}"
response = requests.get(url)
data = response.json()

st.write("📡 API レスポンス:")
st.json(data)

if data.get("status") != "OK":
    st.error(f"❌ APIエラー: {data.get('error_message', '不明なエラー')}")
else:
    st.success("✅ APIリクエスト成功！")
