const uiRoutes=JSON.parse(document.getElementById('ui-routes').textContent);
// 상단 검색: 키워드를 실제 검색 결과 페이지(WEB 담당의 공연 탐색 파트)로 넘겨서 이동만 시킴
  function doSearch(){
    var keyword = document.getElementById('searchInput').value.trim();
    if(!keyword){
      alert('검색어를 입력해주세요.');
      return;
    }
    window.location.href = uiRoutes.performances+'?q=' + encodeURIComponent(keyword);
  }

  // /events/ 카드 6개와 1:1로 매칭되는 더미 데이터.
  // 나중에 Django에서는 이 객체 대신 실제 DB에서 조회한 event 값이 들어감
  var eventData = {
    "1": { tag:"예매 이벤트",   title:"EARLY BIRD 할인 이벤트",        date:"2025.04.01(화) ~ 2025.04.30(수)", dateShort:"04.01 ~ 04.30", desc:"지금, 가장 특별한 가격으로 공연을 만나보세요! 기간 내 예매 시 선예매가와 동일한 할인 혜택을 드립니다.", media:"media-1" },
    "2": { tag:"멤버십 혜택",   title:"LINK TICKET 멤버십 특별 혜택",   date:"2025.04.01(화) ~ 상시 진행",       dateShort:"04.01 ~ 상시",  desc:"멤버십 회원만을 위한 다양한 혜택과 선예매 기회를 드립니다.", media:"media-2" },
    "3": { tag:"SNS 이벤트",    title:"공연 인증샷 이벤트",             date:"2025.04.05(토) ~ 2025.05.10(토)", dateShort:"04.05 ~ 05.10", desc:"공연장의 뜨거운 순간을 공유하고 푸짐한 선물을 받아보세요!", media:"media-3" },
    "4": { tag:"프로모션",      title:"친구와 함께 예매하면 할인!",     date:"2025.04.10(목) ~ 2025.05.15(목)", dateShort:"04.10 ~ 05.15", desc:"함께할수록 더 즐거운 공연, 지금 친구를 초대하세요!", media:"media-4" },
    "5": { tag:"팬 이벤트",     title:"아티스트 사인회 초대 이벤트",    date:"2025.04.15(화) ~ 2025.05.20(화)", dateShort:"04.15 ~ 05.20", desc:"공연 티켓 예매하고 아티스트와 가까워질 특별한 기회!", media:"media-5" },
    "6": { tag:"제휴 이벤트",   title:"제휴사 할인 혜택",               date:"2025.04.01(화) ~ 2025.06.30(월)", dateShort:"04.01 ~ 06.30", desc:"다양한 제휴사와 함께하는 특별한 할인 혜택을 만나보세요!", media:"media-6" }
  };

  var params = new URLSearchParams(window.location.search);
  var id = params.get('id') || "1";
  var data = eventData[id] || eventData["1"];

  document.getElementById('detailTag').textContent = data.tag;
  document.getElementById('detailTitle').textContent = data.title;
  document.getElementById('detailDate').textContent = data.date;
  document.getElementById('detailDateShort').textContent = data.dateShort;
  document.getElementById('detailDesc').textContent = data.desc;
  document.getElementById('detailHero').classList.add(data.media);
  document.title = "LINKTICKET - " + data.title;
