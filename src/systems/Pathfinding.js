// BFS distance fields: every enemy walks "downhill" on a field computed from its target tile.
const Path = {
  field(map, tx, ty, pass){
    const R=map.length, C=map[0].length, d=Array.from({length:R},()=>new Array(C).fill(Infinity));
    if (!pass(tx,ty)) return d; d[ty][tx]=0; const q=[[tx,ty]];
    for (let i=0;i<q.length;i++){ const [x,y]=q[i];
      for (const v of DIRS){ const nx=x+v.x, ny=y+v.y; if (ny>=0&&ny<R&&nx>=0&&nx<C&&d[ny][nx]===Infinity&&pass(nx,ny)) { d[ny][nx]=d[y][x]+1; q.push([nx,ny]); } } }
    return d;
  },
  nearest(x, y, pass){ for (let r=0;r<8;r++) for (let dy=-r;dy<=r;dy++) for (let dx=-r;dx<=r;dx++) if (pass(x+dx,y+dy)) return [x+dx,y+dy]; return [x,y]; },
  step(field, m, pass){ // best neighbour; avoids reversing unless it is the only way
    const rev={x:-m.dir.x,y:-m.dir.y}; let opts=DIRS.filter(v=>pass(m.gx+v.x,m.gy+v.y));
    const fwd=opts.filter(v=>!(v.x===rev.x&&v.y===rev.y)); if (fwd.length) opts=fwd;
    let best=null, bd=Infinity;
    for (const v of opts){ const val=(field[m.gy+v.y]||[])[m.gx+v.x]; const s=(val===undefined?Infinity:val)+Math.random()*.01; if (s<bd){bd=s;best=v;} }
    return best;
  }
};
