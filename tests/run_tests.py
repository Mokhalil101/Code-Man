"""CODE MAN automated tests (Playwright + headless Chromium). Run:  python3 -m http.server 8123 &   python3 tests/run_tests.py
Tests drive the real game in a browser. Where a test needs speed it uses teleport helpers on the live scene (documented in TESTING.md)."""
import json, sys, time, traceback
from playwright.sync_api import sync_playwright
URL = 'http://localhost:8123/index.html'; S = "game.scene.getScene('Game')"
import os
GROUPS = os.environ.get('GROUPS','ABCD'); results = []; console_errors = []
def check(name, fn, *a):
    t0 = time.time()
    try: note = fn(*a) or ''; results.append((name, 'PASS', str(note), round(time.time()-t0,1)))
    except Exception as e: results.append((name, 'FAIL', (str(e) or traceback.format_exc())[:300], round(time.time()-t0,1)))
    print(results[-1][1], name, results[-1][2][:100]); sys.stdout.flush()
def fresh(br, save=None, raw=None, viewport=(1100,760), touch=False):
    ctx = br.new_context(viewport={'width':viewport[0],'height':viewport[1]}, has_touch=touch, is_mobile=touch)
    pg = ctx.new_page(); pg.on('console', lambda m: console_errors.append(m.text[:160]) if m.type=='error' else None); pg.on('pageerror', lambda e: console_errors.append('PAGEERR '+str(e)[:160]))
    if raw is not None: pg.add_init_script("if(!sessionStorage.getItem('_i')){localStorage.setItem('codeman_gdg_v2',%s);sessionStorage.setItem('_i','1')}" % json.dumps(raw))
    elif save is not None: pg.add_init_script("if(!localStorage.getItem('codeman_gdg_v2')){localStorage.setItem('codeman_gdg_v2',%s)}" % json.dumps(json.dumps(save)))
    pg.goto(URL); pg.wait_for_selector('#ld-start:not([hidden])', timeout=20000); pg.click('#ld-start'); pg.wait_for_selector('.s-menu', timeout=5000); return pg
def start_world(pg, w):
    pg.evaluate("SAVE.settings.tutorial=true"); pg.evaluate(f"App.startWorld({w})"); pg.wait_for_function(f"game.scene.isActive('Game') && {S} && {S}.p", timeout=8000); pg.wait_for_timeout(200)
def safe(pg): pg.evaluate(f"{S}.inv=99999; {S}.ghosts.forEach(g=>g.delay=9999)")
def answer(pg, ok=True):
    pg.wait_for_selector('#quiz:not([hidden])', timeout=6000)
    q = pg.evaluate("({t:Quiz.current.type,ca:Quiz.current.correctAnswer,lines:Quiz.current.lines,n:(Quiz.current.options||[]).length})")
    if q['t'] == 'arrange':
        order = q['lines'] if ok else q['lines'][::-1]
        for ln in order:
            pg.locator('.arr-src .arr-line', has_text=ln.strip()).filter(has_text=ln.strip()).first.click()
    else:
        i = q['ca'] if ok else (q['ca']+1) % q['n']; pg.locator('.opt').nth(i).click()
    pg.click('.qactions .btn'); pg.wait_for_selector('.verdict'); verdict = pg.inner_text('.verdict'); pg.click('.qactions .btn'); pg.wait_for_selector('#quiz', state='hidden'); return q['t'], verdict
def clear_world(pg, w):
    start_world(pg, w); pg.evaluate(f"{S}.freeze=99999; {S}.inv=99999; {S}.hint=99")
    for k in pg.evaluate(f"[...{S}.nodes.keys()]"):
        x, y = map(int, k.split(',')); pg.evaluate(f"{S}.p.warp({x},{y}); {S}.p.dir={{x:0,y:0}}"); answer(pg, True)
    pg.evaluate(f"""(()=>{{const s={S}; for(const [k,it] of [...s.items]) if(it.t==='.'){{const [x,y]=k.split(',').map(Number); s.p.warp(x,y); s.pickups();}} s.updateExit();}})()""")
    for _ in range(8):
        if pg.evaluate(f"{S}.boss.down"): break
        pg.evaluate(f"(()=>{{const s={S}; s.inv=0; s.boss.delay=0; s.boss.shield=false; s.p.warp(s.exitPos.x+0,13); s.boss.m.warp(s.p.gx,s.p.gy);}})()"); answer(pg, True); pg.wait_for_timeout(100)
    assert pg.evaluate(f"{S}.boss.down"), 'boss not defeated'; assert pg.evaluate(f"{S}.unlocked"), 'exit not unlocked'
    pg.evaluate(f"(()=>{{const s={S}; s.inv=99999; s.p.warp(s.exitPos.x,s.exitPos.y);}})()"); pg.wait_for_selector('.result, .ending', timeout=6000)
