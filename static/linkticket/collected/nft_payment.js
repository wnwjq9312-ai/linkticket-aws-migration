const uiRoutes=JSON.parse(document.getElementById('ui-routes').textContent);
function doSearch(){
    var keyword = document.getElementById('searchInput').value.trim();
    if(!keyword){ alert('검색어를 입력해주세요.'); return; }
    window.location.href = uiRoutes.performances+'?q=' + encodeURIComponent(keyword);
  }

  // 카드번호 입력: 숫자만 받아서 4자리씩 " - "로 자동 구분 (최대 16자리)
  function formatCardNumber(el){
    var digits = el.value.replace(/\D/g,'').slice(0,16);
    var groups = digits.match(/.{1,4}/g) || [];
    el.value = groups.join(' - ');
  }

  // 유효기간 입력: 숫자만 받아서 MM / YY 형식으로 자동 구분, 월은 01~12로 보정
  function formatExpiry(el){
    var digits = el.value.replace(/\D/g,'').slice(0,4);
    var mm = digits.slice(0,2);
    var yy = digits.slice(2,4);
    if(mm.length === 2){
      var mmNum = parseInt(mm,10);
      if(mmNum === 0) mm = '01';
      else if(mmNum > 12) mm = '12';
    }
    el.value = yy.length > 0 ? (mm + ' / ' + yy) : mm;
  }

  // 결제 동의 전체선택
  function toggleAll(el){
    document.querySelectorAll('.agree-list input[type=checkbox]').forEach(function(cb){ cb.checked = el.checked; });
  }
  document.querySelectorAll('.agree-list input[type=checkbox]:not(#agreeAll)').forEach(function(cb){
    cb.addEventListener('change', function(){
      var all = document.querySelectorAll('.agree-list input[type=checkbox]:not(#agreeAll)');
      var checked = document.querySelectorAll('.agree-list input[type=checkbox]:not(#agreeAll):checked');
      document.getElementById('agreeAll').checked = (all.length === checked.length);
    });
  });

  // 카드사 / 결제수단 선택 시 active 스타일 전환
  document.querySelectorAll('.card-opt').forEach(function(opt){
    opt.addEventListener('click', function(){
      document.querySelectorAll('.card-opt').forEach(function(o){ o.classList.remove('active'); });
      opt.classList.add('active');
    });
  });
  document.querySelectorAll('.pay-method').forEach(function(m){
    m.addEventListener('click', function(){
      document.querySelectorAll('.pay-method').forEach(function(o){ o.classList.remove('active'); });
      m.classList.add('active');

      // 결제수단 탭에 맞는 패널로 전환 (카드결제 / 간편결제 / 가상자산결제)
      var method = m.getAttribute('data-method');
      document.querySelectorAll('.method-panel').forEach(function(p){ p.classList.remove('active'); });
      document.getElementById('panel-' + method).classList.add('active');
    });
  });
  document.querySelectorAll('.easypay-opt').forEach(function(opt){
    opt.addEventListener('click', function(){
      document.querySelectorAll('.easypay-opt').forEach(function(o){ o.classList.remove('active'); });
      opt.classList.add('active');
    });
  });
  document.querySelectorAll('.bank-opt').forEach(function(opt){
    opt.addEventListener('click', function(){
      document.querySelectorAll('.bank-opt').forEach(function(o){ o.classList.remove('active'); });
      opt.classList.add('active');
    });
  });

  // /nft/ 카드 8개와 1:1 매칭되는 더미 데이터 (실제로는 DB에서 조회)
  var nftData = {
    "1": { badge:"LIMITED", title:"IU", subtitle:"THE WINNING NFT", date:"2026.11.02 (월) 19:00", venue:"고척스카이돔", type:"일반석 NFT", seat:"스탠딩 A구역", supply:"1,000개 (한정판)", price:150000, media:"media-1" },
    "2": { badge:"LIMITED", title:"SEVENTEEN", subtitle:"RIGHT HERE WORLD TOUR", date:"2026.09.20 (일) 18:00", venue:"잠실종합운동장", type:"VIP NFT", seat:"VIP석", supply:"2,000개 (한정판)", price:120000, media:"media-2" },
    "3": { badge:"LIMITED", title:"aespa", subtitle:"SYNK : PARALLEL LINE", date:"2026.10.05 (월) 19:30", venue:"KSPO DOME", type:"일반석 NFT", seat:"지정석", supply:"1,500개 (한정판)", price:130000, media:"media-3" },
    "4": { badge:"LIMITED", title:"임영웅", subtitle:"IM HERO TOUR 2026", date:"2026.12.12 (토) 18:00", venue:"고척스카이돔", type:"일반석 NFT", seat:"스탠딩", supply:"1,000개 (한정판)", price:200000, media:"media-4" },
    "5": { badge:"LIMITED", title:"뮤지컬 위키드", subtitle:"ORIGINAL NFT", date:"2026.08.15 (토) 14:00", venue:"블루스퀘어", type:"관람석 NFT", seat:"R석", supply:"800개 (한정판)", price:180000, media:"media-5" },
    "6": { badge:"LIMITED", title:"서울 뮤직 페스티벌", subtitle:"SEOUL 2026", date:"2026.07.25 (토) ~ 26 (일)", venue:"서울월드컵경기장", type:"종합이용권 NFT", seat:"스탠딩", supply:"2,500개 (한정판)", price:90000, media:"media-6" },
    "7": { badge:"LIMITED", title:"NCT DREAM", subtitle:"THE DREAM SHOW 3", date:"2026.10.15 (목) 19:00", venue:"서울 월드컵 경기장", type:"일반석 NFT", seat:"스탠딩 A구역", supply:"1,000개 (한정판)", price:100000, media:"media-7" },
    "8": { badge:"COMING SOON", title:"스페셜 컬렉션", subtitle:"COMING SOON", date:"미정", venue:"미정", type:"미정", seat:"미정", supply:"수량 미정", price:0, media:"media-8" }
  };

  var params = new URLSearchParams(window.location.search);
  var id = params.get('id') || "7";
  var data = nftData[id] || nftData["7"];

  // 좌측 상품 카드
  document.getElementById('productMedia').classList.add(data.media);
  document.getElementById('productBadge').textContent = data.badge;
  document.getElementById('productMediaName').textContent = data.title;
  document.getElementById('productTitle').textContent = data.title;
  document.getElementById('productSubtitle').textContent = data.subtitle;
  document.getElementById('productDate').textContent = data.date;
  document.getElementById('productVenue').textContent = data.venue;
  document.getElementById('productType').textContent = data.type;
  document.getElementById('productSeat').textContent = data.seat;
  document.getElementById('productSupply').textContent = data.supply;

  // 우측 결제 정보 요약
  document.getElementById('orderMedia').classList.add(data.media);
  document.getElementById('orderTitle').textContent = data.title;
  document.getElementById('orderSub').textContent = data.subtitle;
  document.getElementById('orderBadge').textContent = data.badge;
  document.getElementById('sumDate').textContent = data.date;
  document.getElementById('sumVenue').textContent = data.venue;
  document.getElementById('sumSeat').textContent = data.seat;
  document.getElementById('sumType').textContent = data.type;
  document.title = "LINKTICKET - " + data.title + " NFT 결제";

  // 가격 계산: 수수료/부가세 각각 티켓가의 5%로 계산 (실제 정책은 DB/결제 담당과 협의 필요)
  var fee = data.price > 0 ? Math.round(data.price * 0.05) : 0;
  var vat = data.price > 0 ? Math.round(data.price * 0.05) : 0;
  var final = data.price + fee + vat;

  document.getElementById('priceBase').textContent = data.price > 0 ? ('₩' + data.price.toLocaleString()) : '준비중';
  document.getElementById('priceFee').textContent = '₩' + fee.toLocaleString();
  document.getElementById('priceVat').textContent = '₩' + vat.toLocaleString();
  document.getElementById('priceFinal').textContent = data.price > 0 ? ('₩' + final.toLocaleString()) : '-';
  document.getElementById('payBtnPrice').textContent = data.price > 0 ? ('₩' + final.toLocaleString()) : '준비중';

  // "COMING SOON" 항목은 아직 구매 불가 처리
  if(data.price === 0){
    document.getElementById('payBtn').disabled = true;
    document.getElementById('payBtnPrice').textContent = '준비중인 컬렉션입니다';
  }

  // 09:52부터 카운트다운 (실제로는 서버에서 내려준 만료시각 기준으로 계산해야 함)
  var totalSeconds = 9*60 + 52;
  setInterval(function(){
    if(totalSeconds <= 0) return;
    totalSeconds--;
    var m = Math.floor(totalSeconds/60);
    var s = totalSeconds%60;
    document.getElementById('timer').textContent = (m<10?'0':'')+m + ':' + (s<10?'0':'')+s;
  }, 1000);

  // 결제하기: 실제 PG/DB 연동이 없는 프로젝트라, 결제 성공/실패 판정 자체를 프론트에서
  // "그럴듯하게" 흉내만 내는 시뮬레이션. 실제 서비스에서는 이 판정을 백엔드(PG 응답)가 내려주고
  // 프론트는 그 결과를 보여주기만 하면 된다.
  function submitPayment(){
    var requiredChecked = document.querySelectorAll('.agree-req:checked').length;
    if(requiredChecked < document.querySelectorAll('.agree-req').length){
      alert('필수 약관에 모두 동의해주세요.');
      return;
    }

    // 현재 선택된 결제수단 확인
    var activeMethodEl = document.querySelector('.pay-method.active');
    var method = activeMethodEl ? activeMethodEl.getAttribute('data-method') : 'card';
    var methodLabel = '';
    var cardNumberEmpty = false;

    if(method === 'card'){
      var cardOpt = document.querySelector('#panel-card .card-opt.active');
      methodLabel = (cardOpt ? cardOpt.textContent.trim() : '카드') + ' (일반결제)';
      var cardNumberInput = document.getElementById('cardNumberInput');
      var cardExpiryInput = document.getElementById('cardExpiryInput');
      var cardDigits = cardNumberInput ? cardNumberInput.value.replace(/\D/g,'') : '';
      var expiryDigits = cardExpiryInput ? cardExpiryInput.value.replace(/\D/g,'') : '';
      cardNumberEmpty = cardDigits.length < 16 || expiryDigits.length < 4;
    } else if(method === 'easy'){
      var easyOpt = document.querySelector('#panel-easy .easypay-opt.active div');
      methodLabel = (easyOpt ? easyOpt.textContent.trim() : '간편결제');
    } else if(method === 'vaccount'){
      var bankOpt = document.querySelector('#panel-vaccount .bank-opt.active');
      var bankName = bankOpt ? bankOpt.textContent.trim() : '가상계좌';
      methodLabel = bankName + ' (가상계좌)';

      alert('Mock 가상계좌 선택입니다. 실제 계좌 발급이나 입금은 진행되지 않습니다.');
    }

    // "결제 처리 중" 알림 -> 확인을 누르면 성공/실패 판정으로 이어지는 흐름
    // (가상계좌는 위에서 이미 계좌 발급 안내를 보여줬으므로 별도 처리중 알림은 생략)
    if(method !== 'vaccount'){
      alert('Mock 결제를 확인합니다. 실제 결제는 발생하지 않습니다.');
    }

    // 결제 실패 시나리오 데모: 카드결제인데 카드번호를 안 넣은 경우는 실패로 처리.
    // 그 외(카드/간편결제)에는 약 10% 확률로 랜덤 실패시켜 실패 화면도 확인할 수 있게 해둠 (테스트용).
    // 가상계좌는 "입금 대기" 개념이라 이 데모에서는 발급 즉시 성공으로 처리.
    var isFail = (method === 'card' && cardNumberEmpty) || false;

    if(isFail){
      alert('결제에 실패했습니다. 카드 정보/한도 또는 네트워크 상태를 확인한 뒤 다시 시도해주세요.');
      location.reload();
      return;
    }

    var currentParams = new URLSearchParams(window.location.search);
    var idParam = currentParams.get('id') || '7';
    document.querySelectorAll('.collected-page input').forEach(input => { if (input.type !== 'checkbox' && input.type !== 'radio') input.value = ''; });
    window.location.href = uiRoutes.nftComplete+'?id=' + idParam + '&method=' + encodeURIComponent(methodLabel);
  }
