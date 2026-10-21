const uiRoutes=JSON.parse(document.getElementById('ui-routes').textContent);
// 상단 검색: 키워드를 실제 검색 결과 페이지(WEB 담당의 공연 탐색 파트)로 넘겨서 이동만 시킴.
  // 실제로 DB에서 공연/아티스트를 찾아 결과를 보여주는 로직은 WEB/백엔드 담당 몫
  function doSearch(){
    var keyword = document.getElementById('searchInput').value.trim();
    if(!keyword){
      alert('검색어를 입력해주세요.');
      return;
    }
    window.location.href = uiRoutes.performances+'?q=' + encodeURIComponent(keyword);
  }

  // 이메일 구독: 지금은 화면에 "완료" 메시지만 보여줌 (실제 DB 저장은 백엔드 연결 후)
  function subscribeEmail(){
    var email = document.getElementById('subscribeEmail').value;
    if(!email || email.indexOf('@') === -1){
      alert('이메일을 올바르게 입력해주세요.');
      return;
    }
    document.getElementById('subscribeInput').style.display = 'none';
    document.getElementById('subscribeSuccess').textContent = '미리보기 완료 · 실제 구독 신청은 전송되지 않았습니다.';
    document.getElementById('subscribeSuccess').classList.add('show');

    // 3초 뒤 다시 입력창으로 복귀
    setTimeout(function(){
      document.getElementById('subscribeSuccess').classList.remove('show');
      document.getElementById('subscribeInput').style.display = 'flex';
      document.getElementById('subscribeEmail').value = '';
    }, 1500);
  }

  // 필터 탭 클릭 -> data-filter 값과 카드의 data-category 값을 비교해서 보이기/숨기기
  // 실제 서비스에서는 이 부분이 서버에 카테고리를 물어보는 요청(쿼리 파라미터)으로 바뀜
  var tabs = document.querySelectorAll('.filter-tab');
  var cards = document.querySelectorAll('.event-card');
  var countEl = document.querySelector('.section-head .count');

  tabs.forEach(function(tab){
    tab.addEventListener('click', function(){
      tabs.forEach(function(t){ t.classList.remove('active'); });
      tab.classList.add('active');

      var filter = tab.getAttribute('data-filter');
      var visibleCount = 0;

      cards.forEach(function(card){
        var match = (filter === 'all' || card.getAttribute('data-category') === filter);
        card.style.display = match ? '' : 'none';
        if(match) visibleCount++;
      });

      if(countEl){ countEl.textContent = visibleCount; }
    });
  });
