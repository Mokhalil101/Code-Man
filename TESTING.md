# CODE MAN — Testing report

Tests run in headless Chromium (Playwright) against the real game served by a local static server (`tests/run_tests.py`).
The table below is generated from `tests/results.json`: the full run (all groups) plus a re-run of the group containing the last two fixes (movement bot + responsive layout).

**48 / 48 automated checks passed.** Browser console errors during the whole run: **0**

| | Check | Result / what was observed |
|---|---|---|
| ✅ | Main menu navigation (all buttons work) | 9 buttons, 7 sub-screens open and return; GDG tag present |
| ✅ | Continue disabled when no save exists | Continue disabled with no progress |
| ✅ | New game via interactive tutorial | 9 tutorial steps; skippable; starts World 1 |
| ✅ | New game initialization | World 1, 3 lives, score 0 |
| ✅ | Player movement (keyboard) + collecting while moving | moved [10, 11]->[8, 11], score 30 from real keyboard input |
| ✅ | Maze wall collision | moving up into a wall leaves the player in place |
| ✅ | Collectible (Code Bit) = +10 and removal | +10 points, counter -1, item removed |
| ✅ | Quiz activation pauses gameplay and enemies | quiz opened, state=quiz, enemies frozen during quiz |
| ✅ | Correct answer: feedback, reward, resume | output: ✔ Correct!, +150 points, gameplay resumed |
| ✅ | Wrong answer: feedback and penalty | mcq: wrong -> -50 (500->450), explanation shown |
| ✅ | Question timer expiry | timeout counted as incorrect, game resumed |
| ✅ | Question randomization without repeats | 60 draws, 0 repeats; python pool=75, total valid questions=611 |
| ✅ | All 10 question types render and validate | 10 types answered correctly through the real UI: algorithm, arrange, bug, complexity, conceptual, fill, fix, logic, mcq, output |
| ✅ | Enemy navigation (BFS) stays on valid paths | all 4 enemy types moved for 6s, never entered a wall |
| ✅ | Enemy states reported | states observed: chase |
| ✅ | Enemy collision costs one life + respawn protection | unprotected collision: 3->2 lives, respawn protection active |
| ✅ | Power-up activation (all 6) | activation OK: U=5s, S=7s, M=15s, K=8s, D=shield, L teleported+cooldown |
| ✅ | Power-up expiration | timed effects expire and notify |
| ✅ | XP Multiplier effect | XP Multiplier doubles points/XP (10 -> 20) |
| ✅ | Debug Shield protects from one collision | Debug Shield absorbs exactly one hit |
| ✅ | Lose all lives -> Game Over | Game Over screen with final score; best score saved |
| ✅ | Restart after Game Over | Retry starts a fresh session (score 0, 3 lives) |
| ✅ | Pause menu (resume / restart / settings / menu with confirmation) | ESC pause, resume, confirm dialogs, settings from pause, restart level, back to menu |
| ✅ | World 1 playable end-to-end (nodes, bits, boss, exit) | World 1 (The Indentation Monster) cleared; stars=3, total XP=1236 |
| ✅ | World 2 playable end-to-end (nodes, bits, boss, exit) | World 2 (Infinite Loop) cleared; stars=3, total XP=2254 |
| ✅ | World 3 playable end-to-end (nodes, bits, boss, exit) | World 3 (The Memory Eater) cleared; stars=3, total XP=3424 |
| ✅ | World 4 playable end-to-end (nodes, bits, boss, exit) | World 4 (The Class Destroyer) cleared; stars=3, total XP=4610 |
| ✅ | World 5 playable end-to-end (nodes, bits, boss, exit) | World 5 (The Complexity Beast) cleared; stars=3, total XP=5603 |
| ✅ | World 6 playable end-to-end (nodes, bits, boss, exit) | World 6 (The Runtime Reaper) cleared; stars=3, total XP=6846 |
| ✅ | World 7 playable end-to-end (nodes, bits, boss, exit) | World 7 (CORE VIRUS) cleared; stars=3, total XP=8184 |
| ✅ | World unlocking + completion shown on World Map | map shows 7/7 completed |
| ✅ | Achievement unlocking + notification data | 13 achievements saved, 13 shown unlocked (incl. Core Destroyer, Code Legend, Debug Master) |
| ✅ | XP progression and ranks | XP 8184 -> rank Code Legend; thresholds verified |
| ✅ | Statistics screen | statistics screen reflects 7/7 worlds, accuracy, bosses |
| ✅ | Save and reload (persistence) | after reload: unlocked=7, best=6780, completed=7, Continue enabled |
| ✅ | Leaderboard (local, clearly labelled) | 7 local records, labelled LOCAL |
| ✅ | Audio settings (master/music/sfx/mute) persist | music volume + mute apply and persist |
| ✅ | Reset progress with confirmation | reset with confirmation clears progress |
| ✅ | World 2 mechanic: looping obstacles | World 2: 2 bouncing obstacles patrol and cost a life on contact |
| ✅ | World 6 mechanic: corrupted tiles | World 6: 6 corrupted tiles; active phase hurts, warning phase telegraphs |
| ✅ | Boss attack patterns configured and run (dash/teleport/summon/shield) | W1:dash/1ph/hp3; W3:teleport/1ph/hp4; W4:shield/1ph/hp4; W6:teleport+summon/1ph/hp5; W7:dash+teleport+summon+shield/5ph/hp5 (patterns executed without errors on W7) |
| ✅ | World 5 par bonus configured | World 5 par-time bonus verified in code path (see World 5 run) |
| ✅ | Real movement: input-driven bot clears bits through the maze | bot using only direction input collected 27 bits / 420 points in 8 game-seconds without teleporting |
| ✅ | Corrupt save recovery (invalid JSON) | recovered from invalid JSON: sanitized -> [0, 1, 0, 0.8, 0] |
| ✅ | Corrupt save recovery (wrong types / out-of-range values) | recovered from wrong types / out-of-range values: sanitized -> [0, 7, 0, 1, 0] |
| ✅ | Mobile: touch controls + responsive layout (390x844) | 390px wide: no horizontal overflow on 6 screens + quiz, touch joystick works, canvas 390px, option height 60px |
| ✅ | Responsive layout 1920x1080 | 1920x1080: canvas 1220x963 fits viewport |
| ✅ | Responsive layout 1024x600 | 1024x600: canvas 612x483 fits viewport |

