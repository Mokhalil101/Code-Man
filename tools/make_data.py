# Generates data/levels/world1..7.json and data/achievements.json.  Run from project root: python3 tools/make_data.py
import json, random
from collections import deque
D4 = [(0,1),(0,-1),(1,0),(-1,0)]
def info(g):
    op = [(x,y) for y in range(15) for x in range(19) if g[y][x] != '#']
    s = op[0]; seen = {s}; dq = deque([s])
    while dq:
        x,y = dq.popleft()
        for dx,dy in D4:
            n = (x+dx,y+dy)
            if g[n[1]][n[0]] != '#' and n not in seen: seen.add(n); dq.append(n)
    dead = [(x,y) for x,y in op if sum(g[y+dy][x+dx] != '#' for dx,dy in D4) <= 1]
    return len(seen) == len(op), dead
def base(seed):
    r = random.Random(seed)
    for _ in range(8000):
        g = [['#' if x in (0,18) or y in (0,14) else '.' for x in range(19)] for y in range(15)]
        for y in range(2,13,2):
            for x in range(2,17,2): g[y][x] = '#'
        for y in range(2,13,2):
            for x in range(2,9,2):
                if r.random() < .6: g[y][x+1] = '#'; g[y][18-(x+1)] = '#'
                if y != 6 and y < 12 and r.random() < .5: g[y+1][x] = '#'; g[y+1][18-x] = '#'
        ok, dead = info(g)
        if ok and len(dead) <= 2 and sum(c == '#' for row in g for c in row) > 120: return g, r
    raise SystemExit('maze failed')
def build(seed, nq, extra):
    g, r = base(seed)
    P, E = (9,13), (9,1); corners = [(1,1),(17,1),(1,13),(17,13)]
    fixed = {P, E, *corners}
    cells = [(x,y) for y in range(15) for x in range(19) if g[y][x] == '.' and y != 7 and (x,y) not in fixed]
    r.shuffle(cells); used = set()
    def take(k, ok=lambda c: True, spread=0, away=None):
        out = []
        for c in cells:
            if len(out) == k: break
            if c in used or not ok(c): continue
            if all(abs(c[0]-o[0])+abs(c[1]-o[1]) >= spread for o in out) and (away is None or abs(c[0]-away[0])+abs(c[1]-away[1]) >= 4):
                out.append(c); used.add(c)
        return out
    put = lambda lst, ch: [g[y].__setitem__(x, ch) for x, y in lst]
    put(take(nq, spread=5, away=P), 'Q')
    deadish = lambda c: sum(g[c[1]+dy][c[0]+dx] != '#' for dx,dy in D4) <= 2
    for ch in 'USDMKL': put(take(1), ch)
    put(take(extra.get('D', 0)), 'D'); put(take(4), 'o')
    put(take(extra.get('T', 2), ok=deadish) or take(extra.get('T', 2)), 'T')
    if extra.get('O'): put([(5,3),(13,11)][:extra['O']], 'O')
    if extra.get('C'): put(take(extra['C'], spread=3, ok=lambda c: abs(c[0]-9) + abs(c[1]-13) > 3), 'C')
    for x, y in corners: g[y][x] = 'B'
    g[P[1]][P[0]] = 'P'; g[E[1]][E[0]] = 'E'
    for x in (7,8,10,11): g[7][x] = 'G'
    g[7][9] = 'X'
    assert info([[('.' if c not in '#' else '#') for c in row] for row in g])[0]
    return [''.join(row) for row in g]
