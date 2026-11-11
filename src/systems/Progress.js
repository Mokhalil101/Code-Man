// XP, ranks, achievements, statistics helpers, local leaderboard (clearly local — no backend)
const Progress = {
  rankIdx(xp=SAVE.xp){ let r=0; RANKS.forEach((x,i)=>{ if (xp>=x.xp) r=i; }); return r; },
  rank(){ return RANKS[this.rankIdx()]; },
  nextRank(){ return RANKS[this.rankIdx()+1]||null; },
  addXP(n){ n=Math.round(n); const b=this.rankIdx(); SAVE.xp+=n; if (this.rankIdx()>b) { UI.toast('🎖️ Rank up: '+this.rank().n,'#FBBC04'); Audio.sfx('win'); } return n; },
  worlds(){ return Object.keys(SAVE.completed).length; },
  accuracy(){ const s=SAVE.stats, t=s.correct+s.wrong; return t?Math.round(100*s.correct/t):0; },
  value(a){ if (a.key==='worlds') return this.worlds(); if (a.key==='best') return SAVE.best; if (a.key==='xp') return SAVE.xp; return SAVE.stats[a.key]||0; },
  achieved(a){ if (a.type==='event') return !!SAVE.events[a.key]; if (a.type==='world') return !!SAVE.completed[a.key]; return this.value(a)>=a.min; },
  check(){
    const got=[]; for (const a of DATA.ach) if (!SAVE.ach[a.id]&&this.achieved(a)) { SAVE.ach[a.id]=Date.now(); got.push(a); }
    got.forEach(a=>{ UI.toast(a.icon+' Achievement unlocked: '+a.name,'#34A853'); Audio.sfx('secret'); SAVE.xp+=100; });
    if (got.length) Save.save(); return got;
  },
  event(k){ if (!SAVE.events[k]) { SAVE.events[k]=true; Save.save(); } this.check(); }
};
const Leaderboard = { label:'LOCAL — this device only', top(n=10){ return SAVE.history.slice().sort((a,b)=>b.score-a.score).slice(0,n); },
  submit(e){ SAVE.history.push(e); SAVE.history=SAVE.history.slice(-30); Save.save(); } };
