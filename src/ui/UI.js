// DOM user interface: HUD, menus, world map, tutorial, achievements, statistics, leaderboard, settings, about, pause, results, toasts.
// Visual style: "sticker arcade" (see styles/main.css). Icons are small inline SVGs built from constant strings.
const ICON = {
  play:'<path d="M7 4.5v15l12-7.5z" fill="currentColor" stroke-width="2"/>',
  map:'<path d="M3 6.5l6-3 6 3 6-3v14l-6 3-6-3-6 3z"/><path d="M9 3.5v14M15 6.5v14"/>',
  help:'<path d="M8.6 9a3.5 3.5 0 1 1 5.1 3.1c-1.1.6-1.7 1.3-1.7 2.6"/><circle cx="12" cy="19.2" r="1.4" fill="currentColor" stroke="none"/>',
  trophy:'<path d="M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M7 6H4.5a2.6 2.6 0 0 0 3 3.6M17 6h2.5a2.6 2.6 0 0 1-3 3.6M12 14v4M8 20h8"/>',
  stats:'<path d="M5 20v-7M12 20V5M19 20v-10"/>',
  podium:'<path d="M3 20v-6h6v6M9 20V7h6v13M15 20v-8h6v8"/>',
  gear:'<path d="M4 7h9M18 7h2M4 17h3M12 17h8"/><circle cx="15.5" cy="7" r="2.4"/><circle cx="9.5" cy="17" r="2.4"/>',
  heart:'<path d="M12 20s-7.5-4.6-7.5-10.2A4.2 4.2 0 0 1 12 7.3a4.2 4.2 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20z" fill="currentColor" stroke-width="2"/>',
  back:'<path d="M15 5l-7 7 7 7"/>', next:'<path d="M9 5l7 7-7 7"/>', check:'<path d="M5 12.5l4.5 4.5L19 7.5"/>',
  lock:'<rect x="5" y="11" width="14" height="10" rx="2.5" fill="currentColor"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
  restart:'<path d="M4.5 12a7.5 7.5 0 1 0 2.2-5.3"/><path d="M4 4v4.5h4.5"/>', home:'<path d="M4 11.5L12 4l8 7.5"/><path d="M6.5 10v10h11V10"/>',
  expand:'<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>'
};
const icon = (n, sz=22) => { const s=document.createElement('span'); s.innerHTML=`<svg width="${sz}" height="${sz}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON[n]}</svg>`; return s.firstChild; };
const HEART = lost => `<svg viewBox="0 0 24 24" class="${lost?'lost':''}" aria-hidden="true"><path d="M12 21s-8-5.2-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.8-8 11-8 11z" fill="${lost?'#3A2F6E':'#EA4335'}" stroke="#1B1340" stroke-width="2.2" stroke-linejoin="round"/>${lost?'':'<path d="M8 8.5a2 2 0 0 1 2-1.5" stroke="#fff" stroke-width="1.6" fill="none" stroke-linecap="round"/>'}</svg>`;
const STAR = (on, i) => { const s=document.createElement('span'); s.innerHTML=`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.8l2.8 5.8 6.3.9-4.6 4.4 1.1 6.3L12 17.2 6.4 20.2l1.1-6.3L2.9 9.5l6.3-.9z" fill="${on?'#FBBC04':'#4A3F7A'}" stroke="#1B1340" stroke-width="1.5" stroke-linejoin="round"/>${on&&i===1?'<path d="M9 8.8l1.3-.2" stroke="#fff" stroke-width="1" stroke-linecap="round"/>':''}</svg>`; return s.firstChild; };
const GDG_DOTS = () => h('span',{class:'gdg-dots'}, ...['#4285F4','#EA4335','#FBBC04','#34A853'].map(c=>h('i',{style:'background:'+c})));
const GDG_TAG = () => h('div',{class:'gdg-tag'}, GDG_DOTS(), h('span',{}, 'Powered by '), h('b',{}, 'GDG Assiut'));
const LOGO = (cls='') => h('h1',{class:'logo '+cls}, h('span',{class:'lg-row'}, ...[['C','b'],['O','r'],['D','y'],['E','g']].map(([c,k])=>h('span',{class:'lc-'+k},c))), h('span',{class:'lg-row lg-man'},'MAN'));
const BUG = c => h('div',{class:'bug',style:'--c:'+c}, h('span',{class:'be'}), h('span',{class:'be'}), h('span',{class:'bm'}));
const fmtTime = s => Math.floor(s/60)+':'+String(Math.floor(s%60)).padStart(2,'0');
const fmtN = n => Number(n||0).toLocaleString('en-US');
const prand = (i, m) => ((Math.sin(i*78.233)*43758.5453)%1+1)%1*m;
const CONFETTI = () => h('div',{class:'confetti','aria-hidden':'true'}, ...Array.from({length:46},(_,i)=>{ const w=8+Math.round(prand(i+1,10)), round=i%3===0;
  return h('i',{style:`left:${prand(i,100).toFixed(1)}%;width:${w}px;height:${round?w:Math.round(w*.5)}px;border-radius:${round?'50%':'2px'};background:${['#4285F4','#EA4335','#FBBC04','#34A853','#FFF6E0','#A142F4'][i%6]};animation-duration:${(5+prand(i+6,5)).toFixed(1)}s;animation-delay:-${prand(i+8,8).toFixed(1)}s`}); }));
