(() => {
  'use strict';
  const config = JSON.parse(document.getElementById('payment-config').textContent);
  const $ = (s) => document.querySelector(s), $$ = (s) => [...document.querySelectorAll(s)];
  const storageKey = 'linkticket.payment.demo.v3.' + config.performanceId;
  const defaultState = () => ({date:Object.keys(config.dates)[0], grade:Object.keys(config.prices)[0], seats:[], discount:'none'});
  const dates = config.dates;
  let seatData = config.scheduleSeats?.[Object.keys(config.dates)[0]] || config.seats;
  const labelFor=id=>seatData[id]?.label||id;
  const priceFor=id=>seatData[id]?.price ?? config.prices[state.grade];
  const isAvailable = (id, grade) => seatData[id]?.status === 'available' && seatData[id].grade === grade;
  let state = defaultState();
  try { const saved = JSON.parse(sessionStorage.getItem(storageKey));
    if (saved && dates[saved.date] && Object.hasOwn(config.prices,saved.grade) && ['none','youth','coupon'].includes(saved.discount) && Array.isArray(saved.seats)) {
      seatData = config.scheduleSeats?.[saved.date] || config.seats;
      state = {...saved, seats:[...new Set(saved.seats)].filter(id => {if(typeof id !== 'string' || !Object.hasOwn(seatData,id)) return false; return true;}).slice(0,config.maxSeats)};
    }
  } catch (_) { /* Private browsing or stale demo data: use defaults. */ }
  if(config.initialSchedule && state.date !== config.initialSchedule){state.date=config.initialSchedule;state.seats=[];}
  const money = n => n.toLocaleString('ko-KR')+'원';
  let toastTimer;
  function toast(text) {const el=$('.lt-toast');el.textContent=text;el.classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('visible'),3500);}
  function modal(title,text) {$('#dialog-title').textContent=title;$('#dialog-text').textContent=text;$('.lt-dialog').showModal();}
  function save(){try{sessionStorage.setItem(storageKey,JSON.stringify(state));}catch(_){toast('브라우저 저장이 제한되어 페이지 이동 시 선택 정보가 초기화될 수 있습니다.');}}
  function totals(){const subtotal=state.seats.reduce((sum,id)=>sum+priceFor(id),0);const discount=state.discount==='youth'?Math.floor(subtotal*.2):state.discount==='coupon'?Math.min(subtotal,10000):0;const fee=state.seats.length*config.fee;return {subtotal,discount,fee,total:subtotal-discount+fee};}
  function render(){
    seatData=config.scheduleSeats?.[state.date] || config.seats;
    if(Object.values(seatData).length&&!Object.values(seatData).some(s=>s.grade===state.grade))state.grade=Object.values(seatData)[0].grade;
    state.seats=state.seats.filter(id=>isAvailable(id,state.grade));
    buildGrid();
    const t=totals();
    for(const [attr,value] of Object.entries({'subtotal':t.subtotal,'discount-total':t.discount,'fee':t.fee,'total':t.total})) $$('[data-'+attr+']').forEach(el=>el.textContent=(attr==='discount-total'&&value?'-':'')+money(value));
    $$('[data-date-summary]').forEach(el=>el.textContent=dates[state.date]);
    $$('[data-date]').forEach(el=>{const active=el.dataset.date===state.date;el.classList.toggle('active',active);el.setAttribute('aria-pressed',String(active));});
    $$('[data-grade]').forEach(el=>{el.disabled=!Object.values(seatData).some(s=>s.grade===el.dataset.grade);const cost=el.querySelector('[data-money]');const match=Object.values(seatData).find(s=>s.grade===el.dataset.grade);if(cost&&match?.price!==undefined)cost.textContent=money(match.price);const active=el.dataset.grade===state.grade;el.classList.toggle('active',active);el.setAttribute('aria-pressed',String(active));});
    $$('[data-discount]').forEach(el=>el.value=state.discount);
    $$('[data-seat]').forEach(el=>{
      const info=seatData[el.dataset.seat], selected=state.seats.includes(el.dataset.seat);
      const other=info.grade!==state.grade;
      el.disabled=info.status!=='available'||other;
      el.classList.toggle('other-grade',other&&info.status==='available');
      el.classList.toggle('selected',selected);
      el.setAttribute('aria-pressed',String(selected));
      const status=info.status==='reserved'?'예매 완료':info.status==='unavailable'?'선택 불가':other?'다른 등급':selected?'선택됨':'선택 가능';
      el.setAttribute('aria-label',`${info.label} ${info.grade}석 ${status}`);
      el.title=el.getAttribute('aria-label');
    });
    $$('[data-remaining]').forEach(el=>el.textContent='잔여 '+Object.values(seatData).filter(s=>s.grade===el.dataset.remaining&&s.status==='available').length+'석');
    if($('[data-quantity]')) $('[data-quantity]').textContent=state.seats.length+'매';
    if($('[data-seat-summary]')) $('[data-seat-summary]').textContent=state.seats.length?state.seats.map(id=>{const [r,c]=id.split('-');return `${state.grade}석 · ${labelFor(id)}`;}).join(', '):'선택한 좌석 없음';
    const container=$('[data-selected-seats]');
    if(container){container.replaceChildren();if(!state.seats.length){const p=document.createElement('p');p.textContent='좌석을 선택해주세요.';container.append(p);}state.seats.forEach(id=>{const [r,c]=id.split('-');const item=document.createElement('div');item.className='lt-seat-item';const dot=document.createElement('i');dot.textContent='●';const label=document.createElement('span');label.textContent=labelFor(id);const price=document.createElement('small');price.textContent=`${state.grade}석  ${money(priceFor(id))}`;label.append(price);const remove=document.createElement('button');remove.textContent='×';remove.setAttribute('aria-label',`${labelFor(id)} 선택 해제`);remove.addEventListener('click',()=>{state.seats=state.seats.filter(s=>s!==id);save();render();});item.append(dot,label,remove);container.append(item);});}
  }
  $$('[data-money]').forEach(el=>el.textContent=money(Number(el.dataset.money)));
  const grid=$('.lt-seat-grid');
  let gridDate;
  function buildGrid(){
    if(!grid||gridDate===state.date)return;gridDate=state.date;grid.replaceChildren();
    Object.entries(seatData).forEach(([id,info])=>{
    const seat=document.createElement('button');seat.type='button';seat.className='lt-seat';seat.dataset.seat=id;seat.dataset.seatGrade=info.grade;seat.title=info.label;
    seat.classList.toggle('reserved',info.status==='reserved');
    seat.addEventListener('click',()=>{
      if(!isAvailable(id,state.grade))return;
      if(state.seats.includes(id))state.seats=state.seats.filter(s=>s!==id);
      else if(state.seats.length<config.maxSeats)state.seats.push(id);
      else return toast('최대 4매까지 선택할 수 있습니다.');
      save();render();
    });grid.append(seat);
  });
    if(!Object.keys(seatData).length){const message=document.createElement('p');message.className='empty-state';message.textContent='등록된 좌석이 없습니다.';grid.append(message);}
  }
  $$('[data-date]').forEach(el=>el.addEventListener('click',()=>{if(state.date!==el.dataset.date){state.date=el.dataset.date;state.seats=[];const next=config.scheduleSeats?.[state.date];if(next&&Object.values(next).length)state.grade=Object.values(next)[0].grade;toast('관람일이 변경되었습니다. 좌석을 다시 선택해주세요.');save();render();}}));
  $$('[data-grade]').forEach(el=>el.addEventListener('click',()=>{if(state.grade!==el.dataset.grade){state.grade=el.dataset.grade;state.seats=[];toast('등급이 변경되어 기존 선택 좌석을 해제했습니다. 새 등급 좌석을 선택해주세요.');save();render();}}));
  $$('[data-discount]').forEach(el=>el.addEventListener('change',()=>{state.discount=el.value;save();render();}));
  $('[data-reset]')?.addEventListener('click',()=>{state.seats=[];save();render();});
  $('[data-next]')?.addEventListener('click',e=>{if(!state.seats.length){e.preventDefault();toast('좌석을 1개 이상 선택해주세요.');}else save();});
  $$('[data-demo]').forEach(el=>el.addEventListener('click',()=>toast('이 기능은 백엔드 연결 예정입니다. 현재는 Mock 예매 체험만 지원합니다.')));
  $$('[data-like]').forEach(el=>el.addEventListener('click',()=>{const pressed=el.getAttribute('aria-pressed')==='true';el.setAttribute('aria-pressed',String(!pressed));el.textContent=pressed?'♡ 찜하기':'♥ 찜 완료';toast(pressed?'찜을 해제했습니다.':'찜 목록에 담았습니다. (현재 화면 데모)');}));
  $$('[data-share]').forEach(el=>el.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);toast('현재 페이지 주소를 복사했습니다.');}catch(_){modal('공유하기',location.href);}}));
  $('[data-seat-help]')?.addEventListener('click',()=>modal('좌석 선택 안내','선택한 등급의 진한 색 좌석만 선택할 수 있습니다. 파란색은 현재 선택, 사선은 다른 등급, 분홍색 ×는 예매 완료입니다. 최대 4매까지 선택할 수 있습니다.\n잔여 수량과 좌석 배치는 임시 데이터입니다. 실제 좌석을 확보하지 않습니다.'));
  let zoom=1;$$('[data-zoom]').forEach(el=>el.addEventListener('click',()=>{zoom=el.dataset.zoom==='reset'?1:Math.min(1.5,Math.max(.8,zoom+(el.dataset.zoom==='in'?.1:-.1)));grid.style.transform=`scale(${zoom})`;}));

  const cardInputs=$$('[data-card-input]');
  const digits=value=>value.replace(/[^0-9]/g,'');
  function clearCard(){cardInputs.forEach(el=>{el.value='';el.removeAttribute('aria-invalid');$('[data-card-error="'+el.dataset.cardInput+'"]').textContent='';});}
  function setCardMode(active){
    $('[data-card-panel]').hidden=!active;
    cardInputs.forEach(el=>el.disabled=!active);
    if(!active)clearCard();
  }
  function cardError(el){
    const value=el.value.trim();
    if(!value)return '필수 입력 항목입니다.';
    if(el.dataset.cardInput==='number'&&!/^\d{4} \d{4} \d{4} \d{4}$/.test(value))return '숫자 16자리를 입력해주세요.';
    if(el.dataset.cardInput==='expiry'&&!/^(0[1-9]|1[0-2])\/\d{2}$/.test(value))return 'MM/YY 형식과 월(01~12)을 확인해주세요.';
    if(el.dataset.cardInput==='cvc'&&!/^\d{3,4}$/.test(value))return '숫자 3~4자리를 입력해주세요.';
    return '';
  }
  function showCardError(el){const message=cardError(el);el.setAttribute('aria-invalid',String(!!message));$('[data-card-error="'+el.dataset.cardInput+'"]').textContent=message;return !message;}
  function validateCard(){let first;cardInputs.forEach(el=>{if(!showCardError(el)&&!first)first=el;});first?.focus();return !first;}
  cardInputs.forEach(el=>{
    el.addEventListener('input',()=>{
      if(el.dataset.cardInput==='number')el.value=digits(el.value).slice(0,16).replace(/(.{4})(?=.)/g,'$1 ');
      if(el.dataset.cardInput==='expiry'){const d=digits(el.value).slice(0,4);el.value=d.length>2?d.slice(0,2)+'/'+d.slice(2):d;}
      if(el.dataset.cardInput==='cvc')el.value=digits(el.value).slice(0,4);
      if(el.getAttribute('aria-invalid')==='true')showCardError(el);
    });
    el.addEventListener('blur',()=>showCardError(el));
  });
  if($('[data-card-panel]'))setCardMode(false);
  window.addEventListener('pagehide',clearCard);
  window.addEventListener('pageshow',event=>{if(event.persisted)clearCard();});

  let method='';
  $$('[data-method]').forEach(el=>el.addEventListener('click',()=>{method=el.dataset.method;$$('[data-method]').forEach(b=>{b.classList.toggle('active',b===el);b.setAttribute('aria-pressed',String(b===el));});setCardMode(method==='신용카드');$('.lt-alt-method').hidden=method==='신용카드';$('[data-method-title]').textContent=method+' · 모의 결제';}));
  const required=$$('[data-required]');
  $('[data-all]')?.addEventListener('change',e=>required.forEach(el=>el.checked=e.target.checked));
  required.forEach(el=>el.addEventListener('change',()=>{const count=required.filter(c=>c.checked).length;$('[data-all]').checked=count===required.length;$('[data-all]').indeterminate=count>0&&count<required.length;}));
  $$('[data-terms]').forEach(el=>el.addEventListener('click',()=>modal(el.dataset.terms,'프론트엔드 확인용 약관 예시입니다.\n실제 결제, 개인정보 수집 또는 제3자 제공은 진행되지 않습니다. 실제 서비스 연동 시 확정된 약관 원문과 버전을 연결해야 합니다.')));
  function submitMockPayment(event) {
    const error = $('.lt-form-error');
    const form = $('#lt-mock-payment');
    const fail = message => { event.preventDefault(); error.textContent=message; };
    if (!state.seats.length) return fail('이전 단계에서 좌석을 선택해주세요.');
    if (!method) return fail('결제수단을 선택해주세요.');
    if (method==='신용카드' && !validateCard()) return fail('카드 입력 항목을 확인해주세요.');
    if (!required.every(el=>el.checked)) return fail('필수 약관에 모두 동의해주세요.');
    // Populate a normal HTML form. Django owns success/failure navigation.
    const values = {
      date:state.date, grade:state.grade, discount:state.discount,
      seats:JSON.stringify(state.seats), method,
      card:$('input[name="card"]:checked')?.value || '',
      installment:$('[data-installment]').value,
      terms_finance:required[0].checked?'on':'',
      terms_privacy:required[1].checked?'on':'',
      terms_provider:required[2].checked?'on':''
    };
    Object.entries(values).forEach(([name,value])=>{
      let input=form.querySelector(`input[name="${name}"]`);
      if(!input){input=document.createElement('input');input.type='hidden';input.name=name;form.append(input);}
      input.value=value;
    });
    clearCard(); // UI-only fields are never included in the submitted form.
    save();
  }
  $('#lt-mock-payment')?.addEventListener('submit',submitMockPayment);
  $$('[data-complete-info]').forEach(el=>el.addEventListener('click',()=>modal(el.dataset.title,el.dataset.completeInfo)));
  $('[data-close]').addEventListener('click',()=>$('.lt-dialog').close());
  $$('[data-open-payment-dialog]').forEach(button=>button.addEventListener('click',()=>document.getElementById(button.dataset.openPaymentDialog).showModal()));
  $$('.lt-payment-dialog').forEach(dialog=>{
    dialog.querySelector('[data-close-payment-dialog]').addEventListener('click',()=>dialog.close());
    let outsideDown=false;
    const outside=e=>{const r=dialog.getBoundingClientRect();return e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom;};
    dialog.addEventListener('pointerdown',e=>{outsideDown=e.target===dialog&&outside(e);});
    dialog.addEventListener('click',e=>{if(outsideDown&&e.target===dialog&&outside(e))dialog.close();outsideDown=false;});
  });
  render();
})();
