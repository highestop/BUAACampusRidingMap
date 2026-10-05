# 北京航空航天大学沙河校区线路图

北航沙河校区的离线交互线路图，展示校区道路、交叉点和路段距离。目前包含 **62 个交叉点、97 条路段**，路线总长约 **11.811 千米**。

## 打开地图

下载或克隆仓库，在浏览器中打开 [`route_network.html`](route_network.html)。页面已内嵌地图与数据，无需安装依赖、启动服务或申请地图 API Key。

支持缩放、拖动、点线详情、图层开关和下载完整网络 JSON。拖动和缩放限制在已有底图范围内。GitHub 文件页展示 HTML 源码；下载后打开即可使用交互地图。

![当前网络与实际地图](network_with_map.png)

## 文件

| 文件 | 内容 |
| --- | --- |
| `route_network.html` | 完整离线交互页面 |
| `route_network.json` | 节点、路段、原始 GPS 轨迹和来源记录 |
| `route_network.geojson` | 可导入 GIS 的 Point 与 LineString |
| `points.csv` / `segments.csv` | 节点坐标、连接关系、沿线距离与折线 |
| `map_basemap.json` / `map_basemap.geojson` | 本区域离线 OpenStreetMap 底图 |
| `removed_dead_ends.geojson` | 初始提取时剔除的死路，供历史核查 |
| `validation.json` | 当前验证结果及有明确适用范围的历史审核 |
| `DATA_GUIDE.txt` | 英文数据说明：字段约定、校正记录、方法与局限 |
| `*.png` | 全网及局部校正预览 |
| `scripts/build_viewer.py` | 从当前 JSON 数据重新生成页面 |

## 数据约定

- 经纬度采用 WGS84，数组顺序为 `[经度, 纬度]`。
- 所有路段均无向；`point_a` / `point_b` 只约定折线坐标的存储顺序。
- 路段保存完整曲线。`length_m` 沿曲线逐段累计，不是两端的直线距离。
- 每个交叉点至少连接两条不同路段；同一对端点可以有多条不同路线。
- 地图校正后的长度属于估算，不是活动累计计距，也不是测绘结果。
- 手绘路线优先于自动地图匹配；底图缺路的部分保留轨迹推断，来源与状态见数据字段。

本仓库包含地理位置与活动轨迹，应按私有数据管理。原始 FIT、手绘标注截图、心率等活动消息和本地调试环境未纳入仓库；数据中的来源文件名仅作记录。

## 重新生成页面

需要 Python 3，仅使用标准库：

```sh
python3 scripts/build_viewer.py
```

脚本读取仓库根目录的 `route_network.json` 和 `map_basemap.json`，生成根目录的 `route_network.html`。它只构建页面，不会重新推断或修改路网。

## 地图来源

底图数据：© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright)，采用 [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) 许可。底图和轨迹网络分别保存；页面保留来源署名。外部版权链接由用户点击时打开，正常查看和缩放不发起网络请求。
