(function(){
  var h=location.hash.replace('#','');
  if(h==='check'){
    // QA 模式：量出每张卡片内容超出页脚多少（单位 cqw，1cqw = 卡片宽度的 1%）
    var out=[];
    var measure=function(){
    document.querySelectorAll('.card').forEach(function(c){
      // 不依赖窗口大小：每张固定成 1080x1920 再量
      c.style.width='1080px';c.style.height='1920px';c.style.aspectRatio='auto';
      var cr=c.getBoundingClientRect(),ft=c.querySelector('.ft');
      if(!ft)return;  // 封面没有页脚，不检查
      var limit=ft.getBoundingClientRect().top;
      var maxB=0,maxR=0,who='';
      c.querySelectorAll('.in *').forEach(function(el){
        if(el.classList.contains('btm'))return;
        var r=el.getBoundingClientRect();
        if(r.width===0&&r.height===0)return;
        if(r.bottom>maxB){maxB=r.bottom;who=el.tagName.toLowerCase()+'.'+el.className;}maxR=Math.max(maxR,r.right);
      });
      var u=cr.width/100;
      out.push({n:+c.dataset.n,overflow:+((maxB-(limit-2*u))/u).toFixed(1),right:+((maxR-cr.right)/u).toFixed(1),who:who});
    });
    var s=document.createElement('script');s.type='application/json';s.id='qa';
    s.textContent=JSON.stringify(out);document.body.appendChild(s);
    };
    // 等网页字体加载完再量，否则用的是备用字体，宽度不对
    (document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(function(){setTimeout(measure,300);});
    return;
  }
  if(!/^c\d+$/.test(h))return;
  var el=document.getElementById(h);
  if(!el)return;
  document.body.classList.add('solo');
  el.classList.add('on');
})();
