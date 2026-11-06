/* Load only the registered pixels and resolution needed by the visible canvas. */
const OpeningAssets = (() => {
 const profile = () => matchMedia('(max-aspect-ratio:1/1)').matches ? 'portrait' : 'wide';
 function pick(scene,which=profile(),width=innerWidth,height=innerHeight,dpr=devicePixelRatio){
  const data=scene.delivery[which];
  let need=Math.max(width/data.width,height/data.height)*dpr;
  if(navigator.connection?.saveData)need=Math.min(need,1);
  let level=data.levels.find(item=>item.density>=need*.97)||data.levels.at(-1);
  const artWidth=Math.max(width,height*data.width/data.height);
  const minimumInset=((artWidth-width)/2+Math.min(40,width*.06))/artWidth;
  const openingInset=Math.max(scene.finalInset,which==='portrait'?(scene.portrait_openingInset??25):(scene.openingInset??26))/100;
  if(level.tall&&Math.max(openingInset,minimumInset)>level.widths[0])level={...level,...level.tall};
  return {...level,profile:which,width:data.width,height:data.height,key:which+':'+level.urls.join('|')};
 }
 // Keep the current and previous three-layer frames decoded. Share requests
 // between overlapping selections instead of downloading or decoding twice.
 const pending=new Map(),decoded=new Map(),decodedLimit=6;
 function remember(url,image){
  decoded.delete(url);decoded.set(url,image);
  while(decoded.size>decodedLimit)decoded.delete(decoded.keys().next().value);
 }
 function loadOne(url,signal){
  if(signal?.aborted)return Promise.resolve(false);
  if(decoded.has(url)){
   remember(url,decoded.get(url));return Promise.resolve(true);
  }
  let asset=pending.get(url);
  if(!asset){
   const image=new Image();image.decoding='async';image.fetchPriority='high';
   asset={image,waiters:new Set(),done:false};pending.set(url,asset);
   asset.finish=ok=>{
    if(asset.done)return;asset.done=true;pending.delete(url);
    image.onload=image.onerror=null;
    if(ok)remember(url,image);
    for(const waiter of [...asset.waiters])waiter.finish(ok);
   };
   image.onload=async()=>{try{await image.decode();asset.finish(true);}catch{asset.finish(false);}};
   image.onerror=()=>asset.finish(false);image.src=url;
  }
  return new Promise(resolve=>{
   const waiter={finish:ok=>{
    signal?.removeEventListener('abort',abort);asset.waiters.delete(waiter);resolve(ok);
   }};
   const abort=()=>{
    waiter.finish(false);
    // A new orientation/selection may reuse the same URLs synchronously after
    // cancelling its predecessor. Give that subscriber a chance to join.
    queueMicrotask(()=>{
     if(!asset.done&&!asset.waiters.size){asset.finish(false);asset.image.removeAttribute('src');}
    });
   };
   asset.waiters.add(waiter);signal?.addEventListener('abort',abort,{once:true});
  });
 }
 async function load(choice,signal){return (await Promise.all(choice.urls.map(url=>loadOne(url,signal)))).every(Boolean);}
 async function prepare(scene,signal){
  for(let attempt=0;attempt<3;attempt++){
   const choice=pick(scene);
   if(!await load(choice,signal))return null;
   if(signal?.aborted)return null;
   if(pick(scene).key===choice.key)return choice;
  }
  return null;
 }
 function apply(canvas,choice){
  canvas.style.width=`max(100cqw,${choice.width/choice.height*100}cqh)`;
  canvas.style.height=`max(${choice.height/choice.width*100}cqw,100cqh)`;
  for(const [index,slot] of [0,2,1].entries()){
   const layer=canvas.children[index];layer.style.backgroundImage=`url("${choice.urls[slot]}")`;
   layer.style.backgroundSize=`${choice.widths[slot]*100}% 100%`;
   layer.style.backgroundPosition=slot===0?'left center':slot===2?'right center':'center';
  }
  canvas.dataset.assetProfile=choice.profile;canvas.dataset.assetKey=choice.key;
  canvas.dataset.sideCoverage=Math.min(choice.widths[0],choice.widths[2])*100;
 }
 return {profile,pick,prepare,apply,load};
})();
