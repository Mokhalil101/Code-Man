// Fullscreen toggle (F key, buttons, double-click on the maze, controller SHARE / touchpad). Prefixed API for older Safari.
// iPhone Safari has no Fullscreen API for pages: the buttons are hidden there and the PWA meta tags in index.html
// give a fullscreen experience via "Add to Home Screen".
const Full = {
  el: document.documentElement,
  supported(){ return !!(document.fullscreenEnabled || document.webkitFullscreenEnabled); },
  active(){ return !!(document.fullscreenElement || document.webkitFullscreenElement); },
  async toggle(){
    try {
      if (this.active()) { await (document.exitFullscreen || document.webkitExitFullscreen).call(document); }
      else if (this.supported()) { const f = this.el.requestFullscreen || this.el.webkitRequestFullscreen; await f.call(this.el, {navigationUI:'hide'}); }
      else if (window.UI) UI.toast('Fullscreen is not available here — use “Add to Home Screen” for full-screen play','#FBBC04');
    } catch (e) { if (window.UI) UI.toast('Fullscreen was blocked by the browser — press F or the ⛶ button','#FBBC04'); }
  },
  sync(){
    const on = this.active(); document.body.classList.toggle('is-full', on);
    const ico = on ? 'M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5' : 'M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5';
    document.querySelectorAll('[data-fs]').forEach(b => { b.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="' + ico + '"/></svg>'; b.title = on ? 'Exit fullscreen (F)' : 'Fullscreen (F)'; b.setAttribute('aria-label', b.title); });
    setTimeout(() => { try { App.game.scale.refresh(); } catch (_) {} }, 60);
  },
  init(){
    document.querySelectorAll('[data-fs]').forEach(b => { b.hidden = !this.supported(); b.addEventListener('click', e => { e.stopPropagation(); this.toggle(); }); });
    ['fullscreenchange', 'webkitfullscreenchange'].forEach(ev => document.addEventListener(ev, () => this.sync()));
    document.addEventListener('keydown', e => { if ((e.key === 'f' || e.key === 'F') && !e.ctrlKey && !e.metaKey && !e.altKey && !/INPUT|SELECT|TEXTAREA/.test((e.target.tagName||''))) { e.preventDefault(); this.toggle(); } });
    window.addEventListener('resize', () => { try { App.game.scale.refresh(); } catch (_) {} });
    window.addEventListener('orientationchange', () => setTimeout(() => { try { App.game.scale.refresh(); } catch (_) {} }, 250));
    this.sync();
  }
};
