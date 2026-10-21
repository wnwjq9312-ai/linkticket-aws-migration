const uiRoutes=JSON.parse(document.getElementById('ui-routes').textContent);
// 헤더 상단 검색(사이트 전체 공연 검색) - 이건 그대로 외부 검색 페이지로 이동
  function doSearch(){
    var keyword = document.getElementById('searchInput').value.trim();
    if(!keyword){ alert('검색어를 입력해주세요.'); return; }
    window.location.href = uiRoutes.performances+'?q=' + encodeURIComponent(keyword);
  }

  // ===== NFT 컬렉션 필터 =====
  // 체크박스(카테고리/아티스트/가격대)는 클릭 즉시 반영, 검색창은 엔터/돋보기/검색하기 버튼을 눌러야 반영.
  // 실제 서비스에서는 이 로직 전체가 서버에 쿼리 파라미터(category=, artist=, price=, q=)로 요청을 보내고
  // DB에서 필터링된 결과를 받아오는 방식으로 바뀜
  var nftCards = document.querySelectorAll('.nft-card');
  var activeKeyword = ''; // 검색 제출(엔터/돋보기/검색하기)이 있어야만 갱신됨

  // 가격을 가격대 버킷 키로 변환
  function priceBucket(price){
    if(price >= 500000) return 'over50';
    if(price >= 300000) return '30to50';
    if(price >= 100000) return '10to30';
    return 'under10';
  }

  // "전체" 체크박스와 개별 체크박스 동기화 (전체 클릭 -> 개별 일괄 토글 / 개별 클릭 -> 전체 상태 자동 갱신)
  document.querySelectorAll('.filter-group').forEach(function(group){
    var allBox = group.querySelector('.filter-all');
    var itemBoxes = group.querySelectorAll('.filter-item');

    allBox.addEventListener('change', function(){
      itemBoxes.forEach(function(box){ box.checked = allBox.checked; });
      applyNftFilter();
    });

    itemBoxes.forEach(function(box){
      box.addEventListener('change', function(){
        var allChecked = Array.prototype.every.call(itemBoxes, function(b){ return b.checked; });
        allBox.checked = allChecked;
        applyNftFilter();
      });
    });
  });

  // 검색창(필터 상단 돋보기/엔터, 하단 검색하기 버튼 - 전부 동일 동작)
  function applyNftFilter(){
    activeKeyword = document.getElementById('nftSearchInput').value.trim().toLowerCase();
    runNftFilter();
  }

  function runNftFilter(){
    // 그룹별로 "개별 항목 중 체크된 값" 목록을 만든다. 아무것도 체크 안 돼있으면(=전체 상태) 그 그룹은 필터링하지 않음
    var groupValues = {};
    document.querySelectorAll('.filter-group').forEach(function(group){
      var key = group.getAttribute('data-group');
      var checked = Array.prototype.filter.call(group.querySelectorAll('.filter-item'), function(b){ return b.checked; })
                          .map(function(b){ return b.getAttribute('data-value'); });
      groupValues[key] = checked; // 빈 배열 = 제한 없음
    });

    var visibleCount = 0;

    nftCards.forEach(function(card){
      var category = card.getAttribute('data-category');
      var artist = card.getAttribute('data-artist');
      var price = parseInt(card.getAttribute('data-price'), 10);

      var matchCategory = groupValues.category.length === 0 || groupValues.category.indexOf(category) !== -1;
      var matchArtist = groupValues.artist.length === 0 || groupValues.artist.indexOf(artist) !== -1;
      // 가격 미정(0)인 항목(예: 스페셜 컬렉션)은 가격대 필터에서 항상 통과시킴
      var matchPrice = groupValues.price.length === 0 || price === 0 || groupValues.price.indexOf(priceBucket(price)) !== -1;
      var matchKeyword = !activeKeyword || card.textContent.toLowerCase().indexOf(activeKeyword) !== -1;

      var match = matchCategory && matchArtist && matchPrice && matchKeyword;
      card.style.display = match ? '' : 'none';
      if(match) visibleCount++;
    });

    var countEl = document.querySelector('.section-head .count');
    if(countEl){ countEl.textContent = visibleCount; }
  }
  runNftFilter();
