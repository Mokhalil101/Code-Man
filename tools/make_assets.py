# Generates all original pixel-art sprites (PNG) and chiptune audio (WAV).  Run from project root:  python3 tools/make_assets.py
from PIL import Image, ImageDraw
import numpy as np, wave, random
CLR=(0,0,0,0); W=(255,255,255,255); K=(0,0,0,255)
BL=(66,133,244,255); RD=(234,67,53,255); YL=(251,188,4,255); GR=(52,168,83,255); PU=(161,66,244,255)
def new(n=16): return Image.new('RGBA',(n,n),CLR)
def D(im): return ImageDraw.Draw(im)
def save(im,name,s=2): im.resize((im.width*s,im.height*s),Image.NEAREST).save(f'assets/sprites/{name}.png')
def dark(c,f=.6): return (int(c[0]*f),int(c[1]*f),int(c[2]*f),255)
G={'U':["101","101","101","101","111"],'S':["111","100","111","001","111"],'D':["110","101","101","101","110"],'M':["101","111","111","101","101"],
   'K':["101","101","110","101","101"],'L':["100","100","100","100","111"],'?':["111","001","011","000","010"]}
def glyph(d,ch,x,y,col):
    for j,row in enumerate(G[ch]):
        for i,v in enumerate(row):
            if v=='1': d.point((x+i,y+j),fill=col)
# ---- player: blue developer bot (2 chomp frames)
for k,mouth in enumerate([True,False]):
    im=new();d=D(im);d.ellipse([1,1,14,14],fill=BL,outline=dark(BL,.7))
    if mouth: d.polygon([(8,8),(16,2),(16,14)],fill=CLR)
    d.rectangle([7,3,9,4],fill=W); d.point((9,3),fill=K); d.point((4,10),fill=YL); save(im,f'pac{k}')
# ---- enemies: four bug species (Google colours) + frightened + eyes
def bug(col,name):
    im=new();d=D(im);d.ellipse([3,5,12,14],fill=col);d.ellipse([4,1,11,7],fill=col)
    for y in (7,10,13): d.line([(0,y),(3,y+1)],fill=col);d.line([(12,y+1),(15,y)],fill=col)
    d.line([(5,1),(3,0)],fill=col);d.line([(10,1),(12,0)],fill=col);d.line([(8,7),(8,13)],fill=dark(col))
    d.rectangle([5,3,6,4],fill=W);d.rectangle([9,3,10,4],fill=W);d.point((6,4),fill=K);d.point((9,4),fill=K);save(im,name)
for i,c in enumerate([RD,YL,GR,PU]): bug(c,f'bug{i}')
bug((170,200,255,255),'scared'); im=Image.open('assets/sprites/scared.png'); d=D(im)
for x in (10,22): d.line([(x,8),(x+4,12)],fill=K,width=2);d.line([(x,12),(x+4,8)],fill=K,width=2)
im.save('assets/sprites/scared.png')
im=new();d=D(im);[d.rectangle([x,4,x+2,7],fill=W) or d.rectangle([x+1,5,x+2,7],fill=BL) for x in (4,9)];save(im,'eyes')
# ---- collectibles / props
im=new();d=D(im);d.ellipse([6,6,9,9],fill=YL);d.point((7,7),fill=W);save(im,'bit')
im=new();d=D(im);d.ellipse([2,2,13,13],fill=YL,outline=W);d.rectangle([7,5,8,10],fill=dark(YL,.5));save(im,'chip')
im=new();d=D(im);d.ellipse([3,3,12,12],fill=GR,outline=W);d.ellipse([6,5,8,7],fill=W);save(im,'orb')
im=new();d=D(im);d.polygon([(8,0),(10,6),(16,6),(11,9),(13,15),(8,11),(3,15),(5,9),(0,6),(6,6)],fill=YL,outline=W);save(im,'secret')
for ch,col in [('U',BL),('S',GR),('D',(108,140,255,255)),('M',(255,155,255,255)),('K',YL),('L',PU)]:
    im=new();d=D(im);d.rounded_rectangle([1,1,14,14],radius=3,fill=col,outline=W);glyph(d,ch,6,5,K);save(im,'pu_'+ch)
