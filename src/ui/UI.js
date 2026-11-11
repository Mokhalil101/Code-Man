// DOM user interface: HUD, menus, world map, tutorial, achievements, statistics, leaderboard, settings, about, pause, results, toasts.
const GDG_DOTS = () => h('span',{class:'gdg-dots'}, ...['#4285F4','#EA4335','#FBBC04','#34A853'].map(c=>h('i',{style:'background:'+c})));
const GDG_TAG = () => h('div',{class:'gdg-tag'}, GDG_DOTS(), h('span',{}, 'Powered by '), h('b',{}, 'GDG Assiut'));
const fmtTime = s => Math.floor(s/60)+':'+String(Math.floor(s%60)).padStart(2,'0');
const HUD = {
  refit(){ setTimeout(()=>{ try{ App.game.scale.refresh(); }catch(e){} },30); },
  show(){ $('#hud').hidden=false; document.body.classList.add('playing'); this.refit(); }, hide(){ $('#hud').hidden=true; document.body.classList.remove('playing'); $('#joy').hidden=true; this.refit(); },
  _pk:'',
  set(s){
    $('#h-score').textContent=s.score; $('#h-lives').textContent='♥'.repeat(Math.max(0,s.lives)); $('#h-xp').textContent=s.xp; $('#h-world').textContent=s.world;
    $('#h-bits').textContent=s.bits; $('#h-time').textContent=fmtTime(s.time);
    const pk=JSON.stringify(s.powers.map(p=>[p.icon,p.left])); if (pk!==this._pk) { this._pk=pk; const box=$('#h-powers'); box.textContent='';
      s.powers.forEach(p=>box.append(h('span',{class:'pw '+(p.cd?'cd':'')},h('img',{src:'assets/sprites/'+p.icon+'.png',alt:''}),h('em',{},p.name+' '+p.left)))); }
    const b=$('#h-boss'); b.hidden=!s.boss; if (s.boss) { $('.boss-name',b).textContent=s.boss.name; $('.bar i',b).style.width=(s.boss.hp/s.boss.max*100)+'%'; $('.boss-phase',b).textContent=s.boss.phase+'  ·  HP '+s.boss.hp+'/'+s.boss.max; }
  }
};
const UI = {
  cur:null, retPause:false,
  init(){
    $('#h-pause').addEventListener('click',()=>App.pause()); this.joystick();
    const bg=$('#bgcode'); '{ } < > ; = ( ) [ ] 0 1 / * # def if for'.split(' ').forEach((t,i)=>bg.append(h('span',{style:`left:${(i*37)%100}%;animation-duration:${9+(i*7)%9}s;animation-delay:${-(i*3)%9}s;color:${['#4285F4','#EA4335','#FBBC04','#34A853'][i%4]}`},t)));
  },
  clear(){ $('#screens').textContent=''; this.cur=null; },
  screen(name, ...kids){ this.clear(); this.cur=name; const s=h('div',{class:'screen s-'+name},...kids); $('#screens').append(s); $('#screens').hidden=false; return s; },
  hideAll(){ this.clear(); $('#screens').hidden=true; $('#modal').hidden=true; $('#modal').textContent=''; },
  btn(label,fn,cls=''){ return h('button',{class:'btn '+cls,onclick:()=>{ Audio.sfx('click'); fn(); }},label); },
  back(fn=()=>App.menu()){ return this.btn('◀ Back',fn,'ghost back'); },
  toast(msg,color='#4285F4'){ const t=h('div',{class:'toast',style:'border-color:'+color},msg); $('#toasts').append(t); setTimeout(()=>t.remove(),3200); },
  banner(title,sub,color){ const b=$('#banner'); b.textContent=''; b.append(h('div',{class:'bn-t',style:'color:'+(color||'#F8FAFC')},title),h('div',{class:'bn-s'},sub||'')); b.hidden=false; b.classList.remove('go'); void b.offsetWidth; b.classList.add('go'); clearTimeout(this._bt); this._bt=setTimeout(()=>b.hidden=true,2600); },
  modal(...kids){ const m=$('#modal'); m.textContent=''; m.append(h('div',{class:'dialog'},...kids)); m.hidden=false; },
  closeModal(){ $('#modal').hidden=true; $('#modal').textContent=''; },
  confirm(msg,yes,no=()=>{}){ this.modal(h('p',{},msg),h('div',{class:'row'},this.btn('Yes',()=>{this.closeModal();yes();},'primary'),this.btn('Cancel',()=>{this.closeModal();no();},'ghost'))); },
  progressPct(){ return Math.round(Progress.worlds()/7*100); },
  // ---------- main menu ----------
  menu(){
    const r=Progress.rank(), next=Progress.nextRank(), hasProg=SAVE.xp>0||SAVE.unlocked>1||Progress.worlds()>0;
    const col=['#4285F4','#EA4335','#FBBC04','#34A853','#4285F4','#EA4335','#FBBC04','#34A853'];
    const logo=h('h1',{class:'logo'}, ...'CODE MAN'.split('').map((c,i)=>h('span',{style:'color:'+(c===' '?'transparent':col[i])},c===' '?'\u00a0':c)));
    const items=[['▶  Play',()=>App.play(),'primary'],['⏩  Continue',()=>App.continue(),'',!hasProg],['🗺️  World Map',()=>this.worldMap()],['❓  How to Play',()=>this.tutorial(false)],
      ['🏆  Achievements',()=>this.achievements()],['📊  Statistics',()=>this.stats()],['🥇  Leaderboard',()=>this.leaderboard()],['⚙️  Settings',()=>this.settings()],['💙  About GDG Assiut',()=>this.about()]];
    this.screen('menu', h('div',{class:'menu-left'}, logo, h('div',{class:'tagline'},'Eat Code. Escape Bugs. Master Programming.'), GDG_TAG(),
      h('div',{class:'menu-btns'}, items.map(([l,f,c,dis])=>{ const b=this.btn(l,f,c||''); if(dis){ b.disabled=true; b.title='Play first to create progress'; } return b; }))),
      h('div',{class:'menu-right'}, h('div',{class:'stage'}, h('img',{class:'hero',src:'assets/sprites/pac0.png',alt:'player'}), ...[0,1,2,3].map(i=>h('img',{class:'foe f'+i,src:'assets/sprites/bug'+i+'.png',alt:''})),
          ...['bit','bit','bit','chip','orb'].map((k,i)=>h('img',{class:'fb fb'+i,src:'assets/sprites/'+k+'.png',alt:''}))),
        h('div',{class:'card glass'}, h('div',{class:'kv'},h('span',{},'Rank'),h('b',{},r.n)), h('div',{class:'kv'},h('span',{},'Highest score'),h('b',{},SAVE.best)),
          h('div',{class:'kv'},h('span',{},'Worlds'),h('b',{},'Level '+Math.min(7,SAVE.unlocked)+'/7 unlocked')),
          h('div',{class:'meter'},h('i',{style:'width:'+this.progressPct()+'%'})), h('small',{},'Progress '+this.progressPct()+'%'+(next?'  ·  '+SAVE.xp+' / '+next.xp+' XP to '+next.n:'  ·  max rank')))));
  },
  // ---------- world map ----------
  worldMap(sel){
    sel = sel || Math.min(7, SAVE.unlocked); const pos=[[9,66],[24,30],[40,62],[55,26],[70,60],[84,28],[93,64]];
    const svgNS='http://www.w3.org/2000/svg', svg=document.createElementNS(svgNS,'svg'); svg.setAttribute('viewBox','0 0 100 90'); svg.setAttribute('class','map-svg');
    const line=document.createElementNS(svgNS,'polyline'); line.setAttribute('points',pos.map(p=>p.join(',')).join(' ')); svg.append(line);
    const map=h('div',{class:'map'},svg);
    DATA.worlds.forEach((w,i)=>{ const id=i+1, locked=id>SAVE.unlocked, done=!!SAVE.completed[id];
      map.append(h('button',{class:'node'+(locked?' locked':'')+(done?' done':'')+(id===sel?' sel':''),style:`left:${pos[i][0]}%;top:${pos[i][1]}%;--ac:${w.theme.accent}`,onclick:()=>{ Audio.sfx('click'); this.worldMap(id); }},
        h('b',{},locked?'🔒':id), h('small',{},w.name), h('span',{class:'stars'},'★'.repeat(SAVE.stars[id]||0)+'☆'.repeat(3-(SAVE.stars[id]||0))))); });
    const w=DATA.worlds[sel-1], locked=sel>SAVE.unlocked;
    const info=h('div',{class:'card glass world-info',style:'--ac:'+w.theme.accent},
      h('h2',{},'World '+sel+' — '+w.name), h('p',{},w.subtitle),
      h('div',{class:'kv'},h('span',{},'Difficulty'),h('b',{},w.difficulty)), h('div',{class:'kv'},h('span',{},'Challenges'),h('b',{},(w.mazeLayout.join('').split('Q').length-1)+' quiz nodes · '+w.boss.hp+' boss hits')),
      h('div',{class:'kv'},h('span',{},'Boss'),h('b',{},w.boss.name+(SAVE.completed[sel]?'  ✔ defeated':''))), h('div',{class:'kv'},h('span',{},'Rating'),h('b',{},'★'.repeat(SAVE.stars[sel]||0)+'☆'.repeat(3-(SAVE.stars[sel]||0)))),
      h('div',{class:'kv'},h('span',{},'Status'),h('b',{},locked?'Locked — complete World '+(sel-1):SAVE.completed[sel]?'Completed':'Available')),
      h('p',{class:'mech'},'⚙ '+w.mechanic), locked?h('div',{class:'lockmsg'},'🔒 Finish the previous world to unlock'):this.btn(SAVE.completed[sel]?'Replay World '+sel:'Start World '+sel,()=>App.startWorld(sel),'primary'));
    this.screen('worldmap', h('h2',{class:'title'},'World Map'), map, info, this.back());
  },
  // ---------- tutorial ----------
  tutorial(startAfter){
    const S=(k)=>h('img',{src:'assets/sprites/'+k+'.png',alt:''});
    const steps=[
      ['Move','Use the Arrow Keys or WASD (or the on-screen joystick / swipe). Your direction is buffered, so you can press early and turn at the next corner.',[S('pac0'),h('span',{class:'keys'},'↑ ← ↓ →  /  W A S D')]],
      ['Collect Code Bits','Yellow Code Bits give +10 points. Bonus Chips give +250, green XP Orbs give XP and hidden stars are secrets.',[S('bit'),S('bit'),S('chip'),S('orb'),S('secret')]],
      ['Avoid the Bugs','Syntax chases you, Logic predicts you, Runtime blocks your escape and Memory remembers where you were. You have 3 lives.',[S('bug0'),S('bug1'),S('bug2'),S('bug3')]],
      ['Power-ups','U Power Compiler freezes bugs (touch them to squash). S Speed. D Shield. M XP x2. K Scanner reveals secrets. L Teleport Chip. Space = Dash.',['U','S','D','M','K','L'].map(k=>S('pu_'+k))],
      ['Quiz Nodes','Touch a purple ? node to pause the game and answer a programming question. Correct = points + XP. Wrong or timeout = penalty.',[S('quiz')]],
      ['Answering','Pick an answer (or press 1-4), then Submit. Some questions ask you to arrange code lines in order. Read the explanation afterwards!',[h('span',{class:'keys'},'1 2 3 4  ·  Enter')]],
      ['The Exit Gate','Collect every Code Bit, finish all quiz nodes and defeat the world boss. Then the gate turns green — step in!',[S('exit0'),h('span',{class:'arrow'},'→'),S('exit1')]],
      ['Bosses','Touch the boss to face a challenge. Every correct answer damages it; a wrong answer costs a life. Bosses dash, teleport, summon and shield — watch for warnings.',[S('boss1'),S('boss4'),S('boss7')]],
      ['Score & XP','Points: bit 10 · answer 100 (+50 fast) · chip 250 · bug 200 · world 500 (+300 flawless). XP raises your rank from Beginner Coder to Code Legend.',[h('span',{class:'keys'},'🎖️ Beginner → Legend')]]];
    let i=0; const finish=()=>{ SAVE.settings.tutorial=true; Save.save(); startAfter?App.startWorld(1,true):App.menu(); };
    const draw=()=>{ const [t,d,vis]=steps[i];
      this.screen('tutorial', h('div',{class:'card glass tut'}, h('small',{},'Step '+(i+1)+' / '+steps.length), h('h2',{},t), h('div',{class:'vis'},vis), h('p',{},d),
        h('div',{class:'row'}, i>0?this.btn('◀ Back',()=>{i--;draw();},'ghost'):'', this.btn('Skip',finish,'ghost'), i<steps.length-1?this.btn('Next ▶',()=>{i++;draw();},'primary'):this.btn(startAfter?'Start World 1':'Done',finish,'primary')))); };
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
        h('tbody',{},top.map((e,i)=>h('tr',{},h('td',{},i+1),h('td',{},e.score),h('td',{},e.world),h('td',{},e.xp),h('td',{},e.acc+'%'),h('td',{},e.result),h('td',{},e.date?new Date(e.date).toLocaleDateString():'-')))))
        :h('p',{class:'empty'},'No runs yet — finish or lose a game to record your first score.')),
      h('small',{},'These are your personal records stored on this device. A global leaderboard is not part of the static version.'), this.back());
  },
  // ---------- settings ----------
  settings(fromPause){
    const S=SAVE.settings, slider=(label,key)=>h('label',{class:'slider'},h('span',{},label),h('input',{type:'range',min:0,max:100,value:Math.round(S[key]*100),oninput:e=>{ S[key]=e.target.value/100; Audio.refresh(); Save.save(); },onchange:()=>Audio.sfx('click')}));
    const mute=h('input',{type:'checkbox',onchange:e=>{ S.mute=e.target.checked; Audio.refresh(); Save.save(); }}); mute.checked=S.mute;
    const diff=h('select',{onchange:e=>{ S.diff=+e.target.value; Save.save(); }},['Easy','Normal','Hard'].map((n,i)=>h('option',{value:i},n))); diff.value=S.diff;
    const kids=[h('h2',{class:'title'},'Settings'), h('div',{class:'card glass settings'}, slider('Master volume','master'),slider('Music volume','music'),slider('Sound effects','sfx'),
      h('label',{class:'slider'},h('span',{},'Mute all'),mute), h('label',{class:'slider'},h('span',{},'Enemy speed (applies to next world run)'),diff),
      h('div',{class:'row'}, this.btn('Replay tutorial',()=>this.tutorial(false),'ghost'), this.btn('Reset progress',()=>this.confirm('Reset ALL progress, XP, achievements and settings? This cannot be undone.',()=>{ Save.reset(); Audio.refresh(); App.menu(); this.toast('Progress reset','#EA4335'); }),'danger')))];
    if (fromPause) { this.modal(...kids.slice(0), this.btn('◀ Back to pause',()=>this.pauseMenu(),'ghost')); $('#modal').classList.add('wide'); } else this.screen('settings',...kids,this.back());
  },
  about(){
    this.screen('about', h('div',{class:'card glass about'}, h('h1',{class:'logo small'},'CODE MAN'), GDG_TAG(),
      h('p',{},'An interactive programming arcade experience designed to make learning, problem-solving, and software development more engaging through gameplay.'),
      h('h3',{},'Game objectives'), h('p',{},'Explore seven programming worlds, collect Code Bits, escape the bugs, answer questions in Python, C++, Java and JavaScript, defeat each world boss and finally shut down the Core Virus.'),
      h('h3',{},'About GDG Assiut'), h('p',{},'Google Developer Groups (GDG) are developer communities. This game is a community-inspired project made for GDG Assiut. It is not an official Google product.'),
      h('h3',{},'Credits'), h('p',{},'Game design, code, pixel art and chiptune audio are original to this project. Built with Phaser 3. Font: Press Start 2P (SIL OFL).'),
      h('p',{class:'ph'},'[ Developer / community team information — add your team here ]'), CONFIG.gdgLogo?h('img',{class:'gdg-logo',src:'assets/icons/gdg-assiut-logo.png',alt:'GDG Assiut'}):''), this.back());
  },
  // ---------- in-game overlays ----------
  pauseMenu(){
    this.modal(h('h2',{},'Paused'), h('div',{class:'col'}, this.btn('▶ Resume',()=>App.resume(),'primary'), this.btn('↻ Restart level',()=>this.confirm('Restart this world? Current run progress is lost.',()=>App.startWorld(App.world),()=>this.pauseMenu()),''),
      this.btn('⚙ Settings',()=>this.settings(true),''), this.btn('⌂ Main menu',()=>this.confirm('Leave the current run? Unfinished progress is lost.',()=>App.menu(),()=>this.pauseMenu()),'ghost')));
  },
  statsBlock(r){ return h('div',{class:'grid res-grid'}, [['Score',r.score],['XP earned',r.xp],['Questions',r.q],['Accuracy',r.acc+'%'],['Enemies',r.enemies],['Time',fmtTime(r.time)]].map(([k,v])=>h('div',{class:'card glass stat'},h('small',{},k),h('b',{},v)))); },
  levelComplete(r){
    const w=DATA.worlds[r.world-1];
    this.screen('result', h('div',{class:'card glass result win'}, GDG_TAG(), h('h1',{},'WORLD '+r.world+' COMPLETE!'), h('div',{class:'bigstars'},'★'.repeat(r.stars)+'☆'.repeat(3-r.stars)), h('p',{},w.name+' — '+w.boss.name+' defeated'),
      this.statsBlock(r), r.bonuses.map(b=>h('div',{class:'kv'},h('span',{},b[0]),h('b',{},'+'+b[1]))), r.ach.map(a=>h('div',{class:'badge'},a.icon+' '+a.name)),
      r.world<7?h('p',{},'World '+(r.world+1)+' — '+DATA.worlds[r.world].name+' unlocked!'):'',
      h('div',{class:'row'}, r.world<7?this.btn('Next World ▶',()=>App.startWorld(r.world+1),'primary'):'', this.btn('World Map',()=>this.worldMap(Math.min(7,r.world+1))), this.btn('Menu',()=>App.menu(),'ghost'))));
  },
  gameOver(r){
    this.screen('result', h('div',{class:'card glass result lose'}, GDG_TAG(), h('h1',{},'GAME OVER'), h('p',{},'Final score '+r.score+' · '+DATA.worlds[r.world-1].name), this.statsBlock(r),
      h('p',{},'Levels completed: '+SAVE.stats.levels+' · Rank: '+Progress.rank().n), r.ach.map(a=>h('div',{class:'badge'},a.icon+' '+a.name)),
      h('div',{class:'row'}, this.btn('↻ Retry',()=>App.startWorld(r.world),'primary'), this.btn('Main menu',()=>App.menu(),'ghost'))));
  },
  ending(r){
    const lines=['The Core Virus collapses into a thousand harmless bits of light…','Every world is compiled. Every bug is squashed.','Somewhere, a community of developers cheers.','You are no longer a beginner.','You are a CODE MAN.'];
    let done=false; const el=h('div',{class:'ending'}); const scr=this.screen('ending', el);
    const credits=()=>{ if(done)return; done=true; el.textContent=''; el.append(h('h1',{class:'logo'},'CODE MAN'), GDG_TAG(), h('p',{},'Eat Code. Escape Bugs. Master Programming.'), this.statsBlock(r),
      h('div',{class:'badge'},'Final rank: '+Progress.rank().n), r.ach.map(a=>h('div',{class:'badge'},a.icon+' '+a.name)), h('div',{class:'row'},this.btn('World Map',()=>this.worldMap(7)),this.btn('Main menu',()=>App.menu(),'primary'))); };
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
