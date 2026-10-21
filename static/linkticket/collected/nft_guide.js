const uiRoutes=JSON.parse(document.getElementById('ui-routes').textContent);
function doSearch(){
    var keyword = document.getElementById('searchInput').value.trim();
    if(!keyword){ alert('검색어를 입력해주세요.'); return; }
    window.location.href = uiRoutes.performances+'?q=' + encodeURIComponent(keyword);
  }

  function toggleFaq(el){
    el.parentElement.classList.toggle('open');
  }
