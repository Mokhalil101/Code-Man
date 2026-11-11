// Global constants — CODE MAN, powered by GDG Assiut
const T = 32, COLS = 19, ROWS = 15;
const DIRS = [{x:0,y:-1},{x:-1,y:0},{x:0,y:1},{x:1,y:0}];
const Input = {x:0, y:0, dash:false};          // desired direction (keyboard / swipe / joystick); persists = movement buffering
const PAL = {blue:'#4285F4', red:'#EA4335', yellow:'#FBBC04', green:'#34A853', navy:'#101827', surface:'#172337', text:'#F8FAFC', muted:'#94A3B8'};
const RANKS = [{n:'Beginner Coder',xp:0},{n:'Code Explorer',xp:300},{n:'Bug Hunter',xp:800},{n:'Logic Master',xp:1600},{n:'Algorithm Engineer',xp:3000},{n:'Senior Developer',xp:5000},{n:'Code Legend',xp:8000}];
const POWER = { U:{name:'Power Compiler',dur:5,icon:'pu_U'}, S:{name:'Speed Boost',dur:7,icon:'pu_S'}, D:{name:'Debug Shield',dur:0,icon:'pu_D'},
                M:{name:'XP Multiplier',dur:15,icon:'pu_M'}, K:{name:'Code Scanner',dur:8,icon:'pu_K'}, L:{name:'Teleport Chip',dur:0,icon:'pu_L'} };
const DATA = {worlds:[], questions:[], ach:[]};
const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => [...r.querySelectorAll(s)];
const h = (tag, attrs={}, ...kids) => { const e = document.createElement(tag);
  for (const [k,v] of Object.entries(attrs||{})) { if (k==='class') e.className=v; else if (k.startsWith('on')) e.addEventListener(k.slice(2),v); else if (v!==false&&v!=null) e.setAttribute(k,v); }
  kids.flat().forEach(c => e.append(c instanceof Node ? c : document.createTextNode(c==null?'':String(c)))); return e; };
// Set gdgLogo to true after placing the official GDG Assiut logo at assets/icons/gdg-assiut-logo.png (the game never invents a logo).
const CONFIG = { gdgLogo: false };
