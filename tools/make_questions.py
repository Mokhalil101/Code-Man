# Builds data/questions/*.json (python, loops, data-structures, oop, algorithms, debugging, advanced).
# Every output / fill / fix / arrange answer is VERIFIED by actually running the code (Python, Node.js, g++, Java).
import json, random, io, contextlib, subprocess, tempfile, os, re, sys, itertools
R = random.Random(2026)
Q = {t: [] for t in ['python','loops','data','oop','algo','debug','advanced']}
seen = set(); cnt = {}
PFX = dict(python='GPY',loops='GLP',data='GDS',oop='GOP',algo='GAL',debug='GDB',advanced='GAD')
ERR = re.compile(r'^[A-Za-z]*(Error|Exception|Exit)$')
# ---------------- runners ----------------
PYRUNNER = r"""
import sys, json, io, signal, contextlib, resource
resource.setrlimit(resource.RLIMIT_AS, (1<<30, 1<<30))
class Cap(io.StringIO):
    def write(self, s):
        if self.tell() > 20000: raise OSError('OutputLimit')
        return super().write(s)
def alarm(*a): raise TimeoutError('t')
signal.signal(signal.SIGALRM, alarm)
res = []
for b in json.load(sys.stdin):
    buf = Cap()
    try:
        signal.alarm(2)
        with contextlib.redirect_stdout(buf): exec(b, {'__name__': '__main__'})
        signal.alarm(0); res.append(buf.getvalue().strip())
    except BaseException as e:
        signal.alarm(0); res.append(type(e).__name__)
sys.stdout.write(json.dumps(res))
"""
def run_py(bodies):
    r = subprocess.run([sys.executable,'-c',PYRUNNER], input=json.dumps(bodies), capture_output=True, text=True, timeout=300); return json.loads(r.stdout)
def run_js(bodies):
    js = "const U=require('util');const B=JSON.parse(require('fs').readFileSync(0,'utf8'));const out=B.map(b=>{const L=[];const o=console.log;console.log=(...a)=>L.push(a.map(x=>typeof x==='string'?x:U.inspect(x)).join(' '));try{new Function(b)()}catch(e){L.push(e.name)}console.log=o;return L.join('\\n')});process.stdout.write(JSON.stringify(out))"
    r = subprocess.run(['node','-e',js], input=json.dumps(bodies), capture_output=True, text=True, timeout=60); return [x.strip() for x in json.loads(r.stdout)]
def _split(txt, n): p = [x.strip() for x in txt.split('#@#')]; return p[:n] if len(p) > n else None
def run_cpp(bodies):
    def go(bs):
        src = "#include <bits/stdc++.h>\nusing namespace std;\n" + "".join(f"void f{i}(){{\n{b}\n}}\n" for i,b in enumerate(bs)) + "int main(){\n" + "".join(f'f{i}(); cout<<"\\n#@#\\n";\n' for i in range(len(bs))) + "}\n"
        with tempfile.TemporaryDirectory() as d:
            open(d+'/a.cpp','w').write(src)
            if subprocess.run(['g++','-std=c++17','-w','-O0',d+'/a.cpp','-o',d+'/a'],capture_output=True).returncode: return None
            r = subprocess.run([d+'/a'],capture_output=True,text=True,timeout=20); return _split(r.stdout,len(bs))
    res = go(bodies)
    return res if res else [ (go([b]) or [None])[0] for b in bodies ]
def run_java(bodies):
    def go(bs):
        src = "import java.util.*;\npublic class Main {\n" + "".join(f"static void f{i}() {{\n{b}\n}}\n" for i,b in enumerate(bs)) + "public static void main(String[] a){\n" + "".join(f'f{i}(); System.out.println("#@#");\n' for i in range(len(bs))) + "}}\n"
        with tempfile.TemporaryDirectory() as d:
            open(d+'/Main.java','w').write(src)
            r = subprocess.run(['java',d+'/Main.java'],capture_output=True,text=True,timeout=90)
            return _split(r.stdout,len(bs)) if r.returncode==0 else None
    res = go(bodies)
    return res if res else [ (go([b]) or [None])[0] for b in bodies ]
RUN = {'Python':run_py,'JavaScript':run_js,'C++':run_cpp,'Java':run_java}
# ---------------- builders ----------------
def mk(topic, lang, diff, typ, cat, question, code, correct, wrongs, expl, lines=None):
    key = (lang, code, question)
    if key in seen: return False
    if typ == 'arrange':
        q = dict(options=None, correctAnswer=None, lines=lines)
    else:
        opts = [correct]
        for w in wrongs:
            if w != correct and w not in opts: opts.append(w)
        try:
            c = int(correct)
            for w in [c+1,c-1,c+2,c*2,c-2,c+3,c+10,c+5]:
                if len(opts) >= 4: break
                if str(w) not in opts: opts.append(str(w))
        except ValueError: pass
        for w in ['Error','None','0','Nothing is printed']:
            if len(opts) >= 4: break
            if w not in opts: opts.append(w)
        opts = opts[:4]; assert len(opts) == 4, (question, opts)
        R.shuffle(opts); q = dict(options=opts, correctAnswer=opts.index(correct))
    seen.add(key); cnt[topic] = cnt.get(topic,0)+1
    q.update(id=f"{PFX[topic]}_{cnt[topic]:03d}", category=cat, language=lang, difficulty=diff, topic=topic, type=typ, question=question, code=code,
             explanation=expl, points=100+25*(diff-1), timeLimit=({1:15,2:20,3:25}[diff]+(8 if '\n' in code else 0)+(20 if typ=='arrange' else 0)))
    Q[topic].append(q); return True
def family(topic, lang, diff, cat, bodies, k, question='What is the output?', typ='output', expl='The program prints {o}.', pool=None):
    bodies = list(dict.fromkeys(bodies)); outs = RUN[lang](bodies)
    items = [(b,o) for b,o in zip(bodies,outs) if o not in (None,'') and (pool or not ERR.match(o))]; R.shuffle(items); made = 0
    for b,o in items:
        if made >= k: break
        wr = list(dict.fromkeys([x for x in (pool or [y for _,y in items]) if x != o])); R.shuffle(wr)
        if mk(topic, lang, diff, typ, cat, question, b, o, wr[:3], expl.format(o=o)): made += 1
def hand(topic, lang, diff, typ, cat, question, code, opts, expl): mk(topic, lang, diff, typ, cat, question, code, opts[0], opts[1:], expl)
def fill(topic, lang, diff, cat, tpl, correct, wrongs, expect, expl, question=None):
    cands = [correct]+wrongs; outs = RUN[lang]([tpl.replace('____',c) for c in cands])
    assert outs[0] == expect and all(o != expect for o in outs[1:]), ('fill not unique', tpl, outs)
    mk(topic, lang, diff, 'fill', cat, question or f'Fill in the blank so the program prints: {expect}', tpl, correct, wrongs, expl)
def arrange(topic, diff, cat, lines, question, expl):
    out = run_py(['\n'.join(lines)])[0]; assert out and not ERR.match(out), (lines, out)
    mk(topic, 'Python', diff, 'arrange', cat, question + f' It must print: {out}', '', None, None, expl, lines=lines)
def fixq(topic, diff, cat, buggy, expect, fixes, expl):
    outs = run_py(fixes); assert outs[0] == expect and all(o != expect for o in outs[1:]), ('fix not unique', buggy, outs)
    mk(topic, 'Python', diff, 'fix', cat, f'Which version fixes the code so it prints: {expect}', buggy, fixes[0], fixes[1:], expl)
