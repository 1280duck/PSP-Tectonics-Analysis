import pygmt
import pandas as pd

# --- 1. 設定繪圖區域與投影 ---
# 範圍：包含台灣、日本、馬里亞納 (經度 115-150, 緯度 0-40)
region = [115, 150, 0, 40] 
projection = "M15c"  # Mercator 投影

fig = pygmt.Figure()

# --- 2. 繪製地形與海洋 (Topography & Bathymetry) ---
# 使用 @earth_relief_05m 數據 (5 arc minutes 解析度，適合快速繪圖)
# 實作報告建議改用 "01m" 以獲得更高解析度
fig.grdimage(
    grid="@earth_relief_05m",
    region=region,
    projection=projection,
    cmap="geo",  # 地理配色
    shading=True # 增加立體陰影
)

# 加入海岸線與邊框
fig.coast(shorelines=True, frame=["a", '+t"Tectonic Map of the Philippine Sea Plate"'])

# --- 3. 繪製板塊邊界 (Plate Boundaries) ---
# 使用 PyGMT 內建板塊數據
# 紅色粗線表示
fig.plot(data="@plates", pen="2p,red", label="Plate Boundaries")

# --- 4. 繪製歷史著名地震 (Historical Earthquakes) ---
# 整理著名地震資料 (學術引用需標註 ISC-GEM 或 USGS 來源)
# 包含：1923 關東大地震, 1999 集集地震, 1990 呂宋地震
eq_history = pd.DataFrame({
    "lon": [139.3, 120.98, 121.35],
    "lat": [35.3, 23.85, 15.7],
    "year": ["1923 Kanto (M7.9)", "1999 Chi-Chi (M7.7)", "1990 Luzon (M7.7)"]
})

# 繪製黃色星星
fig.plot(
    x=eq_history.lon,
    y=eq_history.lat,
    style="a0.6c",
    fill="yellow",
    pen="1p,black",
    label="Major Historical EQ"
)

# 標註文字
fig.text(
    x=eq_history.lon,
    y=eq_history.lat,
    text=eq_history.year,
    font="8p,Helvetica-Bold,black",
    justify="LM",
    offset="0.4c/0c"
)

# --- 5. 獲取並繪製近期地震 (Recent Seismicity) ---
# 直接從 USGS 下載過去 30 天 M4.5+ 地震
try:
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.csv"
    df = pd.read_csv(url)
    # 篩選範圍內
    df = df[(df.longitude >= region[0]) & (df.longitude <= region[1]) & 
            (df.latitude >= region[2]) & (df.latitude <= region[3])]
    
    # 製作色標 (Colorbar) 依深度著色
    pygmt.makecpt(cmap="seis", series=[0, 600, 10], reverse=True)
    
    fig.plot(
        x=df.longitude,
        y=df.latitude,
        style="c0.15c", # 小圓點
        cmap=True,      # 使用上面設定的色標
        zvalue=df.depth,
        pen="0.1p,black"
    )
    fig.colorbar(frame='af+l"Depth (km)"', position="JMR+o1c/0c+w6c/0.5c")
except Exception as e:
    print(f"USGS Data Warning: {e}")

# --- 6. 繪製主要火山 (Volcanoes) ---
# 菲律賓海板塊周圍的代表性火山
volcanoes = pd.DataFrame({
    "lon": [138.72, 120.35, 123.68, 130.65, 140.0],
    "lat": [35.36, 15.14, 13.25, 31.59, 30.0],
    "name": ["Mt. Fuji", "Pinatubo", "Mayon", "Sakurajima", "Izu-Oshima"]
})

fig.plot(
    x=volcanoes.lon,
    y=volcanoes.lat,
    style="t0.4c", # 紅色三角形
    fill="red",
    pen="1p,black",
    label="Active Volcanoes"
)

# --- 7. 輸出圖檔 ---
# 加入比例尺 (左下角, 500km 長)
fig.basemap(map_scale="jBL+w500k+o1c/1c+f")

# 處理圖例 (手動調整位置)
fig.legend(position="JTL+o0.2c", box=True)

fig.savefig("PSP_Map.png")
print("繪圖完成：PSP_Map.png")
