# Generates all original sprites (PNG) and chiptune audio (WAV).  Run from project root:  python3 tools/make_assets.py
#   python3 tools/make_assets.py sprites   -> regenerate only the sprites (audio untouched)
# Sprite style: "sticker arcade" -- chunky cartoon shapes, thick ink outlines (#1B1340), big eyes.
# Every sprite is drawn 4x supersampled and downscaled (smooth edges). Sprites are 64x64 (bosses 80x80) and are
# shown at half size in the game, whose camera renders at 2x, so they stay crisp on big screens.
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, wave, random, sys
ONLY_SPRITES = 'sprites' in sys.argv[1:]
SS = 4
INK = (27, 19, 64, 255); INK2 = (12, 7, 38, 255); CREAM = (255, 246, 224, 255); W = (255, 255, 255, 255)
BL = (66, 133, 244, 255); RD = (234, 67, 53, 255); YL = (251, 188, 4, 255); GR = (52, 168, 83, 255); PU = (161, 66, 244, 255)
PINK = (255, 143, 177, 255); TEAL = (18, 181, 203, 255); ORANGE = (255, 138, 40, 255)
def rgba(c, a): return (c[0], c[1], c[2], a)
def font(px):
    for f in ('segoeuib.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf', 'C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        try: return ImageFont.truetype(f, int(px * SS))
        except Exception: pass
    return ImageFont.load_default(size=int(px * SS))
class Pen:
    """ImageDraw wrapper that takes coordinates in final-pixel units and scales them by SS."""
    def __init__(self, im): self.d = ImageDraw.Draw(im)
    @staticmethod
    def b(box): return [v * SS for v in box]
    def ellipse(self, box, fill): self.d.ellipse(self.b(box), fill=fill)
    def rect(self, box, fill): self.d.rectangle(self.b(box), fill=fill)
    def rrect(self, box, r, fill): self.d.rounded_rectangle(self.b(box), radius=r * SS, fill=fill)
    def poly(self, pts, fill): self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)
    def pie(self, box, a0, a1, fill): self.d.pieslice(self.b(box), a0, a1, fill=fill)
    def chord(self, box, a0, a1, fill): self.d.chord(self.b(box), a0, a1, fill=fill)
    def line(self, pts, w, fill):
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=int(w * SS), joint='curve')
        for x, y in (pts[0], pts[-1]): r = w * SS / 2; self.d.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], fill=fill)
    def text(self, xy, s, px, fill, stroke=0, stroke_fill=None):
        self.d.text((xy[0] * SS, xy[1] * SS), s, font=font(px), fill=fill, anchor='mm', stroke_width=int(stroke * SS), stroke_fill=stroke_fill)
class Sprite:
    def __init__(self, n): self.n = n; self.im = Image.new('RGBA', (n * SS, n * SS), (0, 0, 0, 0))
    def _mask(self, fn):
        m = Image.new('L', self.im.size, 0); fn(Pen(m)); return np.array(m) > 127
    @staticmethod
    def dilate(mask, r):
        r = r * SS; ri = int(np.ceil(r)); H, Wd = mask.shape; pad = np.pad(mask, ri); out = np.zeros_like(mask)
        for dy in range(-ri, ri + 1):
            for dx in range(-ri, ri + 1):
                if dx * dx + dy * dy <= r * r: out |= pad[ri + dy:ri + dy + H, ri + dx:ri + dx + Wd]
        return out
    def paint(self, mask, color):
        layer = Image.new('RGBA', self.im.size, color); a = Image.fromarray((mask * (color[3])).astype(np.uint8), 'L')
        layer.putalpha(a); self.im.alpha_composite(layer)
    def blob(self, fn, fill, ow=3.5, shadow=0, ink=INK):
        """Draw a filled shape with a thick ink outline (and an optional hard drop shadow). Returns the fill mask."""
        mask = self._mask(fn); outer = self.dilate(mask, ow) if ow else mask
        if shadow:
            s = int(shadow * SS); sh = np.zeros_like(outer); sh[s:, :] = outer[:-s, :]; self.paint(sh & ~outer, INK2)
        if ow: self.paint(outer, ink)
        self.paint(mask, fill); return mask
    def clip(self, mask, fn):
        """Draw fn on a temp layer, keep only the pixels inside mask (shines / shades)."""
        layer = Image.new('RGBA', self.im.size, (0, 0, 0, 0)); fn(Pen(layer))
        a = np.array(layer.getchannel('A')).astype(np.float32) * mask; layer.putalpha(Image.fromarray(a.astype(np.uint8), 'L')); self.im.alpha_composite(layer)
    def glow(self, fn, color, radius=6, strength=1.0):
        layer = Image.new('RGBA', self.im.size, (0, 0, 0, 0)); fn(Pen(layer), color)
        g = layer.filter(ImageFilter.GaussianBlur(radius * SS)); a = np.clip(np.array(g.getchannel('A')).astype(np.float32) * strength, 0, 255)
        g.putalpha(Image.fromarray(a.astype(np.uint8), 'L')); self.im.alpha_composite(g)
    def draw(self, fn): fn(Pen(self.im))
    def save(self, name): self.im.resize((self.n, self.n), Image.LANCZOS).save(f'assets/sprites/{name}.png')
