/* Decode before swapping; rotate only while a subject panel is engaged. */
(() => {
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 function setup(selector,manifest){
  const card=document.querySelector(selector);if(!card)return;
  const first=card.querySelector('.area-preview'),second=first.cloneNode();
  first.alt='';first.setAttribute('aria-hidden','true');second.alt='';second.setAttribute('aria-hidden','true');second.removeAttribute('src');second.dataset.active='false';card.append(second);
  const layers=[first,second];let paintings=[],position=-1,layer=0,busy=false,engaged=false,timer=null,pending;
  function load(){return pending||(pending=fetch(manifest).then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(x=>paintings=x).catch(()=>[]))}
  async function advance(){
   await load();if(busy||!paintings.length)return;busy=true;
   const next=(position+1)%paintings.length,p=paintings[next],image=new Image();image.src=p.url;
   try{await image.decode();const dest=position<0?0:1-layer;layers[dest].src=p.url;layers[dest].dataset.active='true';layers[1-dest].dataset.active='false';position=next;layer=dest;card.dataset.painting=p.id;}
   catch(e){/* Keep the last decoded image if a request fails. */}finally{busy=false}
  }
  function stop(){engaged=false;clearInterval(timer);timer=null}
  function start(){if(engaged)return;engaged=true;advance();if(!reduced.matches)timer=setInterval(advance,5500)}
  card.addEventListener('pointerenter',start);card.addEventListener('pointerleave',()=>{if(!card.contains(document.activeElement))stop()});
  card.addEventListener('focusin',start);card.addEventListener('focusout',()=>{if(!card.matches(':hover'))stop()});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});reduced.addEventListener('change',stop);
  const observer=new IntersectionObserver(entries=>{if(entries.some(x=>x.isIntersecting)){if(position<0)advance();observer.disconnect()}},{rootMargin:'180px'});observer.observe(card);
 }
 setup('#oceanography','/assets/monet/rotation.json');
 setup('#mathematics','/assets/classical/rotation.json');
})();
