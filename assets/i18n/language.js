(() => {
 const originalTitle=document.title;let language='en';try{language=localStorage.getItem('site-language')==='mi'?'mi':'en'}catch(_){}
 const controls=[...document.querySelectorAll('[data-language]')];let messages;
 function apply(next){
  if(!messages)return;language=next==='mi'?'mi':'en';const strings=messages[language];document.documentElement.lang=language;
  document.querySelectorAll('[data-i18n]').forEach(el=>{if(strings[el.dataset.i18n])el.textContent=strings[el.dataset.i18n]});
  document.querySelectorAll('[data-i18n-aria]').forEach(el=>{if(strings[el.dataset.i18nAria])el.setAttribute('aria-label',strings[el.dataset.i18nAria])});
  ['alt','title'].forEach(attr=>document.querySelectorAll('[data-i18n-'+attr+']').forEach(el=>{const key=el.getAttribute('data-i18n-'+attr);if(strings[key])el.setAttribute(attr,strings[key])}));
  controls.forEach(el=>el.setAttribute('aria-pressed',String(el.dataset.language===language)));
  // Publication metadata keeps the canonical titles; the displayed titles follow the language.
  document.querySelectorAll('.published-paper h2,.preprint-panel h3').forEach(el=>el.lang=language);
  document.title=location.pathname.includes('mathematics')?strings.mathematics+' · Logan Chalmers':(language==='en'?originalTitle:'Logan Chalmers · Mātai aumoana me te Pāngarau');
  try{localStorage.setItem('site-language',language)}catch(_){}
  document.dispatchEvent(new CustomEvent('site-language-change',{detail:{language}}));
 }
 controls.forEach(el=>el.addEventListener('click',()=>apply(el.dataset.language)));
 window.addEventListener('storage',e=>{if(e.key==='site-language'&&['en','mi'].includes(e.newValue)&&e.newValue!==language)apply(e.newValue)});
 fetch('/assets/i18n/messages.json?v=20261110-reo1').then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(data=>{messages=data;apply(language)}).catch(()=>controls.forEach(el=>el.disabled=true));
})();
