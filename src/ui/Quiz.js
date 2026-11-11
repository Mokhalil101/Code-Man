// Quiz interface (DOM): 10 question types, syntax highlighting, timer, submit/continue flow. Uses textContent only (no unsafe HTML).
const KW = {
  Python:'def class return if elif else for while in import from as with try except finally raise lambda not and or is None True False print pass break continue yield self range len',
  JavaScript:'function const let var return if else for while of in new class extends this null undefined true false typeof async await try catch throw switch case break continue console',
  Java:'public private protected static final class extends implements interface new return if else for while int double boolean String void null true false this super try catch throw abstract',
  'C++':'int double float bool char void class struct public private protected virtual const static return if else for while new delete cout cin endl include using namespace std true false nullptr auto template'
};
function highlight(code, lang, target){
  const set = new Set((KW[lang]||KW.Python).split(' ')), re=/(#.*|\/\/.*)|("(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')|\b(\d+\.?\d*)\b|\b([A-Za-z_]\w*)\b|([\s\S])/g;
  let m, buf='';
  const flush=()=>{ if (buf) { target.append(document.createTextNode(buf)); buf=''; } };
  const span=(c,t)=>{ flush(); target.append(h('span',{class:c},t)); };
  while ((m=re.exec(code))) {
    if (m[1]) span('tk-c',m[1]); else if (m[2]) span('tk-s',m[2]); else if (m[3]) span('tk-n',m[3]);
    else if (m[4]&&set.has(m[4])) span('tk-k',m[4]); else buf+=m[0];
  }
  flush();
}
const Quiz = {
  active:false, current:null, _t:null, _kd:null,
  limitFor(q){ return q.timeLimit || (q.type==='arrange'?45:{1:15,2:20,3:25}[q.difficulty]||20); },
  open(q, meta, cb){
    if (this.active) return;               // never two quizzes at once (NFR-016)
    this.active=true; this.current=q;
    const root=$('#quiz'), box=$('.box',root); box.textContent='';
    const limit=this.limitFor(q); let left=limit, done=false, sel=-1, order=[]; const idx=q.type==='arrange'?q.lines.map((_,i)=>i):[]; const pool=idx.slice().sort(()=>Math.random()-.5);
    const bar=h('i'), secs=h('b',{},limit), submit=h('button',{class:'btn primary',disabled:true},'Submit'), fb=h('div',{class:'qfb'}), body=h('div',{class:'qbody'});
    const stars='★'.repeat(q.difficulty)+'☆'.repeat(3-q.difficulty);
    box.append(
      h('div',{class:'qhead'}, h('span',{class:'chip c-blue'},q.category||'Programming'), h('span',{class:'chip c-green'},q.language||'General'), h('span',{class:'chip c-yellow'},stars),
        h('span',{class:'chip c-red'},'Question '+meta.n), h('span',{class:'qbrand'},'GDG Assiut · CODE MAN'), h('span',{class:'qprog'},'Quiz '+meta.done+' / '+meta.total)),
      h('div',{class:'qtimer'}, h('div',{class:'qbar'},bar), secs),
      h('div',{class:'qtext'},q.question));
    if (q.code) { const pre=h('pre',{class:'qcode'}); highlight(q.code,q.language,pre); box.append(pre); }
    box.append(body, fb, h('div',{class:'qactions'},submit)); root.hidden=false;
    const refresh=()=>{ submit.disabled = done || (q.type==='arrange' ? order.length!==q.lines.length : sel<0); };
    let optEls=[];
    if (q.type==='arrange') {
      const ans=h('div',{class:'arr-ans'}), src=h('div',{class:'arr-src'}); body.append(h('div',{class:'arr-label'},'Your order (tap a line to remove it):'),ans,h('div',{class:'arr-label'},'Available lines:'),src);
      const draw=()=>{ ans.textContent=''; src.textContent='';
        order.forEach((i,k)=>ans.append(h('button',{class:'arr-line',onclick:()=>{ if(done)return; order.splice(k,1); draw(); }},(k+1)+'.  '+q.lines[i])));
        pool.filter(i=>!order.includes(i)).forEach(i=>src.append(h('button',{class:'arr-line',onclick:()=>{ if(done)return; order.push(i); draw(); }},q.lines[i])));
        if (!order.length) ans.append(h('div',{class:'arr-empty'},'Tap lines below to build the program')); refresh(); };
      draw();
    } else {
      q.options.forEach((t,i)=>{ const b=h('button',{class:'opt'+(t.includes('\n')?' multi':''),onclick:()=>{ if(done)return; sel=i; optEls.forEach((o,j)=>o.classList.toggle('sel',j===i)); refresh(); }},h('b',{},'ABCDEF'[i]),h('span',{},t)); optEls.push(b); body.append(b); });
    }
    const finish=(timeout)=>{
      if (done) return; done=true; clearInterval(this._t); refresh();
      const ok = !timeout && (q.type==='arrange' ? order.every((v,k)=>v===k) : sel===q.correctAnswer);
      if (q.type!=='arrange') optEls.forEach((o,i)=>{ o.disabled=true; if(i===q.correctAnswer) o.classList.add('ok'); else if(i===sel) o.classList.add('bad'); });
      else { $$('.arr-line',body).forEach(b=>b.disabled=true); if(!ok) fb.append(h('pre',{class:'qcode'},'Correct order:\n'+q.lines.join('\n'))); }
      fb.prepend(h('div',{class:'verdict '+(ok?'good':'bad')}, timeout?'⏱ Time is up!':ok?'✔ Correct!':'✘ Not quite.'), h('div',{class:'expl'},q.explanation||''));
      submit.disabled=false; submit.textContent='Continue ▶'; submit.onclick=()=>this.close(()=>cb({ok,fast:ok&&left>limit*.5,timeout,q})); submit.focus();
    };
    submit.onclick=()=>finish(false);
    this._kd=e=>{ if(!this.active) return;
      if (e.key==='Enter') { e.preventDefault(); if(!submit.disabled) submit.click(); }
      else if (!done && q.type!=='arrange' && /^[1-6]$/.test(e.key) && optEls[+e.key-1]) optEls[+e.key-1].click(); };
    document.addEventListener('keydown',this._kd);
    const t0=Date.now(); this._t=setInterval(()=>{ left=Math.max(0,limit-(Date.now()-t0)/1000); bar.style.width=(left/limit*100)+'%'; bar.className=left<limit*.25?'low':''; secs.textContent=Math.ceil(left); if(left<=0) finish(true); },100);
  },
  close(next){ clearInterval(this._t); document.removeEventListener('keydown',this._kd); $('#quiz').hidden=true; this.active=false; this.current=null; if(next) next(); }
};