TH = ['members','attendees','sessions','speakers','workshops','teams','volunteers','mentors','projects','talks']
WD = ['GDG Assiut','DevFest','Study Jam','Flutter','Firebase','Hackathon','Code Man','Android','TensorFlow','Cloud Run']
ri = R.randint; pick = R.choice
# =============== PYTHON (World 1: Python City) ===============
B=[]
for _ in range(60):
    a,b,z = ri(2,12),ri(2,9),ri(2,5); n1,n2 = R.sample(TH,2)
    B += [f"{n1} = {a}\n{n2} = {b}\nprint({n1} + {n2} * {z})", f"{n1} = {a}\n{n2} = {b}\nprint(({n1} + {n2}) * {z})", f"{n1} = {a*z}\nprint({n1} // {z} + {n1} % {b})", f"{n1} = {a}\n{n1} += {b}\n{n1} *= {z}\nprint({n1})", f"{n1} = {a}\n{n2} = {n1} ** 2\nprint({n2} - {b})"]
family('python','Python',1,'Python',B,6); family('python','Python',2,'Python',B,6)
S1,S2=[],[]
for w in WD:
    v = pick(['community','event','topic']); S1 += [f"{v} = {w!r}\nprint({v}.upper())", f"{v} = {w!r}\nprint({v}[:3])", f"{v} = {w!r}\nprint({v}[::-1])", f"{v} = {w!r}\nprint({v}.replace('a', '4'))", f"{v} = {w!r}\nprint({v} + '!' * 2)", f"{v} = {w!r}\nprint({v}.split()[0])"]
    S2 += [f"{v} = {w!r}\nprint(len({v}))", f"{v} = {w!r}\nprint({v}.count('s'))", f"{v} = {w!r}\nprint({v}.find('e'))", f"{v} = {w!r}\nprint(len({v}.split()))"]
family('python','Python',1,'Python',S1,6); family('python','Python',2,'Python',S2,5)
family('python','Python',1,'Python',[f"print(type({v}).__name__)" for v in ["42","3.14","'GDG'","True","['Flutter', 'Firebase']","('a', 'b')","{'event': 'DevFest'}","{1, 2, 3}","None"]],5,question='What type name is printed?')
family('python','Python',1,'Python',[f"name = {pick(WD)!r}\nmembers = {ri(20,300)}\nprint(f\"{{name}} has {{members}} members\")" for _ in range(8)],3)
L1,L2=[],[]
for _ in range(12):
    xs = R.sample(['Flutter','Firebase','Android','Cloud','Dart','Kotlin','Colab'],4); n = ri(2,9)
    L1 += [f"tools = {xs}\nprint(len(tools))", f"tools = {xs}\nprint(tools[-1])", f"tools = {xs}\ntools.append('Gemini')\nprint(len(tools))", f"tools = {xs}\nprint(sorted(tools)[0])", f"tools = {xs}\nprint(tools.pop())", f"tools = {xs}\nprint(tools[1:3][0])"]
family('python','Python',1,'Python',[b for b in L1 if 'len' in b or 'append' in b],3); family('python','Python',2,'Python',[b for b in L1 if 'len' not in b and 'append' not in b],4)
F=[]
for _ in range(14):
    a,b = ri(2,9),ri(2,9); nm = pick(['score','points','bonus','total'])
    F += [f"def {nm}(base, extra=10):\n    return base + extra\nprint({nm}({a}))", f"def {nm}(a, b):\n    return a * b + {a}\nprint({nm}({a}, {b}))", f"def {nm}(n):\n    return n * n - {b}\nprint({nm}({a}) + {nm}({b}))", f"def {nm}(x, y=2):\n    return x ** y\nprint({nm}({a}), {nm}({a}, 3))"]
family('python','Python',2,'Python',[b for b in F if ',' not in b.split('print')[-1]],3); family('python','Python',2,'Python',[b for b in F if b.split('print')[-1].count(',')>=1 and 'y=2' in b],2)
fill('python','Python',1,'Python',"attendees = [12, 30, 25]\nprint(____(attendees))",'sum',['len','max','min'],'67','sum() adds all items: 12 + 30 + 25 = 67.')
fill('python','Python',1,'Python',"event = 'DevFest'\nprint(event.____())",'upper',['lower','title','capitalize'],'DEVFEST','upper() converts every letter to uppercase.')
fill('python','Python',2,'Python',"teams = ['Red', 'Blue']\nteams.____('Green')\nprint(len(teams))",'append',['remove','pop','sort'],'3','append() adds one item at the end, so the length becomes 3.')
arrange('python',1,'Python',["members = ['Ali', 'Sara']","members.append('Omar')","print(len(members))"],'Arrange the lines in the right order.','Create the list, add an item, then print its length.')
arrange('python',2,'Python',["def welcome(name):","    return 'Welcome ' + name","print(welcome('GDG Assiut'))"],'Arrange the function definition and its call.','Define the function first, then call it.')
# =============== LOOPS (World 2: Loop Valley) ===============
B=[]
for _ in range(14):
    a,b,s,m,t = ri(0,3),ri(5,10),ri(2,3),ri(2,4),ri(10,60); n = pick(TH)
    B += [f"{n} = 0\nfor i in range({a}, {b}):\n    {n} += i\nprint({n})", f"count = 0\nfor i in range({a}, {b+4}, {s}):\n    count += 1\nprint(count)", f"x = {ri(1,3)}\nsteps = 0\nwhile x < {b*3}:\n    x *= 2\n    steps += 1\nprint(steps)",
          f"total = 0\nfor i in range({b-3}):\n    for j in range({s+1}):\n        total += 1\nprint(total)", f"s = 0\nfor i in range({b+3}):\n    if i % {m} == 0:\n        continue\n    s += i\nprint(s)", f"for i in range(20):\n    if i * i > {t}:\n        break\nprint(i)",
          f"{n} = {b*4}\nrounds = 0\nwhile {n} > 0:\n    {n} -= {b-2}\n    rounds += 1\nprint(rounds)"]
family('loops','Python',1,'Python',B[::7]+B[1::7],8); family('loops','Python',2,'Python',B[2::7]+B[3::7]+B[4::7],10); family('loops','Python',3,'Problem Solving',B[5::7]+B[6::7],7)
J=[]
for _ in range(10):
    a,s = ri(4,12),ri(2,3)
    J += [f"let total = 0;\nfor (let i = 1; i <= {a}; i++) {{\n  total += i;\n}}\nconsole.log(total);", f"let n = {a*3};\nlet c = 0;\nwhile (n > 0) {{\n  n -= {s+1};\n  c++;\n}}\nconsole.log(c);", f"let c = 0;\nfor (let i = 0; i < {a}; i++) {{\n  if (i % 2 === 0) continue;\n  c++;\n}}\nconsole.log(c);", f"let r = 1;\nfor (let i = 0; i < {s+2}; i++) r *= {s};\nconsole.log(r);"]
family('loops','JavaScript',2,'JavaScript',J,6)
C=[]
for _ in range(10):
    a,s = ri(4,12),ri(2,3)
    C += [f"int total = 0;\nfor (int i = 1; i <= {a}; i++) total += i;\ncout << total;", f"int n = {a*3}, c = 0;\nwhile (n > 0) {{ n -= {s+1}; c++; }}\ncout << c;", f"int c = 0;\nfor (int i = 0; i < {a}; i++) {{\n  if (i % 2 == 0) continue;\n  c++;\n}}\ncout << c;", f"int r = 1;\nfor (int i = 0; i < {s+2}; i++) r *= {s};\ncout << r;"]
