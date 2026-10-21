(() => {
  function connect(host, rows, select){
    if(!rows.length){host.textContent='선택 가능한 공연 회차가 없습니다.';return;}
    const apply=day=>{const previous=select.value;select.replaceChildren(...rows.filter(r=>r.day===day).map(r=>new Option(`${r.time}`,r.id)));if([...select.options].some(o=>o.value===previous))select.value=previous;select.dispatchEvent(new Event('change',{bubbles:true}));};
    let selected=rows.find(r=>r.id===select.value)?.day||rows[0].day;apply(selected);
    LinkCalendar.mount(host,{initial:selected,selected:()=>selected,available:day=>rows.some(r=>r.day===day),choose:day=>{selected=day;apply(day);}});
  }
  const detail=document.querySelector('[data-detail-calendar]');
  if(detail)connect(detail,JSON.parse(document.getElementById('detail-schedules').textContent),document.querySelector('[data-booking-schedule]'));
  const quick=document.querySelector('[data-quick-performance]');
  if(quick){let generation=0;quick.addEventListener('change',async()=>{
    const id=++generation,host=document.querySelector('[data-quick-calendar]'),select=document.querySelector('[data-quick-schedule]'),submit=document.querySelector('[data-quick-submit]');
    select.replaceChildren();submit.disabled=true;host.replaceChildren();if(!quick.value)return;
    try{const response=await fetch(`/performance/${encodeURIComponent(quick.value)}/booking-options/`);if(!response.ok)throw Error();const data=await response.json();if(id!==generation)return;connect(host,data.dates,select);submit.disabled=!data.dates.length;}
    catch(_){if(id===generation)host.textContent='선택 가능한 회차가 없습니다.';}
  });}
})();