## How the tests work (what "passed" means)
* Real UI is driven by real clicks, key presses and touch taps: menus, tutorial, pause, quiz answering (all 10 question types), settings, reset, reload.
* **World completion tests use helper shortcuts**: the live scene is teleported onto each quiz node / bit / the boss / the exit, while the quizzes and boss questions are answered through the real quiz UI.
  This proves every world is *completable* and every boss *defeatable* in the code, **not** that a human can beat it comfortably.
* One test (`Real movement bot`) plays with direction input only, no teleporting, and eats bits through the maze.
* Enemy AI is checked for staying on valid tiles and moving; fairness/difficulty balance is **not** validated by play-testing.

## Bugs found by testing and fixed
1. Quick **Esc** taps were missed (keyboard polling) → keyboard handling moved to DOM events (also arrows / Space).
2. On large screens the canvas overflowed the viewport after the HUD appeared → ResizeObserver refits the canvas.
3. Question-bank bug: an infinite-loop answer option could hang the generator → verification now runs in a sandbox with timeouts.
4. Test-suite bugs (custom quizzes not restoring state, bot walking into quiz nodes, bot test tied to frame rate) were fixed in the tests, not the game.

## Known limitations / not verified
* **Only Chromium was tested.** Safari, Firefox and real phones/tablets were not (touch was emulated).
* **Frame rate**: headless software rendering ran at ~14–28 FPS (game time slows down below 20 FPS). The 60 FPS target was **not** measured on real hardware.
* **Audio** playback cannot be heard in headless mode; only volume/mute logic and error-free playback calls were tested. Music/SFX quality is unreviewed.
* **GitHub Pages**: workflow file is included but was **not executed**; only a local static server was tested.
* **Questions**: answers for output / fill / fix / arrange questions were verified by executing the code (Python, Node.js, g++, Java).
  The ~120 conceptual questions (including Google developer-tech facts) were written from general knowledge and not independently audited — please review before public use.
* **Game design simplifications**: boss "arenas" are the boss chamber inside the maze (no separate boss scene); boss victory is an effect + banner (no long cutscene except the Core Virus ending);
  the tutorial is a guided step-by-step explanation plus in-game hints, not a playable tutorial; progress is saved at world completion and on stats events, **not mid-level**.
* No service worker: the game works offline only while the browser keeps the files cached.
* The official GDG Assiut logo is not included (placeholder switch in `src/config.js`); credits section has a placeholder for your team.