family('loops','C++',2,'C++',C,5)
JV=[c.replace('cout << ','System.out.println(').replace(';\n',');\n') if False else c for c in []]
JV=[]
for _ in range(10):
    a,s = ri(4,12),ri(2,3)
    JV += [f"int total = 0;\nfor (int i = 1; i <= {a}; i++) total += i;\nSystem.out.println(total);", f"int n = {a*3}, c = 0;\nwhile (n > 0) {{ n -= {s+1}; c++; }}\nSystem.out.println(c);", f"int c = 0;\nfor (int i = 0; i < {a}; i++) {{\n  if (i % 2 == 0) continue;\n  c++;\n}}\nSystem.out.println(c);", f"int r = 1;\nfor (int i = 0; i < {s+2}; i++) r *= {s};\nSystem.out.println(r);"]
family('loops','Java',2,'Java',JV,5)
fill('loops','Python',1,'Python',"total = 0\nfor i in ____(1, 4):\n    total += i\nprint(total)",'range',['len','sum','list'],'6','range(1, 4) yields 1, 2, 3, which add up to 6.')
fill('loops','Python',2,'Python',"for i in range(10):\n    if i == 3:\n        ____\n    print(i)\nprint('end')",'break',['continue','pass','exit'],'0\n1\n2\nend','break leaves the loop at i == 3.')
arrange('loops',1,'Python',["count = 0","while count < 3:","    count += 1","print(count)"],'Arrange the while loop.','Initialise, loop while the condition holds, update inside, then print.')
arrange('loops',2,'Python',["total = 0","for i in range(1, 5):","    total += i","print(total)"],'Arrange the summing loop.','Start from zero, loop through the range, accumulate, print.')
# =============== DATA STRUCTURES (World 3: Data Dungeon) ===============
D=[]; DS=[]
for _ in range(16):
    a,b,c,d = ri(2,20),ri(2,20),ri(2,20),ri(2,20); w1,w2,w3 = R.sample(WD,3); k = ri(3,6)
    D += [f"attendees = [{a}, {b}, {c}]\nattendees.append({d})\nprint(sum(attendees))", f"talks = {{'python': {a}, 'flutter': {b}}}\ntalks['ai'] = {c}\nprint(sum(talks.values()))", f"s = {{{a}, {b}, {a}}}\nprint(len(s))", f"t = ({a}, {b}, {c})\nprint(t[1] + t[-1])", f"words = {R.sample(WD,4)}\nprint(len([w for w in words if len(w) > {k+3}]))", f"data = [{a}, {b}, {c}, {d}]\nprint(max(data) - min(data))"]
    DS += [f"stack = []\nstack.append('{w1}')\nstack.append('{w2}')\nprint(stack.pop())", f"from collections import deque\nq = deque(['{w1}', '{w2}', '{w3}'])\nq.popleft()\nprint(q[0])", f"d = {{'{w1}': 1, '{w2}': 2}}\nprint(list(d)[-1])", f"names = ['{w1}', '{w2}', '{w3}']\nprint(sorted(names)[0])"]
family('data','Python',1,'Data Structures',D[::6]+D[1::6],7); family('data','Python',2,'Data Structures',D[2::6]+D[3::6]+D[4::6],8); family('data','Python',3,'Data Structures',D[5::6]+D[4::6][:5],4)
family('data','Python',2,'Data Structures',DS,6,question='What is printed?')
J=[]
for _ in range(10):
    a,b,c = ri(2,9),ri(2,9),ri(2,9)
    J += [f"const m = new Map();\nm.set('a', {a});\nm.set('b', {b});\nconsole.log(m.size + m.get('b'));", f"const arr = [{a}, {b}, {c}];\nconsole.log(arr.map(x => x * 2).reduce((s, x) => s + x, 0));", f"const set = new Set([{a}, {b}, {a}]);\nconsole.log(set.size);", f"const o = {{ events: {a} }};\no.events += {b};\nconsole.log(o.events);", f"const q = [{a}, {b}, {c}];\nq.shift();\nconsole.log(q[0] + q.length);"]
family('data','JavaScript',2,'JavaScript',J,6)
C=[]
for _ in range(10):
    a,b,c,d = ri(2,9),ri(2,9),ri(2,9),ri(2,9)
    C += [f"vector<int> v = {{{a}, {b}, {c}}};\nv.push_back({d});\ncout << v.size() + v[1];", f"map<string,int> m;\nm[\"flutter\"] = {a};\nm[\"dart\"] = {b};\ncout << m.size() * m[\"dart\"];", f"stack<int> s;\ns.push({a});\ns.push({b});\ns.pop();\ncout << s.top();", f"queue<int> q;\nq.push({a});\nq.push({b});\ncout << q.front();"]
family('data','C++',2,'C++',C,5)
JV=[]
for _ in range(10):
    a,b = ri(2,9),ri(2,9)
    JV += [f"ArrayList<Integer> list = new ArrayList<>();\nlist.add({a});\nlist.add({b});\nSystem.out.println(list.get(1) + list.size());", f"HashMap<String,Integer> m = new HashMap<>();\nm.put(\"dev\", {a});\nm.put(\"dev\", {b});\nSystem.out.println(m.get(\"dev\") + m.size());", f"Deque<Integer> st = new ArrayDeque<>();\nst.push({a});\nst.push({b});\nSystem.out.println(st.pop());", f"HashSet<Integer> s = new HashSet<>();\ns.add({a});\ns.add({a});\ns.add({b});\nSystem.out.println(s.size());"]
family('data','Java',2,'Java',JV,5)
fill('data','Python',1,'Data Structures',"speakers = {'Sara': 'AI', 'Omar': 'Flutter'}\nprint(speakers.____('Omar'))",'get',['values','keys','index'],'Flutter','dict.get(key) returns the value stored under the key.')
fill('data','Python',2,'Data Structures',"stack = ['a', 'b', 'c']\nprint(stack.____())",'pop',['push','remove','top'],'c','pop() removes and returns the last item, which is how a stack behaves.')
fill('data','Python',2,'Data Structures',"ids = [3, 1, 3, 2, 1]\nprint(len(____(ids)))",'set',['list','sorted','tuple'],'3','set() keeps only unique values: {1, 2, 3}.')
arrange('data',1,'Data Structures',["stack = []","stack.append('A')","stack.append('B')","print(stack.pop())"],'Arrange the stack operations.','Create, push A, push B, then pop returns the last pushed item.')
arrange('data',2,'Data Structures',["info = {}","info['event'] = 'DevFest'","info['city'] = 'Assiut'","print(len(info))"],'Arrange the dictionary code.','Create the dict, add two keys, then print its size.')
arrange('data',2,'Data Structures',["from collections import deque","line = deque(['a', 'b'])","line.append('c')","print(line.popleft())"],'Arrange the queue code.','A queue is FIFO: popleft returns the first item added.')
# =============== OOP (World 4: OOP Fortress) ===============
O=[]; OS=[]
for _ in range(14):
    a,b = ri(2,9),ri(2,9); n = pick(['Ali','Sara','Omar','Nour']); w1,w2 = R.sample(WD,2)
    O += [f"class Member:\n    def __init__(self, name, points):\n        self.name = name\n        self.points = points\n    def bonus(self):\n        return self.points + {a}\nm = Member('{n}', {b})\nprint(m.bonus())",
          f"class Badge:\n    count = 0\n    def __init__(self):\n        Badge.count += 1\nfor _ in range({a}):\n    Badge()\nprint(Badge.count)",
          f"class Wallet:\n    def __init__(self):\n        self._coins = {a}\n    def add(self, n):\n        self._coins += n\n        return self._coins\nprint(Wallet().add({b}))",
          f"from abc import ABC, abstractmethod\nclass Shape(ABC):\n    @abstractmethod\n    def area(self): ...\nclass Sq(Shape):\n    def __init__(self, s): self.s = s\n    def area(self): return self.s ** 2\nprint(Sq({a}).area())"]
    OS += [f"class Event:\n    def title(self):\n        return '{w1}'\nclass Workshop(Event):\n    def title(self):\n        return super().title() + ' Workshop'\nprint(Workshop().title())",
           f"class Speaker:\n    def talk(self): return '{w1}'\nclass Mentor(Speaker):\n    def talk(self): return '{w2}'\nfor p in [Speaker(), Mentor()]:\n    print(p.talk(), end=' ')",
           f"class P:\n    def hi(self): return '{w1}'\nclass K(P): pass\nprint(K().hi())"]
