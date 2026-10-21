(() => {
  'use strict';
  const configNode = document.getElementById('lt-venue-config');
  const dialog = document.querySelector('.lt-venue-modal');
  if (!configNode || !dialog) return;
  let config;
  try { config = JSON.parse(configNode.textContent); }
  catch (_) { console.error('[LINKTICKET map] config-json-invalid'); return; }
  config.key = typeof config.key === 'string' ? config.key.trim() : '';
  // Never log config, script URLs, events or SDK exceptions: they may contain the key.
  const fail = code => console.error('[LINKTICKET map] ' + code);
  let venue = config.venue, opener;
  const $ = selector => dialog.querySelector(selector);
  const $$ = selector => [...dialog.querySelectorAll(selector)];
  const mapNode = $('#lt-kakao-map');
  const fallback = $('.lt-map-fallback');
  const status = $('.lt-venue-status');
  let map, center, sdkPromise, opening;
  const normalize = value => String(value || '').replace(/\s/g, '').toLowerCase();
  function showFallback(message) {
    fallback.hidden = false;
    fallback.querySelector('p').textContent = message;
  }
  function sdk() {
    if (window.kakao?.maps?.Map && window.kakao?.maps?.services?.Places) return Promise.resolve();
    if (sdkPromise) return sdkPromise;
    sdkPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      let settled = false;
      const finish = error => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        if (error) { fail(error.message); script.remove(); reject(error); } else resolve();
      };
      const timer = setTimeout(() => finish(new Error('sdk-timeout')), 15000);
      script.async = true;
      script.src = 'https://dapi.kakao.com/v2/maps/sdk.js?autoload=false&libraries=services&appkey=' + encodeURIComponent(config.key);
      script.onerror = () => finish(new Error('sdk-script-onerror: check Network, allowed domain and Kakao Maps activation')); 
      script.onload = () => {
        try {
          if (!window.kakao?.maps?.load) return finish(new Error('sdk-unavailable'));
          window.kakao.maps.load(() => {
            finish(window.kakao.maps.Map && window.kakao.maps.services?.Places ? null : new Error('sdk-components-unavailable'));
          });
        } catch (_) { finish(new Error('sdk-initialization-failed')); }
      };
      document.head.append(script);
    }).catch(error => { sdkPromise = null; throw error; });
    return sdkPromise;
  }
  function locate() {
    if (typeof venue.latitude === 'number' && typeof venue.longitude === 'number' &&
        Math.abs(venue.latitude) <= 90 && Math.abs(venue.longitude) <= 180) {
      return Promise.resolve({latitude:venue.latitude, longitude:venue.longitude});
    }
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('location-timeout')), 10000);
      const places = new kakao.maps.services.Places();
      places.keywordSearch(venue.search_query, (results, resultStatus) => {
        clearTimeout(timer);
        if (resultStatus !== kakao.maps.services.Status.OK) { fail('Places search failed: ' + resultStatus); return reject(new Error('location-not-found')); }
        const matches = results.filter(place =>
          venue.match_names.some(name => normalize(place.place_name).includes(normalize(name))) &&
          normalize(place.road_address_name).includes(normalize(venue.match_address)));
        // Never silently select an unrelated place or invent a coordinate.
        if (matches.length !== 1) { fail('Places match count: ' + matches.length); return reject(new Error('location-ambiguous')); }
        const latitude = Number(matches[0].y), longitude = Number(matches[0].x);
        if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return reject(new Error('location-invalid'));
        resolve({latitude, longitude});
      });
    });
  }
  function relayout() {
    if (dialog.open && map && center) {
      map.relayout();
      map.setCenter(center);
    }
  }
  async function initMap() {
    if (!config.key) {
      // Missing optional configuration is a visible state, not a JS failure.
      showFallback('카카오맵 API 키를 설정하면 공연장 지도가 표시됩니다.');
      return;
    }
    if (map) { relayout(); return; }
    let stage = 'sdk';
    try {
      showFallback('카카오 지도를 불러오는 중입니다…');
      await sdk();
      stage = 'location';
      const location = await locate();
      // A user may close the modal while the SDK/search is loading.
      if (!dialog.open) return;
      stage = 'map-create';
      center = new kakao.maps.LatLng(location.latitude, location.longitude);
      map = new kakao.maps.Map(mapNode, {center, level:4});
      new kakao.maps.Marker({map, position:center});
      const label = document.createElement('div');
      label.className = 'lt-map-label';
      label.textContent = venue.name + ' (' + venue.subtitle + ')';
      new kakao.maps.CustomOverlay({map, position:center, content:label, yAnchor:2.4});
      const destination = encodeURIComponent(venue.name) + ',' + location.latitude + ',' + location.longitude;
      $('.lt-kakao-link').href = 'https://map.kakao.com/link/map/' + destination;
      $('.lt-directions').href = 'https://map.kakao.com/link/to/' + destination;
      $('.lt-directions').removeAttribute('aria-disabled');
      $$('[data-map-type], [data-venue-zoom], [data-venue-center]').forEach(button => button.disabled = false);
      fallback.hidden = true;
      requestAnimationFrame(relayout);
    } catch (error) {
      fail('initialization-failed at ' + stage);
      const locationError = stage === 'location';
      showFallback(locationError ? '공연장 위치를 확인하지 못했습니다. 카카오맵 검색을 이용해주세요.' : '지도를 불러오지 못했습니다. API 키·등록 도메인·Kakao Map 활성화와 네트워크 연결을 확인해주세요.');
    }
  }
  function updateVenue(next){
    venue=next;map=null;center=null;mapNode.replaceChildren();
    $('.lt-venue-info h3').textContent=venue.name;
    $('.lt-venue-info h3 + p').textContent=venue.description||'';
    const values=$$('.lt-venue-info dd');[venue.address,venue.name,venue.phone||'미등록',venue.capacity||'미등록'].forEach((v,i)=>values[i].textContent=v||'미등록');
    $('.lt-venue-address span').textContent=venue.address||'주소 미등록';
    $('.lt-venue-photo')?.setAttribute('hidden','');
    $('.lt-kakao-link').href='https://map.kakao.com/link/search/'+encodeURIComponent(venue.search_query||venue.name);
    $('.lt-directions').removeAttribute('href');$('.lt-directions').setAttribute('aria-disabled','true');
    $$('[data-map-type], [data-venue-zoom], [data-venue-center]').forEach(b=>b.disabled=true);
    $$('[data-venue-panel]').forEach(panel=>{panel.replaceChildren();const p=document.createElement('p');p.textContent='등록된 추가 안내가 없습니다. 공연장에 확인해주세요.';panel.append(p);});
  }
  document.addEventListener('click', async event => {
    const button=event.target.closest('[data-map]');if(!button||dialog.open||opening)return;
    opener=button;button.disabled=true;
    try {
      if(button.dataset.mapSource){const response=await fetch(button.dataset.mapSource);if(!response.ok)throw Error();updateVenue(await response.json());}
      dialog.showModal();document.body.classList.add('lt-venue-open');
      opening=initMap();await opening;
    }catch(_){status.textContent='공연장 정보를 불러오지 못했습니다.';if(!dialog.open)dialog.showModal();}
    finally{opening=null;button.disabled=false;}
  });
  $('.lt-venue-close').addEventListener('click', () => dialog.close());
  let outsideDown = false;
  const outside = event => { const rect = dialog.getBoundingClientRect(); return event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom; };
  dialog.addEventListener('pointerdown', event => { outsideDown = event.target === dialog && outside(event); });
  dialog.addEventListener('click', event => { if (outsideDown && event.target === dialog && outside(event)) dialog.close(); outsideDown = false; });
  dialog.addEventListener('close', () => { document.body.classList.remove('lt-venue-open'); opener?.focus(); });
  // Native dialog handles Escape and traps keyboard focus.
  new ResizeObserver(() => requestAnimationFrame(relayout)).observe(mapNode);
  $$('[data-map-type]').forEach(button => button.addEventListener('click', () => {
    if (!map) return;
    map.setMapTypeId(button.dataset.mapType === 'sky' ? kakao.maps.MapTypeId.HYBRID : kakao.maps.MapTypeId.ROADMAP);
    $$('[data-map-type]').forEach(item => item.classList.toggle('active', item === button));
  }));
  $$('[data-venue-zoom]').forEach(button => button.addEventListener('click', () => { if (map) map.setLevel(map.getLevel() + (button.dataset.venueZoom === 'in' ? -1 : 1)); }));
  $('[data-venue-center]').addEventListener('click', () => { if (map) map.panTo(center); });
  $('.lt-directions').addEventListener('click', event => { if (!event.currentTarget.href) { event.preventDefault(); status.textContent='길찾기는 공연장 좌표 확인 후 사용할 수 있습니다. 카카오맵 검색을 이용해주세요.'; } });
  $('[data-copy-address]').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(venue.address); status.textContent='주소가 복사되었습니다.'; }
    catch (_) { status.textContent='자동 복사를 사용할 수 없습니다. 주소를 선택해 복사해주세요: ' + venue.address; }
  });
  const tabs = $$('[data-venue-tab]');
  function activate(tab) {
    tabs.forEach(button => { const selected = button === tab; button.setAttribute('aria-selected', String(selected)); button.tabIndex = selected ? 0 : -1; });
    $$('[data-venue-panel]').forEach(panel => panel.hidden = panel.dataset.venuePanel !== tab.dataset.venueTab);
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activate(tab));
    tab.addEventListener('keydown', event => {
      const next = event.key === 'ArrowRight' ? (index + 1) % tabs.length : event.key === 'ArrowLeft' ? (index + tabs.length - 1) % tabs.length : event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : null;
      if (next !== null) { event.preventDefault(); activate(tabs[next]); tabs[next].focus(); }
    });
  });
})();
