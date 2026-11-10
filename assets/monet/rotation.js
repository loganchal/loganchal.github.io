/* Load paintings near the profile, decode before swapping, and rotate only on engagement. */
(() => {
 const card=document.querySelector('#oceanography'); if(!card)return;
 const first=card.querySelector('.area-preview'), credit=card.querySelector('.painting-caption');
 const second=first.cloneNode();second.alt='';second.setAttribute('aria-hidden','true');second.removeAttribute('src');card.append(second);
 const layers=[first,second];let paintings=[],position=-1,layer=0,busy=false,engaged=false,timer=null;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const load=fetch('/assets/monet/rotation.json').then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(x=>paintings=x).catch(()=>[]);
 async function advance(){
  await load;if(busy||!paintings.length)return;busy=true;
  const next=(position+1)%paintings.length,p=paintings[next],image=new Image();image.src=p.url;
  try{await image.decode();const dest=position<0?0:1-layer;layers[dest].src=p.url;layers[dest].alt=dest===0?'Claude Monet, '+p.title+', '+p.date:'';
   layers[dest].dataset.active='true';layers[1-dest].dataset.active='false';position=next;layer=dest;
   if(credit)credit.textContent='Monet · '+p.title+' · '+p.date;card.dataset.painting=p.id;
  }catch(e){/* Retain the last decoded image if a request fails. */}finally{busy=false}
 }
 function stop(){engaged=false;clearInterval(timer);timer=null}
 function start(){if(engaged)return;engaged=true;advance();if(!reduced.matches)timer=setInterval(advance,5500)}
 card.addEventListener('pointerenter',start);card.addEventListener('pointerleave',()=>{if(!card.contains(document.activeElement))stop()});
 card.addEventListener('focusin',start);card.addEventListener('focusout',()=>{if(!card.matches(':hover'))stop()});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});
 reduced.addEventListener('change',stop);
 const observer=new IntersectionObserver(entries=>{if(entries.some(x=>x.isIntersecting)){if(position<0)advance();observer.disconnect()}},{rootMargin:'180px'});observer.observe(card);
})();