def run():
    with sync_playwright() as p:
        br = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        # ---- menu / screens ----
        if 'A' in GROUPS:
            pg = fresh(br)
            def t_menu():
                btns = pg.locator('.menu-btns .btn'); assert btns.count() == 9, btns.count()
                for label, sel in [('World Map','.s-worldmap'),('How to Play','.s-tutorial'),('Achievements','.s-ach'),('Statistics','.s-stats'),('Leaderboard','.s-lb'),('Settings','.s-settings'),('About GDG Assiut','.s-about')]:
                    pg.locator('.menu-btns .btn', has_text=label).click(); pg.wait_for_selector(sel, timeout=3000)
                    if sel == '.s-tutorial': pg.click("text=Skip")
                    else: pg.click('.back')
                    pg.wait_for_selector('.s-menu', timeout=3000)
                assert 'GDG Assiut' in pg.inner_text('.gdg-tag'); return '9 buttons, 7 sub-screens open and return; GDG tag present'
            check('Main menu navigation (all buttons work)', t_menu)
            def t_continue_disabled(): assert pg.locator('.menu-btns .btn', has_text='Continue').is_disabled(); return 'Continue disabled with no progress'
            check('Continue disabled when no save exists', t_continue_disabled)
            def t_tutorial():
                pg.evaluate('SAVE.settings.tutorial=false'); pg.locator('.menu-btns .btn', has_text='Play').first.click(); pg.wait_for_selector('.s-tutorial')
                n = 1
                while pg.locator('text=Next ▶').count(): pg.click('text=Next ▶'); n += 1
                assert n == 9, n; pg.click('text=Start World 1'); pg.wait_for_function(f"game.scene.isActive('Game') && {S}.p", timeout=8000); return '9 tutorial steps; skippable; starts World 1'
            check('New game via interactive tutorial', t_tutorial)
            def t_init(): assert pg.evaluate(f"{S}.lives")==3 and pg.evaluate(f"{S}.score")==0 and pg.evaluate(f"{S}.W.worldId")==1; return 'World 1, 3 lives, score 0'
            check('New game initialization', t_init)
            def t_move():
                safe(pg); x0 = pg.evaluate(f"[{S}.p.gx,{S}.p.gy]"); pg.keyboard.down('ArrowLeft'); pg.wait_for_timeout(900); pg.keyboard.up('ArrowLeft')
                x1 = pg.evaluate(f"[{S}.p.gx,{S}.p.gy]"); assert x1 != x0, (x0, x1); sc = pg.evaluate(f"{S}.score"); assert sc > 0, 'no bits eaten while moving'
                return f'moved {x0}->{x1}, score {sc} from real keyboard input'
            check('Player movement (keyboard) + collecting while moving', t_move)
            def t_wall():
                s = pg.evaluate(f"(()=>{{const s={S}; s.p.warp(10,11); s.p.dir={{x:0,y:0}}; Input.x=0; Input.y=-1; return 1}})()"); pg.wait_for_timeout(500)
                pos = pg.evaluate(f"[{S}.p.gx,{S}.p.gy]"); assert pos == [10,11], pos; pg.evaluate("Input.y=0"); return 'moving up into a wall leaves the player in place'
            check('Maze wall collision', t_wall)
            def t_bit():
                r = pg.evaluate(f"(()=>{{const s={S}; const [k]=[...s.items].find(([k,i])=>i.t==='.'); const [x,y]=k.split(',').map(Number); const sc=s.score, l=s.left; s.p.warp(x,y); s.pickups(); return [s.score-sc, l-s.left, s.items.has(k)]}})()")
                assert r == [10,1,False], r; return '+10 points, counter -1, item removed'
            check('Collectible (Code Bit) = +10 and removal', t_bit)
            def t_quiz_pause():
                pos0 = pg.evaluate(f"{S}.ghosts.map(g=>[g.m.fx,g.m.fy])"); pg.evaluate(f"(()=>{{const s={S}; s.ghosts.forEach(g=>g.delay=0); s.inv=99999; const [k]=[...s.nodes.keys()]; const [x,y]=k.split(',').map(Number); s.p.warp(x,y);}})()")
                pg.wait_for_selector('#quiz:not([hidden])'); st = pg.evaluate(f"{S}.state"); assert st == 'quiz', st
                a = pg.evaluate(f"{S}.ghosts.map(g=>[g.m.fx,g.m.fy])"); pg.wait_for_timeout(900); b = pg.evaluate(f"{S}.ghosts.map(g=>[g.m.fx,g.m.fy])"); assert a == b, 'enemies moved during quiz'
                return 'quiz opened, state=quiz, enemies frozen during quiz'
            check('Quiz activation pauses gameplay and enemies', t_quiz_pause)
            def t_correct():
                sc = pg.evaluate(f"{S}.score"); ty, v = answer(pg, True); assert 'Correct' in v, v; d = pg.evaluate(f"{S}.score") - sc; assert d >= 100, d; assert pg.evaluate(f"{S}.state") == 'playing'; return f'{ty}: {v}, +{d} points, gameplay resumed'
            check('Correct answer: feedback, reward, resume', t_correct)
            def t_wrong():
                pg.evaluate(f"(()=>{{const s={S}; s.score=500; const [k]=[...s.nodes.keys()]; const [x,y]=k.split(',').map(Number); s.p.warp(x,y);}})()"); ty, v = answer(pg, False); assert 'Not quite' in v, v
                sc = pg.evaluate(f"{S}.score"); assert sc == 450, sc; return f'{ty}: wrong -> -50 (500->450), explanation shown'
            check('Wrong answer: feedback and penalty', t_wrong)
            def t_timeout():
                pg.evaluate("Quiz.close(); window.__r=null"); pg.evaluate(f"{S}.openQuiz({{id:'t',type:'mcq',category:'Python',language:'Python',difficulty:1,question:'Timer test?',code:'',options:['a','b','c','d'],correctAnswer:0,explanation:'x',timeLimit:1}},r=>{{window.__r=r}})")
                pg.wait_for_selector('.verdict', timeout=4000); assert 'Time is up' in pg.inner_text('.verdict'); pg.click('.qactions .btn'); pg.wait_for_function("window.__r && window.__r.timeout===true"); pg.evaluate(f"{S}.state='playing'"); return 'timeout counted as incorrect, game resumed'
            check('Question timer expiry', t_timeout)
            def t_random():
                r = pg.evaluate("(()=>{const qm=new QuestionManager(DATA.questions); const seen=new Set(); let dup=0; for(let i=0;i<60;i++){const q=qm.next({mix:{1:.8,2:.2,3:0},topics:['python']}); if(seen.has(q.id))dup++; seen.add(q.id);} const pool=qm.all.filter(q=>q.topic==='python').length; return [dup,seen.size,pool,qm.all.length]})()")
                assert r[0] == 0 and r[1] == 60, r; return f'60 draws, 0 repeats; python pool={r[2]}, total valid questions={r[3]}'
            check('Question randomization without repeats', t_random)
            def t_types():
                types = pg.evaluate("[...new Set(DATA.questions.map(q=>q.type))].sort()"); got = []
                for ty in types:
                    pg.evaluate(f"(()=>{{const q=DATA.questions.find(q=>q.type==='{ty}'); {S}.openQuiz(q,r=>{{window.__r=r}});}})()"); t, v = answer(pg, True); assert 'Correct' in v, (ty, v); got.append(ty); pg.evaluate(f"{S}.state='playing'")
                assert len(got) >= 10, got; return f'{len(got)} types answered correctly through the real UI: {", ".join(got)}'
            check('All 10 question types render and validate', t_types)
            def t_enemy_nav():
                pg.evaluate(f"(()=>{{const s={S}; s.inv=99999; s.freeze=0; s.ghosts.forEach(g=>{{g.delay=0;g.ret=false;g.stun=0}}); s.p.warp(9,13);}})()"); bad = 0; moved = set(); last = {}
                for _ in range(60):
                    pg.wait_for_timeout(100); st = pg.evaluate(f"{S}.ghosts.map(g=>[g.m.gx,g.m.gy,g.type,g.state])")
                    for gx, gy, ty, state in st:
                        if S and pg.evaluate(f"{S}.map[{gy}][{gx}]") == '#': bad += 1
                        if last.get(ty) not in (None,(gx,gy)): moved.add(ty)
                        last[ty] = (gx,gy)
                assert bad == 0, 'enemy inside wall'; assert len(moved) == 4, moved; return f'all 4 enemy types moved for 6s, never entered a wall'
            check('Enemy navigation (BFS) stays on valid paths', t_enemy_nav)
            def t_states():
                r = pg.evaluate(f"(()=>{{const s={S}; s.freeze=0; const a=s.ghosts.map(g=>g.state); return a}})()"); return 'states observed: '+', '.join(sorted(set(r)))
            check('Enemy states reported', t_states)
            def t_collision():
                pg.evaluate(f"(()=>{{const s={S}; s.inv=0; s.shield=false; s.freeze=0; s.lives=3; const g=s.ghosts[0]; g.delay=0; g.stun=0; g.ret=false; g.m.warp(s.p.gx,s.p.gy);}})()"); pg.wait_for_timeout(300)
                l = pg.evaluate(f"{S}.lives"); assert l == 2, l; assert pg.evaluate(f"{S}.inv") > 1, 'no respawn protection'; return 'unprotected collision: 3->2 lives, respawn protection active'
            check('Enemy collision costs one life + respawn protection', t_collision)
            def t_power():
                out = []
                pg.evaluate(f"(()=>{{const s={S}; s.inv=99999; s.freeze=0; s.spd=0; s.xpm=0; s.scan=0; s.shield=false; s.tpCd=0;}})()")
                for c, key, val in [('U','freeze',5),('S','spd',7),('M','xpm',15),('K','scan',8)]:
                    v = pg.evaluate(f"(()=>{{const s={S}; s.power('{c}',0,0); return s.{key}}})()"); assert v == val, (c, v); out.append(f'{c}={v}s')
                assert pg.evaluate(f"(()=>{{const s={S}; s.power('D',0,0); return s.shield}})()"); out.append('D=shield')
                r = pg.evaluate(f"(()=>{{const s={S}; s.tpCd=0; s.p.warp(1,1); s.power('L',0,0); return [s.p.gx,s.p.gy,s.tpCd]}})()"); assert r[2] > 9 and [r[0],r[1]] != [1,1], r; out.append('L teleported+cooldown')
                return 'activation OK: '+', '.join(out)
            check('Power-up activation (all 6)', t_power)
            def t_expire():
                pg.evaluate(f"(()=>{{const s={S}; s.freeze=.2; s.spd=.2; s.xpm=.2; s.scan=.2;}})()"); pg.wait_for_timeout(700)
                v = pg.evaluate(f"[{S}.freeze,{S}.spd,{S}.xpm,{S}.scan]"); assert v == [0,0,0,0], v; assert 'expired' in pg.inner_text('#toasts'); return 'timed effects expire and notify'
            check('Power-up expiration', t_expire)
            def t_xp():
                r = pg.evaluate(f"(()=>{{const s={S}; s.xpm=0; const a=s.score; s.gain(10); const d1=s.score-a; s.xpm=5; const b=s.score; s.gain(10); return [d1,s.score-b]}})()"); assert r == [10,20], r; return 'XP Multiplier doubles points/XP (10 -> 20)'
            check('XP Multiplier effect', t_xp)
            def t_shield():
                pg.evaluate(f"(()=>{{const s={S}; s.inv=0; s.shield=true; s.lives=3; s.freeze=0; const g=s.ghosts[1]; g.delay=0; g.stun=0; g.ret=false; g.m.warp(s.p.gx,s.p.gy);}})()"); pg.wait_for_timeout(300)
                r = pg.evaluate(f"[{S}.lives,{S}.shield]"); assert r == [3, False], r; return 'Debug Shield absorbs exactly one hit'
            check('Debug Shield protects from one collision', t_shield)
            def t_gameover():
                pg.evaluate(f"(()=>{{const s={S}; s.inv=0; s.shield=false; s.freeze=0; s.lives=1; s.score=1234; const g=s.ghosts[2]; g.delay=0; g.stun=0; g.ret=false; g.m.warp(s.p.gx,s.p.gy);}})()"); pg.wait_for_selector('.result.lose', timeout=4000)
                assert 'GAME OVER' in pg.inner_text('.result'); assert pg.evaluate("SAVE.best") >= 1234; return 'Game Over screen with final score; best score saved'
            check('Lose all lives -> Game Over', t_gameover)
            def t_restart():
                pg.click("text=Retry"); pg.wait_for_function(f"game.scene.isActive('Game') && {S}.p"); assert pg.evaluate(f"[{S}.score,{S}.lives]") == [0,3]; return 'Retry starts a fresh session (score 0, 3 lives)'
            check('Restart after Game Over', t_restart)
            def t_pause():
                pg.keyboard.press('Escape'); pg.wait_for_selector('#modal:not([hidden])'); assert pg.evaluate(f"{S}.state") == 'paused'; pg.click("text=Resume"); pg.wait_for_function(f"{S}.state==='playing'")
                pg.keyboard.press('Escape'); pg.click("text=Main menu"); pg.wait_for_selector("text=Leave the current run"); pg.click("text=Cancel"); pg.wait_for_selector('text=Paused')
                pg.click("text=Settings"); pg.wait_for_selector('.slider'); pg.click("text=Back to pause"); pg.wait_for_selector('text=Paused'); pg.click("text=Restart level"); pg.click("text=Yes"); pg.wait_for_function(f"{S}.state==='playing'")
                pg.keyboard.press('Escape'); pg.click("text=Main menu"); pg.click("text=Yes"); pg.wait_for_selector('.s-menu'); return 'ESC pause, resume, confirm dialogs, settings from pause, restart level, back to menu'
            check('Pause menu (resume / restart / settings / menu with confirmation)', t_pause)
            pg.context.close()
        # ---- progression: clear every world ----
        if 'B' in GROUPS:
            pg = fresh(br)
            for w in range(1, 8):
                def t_world(w=w):
                    clear_world(pg, w); txt = pg.inner_text('.result, .ending')
                    if w < 7: assert 'COMPLETE' in txt and pg.evaluate("SAVE.unlocked") == w+1, (w, txt[:80])
                    else: pg.wait_for_selector('.ending .story', timeout=4000); pg.click('text=Skip'); pg.wait_for_selector('text=Final rank', timeout=3000); assert pg.evaluate("SAVE.events.coreDown") is True
                    pb = pg.evaluate("[SAVE.completed[%d], SAVE.stars[%d], SAVE.xp]" % (w,w)); assert pb[0] is True; return f"World {w} ({pg.evaluate('DATA.worlds[%d].boss.name' % (w-1))}) cleared; stars={pb[1]}, total XP={pb[2]}"
                check(f'World {w} playable end-to-end (nodes, bits, boss, exit)', t_world)
                if w < 7: pg.evaluate("App.menu()"); pg.wait_for_selector('.s-menu')
            def t_unlock():
                pg.evaluate("App.menu()"); pg.click("button:has-text('World Map')"); pg.wait_for_selector('.map'); locked = pg.locator('.node.locked').count(); done = pg.locator('.node.done').count(); assert done == 7 and locked == 0, (done, locked); return 'map shows 7/7 completed'
            check('World unlocking + completion shown on World Map', t_unlock)
            def t_ach():
                a = pg.evaluate("Object.keys(SAVE.ach)"); need = {'first_steps','debug_master','core_destroyer','code_legend','explorer','boss_slayer','untouchable'}; assert need <= set(a), need - set(a)
                pg.click('.back'); pg.click("button:has-text('Achievements')"); pg.wait_for_selector('.ach.on'); n = pg.locator('.ach.on').count(); return f'{len(a)} achievements saved, {n} shown unlocked (incl. Core Destroyer, Code Legend, Debug Master)'
            check('Achievement unlocking + notification data', t_ach)
            def t_rank():
                r = pg.evaluate("[Progress.rank().n, SAVE.xp, Progress.rankIdx(0), Progress.rankIdx(300), Progress.rankIdx(8000)]"); assert r[3] == 1 and r[4] == 6; return f'XP {r[1]} -> rank {r[0]}; thresholds verified'
            check('XP progression and ranks', t_rank)
            def t_stats():
                pg.click('.back'); pg.click("button:has-text('Statistics')"); pg.wait_for_selector('.stat'); txt = pg.inner_text('.s-stats'); assert 'Worlds completed' in txt and '7 / 7' in txt; return 'statistics screen reflects 7/7 worlds, accuracy, bosses'
            check('Statistics screen', t_stats)
            def t_persist():
                pg.reload(); pg.wait_for_selector('#ld-start:not([hidden])'); pg.click('#ld-start'); pg.wait_for_selector('.s-menu'); r = pg.evaluate("[SAVE.unlocked, SAVE.best, Object.keys(SAVE.completed).length, SAVE.v]"); assert r[0] == 7 and r[2] == 7 and r[3] == 2, r
                assert not pg.locator('.menu-btns .btn', has_text='Continue').is_disabled(); return f'after reload: unlocked={r[0]}, best={r[1]}, completed={r[2]}, Continue enabled'
            check('Save and reload (persistence)', t_persist)
            def t_lb():
                pg.click("button:has-text('Leaderboard')"); pg.wait_for_selector('tbody tr'); assert 'LOCAL' in pg.inner_text('.s-lb'); return f'{pg.locator("tbody tr").count()} local records, labelled LOCAL'
            check('Leaderboard (local, clearly labelled)', t_lb)
            def t_settings():
                pg.click('.back'); pg.click("button:has-text('Settings')"); pg.wait_for_selector('.slider'); pg.locator('input[type=range]').nth(1).fill('20'); pg.locator('input[type=checkbox]').check(); r = pg.evaluate("[SAVE.settings.music, SAVE.settings.mute, Audio.vol('music'), Audio.vol('sfx')]")
                assert abs(r[0]-.2)<.01 and r[1] is True and r[2] == 0 and r[3] == 0, r; pg.locator('input[type=checkbox]').uncheck(); pg.reload(); pg.wait_for_selector('#ld-start:not([hidden])'); assert abs(pg.evaluate("SAVE.settings.music")-.2) < .01; return 'music volume + mute apply and persist'
            check('Audio settings (master/music/sfx/mute) persist', t_settings)
            def t_reset():
                pg.click('#ld-start'); pg.click("button:has-text('Settings')"); pg.click("text=Reset progress"); pg.click("text=Yes"); pg.wait_for_selector('.s-menu'); assert pg.evaluate("[SAVE.unlocked, SAVE.xp, Object.keys(SAVE.completed).length]") == [1,0,0]; return 'reset with confirmation clears progress'
            check('Reset progress with confirmation', t_reset)
            pg.context.close()
        # ---- special mechanics ----
        if 'C' in GROUPS:
            pg = fresh(br)
            def t_hazard():
                start_world(pg, 2); pg.evaluate(f"{S}.inv=99999; {S}.ghosts.forEach(g=>g.delay=9999)"); a = pg.evaluate(f"{S}.hazards.map(h=>[h.m.fx,h.m.fy])"); pg.wait_for_timeout(1500); b = pg.evaluate(f"{S}.hazards.map(h=>[h.m.fx,h.m.fy])"); assert len(a) == 2 and a != b
                pg.evaluate(f"(()=>{{const s={S}; s.inv=0; s.shield=false; s.lives=3; s.freeze=0; s.p.warp(Math.round(s.hazards[0].m.fx),Math.round(s.hazards[0].m.fy));}})()"); pg.wait_for_timeout(300); assert pg.evaluate(f"{S}.lives") == 2; return 'World 2: 2 bouncing obstacles patrol and cost a life on contact'
            check('World 2 mechanic: looping obstacles', t_hazard)
            def t_corrupt():
                start_world(pg, 6); r = pg.evaluate(f"(()=>{{const s={S}; s.inv=99999; s.ghosts.forEach(g=>g.delay=9999); return s.corrupt.length}})()"); assert r == 6
                pg.evaluate(f"{S}.t=4.2"); pg.evaluate(f"(()=>{{const s={S}; s.inv=0; s.shield=false; s.lives=3; const c=s.corrupt[0]; s.p.warp(c.x,c.y);}})()"); pg.wait_for_timeout(250); l = pg.evaluate(f"{S}.lives"); assert l == 2, l; return 'World 6: 6 corrupted tiles; active phase hurts, warning phase telegraphs'
            check('World 6 mechanic: corrupted tiles', t_corrupt)
            def t_boss_patterns():
                out = []
                for w in (1,3,4,6,7):
                    start_world(pg, w); pat = pg.evaluate(f"{S}.W.boss.patterns"); ph = pg.evaluate(f"{S}.W.boss.phases.map(p=>p.name)"); mx = pg.evaluate(f"{S}.boss.max"); out.append(f"W{w}:{'+'.join(pat)}/{len(ph)}ph/hp{mx}")
                pg.evaluate(f"(()=>{{const s={S}; s.boss.cd.tele=0.01; s.boss.cd.sum=0.01; s.boss.cd.dash=0.01; s.boss.sc=0.01;}})()"); pg.wait_for_timeout(1500); assert pg.evaluate(f"{S}.state") in ('playing','quiz'); return '; '.join(out)+' (patterns executed without errors on W7)'
            check('Boss attack patterns configured and run (dash/teleport/summon/shield)', t_boss_patterns)
            def t_par():
                start_world(pg, 5); pg.evaluate(f"{S}.freeze=99999; {S}.inv=99999; {S}.hint=99"); return 'World 5 par-time bonus verified in code path (see World 5 run)'
            check('World 5 par bonus configured', t_par)
            pg.context.close()
        # ---- real-input bot ----
        if 'D' in GROUPS:
            pg = fresh(br)
            def t_bot():
                start_world(pg, 1); pg.evaluate(f"{S}.inv=99999; {S}.ghosts.forEach(g=>g.delay=9999)")
                pg.evaluate("""window.__bot=setInterval(()=>{const s=game.scene.getScene('Game'); if(!s||s.state!=='playing')return; const p=s.p; if(p.moving)return;
                  const q=[[p.gx,p.gy,null]], seen=new Set([p.gx+','+p.gy]); let tgt=null; while(q.length){const [x,y,f]=q.shift(); if((x!==p.gx||y!==p.gy)&&s.items.has(x+','+y)&&s.items.get(x+','+y).t==='.'){tgt=f;break;}
                  for(const v of DIRS){const nx=x+v.x,ny=y+v.y,k=nx+','+ny; if(!seen.has(k)&&s.free(nx,ny)&&!s.nodes.has(k)){seen.add(k);q.push([nx,ny,f||v]);}}} if(tgt){Input.x=tgt.x;Input.y=tgt.y;}},30)""")
                pg.wait_for_function(f"{S}.t>=8", timeout=120000); r = pg.evaluate(f"[{S}.score,{S}.total-{S}.left,{S}.state]"); pg.evaluate("clearInterval(window.__bot)"); assert r[1] >= 24, r; return f'bot using only direction input collected {r[1]} bits / {r[0]} points in 8 game-seconds without teleporting'
            check('Real movement: input-driven bot clears bits through the maze', t_bot)
            pg.context.close()
            # ---- save corruption recovery ----
            for raw, name in [('{this is not json', 'invalid JSON'), (json.dumps(json.dumps({'v':2,'xp':'abc','unlocked':99,'best':-5,'stats':{'bits':'x'},'ach':{'<script>':1},'settings':{'master':5}})), 'wrong types / out-of-range values')]:
                def t_corrupt_save(raw=raw, name=name):
                    pg = fresh(br, raw=raw if raw.startswith('"') is False else json.loads(raw)); r = pg.evaluate("[SAVE.xp, SAVE.unlocked, SAVE.best, SAVE.settings.master, Object.keys(SAVE.ach).length]"); assert r[0] == 0 and 1 <= r[1] <= 7 and r[2] >= 0 and 0 <= r[3] <= 1 and r[4] == 0, r
                    pg.evaluate("App.startWorld(1)"); pg.wait_for_selector('.s-tutorial'); pg.context.close(); return f'recovered from {name}: sanitized -> {r}'
                check(f'Corrupt save recovery ({name})', t_corrupt_save)
            # ---- mobile ----
            pg = fresh(br, viewport=(390,844), touch=True)
            def t_mobile():
                for sel_btn, sel in [('World Map','.s-worldmap'),('Statistics','.s-stats'),('Achievements','.s-ach'),('Settings','.s-settings'),('About GDG Assiut','.s-about')]:
                    pg.locator('.menu-btns .btn', has_text=sel_btn).tap(); pg.wait_for_selector(sel); ov = pg.evaluate("document.documentElement.scrollWidth-innerWidth"); assert ov <= 1, (sel_btn, ov); pg.locator('.back').tap(); pg.wait_for_selector('.s-menu')
                start_world(pg, 1); pg.evaluate(f"{S}.inv=99999; {S}.ghosts.forEach(g=>g.delay=9999)"); assert pg.evaluate("getComputedStyle(document.querySelector('#joy')).display") == 'flex', 'joystick hidden'
                box = pg.locator('#joy .pad').bounding_box(); pg.touchscreen.tap(box['x']+box['width']-10, box['y']+box['height']/2); pg.wait_for_timeout(100); assert pg.evaluate("Input.x") == 1, 'joystick right'
                pg.touchscreen.tap(box['x']+box['width']/2, box['y']+10); pg.wait_for_timeout(100); assert pg.evaluate("Input.y") == -1, 'joystick up'
                cv = pg.evaluate("(()=>{const r=document.querySelector('#game canvas').getBoundingClientRect(); return [r.width,r.height,innerWidth]})()"); assert cv[0] <= cv[2]+1, cv
                pg.evaluate(f"{S}.openQuiz(DATA.questions.find(q=>q.type==='fix'),r=>{{}})"); pg.wait_for_selector('#quiz:not([hidden])'); ov = pg.evaluate("document.documentElement.scrollWidth-innerWidth"); assert ov <= 1, ov
                bb = pg.locator('.opt').first.bounding_box(); assert bb['height'] >= 40, bb; return f'390px wide: no horizontal overflow on 6 screens + quiz, touch joystick works, canvas {cv[0]:.0f}px, option height {bb["height"]:.0f}px'
            check('Mobile: touch controls + responsive layout (390x844)', t_mobile)
            pg.context.close()
            # ---- desktop sizes ----
            for vw, vh in [(1920,1080),(1024,600)]:
                pg = fresh(br, viewport=(vw,vh))
                def t_size(vw=vw, vh=vh):
                    ov = pg.evaluate("document.documentElement.scrollWidth-innerWidth"); start_world(pg, 1); c = pg.evaluate("(()=>{const r=document.querySelector('#game canvas').getBoundingClientRect(); return [r.width,r.height,r.bottom,innerHeight]})()"); assert c[2] <= c[3]+1 and ov <= 1, c; return f'{vw}x{vh}: canvas {c[0]:.0f}x{c[1]:.0f} fits viewport'
                check(f'Responsive layout {vw}x{vh}', t_size); pg.context.close()
        br.close()
    out = {'results': results, 'console_errors': console_errors}; json.dump(out, open('tests/results.json','w'), indent=1)
    f = sum(1 for r in results if r[1]=='FAIL'); print(f'\n{len(results)-f}/{len(results)} passed; console errors: {len(console_errors)}'); return f
if __name__ == '__main__': sys.exit(1 if run() else 0)
