// The playable maze: player, 4 bug AIs (BFS pathfinding), hazards, bosses, power-ups, quizzes, scoring and progression.
class GameScene extends Phaser.Scene {
  constructor(){ super('Game'); }
  init(d){ this.wid=d.world; }
  create(){
    const W=this.W=DATA.worlds[this.wid-1]; this.map=W.mazeLayout; this.qm=new QuestionManager(DATA.questions);
    this.cameras.main.setBackgroundColor(W.theme.bg); this.cameras.main.fadeIn(300);
    Object.assign(this,{state:'playing',t:0,score:0,lives:3,runXP:0,lostLife:false,unlocked:false,left:0,total:0,freeze:0,spd:0,xpm:0,scan:0,inv:2.5,shield:false,dash:0,dashCd:0,tpCd:0,
      modeT:0,forceChase:0,qOK:0,qBad:0,answered:0,hudT:0,trailT:0,hint:0,scatter:true,bossMusic:false,enemiesKilled:0,fields:new Map(),trail:[],lastKey:'',secretsRun:0});
    this.gspeed=W.ghostSpeed*([0.85,1,1.15][SAVE.settings.diff]||1); this.pG=(x,y)=>this.freeG(x,y);
    const acc=parseInt(W.theme.accent.slice(1),16); this.acc=acc;
    this.items=new Map(); this.nodes=new Map(); this.ghosts=[]; this.hazards=[]; this.corrupt=[]; this.boss=null; this.junctions=[];
    const keys=['bug0','bug1','bug2','bug3'], names=['Syntax','Logic','Runtime','Memory'], corners=[[17,1],[1,1],[17,13],[1,13]]; let gi=0, P={x:9,y:13}, E={x:9,y:1}, B=null;
    this.drift=[...Array(14)].map(()=>this.add.text(Math.random()*COLS*T,Math.random()*ROWS*T,'{}<>;01/=()[]'[Math.floor(Math.random()*13)],{fontFamily:'"Press Start 2P"',fontSize:'14px',color:W.theme.accent}).setAlpha(.12).setDepth(-1));
    const walls=[];
    this.map.forEach((row,y)=>[...row].forEach((c,x)=>{
      const px=x*T+T/2, py=y*T+T/2, key=x+','+y;
      if (c==='#') { walls.push([x*T,y*T]); return; }
      if (c==='.') { this.items.set(key,{t:c,o:[this.add.image(px,py,'bit')]}); this.total++; this.left++; }
      else if (c==='B') this.items.set(key,{t:c,o:[this.add.image(px,py,'chip')]});
      else if (c==='o') this.items.set(key,{t:c,o:[this.add.image(px,py,'orb')]});
      else if (c==='T') this.items.set(key,{t:c,o:[this.add.image(px,py,'secret').setAlpha(.1)]});
      else if ('USDMKL'.includes(c)) { const im=this.add.image(px,py,'pu_'+c); this.tweens.add({targets:im,scale:{from:1,to:1.18},yoyo:true,repeat:-1,duration:520}); this.items.set(key,{t:c,o:[im]}); }
      else if (c==='Q') { const im=this.add.image(px,py,'quiz'); this.tweens.add({targets:im,angle:{from:-6,to:6},yoyo:true,repeat:-1,duration:600}); this.nodes.set(key,[im]); }
      else if (c==='C') this.corrupt.push({x,y,img:this.add.image(px,py,'corrupt').setAlpha(.25).setDepth(1)});
      else if (c==='O') { const m=new Mover(x,y,2.3); m.dir={x:1,y:0}; this.hazards.push({m,s:this.add.image(0,0,'hazard').setDepth(3)}); }
      else if (c==='P') P={x,y}; else if (c==='E') E={x,y}; else if (c==='X') B={x,y};
      else if (c==='G'&&gi<4) { const m=new Mover(x,y,this.gspeed); this.ghosts.push({m,s:this.add.image(0,0,keys[gi]).setDepth(3),key:keys[gi],type:names[gi],corner:corners[gi],delay:gi*2,ret:false,stun:0,state:'waiting',home:null}); gi++; }
    }));
    const rt=this.add.renderTexture(0,0,COLS*T,ROWS*T).setOrigin(0,0).setDepth(0); rt.beginDraw(); walls.forEach(([wx,wy])=>rt.batchDraw(W.theme.wall,wx,wy)); rt.endDraw();   // bake all wall tiles into ONE texture (performance)
    this.map.forEach((row,y)=>[...row].forEach((c,x)=>{ if (this.freeG(x,y)&&DIRS.filter(v=>this.freeG(x+v.x,y+v.y)).length>=3) this.junctions.push([x,y]); }));
    this.ghosts.forEach(g=>g.home=Path.field(this.map,g.m.sx,g.m.sy,this.pG));
    this.nodeTotal=this.nodes.size; this.exitPos=E;
    this.exit=this.add.image(E.x*T+T/2,E.y*T+T/2,'exit0').setDepth(2); this.exitLbl=this.add.text(E.x*T+T/2,E.y*T+T/2-20,'EXIT',{fontFamily:'"Press Start 2P"',fontSize:'8px',color:'#34A853'}).setOrigin(.5).setVisible(false).setDepth(5);
    if (B) { const m=new Mover(B.x,B.y,this.gspeed*.85); this.boss={m,s:this.add.image(0,0,W.theme.boss).setDepth(4),hp:W.boss.hp,max:W.boss.hp,delay:3.5,shield:false,sc:7,mult:1,dashT:0,warn:false,cd:{dash:6,tele:8,sum:10},shTold:false,down:false};
      this.arena=this.add.circle(B.x*T+T/2,B.y*T+T/2,76,acc,.06).setStrokeStyle(2,acc,.4); this.tweens.add({targets:this.arena,alpha:{from:.5,to:1},yoyo:true,repeat:-1,duration:900}); }
    this.p=new Mover(P.x,P.y,4.2); this.ps=this.add.image(0,0,'pac0').setDepth(6); this.shieldG=this.add.circle(0,0,19,0x66ccff,.25).setStrokeStyle(2,0x66ccff).setDepth(7).setVisible(false);
    this.cur=this.input.keyboard.createCursorKeys(); this.wasd=this.input.keyboard.addKeys('W,A,S,D'); this.kSpace=this.input.keyboard.addKey('SPACE'); this.kEsc=this.input.keyboard.addKey('ESC'); this.kP=this.input.keyboard.addKey('P');
    this._swipe=p=>{ const dx=p.upX-p.downX, dy=p.upY-p.downY; if (Math.max(Math.abs(dx),Math.abs(dy))>20) { if (Math.abs(dx)>Math.abs(dy)) { Input.x=Math.sign(dx); Input.y=0; } else { Input.y=Math.sign(dy); Input.x=0; } } };
    this.input.on('pointerup',this._swipe); this.events.once('shutdown',()=>{ this.input.off('pointerup',this._swipe); this.tweens.killAll(); });
    Input.x=0; Input.y=0; Input.dash=false; Audio.music('w'+this.wid); this.placeAll();
    UI.banner('WORLD '+this.wid+' — '+W.name.toUpperCase(),W.mechanic,W.theme.accent); setTimeout(()=>{ if(this.state==='playing'&&this.t<8) UI.banner('BOSS: '+W.boss.name.toUpperCase(),W.boss.description,'#EA4335'); },2900);
    $('#joy').hidden=false; this.updateExit(); this.pushHud();
  }
  // ----- helpers -----
  free(x,y){ const c=this.map[y]&&this.map[y][x]; if(!c||c==='#') return false; if(c==='E'&&!this.unlocked) return false; return true; }
  freeG(x,y){ const c=this.map[y]&&this.map[y][x]; return !!c&&c!=='#'&&c!=='E'; }
  place(o,m){ o.setPosition(m.fx*T+T/2,m.fy*T+T/2); }
  placeAll(){ this.place(this.ps,this.p); this.ghosts.forEach(g=>this.place(g.s,g.m)); this.hazards.forEach(h=>this.place(h.s,h.m)); if(this.boss&&!this.boss.down) this.place(this.boss.s,this.boss.m); }
  field(tx,ty){ const k=tx+','+ty; let f=this.fields.get(k); if(!f){ if(this.fields.size>80) this.fields.clear(); f=Path.field(this.map,tx,ty,this.pG); this.fields.set(k,f); } return f; }
  pop(s,x,y,color='#FBBC04'){ const t=this.add.text(x,y,s,{fontFamily:'"Press Start 2P"',fontSize:'9px',color,stroke:'#000',strokeThickness:3}).setOrigin(.5).setDepth(20); this.tweens.add({targets:t,y:y-28,alpha:0,duration:1300,onComplete:()=>t.destroy()}); }
  burst(x,y,col,n=7){ for(let i=0;i<n;i++){ const c=this.add.circle(x,y,2+Math.random()*2,col).setDepth(9),a=Math.random()*6.28,r=12+Math.random()*18; this.tweens.add({targets:c,x:x+Math.cos(a)*r,y:y+Math.sin(a)*r,alpha:0,duration:380,onComplete:()=>c.destroy()}); } }
  pulse(x,y){ [0x4285F4,0xEA4335,0xFBBC04,0x34A853].forEach((c,i)=>{ const r=this.add.circle(x,y,10).setStrokeStyle(3,c).setDepth(9); this.tweens.add({targets:r,scale:{from:1,to:14},alpha:{from:.9,to:0},duration:700,delay:i*90,onComplete:()=>r.destroy()}); }); }
  mult(){ return this.xpm>0?2:1; }
  gain(pts,xp=0){ const m=this.mult(); this.score+=pts*m; if(xp) this.runXP+=Progress.addXP(xp*m); }
  tile(){ return [Math.round(this.p.fx),Math.round(this.p.fy)]; }
  ahead(n){ const p=this.p,d=(p.dir.x||p.dir.y)?p.dir:{x:0,y:0}; let x=p.gx,y=p.gy; for(let i=0;i<n;i++){ if(!this.freeG(x+d.x,y+d.y)) break; x+=d.x; y+=d.y; } return [x,y]; }
  junctionNear([ax,ay]){ let best=[ax,ay],bd=1e9; for(const j of this.junctions){ if(j[0]===this.p.gx&&j[1]===this.p.gy) continue; const d=Math.abs(j[0]-ax)+Math.abs(j[1]-ay); if(d<bd){bd=d;best=j;} } return best; }
  // ----- enemy AI -----
  target(g){
    const p=this.p,m=g.m,pt=[p.gx,p.gy]; if (this.scatter) return {mode:'scatter',t:g.corner};
    switch(g.type){
      case 'Syntax': return {mode:'chase',t:pt};
      case 'Logic': return {mode:'chase',t:this.ahead(4)};                                      // predicts movement
      case 'Runtime': return Math.hypot(m.gx-p.gx,m.gy-p.gy)<4?{mode:'chase',t:pt}:{mode:'chase',t:this.junctionNear(this.ahead(6))}; // blocks escape routes
      default: return Math.hypot(m.gx-p.gx,m.gy-p.gy)>8?{mode:'patrol',t:this.trail[0]||g.corner}:{mode:'chase',t:pt};          // Memory: patrol remembered positions, chase when close
    }
  }
  enemyTick(g,dt){
    const m=g.m;
    if (g.ret) { g.state='return'; m.speed=7; m.update(dt,()=>Path.step(g.home,m,this.pG),this.pG); if(!m.moving&&m.gx===m.sx&&m.gy===m.sy){ g.ret=false; g.delay=1; m.speed=this.gspeed; } }
    else if (g.stun>0) { g.stun-=dt; g.state='stunned'; }
    else if (g.delay>0) { g.delay-=dt; g.state='waiting'; }
    else if (this.freeze>0) g.state='frightened';
    else { const tg=this.target(g); g.state=tg.mode; const [tx,ty]=Path.nearest(tg.t[0],tg.t[1],this.pG); m.speed=this.gspeed; m.update(dt,()=>Path.step(this.field(tx,ty),m,this.pG),this.pG); }
    g.s.setTexture(g.ret?'eyes':(g.state==='frightened'||g.state==='stunned')?'scared':g.key).setAlpha(g.state==='stunned'?.5+.5*Math.sin(this.t*30):1); this.place(g.s,m);
  }
  bossTick(dt){
    const b=this.boss; if(!b||b.down) return; const m=b.m;
    for (const pt of this.W.boss.patterns) {
      if (pt==='shield') { b.sc-=dt; if(b.sc<=0){ b.shield=!b.shield; b.sc=b.shield?3:7; b.shTold=false; b.s.setTint(b.shield?0x66ccff:0xffffff); if(b.shield) UI.toast('Boss shield up — wait for it to drop!','#66ccff'); } }
      if (pt==='dash') { if(b.dashT>0){ b.dashT-=dt; if(b.dashT<=0){ b.mult=1; b.s.clearTint(); } } else { b.cd.dash-=dt; if(b.cd.dash<=.8&&!b.warn){ b.warn=true; b.s.setTint(0xff4444); UI.toast('⚠ Boss is about to DASH!','#EA4335'); } if(b.cd.dash<=0){ b.dashT=1.6; b.mult=1.8; b.cd.dash=9; b.warn=false; } } }
      if (pt==='teleport') { b.cd.tele-=dt; if(b.cd.tele<=1.2) b.s.setAlpha(.3+.5*Math.abs(Math.sin(this.t*14))); if(b.cd.tele<=0){ this.bossTeleport(); b.cd.tele=10; b.s.setAlpha(1); } }
      if (pt==='summon') { b.cd.sum-=dt; if(b.cd.sum<=0){ b.cd.sum=12; this.forceChase=6; this.ghosts.forEach(g=>{ if(g.delay>0)g.delay=0; }); UI.toast('⚠ Boss SUMMONS — bugs rush you!','#EA4335'); this.cameras.main.flash(200,234,67,53); } }
    }
    if (b.delay>0) { b.delay-=dt; b.s.setAlpha(.4); } else if (this.freeze<=0) { if(b.s.alpha<1&&!this.W.boss.patterns.includes('teleport')) b.s.setAlpha(1); m.speed=this.gspeed*.85*b.mult; const [tx,ty]=[this.p.gx,this.p.gy]; m.update(dt,()=>Path.step(this.field(tx,ty),m,this.pG),this.pG); }
    this.place(b.s,m);
  }
  bossTeleport(){ const b=this.boss, f=this.field(this.p.gx,this.p.gy); let best=null,bd=-1; const open=this.junctions.length?this.junctions:[[b.m.sx,b.m.sy]];
    for(const [x,y] of open){ const d=f[y][x]; if(d>=8&&d<1e9&&Math.random()<.5){ best=[x,y]; break; } if(d<1e9&&d>bd){bd=d;best=[x,y];} }
    if(best){ this.burst(b.s.x,b.s.y,0xA142F4,10); b.m.warp(best[0],best[1]); b.m.dir={x:0,y:0}; this.place(b.s,b.m); this.burst(b.s.x,b.s.y,0xA142F4,10); } }
  // ----- damage -----
  damage(src,g){
    if (this.inv>0||this.state!=='playing') return;
    if (this.shield) { this.shield=false; this.inv=1.5; Audio.sfx('expire'); this.pop('SHIELD BROKEN',this.ps.x,this.ps.y,'#66ccff'); if(g){ g.stun=2.5; } this.burst(this.ps.x,this.ps.y,0x66ccff,10); return; }
    this.loseLife(src);
  }
  loseLife(){
    this.lives--; this.lostLife=true; SAVE.stats.deaths++; SAVE.stats.streak=0; Audio.sfx('hit'); this.cameras.main.shake(260,.012); this.cameras.main.flash(180,234,67,53);
    if (this.lives<=0) { this.gameOver(); return true; }
    this.p.reset(); this.ghosts.forEach((x,i)=>{ x.m.reset(); x.ret=false; x.stun=0; x.delay=i*1.5; }); if(this.boss&&!this.boss.down){ this.boss.m.reset(); this.boss.delay=3.5; }
    this.hazards.forEach(h=>{ h.m.reset(); h.m.dir={x:1,y:0}; }); Input.x=0; Input.y=0; this.inv=2.5; this.placeAll(); return false;
  }
  hitGhost(g){
    if (g.ret||g.delay>0||g.stun>0||Math.hypot(g.m.fx-this.p.fx,g.m.fy-this.p.fy)>.6) return;
    if (this.freeze>0) { this.gain(200,15); SAVE.stats.enemies++; this.enemiesKilled++; g.ret=true; this.pop('+200 BUG FIXED',this.ps.x,this.ps.y,'#EA4335'); this.burst(g.s.x,g.s.y,0xEA4335,10); Audio.sfx('squash'); Progress.check(); return; }
    this.damage('bug',g);
  }
  // ----- main loop -----
  update(_,ms){
    for (const d of this.drift) { d.y+=ms*.012; if(d.y>ROWS*T+10) { d.y=-10; d.x=Math.random()*COLS*T; } }
    if (this.state!=='playing') return;
    const dt=Math.min(ms/1000,.05); this.t+=dt; this.readInput();
    for (const [k,lbl] of [['freeze','U'],['spd','S'],['xpm','M'],['scan','K']]) { const was=this[k]; this[k]=Math.max(0,this[k]-dt); if(was>0&&this[k]<=0){ UI.toast(POWER[lbl].name+' expired','#94A3B8'); Audio.sfx('expire',.7); } }
    this.inv=Math.max(0,this.inv-dt); this.dash=Math.max(0,this.dash-dt); this.dashCd=Math.max(0,this.dashCd-dt); this.tpCd=Math.max(0,this.tpCd-dt); this.forceChase=Math.max(0,this.forceChase-dt);
    this.modeT+=dt; const cy=this.W.cycle; this.scatter=(this.modeT%(cy.scatter+cy.chase))<cy.scatter&&this.forceChase<=0;
    const p=this.p; p.speed=Math.min(7,4.2*(this.spd>0?1.4:1)*(this.dash>0?1.35:1));
    p.update(dt,m=>this.playerDecide(m),(x,y)=>this.free(x,y)); this.place(this.ps,p);
    const moving=p.moving; this.ps.setTexture(moving&&Math.floor(this.t*9)%2?'pac1':'pac0').setFlipX(p.dir.x<0).setAngle(p.dir.y<0?-90:p.dir.y>0?90:0).setAlpha(this.inv>0?.5+.4*Math.sin(this.t*25):1);
    this.shieldG.setVisible(this.shield).setPosition(this.ps.x,this.ps.y).setScale(1+.05*Math.sin(this.t*8));
    if (this.spd>0&&moving&&(this.trailT-=dt)<=0) { this.trailT=.06; const a=this.add.image(this.ps.x,this.ps.y,this.ps.texture.key).setTint(0x4285F4).setAlpha(.5).setFlipX(this.ps.flipX).setAngle(this.ps.angle).setDepth(5); this.tweens.add({targets:a,alpha:0,duration:260,onComplete:()=>a.destroy()}); }
    const [tx,ty]=this.tile(); const tk=tx+','+ty; if(tk!==this.lastKey){ this.lastKey=tk; this.trail.push([tx,ty]); if(this.trail.length>14) this.trail.shift(); }
    this.pickups(); if(this.state!=='playing') return;
    for (const g of this.ghosts) { this.enemyTick(g,dt); this.hitGhost(g); if(this.state!=='playing') return; }
    for (const h of this.hazards) { if(this.freeze<=0) h.m.update(dt,m=>{ if(this.freeG(m.gx+m.dir.x,m.gy+m.dir.y)) return m.dir; return {x:-m.dir.x,y:-m.dir.y}; },this.pG); this.place(h.s,h.m); h.s.setAngle(this.t*120%360);
      if (Math.hypot(h.m.fx-p.fx,h.m.fy-p.fy)<.6&&this.freeze<=0) { this.damage('hazard'); if(this.state!=='playing') return; } }
    const ph=this.t%6; for (const c of this.corrupt) { const act=ph>=4, warn=ph>=3&&ph<4; c.img.setAlpha(act?.95:warn?(Math.floor(this.t*10)%2?.7:.25):.22); if(act&&c.x===tx&&c.y===ty) { this.damage('corrupt'); if(this.state!=='playing') return; } }
    this.bossTick(dt); if(this.state!=='playing') return; this.bossTouch(); if(this.state!=='playing') return;
    this.checkNode(); if(this.state!=='playing') return;
    this.checkExit(); this.hints(); if ((this.hudT-=dt)<=0) { this.hudT=.1; this.pushHud(); }
  }
  readInput(){
    const c=this.cur,w=this.wasd;
    if (c.left.isDown||w.A.isDown) { Input.x=-1; Input.y=0; } else if (c.right.isDown||w.D.isDown) { Input.x=1; Input.y=0; } else if (c.up.isDown||w.W.isDown) { Input.x=0; Input.y=-1; } else if (c.down.isDown||w.S.isDown) { Input.x=0; Input.y=1; }
    if ((Phaser.Input.Keyboard.JustDown(this.kSpace)||Input.dash)&&this.dashCd<=0) { this.dash=1; this.dashCd=8; this.burst(this.ps.x,this.ps.y,0x4285F4,6); } Input.dash=false;
  }
  playerDecide(m){ if ((Input.x||Input.y)&&this.free(m.gx+Input.x,m.gy+Input.y)) return {x:Input.x,y:Input.y}; return (m.dir.x||m.dir.y)?m.dir:null; }
  pickups(){
    const k=this.tile().join(','), it=this.items.get(k); if(!it) return; const px=this.ps.x,py=this.ps.y,s=SAVE.stats;
    if (it.t==='L'&&this.tpCd>0) return;
    this.items.delete(k); it.o.forEach(o=>o.destroy());
    switch(it.t){
      case '.': this.gain(10,1); this.left--; s.bits++; Audio.sfx('bit',.5); this.burst(px,py,0xFBBC04,3); this.updateExit(); break;
      case 'B': this.gain(250,10); s.bits++; this.pop('+250',px,py); Audio.sfx('bonus'); this.burst(px,py,0xFBBC04,10); break;
      case 'o': this.gain(0,25); s.bits++; this.pop('+25 XP',px,py,'#34A853'); Audio.sfx('orb'); this.burst(px,py,0x34A853,8); break;
      case 'T': this.gain(500,50); s.secrets++; this.secretsRun++; this.pop('SECRET! +500',px,py,'#FBBC04'); Audio.sfx('secret'); this.burst(px,py,0xFBBC04,14); break;
      default: s.powerups++; this.power(it.t,px,py);
    }
    Progress.check();
  }
  power(c,px,py){
    Audio.sfx('power'); this.pop(POWER[c].name.toUpperCase()+'!',px,py,'#4285F4');
    if (c==='U') { this.freeze=5; this.pulse(px,py); } else if (c==='S') this.spd=7; else if (c==='D') this.shield=true; else if (c==='M') this.xpm=15;
    else if (c==='K') { this.scan=8; for(const [,i] of this.items) if(i.t==='T') this.tweens.add({targets:i.o[0],alpha:1,duration:300}); this.pulse(px,py); }
    else if (c==='L') this.teleport();
  }
  teleport(){
    const spots=[[this.p.sx,this.p.sy],[1,1],[17,1],[1,13],[17,13]].filter(([x,y])=>this.free(x,y)), foes=[...this.ghosts.map(g=>g.m),...this.hazards.map(h=>h.m),...(this.boss&&!this.boss.down?[this.boss.m]:[])];
    let best=spots[0],bd=-1; for(const s of spots){ const d=Math.min(...foes.map(m=>Math.hypot(m.fx-s[0],m.fy-s[1])),99); if(d>bd){bd=d;best=s;} }
    this.burst(this.ps.x,this.ps.y,0xA142F4,12); this.p.warp(best[0],best[1]); Input.x=0; Input.y=0; this.inv=1.5; this.tpCd=10; SAVE.stats.teleports++; Audio.sfx('teleport'); this.place(this.ps,this.p); this.burst(this.ps.x,this.ps.y,0xA142F4,12);
  }
  // ----- quiz -----
  openQuiz(q,cb){ this.state='quiz'; Input.x=0; Input.y=0; Quiz.open(q,{n:SAVE.stats.questions+1,done:Math.min(this.answered+1,this.nodeTotal+(this.boss?this.boss.max:0)),total:this.nodeTotal+(this.boss?this.boss.max:0)},r=>{ this.handleAnswer(r); cb(r); }); }
  handleAnswer(r){
    const s=SAVE.stats, q=r.q; s.questions++; this.answered++;
    if (r.ok) { s.correct++; this.qOK++; s.streak++; s.bestStreak=Math.max(s.bestStreak,s.streak); if(r.fast) s.fast++; this.gain((q.points||100)+(r.fast?50:0)+(q.difficulty===3?50:0),15+10*q.difficulty); Audio.sfx('good'); }
    else { s.wrong++; this.qBad++; s.streak=0; this.score=Math.max(0,this.score-50); Audio.sfx('bad'); }
    Progress.check();
  }
  checkNode(){
    const k=this.tile().join(','), n=this.nodes.get(k); if(!n) return;
    this.nodes.delete(k); n.forEach(o=>o.destroy());
    const mx=this.W.difficultyMix; this.openQuiz(this.qm.next({mix:mx,topics:this.wid===7?null:[this.W.topic]}),()=>{ this.state='playing'; this.inv=Math.max(this.inv,.8); this.updateExit(); });
  }
  bossTouch(){
    const b=this.boss; if(!b||b.down||b.delay>0||this.inv>0||Math.hypot(b.m.fx-this.p.fx,b.m.fy-this.p.fy)>.75) return;
    if (b.shield) { if(!b.shTold){ b.shTold=true; UI.toast('The boss is shielded — wait!','#66ccff'); } return; }
    const phases=this.W.boss.phases, ph=phases[Math.min(b.max-b.hp,phases.length-1)], mx=ph.mix;
    this.openQuiz(this.qm.next({mix:{1:mx[0],2:mx[1],3:mx[2]},topics:ph.topics,types:ph.types}),r=>{
      if (r.ok) { b.hp--; Audio.sfx('bosshit'); this.gain(300,40); this.cameras.main.shake(200,.01); this.burst(b.s.x,b.s.y,0xEA4335,14);
        if (b.hp<=0) { b.down=true; SAVE.stats.bosses++; this.gain(1000,250); this.pop(this.W.boss.name.toUpperCase()+' DEFEATED!',304,200,'#34A853'); Audio.sfx('win'); this.cameras.main.flash(500,255,255,255);
          this.tweens.add({targets:b.s,scale:0,angle:360,duration:700,onComplete:()=>b.s.destroy()}); if(this.wid===7) Progress.event('coreDown'); UI.banner('BOSS DEFEATED!',this.W.boss.name,'#34A853'); }
        else UI.toast(this.W.boss.phases.length>1?'Next: '+phases[Math.min(b.max-b.hp,phases.length-1)].name:'Boss hit! '+b.hp+' left','#EA4335'); }
      if (!b.down) { b.m.reset(); b.delay=3.5; }
      if (!r.ok && this.loseLife()) return;
      this.inv=Math.max(this.inv,2); Input.x=0; Input.y=0; this.state='playing'; this.updateExit(); Progress.check();
    });
  }
  // ----- exit / completion -----
  updateExit(){
    const was=this.unlocked; this.unlocked=(this.left===0&&this.nodes.size===0&&(!this.boss||this.boss.down)); this.exit.setTexture(this.unlocked?'exit1':'exit0'); this.exitLbl.setVisible(this.unlocked);
    if (this.unlocked&&!was) { UI.toast('🚪 EXIT GATE UNLOCKED!','#34A853'); Audio.sfx('win',.7); this.tweens.add({targets:this.exit,scale:{from:1,to:1.3},yoyo:true,repeat:-1,duration:500}); this.pulse(this.exit.x,this.exit.y); }
    if (!this.bossMusic&&this.left===0&&this.nodes.size===0&&this.boss&&!this.boss.down) { this.bossMusic=true; Audio.music('boss'); UI.banner('BOSS BATTLE!',this.W.boss.name,'#EA4335'); }
  }
  checkExit(){ const [x,y]=this.tile(); if(this.unlocked&&x===this.exitPos.x&&y===this.exitPos.y) this.complete(); }
  hints(){ if(this.wid!==1||SAVE.settings.tutorial===undefined) return; const H=[[4,'Collect all the yellow Code Bits'],[10,'Touch a purple ? node to answer a question'],[18,'Avoid the colorful bugs!'],[26,'Grab power-ups: U S D M K L'],[34,'Clear bits + quizzes, beat the boss, then reach the green EXIT']];
    if (this.hint<H.length&&this.t>H[this.hint][0]) UI.toast('💡 '+H[this.hint++][1],'#FBBC04'); }
  summary(){ const q=this.qOK+this.qBad; return {world:this.wid,score:this.score,xp:this.runXP,q,acc:q?Math.round(100*this.qOK/q):100,enemies:this.enemiesKilled,time:this.t}; }
  finishRun(result){
    const s=SAVE.stats; s.time+=this.t; s.score+=this.score; SAVE.best=Math.max(SAVE.best,this.score);
    const sm=this.summary(); Leaderboard.submit({score:this.score,world:this.wid,xp:this.runXP,acc:sm.acc,date:Date.now(),result}); return sm;
  }
  complete(){
    this.state='done'; Audio.sfx('win'); const W=this.W, sm0=this.summary(), bonuses=[['World complete',500]]; let bonus=500;
    if (!this.lostLife) { bonus+=300; bonuses.push(['No life lost',300]); }
    if (this.wid===5&&this.t<=W.parTime) { bonus+=300; bonuses.push(['Par-time speed bonus',300]); }
    this.score+=bonus; this.runXP+=Progress.addXP(150);
    const acc=sm0.acc/100, stars=1+(acc>=.7?1:0)+(acc>=.7&&!this.lostLife?1:0); SAVE.stars[this.wid]=Math.max(SAVE.stars[this.wid]||0,stars);
    SAVE.completed[this.wid]=true; SAVE.unlocked=Math.min(7,Math.max(SAVE.unlocked,this.wid+1)); SAVE.stats.levels++;
    if (!this.lostLife) SAVE.events.flawless=true; if (this.lives===1) SAVE.events.lastLife=true;
    const sm=this.finishRun('Completed'); Save.save(); const ach=Progress.check(); Save.save(); HUD.hide(); Audio.music('win',false);
    const r=Object.assign(sm,{stars,bonuses,ach}); this.state='ended'; if(this.wid===7) UI.ending(r); else UI.levelComplete(r);
  }
  gameOver(){
    this.state='ended'; Audio.music('over',false); const sm=this.finishRun('Game over'); Save.save(); const ach=Progress.check(); HUD.hide(); UI.gameOver(Object.assign(sm,{ach}));
  }
  pushHud(){
    const pw=[]; for(const [k,c] of [['freeze','U'],['spd','S'],['xpm','M'],['scan','K']]) if(this[k]>0) pw.push({icon:POWER[c].icon,name:POWER[c].name,left:Math.ceil(this[k])+'s'});
    if(this.shield) pw.push({icon:'pu_D',name:'Debug Shield',left:'ON'}); if(this.dashCd>0) pw.push({icon:'pu_S',name:'Dash cooldown',left:Math.ceil(this.dashCd)+'s',cd:1}); if(this.tpCd>0) pw.push({icon:'pu_L',name:'Teleport cooldown',left:Math.ceil(this.tpCd)+'s',cd:1});
    const b=this.boss, phases=this.W.boss.phases;
    HUD.set({score:this.score,lives:this.lives,xp:this.runXP,world:this.W.name,bits:this.left,time:this.t,powers:pw,boss:b&&!b.down&&this.left+this.nodes.size<=this.total?{name:this.W.boss.name,hp:b.hp,max:b.max,phase:phases[Math.min(b.max-b.hp,phases.length-1)].name}:(b&&!b.down?{name:this.W.boss.name,hp:b.hp,max:b.max,phase:'Boss'}:null)});
  }
}
