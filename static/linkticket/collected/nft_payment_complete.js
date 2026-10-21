const uiRoutes=JSON.parse(document.getElementById('ui-routes').textContent);
function doSearch(){
    var keyword = document.getElementById('searchInput').value.trim();
    if(!keyword){ alert('검색어를 입력해주세요.'); return; }
    window.location.href = uiRoutes.performances+'?q=' + encodeURIComponent(keyword);
  }

  // /nft/payment/과 동일한 더미 데이터 (실제로는 DB에서 예매/결제 결과를 조회)
  var nftData = {
    "1": { badge:"LIMITED", title:"IU", subtitle:"THE WINNING NFT", date:"2026.11.02 (월) 19:00", venue:"고척스카이돔", seat:"스탠딩 A구역", price:150000, media:"media-1" },
    "2": { badge:"LIMITED", title:"SEVENTEEN", subtitle:"RIGHT HERE WORLD TOUR", date:"2026.09.20 (일) 18:00", venue:"잠실종합운동장", seat:"VIP석", price:120000, media:"media-2" },
    "3": { badge:"LIMITED", title:"aespa", subtitle:"SYNK : PARALLEL LINE", date:"2026.10.05 (월) 19:30", venue:"KSPO DOME", seat:"지정석", price:130000, media:"media-3" },
    "4": { badge:"LIMITED", title:"임영웅", subtitle:"IM HERO TOUR 2026", date:"2026.12.12 (토) 18:00", venue:"고척스카이돔", seat:"스탠딩", price:200000, media:"media-4" },
    "5": { badge:"LIMITED", title:"뮤지컬 위키드", subtitle:"ORIGINAL NFT", date:"2026.08.15 (토) 14:00", venue:"블루스퀘어", seat:"R석", price:180000, media:"media-5" },
    "6": { badge:"LIMITED", title:"서울 뮤직 페스티벌", subtitle:"SEOUL 2026", date:"2026.07.25 (토) ~ 26 (일)", venue:"서울월드컵경기장", seat:"스탠딩", price:90000, media:"media-6" },
    "7": { badge:"LIMITED", title:"NCT DREAM", subtitle:"THE DREAM SHOW 3", date:"2026.10.15 (목) 19:00", venue:"서울 월드컵 경기장", seat:"스탠딩 A구역", price:100000, media:"media-7" },
    "8": { badge:"COMING SOON", title:"스페셜 컬렉션", subtitle:"COMING SOON", date:"미정", venue:"미정", seat:"미정", price:0, media:"media-8" }
  };

  var params = new URLSearchParams(window.location.search);
  var id = params.get('id') || "7";
  var methodParam = params.get('method');
  var data = nftData[id] || nftData["7"];

  document.getElementById('productMedia').classList.add(data.media);
  document.getElementById('productBadge').textContent = data.badge;
  document.getElementById('productMediaName').textContent = data.title;
  document.getElementById('productTitle').textContent = data.title;
  document.getElementById('productSubtitle').textContent = data.subtitle;

  document.getElementById('rsvTitle').textContent = data.title + ' ' + data.subtitle;
  document.getElementById('rsvDate').textContent = data.date;
  document.getElementById('rsvVenue').textContent = data.venue;
  document.getElementById('rsvSeat').textContent = data.seat;
  if(methodParam){ document.getElementById('rsvMethod').textContent = methodParam; }

  var fee = data.price > 0 ? Math.round(data.price * 0.05) : 0;
  var vat = data.price > 0 ? Math.round(data.price * 0.05) : 0;
  var final = data.price + fee + vat;
  document.getElementById('rsvFinal').textContent = '₩' + final.toLocaleString();

  // 예매번호 / 결제일시: 실제로는 DB에서 내려주는 값. 지금은 현재 시각 기준으로 생성
  var now = new Date();
  var pad = function(n){ return (n<10?'0':'')+n; };
  var ymd = now.getFullYear() + '' + pad(now.getMonth()+1) + pad(now.getDate());
  var randNo = String(Math.floor(Math.random()*900000)+100000);
  document.getElementById('rsvId').firstChild.textContent = 'RSV-' + ymd + '-' + randNo + ' ';

  var days = ['일','월','화','수','목','금','토'];
  var paidAt = now.getFullYear() + '.' + pad(now.getMonth()+1) + '.' + pad(now.getDate()) +
    ' (' + days[now.getDay()] + ') ' + pad(now.getHours()) + ':' + pad(now.getMinutes()) + ':' + pad(now.getSeconds());
  document.getElementById('rsvPaidAt').textContent = paidAt;

  function copyRsvId(){
    var text = document.getElementById('rsvId').firstChild.textContent.trim();
    if(navigator.clipboard){ navigator.clipboard.writeText(text); }
    alert('예매번호가 복사되었습니다: ' + text);
  }
  function shareRsv(){
    alert('지금은 화면만 확인하는 단계라, 실제 공유 기능(카카오톡 공유 등)은 백엔드 연결 후 동작합니다.');
  }

  // ===== 이런 공연은 어떠세요? : 현재 구매한 항목을 제외한 나머지 중 4개 =====
  var recGrid = document.getElementById('recGrid');
  var ids = Object.keys(nftData).filter(function(k){ return k !== id && nftData[k].price > 0; }).slice(0,4);
  ids.forEach(function(k){
    var d = nftData[k];
    var card = document.createElement('a');
    card.href = uiRoutes.nftPayment+'?id=' + k;
    card.className = 'rec-card';
    card.innerHTML =
      '<div class="rec-card__media ' + d.media + '"><span class="rec-card__like">♡</span></div>' +
      '<div class="rec-card__body">' +
        '<div class="rec-card__title">' + d.title + '</div>' +
        '<div class="rec-card__sub">' + d.subtitle + '</div>' +
        '<div class="rec-card__meta">' + d.date + ' · ' + d.venue + '</div>' +
      '</div>';
    recGrid.appendChild(card);
  });