def eye(s, box, look=(0, 0), pupil=0.42, ow=2.5, iris=None):
    """Big cartoon eye: white ball, ink outline, pupil shifted by look (-1..1)."""
    x0, y0, x1, y1 = box; s.blob(lambda p: p.ellipse(box, 255), W, ow)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; rw, rh = (x1 - x0) / 2, (y1 - y0) / 2; r = min(rw, rh) * pupil
    px, py = cx + look[0] * (rw - r - 1), cy + look[1] * (rh - r - 1)
    if iris: ri = r * 1.55; s.draw(lambda p: p.ellipse([px - ri, py - ri, px + ri, py + ri], iris))
    s.draw(lambda p: (p.ellipse([px - r, py - r, px + r, py + r], INK), p.ellipse([px - r * .9 + r * .2, py - r * .9, px - r * .1 + r * .2, py - r * .1], W)))
def shine(s, mask, box):
    s.clip(mask, lambda p: p.ellipse(box, (255, 255, 255, 105)))
# ---------------- player: Code-Man (2 chomp frames) ----------------
for k, half in enumerate([36, 7]):
    s = Sprite(64); m = s.blob(lambda p: p.pie([7, 7, 57, 57], half, 360 - half, 255), BL, 3.5)
    s.clip(m, lambda p: p.ellipse([4, 34, 60, 66], (0, 0, 0, 40)))           # soft shade on the lower half
    shine(s, m, [13, 11, 27, 21])
    s.draw(lambda p: p.ellipse([15, 36, 25, 42], rgba(PINK, 210)))           # blush
    eye(s, [26, 8, 41, 23], look=(.5, -.1))
    s.save(f'pac{k}')
# ---------------- bugs (Syntax red, Logic yellow, Runtime green, Memory pink) ----------------
def bug_body(p, f):
    p.ellipse([8, 8, 56, 50], f); p.rrect([8, 28, 56, 57], 9, f)
def bug(col, name, scared=False):
    s = Sprite(64)
    s.draw(lambda p: (p.line([(10, 42), (2, 48)], 3.5, INK), p.line([(54, 42), (62, 48)], 3.5, INK), p.line([(10, 33), (2, 34)], 3.5, INK), p.line([(54, 33), (62, 34)], 3.5, INK),
                      p.line([(23, 12), (17, 3)], 3.5, INK), p.line([(41, 12), (47, 3)], 3.5, INK)))
    for cx in (17, 47): s.blob(lambda p, cx=cx: p.ellipse([cx - 3.5, -0.5, cx + 3.5, 6.5], 255), col, 2.5)
    m = s.blob(lambda p: bug_body(p, 255), col, 3.5)
    s.clip(m, lambda p: p.rect([0, 50, 64, 64], (0, 0, 0, 45)))
    shine(s, m, [13, 12, 25, 20])
    if scared:
        s.draw(lambda p: (p.rrect([18, 22, 26, 31], 3, W), p.rrect([38, 22, 46, 31], 3, W)))
        s.draw(lambda p: p.line([(16, 45), (21, 40), (27, 45), (32, 40), (37, 45), (43, 40), (48, 45)], 3, W))
    else:
        eye(s, [14, 17, 30, 35], look=(-.45, .35)); eye(s, [34, 17, 50, 35], look=(-.45, .35))
        s.draw(lambda p: p.chord([25, 36, 39, 50], 0, 180, INK))
        s.draw(lambda p: p.rect([29, 43, 32, 46], W))
    s.save(name)
