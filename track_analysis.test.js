/* Synthetic fixtures contain no personal activity data. Run with node --test. */
'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const A=require('./track_analysis.js');
const data={metadata:{local_xy_origin_utm_m:[0,0]},points:[{id:'A'},{id:'B'},{id:'C'},{id:'D'}],segments:[
 {id:'AB',point_a:'A',point_b:'B',length_m:120,geometry_xy:[[0,0],[100,0]]},
 {id:'BC',point_a:'B',point_b:'C',length_m:100,geometry_xy:[[100,0],[200,0]]},
 {id:'CD',point_a:'C',point_b:'D',length_m:100,geometry_xy:[[200,0],[200,100]]},
 {id:'DA',point_a:'D',point_b:'A',length_m:225,geometry_xy:[[200,100],[0,100],[0,0]]}
]};
const along=(from,to,y=0)=>Array.from({length:Math.abs(to-from)/5+1},(_,i)=>({xy:[from+i*5*Math.sign(to-from),y]}));
const match=t=>A.createMatcher(data).match(t,{xy:true});
test('one, two and three traversals use stored lengths including reversal',async()=>{
 for(let n=1;n<=3;n++){let t=[];for(let i=0;i<n;i++)t.push(...along(i%2?200:0,i%2?0:200));const r=await match([t]);assert.equal(r.counts.AB,n);assert.equal(r.counts.BC,n);assert.equal(r.length_m,220*n);assert.equal(r.pointCount,3);assert.equal(r.segmentCount,2);}
});
test('stationary jitter, partial passes and separate track groups do not become full traversals',async()=>{
 assert.equal((await match([along(20,70)])).segmentCount,0);
 assert.equal((await match([Array.from({length:80},(_,i)=>({xy:[i%2?4:0,0]}))])).segmentCount,0);
 assert.equal((await match([along(0,40),along(60,100)])).segmentCount,0);
});
test('time gaps and unmatched coordinates break connectivity',async()=>{
 const t=[...along(0,40).map(p=>({...p,time:0})),...along(60,100).map(p=>({...p,time:300}))];assert.equal((await match([t])).segmentCount,0);
 assert.equal((await match([[...along(0,40),{xy:[9999,9999]},...along(60,100)]])).segmentCount,0);
});
test('nearby parallel roads remain separate',async()=>{
 const d={...data,points:[...data.points,{id:'E'},{id:'F'}],segments:[...data.segments,{id:'EF',point_a:'E',point_b:'F',length_m:100,geometry_xy:[[0,15],[100,15]]}]};
 const r=await A.createMatcher(d).match([along(0,100,1)],{xy:true});assert.equal(r.counts.AB,1);assert.equal(r.counts.EF,0);
});
test('curved geometry is followed and uses its stored route length',async()=>{
 const d={...data,segments:[{id:'curve',point_a:'A',point_b:'B',length_m:155,geometry_xy:[[0,0],[50,50],[100,0]]}]};
 const t=[...along(0,50).map(p=>({xy:[p.xy[0],p.xy[0]]})),...along(50,100).map(p=>({xy:[p.xy[0],100-p.xy[0]]}))];const r=await A.createMatcher(d).match([t],{xy:true});assert.equal(r.counts.curve,1);assert.equal(r.length_m,155);
});
test('cancellation is observed during long analyses',async()=>{
 let stop=false;await assert.rejects(A.createMatcher(data).match([Array.from({length:1000},(_,i)=>({xy:[i%100,0]}))],{xy:true,onProgress:()=>{stop=true;},cancelled:()=>stop}),/cancelled/);
});
function fixture(little=true,developer=false,compressed=false){
 const chunks=[],u32=(n,signed=false)=>{const b=Buffer.alloc(4);signed?b[little?'writeInt32LE':'writeInt32BE'](n):b[little?'writeUInt32LE':'writeUInt32BE'](n);return b;};
 chunks.push(Buffer.from([developer?0x60:0x40,0,little?0:1,...(little?[20,0]:[0,20]),3,253,4,0x86,0,4,0x85,1,4,0x85,...(developer?[1,0,2,0]:[])]));
 for(let i=0;i<3;i++)chunks.push(Buffer.concat([Buffer.from([0]),u32(100+i),u32(Math.round((40+i*.001)/180*2**31),true),u32(Math.round(116/180*2**31),true),...(developer?[Buffer.from([9,8])]:[])]));
 if(compressed){chunks.push(Buffer.from([0x41,0,little?0:1,...(little?[20,0]:[0,20]),2,0,4,0x85,1,4,0x85]));chunks.push(Buffer.concat([Buffer.from([0xa7]),u32(Math.round(40.003/180*2**31),true),u32(Math.round(116/180*2**31),true)]));}
 const payload=Buffer.concat(chunks),header=Buffer.alloc(14);header[0]=14;header[1]=0x20;header.writeUInt32LE(payload.length,4);header.write('.FIT',8);header.writeUInt16LE(A.crc(header,0,12),12);
 const body=Buffer.concat([header,payload]),tail=Buffer.alloc(2);tail.writeUInt16LE(A.crc(body,0,body.length));return Buffer.concat([body,tail]);
}
const buffer=b=>b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength);
test('FIT endian, developer fields, compressed timestamps, chained files and CRC',()=>{
 for(const little of [true,false])for(const dev of [true,false]){const r=A.parseFIT(buffer(fixture(little,dev,true)));assert.equal(r[0].length,4);assert.ok(Math.abs(r[0][0].lat-40)<1e-6);assert.equal(r[0][3].time,103);}
 assert.equal(A.parseFIT(buffer(Buffer.concat([fixture(),fixture()]))).length,2);
 const bad=fixture();bad[30]^=1;assert.throws(()=>A.parseFIT(buffer(bad)),/校验/);assert.throws(()=>A.parseFIT(new ArrayBuffer(10)),/文件头/);
});
test('projection agrees with stored WGS84 coordinates',()=>{
 const d=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'route_network.json')));for(const p of d.points){const xy=A.project(p.longitude,p.latitude,d.metadata.local_xy_origin_utm_m);assert.ok(Math.hypot(xy[0]-p.x_m,xy[1]-p.y_m)<.01);}
});
test('every current segment, including short junction links, supports one or three passes without covering adjacent roads',async()=>{
 const d=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'route_network.json'))),m=A.createMatcher(d);
 for(const s of d.segments){const track=[];for(let i=1;i<s.geometry_xy.length;i++){const p=s.geometry_xy[i-1],q=s.geometry_xy[i],n=Math.ceil(Math.hypot(p[0]-q[0],p[1]-q[1])/3);for(let j=0;j<n;j++)track.push({xy:[p[0]+(q[0]-p[0])*j/n,p[1]+(q[1]-p[1])*j/n]});}track.push({xy:s.geometry_xy.at(-1)});for(const [passes,route]of [[1,track],[3,track.concat([...track].reverse(),track)]]){const r=await m.match([route],{xy:true});assert.equal(r.counts[s.id],passes,s.id);assert.equal(r.segmentCount,1,s.id);assert.ok(Math.abs(r.length_m-s.length_m*passes)<1e-6,s.id);}}
});
