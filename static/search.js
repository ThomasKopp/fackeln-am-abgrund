const input=document.querySelector('#suche');
if(input){
  document.querySelector('.search').hidden=false;
  const cards=[...document.querySelectorAll('.card')];
  const normalize=s=>s.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('de');
  input.addEventListener('input',()=>{
    const term=normalize(input.value.trim());let count=0;
    for(const card of cards){card.hidden=!normalize(card.dataset.search).includes(term);if(!card.hidden)count++;}
    document.querySelector('#suchstatus').textContent=`${count} von ${cards.length} Beiträgen`;
  });
}