for i, c in enumerate([RD, YL, GR, PINK]): bug(c, f'bug{i}')
bug((132, 150, 255, 255), 'scared', scared=True)
s = Sprite(64); eye(s, [14, 17, 30, 35], look=(0, .4), iris=BL); eye(s, [34, 17, 50, 35], look=(0, .4), iris=BL); s.save('eyes')
# ---------------- collectibles ----------------
s = Sprite(64); s.glow(lambda p, c: p.rrect([23, 23, 41, 41], 6, c), YL, 5, 1.6)
s.draw(lambda p: (p.rrect([24, 24, 40, 40], 5, YL), p.rrect([27, 26, 37, 34], 3, (255, 222, 120, 255)), p.ellipse([27, 26, 31, 30], W))); s.save('bit')
s = Sprite(64); s.glow(lambda p, c: p.ellipse([12, 12, 52, 52], c), YL, 6, 1.3)
m = s.blob(lambda p: p.ellipse([12, 12, 52, 52], 255), YL, 3.5); shine(s, m, [18, 15, 32, 24])
s.draw(lambda p: p.text((32, 33), '</>', 15, INK, .4, INK)); s.save('chip')
s = Sprite(64); s.glow(lambda p, c: p.ellipse([15, 15, 49, 49], c), GR, 5, 1.1)
m = s.blob(lambda p: p.ellipse([15, 15, 49, 49], 255), GR, 3.5); shine(s, m, [20, 18, 32, 26])
s.draw(lambda p: p.text((32, 33.5), 'XP', 13, W, .8, INK)); s.save('orb')
def star_pts(cx, cy, ro, ri, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        a = np.radians(rot + i * 180 / n); r = ro if i % 2 == 0 else ri; pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return pts
s = Sprite(64); s.glow(lambda p, c: p.poly(star_pts(32, 34, 26, 12), c), YL, 5, 1.0)
m = s.blob(lambda p: p.poly(star_pts(32, 34, 25, 11.5), 255), YL, 3.5); shine(s, m, [24, 14, 34, 26]); s.save('secret')
# ---------------- power-ups and quiz node: chunky stickers with a hard shadow ----------------
for ch, col, fg in [('U', BL, W), ('S', GR, W), ('D', (138, 180, 248, 255), INK), ('M', PINK, INK), ('K', YL, INK), ('L', TEAL, W)]:
    s = Sprite(64); m = s.blob(lambda p: p.rrect([9, 7, 55, 51], 13, 255), col, 3.5, shadow=4)
    s.clip(m, lambda p: p.rect([0, 7, 64, 13], (255, 255, 255, 90))); s.clip(m, lambda p: p.rect([0, 45, 64, 51], (0, 0, 0, 45)))
    s.draw(lambda p: p.text((32, 30), ch, 27, fg, 1 if fg == W else 0, INK)); s.save('pu_' + ch)
s = Sprite(64); m = s.blob(lambda p: p.rrect([9, 7, 55, 51], 14, 255), PU, 3.5, shadow=4)
s.clip(m, lambda p: p.rect([0, 7, 64, 13], (255, 255, 255, 90))); s.clip(m, lambda p: p.rect([0, 45, 64, 51], (0, 0, 0, 50)))
s.draw(lambda p: p.text((32, 30), '?', 32, W, 1, INK)); s.save('quiz')
# ---------------- exit gate (locked / open) ----------------
def arch(p, f, inset=0):
    i = inset; p.ellipse([11 + i, 4 + i, 53 - i, 46 - i], f); p.rect([11 + i, 25, 53 - i, 59 - i], f)
for k in (0, 1):
    s = Sprite(64)
    if k: s.glow(lambda p, c: arch(p, c), GR, 7, 1.4)
    m = s.blob(lambda p: arch(p, 255), GR if k else (118, 104, 178, 255), 3.5)
    s.draw(lambda p: arch(p, (25, 110, 55, 255) if k else (66, 54, 118, 255), 8))
    if k: s.draw(lambda p: (p.line([(24, 38), (32, 30), (40, 38)], 4, W), p.line([(24, 49), (32, 41), (40, 49)], 4, W)))
    else:
        s.draw(lambda p: (p.d.arc(Pen.b([25, 23, 39, 41]), 180, 360, fill=INK, width=4 * SS), p.rect([25, 31, 29, 36], INK), p.rect([35, 31, 39, 36], INK)))
        s.blob(lambda p: p.rrect([22, 34, 42, 50], 4, 255), YL, 2.5)
        s.draw(lambda p: p.ellipse([30, 39, 34, 43], INK))
    shine(s, m, [17, 8, 29, 16]); s.save(f'exit{k}')
# ---------------- hazard (World 2 looping saw) and corrupted tile (World 6) ----------------
s = Sprite(64); m = s.blob(lambda p: p.poly(star_pts(32, 32, 29, 20, 10, 0), 255), RD, 3)
s.blob(lambda p: p.ellipse([22, 22, 42, 42], 255), YL, 3); s.draw(lambda p: p.ellipse([28, 28, 36, 36], INK)); shine(s, m, [14, 12, 28, 22]); s.save('hazard')
s = Sprite(64); m = s.blob(lambda p: p.rrect([4, 4, 60, 60], 12, 255), (92, 14, 44, 255), 3)
def stripes(p):
    for x in range(-64, 96, 16): p.poly([(x, 64), (x + 8, 64), (x + 72, 0), (x + 64, 0)], (234, 67, 53, 255))
s.clip(m, stripes); r = random.Random(3)
for _ in range(9):
    x0, y0 = r.randint(8, 48), r.randint(8, 52); s.clip(m, lambda p, x0=x0, y0=y0: p.rect([x0, y0, x0 + r.randint(4, 10), y0 + 3], (255, 143, 177, 230)))
s.save('corrupt')
# ---------------- wall tiles (kept for completeness; the maze itself is drawn as joined candy shapes in GameScene) ----------------
for i, c in enumerate([BL, GR, PU, RD, YL, (255, 112, 67, 255), (0, 229, 255, 255)], 1):
    s = Sprite(64); m = s.blob(lambda p: p.rrect([3, 3, 61, 61], 12, 255), c, 3)
    s.clip(m, lambda p: p.rect([0, 3, 64, 12], (255, 255, 255, 90))); s.clip(m, lambda p: p.rect([0, 52, 64, 61], (0, 0, 0, 46))); s.save(f'wall{i}')
# ---------------- seven bosses (80x80) ----------------
def brows(s, l, r, w=4):
    s.draw(lambda p: (p.line(l, w, INK), p.line(r, w, INK)))
def teeth_mouth(s, box, n=4, rows=1):
    x0, y0, x1, y1 = box; s.blob(lambda p: p.rrect(box, (y1 - y0) / 2.2, 255), INK, 0)
    tw = (x1 - x0 - 6) / n
    for i in range(n):
        tx = x0 + 3 + i * tw; s.draw(lambda p, tx=tx: p.poly([(tx, y0 + 1), (tx + tw, y0 + 1), (tx + tw / 2, y0 + (y1 - y0) * .55)], W))
        if rows > 1: s.draw(lambda p, tx=tx: p.poly([(tx, y1 - 1), (tx + tw, y1 - 1), (tx + tw / 2, y1 - (y1 - y0) * .5)], W))
def boss(i):
    s = Sprite(80)
    if i == 1:   # The Indentation Monster: a blue block with tab-arrows
        for y in (24, 46): s.blob(lambda p, y=y: p.poly([(2, y - 8), (14, y), (2, y + 8)], 255), YL, 3)
        m = s.blob(lambda p: p.rrect([11, 12, 71, 72], 16, 255), BL, 4); shine(s, m, [18, 16, 36, 26])
        eye(s, [20, 24, 38, 44], look=(.2, .3)); eye(s, [44, 24, 62, 44], look=(-.2, .3)); brows(s, [(20, 20), (36, 25)], [(62, 20), (46, 25)])
        teeth_mouth(s, [24, 52, 58, 64], 5)
    if i == 2:   # Infinite Loop: a green ring with an arrow and one big eye
        m = s.blob(lambda p: (p.ellipse([6, 8, 74, 76], 255), p.ellipse([24, 26, 56, 58], 0)), GR, 4)
        s.blob(lambda p: p.poly([(54, 2), (76, 12), (58, 26)], 255), GR, 3.5); shine(s, m, [14, 14, 30, 24])
        eye(s, [27, 29, 53, 55], look=(0, .2), pupil=.3, iris=RD, ow=3)
    if i == 3:   # The Memory Eater: a purple chomper with a RAM-chip crown
        s.blob(lambda p: p.rect([24, 2, 56, 13], 255), GR, 3); s.draw(lambda p: [p.rect([x, 5, x + 3, 10], YL) for x in (28, 35, 42, 49)])
        m = s.blob(lambda p: p.ellipse([6, 10, 74, 76], 255), PU, 4); shine(s, m, [14, 16, 32, 26])
        eye(s, [20, 18, 36, 34], look=(.2, .2)); eye(s, [44, 18, 60, 34], look=(-.2, .2))
        teeth_mouth(s, [16, 40, 64, 66], 6, 2)
    if i == 4:   # The Class Destroyer: an angry red castle tower
        m = s.blob(lambda p: (p.rrect([12, 18, 68, 76], 8, 255), p.rect([12, 6, 25, 22], 255), p.rect([34, 6, 47, 22], 255), p.rect([55, 6, 68, 22], 255)), RD, 4)
        shine(s, m, [16, 22, 32, 30]); s.clip(m, lambda p: p.rect([0, 66, 80, 80], (0, 0, 0, 50)))
        eye(s, [20, 30, 37, 48], look=(.3, .3)); eye(s, [43, 30, 60, 48], look=(-.3, .3)); brows(s, [(19, 27), (37, 33)], [(61, 27), (43, 33)], 4.5)
        s.blob(lambda p: p.chord([26, 54, 54, 76], 180, 360, 255), INK, 0)
    if i == 5:   # The Complexity Beast: an orange horned beast
        for pts in ([(14, 22), (6, 0), (28, 14)], [(66, 22), (74, 0), (52, 14)]): s.blob(lambda p, pts=pts: p.poly(pts, 255), YL, 3)
        m = s.blob(lambda p: p.ellipse([8, 12, 72, 76], 255), ORANGE, 4); shine(s, m, [16, 18, 32, 28])
        eye(s, [20, 26, 37, 43], look=(.2, .2)); eye(s, [43, 26, 60, 43], look=(-.2, .2)); brows(s, [(20, 23), (36, 28)], [(60, 23), (44, 28)])
        teeth_mouth(s, [24, 50, 56, 66], 4, 2)
    if i == 6:   # The Runtime Reaper: a hooded reaper with a scythe
        s.draw(lambda p: p.line([(70, 10), (66, 78)], 4, INK)); s.blob(lambda p: p.poly([(60, 6), (79, 10), (78, 26), (70, 14)], 255), (200, 205, 220, 255), 2.5)
        m = s.blob(lambda p: p.poly([(40, 3), (66, 22), (68, 77), (12, 77), (14, 22)], 255), (70, 50, 110, 255), 4)
        s.draw(lambda p: p.ellipse([22, 24, 58, 60], INK)); shine(s, m, [22, 8, 36, 16])
        s.glow(lambda p, c: (p.ellipse([28, 36, 37, 45], c), p.ellipse([43, 36, 52, 45], c)), RD, 4, 2)
        s.draw(lambda p: (p.ellipse([28, 36, 37, 45], RD), p.ellipse([43, 36, 52, 45], RD), p.ellipse([30, 37, 33, 40], W), p.ellipse([45, 37, 48, 40], W)))
    if i == 7:   # CORE VIRUS: a dark core with eight coloured spikes and a cyan eye
        cols = [BL, RD, YL, GR, BL, RD, YL, GR]
        for k in range(8):
            a = np.radians(k * 45 - 90); x, y = 40 + 34 * np.cos(a), 40 + 34 * np.sin(a)
            s.draw(lambda p, x=x, y=y: p.line([(40, 40), (x, y)], 8, INK))
            s.blob(lambda p, x=x, y=y: p.ellipse([x - 6, y - 6, x + 6, y + 6], 255), cols[k], 3)
        m = s.blob(lambda p: p.ellipse([14, 14, 66, 66], 255), (52, 40, 92, 255), 4); shine(s, m, [22, 18, 36, 27])
        s.glow(lambda p, c: p.ellipse([26, 26, 54, 54], c), (0, 229, 255, 255), 5, 1.2)
        eye(s, [24, 24, 56, 56], look=(0, .15), pupil=.3, iris=(0, 229, 255, 255), ow=3); brows(s, [(22, 22), (38, 28)], [(58, 22), (42, 28)], 4.5)
    s.save(f'boss{i}')
for i in range(1, 8): boss(i)
print('sprites ok')
if ONLY_SPRITES: sys.exit(0)
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
