/* Local-only track decoding and topology-aware route matching. */
(function (root) {
'use strict';
const distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const valid=(lon,lat)=>Number.isFinite(lon)&&Number.isFinite(lat)&&Math.abs(lon)<=180&&Math.abs(lat)<=90;
function parseGPX(xml,Parser=globalThis.DOMParser){
 if(!Parser)throw Error('无法解析 XML');
 if(/<!DOCTYPE/i.test(xml))throw Error('GPX 不支持文档类型声明');
 const doc=new Parser().parseFromString(xml,'application/xml');
 if(doc.getElementsByTagName('parsererror').length||doc.documentElement?.localName!=='gpx')throw Error('GPX 文件格式无效');
 const descendants=(node,name)=>Array.from(node.getElementsByTagName('*')).filter(n=>n.localName===name);
 let groups=descendants(doc,'trkseg').map(n=>descendants(n,'trkpt'));
 if(!groups.some(group=>group.length>=2))groups=descendants(doc,'rte').map(n=>descendants(n,'rtept'));
 const tracks=[];let count=0;
 for(const group of groups){let part=[];for(const n of group){
  if(++count>100000)throw Error('轨迹最多支持 100,000 个坐标点');
  const number=name=>{const value=n.getAttribute(name);return value!=null&&/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(value.trim())?Number(value):NaN;};
  const lon=number('lon'),lat=number('lat');
  if(!valid(lon,lat)){if(part.length>1)tracks.push(part);part=[];continue;}
  const time=Date.parse(descendants(n,'time')[0]?.textContent||'');part.push({lon,lat,time:Number.isFinite(time)?time/1000:null});
 }if(part.length>1)tracks.push(part);}
 if(!tracks.length)throw Error('文件中没有有效的连续 GPS 轨迹');return tracks;
}
function crc(bytes,start,end){let value=0;for(let i=start;i<end;i++){value^=bytes[i];for(let j=0;j<8;j++)value=(value&1)?(value>>>1)^0xa001:value>>>1;}return value;}
function parseFIT(buffer){
 const bytes=new Uint8Array(buffer),v=new DataView(buffer);let pos=0,tracks=[],part=[],count=0;
 const flush=()=>{if(part.length>1)tracks.push(part);part=[];};
 while(pos<bytes.length){
  const base=pos,h=bytes[pos];
  if(![12,14].includes(h)||pos+h>bytes.length||String.fromCharCode(...bytes.slice(pos+8,pos+12))!=='.FIT')throw Error('FIT 文件头无效');
  if(h===14&&v.getUint16(pos+12,true)!==0&&crc(bytes,pos,pos+14)!==0)throw Error('FIT 文件头校验失败');
  const end=pos+h+v.getUint32(pos+4,true);if(end+2>bytes.length)throw Error('FIT 文件不完整');
  if(crc(bytes,base,end+2)!==0)throw Error('FIT 文件校验失败');
  pos+=h;const defs=new Map();let timestamp=null;
  const need=n=>{if(pos+n>end)throw Error('FIT 数据记录不完整');};
  while(pos<end){need(1);const header=bytes[pos++],compressed=!!(header&128),local=compressed?(header>>5)&3:header&15;
   if(!compressed&&(header&64)){
    need(5);pos++;const arch=bytes[pos++];if(arch>1)throw Error('FIT 字节序无效');const little=arch===0,global=v.getUint16(pos,little);pos+=2;const n=bytes[pos++],fields=[];need(n*3);
    for(let i=0;i<n;i++){fields.push({num:bytes[pos],size:bytes[pos+1],type:bytes[pos+2]});pos+=3;}
    let extra=0;if(header&32){need(1);const m=bytes[pos++];need(m*3);for(let i=0;i<m;i++){extra+=bytes[pos+1];pos+=3;}}
    defs.set(local,{global,little,fields,extra});continue;
   }
   const def=defs.get(local);if(!def)throw Error('FIT 缺少记录定义');let lon=null,lat=null,time=timestamp;
   for(const f of def.fields){need(f.size);
    if(f.size===4&&f.num===253&&(f.type&31)===6){const t=v.getUint32(pos,def.little);if(t!==0xffffffff)time=timestamp=t;}
    if(def.global===20&&f.size===4&&(f.type&31)===5&&(f.num===0||f.num===1)){const n=v.getInt32(pos,def.little);if(n!==0x7fffffff){if(f.num===0)lat=n*180/2147483648;else lon=n*180/2147483648;}}
    pos+=f.size;
   }
   need(def.extra);pos+=def.extra;
   if(compressed){if(timestamp===null)throw Error('FIT 压缩时间戳缺少基准');const offset=header&31;time=(timestamp&~31)+offset+(offset<(timestamp&31)?32:0);timestamp=time;}
   if(def.global===20){if(++count>100000)throw Error('轨迹最多支持 100,000 个坐标点');if(valid(lon??NaN,lat??NaN))part.push({lon,lat,time});else flush();}
  }
  pos=end+2;flush();
 }
 if(!tracks.length)throw Error('文件中没有有效的连续 GPS 轨迹');return tracks;
}
/* WGS84 transverse Mercator, UTM zone 50 north. */
function project(lon,lat,origin){
 const r=Math.PI/180,a=6378137,e=0.0066943799901413165,k=.9996,p=lat*r,l=(lon-117)*r,ep=e/(1-e);
 const s=Math.sin(p),c=Math.cos(p),t=Math.tan(p)**2,n=a/Math.sqrt(1-e*s*s),C=ep*c*c,A=c*l;
 const M=a*((1-e/4-3*e**2/64-5*e**3/256)*p-(3*e/8+3*e**2/32+45*e**3/1024)*Math.sin(2*p)+(15*e**2/256+45*e**3/1024)*Math.sin(4*p)-35*e**3/3072*Math.sin(6*p));
 return [500000+k*n*(A+(1-t+C)*A**3/6+(5-18*t+t*t+72*C-58*ep)*A**5/120)-origin[0],k*(M+n*Math.tan(p)*(A*A/2+(5-t+9*C+4*C*C)*A**4/24+(61-58*t+t*t+600*C-330*ep)*A**6/720))-origin[1]];
}
function createMatcher(data){
 const nodes=data.points.map(p=>p.id),indices=new Map(nodes.map((id,i)=>[id,i]));
 const edges=data.segments.map(s=>{let sum=0;const spans=[];for(let i=1;i<s.geometry_xy.length;i++){const a=s.geometry_xy[i-1],b=s.geometry_xy[i],length=distance(a,b);if(length){spans.push({a,b,start:sum,length});sum+=length;}}return {...s,spans,total:sum,a:indices.get(s.point_a),b:indices.get(s.point_b)};});
 // Precompute shortest paths while preserving distinct routes between the same endpoints.
 const n=nodes.length,D=Array.from({length:n},()=>Array(n).fill(Infinity)),routes=Array.from({length:n},()=>Array.from({length:n},()=>[]));
 for(let i=0;i<n;i++)D[i][i]=0;
 edges.forEach((e,i)=>{if(e.total<D[e.a][e.b]){D[e.a][e.b]=D[e.b][e.a]=e.total;routes[e.a][e.b]=[{edge:i,from:0,to:e.total}];routes[e.b][e.a]=[{edge:i,from:e.total,to:0}];}});
 for(let k=0;k<n;k++)for(let i=0;i<n;i++)for(let j=0;j<n;j++)if(D[i][k]+D[k][j]<D[i][j]){D[i][j]=D[i][k]+D[k][j];routes[i][j]=routes[i][k].concat(routes[k][j]);}
 function candidates(p){const out=[];edges.forEach((e,i)=>{let best=Infinity,at=0;for(const s of e.spans){const dx=s.b[0]-s.a[0],dy=s.b[1]-s.a[1],f=Math.max(0,Math.min(1,((p[0]-s.a[0])*dx+(p[1]-s.a[1])*dy)/(s.length*s.length))),d=Math.hypot(p[0]-s.a[0]-f*dx,p[1]-s.a[1]-f*dy);if(d<best){best=d;at=s.start+f*s.length;}}if(best<=25)out.push({edge:i,at,offset:best});});return out.sort((a,b)=>a.offset-b.offset).slice(0,5);}
 function transition(a,b){const x=edges[a.edge],y=edges[b.edge];let best=a.edge===b.edge?{length:Math.abs(a.at-b.at),pieces:[{edge:a.edge,from:a.at,to:b.at}]}:{length:Infinity,pieces:[]};
  for(const [u,from]of[[x.a,0],[x.b,x.total]])for(const [w,to]of[[y.a,0],[y.b,y.total]]){const length=Math.abs(a.at-from)+D[u][w]+Math.abs(b.at-to);if(length<best.length)best={length,pieces:[{edge:a.edge,from:a.at,to:from},...routes[u][w],{edge:b.edge,from:to,to:b.at}]};}return best;
 }
 async function match(tracks,{onProgress=()=>{},cancelled=()=>false,xy=false}={}){
  const counts=Object.fromEntries(edges.map(e=>[e.id,0])),covered=new Set();let sampleCount=0,matched=0,processed=0,episodes=[],run=[],previous=null;
  const check=()=>{if(cancelled())throw Error('cancelled');};
  // Backtrack the most likely connected route, then count directional passes.
  function finish(){if(!run.length)return;let state=run.at(-1).reduce((a,b)=>a.cost<b.cost?a:b),states=[];while(state){states.push(state);state=state.prev;}states.reverse();
   for(const state of states){const e=edges[state.edge],tol=Math.min(12,e.total*.2);if(state.at<=tol)covered.add(e.point_a);if(e.total-state.at<=tol)covered.add(e.point_b);}
   let current=null;
   function close(){if(current){const e=edges[current.edge];if(current.max-current.min>=e.total*.8-1e-6)counts[e.id]++;}current=null;}
   for(let i=1;i<states.length;i++)for(const p of transition(states[i-1],states[i]).pieces){if(Math.abs(p.to-p.from)<.05)continue;
    const edge=edges[p.edge],tol=Math.min(12,edge.total*.2);if(Math.min(p.from,p.to)<=tol)covered.add(edge.point_a);if(edge.total-Math.max(p.from,p.to)<=tol)covered.add(edge.point_b);
    const sign=Math.sign(p.to-p.from);
    if(!current||current.edge!==p.edge){close();current={edge:p.edge,min:Math.min(p.from,p.to),max:Math.max(p.from,p.to),sign,extreme:p.to};}
    // Ignore small along-route reversals from stationary GPS jitter.
    else if(sign!==current.sign&&Math.abs(p.to-current.extreme)>8){const turning=current.extreme;close();current={edge:p.edge,min:Math.min(turning,p.to),max:Math.max(turning,p.to),sign,extreme:p.to};}
    else{current.min=Math.min(current.min,p.to);current.max=Math.max(current.max,p.to);if(sign===current.sign)current.extreme=p.to;}
   }close();episodes.push(states.length);run=[];previous=null;
  }
  for(const track of tracks){finish();let retained=null;
   for(let i=0;i<track.length;i++){
    check();const t=track[i],p=xy?t.xy:project(t.lon,t.lat,data.metadata.local_xy_origin_utm_m);sampleCount++;
    if(++processed%250===0){onProgress(processed);await new Promise(resolve=>setTimeout(resolve,0));check();}
    if(retained&&distance(retained,p)<2&&i!==track.length-1)continue;
    retained=p;const cs=candidates(p);if(!cs.length){finish();continue;}matched++;
    const step=previous?distance(previous.p,p):0,timeGap=previous&&t.time!=null&&previous.time!=null?t.time-previous.time:0;
    if(previous&&(step>100||timeGap>120||timeGap<0))finish();
    const before=run.at(-1);const row=cs.map(c=>{let cost=c.offset*c.offset/72,prev=null;
     if(before){let best=Infinity;for(const a of before){const tr=transition(a,c),penalty=Math.abs(tr.length-step)/5+(tr.length>step*3+30?20:0);if(a.cost+penalty<best){best=a.cost+penalty;prev=a;}}cost+=best;}
     return {...c,cost,prev};});
    const min=Math.min(...row.map(c=>c.cost));row.forEach(c=>c.cost-=min);run.push(row);previous={p,time:t.time};
   }finish();
  }
  check();const segmentCount=Object.values(counts).filter(c=>c>0).length,length=edges.reduce((sum,e)=>sum+counts[e.id]*e.length_m,0);
  return {counts,pointIds:[...covered],pointCount:covered.size,segmentCount,length_m:length,sampleCount,matchedSampleCount:matched,matchedRunCount:episodes.length};
 }
 return {match,edges,candidates,transition};
}
const api={parseGPX,parseFIT,project,createMatcher,crc};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.TrackAnalysis=api;
})(globalThis);
