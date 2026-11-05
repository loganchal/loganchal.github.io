const openings=openingScenes.filter(scene=>scene.active!==false).map(scene=>scene.id);
let openingDeckMemory;
function chooseOpening({ignoreRequested=false,current=null}={}){
 const requested=ignoreRequested?null:new URLSearchParams(location.search).get('study');
 const catalogue=openings.join('|'),key='opening-deck-v4';let deck=[],last,seenFamilies=[];
 const lead=id=>openingScenes.find(scene=>scene.id===id)?.lead;
 try{const saved=openingDeckMemory||JSON.parse(localStorage.getItem(key));if(saved){last=saved.last;if(saved.catalogue===catalogue&&Array.isArray(saved.deck)&&saved.deck.every(id=>openings.includes(id))&&new Set(saved.deck).size===saved.deck.length){deck=[...saved.deck];seenFamilies=Array.isArray(saved.seenFamilies)?saved.seenFamilies.filter(family=>openingScenes.some(scene=>scene.lead===family)):[];}}}catch{}
 const shuffle=()=>{const result=[...openings];for(let i=result.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[result[i],result[j]]=[result[j],result[i]];}return result;};
 if(!deck.length){deck=shuffle();seenFamilies=[];}
 let choice;
 if(openingScenes.some(scene=>scene.id===requested)){
  // A review link selects its first frame and consumes it from the current deck.
  choice=requested;deck=deck.filter(id=>id!==choice);
 }else{
  const lastLead=lead(current||last);
  const counts={};for(const id of deck)counts[lead(id)]=(counts[lead(id)]||0)+1;
  let candidates=deck.filter(id=>id!==current&&id!==last&&lead(id)!==lastLead);
  if(!candidates.length)candidates=deck.filter(id=>id!==current&&id!==last);
  if(!candidates.length)candidates=deck.filter(id=>id!==current);
  // Keep a valid alternating remainder without pushing rarer photographs to the end.
  const rest=deck.length-1;
  const feasible=candidates.filter(id=>Object.entries(counts).every(([family,n])=>{
   const remaining=n-(family===lead(id)?1:0);
   return remaining<=(family===lead(id)?Math.floor(rest/2):Math.ceil(rest/2));
  }));
  if(feasible.length)candidates=feasible;
  const fresh=candidates.filter(id=>!seenFamilies.includes(lead(id)));
  if(fresh.length)candidates=fresh;else seenFamilies=[];
  let next=deck.findIndex(id=>candidates.includes(id));
  if(next<0){deck=shuffle();next=deck.findIndex(id=>id!==current);}
  choice=deck.splice(Math.max(0,next),1)[0];
 }
 if(!seenFamilies.includes(lead(choice)))seenFamilies.push(lead(choice));
 openingDeckMemory={catalogue,deck,last:choice,seenFamilies};
 try{localStorage.setItem(key,JSON.stringify(openingDeckMemory));}catch{}
 return choice;
}
