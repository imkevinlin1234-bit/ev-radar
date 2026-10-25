# 充電站雷達

手機用的電動車充電站地圖：即時定位、附近充電站依距離排序、顏色區分特斯拉超充／超快充／快充／慢充、路線與開車時間、站點詳細資訊。單一 HTML，不需要伺服器。

- 特斯拉超充：[supercharge.info](https://supercharge.info)（每日更新）
- 其他充電站：[OpenStreetMap](https://www.openstreetmap.org)（Overpass API）；可選填 Open Charge Map 金鑰
- 路線：OSRM 公用伺服器；底圖：OpenStreetMap
- 地圖程式庫：Leaflet 1.9.4（vendor/，BSD-2 授權）

沒有即時空位資料（公開資料沒有提供）。

## 冰島景點・超商分頁

即時定位掃描周邊景點、瀑布、自然奇景、溫泉泳池、觀景點、超市、超商、加油站，顯示距離、方向、營業中／已打烊（冰島時間）、路線、維基百科介紹。
資料是 OpenStreetMap 的冰島快照，存在 `data/iceland-poi.json`（App 內建，沒訊號也能用）。更新資料：

```
python tools/fetch_iceland.py   # 從 Overpass 下載（伺服器忙時會自動換台重試）
python tools/build_iceland.py   # 整理成 data/iceland-poi.json
```
