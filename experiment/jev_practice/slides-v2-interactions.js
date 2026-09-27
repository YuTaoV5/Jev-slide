(() => {
  let step=0;const captions=['先提供完整的当前材料','用业务选项限定可执行的答案','示例分布来自人工夹具，不是模型实测','应用代码按门槛路由，低分交回人工'];
  const nodes=[...document.querySelectorAll('[data-step-node]')];
  function renderStep(){nodes.forEach((node,i)=>node.classList.toggle('on',i===step));document.querySelector('.mechanism-counter').textContent=`${step+1} / 4`;document.getElementById('mechanism-caption').textContent=captions[step];}
  document.getElementById('mechanism-step').onclick=()=>{step=(step+1)%4;renderStep();};document.getElementById('mechanism-back').onclick=()=>{step=(step+3)%4;renderStep();};renderStep();
  const labels=['billing','technical','unknown'],sets=[[.82,.12,.06],[.36,.34,.30]];let set=0;
  function gate(){
    const ps=sets[set],threshold=Number(document.getElementById('gate-threshold').value);document.getElementById('gate-number').textContent=threshold.toFixed(2);
    document.getElementById('gate-high').classList.toggle('selected',set===0);document.getElementById('gate-low').classList.toggle('selected',set===1);
    document.getElementById('gate-bars').innerHTML=ps.map((p,i)=>`<div class="gate-bar-row"><div class="gate-bar-meta"><span>${labels[i]}</span><b>${p.toFixed(2)}</b></div><div class="gate-track"><div class="gate-fill" style="width:${p*100}%"></div></div></div>`).join('');
    const abstained=ps[0]<threshold;document.getElementById('gate-output').textContent=abstained?'交回人工处理':'进入 billing 队列';
    document.getElementById('gate-json').textContent=JSON.stringify({value:abstained?null:'billing',abstained},null,2);
  }
  document.getElementById('gate-high').onclick=()=>{set=0;gate();};document.getElementById('gate-low').onclick=()=>{set=1;gate();};document.getElementById('gate-threshold').oninput=gate;gate();
  const replay=JSON.parse(document.getElementById('maze-data').textContent),canvases=[...document.querySelectorAll('.maze-panel canvas')];
  let frame=225,playing=false,lastTick=0;const max=Math.max(...replay.systems.map(s=>s.positions.length-1));
  function maze(){
    canvases.forEach((canvas,index)=>{
      const ctx=canvas.getContext('2d'),system=replay.systems[index],k=Math.min(frame,system.positions.length-1),u=canvas.width/replay.size;
      ctx.fillStyle='#f8f9f6';ctx.fillRect(0,0,440,440);ctx.fillStyle='#d1d8cc';replay.initial.walls.forEach(([x,y])=>ctx.fillRect(x*u,y*u,Math.ceil(u),Math.ceil(u)));
      ctx.strokeStyle='#a5bee4';ctx.lineWidth=u*.4;ctx.beginPath();system.positions.slice(0,k+1).forEach(([x,y],i)=>{if(i===0)ctx.moveTo((x+.5)*u,(y+.5)*u);else ctx.lineTo((x+.5)*u,(y+.5)*u);});ctx.stroke();
      const [gx,gy]=replay.initial.goal;ctx.fillStyle='#1d1d1f';ctx.fillRect(gx*u+1,gy*u+1,u-1,u-1);
      const [x,y]=system.positions[k];ctx.fillStyle='#0071e3';ctx.fillRect(x*u,y*u,u,u);ctx.strokeStyle='#0071e3';ctx.lineWidth=2;ctx.strokeRect(x*u-2,y*u-2,u+4,u+4);
      canvas.parentElement.querySelector('.maze-readout').textContent=`${k.toLocaleString()} / ${system.summary.steps.toLocaleString()} 步${k===system.positions.length-1?' · 已到达':''}`;
    });
    document.getElementById('maze-step').value=frame;document.getElementById('maze-position').textContent=`${frame.toLocaleString()} / ${max.toLocaleString()}`;
    document.getElementById('maze-play').textContent=playing?'暂停轨迹':'播放轨迹';
  }
  function tick(now){if(!playing)return;const steps=Math.floor((now-lastTick)/1000*180);if(steps>0){frame=Math.min(max,frame+steps);lastTick=now;if(frame===max)playing=false;maze();}if(playing)requestAnimationFrame(tick);}
  document.getElementById('maze-play').onclick=()=>{playing=!playing;if(playing){if(frame===max)frame=0;lastTick=performance.now();requestAnimationFrame(tick);}maze();};
  document.getElementById('maze-reset').onclick=()=>{playing=false;frame=0;maze();};document.getElementById('maze-step').oninput=event=>{playing=false;frame=Number(event.target.value);maze();};maze();
  document.addEventListener('deckchange',event=>{if(!event.detail.slide.querySelector('.maze-panels')){playing=false;maze();}if(event.detail.slide.querySelector('[data-mechanism]')){step=0;renderStep();}});
})();
