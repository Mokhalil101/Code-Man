// Loads, validates and selects questions (world topic + difficulty mix + allowed types, no repeats per level session)
class QuestionManager {
  constructor(list){ this.all=(list||[]).filter(QuestionManager.valid); this.used=new Set(); }
  static valid(q){
    if (!q||typeof q.id!=='string'||typeof q.question!=='string'||![1,2,3].includes(q.difficulty)) return false;
    if (q.type==='arrange') return Array.isArray(q.lines)&&q.lines.length>=3&&q.lines.every(l=>typeof l==='string');
    return Array.isArray(q.options)&&q.options.length>=2&&q.options.length<=6&&Number.isInteger(q.correctAnswer)&&q.correctAnswer>=0&&q.correctAnswer<q.options.length;
  }
  reset(){ this.used.clear(); }
  next(o={}){
    const mix=o.mix||{}; let r=Math.random(), acc=0, d=1;
    for (const k of [1,2,3]) { acc+=+(mix[k]||0); d=k; if (r<=acc) break; }
    const free=q=>!this.used.has(q.id), tp=q=>!o.topics||o.topics.includes(q.topic), ty=q=>!o.types||o.types.includes(q.type);
    const tries=[q=>free(q)&&tp(q)&&ty(q)&&q.difficulty===d, q=>free(q)&&tp(q)&&ty(q), q=>free(q)&&tp(q)&&q.difficulty===d, q=>free(q)&&tp(q), q=>free(q)&&q.difficulty===d, free];
    let pool=[]; for (const f of tries){ pool=this.all.filter(f); if (pool.length) break; }
    if (!pool.length) { this.used.clear(); pool=this.all.filter(tp); if (!pool.length) pool=this.all; }
    const q=pool[Math.floor(Math.random()*pool.length)]; this.used.add(q.id); return q;
  }
}