family('oop','Python',2,'Python',O[::2],8,expl='The code prints {o}.'); family('oop','Python',3,'Python',O[1::2],4); family('oop','Python',2,'Python',OS,5,pool=None)
J=[]; C=[]; JV=[]
for _ in range(8):
    a,b = ri(2,9),ri(2,9)
    J += [f"class Team {{\n  constructor(n) {{ this.n = n; }}\n  double() {{ return this.n * 2; }}\n}}\nconsole.log(new Team({a}).double());", f"class A {{ val() {{ return {a}; }} }}\nclass B extends A {{ val() {{ return super.val() + {b}; }} }}\nconsole.log(new B().val());", f"class C {{ static count = {a}; static inc() {{ return ++C.count; }} }}\nC.inc();\nconsole.log(C.inc());"]
    C += [f"class Counter {{\npublic:\n  int n = {a};\n  void inc() {{ n += {b}; }}\n}};\nCounter c;\nc.inc();\ncout << c.n;", f"class A {{ public: virtual int f() {{ return {a}; }} }};\nclass B : public A {{ public: int f() override {{ return {b}; }} }};\nA* p = new B();\ncout << p->f();", f"class P {{ int x; public: P(int v) : x(v) {{}} int get() {{ return x * {b}; }} }};\nP p({a});\ncout << p.get();"]
    JV += [f"class Box {{ int v; Box(int v) {{ this.v = v; }} int twice() {{ return v * 2; }} }}\nSystem.out.println(new Box({a}).twice());", f"class A {{ int f() {{ return {a}; }} }}\nclass B extends A {{ int f() {{ return super.f() + {b}; }} }}\nSystem.out.println(new B().f());", f"class Cnt {{ static int c = 0; Cnt() {{ c++; }} }}\nfor (int i = 0; i < {a}; i++) new Cnt();\nSystem.out.println(Cnt.c);"]
family('oop','JavaScript',2,'JavaScript',J,6); family('oop','C++',3,'C++',C,6); family('oop','Java',2,'Java',JV,6)
fill('oop','Python',2,'Python',"class Member:\n    def __init__(self, name):\n        ____.name = name\nprint(Member('Sara').name)",'self',['this','cls','me'],'Sara',"Inside a method, self is the current instance.")
fill('oop','Python',2,'Python',"class A:\n    def hi(self): return 'A'\nclass B(____):\n    pass\nprint(B().hi())",'A',['object2','self','B'],'A','class B(A) makes B inherit from A.')
fill('oop','Python',3,'Python',"class A:\n    def f(self): return 1\nclass B(A):\n    def f(self): return ____.f() + 1\nprint(B().f())",'super()',['self','A','B()'],'2','super() reaches the parent implementation.')
arrange('oop',2,'Python',["class Event:","    def __init__(self, name):","        self.name = name","print(Event('DevFest').name)"],'Arrange the class definition and use.','Define the class, then its constructor body, then create and use an object.')
arrange('oop',3,'Python',["class Shape:","    def area(self):","        return 0","class Sq(Shape):","    def area(self):","        return 4","print(Sq().area())"],'Arrange the inheritance example.','Parent first, then the subclass overriding the method, then the call.')
arrange('oop',2,'Python',["class Counter:","    def __init__(self):","        self.n = 0","    def inc(self):","        self.n += 1","c = Counter()","c.inc()","print(c.n)"],'Arrange the Counter class.','Class body first, then create an instance, call inc, and print.')
for d,c,l,q,opts,e in [
 (1,'Python','Python',"Which Python method runs when an object is created?",["__init__","__start__","__make__","__create__"],"__init__ initialises new instances."),
 (1,'Java','Java',"Which Java keyword creates an object?",["new","make","create","alloc"],"new allocates and constructs an object."),
 (2,'Computer Science Fundamentals','CS',"Which OOP principle hides internal data behind methods?",["Encapsulation","Inheritance","Recursion","Compilation"],"Encapsulation restricts direct access to internals."),
 (2,'Computer Science Fundamentals','CS',"Polymorphism lets you...",["Call the same method on different types with different behavior","Declare variables without types","Run code faster","Avoid classes"],"One interface, many implementations."),
 (3,'C++','C++',"Which keyword allows overriding through a base-class pointer in C++?",["virtual","static","const","inline"],"virtual enables runtime dispatch."),
 (3,'Java','Java',"Can you create an instance of an abstract class directly in Java?",["No, only of a concrete subclass","Yes, always","Only inside main","Only if it has no methods"],"Abstract classes cannot be instantiated.")]:
    hand('oop',l,d,'conceptual',c,q,'',opts,e)
# =============== ALGORITHMS (World 5: Algorithm Arena) ===============
CX = ['O(1)','O(log n)','O(n)','O(n log n)','O(n^2)','O(n^3)','O(2^n)']
for _ in range(2):
    v = pick(TH); w = pick(['i','k','idx'])
    for diff,code,ans in [
      (1,f"for {w} in range(n):\n    print({w})",'O(n)'),(1,f"print({v}[0])",'O(1)'),(2,f"for i in range(n):\n    for j in range(n):\n        print(i, j)",'O(n^2)'),(2,f"i = 1\nwhile i < n:\n    i *= 2",'O(log n)'),
      (1,f"for i in range(n):\n    print(i)\nfor j in range(n):\n    print(j)",'O(n)'),(2,f"for i in range(n):\n    for j in range(10):\n        print(i, j)",'O(n)'),(2,f"for i in range(n):\n    for j in range(i):\n        print(j)",'O(n^2)'),
      (2,f"def search(a, x, lo, hi):\n    if lo > hi: return -1\n    mid = (lo + hi) // 2\n    if a[mid] == x: return mid\n    if a[mid] < x: return search(a, x, mid + 1, hi)\n    return search(a, x, lo, mid - 1)",'O(log n)'),
      (3,f"def fib(n):\n    return n if n < 2 else fib(n-1) + fib(n-2)",'O(2^n)'),(3,f"for i in range(n):\n    for j in range(n):\n        for k in range(n):\n            pass",'O(n^3)'),(3,f"{v}.sort()\nfor x in {v}:\n    print(x)",'O(n log n)'),
      (3,f"for i in range(n):\n    j = 1\n    while j < n:\n        j *= 2",'O(n log n)')]:
        c2 = code if _==0 else code.replace('print(i, j)','pass').replace('print(i)','pass').replace('print(j)','pass') if 'print' in code else code+'\n# '+v
        wr = [x for x in CX if x != ans]; R.shuffle(wr); mk('algo','Python',diff,'complexity','Algorithms',"What is the time complexity of this code (n = input size)?",c2,ans,wr[:3],f"The dominant work grows as {ans}.")
