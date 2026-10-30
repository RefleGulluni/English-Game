"""Lexicon sky, round 2 sketches (after D-088 round 1): regions laid out like a real sky along a
faint milky way, each region's ink wash shaped by its meaning, built up in four states, and the
bookmarks as hand-drawn marks in the page margin. Run from the repo root."""
import math, random, sys
from PIL import Image, ImageDraw, ImageFont
sys.argv = [sys.argv[0]]
exec(open('scripts/tools/sketch_lexicon_sky.py').read().split("ST={")[0])  # base(), blank(), up(), text() ...

CJK = '/System/Library/Fonts/Hiragino Sans GB.ttc'
PEN = (78, 58, 44)
OUT = 'docs/reference/lexicon_sky/round2/'
import os; os.makedirs(OUT, exist_ok=True)

def h(*a):
    return (hash(a) & 0xffffffff) / 0xffffffff
def vnoise(x, y, seed, scale):
    x /= scale; y /= scale
    x0, y0 = math.floor(x), math.floor(y); fx, fy = x - x0, y - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b, c, d = h(x0, y0, seed), h(x0 + 1, y0, seed), h(x0, y0 + 1, seed), h(x0 + 1, y0 + 1, seed)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

def seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay; t = max(0, min(1, ((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy)))
    return math.hypot(px - ax - t * vx, py - ay - t * vy)

TREE = [(0, 0.9, 0, -0.1), (0, 0.2, -0.6, -0.5), (0, 0.0, 0.55, -0.6), (-0.35, -0.3, -0.5, -0.9), (0.3, -0.35, 0.75, -0.2), (0, -0.1, 0.05, -0.85)]

def shape(kind, dx, dy, seed):
    """-> (v, density multiplier, hole): v < 1 is inside."""
    d = math.hypot(dx, dy); a = math.atan2(dy, dx); mult = 1.0
    if kind == 'Breaking':
        tri = abs(((a * 7 / math.tau + seed) % 1) - 0.5) * 2
        v = d / (0.72 + 0.38 * tri)
    elif kind == 'Holding':
        v = abs(d - 0.66) / 0.3
        if -2.0 < a < -1.15: v = 9  # the ring is not quite closed
    elif kind == 'Seeing':
        v = math.hypot(dx / 1.7, dy / 0.72)
        if math.hypot(dx / 0.55, dy / 0.42) < 1: return v, 0, True
    elif kind == 'Death':
        width = 0.45 + 0.8 * max(0, min(1, (dy + 1) / 1.6))  # narrow above, heavy and wide below: a drop
        v = math.hypot(dx / width, (dy - 0.1) / 1.05); mult = max(0.2, min(1, 0.25 + 0.8 * (dy + 1) / 2)) ** 1.5
    elif kind == 'Feeling':
        v = math.hypot(dx / 1.35, dy) * 0.95; mult = max(0, 1 - v) ** 0.5 * 1.3
    elif kind == 'Sound':
        v = d * 0.95
        if math.sin(d * 9.5) < -0.1: return v, 0, True  # the gaps between the rings
    elif kind == 'Light':
        ray = 1 if math.cos(7 * a + seed) > 0.7 else 0
        v = d / (0.55 + 0.6 * ray)  # a small core, long rays
        if d < 0.28: return v, 0, True
    elif kind == 'Nature':
        v = min(seg_dist(dx, dy, *s) for s in TREE) / 0.2; mult = 1.1
    elif kind == 'Places':
        v = math.hypot(dx / 1.9, dy / 0.55)
        if dy > 0.32: v = 9
    else:
        v = math.hypot(dx / 1.3, dy)
    return v, mult, False

def nebula(px_get, px_set, cx, cy, r, kind, state, seed, bounds, ok):
    """Paints one region: state 0 just found, 1 some, 2 many, 3 all usable."""
    scale = [0.78, 0.92, 1.0, 1.0][state]; r = r * scale
    base = [0.3, 0.5, 0.62, 0.62][state]; rim = [0.0, 0.7, 0.85, 0.85][state]
    soft = kind == 'Feeling'
    edge_px = []
    for y in range(int(cy - r * 2.2), int(cy + r * 2.2) + 1):
        for x in range(int(cx - r * 2.4), int(cx + r * 2.4) + 1):
            if not (bounds[0] <= x < bounds[2] and bounds[1] <= y < bounds[3]) or not ok(x, y): continue
            dx, dy = (x - cx) / r, (y - cy) / r
            v, mult, hole = shape(kind, dx, dy, seed)
            if hole: continue
            if kind == 'Sound': mult = 1.0
            v += (vnoise(x, y, seed, 4.0) - 0.5) * 0.45 + (vnoise(x, y, seed + 9, 1.6) - 0.5) * 0.15
            if v > 1: continue
            p = h(x, y, seed, 3)
            c = px_get(x, y)
            if not soft and v > 0.78 and p < rim:  # ink settles at the edge as it dries
                px_set(x, y, tuple(int(c[i] * 0.8) for i in range(3)) + (255,)); edge_px.append((x, y)); continue
            dens = base * mult * min(1, (1 - v) * (1.6 if soft else 2.6) + 0.25)
            if p < dens:
                px_set(x, y, tuple(int(c[i] * 0.885) for i in range(3)) + (255,))
    rnd = random.Random(seed)
    if kind == 'Breaking' and state >= 1:  # fine cracks out from the middle
        for k in range(3):
            a = rnd.uniform(0, math.tau); x, y = cx, cy
            for s in range(int(r * (0.5 + 0.4 * state / 3))):
                a += rnd.uniform(-0.5, 0.5); x += math.cos(a); y += math.sin(a)
                xi, yi = round(x), round(y)
                if bounds[0] <= xi < bounds[2] and bounds[1] <= yi < bounds[3] and ok(xi, yi): px_set(xi, yi, PEN + (255,))
    if state >= 2:  # more of its stars show, and a few pen strokes describe it
        for k in range(7):
            for _ in range(20):
                x, y = round(cx + rnd.uniform(-r, r)), round(cy + rnd.uniform(-r, r) * 0.8)
                v, _m, hole = shape(kind, (x - cx) / r, (y - cy) / r, seed)
                if v < 0.85 and not hole and ok(x, y): break
            col = [PENCIL, INK, INK, PENCIL, (90, 170, 190), INK, PENCIL][k]
            px_set(x, y, col + (255,))
        for k in range(3):
            x, y = round(cx + rnd.uniform(-0.6, 0.6) * r), round(cy + rnd.uniform(-0.5, 0.5) * r)
            for s in range(4):
                if ok(x + s, y - s // 2): px_set(x + s, y - s // 2, (150, 132, 116, 255))
    if state == 3:  # every word in it usable: a thin cyan rim, the book's highest honour
        for (x, y) in edge_px[::3]:
            px_set(x, y, (132, 196, 210, 255))
    if kind == 'Seeing' and state >= 1:
        px_set(round(cx), round(cy), INK + (255,))

def milky_way(px_get, px_set, a, b, width, ok, bounds, seed=5):
    for y in range(bounds[1], bounds[3]):
        for x in range(bounds[0], bounds[2]):
            if not ok(x, y): continue
            d = seg_dist(x, y, *a, *b) / width + (vnoise(x, y, seed, 6) - 0.5) * 0.8
            if d < 1 and h(x, y, 77) < 0.2 * (1 - d) ** 0.7:
                c = px_get(x, y); px_set(x, y, tuple(int(c[i] * 0.9) for i in range(3)) + (255,))

# Hand-drawn margin marks (7x7, book pixels): find, recent, review, stage.
MARKS = {
 'find':   ["..###..", ".#...#.", ".#...#.", ".#...#.", "..###..", "....##.", ".....##"],
 'recent': [".#####.", "..#.#..", "...#...", "...#...", "..#.#..", ".#.#.#.", ".#####."],
 'review': ["..###..", ".#...#.", "#.....#", "#...#.#", ".#..###", "..#..#.", "......."],
 'stage':  [".......", ".......", "a.b.c.d", ".......", ".......", ".......", "......."],
}
def marks(im, x0, y0, chosen):
    px = im.load()
    for i, (name, rows) in enumerate(MARKS.items()):
        for yy, row in enumerate(rows):
            for xx, ch in enumerate(row):
                if ch == '.': continue
                col = {'a': (176, 162, 146), 'b': PENCIL, 'c': INK, 'd': (70, 150, 170)}.get(ch, INK if i == chosen else (150, 136, 120))
                px[x0 + xx, y0 + i * 12 + yy] = col + (255,)
        if i == chosen:
            for xx in range(7): px[x0 + xx, y0 + i * 12 + 8] = INK + (255,)

def label(d, xy, s, size, col, anchor='la', font=FONT):
    d.text((xy[0] * S, xy[1] * S), s, font=ImageFont.truetype(font, size), fill=col + (255,), anchor=anchor)

# 1. the whole sky, round 2 ------------------------------------------------------------------
LAYOUT = [  # name, centre, radius, state
    ('Breaking', (48, 38), 12, 2), ('Holding', (80, 33), 8, 1), ('Places', (106, 26), 6, 0),
    ('Seeing', (102, 50), 8, 1), ('Feeling', (68, 58), 10, 2), ('Death', (40, 72), 11, 1),
    ('Sound', (96, 78), 7, 0), ('Light', (62, 88), 8, 3), ('Nature', (88, 96), 7, 1)]
NAME_AT = {'Breaking': (48, 53, 'mm'), 'Holding': (80, 45, 'mm'), 'Places': (106, 34, 'mm'), 'Seeing': (102, 60, 'mm'),
           'Feeling': (68, 71, 'mm'), 'Death': (40, 86, 'mm'), 'Sound': (96, 88, 'mm'), 'Light': (74, 92, 'lm'), 'Nature': (100, 99, 'lm')}
im = base(); blank(im, LEFT); blank(im, (140, 14 + PADT, 232, 102 + PADT))
px = im.load(); ok = lambda x, y: is_paper(px, x, y)
get = lambda x, y: px[x, y]
def put(x, y, c): px[x, y] = c
milky_way(get, put, (28, 100 + PADT), (116, 18 + PADT), 9, ok, (LEFT[0], LEFT[1], LEFT[2], LEFT[3]))
for i, (name, (x, y), r, st) in enumerate(LAYOUT):
    nebula(get, put, x, y + PADT, r, name, st, 11 + i, LEFT, ok)
marks(im, 223, 30 + PADT, 1)
big = up(im).convert('RGBA'); d = ImageDraw.Draw(big)
for name, (x, y, anc) in NAME_AT.items():
    st = [l[3] for l in LAYOUT if l[0] == name][0]
    label(d, (x, y + PADT), name, 21, INK if st >= 2 else PENCIL, anc)
right = [('The sky', INK, 40, 0), ('9 of 12 regions found', PENCIL, 22, 9)]
y = 22 + PADT
for s, col, size, gap in right:
    label(d, (146, y + gap), s, size, col); y += gap
yy = 44 + PADT
for name, _c, _r, st in LAYOUT:
    label(d, (146, yy), name, 22, INK if st >= 2 else PENCIL); label(d, (186, yy), ['just found', 'some', 'many', 'all usable'][st], 18, PENCIL); yy += 6.4
label(d, (219, 52 + PADT + 12), 'recent', 15, INK, 'rm')
bg = Image.new('RGBA', (big.width + 60, big.height + 60), (24, 26, 28, 255)); bg.paste(big, (30, 30), big)
bg.convert('RGB').save(OUT + 'r2_1_sky_layout.png')

# 2. nine shapes, 3. four states -- on loose paper -------------------------------------------
def paper(w, hgt, seed=3):
    p = Image.new('RGBA', (w, hgt), PAPER + (255,)); q = p.load()
    for y in range(hgt):
        for x in range(w):
            if h(x, y, seed) < 0.06: q[x, y] = tuple(int(PAPER[i] * 0.95) for i in range(3)) + (255,)
    return p
def sheet(cells, cols, cw, ch, captions, file, title):
    rows = math.ceil(len(cells) / cols)
    p = paper(cols * cw, rows * ch); q = p.load()
    g = lambda x, y: q[x, y]
    def s(x, y, c): q[x, y] = c
    for i, (kind, st, r) in enumerate(cells):
        cx, cy = (i % cols) * cw + cw // 2, (i // cols) * ch + ch // 2 - 3
        nebula(g, s, cx, cy, r, kind, st, 21 + i, ((i % cols) * cw + 1, (i // cols) * ch + 1, (i % cols + 1) * cw - 1, (i // cols + 1) * ch - 1), lambda x, y: True)
    big = p.resize((p.width * S, p.height * S), Image.NEAREST); d = ImageDraw.Draw(big)
    for i, cap in enumerate(captions):
        cx, cy = (i % cols) * cw + cw / 2, (i // cols) * ch + ch - 8
        for k, part in enumerate(cap.split('：')):
            d.text((cx * S, (cy + k * 4.5) * S), part, font=ImageFont.truetype(CJK, 19 if k else 21), fill=(PENCIL if k else INK) + (255,), anchor='mm')
    out = Image.new('RGB', (big.width + 60, big.height + 110), (24, 26, 28))
    ImageDraw.Draw(out).text((30, 30), title, font=ImageFont.truetype(CJK, 30), fill=(230, 222, 210))
    out.paste(big, (30, 80)); out.save(file)
SHAPES = ['Breaking', 'Holding', 'Seeing', 'Death', 'Feeling', 'Sound', 'Light', 'Nature', 'Places']
ZH = ['Breaking 打碎：参差的碎边、细裂纹', 'Holding 抓住：没完全合上的圈', 'Seeing 看见：中间留白的眼睛',
      'Death 死亡：往下沉', 'Feeling 感受：最柔、边缘看不出', 'Sound 声音：一圈圈波纹',
      'Light 光：中间留白、往外放射', 'Nature 自然：像树枝分叉', 'Places 地方：平平铺开']
sheet([(k, 2, 13) for k in SHAPES], 3, 64, 58, ZH, OUT + 'r2_2_nine_shapes.png', '9 个天区各自的形状（都画成“学了很多”的状态）')
sheet([('Breaking', s, 13) for s in range(4)], 4, 60, 58, ['① 刚发现：最淡的一层', '② 学了一些：边缘积墨、细裂纹', '③ 学了很多：更多星星、钢笔纹路', '④ 全部能用：一圈淡青蓝'],
      OUT + 'r2_3_four_states.png', '同一个天区（Breaking）从刚发现到全部能用')
print('ok')
