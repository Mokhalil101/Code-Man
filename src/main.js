// Application controller: data loading, screen flow, game start / pause / resume.
const App = {
  world:1, game:null,
  async boot(){
    UI.init();
    try {
      const j=async u=>{ const r=await fetch(u); if(!r.ok) throw new Error(u+' '+r.status); return r.json(); };
      DATA.worlds=await Promise.all([1,2,3,4,5,6,7].map(i=>j('data/levels/world'+i+'.json')));
      DATA.ach=await j('data/achievements.json');
      DATA.questions=(await Promise.all(['python','loops','data-structures','oop','algorithms','debugging','advanced'].map(f=>j('data/questions/'+f+'.json')))).flat();
    } catch(e){ $('#ld-msg').textContent='Could not load game data — run via a web server (see README).'; return; }
    (document.fonts?document.fonts.load('12px "Press Start 2P"').catch(()=>{}):Promise.resolve()).then(()=>{
      this.game=new Phaser.Game({type:Phaser.AUTO,parent:'game',width:COLS*T,height:ROWS*T,backgroundColor:'#101827',scale:{mode:Phaser.Scale.FIT,autoCenter:Phaser.Scale.CENTER_BOTH},scene:[PreloadScene,GameScene]});
      window.game=this.game; if (window.ResizeObserver) new ResizeObserver(()=>{ try{ this.game.scale.refresh(); }catch(e){} }).observe($('#game')); });   // refit the canvas whenever its container changes (HUD show/hide, rotation)
  },
  loaded(){ $('#ld-msg').textContent='Ready'; const go=$('#ld-start'); go.hidden=false; const start=()=>{ document.removeEventListener('keydown',start); go.removeEventListener('click',start); Audio.sfx('jingle'); $('#loader').classList.add('out'); setTimeout(()=>$('#loader').remove(),600); this.menu(); };
    document.addEventListener('keydown',start); go.addEventListener('click',start); },
  menu(){ try{ this.game.scene.stop('Game'); }catch(e){} Quiz.close(); HUD.hide(); UI.hideAll(); Audio.music('menu'); UI.menu(); },
  play(){ SAVE.settings.tutorial?UI.worldMap(Math.min(7,SAVE.unlocked)):UI.tutorial(true); },
  continue(){ this.startWorld(Math.min(7,SAVE.unlocked)); },
  startWorld(id){ if(!SAVE.settings.tutorial&&id===1&&SAVE.xp===0&&!SAVE.completed[1]){ UI.tutorial(true); return; } this.world=id; Quiz.close(); UI.hideAll(); HUD.show(); this.game.scene.stop('Game'); this.game.scene.start('Game',{world:id}); },
  pause(){ const s=this.game.scene.getScene('Game'); if(!s||s.state!=='playing') return; s.state='paused'; UI.pauseMenu(); },
  resume(){ const s=this.game.scene.getScene('Game'); UI.closeModal(); if(s&&s.state==='paused') s.state='playing'; }
};
App.scene=function(){ return this.game&&this.game.scene.isActive('Game')?this.game.scene.getScene('Game'):null; };
const KEYDIR={ArrowLeft:[-1,0],a:[-1,0],A:[-1,0],ArrowRight:[1,0],d:[1,0],D:[1,0],ArrowUp:[0,-1],w:[0,-1],W:[0,-1],ArrowDown:[0,1],s:[0,1],S:[0,1]};
document.addEventListener('keydown',e=>{
  if (Quiz.active||e.repeat&&e.key==='Escape') return; const s=App.scene(), k=e.key;
  if (s&&s.state==='playing') { if (KEYDIR[k]) { Input.x=KEYDIR[k][0]; Input.y=KEYDIR[k][1]; e.preventDefault(); } else if (k===' ') { Input.dash=true; e.preventDefault(); } }
  if (k==='Escape'||k==='p'||k==='P') { if (s&&s.state==='playing') App.pause(); else if (s&&s.state==='paused'&&$('#modal .dialog h2')&&$('#modal .dialog h2').textContent==='Paused') App.resume(); }
});
window.addEventListener('DOMContentLoaded',()=>App.boot());