for d,q,opts,e in [
 (1,"Find a member in a SORTED list of 1,000,000 names as fast as possible.",["Binary search","Linear search","Bubble sort","Random guessing"],"Binary search halves the range each step."),
 (1,"Process support tickets in the order they arrive.",["Queue","Stack","Binary tree","Set"],"A queue is first-in, first-out."),
 (1,"Implement the 'undo' button of an editor.",["Stack","Queue","Hash set","Graph"],"Undo reverses the most recent action first (LIFO)."),
 (2,"Find the shortest path in an unweighted maze, like CODE MAN.",["Breadth-first search","Depth-first search only","Bubble sort","Binary search"],"BFS reaches every cell in order of distance."),
 (2,"Check quickly (average O(1)) whether a username already exists.",["Hash set","Sorted array scan","Linked list scan","Bubble sort"],"Hashing gives average constant-time membership checks."),
 (2,"Count how many times each word appears in a text.",["Hash map","Stack","Binary search","Queue"],"Map each word to a counter."),
 (3,"Repeatedly get the smallest of a changing collection.",["Min-heap (priority queue)","Stack","Queue","Plain array scan each time"],"A heap gives O(log n) insert and extract-min."),
 (3,"Sort a small, nearly sorted list with very little code and overhead.",["Insertion sort","Quick sort with random pivot only","Bogo sort","Radix sort of strings"],"Insertion sort is near O(n) on nearly sorted input.")]:
    hand('algo','Python',d,'algorithm','Algorithms',q,'',opts,e)
for d,q,opts,e in [
 (1,"Binary search requires the array to be...",["Sorted","Unique","Reversed","Small"],"It discards half using the order."),(1,"A recursive function must have...",["A base case","A loop","A global variable","A return type of int"],"Without it recursion never stops."),
 (2,"Average time complexity of merge sort?",["O(n log n)","O(n)","O(n^2)","O(log n)"],"log n levels of merging, n work per level."),(2,"Worst-case time of bubble sort?",["O(n^2)","O(n)","O(n log n)","O(log n)"],"Nested passes over the data."),
 (3,"Space complexity of merge sort?",["O(n)","O(1)","O(log n)","O(n^2)"],"It needs an auxiliary array."),(3,"Which algorithm does Python's built-in sorted() use?",["Timsort","Quick sort","Heap sort","Selection sort"],"Timsort is stable and adaptive."),
 (3,"Worst-case search time in a degenerate (list-like) binary search tree?",["O(n)","O(1)","O(log n)","O(n log n)"],"It behaves like a linked list.")]:
    hand('algo','Python',d,'complexity' if 'complexity' in q or 'time' in q or 'Space' in q else 'conceptual','Algorithms',q,'',opts,e)
A=[]
for _ in range(14):
    n = ri(3,8); a,b = ri(12,60),ri(2,9)
    A += [f"def f(n):\n    return 1 if n <= 1 else n * f(n - 1)\nprint(f({n}))", f"def f(n):\n    return n if n < 2 else f(n - 1) + f(n - 2)\nprint(f({n+2}))", f"def f(n):\n    return 0 if n == 0 else n + f(n - 1)\nprint(f({n+2}))", f"def g(a, b):\n    return a if b == 0 else g(b, a % b)\nprint(g({a}, {b}))", f"def p(n):\n    return 1 if n == 0 else 2 * p(n - 1)\nprint(p({n}))",
          f"a = {R.sample(range(1,30),5)}\nfor i in range(len(a) - 1):\n    if a[i] > a[i + 1]:\n        a[i], a[i + 1] = a[i + 1], a[i]\nprint(a)"]
family('algo','Python',3,'Algorithms',[b for b in A if 'def' in b],9); family('algo','Python',2,'Algorithms',[b for b in A if 'def' not in b],4,question='What is printed after ONE bubble-sort pass?')
bs = lambda arr,t: f"a = {arr}\nt = {t}\nlo, hi, steps = 0, len(a) - 1, 0\nwhile lo <= hi:\n    mid = (lo + hi) // 2\n    steps += 1\n    if a[mid] == t:\n        break\n    elif a[mid] < t:\n        lo = mid + 1\n    else:\n        hi = mid - 1\nprint(steps)"
family('algo','Python',3,'Algorithms',[bs(list(range(1,32,2)),t) for t in (1,5,9,15,21,31,7,13)],4,question='How many steps does this binary search take?')
family('algo','JavaScript',3,'JavaScript',[f"function f(n) {{ return n <= 1 ? 1 : n * f(n - 1); }}\nconsole.log(f({n}));" for n in range(3,9)]+[f"const a = [{', '.join(map(str,R.sample(range(1,20),5)))}];\na.sort((x, y) => x - y);\nconsole.log(a[0] + a[a.length - 1]);" for _ in range(5)],4)
family('algo','C++',3,'C++',[f"int f(int n) {{ return n <= 1 ? 1 : n * f(n - 1); }}".replace('int f(int n) { return n <= 1 ? 1 : n * f(n - 1); }',"function<int(int)> f = [&](int n) { return n <= 1 ? 1 : n * f(n - 1); };")+f"\ncout << f({n});" for n in range(3,8)]+[f"vector<int> v = {{{', '.join(map(str,R.sample(range(1,20),5)))}}};\nsort(v.begin(), v.end());\ncout << v[0] + v[4];" for _ in range(5)],4)
arrange('algo',2,'Algorithms',["def is_even(n):","    return n % 2 == 0","print(is_even(10))"],'Arrange this helper function.','Define, then call.')
arrange('algo',3,'Algorithms',["def fact(n):","    if n <= 1:","        return 1","    return n * fact(n - 1)","print(fact(4))"],'Arrange the recursive factorial.','Base case first, then the recursive step, then the call.')
arrange('algo',3,'Algorithms',["a = [1, 3, 5, 7, 9]","lo, hi = 0, len(a) - 1","while lo <= hi:","    mid = (lo + hi) // 2","    if a[mid] == 7:","        print(mid)","        break","    lo = mid + 1"],'Arrange this binary search for 7.','Setup, loop, midpoint, check, and move the lower bound.')
arrange('algo',2,'Algorithms',["a = [3, 1, 2]","a.sort()","print(a[0])"],'Arrange the sorting snippet.','Create the list, sort it, then read the first item.')
fill('algo',  'Python',2,'Algorithms',"a = [5, 2, 9]\nprint(____(a))",'sorted',['len','sum','list'],'[2, 5, 9]','sorted() returns a new sorted list.')
fill('algo','Python',3,'Algorithms',"def power(b, e):\n    if e == 0:\n        return ____\n    return b * power(b, e - 1)\nprint(power(2, 5))",'1',['0','b','e'],'32','The base case for e == 0 must return 1, the multiplicative identity.')
fill('algo','Python',3,'Algorithms',"lo, hi = 0, 9\nmid = (lo ____ hi) // 2\nprint(mid)",'+',['-','*','%'],'4','The midpoint is the average of lo and hi.')
# =============== DEBUGGING (World 6: Debugging Lab) ===============
PE=['IndexError','KeyError','TypeError','NameError','ValueError','ZeroDivisionError','AttributeError']
E=[]
for _ in range(2):
    a = ri(3,9); w = pick(WD)
    E += [f"attendees = [1, 2, 3]\nprint(attendees[{a}])", f"d = {{'event': 'DevFest'}}\nprint(d['{w}'])", f"print({a} / 0)", "print(total + 1)", "int('GDG')", f"print('{w}' + {a})", "x = None\nx.speak()", "t = (1, 2)\nt[0] = 5", "len(5)", "[].pop()", "float('x')", f"a = [{a}]\na.nope", "print(undefined_var)", "'abc'.foo()", "{}.pop('k')", "int([1])"]
