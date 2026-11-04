const openings=openingScenes.map(scene=>scene.id);
function chooseOpening(){
 const requested=new URLSearchParams(location.search).get('study');
 if(openings.includes(requested))return requested;
 const catalogue=openings.join('|'),key='opening-deck-v3';let deck=[],last;
 try{const saved=JSON.parse(localStorage.getItem(key));if(saved){last=saved.last;if(saved.catalogue===catalogue&&Array.isArray(saved.deck)&&saved.deck.every(id=>openings.includes(id))&&new Set(saved.deck).size===saved.deck.length)deck=saved.deck;}}catch{}
 if(!deck.length){deck=[...openings];for(let i=deck.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[deck[i],deck[j]]=[deck[j],deck[i]];}if(deck.length>1&&deck[0]===last)[deck[0],deck[1]]=[deck[1],deck[0]];}
 const choice=deck.shift();try{localStorage.setItem(key,JSON.stringify({catalogue,deck,last:choice}));}catch{}return choice;
}
