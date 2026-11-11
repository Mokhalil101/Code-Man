# Turns tests/results.json (written by tests/run_tests.py) into the results table inside TESTING.md
import json
r = json.load(open('tests/results.json')); res = r['results']; ok = sum(1 for x in res if x[1] == 'PASS')
rows = '\n'.join(f"| {'✅' if s=='PASS' else '❌'} | {n} | {note.replace('|','/')} |" for n, s, note, _ in res)
print(f"**{ok} / {len(res)} automated checks passed.** Browser console errors during the whole run: **{len(r['console_errors'])}**"+(f" ({'; '.join(set(r['console_errors']))})" if r['console_errors'] else '')+"\n\n| | Check | Result / what was observed |\n|---|---|---|\n"+rows)
