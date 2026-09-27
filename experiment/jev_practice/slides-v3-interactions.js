(() => {
  const replay=JSON.parse(document.getElementById('maze-data').textContent),canvases=[...document.querySelectorAll('.maze-panel canvas')];
  let frame=225,playing=false,lastTick=0;const max=Math.max(...replay.systems.map(s=>s.positions.length-1));
  function maze(){
    canvases.forEach((canvas,index)=>{
      const ctx=canvas.getContext('2d'),system=replay.systems[index],k=Math.min(frame,system.positions.length-1),u=canvas.width/replay.size;
      ctx.fillStyle='#f8f9f6';ctx.fillRect(0,0,440,440);ctx.fillStyle='#d1d8cc';replay.initial.walls.forEach(([y,x])=>ctx.fillRect(x*u,y*u,Math.ceil(u),Math.ceil(u)));
      ctx.strokeStyle='#a5bee4';ctx.lineWidth=u*.4;ctx.beginPath();system.positions.slice(0,k+1).forEach(([y,x],i)=>{if(i===0)ctx.moveTo((x+.5)*u,(y+.5)*u);else ctx.lineTo((x+.5)*u,(y+.5)*u);});ctx.stroke();
      const [gy,gx]=replay.initial.goal;ctx.fillStyle='#1d1d1f';ctx.fillRect(gx*u+1,gy*u+1,u-1,u-1);
      const [y,x]=system.positions[k];ctx.fillStyle='#0071e3';ctx.fillRect(x*u,y*u,u,u);ctx.strokeStyle='#0071e3';ctx.lineWidth=2;ctx.strokeRect(x*u-2,y*u-2,u+4,u+4);
      canvas.parentElement.querySelector('.maze-readout').textContent=`${k.toLocaleString()} / ${system.summary.steps.toLocaleString()} 次尝试${k===system.positions.length-1?' · 已到达':''}`;
    });
    document.getElementById('maze-step').value=frame;document.getElementById('maze-position').textContent=`${frame.toLocaleString()} / ${max.toLocaleString()}`;
    document.getElementById('maze-play').textContent=playing?'暂停轨迹':'播放轨迹';
  }
  function tick(now){if(!playing)return;const steps=Math.floor((now-lastTick)/1000*180);if(steps>0){frame=Math.min(max,frame+steps);lastTick=now;if(frame===max)playing=false;maze();}if(playing)requestAnimationFrame(tick);}
  document.getElementById('maze-play').onclick=()=>{playing=!playing;if(playing){if(frame===max)frame=0;lastTick=performance.now();requestAnimationFrame(tick);}maze();};
  document.getElementById('maze-reset').onclick=()=>{playing=false;frame=0;maze();};document.getElementById('maze-step').oninput=event=>{playing=false;frame=Number(event.target.value);maze();};maze();
  document.addEventListener('deckchange',event=>{if(!event.detail.slide.querySelector('.maze-panels')){playing=false;maze();}});
})();
