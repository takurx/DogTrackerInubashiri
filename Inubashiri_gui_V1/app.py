import streamlit as st
import leafmap.foliumap as leafmap
import serial
import re
import time
import pandas as pd
from datetime import datetime
import threading
from collections import deque
from queue import Queue

# ページ設定
st.set_page_config(
    page_title="GPS Tracker - Inubashiri",
    page_icon="🐕",
    layout="wide"
)

# タイトル
st.title("🐕 GPS Tracker - Inubashiri")

# セッション状態の初期化
if 'gps_data' not in st.session_state:
    st.session_state.gps_data = deque(maxlen=1000)  # 最大1000ポイント保存
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'serial_thread' not in st.session_state:
    st.session_state.serial_thread = None
if 'current_position' not in st.session_state:
    st.session_state.current_position = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'data_queue' not in st.session_state:
    st.session_state.data_queue = Queue()
if 'stop_flag' not in st.session_state:
    st.session_state.stop_flag = threading.Event()

def parse_nmea_gpgga(line):
    """
    NMEA GPGGA形式のデータをパース
    例: $GPGGA,050358.00,3605.68559,N,14006.62865,E,1,06,1.31,21.2,M,39.3,M,,*61
    """
    pattern = r'\$GPGGA,(\d+\.\d+),(\d+\.\d+),([NS]),(\d+\.\d+),([EW]),(\d),(\d+),([^,]*),([^,]*),M'
    match = re.search(pattern, line)
    
    if match:
        time_str = match.group(1)
        lat_raw = float(match.group(2))
        lat_dir = match.group(3)
        lon_raw = float(match.group(4))
        lon_dir = match.group(5)
        quality = int(match.group(6))
        satellites = int(match.group(7))
        altitude = match.group(9)
        
        # 緯度を度に変換 (DDMM.MMMMM -> DD.DDDDDD)
        lat_deg = int(lat_raw / 100)
        lat_min = lat_raw - (lat_deg * 100)
        latitude = lat_deg + (lat_min / 60)
        if lat_dir == 'S':
            latitude = -latitude
        
        # 経度を度に変換 (DDDMM.MMMMM -> DDD.DDDDDD)
        lon_deg = int(lon_raw / 100)
        lon_min = lon_raw - (lon_deg * 100)
        longitude = lon_deg + (lon_min / 60)
        if lon_dir == 'W':
            longitude = -longitude
        
        return {
            'time': time_str,
            'latitude': latitude,
            'longitude': longitude,
            'quality': quality,
            'satellites': satellites,
            'altitude': altitude,
            'timestamp': datetime.now()
        }
    return None

def read_serial_data(port, baudrate, data_queue, stop_flag):
    """シリアルポートからデータを読み取る"""
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        
        while not stop_flag.is_set():
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line.startswith('$GPGGA'):
                    gps_info = parse_nmea_gpgga(line)
                    if gps_info and gps_info['quality'] > 0:
                        data_queue.put(('data', gps_info))
                        
            except Exception as e:
                data_queue.put(('error', f"データ読み取りエラー: {e}"))
                time.sleep(0.1)
                
        ser.close()
    except Exception as e:
        data_queue.put(('error', f"シリアルポート接続エラー: {e}"))

def read_test_file(filepath, data_queue, stop_flag):
    """テストファイルからデータを読み取る（デモモード）"""
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if stop_flag.is_set():
                    break
                    
                if line.startswith('$GPGGA'):
                    gps_info = parse_nmea_gpgga(line)
                    if gps_info and gps_info['quality'] > 0:
                        data_queue.put(('data', gps_info))
                        time.sleep(0.5)  # 0.5秒ごとに更新（デモ用）
                        
    except Exception as e:
        data_queue.put(('error', f"ファイル読み取りエラー: {e}"))

# サイドバー設定
st.sidebar.header("⚙️ 設定")

# モード選択
mode = st.sidebar.radio(
    "モード選択",
    ["シリアルポート", "テストファイル"],
    index=1
)

if mode == "シリアルポート":
    port = st.sidebar.text_input("シリアルポート", "/dev/ttyUSB0")
    baudrate = st.sidebar.number_input("ボーレート", value=115200, step=1)
else:
    test_file = st.sidebar.text_input("テストファイルパス", "test_input_data/test_input_data-0.txt")

# 開始/停止ボタン
col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("▶️ 開始", disabled=st.session_state.is_running):
        st.session_state.stop_flag.clear()
        st.session_state.is_running = True
        if mode == "シリアルポート":
            thread = threading.Thread(
                target=read_serial_data, 
                args=(port, baudrate, st.session_state.data_queue, st.session_state.stop_flag)
            )
            thread.daemon = True
            thread.start()
            st.session_state.serial_thread = thread
        else:
            thread = threading.Thread(
                target=read_test_file, 
                args=(test_file, st.session_state.data_queue, st.session_state.stop_flag)
            )
            thread.daemon = True
            thread.start()
            st.session_state.serial_thread = thread
        st.rerun()