const HUD = {
  refit(){ setTimeout(()=>{ try{ App.game.scale.refresh(); }catch(e){} },30); },
  show(){ this._pk=''; this._lv=null; this._bi=''; $('#hud').hidden=false; document.body.classList.add('playing'); this.refit(); }, hide(){ $('#hud').hidden=true; document.body.classList.remove('playing'); $('#joy').hidden=true; this.refit(); },
  _pk:'', _lv:null, _bi:'',
  set(s){
    $('#h-score').textContent=fmtN(s.score);
    if (s.lives!==this._lv) { this._lv=s.lives; const box=$('#h-lives'); box.innerHTML=''; for (let i=0;i<Math.max(3,s.lives);i++) box.insertAdjacentHTML('beforeend',HEART(i>=s.lives)); box.setAttribute('aria-label',Math.max(0,s.lives)+' lives'); }
    $('#h-xp').textContent=s.xp; $('#h-world').textContent=s.world; $('#h-time').textContent=fmtTime(s.time);
    const bits=$('#h-bits'); if (s.bitsTotal) { bits.textContent=s.bitsTotal-s.bits; bits.append(h('em',{},'/'+s.bitsTotal)); } else bits.textContent=s.bits;
    const pk=JSON.stringify(s.powers.map(p=>[p.icon,p.left])); if (pk!==this._pk) { this._pk=pk; const box=$('#h-powers'); box.textContent='';
      s.powers.forEach(p=>box.append(h('span',{class:'pw '+(p.cd?'cd':''),title:p.name},h('img',{src:'assets/sprites/'+p.icon+'.png',alt:''}),h('em',{},p.name+' '+p.left)))); }
    const b=$('#h-boss'); b.hidden=!s.boss; if (s.boss) { $('.boss-name',b).textContent=s.boss.name; $('.bar i',b).style.width=(s.boss.hp/s.boss.max*100)+'%'; $('.boss-phase',b).textContent=s.boss.phase+'  ·  HP '+s.boss.hp+'/'+s.boss.max;
      if (s.bossIcon && s.bossIcon!==this._bi) { this._bi=s.bossIcon; $('.boss-ico',b).src='assets/sprites/'+s.bossIcon+'.png'; } }
  }
};
const UI = {
  cur:null, retPause:false,
  init(){
    $('#h-pause').addEventListener('click',()=>App.pause()); this.joystick();
    const bg=$('#bgcode'), r=(i,m)=>((Math.sin(i*12.9898)*43758.5453)%1+1)%1*m;
    for (let i=0;i<46;i++) { const sz=2+Math.round(r(i+7,4)); bg.append(h('span',{class:'star',style:`left:${r(i,100).toFixed(1)}%;top:${r(i+3,100).toFixed(1)}%;width:${sz}px;height:${sz}px;animation-duration:${(2+r(i+5,3)).toFixed(1)}s;animation-delay:-${r(i+9,3).toFixed(1)}s`})); }
    [['{ }','g1'],['</>','g2'],[';','g3'],['( )','g4']].forEach(([t,c])=>bg.append(h('span',{class:'glyph '+c},t)));
  },
  clear(){ $('#screens').textContent=''; this.cur=null; },
  screen(name, ...kids){ this.clear(); this.cur=name; const s=h('div',{class:'screen s-'+name},...kids); $('#screens').append(s); $('#screens').hidden=false; $('#screens').scrollTop=0; return s; },
  hideAll(){ this.clear(); $('#screens').hidden=true; $('#modal').hidden=true; $('#modal').textContent=''; },
  btn(label,fn,cls=''){ return h('button',{class:'btn '+cls,onclick:()=>{ Audio.sfx('click'); fn(); }},label); },
  back(fn=()=>App.menu()){ return this.btn([icon('back',20),'Back'],fn,'ghost back'); },
  toast(msg,color='#4285F4'){ const t=h('div',{class:'toast',style:'--c:'+color},msg); $('#toasts').append(t); setTimeout(()=>t.remove(),3200); },
  banner(title,sub,color){ const b=$('#banner'); b.textContent=''; b.append(h('div',{class:'bn-card'},h('div',{class:'bn-t',style:'--c:'+(color||'#FFF6E0')},title),h('div',{class:'bn-s'},sub||''))); b.hidden=false; b.classList.remove('go'); void b.offsetWidth; b.classList.add('go'); clearTimeout(this._bt); this._bt=setTimeout(()=>b.hidden=true,2600); },
  modal(...kids){ const m=$('#modal'); m.textContent=''; m.classList.remove('wide'); m.append(h('div',{class:'dialog'},...kids)); m.hidden=false; },
  closeModal(){ $('#modal').hidden=true; $('#modal').textContent=''; },
  confirm(msg,yes,no=()=>{}){ this.modal(h('p',{},msg),h('div',{class:'row'},this.btn('Yes',()=>{this.closeModal();yes();},'primary'),this.btn('Cancel',()=>{this.closeModal();no();},'ghost'))); },
  progressPct(){ return Math.round(Progress.worlds()/7*100); },
  // ---------- main menu ----------
  menu(){
    const r=Progress.rank(), ri=Progress.rankIdx(), next=Progress.nextRank(), hasProg=SAVE.xp>0||SAVE.unlocked>1||Progress.worlds()>0, cw=Math.min(7,SAVE.unlocked);
    const xpPct=next?Math.max(0,Math.min(100,Math.round((SAVE.xp-r.xp)/(next.xp-r.xp)*100))):100;
    const play=h('button',{class:'btn primary play',onclick:()=>{ Audio.sfx('click'); App.play(); }}, icon('play',34), 'PLAY');
    const cont=h('button',{class:'btn cont',onclick:()=>{ Audio.sfx('click'); App.continue(); }}, 'Continue', h('small',{}, hasProg?'World '+cw:'no save yet'));
    if (!hasProg) { cont.disabled=true; cont.title='Play first to create progress'; }
    const bub=(label,ic,bg,fn)=>h('button',{class:'btn bub',style:'--bg:'+bg,onclick:()=>{ Audio.sfx('click'); fn(); }}, h('span',{class:'bub-ico'},icon(ic,30)), h('span',{class:'bub-lbl'},label));
    const icons=[['World Map','map','#34A853',()=>this.worldMap()],['How to Play','help','#FBBC04',()=>this.tutorial(false)],['Achievements','trophy','#EA4335',()=>this.achievements()],
      ['Statistics','stats','#C2A3FF',()=>this.stats()],['Leaderboard','podium','#4285F4',()=>this.leaderboard()],['Settings','gear','#FFF6E0',()=>this.settings()],['About GDG Assiut','heart','#FF8FB1',()=>this.about()]];
    const stage=h('div',{class:'stage','aria-hidden':'true'}, h('div',{class:'dots'}), h('div',{class:'st-bits'},h('i'),h('i'),h('i')),
      h('span',{class:'cm-hero'},h('i',{class:'cm-eye'})), h('div',{class:'st-bugs'}, ...['#EA4335','#FBBC04','#34A853'].map(BUG)), h('span',{class:'nom'},'nom!'));
    this.screen('menu',
      h('div',{class:'menu-left'}, GDG_TAG(), LOGO(), h('p',{class:'tagline'},'Gobble code. Dodge bugs. Become a Code Legend!'),
        h('div',{class:'menu-btns'}, h('div',{class:'menu-main'},play,cont), h('nav',{class:'menu-icons','aria-label':'More'}, icons.map(([l,ic,bg,f])=>bub(l,ic,bg,f))))),
      h('div',{class:'menu-right'}, stage,
        h('div',{class:'card rank-card'}, h('div',{class:'rank-top'}, h('span',{class:'rank-num'},ri+1), h('div',{class:'rk'},h('span',{},'Your rank'),h('b',{},r.n)),
            h('div',{class:'rk r'},h('span',{},'Best score'),h('b',{},fmtN(SAVE.best)))),
          h('div',{class:'meter'},h('i',{style:'width:'+xpPct+'%'})),
          h('small',{},(next?(next.xp-SAVE.xp)+' XP to '+next.n:'Max rank — you are a Code Legend!')+'  ·  '+Progress.worlds()+' of 7 worlds cleared  ·  World '+cw+' unlocked'))));
  },
  // ---------- world map ----------
  worldMap(sel){
    sel = sel || Math.min(7, SAVE.unlocked); const pos=[[9,64],[23,30],[38,64],[53,28],[68,62],[82,28],[92,66]];
    const svgNS='http://www.w3.org/2000/svg', svg=document.createElementNS(svgNS,'svg'); svg.setAttribute('viewBox','0 0 100 100'); svg.setAttribute('preserveAspectRatio','none'); svg.setAttribute('class','map-svg');
    const line=document.createElementNS(svgNS,'polyline'); line.setAttribute('points',pos.map(p=>p.join(',')).join(' ')); line.setAttribute('vector-effect','non-scaling-stroke'); svg.append(line);
    const map=h('div',{class:'map'},svg);
    DATA.worlds.forEach((w,i)=>{ const id=i+1, locked=id>SAVE.unlocked, done=!!SAVE.completed[id];
      map.append(h('button',{class:'node'+(locked?' locked':'')+(done?' done':'')+(id===sel?' sel':''),style:`left:${pos[i][0]}%;top:${pos[i][1]}%;--ac:${w.theme.accent}`,'aria-label':'World '+id+' '+w.name+(locked?' (locked)':''),onclick:()=>{ Audio.sfx('click'); this.worldMap(id); }},
        h('b',{},locked?icon('lock',26):id), h('small',{},w.name), h('span',{class:'stars'},'★'.repeat(SAVE.stars[id]||0)+'☆'.repeat(3-(SAVE.stars[id]||0))))); });
    const w=DATA.worlds[sel-1], locked=sel>SAVE.unlocked;
    const info=h('div',{class:'card glass world-info',style:'--ac:'+w.theme.accent},
      h('h2',{},'World '+sel+' — '+w.name), h('p',{},w.subtitle),
      h('div',{class:'kv'},h('span',{},'Difficulty'),h('b',{},w.difficulty)), h('div',{class:'kv'},h('span',{},'Challenges'),h('b',{},(w.mazeLayout.join('').split('Q').length-1)+' quiz nodes · '+w.boss.hp+' boss hits')),
      h('div',{class:'kv'},h('span',{},'Boss'),h('b',{},w.boss.name+(SAVE.completed[sel]?'  ✔ defeated':''))), h('div',{class:'kv'},h('span',{},'Rating'),h('b',{style:'color:#E0A800'},'★'.repeat(SAVE.stars[sel]||0)+'☆'.repeat(3-(SAVE.stars[sel]||0)))),
      h('div',{class:'kv'},h('span',{},'Status'),h('b',{},locked?'Locked — complete World '+(sel-1):SAVE.completed[sel]?'Completed':'Available')),
      h('p',{class:'mech'},w.mechanic), locked?h('div',{class:'lockmsg'},icon('lock',20),'Finish the previous world to unlock'):this.btn([icon('play',22),SAVE.completed[sel]?'Replay World '+sel:'Start World '+sel],()=>App.startWorld(sel),'primary'));
    this.screen('worldmap', h('h2',{class:'title'},'World Map'), map, info, this.back());
  },
  // ---------- tutorial ----------
  tutorial(startAfter){
    const S=(k)=>h('img',{src:'assets/sprites/'+k+'.png',alt:''});
    const steps=[
      ['Move','Use the Arrow Keys or WASD, a PlayStation / Xbox controller (left stick or D-pad), or the on-screen joystick / swipe. Your direction is buffered, so you can press early and turn at the next corner.',[S('pac0'),h('span',{class:'keys'},'↑ ← ↓ →  ·  W A S D  ·  D-pad')]],
      ['Collect Code Bits','Yellow Code Bits give +10 points. Bonus Chips give +250, green XP Orbs give XP and hidden stars are secrets.',[S('bit'),S('bit'),S('chip'),S('orb'),S('secret')]],
      ['Avoid the Bugs','Syntax chases you, Logic predicts you, Runtime blocks your escape and Memory remembers where you were. You have 3 lives.',[S('bug0'),S('bug1'),S('bug2'),S('bug3')]],
      ['Power-ups','U Power Compiler freezes bugs (touch them to squash). S Speed. D Shield. M XP x2. K Scanner reveals secrets. L Teleport Chip. Dash: Space / ✕ or □ on the controller.',['U','S','D','M','K','L'].map(k=>S('pu_'+k))],
      ['Quiz Nodes','Touch a purple ? node to pause the game and answer a programming question. Correct = points + XP. Wrong or timeout = penalty.',[S('quiz')]],
      ['Answering','Pick an answer (or press 1-4, or use the controller D-pad + ✕), then lock it in (Enter / △). Some questions ask you to arrange code lines in order. Read the explanation afterwards!',[h('span',{class:'keys'},'1 2 3 4  ·  Enter  ·  ✕ △')]],
      ['The Exit Gate','Collect every Code Bit, finish all quiz nodes and defeat the world boss. Then the gate turns green — step in!',[S('exit0'),h('span',{class:'arrow'},'→'),S('exit1')]],
      ['Bosses','Touch the boss to face a challenge. Every correct answer damages it; a wrong answer costs a life. Bosses dash, teleport, summon and shield — watch for warnings.',[S('boss1'),S('boss4'),S('boss7')]],
      ['Score & XP','Points: bit 10 · answer 100 (+50 fast) · chip 250 · bug 200 · world 500 (+300 flawless). XP raises your rank from Beginner Coder to Code Legend.',[h('span',{class:'keys'},'Beginner → Legend')]]];
    let i=0; const finish=()=>{ SAVE.settings.tutorial=true; Save.save(); startAfter?App.startWorld(1,true):App.menu(); };
    const draw=()=>{ const [t,d,vis]=steps[i];
      this.screen('tutorial', h('div',{class:'card glass tut'}, h('span',{class:'step'},'Step '+(i+1)+' / '+steps.length), h('h2',{},t), h('div',{class:'vis'},vis), h('p',{},d),
        h('div',{class:'row'}, i>0?this.btn([icon('back',18),'Back'],()=>{i--;draw();},'ghost'):'', this.btn('Skip',finish,'ghost'), i<steps.length-1?this.btn('Next ▶',()=>{i++;draw();},'primary'):this.btn(startAfter?'Start World 1':'Done',finish,'primary go')))); };
    draw();
  },
  // ---------- achievements / stats / leaderboard ----------
  achievements(){
    const got=Object.keys(SAVE.ach).length;
    this.screen('ach', h('h2',{class:'title'},'Achievements  '+got+' / '+DATA.ach.length),
      h('div',{class:'grid ach-grid'}, DATA.ach.map(a=>{ const on=!!SAVE.ach[a.id], pr=a.type==='stat'?[Math.min(Progress.value(a),a.min),a.min]:null;
        return h('div',{class:'card glass ach'+(on?' on':'')}, h('div',{class:'ico'},a.icon), h('div',{},h('b',{},a.name),h('small',{},a.desc),
          pr&&!on?h('div',{class:'meter'},h('i',{style:'width:'+(pr[0]/pr[1]*100)+'%'})):'', pr&&!on?h('small',{},pr[0]+' / '+pr[1]):h('small',{class:'ok'},on?'Unlocked':'Locked'))); })), this.back());
  },
  stats(){
    const s=SAVE.stats, r=Progress.rank(), nx=Progress.nextRank(), tot=s.correct+s.wrong;
    const rows=[['Total score (all runs)',s.score],['Highest score',SAVE.best],['Total XP',SAVE.xp],['Current rank',r.n],['Questions answered',s.questions],['Correct answers',s.correct],['Wrong answers',s.wrong],
      ['Accuracy',Progress.accuracy()+'%'],['Best answer streak',s.bestStreak],['Enemies defeated',s.enemies],['Collectibles collected',s.bits],['Secrets found',s.secrets],['Bosses defeated',s.bosses],
      ['Levels completed',s.levels],['Worlds completed',Progress.worlds()+' / 7'],['Total play time',fmtTime(s.time)],['Deaths',s.deaths]];
    this.screen('stats', h('h2',{class:'title'},'Statistics'), h('div',{class:'card glass'}, h('div',{class:'kv'},h('span',{},'Rank'),h('b',{},r.n)), h('div',{class:'meter'},h('i',{style:'width:'+(nx?Math.min(100,(SAVE.xp-r.xp)/(nx.xp-r.xp)*100):100)+'%'})), h('small',{},nx?SAVE.xp+' / '+nx.xp+' XP → '+nx.n:'Maximum rank reached')),
      h('div',{class:'grid stat-grid'}, rows.map(([k,v])=>h('div',{class:'card glass stat'},h('small',{},k),h('b',{},v)))), this.back());
  },
  leaderboard(){
    const top=Leaderboard.top(10);
    this.screen('lb', h('h2',{class:'title'},'Leaderboard'), h('div',{class:'badge'},Leaderboard.label), h('div',{class:'card glass'},
      top.length?h('table',{},h('thead',{},h('tr',{},['#','Score','World','XP','Accuracy','Result','Date'].map(x=>h('th',{},x)))),
        h('tbody',{},top.map((e,i)=>h('tr',{},h('td',{},i+1),h('td',{},fmtN(e.score)),h('td',{},e.world),h('td',{},e.xp),h('td',{},e.acc+'%'),h('td',{},e.result),h('td',{},e.date?new Date(e.date).toLocaleDateString():'-')))))
        :h('p',{class:'empty'},'No runs yet — finish or lose a game to record your first score.')),
      h('small',{},'These are your personal records stored on this device. A global leaderboard is not part of the static version.'), this.back());
  },
  // ---------- settings ----------
  settings(fromPause){
    const S=SAVE.settings, slider=(label,key)=>h('label',{class:'slider'},h('span',{},label),h('input',{type:'range',min:0,max:100,value:Math.round(S[key]*100),oninput:e=>{ S[key]=e.target.value/100; Audio.refresh(); Save.save(); },onchange:()=>Audio.sfx('click')}));
    const mute=h('input',{type:'checkbox',onchange:e=>{ S.mute=e.target.checked; Audio.refresh(); Save.save(); }}); mute.checked=S.mute;
    const rumble=h('input',{type:'checkbox',onchange:e=>{ S.rumble=e.target.checked; Save.save(); if(S.rumble) Pad.rumble(200,.6,.6); }}); rumble.checked=S.rumble!==false;
    const diff=h('select',{onchange:e=>{ S.diff=+e.target.value; Save.save(); }},['Easy','Normal','Hard'].map((n,i)=>h('option',{value:i},n))); diff.value=S.diff;
    const kids=[h('h2',{class:'title'},'Settings'), h('div',{class:'card glass settings'}, slider('Master volume','master'),slider('Music volume','music'),slider('Sound effects','sfx'),
      h('label',{class:'slider'},h('span',{},'Mute all'),mute), h('label',{class:'slider'},h('span',{},'Controller vibration'),rumble), Full.supported()?h('div',{class:'row'},this.btn([icon('expand',20),'Toggle fullscreen (F)'],()=>Full.toggle(),'ghost')):'', h('label',{class:'slider'},h('span',{},'Enemy speed (applies to next world run)'),diff),
      h('div',{class:'row'}, this.btn('Replay tutorial',()=>this.tutorial(false),'ghost'), this.btn('Reset progress',()=>this.confirm('Reset ALL progress, XP, achievements and settings? This cannot be undone.',()=>{ Save.reset(); Audio.refresh(); App.menu(); this.toast('Progress reset','#EA4335'); }),'danger')))];
    if (fromPause) { this.modal(...kids.slice(0), this.btn([icon('back',20),'Back to pause'],()=>this.pauseMenu(),'ghost')); $('#modal').classList.add('wide'); } else this.screen('settings',...kids,this.back());
  },
  about(){
    this.screen('about', h('div',{class:'card glass about'}, LOGO('small'), GDG_TAG(),
      h('p',{},'An interactive programming arcade experience designed to make learning, problem-solving, and software development more engaging through gameplay.'),
      h('h3',{},'Game objectives'), h('p',{},'Explore seven programming worlds, collect Code Bits, escape the bugs, answer questions in Python, C++, Java and JavaScript, defeat each world boss and finally shut down the Core Virus.'),
      h('h3',{},'About GDG Assiut'), h('p',{},'Google Developer Groups (GDG) are developer communities. This game is a community-inspired project made for GDG Assiut. It is not an official Google product.'),
      h('h3',{},'Credits'), h('p',{},'Game design, code, cartoon art and chiptune audio are original to this project. Built with Phaser 3. Fonts: Baloo 2 and JetBrains Mono (SIL OFL, via Google Fonts).'),
      h('p',{class:'ph'},'[ Developer / community team information — add your team here ]'), CONFIG.gdgLogo?h('img',{class:'gdg-logo',src:'assets/icons/gdg-assiut-logo.png',alt:'GDG Assiut'}):''), this.back());
  },
  // ---------- in-game overlays ----------
  pauseMenu(){
    this.modal(h('h2',{},'Paused'), h('div',{class:'col'}, this.btn([icon('play',20),'Resume'],()=>App.resume(),'primary'), this.btn([icon('restart',20),'Restart level'],()=>this.confirm('Restart this world? Current run progress is lost.',()=>App.startWorld(App.world),()=>this.pauseMenu()),''),
      this.btn([icon('gear',20),'Settings'],()=>this.settings(true),''), Full.supported()?this.btn([icon('expand',20),'Fullscreen'],()=>Full.toggle(),''):'', this.btn([icon('home',20),'Main menu'],()=>this.confirm('Leave the current run? Unfinished progress is lost.',()=>App.menu(),()=>this.pauseMenu()),'ghost')));
  },
  statsBlock(r){ return h('div',{class:'grid res-grid'}, [['score',fmtN(r.score)],['XP earned',r.xp],['questions',r.q],['accuracy',r.acc+'%'],['bugs squashed',r.enemies],['time',fmtTime(r.time)]].map(([k,v])=>h('div',{class:'card glass stat'},h('small',{},k),h('b',{},v)))); },
  savedLine(r, extra){ const rank=1+SAVE.history.filter(e=>e.score>r.score).length;
    return h('div',{class:'saved'}, h('span',{class:'ok-dot'},icon('check',18)), h('span',{},'Saved to this device’s leaderboard — you’re ',h('b',{},'#'+rank),'!',extra?'  '+extra:'')); },
  scoreBig(r, label='SCORE'){ return h('div',{class:'res-score'}, h('div',{class:'score-big'},h('span',{},label),h('b',{},fmtN(r.score))), r.newBest?h('span',{class:'new-best'},'NEW',h('br'),'BEST!'):''); },
  levelComplete(r){
    const w=DATA.worlds[r.world-1];
    this.screen('result', CONFETTI(), h('div',{class:'sunburst','aria-hidden':'true'}),
      h('div',{class:'result win'}, h('div',{class:'bigstars',role:'img','aria-label':r.stars+' of 3 stars'}, [0,1,2].map(i=>STAR(i<r.stars,i))),
        h('h1',{class:'big-title'},'WORLD '+r.world+' COMPLETE!'), h('p',{class:'res-sub'},w.name+' is free of bugs — '+w.boss.name+' defeated!'),
        this.scoreBig(r), this.statsBlock(r),
        h('div',{class:'res-chips'}, r.bonuses.map(b=>h('span',{class:'badge'},b[0]+'  +'+b[1])), r.ach.map(a=>h('span',{class:'badge',style:'background:#C8F0D0'},a.icon+' '+a.name))),
        this.savedLine(r, r.world<7?'World '+(r.world+1)+' — '+DATA.worlds[r.world].name+' unlocked!':''),
        h('div',{class:'row'}, this.btn([icon('map',20),'World Map'],()=>this.worldMap(Math.min(7,r.world+1))), this.btn([icon('home',20),'Menu'],()=>App.menu(),'ghost'), r.world<7?this.btn(['Next World',icon('next',22)],()=>App.startWorld(r.world+1),'primary go'):'')));
  },
  gameOver(r){
    this.screen('result', h('div',{class:'result lose'}, h('div',{class:'sad-bug st-bugs','aria-hidden':'true'}, ...['#EA4335','#FBBC04','#34A853'].map(BUG)),
      h('h1',{class:'big-title'},'GAME OVER'), h('p',{class:'res-sub'},'The bugs got you in '+DATA.worlds[r.world-1].name+'. Shake it off and try again!'),
      this.scoreBig(r,'FINAL SCORE'), this.statsBlock(r),
      h('div',{class:'res-chips'}, h('span',{class:'badge'},'Levels completed: '+SAVE.stats.levels), h('span',{class:'badge',style:'background:#C2D8FF'},'Rank: '+Progress.rank().n), r.ach.map(a=>h('span',{class:'badge',style:'background:#C8F0D0'},a.icon+' '+a.name))),
      this.savedLine(r),
      h('div',{class:'row'}, this.btn([icon('home',20),'Main menu'],()=>App.menu(),'ghost'), this.btn([icon('restart',22),'Retry'],()=>App.startWorld(r.world),'primary'))));
  },
  ending(r){
    const lines=['The Core Virus collapses into a thousand harmless bits of light…','Every world is compiled. Every bug is squashed.','Somewhere, a community of developers cheers.','You are no longer a beginner.','You are a CODE MAN.'];
    let done=false; const el=h('div',{class:'ending'}); const scr=this.screen('ending', el);
    const credits=()=>{ if(done)return; done=true; el.textContent=''; scr.prepend(CONFETTI(), h('div',{class:'sunburst','aria-hidden':'true'}));
      el.append(LOGO(), GDG_TAG(), h('p',{class:'res-sub'},'Eat Code. Escape Bugs. Master Programming.'), this.statsBlock(r),
      h('div',{class:'badge'},'Final rank: '+Progress.rank().n), r.ach.map(a=>h('div',{class:'badge',style:'background:#C8F0D0'},a.icon+' '+a.name)), h('div',{class:'row'},this.btn([icon('map',20),'World Map'],()=>this.worldMap(7)),this.btn([icon('home',20),'Main menu'],()=>App.menu(),'primary'))); };
    lines.forEach((l,i)=>setTimeout(()=>{ if(!done&&this.cur==='ending'){ el.textContent=''; el.append(h('p',{class:'story'},l),h('button',{class:'btn ghost skip',onclick:credits},'Skip ▶')); } },i*2600));
    setTimeout(()=>{ if(this.cur==='ending') credits(); },lines.length*2600);
  },
  // ---------- mobile joystick ----------
  joystick(){
    const j=$('#joy'), knob=$('.knob',j); let id=null, cx=0, cy=0;
    const move=(x,y)=>{ const dx=x-cx, dy=y-cy, d=Math.hypot(dx,dy), max=44; const k=d>max?max/d:1; knob.style.transform=`translate(${dx*k}px,${dy*k}px)`;
      if (d>14) { if (Math.abs(dx)>Math.abs(dy)) { Input.x=Math.sign(dx); Input.y=0; } else { Input.y=Math.sign(dy); Input.x=0; } } };
    const pad=$('.pad',j);
    pad.addEventListener('pointerdown',e=>{ e.preventDefault(); id=e.pointerId; try{ pad.setPointerCapture(id); }catch(_){} const r=pad.getBoundingClientRect(); cx=r.left+r.width/2; cy=r.top+r.height/2; move(e.clientX,e.clientY); });
    pad.addEventListener('pointermove',e=>{ if(e.pointerId===id) move(e.clientX,e.clientY); });
    const end=e=>{ if(e.pointerId===id){ id=null; knob.style.transform=''; } }; pad.addEventListener('pointerup',end); pad.addEventListener('pointercancel',end);
    $('#j-dash').addEventListener('pointerdown',e=>{ e.preventDefault(); Input.dash=true; });
  }
};
