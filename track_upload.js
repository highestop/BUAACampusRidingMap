/* Bind local track analysis to the offline viewer. */
let coverage=null,uploadGeneration=0,originalState=null,matcher=null;
const coverageLayer=el('g',{id:'coverageCountLayer','pointer-events':'none'},svg);
function refreshCoverage(){
 document.querySelectorAll('.seg-group').forEach(g=>{const count=coverage?.counts[g.dataset.id]||0;g.classList.toggle('coverage-active',!!coverage);g.classList.toggle('covered',count>0);g.style.setProperty('--coverage-color',count>=3?'#e34848':count===2?'#d69b00':count===1?'#179c58':'var(--uncovered)');});
 document.querySelectorAll('.point-group').forEach(g=>{g.classList.toggle('coverage-point',!!coverage?.pointIds.includes(g.dataset.id));});
 coverageLayer.replaceChildren();
 if(coverage)for(const s of segments){const count=coverage.counts[s.id];if(count<3)continue;const xy=s.geometry_xy;let total=0;const lengths=xy.slice(1).map((p,i)=>{const d=Math.hypot(p[0]-xy[i][0],p[1]-xy[i][1]);total+=d;return d;});let half=total/2,anchor=xy[0];for(let i=0;i<lengths.length;i++){if(half<=lengths[i]){const f=lengths[i]?half/lengths[i]:0;anchor=[xy[i][0]+(xy[i+1][0]-xy[i][0])*f,xy[i][1]+(xy[i+1][1]-xy[i][1])*f];break;}half-=lengths[i];}el('text',{x:anchor[0],y:-anchor[1],class:'coverage-count'},coverageLayer).textContent=`${count}×`;}
 renderCoverageLabels();if(selected)select(selected.kind,selected.id);
}
function renderCoverageLabels(){const u=view.w/Math.max(1,svg.clientWidth);coverageLayer.querySelectorAll('text').forEach(n=>{n.setAttribute('font-size',11*u);n.setAttribute('dy',-7*u);n.setAttribute('stroke-width',3*u);});}
function clearUploadedTrack(){
 $('uploadedTrackLayer').replaceChildren();$('uploadedTrackLayer').style.display='none';$('showUploadedTrack').checked=false;$('uploadedTrackToggle').hidden=true;$('uploadedTrackLegend').hidden=true;
}
function renderUploadedTrack(tracks){
 clearUploadedTrack();
 for(const track of tracks){let part=[],previous=null;
  const flush=()=>{if(part.length>1){const d=pathOf(part);el('path',{d,class:'uploaded-track-halo'},$('uploadedTrackLayer'));el('path',{d,class:'uploaded-track-path'},$('uploadedTrackLayer'));}part=[];};
  for(const point of track){const xy=TrackAnalysis.project(point.lon,point.lat,data.metadata.local_xy_origin_utm_m);
   if(!xy.every(Number.isFinite)){flush();previous=null;continue;}
   const gap=previous&&point.time!=null&&previous.time!=null?point.time-previous.time:0;
   if(previous&&(Math.hypot(xy[0]-previous.xy[0],xy[1]-previous.xy[1])>100||gap>120||gap<0))flush();
   part.push(xy);previous={xy,time:point.time};
  }flush();
 }
 const available=$('uploadedTrackLayer').childElementCount>0;
 $('uploadedTrackToggle').hidden=!available;$('uploadedTrackLegend').hidden=!available;$('showUploadedTrack').checked=available;$('uploadedTrackLayer').style.display=available?'':'none';
}
function restoreOriginal(){
 uploadGeneration++;coverage=null;clearUploadedTrack();$('trackFile').value='';$('trackResults').hidden=true;$('cancelTrack').hidden=true;$('trackStatus').textContent='支持 GPX / FIT；文件仅在浏览器内处理。';$('trackFile').disabled=false;refreshCoverage();
 if(originalState){for(const [id,checked]of Object.entries(originalState.layers)){$(id).checked=checked;$(id).dispatchEvent(new Event('change'));}view={...originalState.view};clearSelection();if(originalState.selection)select(originalState.selection.kind,originalState.selection.id);originalState=null;renderView();}
}
$('cancelTrack').addEventListener('click',restoreOriginal);
$('trackFile').addEventListener('change',async e=>{
 const file=e.target.files?.[0];if(!file)return;
 if(!originalState)originalState={view:{...view},selection:selected?{...selected}:null,layers:Object.fromEntries(['showRemoved','showBasemap','showLabels'].map(id=>[id,$(id).checked]))};
 const generation=++uploadGeneration;coverage=null;clearUploadedTrack();refreshCoverage();$('trackResults').hidden=true;$('cancelTrack').hidden=false;$('trackFile').disabled=true;$('trackStatus').textContent='正在读取轨迹…';
 try{
  if(file.size>20*1024*1024)throw Error('文件大小不能超过 20 MB');
  const extension=file.name.split('.').pop().toLowerCase();let tracks;
  if(extension==='gpx'){const xml=await file.text();if(generation!==uploadGeneration)return;tracks=TrackAnalysis.parseGPX(xml);}
  else if(extension==='fit'){const buffer=await file.arrayBuffer();if(generation!==uploadGeneration)return;tracks=TrackAnalysis.parseFIT(buffer);}
  else throw Error('请选择 .gpx 或 .fit 文件');
  renderUploadedTrack(tracks);
  const total=tracks.reduce((sum,t)=>sum+t.length,0);$('trackStatus').textContent=`正在匹配 ${nf.format(total)} 个坐标点…`;
  matcher ||= TrackAnalysis.createMatcher(data);
  const result=await matcher.match(tracks,{cancelled:()=>generation!==uploadGeneration,onProgress:n=>{$('trackStatus').textContent=`正在匹配 ${nf.format(n)} / ${nf.format(total)} 个坐标点…`;}});
  if(generation!==uploadGeneration)return;coverage=result;
  $('coveredPoints').textContent=`${result.pointCount} / ${points.length}（${(result.pointCount/points.length*100).toFixed(1)}%）`;
  $('coveredSegments').textContent=`${result.segmentCount} / ${segments.length}（${(result.segmentCount/segments.length*100).toFixed(1)}%）`;
  $('coveredDistance').textContent=dist(result.length_m);
  $('traversalTotal').textContent=Object.values(result.counts).reduce((a,b)=>a+b,0)+' 次';
  $('trackStatus').textContent=result.segmentCount?'匹配完成；颜色表示经过次数，3 次及以上显示数字标签。':'没有识别到完整通过的路段，请检查轨迹是否位于本校区。';
  $('trackResults').hidden=false;$('showRemoved').checked=false;$('removedLayer').style.display='none';clearSelection();refreshCoverage();reset();
 }catch(error){if(generation!==uploadGeneration)return;clearUploadedTrack();$('trackStatus').textContent=`无法分析：${error.message}`;}
 finally{if(generation===uploadGeneration)$('trackFile').disabled=false;}
});
window.routeNetworkViewer.clearTrack=restoreOriginal;
window.routeNetworkViewer.getCoverage=()=>coverage;
