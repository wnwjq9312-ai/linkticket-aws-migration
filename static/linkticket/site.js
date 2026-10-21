(() => {
  document.querySelector('[data-booking-link]')?.addEventListener('click',function(){const url=new URL(this.href);url.searchParams.set('schedule',document.querySelector('[data-booking-schedule]').value);this.href=url.href;});
  const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
  function info(text) { const dialog=$('#site-dialog');dialog.querySelector('p').textContent=text;dialog.showModal(); }
  function toast(text) { const el=$('.site-toast');el.textContent=text;el.classList.add('visible');clearTimeout(el.timer);el.timer=setTimeout(()=>el.classList.remove('visible'),3500); }
  $('[data-close-dialog]')?.addEventListener('click',()=>$('#site-dialog').close());
  $$('[data-info]').forEach(el=>el.addEventListener('click',()=>info(el.dataset.info)));
  $$('[data-password]').forEach(el=>el.addEventListener('click',()=>{const input=document.getElementById(el.dataset.password);input.type=input.type==='password'?'text':'password';el.setAttribute('aria-pressed',String(input.type==='text'));}));
  $('[data-all-terms]')?.addEventListener('change',e=>$$('[data-term]').forEach(x=>x.checked=e.target.checked));
  $$('[data-term]').forEach(el=>el.addEventListener('change',()=>{const checked=$$('[data-term]').filter(x=>x.checked).length;const all=$('[data-all-terms]');all.checked=checked===$$('[data-term]').length;all.indeterminate=checked>0&&!all.checked;}));
  $$('[data-check]').forEach(el=>el.addEventListener('click',async()=>{const field=el.dataset.check;const value=document.getElementById('signup-'+field).value;try{const res=await fetch(el.dataset.url+'?'+field+'='+encodeURIComponent(value));const data=await res.json();toast(data.message||'확인하지 못했습니다.');}catch{toast('연결을 확인해주세요.');}}));
  let favorites=[];try{favorites=JSON.parse(localStorage.getItem('linkticket.favorites')||'[]');if(!Array.isArray(favorites))favorites=[];}catch{}
  function refreshFavorites(){ $$('[data-favorite]').forEach(el=>{const active=favorites.includes(el.dataset.favorite);el.setAttribute('aria-pressed',String(active));el.textContent=active?'♥':'♡';});$$('[data-interest-card]').forEach(el=>el.hidden=!favorites.includes(el.dataset.interestCard)); }
  $$('[data-favorite]').forEach(el=>el.addEventListener('click',()=>{const id=el.dataset.favorite;favorites=favorites.includes(id)?favorites.filter(x=>x!==id):[...favorites,id];try{localStorage.setItem('linkticket.favorites',JSON.stringify(favorites));}catch{}refreshFavorites();}));refreshFavorites();
  $$('[data-share-page]').forEach(el=>el.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);toast('페이지 주소를 복사했습니다.');}catch{info(location.href);}}));
  $$('[data-slide]').forEach(el=>el.addEventListener('click',()=>{const titles=['특별한 순간,','음악이 만드는 순간,','함께하는 즐거움,'];const hero=$('.home-hero');hero.querySelector('h1').firstChild.textContent=titles[Number(el.dataset.slide)];$$('[data-slide]').forEach(b=>b.style.borderColor=b===el?'#2cb7ff':'transparent');}));
  $$('[data-cancel-reservation]').forEach(el=>el.addEventListener('click',async()=>{if(!confirm('이 예매를 취소하시겠습니까?'))return;const token=document.cookie.match(/csrftoken=([^;]+)/)?.[1]||'';try{const response=await fetch(el.dataset.cancelReservation,{method:'POST',headers:{'X-CSRFToken':decodeURIComponent(token)}});if(!response.ok)throw Error();location.reload();}catch{info('예매 취소를 처리하지 못했습니다. 상태를 확인해주세요.');}}));
})();
