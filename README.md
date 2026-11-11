# CODE MAN — Eat Code. Escape Bugs. Master Programming.
### Powered by GDG Assiut

An educational arcade game inspired by classic maze-chase gameplay, rebuilt around programming. You are a developer bot exploring
seven programming worlds: collect Code Bits, escape intelligent Bug enemies, answer real programming questions, grab power-ups,
defeat a boss in every world, and finally shut down the **Core Virus**.

Static web game — **Phaser 3 + vanilla JavaScript/CSS/JSON**, no backend, no build step, deployable on **GitHub Pages**.
*Community-inspired project for GDG Assiut; it is not an official Google product.*

---
## Quick start
Browsers block `fetch()` of JSON from `file://`, so serve the folder with any static server:

```bash
cd code-man
python3 -m http.server 8000        # or:  npm start     /     npx serve .
# open http://localhost:8000
```
Phaser is bundled in `lib/`, the font and all art/audio are in `assets/` → the game works **offline** once loaded.

## Deploy to GitHub Pages
1. Push this folder to a GitHub repository (branch `main`).
2. **Settings → Pages → Source: GitHub Actions** — the included `.github/workflows/pages.yml` publishes the game on every push.
   (Or choose *Deploy from a branch → main / root*; the game is plain static files.)
3. Open `https://<user>.github.io/<repo>/`.

## Controls
| Action | Keyboard | Touch |
|---|---|---|
| Move | Arrow keys / WASD | Virtual joystick or swipe on the maze |
| Dash (8 s cooldown) | Space | DASH button |
| Pause | Esc / P | ❚❚ button |
| Answer quiz | click, or keys 1–4 then Enter | tap, then Submit |

## What is inside
* **7 worlds**, each with its own maze, colours, music, enemies speed, mechanic and **boss**

| # | World | Topics | Boss | Special mechanic |
|---|---|---|---|---|
| 1 | Python City | variables, types, operators, strings, lists, functions | The Indentation Monster | tutorial hints, gentle enemies |
| 2 | Loop Valley | if/else, for/while, break/continue, nested loops | Infinite Loop | bouncing loop obstacles |
| 3 | Data Dungeon | arrays, lists, stacks, queues, hash maps, sets | The Memory Eater | hidden secret chambers (use the Code Scanner) |
| 4 | OOP Fortress | classes, inheritance, polymorphism, abstraction | The Class Destroyer | extra Debug Shields, shielded boss |
| 5 | Algorithm Arena | searching, sorting, recursion, Big O | The Complexity Beast | par-time speed bonus |
| 6 | Debugging Lab | errors, exceptions, tracing, fixing | The Runtime Reaper | corrupted tiles that flicker then hurt |
| 7 | Cyber Core | mixed advanced topics | **CORE VIRUS** (5 phases) | everything combined + cinematic ending |

* **4 enemy AIs** on BFS pathfinding — *Syntax* chases the shortest path, *Logic* predicts your direction, *Runtime* takes the junctions that block your escape,
  *Memory* patrols your remembered trail and chases when close. States: chase, scatter, patrol, frightened (frozen), return (eyes run home), stunned.
* **Bosses** with health bars and attack patterns — *dash*, *teleport*, *summon*, *shield* — each with a visible warning. Touch the boss to face a question: correct = damage, wrong = lose a life.
  The Core Virus fight runs through 5 phases: Syntax Corruption → Logic Infection → Memory Collapse → Algorithm Overload → Core Shutdown.
* **6 power-ups**: Power Compiler (freeze/neutralize 5 s), Speed Boost (7 s), Debug Shield (1 hit), XP Multiplier (×2 for 15 s), Code Scanner (reveals secrets 8 s), Teleport Chip (safe teleport, 10 s cooldown) + Space dash.
* **Collectibles**: Code Bits (+10), Bonus Chips (+250), XP Orbs, hidden Secret stars (+500).
* **611 questions** in `data/questions/` — Python, C++, Java, JavaScript, data structures, algorithms, debugging, CS fundamentals and **Google developer tech / dev-community topics** (Flutter, Firebase, Android, TensorFlow, Cloud, Git, web…),
  with GDG-flavoured code (members, attendees, DevFest, Study Jam…) and GDG Assiut lead-ins. 10 types: multiple choice, predict output, find the bug, fix the code, fill the blank,
  arrange code blocks, logic, conceptual, algorithm selection, time complexity. Syntax-highlighted code, countdown timer, explanations after every answer.
  **Every output/fill/fix/arrange answer was verified by actually running the code** (Python, Node.js, g++, Java) by `tools/make_questions.py`.
