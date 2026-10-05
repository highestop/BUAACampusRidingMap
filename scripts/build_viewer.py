#!/usr/bin/env python3
"""Embed route_network.json in a completely offline SVG network explorer."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>北京航空航天大学沙河校区线路图</title>
<style>
:root{--bg:#f3f5f8;--panel:#fff;--ink:#1b293b;--muted:#718097;--border:#e3e9f0;--blue:#1976d2;--blue-light:#eaf3fe;--red:#cf4963;--orange:#d78c44;--grid:#cdd6e0;--map:#fafcfe;--shadow:0 5px 25px rgba(41,69,99,.04);--raw:#a8b4c4;--purple:#7c4dcc;--land:#f2f1e9;--park:#dfe9d5;--forest:#d4e2c9;--water:#cbdfea;--building:#e7e2d9;--building-edge:#d7d0c6;--road:#fdfcf9;--road-edge:#d7d8d2;--path:#aaa99a;--map-label:#697364;--pitch:#d3e3d4;--landuse:#eae8e2;--planned:#aaa99f}
@media(prefers-color-scheme:dark){:root{--bg:#101722;--panel:#182331;--ink:#e3ebf5;--muted:#91a1b5;--border:#2a3a4d;--blue:#65b3ff;--blue-light:#1c3550;--red:#ff8096;--orange:#eda663;--grid:#344358;--map:#131d2a;--shadow:none;--raw:#637488;--purple:#bd9dff;--land:#202a2c;--park:#293c31;--forest:#233b2c;--water:#273e50;--building:#39403e;--building-edge:#474d48;--road:#405058;--road-edge:#29373c;--path:#67776b;--map-label:#acb8aa;--pitch:#34483d;--landuse:#2c3234;--planned:#7c8582}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;font-size:14px;line-height:1.55}button,select,input{font:inherit}button,select{color:var(--ink);background:var(--panel);border:1px solid var(--border);border-radius:9px}button{cursor:pointer;padding:8px 12px;white-space:nowrap}button:hover{border-color:var(--blue);color:var(--blue)}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid var(--blue);outline-offset:3px}.shell{max-width:1520px;margin:0 auto;padding:28px 32px 22px}.eyebrow{color:var(--blue);font-size:11px;letter-spacing:2.2px;font-weight:750;margin:0 0 9px}.masthead{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:26px;margin-bottom:25px}.masthead>div:first-child{min-width:0}h1{font-size:30px;font-weight:730;letter-spacing:-.7px;line-height:1.35;word-break:keep-all;overflow-wrap:anywhere;margin:0 0 5px}.intro{margin:0;color:var(--muted);font-size:13px}.summary{display:flex;gap:30px;flex-shrink:0}.stat{padding-left:23px;border-left:1px solid var(--border)}.stat strong{display:block;font-size:28px;font-weight:700;line-height:1.25;font-variant-numeric:tabular-nums;letter-spacing:-1px}.stat span{display:block;font-size:11px;color:var(--muted);margin-top:5px}.stat small{font-size:13px;font-weight:550;letter-spacing:0;margin-left:3px}.layout{display:grid;grid-template-columns:minmax(0,1fr) 310px;gap:18px;align-items:stretch}.card{background:var(--panel);border:1px solid var(--border);border-radius:16px;box-shadow:var(--shadow);overflow:hidden}.map-card{display:flex;flex-direction:column;min-width:0}.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:12px;padding:14px 18px;border-bottom:1px solid var(--border);min-height:64px}.toolbar-title{font-size:12px;font-weight:700;margin-right:auto;display:flex;align-items:center;gap:7px}.live-dot{width:6px;height:6px;border-radius:50%;background:var(--blue)}.toggles{display:flex;flex-wrap:wrap;gap:13px}.toggle{font-size:11px;color:var(--muted);cursor:pointer;display:flex;align-items:center;gap:5px;white-space:nowrap}.toggle input{accent-color:var(--blue);margin:0;width:13px;height:13px}.canvas{height:clamp(480px,68vh,780px);min-height:460px;position:relative;background:var(--map);background-image:radial-gradient(var(--grid) .6px,transparent .6px);background-size:20px 20px;overflow:hidden}.canvas svg{display:block;width:100%;height:100%;touch-action:none;cursor:grab;outline:none}.canvas svg.panning{cursor:grabbing}.basemap{pointer-events:none}.basemap path{stroke-linejoin:round;stroke-linecap:round}.base-area{stroke-width:.7;vector-effect:non-scaling-stroke}.base-label{fill:var(--map-label);font-weight:500;text-anchor:middle;dominant-baseline:middle;paint-order:stroke;stroke:var(--land);stroke-linejoin:round}.base-label.park,.base-label.forest{font-weight:650}.map-attribution{position:absolute;right:14px;bottom:4px;font-size:9px;line-height:1.4;color:var(--muted);background:var(--panel);padding:1px 4px;border-radius:3px}.map-attribution a{color:inherit;text-decoration:none}.map-attribution a:hover{text-decoration:underline}.map-controls{margin-bottom:13px}.raw-path{fill:none;stroke:var(--raw);stroke-width:1;opacity:.5;pointer-events:none;vector-effect:non-scaling-stroke}.removed-path{fill:none;stroke:var(--orange);stroke-width:2;stroke-dasharray:5 5;opacity:.85;vector-effect:non-scaling-stroke;pointer-events:none}.seg-path{fill:none;stroke:var(--blue);stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke;pointer-events:none}.seg-group.inferred .seg-path{stroke:var(--purple);stroke-dasharray:7 5}.seg-hit{fill:none;stroke:transparent;stroke-width:15;vector-effect:non-scaling-stroke;cursor:pointer;pointer-events:stroke}.seg-group:hover .seg-path{stroke:var(--purple);stroke-width:4}.seg-group.selected .seg-path{stroke:var(--purple);stroke-width:5}.seg-group.confirmed:hover .seg-path,.seg-group.confirmed.selected .seg-path{stroke:var(--blue)}.point-dot{fill:var(--red);stroke:var(--panel);stroke-width:1.7;vector-effect:non-scaling-stroke;pointer-events:none}.point-hit{fill:transparent;cursor:pointer}.point-group:hover .point-dot,.point-group.selected .point-dot{fill:var(--purple);stroke:var(--purple);stroke-width:3}.point-label{font-weight:680;fill:var(--ink);paint-order:stroke;stroke:var(--map);stroke-width:3px;stroke-linejoin:round;vector-effect:non-scaling-stroke;pointer-events:none}.label-selected{fill:var(--purple)}.map-controls{position:absolute;right:16px;bottom:18px;display:flex;flex-direction:column;gap:6px}.map-controls button{width:36px;height:36px;padding:0;background:var(--panel);font-size:21px;box-shadow:var(--shadow)}.map-controls .home{font-size:17px}.north{position:absolute;right:20px;top:16px;color:var(--muted);font-size:10px;text-align:center;pointer-events:none}.north .arrow{width:0;height:0;border-left:4px solid transparent;border-right:4px solid transparent;border-bottom:14px solid var(--muted);margin:4px auto}.scale{position:absolute;left:20px;bottom:19px;color:var(--muted);font-size:10px;pointer-events:none;font-variant-numeric:tabular-nums}.scale-line{border-bottom:1.5px solid var(--muted);border-left:1.5px solid var(--muted);border-right:1.5px solid var(--muted);height:5px;margin-top:4px}.map-footer{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:11px 18px;color:var(--muted);font-size:10px;border-top:1px solid var(--border)}.side{display:flex;flex-direction:column;gap:16px;min-width:0}.side .card{padding:20px}.section-label{font-size:10px;color:var(--muted);letter-spacing:1.8px;text-transform:uppercase;margin:0 0 12px;font-weight:700}.select-wrap{display:grid;gap:9px}select{width:100%;padding:10px 11px;font-size:12px;min-width:0}.detail{min-height:242px}.detail-heading{display:flex;align-items:center;justify-content:space-between;gap:9px;margin-bottom:15px}.detail-heading h2{font-size:21px;letter-spacing:-.5px;margin:0}.badge{font-size:10px;color:var(--blue);background:var(--blue-light);padding:4px 8px;border-radius:20px;white-space:nowrap}.empty-icon{display:flex;align-items:center;justify-content:center;width:42px;height:42px;background:var(--blue-light);border-radius:13px;color:var(--blue);font-size:22px;margin:10px 0 14px}.empty-title{font-size:15px;font-weight:650;margin:0 0 6px}.empty-text{font-size:12px;color:var(--muted);margin:0}.rows{margin:0}.row{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-bottom:1px solid var(--border);font-size:12px}.row:last-child{border-bottom:0}.row dt{color:var(--muted);flex-shrink:0}.row dd{margin:0;text-align:right;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}.connections{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}.chip{font-size:10px;color:var(--blue);background:var(--blue-light);padding:5px 8px;border:0;border-radius:7px}.info-note{font-size:11px;line-height:1.7;color:var(--muted);margin:13px 0 0}.legend{display:grid;grid-template-columns:1fr 1fr;gap:11px 10px;color:var(--muted);font-size:11px}.legend-item{display:flex;align-items:center;gap:8px;white-space:nowrap}.legend-line{height:0;width:22px;flex:0 0 22px;border-top:2px solid var(--blue)}.legend-line.inferred{border-top:2px dashed var(--purple)}.legend-line.raw{border-color:var(--raw)}.legend-line.removed{border-top:2px dashed var(--orange)}.legend-dot{width:7px;height:7px;background:var(--red);border-radius:50%;margin:0 7px;flex-shrink:0}.method{font-size:11px;line-height:1.8;color:var(--muted);margin:0}.method strong{color:var(--ink);font-weight:600}.method-card{flex:1}details{margin-top:14px;border-top:1px solid var(--border);padding-top:12px}summary{font-size:11px;cursor:pointer;color:var(--muted)}.param-list{margin-top:9px}.param-list .row{font-size:10px;gap:6px}.param-list dt{white-space:normal;flex-shrink:1;max-width:65%}.download{display:block;width:100%;margin-top:14px;font-size:11px;padding:9px}.bottom{display:flex;justify-content:space-between;gap:15px;margin:16px 3px 0;color:var(--muted);font-size:10px}.bottom span:last-child{text-align:right}.sr-only{position:absolute;width:1px;height:1px;margin:-1px;overflow:hidden;clip:rect(0,0,0,0)}
@media(min-width:1650px){.canvas{height:710px}}
@media(max-width:1050px){.shell{padding:24px 22px}.summary{gap:20px}.stat{padding-left:16px}.stat strong{font-size:24px}.layout{grid-template-columns:minmax(0,1fr) 280px;gap:14px}.side .card{padding:17px}.toolbar-title{display:none}.toolbar{padding:13px 15px}.toggles{gap:11px}}
@media(max-width:760px){.shell{padding:22px 14px 18px}.masthead{align-items:flex-start;flex-direction:column;gap:22px;margin-bottom:19px}h1{font-size:27px}.summary{width:100%;gap:0}.stat{width:33.333%;padding-left:17px}.stat:first-child{padding-left:0;border-left:0}.stat strong{font-size:26px}.layout{grid-template-columns:1fr}.canvas{height:56vh;min-height:420px}.side{display:grid;grid-template-columns:1fr 1fr;gap:12px}.select-card,.detail{grid-column:1/-1}.detail{min-height:180px}.side .card{padding:17px}.method-card{grid-column:1/-1}.legend-card{grid-column:1/-1}.legend{display:flex;flex-wrap:wrap;gap:13px 18px}.bottom{flex-direction:column;gap:4px}.bottom span:last-child{text-align:left}.toolbar-title{display:flex}.toolbar{gap:8px}.toggles{gap:12px}.map-footer{font-size:9px}.intro{max-width:35em}.select-wrap{grid-template-columns:1fr 1fr}}
@media(max-width:390px){.toolbar-title{display:none}.toggles{width:100%;justify-content:space-between}.select-wrap{grid-template-columns:1fr}.summary .stat strong{font-size:23px}.map-footer span:last-child{display:none}}
@media(prefers-reduced-motion:no-preference){button{transition:color .15s,border-color .15s}.seg-path{transition:stroke .12s,stroke-width .12s}}
</style>
</head>
<body>
<div class="shell">
<header class="masthead">
<div><p class="eyebrow">BUAA SHAHE / CAMPUS MAP</p><h1>北京航空航天大学<wbr>沙河校区线路图</h1><p class="intro">查看沙河校区道路、交叉点与路段距离。</p></div>
<div class="summary" aria-label="网络汇总"><div class="stat"><strong id="pointCount">—</strong><span>有效 POINT</span></div><div class="stat"><strong id="segmentCount">—</strong><span>无向 SEGMENT</span></div><div class="stat"><strong id="networkLength">—</strong><span id="networkLengthNote">去重后的路线总长</span></div></div>
</header>
<main class="layout">
<section class="card map-card" aria-label="交互网络图">
<div class="toolbar"><span class="toolbar-title"><span class="live-dot"></span> 路线全览</span><div class="toggles"><label class="toggle"><input id="showBasemap" type="checkbox" checked>实际地图</label><label class="toggle"><input id="showRaw" type="checkbox">原始轨迹</label><label class="toggle"><input id="showRemoved" type="checkbox" checked>无效死路</label><label class="toggle"><input id="showLabels" type="checkbox" checked>节点标注</label></div></div>
<div class="canvas" id="canvas"><svg id="network" aria-label="可缩放拖动的校区道路网络；也可使用右侧下拉列表查看每个路段和节点" role="img" tabindex="0"><g id="basemapLayer" class="basemap"></g><g id="rawLayer"></g><g id="removedLayer"></g><g id="segmentLayer"></g><g id="pointLayer"></g></svg><div class="north">N<div class="arrow"></div></div><div class="scale"><span id="scaleText">100 m</span><div class="scale-line" id="scaleLine"></div></div><div class="map-controls"><button id="zoomIn" aria-label="放大" title="放大">+</button><button id="zoomOut" aria-label="缩小" title="缩小">−</button><button id="resetView" class="home" aria-label="恢复全览" title="恢复全览">⌂</button></div><div class="map-attribution" id="mapAttribution"><a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">© OpenStreetMap contributors</a></div></div>
<div class="map-footer"><span>点击查看详情 · Esc 取消选中 · 拖动平移（限底图范围）· 滚轮缩放</span><span>本地米制投影 / 北向上</span></div>
</section>
<aside class="side">
<section class="card select-card"><p class="section-label">QUICK FIND / 快速定位</p><div class="select-wrap"><select id="pointSelect" aria-label="选择一个节点"><option value="">选择 Point…</option></select><select id="segmentSelect" aria-label="选择一个路段"><option value="">选择 Segment…</option></select></div></section>
<section class="card detail" id="detail" aria-live="polite"><p class="section-label">INSPECT / 查看详情</p><div class="empty-icon" aria-hidden="true">⌖</div><p class="empty-title">从一段路线开始</p><p class="empty-text">点击图上的蓝色路线或红色节点，查看坐标、路线距离和连接关系。</p></section>
<section class="card legend-card"><p class="section-label">LAYERS / 图层</p><div class="legend"><div class="legend-item"><span class="legend-line"></span>有效路段</div><div class="legend-item"><span class="legend-dot"></span>连接节点</div><div class="legend-item"><span class="legend-line raw"></span>原始轨迹</div><div class="legend-item"><span class="legend-line removed"></span>已剔除死路</div><div class="legend-item" id="inferredLegend" hidden><span class="legend-line inferred"></span>推测补线</div></div></section>
<section class="card method-card"><p class="section-label">READING THE GRAPH / 读图说明</p><p class="method">每段路线<strong>不区分行进方向</strong>。距离沿合并后的路线折线逐段累计，不是两个端点的直线距离。<br><br>相近轨迹与节点已合并；死路按连接关系迭代剔除。路线总长按每个 Segment 只计算一次，表示当前道路网络的总长度。</p><p class="info-note" id="inferredNote" hidden></p><p class="info-note" id="basemapNote"></p><details><summary>查看处理参数</summary><dl class="param-list" id="parameterList"></dl></details><button id="downloadData" class="download">↓ 下载完整网络 JSON</button></section>
</aside>
</main>
<footer class="bottom"><span>北京航空航天大学沙河校区 · 离线线路图</span><span>按实际道路整理 · 距离沿路线累计</span></footer>
</div>
<script id="networkData" type="application/json">__DATA__</script>
<script id="basemapData" type="application/json">__BASEMAP__</script>
<script>
'use strict';
const data = JSON.parse(document.getElementById('networkData').textContent);
const points = data.points || [], segments = data.segments || [], removed = data.removed_dead_ends || [];
const inferredCount = segments.filter(s=>s.is_inferred===true&&!s.connection_confirmed).length;
const estimatedCount = segments.filter(s=>s.length_is_estimate===true).length;
const correctedCount = segments.filter(s=>s.is_user_corrected===true).length;
const confirmedCount = segments.filter(s=>s.connection_confirmed===true&&s.connection_source==='user').length;
const basemap = JSON.parse(document.getElementById('basemapData').textContent);
const pointById = new Map(points.map(p=>[String(p.id),p])), segmentById = new Map(segments.map(s=>[String(s.id),s]));
const $=id=>document.getElementById(id), svg=$('network'), NS='http://www.w3.org/2000/svg';
const nf=new Intl.NumberFormat('zh-CN',{maximumFractionDigits:1});
const dist=n=>n>=1000?`${(n/1000).toFixed(2)} km`:`${nf.format(n)} m`;
const scalar=x=>typeof x==='number'?nf.format(x):typeof x==='object'?JSON.stringify(x):String(x);
const summary=data.metadata?.summary||{};
$('pointCount').textContent=points.length;
$('segmentCount').textContent=segments.length;
$('inferredLegend').style.display=inferredCount?'flex':'none';
if(estimatedCount){$('networkLengthNote').textContent=`路线总长 · 含 ${estimatedCount} 条估算段`;$('inferredNote').hidden=false;$('inferredNote').textContent=[correctedCount?`${correctedCount} 条路段已按地图校正，蓝色实线表示有效路线，距离沿校正后的曲线估算。`:'',confirmedCount?`${confirmedCount} 条补充路段由用户确认可通行，采用蓝色实线；形状与距离为估计。`:'',inferredCount?`${inferredCount} 条紫色虚线为未确认的推测补线，无原始轨迹支撑。`:'','底图缺少对应道路的部分保留轨迹形状；总长包含估计距离。'].join('');}
$('networkLength').append(document.createTextNode(((summary.total_network_length_m??segments.reduce((a,s)=>a+s.length_m,0))/1000).toFixed(2)));
$('networkLength').firstChild.remove();
const unit=document.createElement('small');unit.textContent='km';$('networkLength').append(unit);
function el(tag,attrs={},parent){const n=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(parent)parent.append(n);return n}
function pathOf(a){return (a||[]).map((p,i)=>`${i?'L':'M'}${p[0]},${-p[1]}`).join(' ')}
const mapLabels=[];
function renderBasemap(){
 const layer=$('basemapLayer'),features=basemap.features||[],b=basemap.bounds_xy;
 const available=features.length>0&&Array.isArray(b)&&b.length===4;
 $('showBasemap').disabled=!available;$('showBasemap').checked=available;$('mapAttribution').hidden=!available;
 $('basemapNote').textContent=available?'底图为 OpenStreetMap 真实地理要素，已内嵌离线使用；仅覆盖校园及周边有限范围，范围以外不显示底图。':'本文件未包含底图，当前仅显示路线网络。';
 if(!available)return;
 el('rect',{x:b[0],y:-b[3],width:b[2]-b[0],height:b[3]-b[1],fill:'var(--land)'},layer);
 const areas=el('g',{},layer),roads=el('g',{},layer),labels=el('g',{},layer);
 const areaPriority={landuse:0,park:1,forest:2,pitch:3,water:4,building:5};
 [...features].filter(f=>f.type==='area').sort((a,b)=>(areaPriority[a.kind]??1)-(areaPriority[b.kind]??1)).forEach(f=>{
  const parts=f.parts_xy?.length?f.parts_xy:[{outer:f.geometry_xy||[],holes:[]}];
  const fill=['park','forest','water','building','pitch','landuse'].includes(f.kind)?`var(--${f.kind})`:'var(--landuse)';
  parts.forEach(part=>{if((part.outer||[]).length<3)return;const d=[part.outer,...(part.holes||[])].filter(r=>r.length>=3).map(r=>pathOf(r)+' Z').join(' ');el('path',{d,class:'base-area',fill,'fill-rule':'evenodd',stroke:f.kind==='building'?'var(--building-edge)':'none'},areas)});
 });
 features.filter(f=>f.type==='line').forEach(f=>{
  const parts=f.line_parts_xy?.length?f.line_parts_xy:[f.geometry_xy||[]];const d=parts.filter(a=>a.length>=2).map(pathOf).join(' ');if(!d)return;
  if(f.kind==='road'){
   const major=['motorway','trunk','primary','secondary','tertiary'].includes(f.tags?.highway),w=major?7:4;
   el('path',{d,fill:'none',stroke:'var(--road-edge)','stroke-width':w+1.5,'vector-effect':'non-scaling-stroke'},roads);
   el('path',{d,fill:'none',stroke:'var(--road)','stroke-width':w,'vector-effect':'non-scaling-stroke'},roads);
  }else if(f.kind==='planned')el('path',{d,fill:'none',stroke:'var(--planned)','stroke-width':1.2,'stroke-dasharray':'5 4','vector-effect':'non-scaling-stroke'},roads);
  else if(f.kind==='water')el('path',{d,fill:'none',stroke:'var(--water)','stroke-width':3,'vector-effect':'non-scaling-stroke'},roads);
  else el('path',{d,fill:'none',stroke:'var(--path)','stroke-width':f.kind==='railway'?1.5:1,'stroke-dasharray':f.kind==='railway'?'5 3':'2 3','vector-effect':'non-scaling-stroke'},roads);
 });
 const names=[];
 [...features].filter(f=>f.name).sort((a,b)=>((a.kind==='park'||a.kind==='water'||a.kind==='label')?0:1)-((b.kind==='park'||b.kind==='water'||b.kind==='label')?0:1)).forEach(f=>{
  const a=f.geometry_xy||[];let pos=f.label_xy;
  if(!pos&&a.length)pos=f.type==='point'?a[0]:f.type==='line'?a[Math.floor(a.length/2)]:[a.reduce((n,p)=>n+p[0],0)/a.length,a.reduce((n,p)=>n+p[1],0)/a.length];
  if(!pos||!pos.every(Number.isFinite))return;
  if(names.some(n=>n.name===f.name&&Math.hypot(n.pos[0]-pos[0],n.pos[1]-pos[1])<250))return;
  names.push({name:f.name,pos});
  const n=el('text',{x:pos[0],y:-pos[1],class:`base-label ${f.kind==='park'||f.kind==='forest'?f.kind:''}`},labels);n.textContent=f.name;
  mapLabels.push({node:n,x:pos[0],y:-pos[1],name:f.name,size:['park','forest','water','label'].includes(f.kind)?11:10});
 });
}
function placeMapLabels(u){const showPointLabels=$('showLabels').checked;const occupied=points.map(p=>{const x=(p.x_m-view.x)/u,y=(-p.y_m-view.y)/u;return showPointLabels?{x:x-6,y:y-19,w:47,h:26}:{x:x-6,y:y-6,w:12,h:12}}).filter(b=>b.x+b.w>0&&b.y+b.h>0&&b.x<svg.clientWidth&&b.y<svg.clientHeight);mapLabels.forEach(l=>{const x=(l.x-view.x)/u,y=(l.y-view.y)/u,w=[...l.name].reduce((v,c)=>v+(c.charCodeAt(0)>255?1:.55),0)*l.size+10,h=l.size+8;const box={x:x-w/2,y:y-h/2,w,h};const visible=box.x>=0&&box.y>=0&&box.x+w<=svg.clientWidth&&box.y+h<=svg.clientHeight&&!occupied.some(b=>box.x<b.x+b.w&&box.x+w>b.x&&box.y<b.y+b.h&&box.y+h>b.y);l.node.style.display=visible?'':'none';if(visible){occupied.push(box);l.node.setAttribute('font-size',l.size*u);l.node.setAttribute('stroke-width',2.4*u)}})}
renderBasemap();
const raw=data.raw_track?.geometry_xy||[];
if(raw.length)el('path',{d:pathOf(raw),class:'raw-path'},$('rawLayer'));
removed.forEach(s=>el('path',{d:pathOf(s.geometry_xy),class:'removed-path'},$('removedLayer')));
segments.forEach(s=>{const g=el('g',{class:'seg-group'+(s.is_inferred&&!s.connection_confirmed?' inferred':'')+(s.connection_confirmed?' confirmed':''),'data-kind':'segment','data-id':s.id},$('segmentLayer'));el('path',{d:pathOf(s.geometry_xy),class:'seg-path'},g);el('path',{d:pathOf(s.geometry_xy),class:'seg-hit'},g);el('title',{},g).textContent=`${s.id} · ${s.point_a} ↔ ${s.point_b} · ${s.length_is_estimate?'估计距离 ':''}${dist(s.length_m)}${s.is_user_corrected?' · 按地图校正 · 路线长度为地图估算':s.connection_confirmed?' · 补充路段 · 用户确认可通行 · 形状与距离为估计':s.is_inferred?' · 推测连接 · 无原始轨迹支撑':''}`;});
points.forEach(p=>{const g=el('g',{class:'point-group','data-kind':'point','data-id':p.id},$('pointLayer'));el('circle',{cx:p.x_m,cy:-p.y_m,class:'point-dot'},g);el('circle',{cx:p.x_m,cy:-p.y_m,class:'point-hit'},g);el('text',{x:p.x_m,y:-p.y_m,class:'point-label'},g).textContent=p.id;el('title',{},g).textContent=`${p.id} · ${p.degree} 段相连`;});
points.forEach(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=`${p.id} · ${p.degree} 段连接`;$('pointSelect').append(o)});
segments.forEach(s=>{const o=document.createElement('option');o.value=s.id;o.textContent=`${s.id} · ${s.length_is_estimate?'约 ':''}${dist(s.length_m)}${s.is_user_corrected?'':s.connection_confirmed?' · 补充':s.is_inferred?' · 推测':''}`;$('segmentSelect').append(o)});
const parameters=data.metadata?.parameters||{};
const paramNames={corridor_radius_m:'轨迹走廊半径',merge_tolerance_m:'轨迹合并容差',junction_merge_radius_m:'节点合并半径',grid_resolution_m:'栅格分辨率',smoothing_sigma_m:'平滑尺度',distance_method:'距离计算方法',projection:'坐标投影',dead_end_pruning:'死路剔除方式',direction:'方向处理',track_merge_radius_m:'轨迹合并半径',node_merge_radius_m:'节点合并半径'};
Object.entries(parameters).forEach(([k,v])=>addRow($('parameterList'),paramNames[k]||k,scalar(v)+(k.endsWith('_m')?' m':'')));
if(!Object.keys(parameters).length)addRow($('parameterList'),'参数','请参阅完整 JSON');
let all=segments.flatMap(s=>s.geometry_xy||[]).concat(raw);
if(!all.length)all=points.map(p=>[p.x_m,p.y_m]);
if(!all.length)all=[[0,0],[100,100]];
const xs=all.map(p=>p[0]),ys=all.map(p=>-p[1]);
const bounds={x:Math.min(...xs),y:Math.min(...ys),w:Math.max(...xs)-Math.min(...xs),h:Math.max(...ys)-Math.min(...ys)};
const mapBox=basemap.bounds_xy;
const navigationBounds=Array.isArray(mapBox)&&mapBox.length===4&&mapBox.every(Number.isFinite)&&mapBox[2]>mapBox[0]&&mapBox[3]>mapBox[1]
 ?{x:mapBox[0],y:-mapBox[3],w:mapBox[2]-mapBox[0],h:mapBox[3]-mapBox[1]}:bounds;
function clampViewport(v,b,pixelWidth,pixelHeight){
 const ratio=Math.max(1,pixelWidth)/Math.max(1,pixelHeight);
 const maxW=Math.min(b.w,b.h*ratio),minW=Math.min(10,maxW);
 const w=Math.max(minW,Math.min(v.w,maxW)),h=w/ratio;
 const cx=v.x+v.w/2,cy=v.y+v.h/2;
 return{x:Math.max(b.x,Math.min(cx-w/2,b.x+b.w-w)),y:Math.max(b.y,Math.min(cy-h/2,b.y+b.h-h)),w,h};
}
function constrainView(v){return clampViewport(v,navigationBounds,svg.clientWidth,svg.clientHeight)}
let view={x:0,y:0,w:100,h:100},initialView,selected=null,drag=null;
const emptyDetail=$('detail').cloneNode(true);
let escapeHandled=false;
function clearSelection(){
 if(!selected)return;
 selected=null;
 document.querySelectorAll('.selected').forEach(n=>n.classList.remove('selected'));
 $('pointSelect').value='';$('segmentSelect').value='';
 const panel=$('detail'),restoreFocus=panel.contains(document.activeElement);
 panel.replaceChildren(...Array.from(emptyDetail.childNodes,n=>n.cloneNode(true)));
 if(restoreFocus)svg.focus({preventScroll:true});
}
window.addEventListener('keydown',e=>{
 if(e.key!=='Escape'||(!selected&&!escapeHandled))return;
 e.preventDefault();e.stopImmediatePropagation();
 escapeHandled=true;clearSelection();
},{capture:true});
window.addEventListener('keyup',e=>{
 if(e.key!=='Escape'||!escapeHandled)return;
 e.preventDefault();e.stopImmediatePropagation();escapeHandled=false;
},{capture:true});
window.addEventListener('blur',()=>{escapeHandled=false});
function fitBounds(b,padding=.14){const ratio=svg.clientWidth/Math.max(1,svg.clientHeight);let w=Math.max(b.w,20)*(1+padding*2),h=Math.max(b.h,20)*(1+padding*2);if(w/h<ratio)w=h*ratio;else h=w/ratio;return{x:b.x+b.w/2-w/2,y:b.y+b.h/2-h/2,w,h}}
function renderView(){view=constrainView(view);svg.setAttribute('viewBox',`${view.x} ${view.y} ${view.w} ${view.h}`);const u=view.w/Math.max(1,svg.clientWidth);placeMapLabels(u);document.querySelectorAll('.point-dot').forEach(n=>n.setAttribute('r',3.6*u));document.querySelectorAll('.point-hit').forEach(n=>n.setAttribute('r',10*u));document.querySelectorAll('.point-label').forEach(n=>{n.setAttribute('font-size',10*u);n.setAttribute('dx',7*u);n.setAttribute('dy',-7*u);n.setAttribute('stroke-width',3*u)});const ideal=u*85,pow=10**Math.floor(Math.log10(ideal)),length=[1,2,5,10].map(n=>n*pow).filter(n=>n<=ideal).pop()||pow;$('scaleText').textContent=dist(length);$('scaleLine').style.width=`${length/u}px`;}
function reset(){initialView=constrainView(fitBounds(bounds));view={...initialView};renderView()}
function zoom(f,x=svg.clientWidth/2,y=svg.clientHeight/2){
 const ratio=Math.max(1,svg.clientWidth)/Math.max(1,svg.clientHeight),maxW=Math.min(navigationBounds.w,navigationBounds.h*ratio);
 const nextW=Math.max(Math.min(10,maxW),Math.min(view.w*f,maxW));f=nextW/view.w;
 if(Math.abs(f-1)<1e-12)return;
 const px=x/Math.max(1,svg.clientWidth),py=y/Math.max(1,svg.clientHeight);
 view={x:view.x+view.w*px*(1-f),y:view.y+view.h*py*(1-f),w:nextW,h:view.h*f};renderView();
}
function focusObject(kind,id){const obj=kind==='point'?pointById.get(id):segmentById.get(id);if(!obj)return;if(kind==='segment'){const a=obj.geometry_xy;const xs=a.map(p=>p[0]),ys=a.map(p=>-p[1]);const b={x:Math.min(...xs),y:Math.min(...ys),w:Math.max(...xs)-Math.min(...xs),h:Math.max(...ys)-Math.min(...ys)};view=fitBounds(b,.35);if(view.w<initialView.w*.2){const w=initialView.w*.2,h=w*svg.clientHeight/svg.clientWidth;view={x:b.x+b.w/2-w/2,y:b.y+b.h/2-h/2,w,h}}if(view.w>initialView.w)view={...initialView};}else{const width=Math.min(view.w,initialView.w*.4),height=width*svg.clientHeight/svg.clientWidth;view={x:obj.x_m-width/2,y:-obj.y_m-height/2,w:width,h:height}}renderView()}
function addRow(dl,key,value){const r=document.createElement('div');r.className='row';const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=key;dd.textContent=value;r.append(dt,dd);dl.append(r)}
function select(kind,id,focus=false){const obj=kind==='point'?pointById.get(id):segmentById.get(id);if(!obj)return;selected={kind,id};document.querySelectorAll('.selected').forEach(n=>n.classList.remove('selected'));document.querySelectorAll('[data-kind]').forEach(n=>{if(n.dataset.kind===kind&&n.dataset.id===id)n.classList.add('selected')});$('pointSelect').value=kind==='point'?id:'';$('segmentSelect').value=kind==='segment'?id:'';const panel=$('detail');panel.replaceChildren();const kicker=document.createElement('p');kicker.className='section-label';kicker.textContent='INSPECT / 查看详情';panel.append(kicker);const heading=document.createElement('div');heading.className='detail-heading';const h=document.createElement('h2');h.textContent=id;const badge=document.createElement('span');badge.className='badge';badge.textContent=kind==='point'?'POINT · 节点':obj.is_user_corrected?'SEGMENT · 地图校正':obj.connection_confirmed?'SEGMENT · 补充路段':obj.is_inferred?'SEGMENT · 推测补线':'SEGMENT · 无向路段';heading.append(h,badge);panel.append(heading);const dl=document.createElement('dl');dl.className='rows';panel.append(dl);let connections=[];
if(kind==='segment'){addRow(dl,'端点 A',obj.point_a);addRow(dl,'端点 B',obj.point_b);addRow(dl,obj.is_user_corrected?'路线长度（地图估算）':obj.length_is_estimate?'估计距离':'路线距离',`${obj.length_is_estimate?'约 ':''}${nf.format(obj.length_m)} m`);if(obj.is_user_corrected){if(obj.junction_straightening)addRow(dl,'路口接入','端部已局部拉直');if(obj.map_alignment?.status==='no_corresponding_mapped_road')addRow(dl,'贴合状态','底图缺路，保留轨迹');else if(obj.map_alignment?.status==='partial')addRow(dl,'贴合状态','已贴合可匹配部分');}addRow(dl,'坐标点数',obj.coordinate_count??obj.coordinates?.length??obj.geometry_xy?.length??0);connections=[obj.point_a,obj.point_b].map(x=>({kind:'point',id:String(x)}));}else{addRow(dl,'经度',Number(obj.longitude).toFixed(7));addRow(dl,'纬度',Number(obj.latitude).toFixed(7));addRow(dl,'连接度',`${obj.degree} 段`);if(obj.is_user_corrected)addRow(dl,'位置来源','按地图校正');if(obj.kind)addRow(dl,'节点类型',({junction:'交叉点',cycle_anchor:'闭环辅助点',loop_anchor:'闭环辅助点',shape_anchor:'闭环辅助点',intersection:'交叉点',artificial_cycle_anchor:'闭环辅助点'})[obj.kind]||obj.kind);connections=(obj.segment_ids||[]).map(x=>({kind:'segment',id:String(x)}));}
const chips=document.createElement('div');chips.className='connections';connections.forEach(c=>{const button=document.createElement('button');button.className='chip';button.textContent=`↗ ${c.id}`;button.addEventListener('click',()=>select(c.kind,c.id));chips.append(button)});panel.append(chips);const note=document.createElement('p');note.className='info-note';note.textContent=kind==='segment'?(obj.is_user_corrected?'按地图校正形状与交叉连接，距离为沿线估算；原始GPS保留供对照。':obj.connection_confirmed?'用户确认此路段可通行。图中形状与距离为估计，尚无完整实测轨迹支撑。':obj.is_inferred?'推测连接 · 无原始轨迹支撑。此线的形状和距离为估计值，需实际轨迹核实。':'折线保留路线的弯曲形状；点击端点可查看其相连路段。'):'坐标为 WGS84 经纬度；点击相连路段可查看路线距离。';panel.append(note);if(focus)focusObject(kind,id)}
$('pointSelect').addEventListener('change',e=>{if(e.target.value)select('point',e.target.value,true)});$('segmentSelect').addEventListener('change',e=>{if(e.target.value)select('segment',e.target.value,true)});
svg.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={x:e.clientX,y:e.clientY,view:{...view},moved:false,target:e.target.closest('[data-kind]')};svg.setPointerCapture(e.pointerId);svg.classList.add('panning')});
svg.addEventListener('pointermove',e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.hypot(dx,dy)>4)drag.moved=true;if(drag.moved){view.x=drag.view.x-dx*drag.view.w/svg.clientWidth;view.y=drag.view.y-dy*drag.view.h/svg.clientHeight;renderView();drag.x=e.clientX;drag.y=e.clientY;drag.view={...view}}});
svg.addEventListener('pointerup',e=>{if(!drag)return;if(!drag.moved&&drag.target)select(drag.target.dataset.kind,drag.target.dataset.id);drag=null;svg.classList.remove('panning');if(svg.hasPointerCapture(e.pointerId))svg.releasePointerCapture(e.pointerId)});
svg.addEventListener('pointercancel',()=>{drag=null;svg.classList.remove('panning')});
svg.addEventListener('wheel',e=>{e.preventDefault();const r=svg.getBoundingClientRect();zoom(Math.exp(Math.max(-.3,Math.min(.3,e.deltaY*.0015))),e.clientX-r.left,e.clientY-r.top)},{passive:false});
svg.addEventListener('keydown',e=>{if(['+','=','-','0','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key))e.preventDefault();if(e.key==='+'||e.key==='=')zoom(.8);if(e.key==='-')zoom(1.25);if(e.key==='0')reset();const d=view.w*.08;if(e.key==='ArrowUp')view.y-=d;if(e.key==='ArrowDown')view.y+=d;if(e.key==='ArrowLeft')view.x-=d;if(e.key==='ArrowRight')view.x+=d;renderView()});
$('zoomIn').onclick=()=>zoom(.75);$('zoomOut').onclick=()=>zoom(1/.75);$('resetView').onclick=reset;
$('showBasemap').onchange=e=>{$('basemapLayer').style.display=e.target.checked?'':'none';$('mapAttribution').hidden=!e.target.checked};
$('showRaw').onchange=e=>$('rawLayer').style.display=e.target.checked?'':'none';$('showRemoved').onchange=e=>$('removedLayer').style.display=e.target.checked?'':'none';$('showLabels').onchange=e=>{document.querySelectorAll('.point-label').forEach(n=>n.style.display=e.target.checked?'':'none');renderView()};
$('downloadData').onclick=()=>{const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='route_network.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
new ResizeObserver(()=>{if(!initialView){reset();return}const centerX=view.x+view.w/2,centerY=view.y+view.h/2;initialView=constrainView(fitBounds(bounds));view.h=view.w*svg.clientHeight/svg.clientWidth;view.x=centerX-view.w/2;view.y=centerY-view.h/2;renderView()}).observe(svg);
$('rawLayer').style.display=$('showRaw').checked?'':'none';
reset();
const initialId=location.hash.slice(1);
if(segmentById.has(initialId))select('segment',initialId,true);
else if(pointById.has(initialId))select('point',initialId,true);
window.routeNetworkViewer={data,select,reset,getView:()=>({...view})};
</script>
</body>
</html>'''

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=ROOT/'route_network.json')
    parser.add_argument('--output',type=Path,default=ROOT/'route_network.html')
    parser.add_argument('--basemap',type=Path,default=ROOT/'map_basemap.json')
    args=parser.parse_args()
    data=json.loads(args.input.read_text())
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    basemap=json.loads(args.basemap.read_text()) if args.basemap.exists() else {'features':[]}
    basemap_encoded=json.dumps(basemap,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    html=TEMPLATE.replace('__DATA__',encoded).replace('__BASEMAP__',basemap_encoded)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(html,encoding='utf-8')
    print(f'Created {args.output} ({args.output.stat().st_size:,} bytes)')

if __name__=='__main__':main()