with col2:
    if st.button("⏸️ 停止", disabled=not st.session_state.is_running):
        st.session_state.stop_flag.set()
        st.session_state.is_running = False
        time.sleep(0.5)
        st.rerun()

# データクリアボタン
if st.sidebar.button("🗑️ データクリア"):
    st.session_state.gps_data.clear()
    st.session_state.current_position = None
    st.rerun()

# ステータス表示
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 ステータス")
if st.session_state.is_running:
    st.sidebar.success("🟢 実行中")
else:
    st.sidebar.info("⚪ 停止中")

st.sidebar.metric("記録ポイント数", len(st.session_state.gps_data))

# キューからデータを取得してセッション状態を更新
while not st.session_state.data_queue.empty():
    msg_type, msg_data = st.session_state.data_queue.get()
    if msg_type == 'data':
        st.session_state.gps_data.append(msg_data)
        st.session_state.current_position = msg_data
    elif msg_type == 'error':
        st.session_state.error_message = msg_data

# エラーメッセージ表示（メインスレッドで）
if st.session_state.error_message:
    st.sidebar.error(st.session_state.error_message)
    st.session_state.error_message = None

# メインコンテンツ
if len(st.session_state.gps_data) > 0:
    # 現在位置情報
    if st.session_state.current_position:
        pos = st.session_state.current_position
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("緯度", f"{pos['latitude']:.6f}")
        with col2:
            st.metric("経度", f"{pos['longitude']:.6f}")
        with col3:
            st.metric("衛星数", pos['satellites'])
        with col4:
            st.metric("高度", f"{pos['altitude']} m")
    
    # 地図表示
    st.markdown("### 🗺️ GPS経路マップ")
    
    # データフレームに変換
    df = pd.DataFrame(list(st.session_state.gps_data))
    
    # 地図の中心を最新の位置に設定
    center_lat = df['latitude'].iloc[-1]
    center_lon = df['longitude'].iloc[-1]
    
    # Leafmapで地図作成
    m = leafmap.Map(center=[center_lat, center_lon], zoom=17)
    
    # 経路をラインで描画
    if len(df) > 1:
        import folium
        route_coords = [[row['latitude'], row['longitude']] for _, row in df.iterrows()]
        folium.PolyLine(
            route_coords,
            color='blue',
            weight=3,
            opacity=0.7,
            popup='GPS経路'
        ).add_to(m)
    
    # 開始地点マーカー
    if len(df) > 0:
        import folium
        first_point = df.iloc[0]
        folium.Marker(
            location=[first_point['latitude'], first_point['longitude']],
            popup=f"開始地点<br>時刻: {first_point['time']}",
            icon=folium.Icon(color='green')
        ).add_to(m)
    
    # 現在位置マーカー
    if st.session_state.current_position:
        import folium
        folium.Marker(
            location=[center_lat, center_lon],
            popup=f"現在位置<br>時刻: {pos['time']}<br>衛星数: {pos['satellites']}",
            icon=folium.Icon(color='red')
        ).add_to(m)
    
    # 地図を表示
    m.to_streamlit(height=600)
    
    # 統計情報
    st.markdown("### 📈 統計情報")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("総データポイント数", len(df))
    with col2:
        if len(df) > 1:
            # 簡易的な距離計算（ハバーサイン公式）
            from math import radians, sin, cos, sqrt, atan2
            
            total_distance = 0
            for i in range(1, len(df)):
                lat1, lon1 = radians(df.iloc[i-1]['latitude']), radians(df.iloc[i-1]['longitude'])
                lat2, lon2 = radians(df.iloc[i]['latitude']), radians(df.iloc[i]['longitude'])
                
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * atan2(sqrt(a), sqrt(1-a))
                distance = 6371000 * c  # 地球の半径(m)
                total_distance += distance
            
            st.metric("総移動距離", f"{total_distance:.1f} m")
        else:
            st.metric("総移動距離", "0 m")
    
    with col3:
        avg_sats = df['satellites'].mean()
        st.metric("平均衛星数", f"{avg_sats:.1f}")
    
    # データテーブル
    with st.expander("📋 詳細データを表示"):
        display_df = df[['time', 'latitude', 'longitude', 'satellites', 'altitude']].tail(50)
        st.dataframe(display_df, use_container_width=True)

else:
    st.info("👆 サイドバーから「開始」ボタンを押してGPSデータの取得を開始してください。")
    st.markdown("""
    ### 使い方
    
    1. **モード選択**: シリアルポートまたはテストファイルを選択
    2. **設定**: 
       - シリアルポートモード: ポート名とボーレートを設定
       - テストファイルモード: テストファイルのパスを指定
    3. **開始**: 「開始」ボタンをクリックしてデータ取得を開始
    4. **可視化**: 地図上に経路と現在位置が表示されます
    5. **停止**: 「停止」ボタンでデータ取得を停止
    
    ### 対応フォーマット
    
    - NMEA 0183 GPGGA形式
    - シリアルポート: /dev/ttyUSB0, COM6など
    - テストファイル: NMEA形式のテキストファイル
    """)

# 自動リフレッシュ（実行中のみ）
if st.session_state.is_running:
    time.sleep(1)
    st.rerun()
