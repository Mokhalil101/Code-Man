// Versioned, validated LocalStorage persistence (survives corrupt / missing storage)
const SAVE_KEY = 'codeman_gdg_v2';
const Save = {
  def(){ return {v:2, best:0, xp:0, unlocked:1, completed:{}, stars:{}, ach:{}, events:{}, history:[],
    stats:{bits:0,enemies:0,correct:0,wrong:0,fast:0,streak:0,bestStreak:0,bosses:0,levels:0,secrets:0,powerups:0,teleports:0,deaths:0,time:0,questions:0,score:0},
    settings:{master:.8,music:.6,sfx:.8,mute:false,diff:1,tutorial:false}}; },
  num(v,lo=0,hi=1e12){ v=Number(v); return Number.isFinite(v)?Math.min(hi,Math.max(lo,v)):lo; },
  sanitize(r){
    const d=this.def(); if(!r||typeof r!=='object') return d;
    d.best=this.num(r.best); d.xp=this.num(r.xp); d.unlocked=Math.round(this.num(r.unlocked,1,7))||1;
    for(const k in d.stats) d.stats[k]=this.num(r.stats&&r.stats[k]);
    for(let i=1;i<=7;i++){ if(r.completed&&r.completed[i]===true) d.completed[i]=true; const s=Math.round(this.num(r.stars&&r.stars[i],0,3)); if(s) d.stars[i]=s; }
    for(const k of Object.keys(r.ach||{})) if(/^[a-z_]{1,32}$/.test(k)) d.ach[k]=this.num(r.ach[k]);
    for(const k of Object.keys(r.events||{})) if(/^[a-zA-Z]{1,32}$/.test(k)&&r.events[k]===true) d.events[k]=true;
    if(Array.isArray(r.history)) d.history=r.history.slice(-30).map(x=>({score:this.num(x&&x.score),world:Math.round(this.num(x&&x.world,1,7))||1,xp:this.num(x&&x.xp),acc:this.num(x&&x.acc,0,100),date:this.num(x&&x.date),result:String(x&&x.result||'').slice(0,12)}));
    const s=r.settings||{}; d.settings={master:this.num(s.master,0,1)||(s.master===0?0:.8),music:this.num(s.music,0,1),sfx:this.num(s.sfx,0,1),mute:s.mute===true,diff:Math.round(this.num(s.diff,0,2)),tutorial:s.tutorial===true};
    if(s.music===undefined) d.settings.music=.6; if(s.sfx===undefined) d.settings.sfx=.8; if(s.diff===undefined) d.settings.diff=1;
    return d;
  },
  load(){ try { const raw=localStorage.getItem(SAVE_KEY); return raw?this.sanitize(JSON.parse(raw)):this.def(); }
          catch(e){ try{ localStorage.setItem(SAVE_KEY+'_corrupt',localStorage.getItem(SAVE_KEY)); }catch(_){} return this.def(); } },
  save(){ try { localStorage.setItem(SAVE_KEY, JSON.stringify(SAVE)); } catch(e){} },
  reset(){ try { localStorage.removeItem(SAVE_KEY); } catch(e){} SAVE = this.def(); }
};
let SAVE = Save.load();
