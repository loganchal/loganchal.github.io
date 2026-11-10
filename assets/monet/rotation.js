/* Decode before revealing a new hover; retain only the current and next painting. */
(() => {
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 function setup(selector,manifest){
  const card=document.querySelector(selector);if(!card)return;
  card.classList.add('rotating-art');
  const first=card.querySelector('.area-preview'),second=first.cloneNode();
  first.alt='';first.setAttribute('aria-hidden','true');second.alt='';second.setAttribute('aria-hidden','true');second.removeAttribute('src');second.dataset.active='false';card.append(second);
  const layers=[first,second];let paintings=[],position=-1,layer=0,busy=false,engaged=false,timer=null,pending,prepared=null,version=0;
  const touch=matchMedia('(hover: none)');
  function load(){return pending||(pending=fetch(manifest).then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(x=>paintings=x).catch(()=>[]))}
  function prepare(index){if(prepared?.index===index)return prepared.promise;const image=new Image();image.src=paintings[index].url;const promise=image.decode().then(()=>image);prepared={index,promise};promise.catch(()=>{});return promise}
  async function advance(revealVersion=null){
   await load();if(busy||!paintings.length)return;busy=true;
   const next=(position+1)%paintings.length,p=paintings[next];
   try{await prepare(next);const dest=position<0?0:1-layer;layers[dest].src=p.url;layers[dest].dataset.active='true';layers[1-dest].dataset.active='false';position=next;layer=dest;card.dataset.painting=p.id;
    if(touch.matches||(engaged&&(revealVersion===null||revealVersion===version))){
     requestAnimationFrame(()=>{if(engaged||touch.matches){card.dataset.artWaiting='false';card.dataset.artVisible='true'}});
    }
    prepare((position+1)%paintings.length);
   }catch(e){/* Keep the solid panel if decoding fails. */}finally{busy=false;if(engaged&&card.dataset.artWaiting==='true'&&revealVersion!==version)advance(version)}
  }
  function stop(){engaged=false;version++;card.dataset.artVisible='false';clearInterval(timer);timer=null}
  function start(){if(engaged)return;engaged=true;version++;card.dataset.artVisible='false';card.dataset.artWaiting='true';advance(version);if(!reduced.matches)timer=setInterval(()=>advance(),5500)}
  card.addEventListener('pointerenter',start);card.addEventListener('pointerleave',()=>{if(!card.contains(document.activeElement))stop()});
  card.addEventListener('focusin',start);card.addEventListener('focusout',()=>{if(!card.matches(':hover'))stop()});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});reduced.addEventListener('change',stop);
  const observer=new IntersectionObserver(entries=>{if(entries.some(x=>x.isIntersecting)){if(position<0&&!engaged)advance();observer.disconnect()}},{rootMargin:'180px'});observer.observe(card);
 }
 setup('#oceanography','/assets/monet/rotation.json');
 setup('#mathematics','/assets/classical/rotation.json?v=pastoral2');
})();