family('debug','Python',2,'Python',E,12,question='Which error does this code raise?',typ='bug',expl='This raises {o}.',pool=PE)
JE=['TypeError','ReferenceError','SyntaxError','RangeError']
family('debug','JavaScript',2,'JavaScript',["const attendees = 5;\nattendees = 6;","console.log(missing);","null.x;","JSON.parse('{bad');","(123).toFixed(101);","new Array(-1);","undefined.length;","let a = 1;\na();"],6,question='Which error type is thrown?',typ='bug',expl='JavaScript throws {o} here.',pool=JE)
for d,c,l,q,code,opts,e in [
 (1,'Python','Python',"Find the bug.","for i in range(3)\n    print(i)",["Missing colon after range(3)","range is invalid","print needs a semicolon","i is undefined"],"for statements need a colon."),
 (1,'Python','Python',"Find the bug.","def add(a, b):\n    return a + b\nprint(add(1))",["A required argument is missing","Wrong return","add is undefined","Needs a semicolon"],"add needs two arguments."),
 (1,'Python','Python',"What goes wrong?","numbers = [1, 2, 3]\nprint(numbers[3])",["Index out of range","Wrong type","Missing import","Missing colon"],"Valid indexes are 0..2."),
 (2,'JavaScript','JavaScript',"Find the bug.","let x = 5;\nlet x = 6;",["x is declared twice with let","Missing semicolon","x must be const","5 is invalid"],"let cannot be redeclared in the same scope."),
 (2,'JavaScript','JavaScript',"Find the bug.","if (x = 3) {\n  run();\n}",["Assignment used instead of comparison","Missing else","Wrong brace","x is const"],"Use === to compare."),
 (2,'JavaScript','JavaScript',"Find the bug.","const a = 1;\na = 2;",["Reassigning a const","Missing let","a is undefined","Semicolon"],"const bindings cannot be reassigned."),
 (2,'C++','C++',"Find the bug.","int a[3] = {1, 2, 3};\ncout << a[3];",["Out-of-bounds access","Missing semicolon","Wrong type","cout undefined"],"Valid indexes are 0..2."),
 (2,'Java','Java',"What goes wrong?","String s = null;\nSystem.out.println(s.length());",["NullPointerException","ArrayIndexOutOfBoundsException","Syntax error","ClassCastException"],"Calling a method on null."),
 (2,'Java','Java',"What goes wrong?","int[] a = new int[3];\na[3] = 1;",["ArrayIndexOutOfBoundsException","NullPointerException","Compile error","Nothing happens"],"Array size 3 has max index 2."),
 (2,'Python','Python',"Find the bug.","a = [1, 2, 3]\nfor i in range(len(a) + 1):\n    print(a[i])",["The loop runs one step too far","a is undefined","len is misused","print is wrong"],"Off-by-one error."),
 (2,'Problem Solving','Python',"Find the logic bug.","def is_even(n):\n    return n % 2 == 1",["It returns True for odd numbers","Missing parameter","Wrong operator %","There is no bug"],"Even numbers leave remainder 0."),
 (2,'Problem Solving','Python',"Find the logic bug.","def average(a):\n    return sum(a) / len(a) + 1",["It adds an extra 1","It divides by zero","Wrong sum","Missing loop"],"The average should not add 1."),
 (3,'Python','Python',"Find the bug.","def add_member(m, team=[]):\n    team.append(m)\n    return team\nprint(add_member('A'), add_member('B'))",["Mutable default argument is shared between calls","Missing return","team is undefined","append is invalid"],"The default list is created once."),
 (3,'Python','Python',"Find the bug.","total = 0\ndef add():\n    total += 1\nadd()",["total is treated as local without 'global'","add is undefined","+= is invalid","Needs a return"],"Assigning inside a function makes the name local."),
 (3,'C++','C++',"Find the bug.","int x;\ncout << x;",["x is uninitialized","Missing include","cout is wrong","x must be const"],"Reading an uninitialized variable is undefined behavior."),
 (3,'JavaScript','JavaScript',"Why does this log 3 three times?","for (var i = 0; i < 3; i++) {\n  setTimeout(() => console.log(i), 0);\n}",["var is function-scoped, so all callbacks share one i","setTimeout is broken","The loop runs 3 times too many","console.log is async"],"Use let to get a fresh binding per iteration.")]:
    hand('debug',l,d,'bug',c,q,code,opts,e)
fixq('debug',1,'Python',"for i in range(3)\n    print(i)","0\n1\n2",["for i in range(3):\n    print(i)","for i in range(3);\n    print(i)","for i in range[3]:\n    print(i)","for i in (3):\n    print(i)"],'for needs a colon.')
fixq('debug',1,'Python',"attendees = [4, 5, 6]\nprint(attendees[3])","6",["attendees = [4, 5, 6]\nprint(attendees[2])","attendees = [4, 5, 6]\nprint(attendees[4])","attendees = [4, 5, 6]\nprint(attendees(2))","attendees = [4, 5, 6]\nprint(attendees[-4])"],'The last index of a 3-item list is 2 (or -1).')
fixq('debug',2,'Python',"x = 5\nif x = 5:\n    print('five')","five",["x = 5\nif x == 5:\n    print('five')","x = 5\nif x === 5:\n    print('five')","x = 5\nif (x := 5) = 5:\n    print('five')","x = 5\nif x => 5:\n    print('five')"],'Comparison uses ==.')
fixq('debug',2,'Python',"name = 'GDG'\nprint('Hello ' + name + 3)","Hello GDG3",["name = 'GDG'\nprint('Hello ' + name + str(3))","name = 'GDG'\nprint('Hello ' + name + int(3))","name = 'GDG'\nprint('Hello ', name, 3 +)","name = 'GDG'\nprint('Hello ' - name + '3')"],'Convert the number to a string before concatenating.')
fixq('debug',2,'Python',"total = 0\nfor i in range(1, 4):\ntotal += i\nprint(total)","6",["total = 0\nfor i in range(1, 4):\n    total += i\nprint(total)","total = 0\nfor i in range(1, 4):\n    total += i\n    print(total)","total = 0\nfor i in range(1, 4)\n    total += i\nprint(total)","total = 0\nfor i in range(1, 4):\n    total =+ i\nprint(total)"],'The loop body must be indented.')
fixq('debug',3,'Python',"def avg(a):\n    return sum(a) / len(a) + 1\nprint(avg([2, 4, 6]))","4.0",["def avg(a):\n    return sum(a) / len(a)\nprint(avg([2, 4, 6]))","def avg(a):\n    return sum(a) // len(a)\nprint(avg([2, 4, 6]))","def avg(a):\n    return sum(a) / (len(a) + 1)\nprint(avg([2, 4, 6]))","def avg(a):\n    return sum(a) * len(a)\nprint(avg([2, 4, 6]))"],'Remove the extra +1.')
fixq('debug',3,'Python',"def add_member(m, team=[]):\n    team.append(m)\n    return team\nprint(add_member('A'))\nprint(add_member('B'))","['A']\n['B']",["def add_member(m, team=None):\n    team = team or []\n    team.append(m)\n    return team\nprint(add_member('A'))\nprint(add_member('B'))","def add_member(m, team=[]):\n    team.append(m)\n    return team\nprint(add_member('A'))\nprint(add_member('B'))","def add_member(m, team=[]):\n    team += [m]\n    return team\nprint(add_member('A'))\nprint(add_member('B'))","def add_member(m, team=()):\n    team.append(m)\n    return team\nprint(add_member('A'))\nprint(add_member('B'))"],'Use None as the default and build a new list each call.')
fixq('debug',2,'Python',"count = 0\nwhile count < 3:\n    print(count)","0\n1\n2",["count = 0\nwhile count < 3:\n    print(count)\n    count += 1","count = 0\nwhile count < 3:\n    print(count)\n    count -= 1","count = 0\nwhile count > 3:\n    print(count)\n    count += 1","count = 0\nwhile count < 3:\n    count += 1\n    print(count)"],'The loop never changed count, so it never ended.')
for tpl,c,w,exp in [("try:\n    value = int('GDG')\nexcept ____:\n    print('invalid')",'ValueError',['TypeError','KeyError','IndexError'],'invalid'),("try:\n    print({}['x'])\nexcept ____:\n    print('missing key')",'KeyError',['ValueError','IndexError','TypeError'],'missing key'),
                    ("attendees = [1, 2]\ntry:\n    print(attendees[5])\nexcept ____:\n    print('out of range')",'IndexError',['KeyError','ValueError','TypeError'],'out of range'),("try:\n    print(10 / 0)\nexcept ____:\n    print('math error')",'ZeroDivisionError',['ValueError','KeyError','TypeError'],'math error')]:
    fill('debug','Python',2,'Python',tpl,c,w,exp,f'{c} is the exception raised, so the matching except block runs.')
