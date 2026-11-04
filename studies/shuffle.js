// Only compositions that have passed contour and native-resolution checks belong here.
const openings = ['eclipse-arc', 'common-arc'];
function chooseOpening() {
  const requested = new URLSearchParams(location.search).get('study');
  if (openings.includes(requested)) return requested;
  let deck = [], last;
  const key = 'opening-deck-v2';
  try {
    const saved = JSON.parse(localStorage.getItem(key));
    if (saved && Array.isArray(saved.deck) && saved.deck.every(id => openings.includes(id))) {
      deck = saved.deck; last = saved.last;
    }
  } catch {}
  if (!deck.length) {
    deck = [...openings];
    for (let i=deck.length-1;i>0;i--) {const j=Math.floor(Math.random()*(i+1));[deck[i],deck[j]]=[deck[j],deck[i]];}
    if (deck.length>1 && deck[0]===last) [deck[0],deck[1]]=[deck[1],deck[0]];
  }
  const choice=deck.shift();
  try {localStorage.setItem(key,JSON.stringify({deck,last:choice}));} catch {}
  return choice;
}
