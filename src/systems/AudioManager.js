// Master / music / SFX volume + mute. Uses Phaser's sound manager (respects browser autoplay rules).
const Audio = {
  g:null, m:null, key:null,
  init(game){ this.g = game; },
  vol(kind){ const s=SAVE.settings; return s.mute ? 0 : s.master * (kind==='music' ? s.music : s.sfx); },
  sfx(k, v=1){ try { const vol=this.vol('sfx')*v; if (vol>0) this.g.sound.play('s_'+k, {volume:Math.min(1,vol)}); } catch(e){} },
  music(k, loop=true){
    try {
      if (this.key===k && this.m && this.m.isPlaying) { this.refresh(); return; }
      if (this.m) { this.m.stop(); this.m.destroy(); this.m=null; }
      this.key=k; this.m=this.g.sound.add('m_'+k, {loop, volume:this.vol('music')*.7}); if (this.vol('music')>0) this.m.play();
    } catch(e){}
  },
  stopMusic(){ try { if (this.m) { this.m.stop(); this.m.destroy(); this.m=null; this.key=null; } } catch(e){} },
  refresh(){ try { if (!this.m) return; const v=this.vol('music')*.7; this.m.setVolume(v); if (v<=0) this.m.pause(); else if (this.m.isPaused) this.m.resume(); else if (!this.m.isPlaying) this.m.play(); } catch(e){} }
};