arrange('debug',2,'Python',["try:","    value = int('42')","except ValueError:","    print('invalid')","else:","    print(value)"],'Arrange the try/except/else block.','try first, then except, then else.')
arrange('debug',3,'Python',["def safe_div(a, b):","    try:","        return a / b","    except ZeroDivisionError:","        return 0","print(safe_div(4, 0))"],'Arrange the safe division function.','Wrap the risky division in try, handle ZeroDivisionError, then call.')
# =============== ADVANCED / CYBER CORE (World 7) ===============
G=[ (1,"What does GDG stand for?",["Google Developer Groups","Global Developer Guild","Google Design Group","General Developer Gathering"],"GDGs are community-run developer groups."),
 (1,"Which Google framework builds apps for mobile, web and desktop from one codebase?",["Flutter","React Native","Xamarin","Cordova"],"Flutter is Google's UI toolkit."),
 (1,"Which programming language is used to write Flutter apps?",["Dart","Swift","Ruby","Perl"],"Flutter apps are written in Dart."),
 (1,"Which Google platform offers Authentication, Firestore and Hosting for apps?",["Firebase","Chrome DevTools","Blogger","Google Maps Static"],"Firebase is a backend-as-a-service platform."),
 (1,"TensorFlow is mainly used for...",["Machine learning","Web hosting","Database design","Photo editing only"],"TensorFlow is an open-source ML library."),
 (1,"Which language does Google recommend for modern Android development?",["Kotlin","COBOL","Fortran","Pascal"],"Android development is Kotlin-first."),
 (2,"What is Jetpack Compose?",["A declarative UI toolkit for native Android","A cloud database","A CSS framework","A Python web framework"],"You describe the UI as composable functions."),
 (2,"Which JavaScript engine, developed by Google, powers Chrome and Node.js?",["V8","SpiderMonkey","Chakra","Rhino"],"V8 compiles JavaScript to machine code."),
 (2,"In Cloud Firestore, data is organized into...",["Collections of documents","Tables of rows only","Folders of images","Linked lists"],"Firestore is a document database."),
 (2,"Which Firebase product sends push notifications to devices?",["Cloud Messaging (FCM)","Remote Config","Crashlytics","Hosting"],"FCM delivers messages to apps."),
 (2,"What is ML Kit?",["On-device machine learning APIs for mobile apps","A SQL engine","An IDE","A CSS preprocessor"],"ML Kit brings ready-made ML features to mobile."),
 (2,"Gemini is...",["A family of AI models from Google","A JavaScript framework","A database","A Linux distribution"],"Gemini is Google's AI model family."),
 (2,"In Flutter, everything on screen is built from...",["Widgets","Servlets","Cursors","Tables"],"Flutter UIs are widget trees."),
 (2,"What does `flutter run` do?",["Builds and launches your app on a device or emulator","Deletes the project","Uploads to GitHub","Formats the code"],"It compiles and starts the app."),
 (2,"What is a hackathon?",["A time-boxed event where teams build projects","A type of virus","A programming language","A database backup"],"Hackathons are build-fast community events."),
 (2,"Which tool runs Python notebooks in the browser and is popular for learning ML?",["Google Colab","Google Docs","Google Forms","Google Calendar"],"Colab provides hosted notebooks."),
 (2,"What does Lighthouse in Chrome DevTools audit?",["Performance, accessibility, SEO and best practices","Your battery","Only spelling","Electric wiring"],"Lighthouse scores web page quality."),
 (2,"In Kotlin, which keyword declares a read-only variable?",["val","var","let","mut"],"val cannot be reassigned; var can."),
 (3,"Which command deploys a site to Firebase Hosting?",["firebase deploy","firebase push","flutter deploy","npm publish"],"firebase deploy uploads your configured project."),
 (3,"Which Cloud model lets you run code without managing servers?",["Serverless (e.g., Cloud Functions or Cloud Run)","Bare-metal colocation","Dial-up hosting","A local USB drive"],"The provider manages the servers."),
 (3,"Which statement about Firebase Realtime Database is correct?",["It stores data as JSON and syncs it in real time","It stores only images","It is a relational SQL database","It works only offline"],"It syncs JSON data to connected clients."),
 (3,"In TensorFlow, a tensor is...",["A multi-dimensional array","A network cable","A loop statement","A CSS selector"],"Tensors generalise vectors and matrices."),
 (2,"What is DevFest?",["A community-organized developer conference run by GDG chapters","A Python library","A type of compiler","A cloud database"],"DevFests are community events for developers."),
 (3,"Which Dart keyword marks a variable that can be assigned only once?",["final","static","dynamic","async"],"final variables are set once."),
 (2,"Which Chrome tool lets you inspect HTML/CSS and debug JavaScript in the browser?",["DevTools","Search Console","Workspace","Safe Browsing"],"Open DevTools with F12.")]