im=new();d=D(im);d.rounded_rectangle([2,2,13,13],radius=2,fill=PU,outline=W);glyph(d,'?',6,5,W);save(im,'quiz')
for k,col in [(0,(85,95,115,255)),(1,GR)]:
    im=new();d=D(im);d.rectangle([3,1,12,14],fill=col,outline=W);d.rectangle([5,3,10,12],outline=(0,0,0,120));d.point((10,8),fill=W);save(im,f'exit{k}')
im=new();d=D(im);d.ellipse([1,1,14,14],outline=GR,width=2);d.polygon([(11,0),(15,3),(11,6)],fill=GR);d.ellipse([6,6,9,9],fill=RD);save(im,'hazard')
r=random.Random(3);im=Image.new('RGBA',(16,16),(40,0,10,255));d=D(im)
for _ in range(40):
    x0,y0=r.randint(0,12),r.randint(0,14); d.rectangle([x0,y0,x0+r.randint(0,3),y0+r.randint(0,1)],fill=(234,67,53,r.randint(60,200)))
save(im,'corrupt')
# ---- world wall tiles
for i,c in enumerate([BL,GR,PU,RD,YL,(255,112,67,255),(0,229,255,255)],1):
    im=Image.new('RGBA',(16,16),dark(c,.22));d=D(im);d.rectangle([0,0,15,15],outline=c);d.rectangle([2,2,13,13],outline=dark(c,.45))
    d.point((4,4),fill=c);d.point((11,11),fill=c); save(im,f'wall{i}')
# ---- seven bosses (20x20 pixel art, shown at 2x)
def boss(i):
    im=new(20);d=D(im)
    if i==1: d.rectangle([3,3,16,16],fill=(90,110,230,255),outline=W);[d.polygon([(4,y),(7,y+2),(4,y+4)],fill=YL) for y in (5,11)];d.rectangle([9,6,10,8],fill=W);d.rectangle([13,6,14,8],fill=W);d.rectangle([8,13,15,14],fill=K)
    if i==2: d.ellipse([1,1,18,18],outline=GR,width=3);d.polygon([(14,0),(19,4),(14,8)],fill=GR);d.ellipse([7,7,12,12],fill=RD,outline=W);d.point((9,9),fill=K)
    if i==3: d.ellipse([2,3,17,17],fill=BL,outline=W);d.rectangle([4,11,15,15],fill=K);[d.polygon([(x,11),(x+1,14),(x+2,11)],fill=W) for x in range(4,15,3)];d.rectangle([5,5,7,7],fill=W);d.rectangle([12,5,14,7],fill=W);d.rectangle([8,0,11,2],fill=YL)
    if i==4: d.rectangle([3,5,16,18],fill=(200,60,50,255),outline=W);[d.rectangle([x,1,x+2,5],fill=(200,60,50,255),outline=W) for x in (3,8,13)];d.line([(5,8),(8,10)],fill=W,width=2);d.line([(14,8),(11,10)],fill=W,width=2);d.rectangle([7,14,12,16],fill=K)
    if i==5: d.ellipse([2,3,17,18],fill=(255,150,30,255),outline=W);d.polygon([(2,5),(5,0),(7,5)],fill=YL);d.polygon([(17,5),(14,0),(12,5)],fill=YL);d.rectangle([5,8,7,10],fill=W);d.rectangle([12,8,14,10],fill=W);d.ellipse([7,12,12,17],fill=K)
    if i==6: d.polygon([(10,0),(18,8),(16,19),(4,19),(2,8)],fill=(40,30,60,255),outline=(120,100,160,255));d.rectangle([6,8,8,10],fill=RD);d.rectangle([12,8,14,10],fill=RD);d.line([(17,2),(17,18)],fill=(180,180,190,255),width=1)
    if i==7:
        d.ellipse([4,4,15,15],fill=(30,30,50,255),outline=W)
        for a,b,c in [(9,0,BL),(9,17,RD),(0,9,YL),(17,9,GR),(2,2,PU),(15,2,BL),(2,15,RD),(15,15,YL)]: d.rectangle([a,b,a+2,b+2],fill=c)
        d.ellipse([7,7,12,12],fill=(0,229,255,255));d.point((9,9),fill=W)
    save(im,f'boss{i}')
for i in range(1,8): boss(i)
# =============== AUDIO ===============
SR=16000
def tone(f,dur,kind='square',vol=.3,slide=0):
    t=np.linspace(0,dur,int(SR*dur),False);ph=2*np.pi*np.cumsum(f+slide*t/dur)/SR
    w=np.sign(np.sin(ph)) if kind=='square' else (np.sin(ph) if kind=='sine' else 2*((ph/(2*np.pi))%1)-1)
    return w*np.clip((dur-t)/dur*3,0,1)*vol