* **Progress**: score, XP, 7 ranks (Beginner Coder → Code Legend), 21 achievements, full statistics, local leaderboard (clearly labelled *local* — no backend), world map with stars, versioned & validated LocalStorage save with corruption recovery.
* **Audio**: 11 chiptune music tracks (menu, 7 worlds, boss, victory, game over) + 16 sound effects; master / music / SFX volume and mute.
* **GDG Assiut identity**: Google four-colour palette (#4285F4 #EA4335 #FBBC04 #34A853) on deep navy, glass panels, neon pixel art, "Powered by GDG Assiut" badge, About section.
  No logo is invented: to show the official logo, put it at `assets/icons/gdg-assiut-logo.png` and set `CONFIG.gdgLogo = true` in `src/config.js`.

## Project structure
```
index.html            DOM shell (HUD, screens, quiz overlay, loader)
styles/               main.css · game.css · quiz.css · responsive.css
src/config.js         constants, palette, ranks, power-up table
src/systems/          Save · AudioManager · Pathfinding (BFS) · QuestionManager · Progress (XP, ranks, achievements, leaderboard)
src/entities/Mover.js grid mover used by player, bugs, bosses, hazards
src/ui/               Quiz (10 question UIs + highlighter) · UI (HUD, menus, world map, tutorial, results, ending)
src/scenes/           PreloadScene · GameScene (maze, AI, bosses, power-ups, scoring)
src/main.js           app controller (boot, flow, input, pause)
data/levels/world1-7.json · data/questions/*.json · data/achievements.json
assets/               sprites (PNG) · audio (WAV) · fonts
tools/                make_assets.py · make_data.py · make_questions.py · make_report.py   (regenerate content)
tests/run_tests.py    browser test-suite (Playwright)
```
## Customising
* **Add questions**: append objects to a file in `data/questions/` (fields: `id, category, language, difficulty 1-3, topic, type, question, code, options, correctAnswer, explanation, points, timeLimit`;
  `arrange` questions use `lines` instead of `options`). Invalid questions are skipped at load time, no code change needed.
* **Tune a world**: edit `data/levels/worldN.json` (`difficultyMix`, `ghostSpeed`, `cycle`, boss `hp/patterns/phases`, maze characters:
  `# wall · . bit · B chip · o orb · T secret · Q quiz · U S D M K L power-ups · P start · E exit · G enemy · X boss · O hazard · C corrupted tile`).
* **Regenerate content**: `python3 tools/make_assets.py` (art+audio, needs Pillow+numpy), `python3 tools/make_data.py`, `python3 tools/make_questions.py` (needs node, g++, java for verification).
* **Run the tests**: `python3 -m http.server 8123 &` then `pip install playwright && playwright install chromium && python3 tests/run_tests.py`. See `TESTING.md`.

## Scoring
Code Bit 10 · correct answer 100 (+50 fast, +50 hard) · wrong answer −50 · Bonus Chip 250 · Secret 500 · squashed bug 200 · boss hit 300 · boss defeat 1000 · world 500 (+300 no life lost, +300 World-5 par time).
XP Multiplier doubles both points and XP. Stars: ★ complete · ★★ ≥70 % answers correct · ★★★ also no life lost.

## Licence & credits
Code, pixel art and chiptune audio are original and generated by the scripts in `tools/`. Phaser 3 (MIT). Font *Press Start 2P* (SIL Open Font License). No Pac-Man assets are used.
Developer / community credits: add your team in `src/ui/UI.js → about()`.
