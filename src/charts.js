/* Shared helpers and charts for the book and the "Какво ако?" page. */
const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => [...r.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const fmt = (v, d=1) => v==null ? '—' : Number(v).toLocaleString('bg-BG',{minimumFractionDigits:d,maximumFractionDigits:d});
const num = v => typeof v === 'number' ? v.toLocaleString('bg-BG') : v;
const get = (arr, y) => { const r = arr && arr.find(p => p[0]===y); return r ? r[1] : null; };
const last = arr => arr && arr.length ? arr[arr.length-1] : null;
const sgn = (v,d=1) => v==null ? '—' : (v>0?'+':v<0?'−':'')+fmt(Math.abs(v),d);
const MONTHS = ['яну','фев','мар','апр','май','юни','юли','авг','сеп','окт','ное','дек'];

/* ---------- tooltip ---------- */
const tip = $('#tip');
function showTip(html, x, y){
  tip.innerHTML = html; tip.hidden = false;
  const r = tip.getBoundingClientRect();
  let lx = x + 14, ly = y + 14;
  if (lx + r.width > innerWidth - 8) lx = x - r.width - 14;
  if (ly + r.height > innerHeight - 8) ly = y - r.height - 14;
  tip.style.left = Math.max(8,lx)+'px'; tip.style.top = Math.max(8,ly)+'px';
}
function hideTip(){ tip.hidden = true; }


/* ---------- figure scaffold ---------- */
function figure(id, {title, cap, src, legend=[], table, head}){
  const f = document.getElementById(id);
  const lg = head ? head : legend.length ? `<div class="legend">${legend.map(l=>`<span><i class="${l.dash?'dash':''} ${l.sq?'sq':''}" style="background:${l.color}"></i>${l.label}</span>`).join('')}</div>` : '';
  f.innerHTML = `<div class="fig-head"><div class="fig-title">${title}</div></div>${lg}${cap?`<div class="fig-cap">${cap}</div>`:''}<div class="chart"></div><div class="fig-head"><span class="fig-src">Източник: ${src}</span></div>${table?`<details class="table-view"><summary>Покажи таблица с данните</summary><div class="tv">${table}</div></details>`:''}`;
  return f.querySelector('.chart');
}
function tableOf(cols){
  const years = [...new Set(cols.flatMap(c=>(c.data||[]).map(p=>p[0])))].sort((a,b)=>a-b);
  return `<table><thead><tr><th>Година</th>${cols.map(c=>`<th>${c.label}</th>`).join('')}</tr></thead><tbody>${years.map(y=>`<tr><td>${y}</td>${cols.map(c=>{const v=get(c.data,y);return `<td>${v==null?'—':num(v)}</td>`}).join('')}</tr>`).join('')}</tbody></table>`;
}
function observeSize(el, draw){ let w=0; new ResizeObserver(()=>{ if (el.clientWidth!==w){ w=el.clientWidth; draw(); } }).observe(el); }

/* ---------- line chart ---------- */
function lineChart(el, cfg){
  const draw = () => {
    const series = cfg.seriesFn ? cfg.seriesFn() : cfg.series;
    const W = el.clientWidth, H = cfg.h || (W < 520 ? 240 : 290);
    const m = {t:18, r: W<520? 58: (cfg.rm||96), b:26, l:cfg.lm||44};
    const iw = W-m.l-m.r, ih = H-m.t-m.b;
    const x = v => m.l + (v-cfg.x0)/(cfg.x1-cfg.x0)*iw;
    const y = v => m.t + ih - (v-cfg.y0)/(cfg.y1-cfg.y0)*ih;
    const lo = Math.min(cfg.y0,cfg.y1), hi = Math.max(cfg.y0,cfg.y1), clamp = v => Math.max(lo,Math.min(hi,v));
    let s = `<svg viewBox="0 0 ${W} ${H}" height="${H}" role="img" aria-label="${cfg.aria}">`;
    if (cfg.band){ const [a,b]=cfg.band; s += `<rect class="band-hl" x="${x(a-0.5)}" y="${m.t}" width="${x(b+0.5)-x(a-0.5)}" height="${ih}"/><text class="band-lbl" x="${x(a-0.5)+4}" y="${m.t+11}">ТАЗИ ГЛАВА</text>`; }
    cfg.yTicks.forEach(t => { s += `<line class="grid" x1="${m.l}" x2="${m.l+iw}" y1="${y(t)}" y2="${y(t)}"/><text x="${m.l-6}" y="${y(t)+4}" text-anchor="end">${cfg.yFmt?cfg.yFmt(t):num(t)}</text>`; });
    const step = cfg.xStep || (W < 520 ? 10 : 5);
    for (let t=Math.ceil(cfg.x0/step)*step; t<=cfg.x1; t+=step) s += `<text x="${x(t)}" y="${H-6}" text-anchor="middle">${t}</text>`;
    s += `<line class="axis" x1="${m.l}" x2="${m.l+iw}" y1="${m.t+ih}" y2="${m.t+ih}"/>`;
    if (cfg.zero || cfg.ref!=null) s += `<line x1="${m.l}" x2="${m.l+iw}" y1="${y(cfg.ref??0)}" y2="${y(cfg.ref??0)}" stroke="var(--ink-2)" stroke-width="1" opacity=".5"/>${cfg.refLbl?`<text x="${m.l+4}" y="${y(cfg.ref??0)-5}" class="lbl" style="font-size:10.5px">${cfg.refLbl}</text>`:''}`;
    (cfg.notes||[]).forEach(n => { s += `<line x1="${x(n.x)}" x2="${x(n.x)}" y1="${m.t+14}" y2="${m.t+ih}" stroke="var(--line)" stroke-dasharray="2 3"/><text x="${x(n.x)+4}" y="${m.t+ (n.dy||24)}" class="lbl" style="font-size:10.5px">${n.text}</text>`; });
    const endLabels = [];
    series.forEach(se => {
      if (se.band && se.band.length){ const up = se.band.map(p=>`${x(p[0]).toFixed(1)},${y(clamp(p[2])).toFixed(1)}`), dn = [...se.band].reverse().map(p=>`${x(p[0]).toFixed(1)},${y(clamp(p[1])).toFixed(1)}`); s += `<path d="M${up.join('L')}L${dn.join('L')}Z" fill="${se.color}" opacity="${se.bandOpacity||.14}"/>`; }
      const pts = (se.data||[]).filter(p=>p[0]>=cfg.x0 && p[0]<=cfg.x1 && p[1]!=null);
      if(!pts.length) return;
      const dpath = pts.map((p,i)=>`${i && (p[0]-pts[i-1][0] <= (cfg.gap||1))?'L':'M'}${x(p[0]).toFixed(1)},${y(clamp(p[1])).toFixed(1)}`).join('');
      if (se.area) s += `<path d="${dpath}L${x(pts[pts.length-1][0])},${y(cfg.y0)}L${x(pts[0][0])},${y(cfg.y0)}Z" fill="${se.color}" opacity=".10"/>`;
      s += `<path d="${dpath}" fill="none" stroke="${se.color}" stroke-width="${se.w||2}" stroke-linejoin="round" stroke-linecap="round" ${se.dash?'stroke-dasharray="5 4"':''}/>`;
      const lp = pts[pts.length-1];
      s += `<circle cx="${x(lp[0])}" cy="${y(clamp(lp[1]))}" r="${se.w>2?4.5:3.5}" fill="${se.color}" stroke="var(--card)" stroke-width="2"/>`;
      if (!se.noLabel) endLabels.push({y:y(clamp(lp[1])), x:x(lp[0]), text:`${cfg.vFmt?cfg.vFmt(lp[1]):num(lp[1])} ${se.short||''}`, strong:se.w>2});
    });
    endLabels.sort((a,b)=>a.y-b.y); for(let i=1;i<endLabels.length;i++) if(endLabels[i].y-endLabels[i-1].y<13) endLabels[i].y=endLabels[i-1].y+13;
    endLabels.forEach(l => s += `<text class="lbl" x="${l.x+8}" y="${l.y+4}" ${l.strong?'style="font-weight:600;fill:var(--ink)"':''}>${l.text}</text>`);
    s += `<line class="xh" x1="0" x2="0" y1="${m.t}" y2="${m.t+ih}" visibility="hidden"/><g class="dots"></g>`;
    s += `<rect x="${m.l}" y="${m.t}" width="${iw}" height="${ih}" fill="transparent" class="hit"/></svg>`;
    el.innerHTML = s;
    const svg = el.querySelector('svg'), xh = svg.querySelector('.xh'), dots = svg.querySelector('.dots');
    const move = ev => {
      const r = svg.getBoundingClientRect();
      const px = (ev.clientX - r.left) * (W / r.width);
      const yr = Math.round(cfg.x0 + (px-m.l)/iw*(cfg.x1-cfg.x0));
      if (yr<cfg.x0||yr>cfg.x1) return;
      xh.setAttribute('x1',x(yr)); xh.setAttribute('x2',x(yr)); xh.setAttribute('visibility','visible');
      let rows='', dd='';
      [...series].map(se=>({se,v:get(se.data,yr)})).filter(o=>o.v!=null).sort((a,b)=>b.v-a.v).forEach(({se,v}) => { rows += `<div class="r"><span><i style="background:${se.color}"></i>${se.label}</span><span>${cfg.vFmt?cfg.vFmt(v):num(v)}</span></div>`; dd += `<circle cx="${x(yr)}" cy="${y(clamp(v))}" r="4.5" fill="${se.color}" stroke="var(--card)" stroke-width="2"/>`; });
      dots.innerHTML = dd;
      const ctx = cfg.ctx ? cfg.ctx(yr) : '';
      if (rows) showTip(`<b>${yr}</b>${rows}${ctx}`, ev.clientX, ev.clientY); else hideTip();
    };
    svg.querySelector('.hit').addEventListener('pointermove', move);
    svg.querySelector('.hit').addEventListener('pointerleave', ()=>{ hideTip(); xh.setAttribute('visibility','hidden'); dots.innerHTML=''; });
  };
  observeSize(el, draw);
  return draw;
}

/* ---------- bar chart ---------- */
function barChart(el, cfg){
  const draw = () => {
    const W = el.clientWidth, H = cfg.h || (W<520?220:260);
    const m = {t:22,r:12,b:26,l:cfg.lm||44}, iw=W-m.l-m.r, ih=H-m.t-m.b;
    const n = cfg.x1-cfg.x0+1, bw = iw/n;
    const x = v => m.l + (v-cfg.x0)*bw;
    const y = v => m.t + ih - (Math.min(v,cfg.y1)-cfg.y0)/(cfg.y1-cfg.y0)*ih;
    let s = `<svg viewBox="0 0 ${W} ${H}" height="${H}" role="img" aria-label="${cfg.aria}">`;
    if (cfg.band){ const [a,b]=cfg.band; s += `<rect class="band-hl" x="${x(a)}" y="${m.t}" width="${x(b+1)-x(a)}" height="${ih}"/>${cfg.bandBottom?'':`<text class="band-lbl" x="${x(a)+4}" y="${m.t+11}">ТАЗИ ГЛАВА</text>`}`; }
    cfg.yTicks.forEach(t => s += `<line class="grid" x1="${m.l}" x2="${m.l+iw}" y1="${y(t)}" y2="${y(t)}"/><text x="${m.l-6}" y="${y(t)+4}" text-anchor="end">${cfg.yFmt?cfg.yFmt(t):num(t)}</text>`);
    const step = cfg.xStep || (W<520?10:5);
    for (let t=Math.ceil(cfg.x0/step)*step; t<=cfg.x1; t+=step) s += `<text x="${x(t)+bw/2}" y="${H-6}" text-anchor="middle">${t}</text>`;
    const gap = Math.min(2, bw*0.25);
    cfg.data.forEach(([yr,v]) => {
      if (yr<cfg.x0||yr>cfg.x1) return;
      const y0 = y(Math.max(cfg.y0,0)), y1 = y(v), top=Math.min(y0,y1), h=Math.max(1,Math.abs(y1-y0));
      s += `<rect data-y="${yr}" x="${x(yr)+gap/2}" y="${top}" width="${Math.max(1,bw-gap)}" height="${h}" rx="${Math.min(2,bw/4)}" fill="${cfg.color(v,yr)}"/>`;
      if (v>cfg.y1) s += `<text class="lbl" x="${x(yr)+bw/2}" y="${m.t-6}" text-anchor="middle">${cfg.vFmt(v)} ▲</text><line x1="${x(yr)}" x2="${x(yr)+bw}" y1="${m.t+6}" y2="${m.t+2}" stroke="var(--card)" stroke-width="3"/>`;
    });
    s += `<line class="axis" x1="${m.l}" x2="${m.l+iw}" y1="${y(Math.max(cfg.y0,0))}" y2="${y(Math.max(cfg.y0,0))}"/>`;
    (cfg.labels||[]).forEach(l => { const v=get(cfg.data,l.x); if(v==null) return; const yy = v>=0? y(v)-6 : y(v)+13; s += `<text class="lbl" x="${x(l.x)+bw/2}" y="${yy}" text-anchor="${l.anchor||'middle'}">${l.text||cfg.vFmt(v)}</text>`; });
    s += `<rect x="${m.l}" y="${m.t}" width="${iw}" height="${ih}" fill="transparent" class="hit"/></svg>`;
    el.innerHTML = s;
    const svg = el.querySelector('svg');
    svg.querySelector('.hit').addEventListener('pointermove', ev => {
      const r = svg.getBoundingClientRect(); const px=(ev.clientX-r.left)*(W/r.width);
      const yr = cfg.x0 + Math.floor((px-m.l)/bw); const v = get(cfg.data, yr);
      svg.querySelectorAll('rect[data-y]').forEach(b => b.style.opacity = (+b.dataset.y===yr?1:.45));
      if (v==null){ hideTip(); return; }
      showTip(`<b>${yr}</b><div class="r"><span>${cfg.name}</span><span>${cfg.vFmt(v)}</span></div>${cfg.ctx?cfg.ctx(yr):''}`, ev.clientX, ev.clientY);
    });
    svg.querySelector('.hit').addEventListener('pointerleave', ()=>{ hideTip(); svg.querySelectorAll('rect[data-y]').forEach(b=>b.style.opacity=1); });
  };
  observeSize(el, draw);
}

