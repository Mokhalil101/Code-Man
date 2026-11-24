// Gamepad support (PlayStation DualShock 4 / DualSense first, any "standard" pad works).
//   In game : left stick / D-pad = move · ✕ □ R1 R2 L1 L2 = dash · OPTIONS = pause · SHARE / touchpad = fullscreen
//   In menus: stick / D-pad = move focus (spatial) · ✕ = select · ○ = back / resume · △ = submit / continue (quiz)
// One polling loop, edge detection, hold-to-repeat, hot-plug, auto-pause on disconnect, rumble.
const Pad = (() => {
  const ENTER = 0.5, MOVE_DZ = 0.4;                  // menu stick threshold / in-game stick dead-zone
  const isPS = id => /054c|dualsense|dualshock|wireless controller|playstation|ps4|ps5/i.test(id||'');
  const BLANK = {up:0,down:0,left:0,right:0,cross:0,circle:0,square:0,triangle:0,l1:0,r1:0,l2:0,r2:0,options:0,share:0,ps:0,touch:0,ax:0,ay:0};
  let prev = {...BLANK}, cur = {...BLANK}, pad = null, hold = {dir:null, next:0}, notified = false;
  const api = {connected:false, ps:false, name:'', ui:false};

  const pressed = b => !!b && (b.pressed || b.value > 0.5);
  // Translate a raw Gamepad into the normalised state above (handles the non-standard Firefox PS layout too).
  function read(p) {
    const s = {...BLANK}, B = i => pressed(p.buttons[i]);
    let ax = p.axes[0] || 0, ay = p.axes[1] || 0;
    if (p.mapping === 'standard' || !isPS(p.id)) {
      Object.assign(s, {cross:B(0),circle:B(1),square:B(2),triangle:B(3),l1:B(4),r1:B(5),l2:B(6),r2:B(7),share:B(8),options:B(9),ps:B(16),touch:B(17),up:B(12),down:B(13),left:B(14),right:B(15)});
    } else {                                          // raw PS layout: □✕○△ = 0..3, D-pad is a hat axis (index 9)
      Object.assign(s, {square:B(0),cross:B(1),circle:B(2),triangle:B(3),l1:B(4),r1:B(5),l2:B(6),r2:B(7),share:B(8),options:B(9),ps:B(12),touch:B(13)});
      const hat = p.axes[9];
      if (hat !== undefined && hat < 1.1) { const k = Math.round((hat + 1) * 3.5);     // 0=N 1=NE 2=E 3=SE 4=S 5=SW 6=W 7=NW
        s.up = [0,1,7].includes(k); s.right = [1,2,3].includes(k); s.down = [3,4,5].includes(k); s.left = [5,6,7].includes(k); }
    }
    s.ax = ax; s.ay = ay;
    return s;
  }
  function pick() {                                   // most recently used connected pad
    const list = (navigator.getGamepads ? [...navigator.getGamepads()] : []).filter(p => p && p.connected);
    return list.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0))[0] || null;
  }
  const edge = k => cur[k] && !prev[k];

  // ---------- menu navigation ----------
  const SEL = 'button:not(:disabled), input:not(:disabled), select:not(:disabled)';
  const shown = el => el && !el.closest('[hidden]') && el.getClientRects().length > 0;
  function layer() {                                  // the top-most visible UI layer that has something to focus
    for (const id of ['#loader', '#modal', '#quiz', '#screens']) {
      const root = document.querySelector(id);
      if (shown(root)) { const els = [...root.querySelectorAll(SEL)].filter(shown); if (els.length) return {root, els}; }
    }
    return null;
  }
  function focusEl(el) { document.body.classList.add('pad-nav'); el.focus({preventScroll:true}); try { el.scrollIntoView({block:'nearest', inline:'nearest', behavior:'smooth'}); } catch (_) {} }
  function navigate(dir) {                            // dir: 'up' | 'down' | 'left' | 'right'
    const L = layer(); if (!L) return;
    const a = document.activeElement;
    if (!L.els.includes(a)) { focusEl(L.els.find(e => e.classList.contains('primary')) || L.els[0]); return; }
    const horiz = dir === 'left' || dir === 'right';
    if (horiz && a.type === 'range') { const st = Math.max(1, +a.step || 5) , d = dir === 'right' ? st : -st;
      a.value = Math.min(+a.max, Math.max(+a.min, +a.value + d)); a.dispatchEvent(new Event('input', {bubbles:true})); a.dispatchEvent(new Event('change', {bubbles:true})); return; }
    if (horiz && a.tagName === 'SELECT') { const i = Math.min(a.options.length - 1, Math.max(0, a.selectedIndex + (dir === 'right' ? 1 : -1)));
      if (i !== a.selectedIndex) { a.selectedIndex = i; a.dispatchEvent(new Event('change', {bubbles:true})); } return; }
    const r = a.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    let best = null, bs = Infinity;
    for (const e of L.els) { if (e === a) continue;
      const q = e.getBoundingClientRect(), dx = q.left + q.width / 2 - cx, dy = q.top + q.height / 2 - cy;
      const along = dir === 'up' ? -dy : dir === 'down' ? dy : dir === 'left' ? -dx : dx, across = horiz ? Math.abs(dy) : Math.abs(dx);
      if (along < 4) continue;
      const sc = along + across * 2.5; if (sc < bs) { bs = sc; best = e; } }
    if (!best && !horiz) { const i = L.els.indexOf(a), n = L.els.length; best = L.els[(i + (dir === 'down' ? 1 : -1) + n) % n]; }   // wrap top <-> bottom
    if (best) focusEl(best);
  }
  function confirm() {
    const L = layer(); if (!L) return; const a = document.activeElement;
    if (!L.els.includes(a)) { focusEl(L.els.find(e => e.classList.contains('primary')) || L.els[0]); return; }
    if (a.tagName === 'BUTTON' || a.type === 'checkbox') a.click();
  }
  function back() {
    const L = layer(); if (!L || L.root.id === 'loader') return;
    const b = L.els.find(e => e.tagName === 'BUTTON' && /\b(back|cancel|resume)\b/i.test(e.textContent));
    if (b) b.click();
  }
  function pauseOpen() { const s = App.game && App.game.scene.getScene('Game'), t = document.querySelector('#modal .dialog h2'); return !!(s && s.state === 'paused' && t && t.textContent === 'Paused' && shown(document.querySelector('#modal'))); }
  function submitQuiz() { const b = document.querySelector('#quiz .qactions .btn'); if (b && !b.disabled && shown(b)) b.click(); }

  // ---------- in-game ----------
  function play(scene) {
    const dx = cur.ax, dy = cur.ay;
    if (cur.left) { Input.x = -1; Input.y = 0; } else if (cur.right) { Input.x = 1; Input.y = 0; }
    else if (cur.up) { Input.x = 0; Input.y = -1; } else if (cur.down) { Input.x = 0; Input.y = 1; }
    else if (Math.max(Math.abs(dx), Math.abs(dy)) > MOVE_DZ) {            // analog stick: dominant axis wins
      if (Math.abs(dx) >= Math.abs(dy)) { Input.x = Math.sign(dx); Input.y = 0; } else { Input.y = Math.sign(dy); Input.x = 0; } }
    if (['cross','square','r1','r2','l1','l2'].some(edge)) Input.dash = true;
    if (edge('options')) App.pause();
  }

  function frame() {
    pad = pick(); const was = api.connected; api.connected = !!pad;
    if (pad) {
      if (!was || api.name !== pad.id) { api.name = pad.id; api.ps = isPS(pad.id); }
      prev = cur; cur = read(pad);
      const any = Object.keys(cur).some(k => k !== 'ax' && k !== 'ay' && cur[k]) || Math.abs(cur.ax) > ENTER || Math.abs(cur.ay) > ENTER;
      if (any && !notified) { notified = true; announce(); }
      const scene = App.scene && App.scene(), L = layer(); api.ui = !!L;
      if (L && notified && !L.els.includes(document.activeElement)) focusEl(L.els.find(e => e.classList.contains('primary')) || L.els[0]);   // cursor appears as soon as a menu opens
      if (edge('share') || edge('touch')) Full.toggle();
      if (L) {
        const dir = cur.up || cur.ay < -ENTER ? 'up' : cur.down || cur.ay > ENTER ? 'down' : cur.left || cur.ax < -ENTER ? 'left' : cur.right || cur.ax > ENTER ? 'right' : null, now = performance.now();
        if (dir && (dir !== hold.dir)) { hold = {dir, next: now + 380}; navigate(dir); }
        else if (dir && now >= hold.next) { hold.next = now + 130; navigate(dir); }
        else if (!dir) hold.dir = null;
        if (edge('cross')) confirm();
        if (edge('circle')) back();
        if (edge('triangle') && document.querySelector('#quiz:not([hidden])')) submitQuiz();
        if (edge('options') && pauseOpen()) App.resume();
      } else if (scene && scene.state === 'playing') { hold.dir = null; play(scene); }
    } else { prev = cur = {...BLANK}; }
    requestAnimationFrame(frame);
  }
  function announce() {
    const g = api.ps ? {ok:'✕', back:'○', dash:'□', sub:'△', pause:'OPTIONS', fs:'SHARE'} : {ok:'A', back:'B', dash:'X', sub:'Y', pause:'MENU', fs:'VIEW'};
    UI.toast('🎮 ' + (api.ps ? 'PlayStation controller' : 'Controller') + ' ready — ' + g.ok + ' select · ' + g.back + ' back · ' + g.dash + ' dash · ' + g.pause + ' pause', '#34A853');
  }
  // ---------- rumble (DualSense / DualShock 4 in Chrome & Edge) ----------
  api.rumble = (ms = 200, strong = .6, weak = .6) => {
    try { if (!pad || (SAVE.settings && SAVE.settings.rumble === false)) return;
      const v = pad.vibrationActuator; if (v && v.playEffect) v.playEffect('dual-rumble', {startDelay:0, duration:ms, strongMagnitude:strong, weakMagnitude:weak});
      else if (pad.hapticActuators && pad.hapticActuators[0]) pad.hapticActuators[0].pulse(strong, ms); } catch (_) {}
  };
  window.addEventListener('gamepadconnected', e => { notified = false; if (api.connected === false) { /* toast appears on first input */ } console.log('Controller connected:', e.gamepad.id); });
  window.addEventListener('gamepaddisconnected', e => {
    console.log('Controller disconnected:', e.gamepad.id); notified = false;
    UI.toast('🎮 Controller disconnected', '#EA4335');
    const s = App.scene && App.scene(); if (s && s.state === 'playing') App.pause();     // never lose a run to an unplugged pad
  });
  document.addEventListener('pointerdown', () => document.body.classList.remove('pad-nav'), true);
  document.addEventListener('mousemove', () => document.body.classList.remove('pad-nav'), true);
  requestAnimationFrame(frame);
  return api;
})();
