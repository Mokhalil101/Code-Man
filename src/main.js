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

// ==========================================
// GAMEPAD UI NAVIGATION
// Controller support for menus, quiz and UI
// ==========================================

(function GamepadUI() {
  const DEADZONE = 0.55;

  let previous = {
    up: false,
    down: false,
    left: false,
    right: false,
    confirm: false,
    back: false,
    start: false
  };

  function visible(el) {
    return el &&
      !el.closest('[hidden]') &&
      el.getClientRects().length > 0;
  }

  function getButtons() {
    const roots = [
      '#screens',
      '#modal',
      '#quiz',
      '#loader'
    ];

    return roots
      .map(selector => document.querySelector(selector))
      .filter(root => root && visible(root))
      .flatMap(root =>
        [...root.querySelectorAll('button:not(:disabled)')]
      )
      .filter(visible);
  }

  function moveSelection(direction) {
    const buttons = getButtons();

    if (!buttons.length) return;

    let index = buttons.indexOf(document.activeElement);

    if (index === -1) {
      index = direction > 0 ? -1 : 0;
    }

    index = (index + direction + buttons.length)
      % buttons.length;

    buttons[index].focus({ preventScroll: true });

    buttons[index].scrollIntoView({
      block: 'nearest',
      behavior: 'smooth'
    });
  }

  function confirmSelection() {
    const buttons = getButtons();

    if (!buttons.length) return;

    const current = document.activeElement;

    if (buttons.includes(current)) {
      current.click();
    } else {
      buttons[0].focus();
      buttons[0].click();
    }
  }

  function backAction() {
    const buttons = getButtons();

    // Find a Back or Cancel button
    const backButton = buttons.find(button =>
      /\b(back|cancel)\b/i.test(button.textContent)
    );

    if (backButton) {
      backButton.click();
      return;
    }

    // Resume from pause menu
    const title = document.querySelector(
      '#modal .dialog h2'
    );

    if (
      visible(document.querySelector('#modal')) &&
      title?.textContent === 'Paused'
    ) {
      App.resume();
    }
  }

  function update() {
    const pads = navigator.getGamepads
      ? navigator.getGamepads()
      : [];

    const pad = [...pads].find(p => p && p.connected);

    if (pad) {
      const x = pad.axes[0] || 0;
      const y = pad.axes[1] || 0;

      const state = {
        up: y < -DEADZONE || !!pad.buttons[12]?.pressed,
        down: y > DEADZONE || !!pad.buttons[13]?.pressed,
        left: x < -DEADZONE || !!pad.buttons[14]?.pressed,
        right: x > DEADZONE || !!pad.buttons[15]?.pressed,

        confirm: !!pad.buttons[0]?.pressed,
        back: !!pad.buttons[1]?.pressed,
        start: !!pad.buttons[9]?.pressed
      };

      const buttons = getButtons();
      const uiActive = buttons.length > 0;

      if (uiActive) {
        // Navigate menus and questions
        if (state.up && !previous.up) {
          moveSelection(-1);
        }

        if (state.down && !previous.down) {
          moveSelection(1);
        }

        if (state.left && !previous.left) {
          moveSelection(-1);
        }

        if (state.right && !previous.right) {
          moveSelection(1);
        }

        // Confirm selection
        if (state.confirm && !previous.confirm) {
          confirmSelection();
        }

        // Back / Cancel
        if (state.back && !previous.back) {
          backAction();
        }
      } else {
        // Start / Pause while playing
        if (state.start && !previous.start) {
          const scene = App.scene();

          if (scene && scene.state === 'playing') {
            App.pause();
          } else if (scene && scene.state === 'paused') {
            App.resume();
          }
        }
      }

      previous = state;
    } else {
      previous = {
        up: false,
        down: false,
        left: false,
        right: false,
        confirm: false,
        back: false,
        start: false
      };
    }

    requestAnimationFrame(update);
  }

  window.addEventListener('gamepadconnected', e => {
    console.log('Controller connected:', e.gamepad.id);
  });

  window.addEventListener('gamepaddisconnected', e => {
    console.log('Controller disconnected:', e.gamepad.id);
  });

  requestAnimationFrame(update);
})();

window.addEventListener('DOMContentLoaded',()=>App.boot());
