(() => {
  'use strict';
  const stage=document.getElementById('stage'),slides=[...document.querySelectorAll('section.slide')];
  const toc=document.getElementById('deck-toc'),count=document.getElementById('deck-count');
  let current=-1, suppressClick=0, digits='',digitTimer;
  const interactive=target=>target instanceof Element && target.closest('button,a,input,select,textarea,video,audio,[contenteditable],[data-interactive],#deck-toc,#deck-controls');
  function fitFigures(slide){
    slide.querySelectorAll(':scope > .fig.card,:scope > .fig.plain').forEach(fig=>{
      const media=fig.querySelector('img,video');if(!media)return;
      const w=media.naturalWidth||media.videoWidth,h=media.naturalHeight||media.videoHeight;if(!w||!h)return;
      fig.style.flex='';fig.style.width='';fig.style.height='';fig.style.margin='';
      const maxW=fig.clientWidth,maxH=fig.clientHeight,pad=fig.classList.contains('card')?60:0;
      let width=maxW,height=(width-pad)*h/w+pad;if(height>maxH){height=maxH;width=(height-pad)*w/h+pad;}
      fig.style.flex='0 0 auto';fig.style.width=Math.round(width)+'px';fig.style.height=Math.round(height)+'px';fig.style.margin='auto';
    });
  }
  function fit(){stage.style.transform=`translate(-50%,-50%) scale(${Math.min(innerWidth/1920,innerHeight/1080)})`;if(current>=0)fitFigures(slides[current]);}
  function show(index){
    index=Math.max(0,Math.min(slides.length-1,Math.trunc(index)));if(index===current){if(location.hash!=='#'+(index+1))history.replaceState(null,'','#'+(index+1));return;}
    slides.forEach((slide,i)=>{
      const active=i===index;slide.classList.toggle('active',active);slide.setAttribute('aria-hidden',String(!active));
      slide.querySelectorAll('video').forEach(video=>{if(active){video.currentTime=0;video.play().catch(()=>{});}else video.pause();});
    });
    current=index;history.replaceState(null,'','#'+(index+1));count.textContent=`${index+1} / ${slides.length}`;
    document.getElementById('deck-prev').disabled=index===0;document.getElementById('deck-next').disabled=index===slides.length-1;
    toc.querySelectorAll('[data-index]').forEach(button=>button.classList.toggle('chosen',Number(button.dataset.index)===index));
    fitFigures(slides[index]);document.dispatchEvent(new CustomEvent('deckchange',{detail:{index,slide:slides[index]}}));
  }
  function menu(open){toc.hidden=open===undefined?!toc.hidden:!open;document.getElementById('deck-menu').setAttribute('aria-expanded',String(!toc.hidden));}
  let section='';slides.forEach((slide,index)=>{
    if(slide.dataset.sec!==section){section=slide.dataset.sec;const label=document.createElement('p');label.textContent=section;toc.append(label);}
    const b=document.createElement('button');b.type='button';b.dataset.index=index;b.textContent=`${index+1}  ${slide.dataset.title||slide.querySelector('h1')?.textContent||section}`;b.onclick=()=>{show(index);menu(false);};toc.append(b);
  });
  document.getElementById('deck-prev').onclick=()=>show(current-1);document.getElementById('deck-next').onclick=()=>show(current+1);
  document.getElementById('deck-menu').onclick=()=>menu();
  document.getElementById('deck-fullscreen').onclick=()=>{if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen().catch(()=>{});};
  addEventListener('keydown',event=>{
    if(event.ctrlKey||event.metaKey||event.altKey)return;
    if(event.key==='Escape'){menu(false);return;}
    const key=event.key;
    if(event.target instanceof Element && event.target.closest('input,select,textarea,video,audio,[contenteditable]'))return;
    if(interactive(event.target)&&[' ','Enter'].includes(key))return;
    if(['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(key)){event.preventDefault();show(current+1);}
    else if(['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(key)){event.preventDefault();show(current-1);}
    else if(key==='Home'){event.preventDefault();show(0);}else if(key==='End'){event.preventDefault();show(slides.length-1);}
    else if(key.toLowerCase()==='g')menu();
    else if(key.toLowerCase()==='c')document.getElementById('deck-hint').hidden=!document.getElementById('deck-hint').hidden;
    else if(key.toLowerCase()==='f')document.getElementById('deck-fullscreen').click();
    else if(['j','k'].includes(key.toLowerCase())&&slides[current].querySelector('[data-mechanism]')){document.getElementById(key.toLowerCase()==='j'?'mechanism-step':'mechanism-back').click();}
    else if(/^\d$/.test(key)){digits=(digits+key).slice(-3);clearTimeout(digitTimer);digitTimer=setTimeout(()=>{const n=Number(digits);digits='';if(n>0&&n<=slides.length)show(n-1);},450);}
  });
  // Lock until the wheel gesture has been quiet; inertial tail cannot skip slides.
  let wheelTotal=0,wheelLocked=false,wheelQuiet;
  addEventListener('wheel',event=>{
    if(event.ctrlKey||event.metaKey||interactive(event.target)||!toc.hidden)return;
    event.preventDefault();clearTimeout(wheelQuiet);wheelQuiet=setTimeout(()=>{wheelTotal=0;wheelLocked=false;},220);
    if(wheelLocked)return;
    const delta=Math.abs(event.deltaY)>=Math.abs(event.deltaX)?event.deltaY:event.deltaX;
    wheelTotal+=delta*(event.deltaMode===1?18:event.deltaMode===2?innerHeight:1);
    if(Math.abs(wheelTotal)>=70){show(current+(wheelTotal>0?1:-1));wheelTotal=0;wheelLocked=true;}
  },{passive:false});
  let touch=null;
  addEventListener('touchstart',event=>{
    if(event.touches.length!==1||interactive(event.target)||!toc.hidden){touch=null;return;}
    touch={x:event.touches[0].clientX,y:event.touches[0].clientY};
  },{passive:true});
  addEventListener('touchmove',event=>{if(touch)event.preventDefault();},{passive:false});
  addEventListener('touchend',event=>{
    if(!touch||!event.changedTouches.length)return;const t=event.changedTouches[0],dx=t.clientX-touch.x,dy=t.clientY-touch.y;touch=null;
    const distance=Math.abs(dx)>=Math.abs(dy)?dx:dy;
    if(Math.abs(distance)>65){suppressClick=performance.now()+650;show(current+(distance<0?1:-1));}
  },{passive:true});
  addEventListener('touchcancel',()=>touch=null);
  addEventListener('click',event=>{if(performance.now()<suppressClick||interactive(event.target))return;if(!toc.hidden){menu(false);return;}show(current+(event.clientX/innerWidth<.2?-1:1));});
  function fromHash(){const n=Number(location.hash.slice(1));if(Number.isInteger(n)&&n>0)show(n-1);}
  addEventListener('hashchange',fromHash);addEventListener('popstate',fromHash);addEventListener('resize',fit);
  slides.forEach(slide=>slide.querySelectorAll('img,video').forEach(m=>m.addEventListener(m.tagName==='VIDEO'?'loadedmetadata':'load',()=>{if(slide.classList.contains('active'))fitFigures(slide);})));
  window.jevDeck={show,get current(){return current;},count:slides.length};
  fit();const initial=Number(location.hash.slice(1));show(Number.isInteger(initial)&&initial>0?initial-1:0);if(location.search.includes('nav=1'))menu(true);
})();
