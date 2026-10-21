(() => {
 const host=document.querySelector('[data-calendar]');if(!host)return;
 const rows=JSON.parse(document.getElementById('payment-config').textContent).calendar;
 const buttons=[...document.querySelectorAll('.lt-dates [data-date]')];
 const selected=()=>rows.find(r=>buttons.find(b=>b.dataset.date===r.id)?.classList.contains('active'))?.day;
 const calendar=LinkCalendar.mount(host,{initial:selected()||rows[0].day,selected,available:key=>rows.some(r=>r.day===key),choose:key=>buttons.find(b=>b.dataset.date===rows.find(r=>r.day===key).id).click()});
 function filter(){buttons.forEach(b=>b.hidden=rows.find(r=>r.id===b.dataset.date).day!==selected());}
 buttons.forEach(b=>b.addEventListener('click',()=>{calendar.show(selected());filter();}));filter();
})();
