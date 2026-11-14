import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export function createLocationGlobe(onSelect:(lat:number,lon:number)=>void) {
 const host=document.getElementById('pick-globe')!;
 const status=document.getElementById('globe-status')!;
 const places:Record<string,[number,number]>={Singapore:[1.35,103.82],Borneo:[-2.2,113.9],London:[51.51,-.13],'New York':[40.71,-74.01],Sydney:[-33.87,151.21]};
 const dropdown=document.getElementById('place') as HTMLSelectElement;
 let lat=1.35,lon=103.82;
 let updateScene=()=>{};
 const position=(latitude:number,longitude:number,r=1.02)=>{
  const a=latitude*Math.PI/180,b=longitude*Math.PI/180;
  return new THREE.Vector3(r*Math.cos(a)*Math.cos(b),r*Math.sin(a),-r*Math.cos(a)*Math.sin(b));
 };
 function select(a:number,b:number,name='Custom',focus=false){
  lat=Math.max(-90,Math.min(90,a));lon=((b+180)%360+360)%360-180;
  dropdown.value=name;document.getElementById('place-name')!.textContent=name==='Custom'?'Your selected point':name;
  document.getElementById('pin-coordinates')!.textContent=Math.abs(lat).toFixed(3)+'° '+(lat>=0?'N':'S')+' · '+Math.abs(lon).toFixed(3)+'° '+(lon>=0?'E':'W');
  const zone=Math.abs(lat)<=23.44?'tropical latitude band':Math.abs(lat)>=66.56?'polar latitude band':'temperate latitude band';
  document.getElementById('geo-facts')!.textContent='The pin is in the '+zone+', approximately '+(Math.abs(lat)*111.2).toFixed(0)+' km from the equator along a meridian. Latitude bands describe geometry, not a local climate classification.';
  updateScene();if(focus)focusPin();onSelect(lat,lon);
 }
 let focusPin=()=>{};
 dropdown.onchange=()=>{const p=places[dropdown.value];if(p)select(...p,dropdown.value,true);};
 document.getElementById('home-pin')!.onclick=()=>select(...places.Singapore,'Singapore',true);
 host.addEventListener('keydown',e=>{
  const delta=e.shiftKey?.1:1;
  if(!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key))return;
  e.preventDefault();
  select(lat+(e.key==='ArrowUp'?delta:e.key==='ArrowDown'?-delta:0),lon+(e.key==='ArrowRight'?delta:e.key==='ArrowLeft'?-delta:0),'Custom',true);
 });
 try{
  const renderer=new THREE.WebGLRenderer({alpha:true,antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));host.append(renderer.domElement);
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(42,1,.1,30);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enablePan=false;controls.minDistance=1.2;controls.maxDistance=5;
  const texture=new THREE.TextureLoader().load('/images/earth.jpg',()=>{render();},undefined,()=>{status.textContent='Surface texture unavailable. Pin selection and place shortcuts still work.';});
  texture.colorSpace=THREE.SRGBColorSpace;
  const globe=new THREE.Mesh(new THREE.SphereGeometry(1,80,56),new THREE.MeshBasicMaterial({map:texture}));
  scene.add(globe);
  const marker=new THREE.Mesh(new THREE.SphereGeometry(.018,16,12),new THREE.MeshBasicMaterial({color:0xffcc66}));scene.add(marker);
  function render(){renderer.render(scene,camera);}
  updateScene=()=>{marker.position.copy(position(lat,lon));render();};
  focusPin=()=>{camera.position.copy(position(lat,lon,2.9));controls.update();render();};
  controls.addEventListener('change',render);
  const resize=new ResizeObserver(()=>{renderer.setSize(host.clientWidth,host.clientHeight);camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix();render();});resize.observe(host);
  const ray=new THREE.Raycaster();let x=0,y=0,dragged=false;
  renderer.domElement.addEventListener('pointerdown',e=>{x=e.clientX;y=e.clientY;dragged=false;});
  renderer.domElement.addEventListener('pointermove',e=>{if(Math.hypot(e.clientX-x,e.clientY-y)>6)dragged=true;});
  renderer.domElement.addEventListener('pointerup',e=>{
   if(dragged||e.button!==0)return;
   const rect=renderer.domElement.getBoundingClientRect();
   ray.setFromCamera(new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,1-(e.clientY-rect.top)/rect.height*2),camera);
   const hit=ray.intersectObject(globe)[0];if(!hit)return;
   const point=hit.point.clone().normalize();
   select(Math.asin(point.y)*180/Math.PI,Math.atan2(-point.z,point.x)*180/Math.PI);
  });
  status.textContent='Click the surface to select a point. Keyboard: arrow keys move the pin 1°; Shift + arrows move 0.1°.';
  focusPin();
 }catch{status.textContent='3D is unavailable on this device. Choose a place above, or focus this area and use arrow keys to move the pin.';}
 select(lat,lon,'Singapore');
}