def seq(fs,dur,**k): return np.concatenate([tone(f,dur,**k) for f in fs])
def noise(dur,vol=.2,lp=1):
    n=np.random.RandomState(1).uniform(-1,1,int(SR*dur));env=np.linspace(1,0,len(n))**lp;return n*env*vol
def wav(name,a):
    a=a/max(1,np.abs(a).max())*.8
    with wave.open(f'assets/audio/{name}.wav','wb') as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((a*32767).astype('<i2').tobytes())
n=lambda m:440*2**((m-69)/12)
sfx={'click':tone(900,.04,vol=.25),'bit':tone(660,.04,vol=.2),'bonus':seq([880,1175,1568],.06),'orb':seq([523,784],.07,kind='sine'),'secret':seq([784,988,1175,1568],.07),
 'power':tone(300,.3,'saw',.25,700),'expire':tone(500,.25,'sine',.3,-300),'squash':seq([200,400],.08),'hit':tone(300,.45,'saw',.3,-240),
 'good':seq([660,880,1320],.07),'bad':np.concatenate([tone(200,.12,slide=-80),tone(150,.22)]),'teleport':tone(1200,.3,'sine',.3,-900),
 'bosshit':np.concatenate([tone(120,.2,'saw',.4),noise(.2,.3)]),'win':seq([523,659,784,1047,1319],.12),'jingle':seq([392,523,659,784,1047],.09,vol=.3),
 'over':seq([392,330,262,196],.22,kind='saw',vol=.25)}
for k,v in sfx.items(): wav('s_'+k,v)
def music(root,scale,bpm,wave_,seed,bass_pat=(0,0,3,4),drums=True,steps=32,rest=.15):
    r=random.Random(seed);sd=60/bpm/2;idx=3;lead=[];low=[]
    for s in range(steps):
        idx=max(0,min(len(scale)-1,idx+r.choice([-2,-1,-1,0,1,1,2])))
        lead.append(tone(n(root+12+scale[idx]),sd,wave_,.1) if r.random()>rest else np.zeros(int(SR*sd)))
        bass=bass_pat[(s//8)%len(bass_pat)]
        if s%4==0: low.append(tone(n(root-12+scale[bass%len(scale)]),sd*4,'sine',.28))
        if drums:
            kick=tone(110,sd,'sine',.35,-70) if s%4==0 else (np.zeros(int(SR*sd)))
            hat=noise(sd*.5,.07,3) if s%2==1 else np.zeros(int(SR*sd*.5))
            lead[-1]=lead[-1]+kick+np.pad(hat,(0,len(lead[-1])-len(hat)))
    L=np.concatenate(lead);B=np.concatenate(low);m=min(len(L),len(B));return L[:m]+B[:m]
MAJ=[0,2,4,7,9,12];MIX=[0,2,4,5,7,9,10];MIN=[0,2,3,5,7,8,10];DOR=[0,2,3,5,7,9,10];HM=[0,2,3,5,7,8,11];LOC=[0,1,3,5,6,8,10]
tr={'m_menu':(60,MAJ,100,'square',1,(0,3,4,0),True),'m_w1':(60,MAJ,112,'square',2,(0,0,3,4),True),'m_w2':(55,MIX,124,'saw',3,(0,3,4,0),True),
 'm_w3':(57,MIN,90,'square',4,(0,5,3,4),True),'m_w4':(50,DOR,104,'saw',5,(0,4,3,0),True),'m_w5':(52,MIN,138,'square',6,(0,3,5,4),True),
 'm_w6':(54,LOC,118,'saw',7,(0,1,3,1),True),'m_w7':(48,HM,128,'square',8,(0,5,4,3),True),'m_boss':(45,HM,156,'saw',9,(0,0,1,0),True)}
for k,(rt,sc,bpm,wv,sd,bp,dr) in tr.items(): wav(k,music(rt,sc,bpm,wv,sd,bp,dr,rest=.1 if k=='m_boss' else .18))
wav('m_win',np.concatenate([seq([523,659,784,1047,784,1047,1319,1568],.16,vol=.3),tone(1047,.6,vol=.3)])); wav('m_over',seq([392,349,330,294,262,196],.28,kind='saw',vol=.25))
print('assets ok')
