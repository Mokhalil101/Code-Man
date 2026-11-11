// Loads all sprites + audio while the DOM loading screen shows progress.
class PreloadScene extends Phaser.Scene {
  constructor(){ super('Preload'); }
  preload(){
    const bar=$('#ld-bar i'), txt=$('#ld-pct');
    this.load.on('progress',v=>{ bar.style.width=Math.round(v*100)+'%'; txt.textContent=Math.round(v*100)+'%'; });
    ['pac0','pac1','bug0','bug1','bug2','bug3','scared','eyes','bit','chip','orb','secret','pu_U','pu_S','pu_D','pu_M','pu_K','pu_L','quiz','exit0','exit1','hazard','corrupt',
     ...[1,2,3,4,5,6,7].flatMap(i=>['wall'+i,'boss'+i])].forEach(k=>this.load.image(k,'assets/sprites/'+k+'.png'));
    ['click','bit','bonus','orb','secret','power','expire','squash','hit','good','bad','teleport','bosshit','win','jingle','over'].forEach(k=>this.load.audio('s_'+k,'assets/audio/s_'+k+'.wav'));
    ['menu','w1','w2','w3','w4','w5','w6','w7','boss','win','over'].forEach(k=>this.load.audio('m_'+k,'assets/audio/m_'+k+'.wav'));
  }
  create(){ Audio.init(this.game); App.loaded(); }
};