G += [
 (2,"In Flutter, which widget type is used when the UI must change over time (it holds mutable state)?",["StatefulWidget","StatelessWidget","Scaffold","Text"],"StatefulWidgets own state objects that can change."),
 (2,"Which Flutter method tells the framework that state changed so the UI should rebuild?",["setState()","rebuild()","refresh()","update()"],"setState() schedules a rebuild."),
 (2,"Which file declares the dependencies of a Flutter project?",["pubspec.yaml","Cargo.toml","requirements.txt","Gemfile"],"Flutter/Dart projects list packages in pubspec.yaml."),
 (2,"Which Firebase service signs users in with email/password or Google accounts?",["Firebase Authentication","Cloud Storage","Remote Config","Test Lab"],"Firebase Authentication manages sign-in."),
 (2,"Which Firebase service stores user-uploaded files such as images?",["Cloud Storage for Firebase","Remote Config","Hosting rewrites","Analytics"],"Cloud Storage holds files and media."),
 (3,"What does Dart's sound null safety mean?",["Variables cannot be null unless declared nullable (for example String?)","Dart has no null value at all","Null is always converted to zero","Only strings can be null"],"Non-nullable by default catches null errors at compile time."),
 (2,"Which Android component represents a single screen with a user interface?",["Activity","Service","BroadcastReceiver","ContentProvider"],"An Activity hosts a screen."),
 (3,"In Kotlin, what does the Elvis operator ?: do?",["Returns the right side when the left side is null","Compares two strings","Declares a lambda","Casts an object"],"name ?: \"guest\" falls back when name is null."),
 (2,"What is the Android Emulator used for?",["Running and testing apps on virtual devices","Editing images","Hosting websites","Compressing videos"],"It simulates Android devices on your computer."),
 (3,"Which TensorFlow API is the high-level API for building and training models?",["Keras","Pandas","Flask","Jinja"],"tf.keras is the high-level model-building API."),
 (2,"In machine learning, overfitting means the model...",["Memorizes the training data and generalizes poorly","Has too few parameters to learn anything","Trains too quickly","Cannot use GPUs"],"It performs well on training data but poorly on new data."),
 (2,"What is Cloud Run used for?",["Running containerized apps without managing servers","Editing spreadsheets","Designing logos","Streaming music"],"Cloud Run is a serverless container platform."),
 (2,"What does PWA stand for?",["Progressive Web App","Primary Web API","Packaged Windows App","Protected Web Archive"],"PWAs are installable, offline-capable web apps."),
 (3,"What does CORS control in browsers?",["Which origins may request resources from another origin","CPU overclocking","The order of CSS rules","Image compression"],"Cross-Origin Resource Sharing is a browser security mechanism.")]
for d,q,o,e in G: hand('advanced','Python',d,'conceptual','Computer Science Fundamentals',q,'',o,e) if False else mk('advanced','General',d,'conceptual','Google Developer Tech',q,'',o[0],o[1:],e)
GIT=[(1,"Which Git command records a snapshot of staged changes?",["git commit","git clone","git fetch","git init"],"commit saves staged changes to history."),(1,"What does `git clone` do?",["Copies a remote repository to your machine","Deletes a branch","Merges two files","Creates a README"],"clone downloads a full repository."),
 (2,"What is a pull request?",["A request to merge your branch's changes into another branch","A command that downloads files","A way to delete a repo","A commit message format"],"Pull requests enable review before merging."),(1,"Which HTTP status code means 'Not Found'?",["404","200","500","301"],"404 = resource not found."),
 (2,"Which HTTP method is normally used to create a resource in a REST API?",["POST","GET","DELETE","HEAD"],"POST submits data to create something."),(1,"What does JSON stand for?",["JavaScript Object Notation","Java Standard Object Network","Joint Script Operation Node","JavaScript Online Network"],"A lightweight data format."),
 (1,"Which language structures the content of a web page?",["HTML","CSS","SQL","Bash"],"HTML defines elements and content."),(1,"Which language styles a web page?",["CSS","HTML","Python","C"],"CSS controls presentation."),(2,"What does API stand for?",["Application Programming Interface","Applied Program Integration","Automatic Page Index","Advanced Python Interpreter"],"An API defines how software talks to software."),
 (2,"What does GitHub Pages provide?",["Free static website hosting from a repository","A paid database","A mobile emulator","A C++ compiler"],"It publishes static sites straight from a repo."),(3,"How does `git rebase` differ from `git merge`?",["It re-applies commits on a new base, giving a linear history","It deletes remote branches","It squashes the whole repo","It encrypts commits"],"Rebase rewrites commits onto another base."),
 (2,"Which file tells Git which files to ignore?",[".gitignore","README.md","package.json","LICENSE"],".gitignore lists patterns Git skips."),(3,"What does HTTPS add on top of HTTP?",["Encryption with TLS","Faster CPUs","Larger images","Free hosting"],"TLS encrypts traffic between browser and server.")]
for d,q,o,e in GIT: mk('advanced','General',d,'conceptual','Computer Science Fundamentals',q,'',o[0],o[1:],e)
for _ in range(40):
    a,b = ri(5,60),ri(2,15); kind = pick(['&','|','^','<<','>>','bin','hex','dec'])
    if kind in '&|^': ex = f"{a} {kind} {b}"; qq = f"What is {ex} in Python (bitwise)?"; v = eval(ex)
    elif kind=='<<': ex = f"{b} << {ri(1,4)}"; qq = f"What is {ex}?"; v = eval(ex)
    elif kind=='>>': ex = f"{a} >> {ri(1,3)}"; qq = f"What is {ex}?"; v = eval(ex)
    elif kind=='bin': qq = f"What is the decimal value of binary {bin(a)[2:]}?"; v = a
    elif kind=='hex': qq = f"What is hex 0x{a:X} in decimal?"; v = a
    else: qq = f"What is decimal {a} in binary?"; v = bin(a)[2:]
    mk('advanced','Python',2 if kind in ('bin','hex','dec','>>') else 3,'logic','Computer Science Fundamentals',qq,'',str(v),[str(v+1) if isinstance(v,int) else bin(a+1)[2:],str(v-1) if isinstance(v,int) else bin(a^1)[2:],str(v*2) if isinstance(v,int) else bin(a+2)[2:]],f'The answer is {v}.')
# ---------------- merge with verified base questions & write ----------------
old = json.load(open('tools/base_questions_v1.json')); mp = dict(basics='python',loops='loops',data='data',oop='oop',algo='algo',debug='debug',mixed='advanced')
for q in old: q['topic'] = mp[q['topic']]; Q[q['topic']].append(q)
LEADS = ["GDG Assiut Study Jam:","DevFest Assiut challenge:","Hackathon judge asks:","GDG Assiut mentor's puzzle:","Workshop exercise at GDG Assiut:","Lightning-talk puzzle:","Community code review:","Build Night at GDG Assiut:","GDG Assiut bootcamp:","Code Man arena:"]
BUGLEADS = ["Bug Bash at GDG Assiut:","GDG Assiut debugging booth:","Community code review:","Hackathon bug hunt:"]
for lst in Q.values():
    for q in lst:
        if q['type'] in ('output','bug','fix','fill','arrange','complexity','logic','algorithm') and R.random() < .85 and not q['question'].startswith(tuple(LEADS+BUGLEADS)):
            q['question'] = pick(BUGLEADS if q['type'] in ('bug','fix') else LEADS) + ' ' + q['question']
files = dict(python='python',loops='loops',data='data-structures',oop='oop',algo='algorithms',debug='debugging',advanced='advanced')
total = 0; types = {}
for t, lst in Q.items():
    ids = [q['id'] for q in lst]; assert len(set(ids)) == len(ids), t
    for q in lst:
        types[q['type']] = types.get(q['type'],0)+1
        if q['type'] != 'arrange': assert 0 <= q['correctAnswer'] < len(q['options']) and len(set(q['options'])) == len(q['options']), q['id']
    json.dump(lst, open(f"data/questions/{files[t]}.json",'w'), indent=1, ensure_ascii=False); total += len(lst); print(t, len(lst))
print('TOTAL', total, types)
