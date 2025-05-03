import streamlit as st
import pandas as pd
import googlemaps
import folium
from streamlit_folium import st_folium
import time

# Google Maps APIキーを読み込み
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

# ------------------------------
# ダミー物件データ（緯度経度つき）
# ------------------------------
dummy_data = pd.DataFrame([
    {"name": "物件A", "address": "千代田区1-1-1", "rent": 120000, "lat": 35.681236, "lon": 139.767125},
    {"name": "物件B", "address": "中央区2-2-2", "rent": 100000, "lat": 35.673343, "lon": 139.770987},
    {"name": "物件C", "address": "新宿区3-3-3", "rent": 90000,  "lat": 35.693825, "lon": 139.703356},
    {"name": "物件D", "address": "渋谷区4-4-4", "rent": 110000, "lat": 35.658034, "lon": 139.701636},
    {"name": "物件E", "address": "品川区5-5-5", "rent": 95000,  "lat": 35.609226, "lon": 139.730186},
    {"name": "物件F", "address": "豊島区6-6-6", "rent": 85000,  "lat": 35.728926, "lon": 139.71038},
    {"name": "物件G", "address": "目黒区7-7-7", "rent": 98000,  "lat": 35.641018, "lon": 139.698212},
    {"name": "物件H", "address": "文京区8-8-8", "rent": 102000, "lat": 35.717356, "lon": 139.752799},
])

# ------------------------------
# 通勤時間フィルタリング
# ------------------------------
st.markdown("## 🚃 通勤時間で探せる物件マップ")
st.write("出発駅からの通勤時間を元に、公共交通機関でアクセス可能な物件を表示します。")

progress_text = "通勤時間を計算中..."
progress_bar = st.progress(0, text=progress_text)

filtered_properties = []
for i, (_, row) in enumerate(dummy_data.iterrows()):
    try:
        result = gmaps.distance_matrix(
            origins=station + "駅",
            destinations=f"{row['lat']},{row['lon']}",
            mode="transit",
            language="ja"
        )
        duration_sec = result["rows"][0]["elements"][0]["duration"]["value"]
        duration_min = duration_sec // 60
        if duration_min <= max_time:
            row_dict = row.to_dict()
            row_dict["commute_time"] = duration_min
            filtered_properties.append(row_dict)
    except Exception as e:
        print("Error:", e)
        continue
    progress_bar.progress((i + 1) / len(dummy_data), text=progress_text)
    time.sleep(0.5)  # 連続アクセス制限対策

progress_bar.empty()

filtered_data = pd.DataFrame(filtered_properties)

# ------------------------------
# マップ表示
# ------------------------------
if not filtered_data.empty:
    m = folium.Map(location=(filtered_data["lat"].mean(), filtered_data["lon"].mean()), zoom_start=12)
    
    # 出発駅マーカー
    folium.Marker(
        location=gmaps.geocode(station + "駅")[0]["geometry"]["location"].values(),
        popup=f"出発駅：{station}",
        icon=folium.Icon(color="blue", icon="train", prefix="fa")
    ).add_to(m)

    # 物件マーカー
    for _, row in filtered_data.iterrows():
        folium.Marker(
            location=(row["lat"], row["lon"]),
            popup=f'{row["name"]}<br>家賃: ¥{row["rent"]:,}<br>通勤: {row["commute_time"]}分',
            icon=folium.Icon(color="green", icon="home", prefix="fa")
        ).add_to(m)

    st_folium(m, width=1000, height=500)

    # ------------------------------
    # 物件一覧表示
    # ------------------------------
    st.markdown("### 🏘️ 該当物件一覧")
    for _, row in filtered_data.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div style="border:1px solid #ccc; border-radius:10px; padding:10px; margin-bottom:10px;">
                    <strong>{row['name']}</strong><br>
                    📍 {row['address']}<br>
                    💰 家賃: ¥{row['rent']:,}<br>
                    ⏱ 通勤時間: {row['commute_time']}分
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.warning("条件に合う物件が見つかりませんでした。")

# ------------------------------
# テーブル表示（任意）
# ------------------------------
with st.expander("📄 表形式で見る"):
    if not filtered_data.empty:
        st.dataframe(filtered_data[["name", "address", "rent", "commute_time"]])
    else:
        st.info("データがありません。")

