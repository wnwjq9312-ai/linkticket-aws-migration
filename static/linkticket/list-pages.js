/* Paginate actual admin API rows, preserving their existing array contract. */
(() => {
  function attach(table){
    if(table.dataset.paginated)return;table.dataset.paginated='1';
    const rows=[...table.querySelectorAll('tbody > tr')];if(rows.length<=10)return;
    const nav=document.createElement('nav');nav.className='pagination';nav.setAttribute('aria-label','목록 페이지');table.after(nav);
    let page=1;const count=Math.ceil(rows.length/10);
    function draw(){rows.forEach((row,i)=>row.hidden=i<(page-1)*10||i>=page*10);nav.replaceChildren();
      const nums=[...new Set([1,page-1,page,page+1,count])].filter(n=>n>=1&&n<=count).sort((a,b)=>a-b);
      for(const n of [page-1,...nums,page+1]){const b=document.createElement('button');b.type='button';const i=nav.children.length;b.textContent=i===0?'‹':i===nums.length+1?'›':n;b.disabled=n<1||n>count;if(n===page&&i>0&&i<=nums.length)b.setAttribute('aria-current','page');b.onclick=()=>{page=n;draw();};nav.append(b);}
    }draw();
  }
  const refresh=()=>document.querySelectorAll('.operations table').forEach(attach);
  new MutationObserver(refresh).observe(document.body,{childList:true,subtree:true});refresh();
  document.querySelectorAll('form').forEach(form=>form.addEventListener('reset',()=>form.querySelectorAll('.upload-preview').forEach(img=>{if(img.dataset.objectUrl)URL.revokeObjectURL(img.dataset.objectUrl);img.remove();})));
  document.querySelectorAll('input[type=file]').forEach(input=>input.addEventListener('change',()=>{const slot=input.parentElement.querySelector('.upload-preview-slot');if(!slot)return;let preview=slot.querySelector('img');if(!preview){preview=document.createElement('img');preview.className='upload-preview';preview.alt='선택한 공연 이미지';slot.append(preview);}if(preview.dataset.objectUrl)URL.revokeObjectURL(preview.dataset.objectUrl);preview.hidden=!input.files[0];if(input.files[0]){preview.src=URL.createObjectURL(input.files[0]);preview.dataset.objectUrl=preview.src;}}));
})();
