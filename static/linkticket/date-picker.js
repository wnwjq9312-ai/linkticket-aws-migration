/* Shared calendar renderer. ISO inputs and existing POST contracts stay intact. */
(() => {
  const pad=n=>String(n).padStart(2,'0'),iso=d=>`${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  window.LinkCalendar={mount(host, options={}) {
    let month=new Date((options.initial||iso(new Date())).slice(0,7)+'-01T12:00:00');
    const draw=()=>{
      host.replaceChildren();host.classList.add('booking-calendar');
      const head=document.createElement('div');head.className='calendar-heading';
      [-1,0,1].forEach(step=>{const el=document.createElement(step?'button':'strong');
        if(step){el.type='button';el.textContent=step<0?'‹':'›';el.setAttribute('aria-label',step<0?'이전 달':'다음 달');el.onclick=()=>{month.setMonth(month.getMonth()+step);draw();};}
        else{el.textContent=`${month.getFullYear()}년 ${month.getMonth()+1}월`;el.setAttribute('aria-live','polite');}head.append(el);});
      host.append(head);const grid=document.createElement('div');grid.className='calendar-grid';
      ['일','월','화','수','목','금','토'].forEach(text=>{const el=document.createElement('small');el.textContent=text;grid.append(el);});
      for(let i=0;i<month.getDay();i++)grid.append(document.createElement('span'));
      const selected=options.selected?.();
      for(let day=1;day<=new Date(month.getFullYear(),month.getMonth()+1,0).getDate();day++){
        const key=iso(new Date(month.getFullYear(),month.getMonth(),day)), b=document.createElement('button');
        b.type='button';b.className='calendar-day';b.dataset.day=key;b.textContent=day;
        b.disabled=options.available ? !options.available(key) : false;
        b.classList.toggle('selected',key===selected);b.classList.toggle('today',key===iso(new Date()));
        b.setAttribute('aria-label',key+(b.disabled?' 선택 불가':''));b.setAttribute('aria-pressed',String(key===selected));
        if(key===iso(new Date()))b.setAttribute('aria-current','date');
        b.onclick=()=>{options.choose?.(key);draw();};grid.append(b);
      }
      host.append(grid);const legend=document.createElement('p');legend.className='calendar-legend';legend.textContent='■ 선택 날짜　○ 오늘　· 회색: 선택 불가';host.append(legend);
    };
    draw();return {refresh:draw,show(date){month=new Date(date.slice(0,7)+'-01T12:00:00');draw();}};
  }};
  document.querySelectorAll('input[type=date],input[type=datetime-local]').forEach(input=>{
    const wrapper=document.createElement('span');wrapper.className='date-control';input.before(wrapper);wrapper.append(input);
    const button=document.createElement('button');button.type='button';button.className='date-open';button.textContent='▦';button.setAttribute('aria-label','달력 열기');wrapper.append(button);
    const dialog=document.createElement('dialog');dialog.className='date-dialog';const title=document.createElement('h2');title.textContent='날짜 선택';
    const host=document.createElement('div'),close=document.createElement('button');close.type='button';close.textContent='닫기';close.onclick=()=>dialog.close();dialog.append(title,host,close);document.body.append(dialog);
    button.onclick=()=>{
      if(input.disabled||input.readOnly)return;
      LinkCalendar.mount(host,{initial:input.value||undefined,selected:()=>input.value.slice(0,10),available:key=>(!input.min||key>=input.min.slice(0,10))&&(!input.max||key<=input.max.slice(0,10)),choose:key=>{const time=input.value.split('T')[1]||'00:00';input.value=key+(input.type==='datetime-local'?'T'+time:'');input.dispatchEvent(new Event('input',{bubbles:true}));input.dispatchEvent(new Event('change',{bubbles:true}));dialog.close();}});
      dialog.showModal();
    };
    dialog.addEventListener('close',()=>button.focus());
  });
})();
