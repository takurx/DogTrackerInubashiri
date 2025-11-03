# 🐕 GPS Tracker - Inubashiri

StreamlitとLeafmapを使用したリアルタイムGPSトラッカー可視化アプリケーション

## 機能

- 📍 リアルタイムGPS位置追跡
- 🗺️ インタラクティブな地図表示（Leafmap）
- 📊 経路の可視化と統計情報
- 🔌 シリアルポート入力対応（/dev/ttyUSB0、COM6など）
- 📁 テストファイルからのデータ読み込み
- 📈 移動距離、衛星数などの統計表示

## スクリーンショット

このアプリケーションは以下の機能を提供します：
- リアルタイムGPS経路表示
- 開始地点（緑マーカー）と現在位置（赤マーカー）
- 移動経路（青いライン）
- 緯度・経度・衛星数・高度の表示

## システム要件

- Python 3.8以上
- シリアルポート（実機使用時）

## インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd Inubashiri_gui_V1
```

### 2. 仮想環境の作成（推奨）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

## 使い方

### アプリケーションの起動

```bash
streamlit run app.py
```

ブラウザが自動的に開き、アプリケーションが表示されます（通常は http://localhost:8501）。

### モード選択

#### 1. テストファイルモード（デモ）

テストデータファイルからGPSデータを読み込みます。

1. サイドバーで「テストファイル」を選択
2. ファイルパスを指定（デフォルト: `test_input_data/test_input_data-0.txt`）
3. 「▶️ 開始」ボタンをクリック
4. 地図上でリアルタイムに経路が表示されます
5. 「⏸️ 停止」ボタンで停止

#### 2. シリアルポートモード（実機）

実際のGPSデバイスからシリアルポート経由でデータを取得します。

1. サイドバーで「シリアルポート」を選択
2. シリアルポート名を入力：
   - Linux: `/dev/ttyUSB0`, `/dev/ttyACM0` など
   - Windows: `COM3`, `COM6` など
3. ボーレートを設定（デフォルト: 9600）
4. 「▶️ 開始」ボタンをクリック
5. GPSデータが受信され、地図上に表示されます

### データフォーマット

このアプリケーションはNMEA 0183 GPGGA形式のGPSデータに対応しています。

```
$GPGGA,050358.00,3605.68559,N,14006.62865,E,1,06,1.31,21.2,M,39.3,M,,*61
```

各フィールドの意味：
- `050358.00`: 時刻（UTC）
- `3605.68559,N`: 緯度（度分形式）
- `14006.62865,E`: 経度（度分形式）
- `1`: GPS品質指標（0=無効, 1=GPS, 2=DGPS）
- `06`: 使用衛星数
- `1.31`: 水平精度低下率（HDOP）
- `21.2,M`: 海抜高度（メートル）

## 機能詳細

### 地図表示

- **緑マーカー**: 開始地点
- **赤マーカー**: 現在位置
- **青いライン**: 移動経路
- **ズーム/パン**: マウスで地図を操作可能

### 統計情報

- **総データポイント数**: 記録されたGPSポイントの数
- **総移動距離**: ハバーサイン公式による移動距離（メートル）
- **平均衛星数**: 受信衛星の平均数

### データ管理

- 最大1000ポイントまで自動保存
- 「🗑️ データクリア」ボタンで全データをリセット
- 詳細データテーブルで最新50件を表示

## トラブルシューティング

### シリアルポートが開けない

```
シリアルポート接続エラー: [Errno 13] Permission denied: '/dev/ttyUSB0'
```

**解決方法（Linux）**:
```bash
# ユーザーをdialoutグループに追加
sudo usermod -a -G dialout $USER
# ログアウト/ログインして再試行
```

または一時的に：
```bash
sudo chmod 666 /dev/ttyUSB0
```

### パッケージのインストールエラー

```bash
# pipを最新版にアップグレード
pip install --upgrade pip

# 個別にインストール
pip install streamlit
pip install leafmap
pip install pyserial
```

### ポートが使用中

```
Port 8501 is already in use
```

**解決方法**:
```bash
# 別のポートを指定
streamlit run app.py --server.port 8502
```

## プロジェクト構造

```
Inubashiri_gui_V1/
├── app.py                      # メインアプリケーション
├── requirements.txt            # 依存パッケージ
├── README.md                   # このファイル
└── test_input_data/
    ├── test_input_data-0.txt  # テストデータ
    └── input_cline.txt        # テストデータ
```

## 開発

### カスタマイズ

#### マーカーアイコンの変更

`app.py`の`icon_color`パラメータを変更：

```python
m.add_marker(
    location=[latitude, longitude],
    icon_color='blue'  # 'red', 'green', 'blue', 'purple', 'orange', etc.
)
```

#### 地図スタイルの変更

Leafmapは複数の地図スタイルをサポート：

```python
m = leafmap.Map(center=[lat, lon], zoom=17, basemap='OpenStreetMap')
# または 'Stamen.Terrain', 'CartoDB.Positron' など
```

#### データ保存数の変更

```python
st.session_state.gps_data = deque(maxlen=2000)  # デフォルトは1000
```

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## サポート

問題が発生した場合は、GitHubのIssuesで報告してください。

---

**Inubashiri GPS Tracker** - リアルタイムGPS追跡を簡単に 🐕
