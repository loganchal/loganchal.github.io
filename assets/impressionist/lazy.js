/* Prepare nearby paper art without downloading the whole page's paintings at once. */
(()=>{
 const panels=[...document.querySelectorAll('.published-paper,.preprint-panel')];
 panels.forEach(p=>p.classList.add('deferred-art'));
 const prepare=async p=>{if(p.dataset.artReady||p.dataset.artLoading)return;p.dataset.artLoading='true';const value=p.style.getPropertyValue('--paper-art');const url=value.match(/url\(['"]?([^'")]+)['"]?\)/)?.[1];if(!url)return;const image=new Image();image.src=url;try{await image.decode();p.dataset.artReady='true'}catch(_){p.classList.remove('deferred-art')}};
 const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){prepare(e.target);observer.unobserve(e.target)}}),{rootMargin:'240px'});panels.forEach(p=>{observer.observe(p);p.addEventListener('pointerenter',()=>prepare(p));p.addEventListener('focusin',()=>prepare(p))});
})();