W = [
 dict(name='Python City', sub='Variables, data types, operators, strings, lists and basic functions.', topic='python', diff='Easy', accent='#4285F4', bg='#0b1530', mix=(.8,.2,0), speed=2.9, nq=4, hp=3,
      boss=('The Indentation Monster','Indentation and syntax challenges.'), pat=['dash'], mech='Tutorial hints guide your first run. Gentle enemies.', par=170, extra={}),
 dict(name='Loop Valley', sub='If/else, for and while loops, break/continue, nested loops and conditions.', topic='loops', diff='Easy-Medium', accent='#34A853', bg='#08241a', mix=(.6,.4,0), speed=3.05, nq=4, hp=3,
      boss=('Infinite Loop','Break the endless execution cycle with loop questions.'), pat=['summon'], mech='Looping obstacles patrol the corridors (they bounce back and forth).', par=170, extra={'O': 2}),
 dict(name='Data Dungeon', sub='Arrays, lists, stacks, queues, linked lists, hash maps, dictionaries and sets.', topic='data', diff='Medium', accent='#A142F4', bg='#1a0f2e', mix=(.4,.5,.1), speed=3.2, nq=5, hp=4,
      boss=('The Memory Eater','Data structure and memory challenges.'), pat=['teleport'], mech='Hidden storage chambers hold extra secret collectibles. Use the Code Scanner.', par=200, extra={'T': 4}),
 dict(name='OOP Fortress', sub='Classes, objects, constructors, encapsulation, inheritance, polymorphism and abstraction.', topic='oop', diff='Medium', accent='#EA4335', bg='#2a0e12', mix=(.25,.55,.2), speed=3.35, nq=5, hp=4,
      boss=('The Class Destroyer','Object-oriented design challenges.'), pat=['shield'], mech='Extra Debug Shields are hidden in the fortress to survive its guards.', par=210, extra={'D': 2}),
 dict(name='Algorithm Arena', sub='Searching, sorting, recursion, binary search, merge/quick sort and Big O.', topic='algo', diff='Hard', accent='#FBBC04', bg='#2a2108', mix=(.15,.5,.35), speed=3.5, nq=5, hp=4,
      boss=('The Complexity Beast','Complexity and algorithm-selection challenges.'), pat=['dash','shield'], mech='Timed arena: finish under the par time for a +300 speed bonus.', par=150, extra={}),
 dict(name='Debugging Lab', sub='Syntax, runtime and logic errors, exceptions, testing and code tracing.', topic='debug', diff='Hard', accent='#FF7043', bg='#2a1208', mix=(.1,.4,.5), speed=3.65, nq=6, hp=5,
      boss=('The Runtime Reaper','Find the bug, fix the code, trace the error.'), pat=['teleport','summon'], mech='Corrupted tiles flicker, warn, then become deadly. Watch the red glitch.', par=230, extra={'C': 6}),
 dict(name='Cyber Core', sub='Mixed advanced programming, algorithms, data structures and computer science.', topic='advanced', diff='Advanced', accent='#00E5FF', bg='#07161f', mix=(0,.3,.7), speed=3.8, nq=6, hp=5,
      boss=('CORE VIRUS','The ultimate enemy: five phases, five kinds of challenge.'), pat=['dash','teleport','summon','shield'], mech='All hazards combined, faster enemies, and a five-phase final boss.', par=260, extra={'O': 2, 'C': 4, 'T': 3}),
]
PH = [dict(name='Phase 1: Syntax Corruption', topics=['debug','python'], types=['bug','fix','mcq','output'], mix=[.4,.5,.1]),
      dict(name='Phase 2: Logic Infection', topics=['loops','advanced'], types=['output','logic','fill','bug'], mix=[.1,.6,.3]),
      dict(name='Phase 3: Memory Collapse', topics=['data','oop'], types=None, mix=[.1,.5,.4]),
      dict(name='Phase 4: Algorithm Overload', topics=['algo'], types=['complexity','algorithm','output','arrange'], mix=[0,.3,.7]),
      dict(name='Final Phase: Core Shutdown', topics=None, types=None, mix=[0,.2,.8])]
