// History grade 8 study site: show/hide solutions, "I solved it" ticks with progress, glossary search and views.
(function(){
  function store(){ try{ return window.localStorage; }catch(e){ return null; } }
  function load(key){ var s=store(); if(!s) return {}; try{ return JSON.parse(s.getItem(key)||'{}')||{}; }catch(e){ return {}; } }
  function save(key,val){ var s=store(); if(!s) return; try{ s.setItem(key,JSON.stringify(val)); }catch(e){} }

  // open every solution before printing
  window.addEventListener('beforeprint',function(){ document.querySelectorAll('details').forEach(function(d){ d.dataset.wasOpen=d.open?'1':''; d.open=true; }); });
  window.addEventListener('afterprint',function(){ document.querySelectorAll('details').forEach(function(d){ d.open=!!d.dataset.wasOpen; }); });

  // workbook toolbar
  var bar=document.querySelector('.toolbar');
  if(bar){
    var key='h8:'+location.pathname.split('/').pop();
    var state=load(key);
    var boxes=[].slice.call(document.querySelectorAll('.tick input'));
    var prog=bar.querySelector('.progress');
    function update(){
      var n=0; boxes.forEach(function(b){ var li=b.closest('li'); if(b.checked){n++; li&&li.classList.add('done');} else {li&&li.classList.remove('done');} });
      if(prog) prog.textContent='פתרתי '+n+' מתוך '+boxes.length;
    }
    boxes.forEach(function(b){ b.checked=!!state[b.dataset.id]; b.addEventListener('change',function(){ state[b.dataset.id]=b.checked; if(!b.checked) delete state[b.dataset.id]; save(key,state); update(); }); });
    var showBtn=bar.querySelector('[data-act=toggle]');
    var shown=false;
    showBtn&&showBtn.addEventListener('click',function(){ shown=!shown; document.querySelectorAll('ol.exercises details').forEach(function(d){ d.open=shown; }); showBtn.textContent=shown?'הסתרת כל הפתרונות':'הצגת כל הפתרונות'; });
    var clr=bar.querySelector('[data-act=clear]');
    clr&&clr.addEventListener('click',function(){ boxes.forEach(function(b){ b.checked=false; }); state={}; save(key,state); update(); });
    update();
  }

  // glossary
  var q=document.getElementById('gl-search');
  if(q){
    var entries=[].slice.call(document.querySelectorAll('.entry'));
    var heads=[].slice.call(document.querySelectorAll('.letter-head, .cat-head'));
    var count=document.getElementById('gl-count');
    function norm(s){ return (s||'').toLowerCase().replace(/[֑-ׇ]/g,'').replace(/[׳״'"\-־]/g,''); }
    function filter(){
      var v=norm(q.value.trim()); var n=0;
      entries.forEach(function(e){ var hit=!v||norm(e.textContent).indexOf(v)>=0; e.classList.toggle('hidden',!hit); if(hit) n++; });
      heads.forEach(function(h){ var box=h.nextElementSibling; if(!box) return; var any=box.querySelector('.entry:not(.hidden)'); h.classList.toggle('hidden',!any); });
      if(count) count.textContent=v? (n+' מושגים נמצאו') : '';
    }
    q.addEventListener('input',filter);
    var vb=[].slice.call(document.querySelectorAll('.views button'));
    vb.forEach(function(b){ b.addEventListener('click',function(){
      vb.forEach(function(x){ x.setAttribute('aria-pressed', x===b?'true':'false'); });
      document.getElementById('view-abc').classList.toggle('hidden', b.dataset.view!=='abc');
      document.getElementById('view-cat').classList.toggle('hidden', b.dataset.view!=='cat');
      var letters=document.querySelector('.letters'); if(letters) letters.classList.toggle('hidden', b.dataset.view!=='abc');
      entries=[].slice.call(document.querySelectorAll('#view-'+b.dataset.view+' .entry'));
      heads=[].slice.call(document.querySelectorAll('#view-'+b.dataset.view+' .letter-head, #view-'+b.dataset.view+' .cat-head'));
      filter();
    }); });
    entries=[].slice.call(document.querySelectorAll('#view-abc .entry'));
    heads=[].slice.call(document.querySelectorAll('#view-abc .letter-head'));
  }
})();