lv1 = ["###################","#........#........#","#.##.###.#.###.##.#","#U.......Q.......D#","#.##.#.#####.#.##.#","#....#...#...#....#","####.###.#.###.####","#......GGGG.......#","####.###.#.###.####","#....#...#...#....#","#.##.#.#####.#.##.#","#S..Q.....P.....Q.#","#.##.###.#.###.##.#","#B.......E.......B#","###################"]
for i, w in enumerate(W, 1):
    if i == 1:
        g = [list(r) for r in lv1]; g[7] = list("#.....GG.X.GG.....#")
        for ch, (x,y) in zip('MKLoooTT', [(7,5),(11,9),(5,13),(3,1),(15,13),(1,9),(17,5),(13,5)]):
            if g[y][x] == '.': g[y][x] = ch
        # keep Q count 3 -> add one more node
        g[3][12] = 'Q' if g[3][12] == '.' else g[3][12]
        maze = [''.join(r) for r in g]
    else: maze = build(100+i, w['nq'], w['extra'])
    phases = PH if i == 7 else [dict(name=w['boss'][0], topics=[w['topic']], types=None, mix=list(w['mix'][:2]) + [max(.1, w['mix'][2])])]
    L = {"worldId": i, "name": w['name'], "subtitle": w['sub'], "topic": w['topic'], "difficulty": w['diff'],
         "theme": {"accent": w['accent'], "bg": w['bg'], "wall": f"wall{i}", "boss": f"boss{i}", "music": f"m_w{i}"},
         "difficultyMix": {"1": w['mix'][0], "2": w['mix'][1], "3": w['mix'][2]}, "ghostSpeed": w['speed'],
         "cycle": {"scatter": max(3, 7-i//2), "chase": 14 + i}, "parTime": w['par'], "mechanic": w['mech'],
         "boss": {"name": w['boss'][0], "description": w['boss'][1], "hp": w['hp'] if i < 7 else 5, "patterns": w['pat'], "phases": phases},
         "mazeLayout": maze}
    assert len(maze) == 15 and all(len(r) == 19 for r in maze) and 'X' in ''.join(maze) and 'E' in ''.join(maze)
    json.dump(L, open(f'data/levels/world{i}.json', 'w'), indent=1)
    print(i, w['name'], 'Q', ''.join(maze).count('Q'), 'T', ''.join(maze).count('T'), 'C', ''.join(maze).count('C'), 'O', ''.join(maze).count('O'))
A = [
 ("first_steps","First Steps","Complete your first world.","👣","stat","levels",1),
 ("code_collector","Code Collector","Collect 100 Code Bits.","💾","stat","bits",100),
 ("bit_hoarder","Bit Hoarder","Collect 1000 Code Bits.","🗄️","stat","bits",1000),
 ("perfect_answer","Perfect Answer","Answer 10 questions correctly in a row.","🎯","stat","bestStreak",10),
 ("bug_hunter","Bug Hunter","Defeat 20 enemies.","🐞","stat","enemies",20),
 ("untouchable","Untouchable","Complete a world without losing a life.","🛡️","event","flawless",1),
 ("speed_coder","Speed Coder","Answer 10 questions quickly.","⚡","stat","fast",10),
 ("quiz_rookie","Quiz Rookie","Answer 25 questions correctly.","📘","stat","correct",25),
 ("quiz_master","Quiz Master","Answer 100 questions correctly.","🎓","stat","correct",100),
 ("code_sage","Code Sage","Answer 300 questions correctly.","🧙","stat","correct",300),
 ("debug_master","Debug Master","Complete the Debugging Lab.","🔧","world","6",1),
 ("boss_slayer","Boss Slayer","Defeat three bosses.","⚔️","stat","bosses",3),
 ("explorer","World Traveler","Complete four worlds.","🗺️","stat","worlds",4),
 ("code_legend","Code Legend","Complete all seven worlds.","👑","stat","worlds",7),
 ("core_destroyer","Core Destroyer","Defeat the Core Virus.","💥","event","coreDown",1),
 ("secret_hunter","Secret Hunter","Find 3 secret collectibles.","⭐","stat","secrets",3),
 ("power_user","Power User","Collect 15 power-ups.","🔋","stat","powerups",15),
 ("teleporter","Warp Speed","Use the Teleport Chip 3 times.","🌀","stat","teleports",3),
 ("high_scorer","High Scorer","Reach a best score of 5000.","🏆","stat","best",5000),
 ("bug_hunter_rank","Rank: Bug Hunter","Reach 800 XP.","🎖️","stat","xp",800),
 ("last_stand","Last Stand","Complete a world with only one life left.","❤️","event","lastLife",1),
]
json.dump([dict(id=a[0], name=a[1], desc=a[2], icon=a[3], type=a[4], key=a[5], min=a[6]) for a in A], open('data/achievements.json','w'), indent=1)
print(len(A), 'achievements')
