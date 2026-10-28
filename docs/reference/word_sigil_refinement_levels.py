"""Four levels of refinement for the B (baseline) Word Sigil, drawn over the real combat bar.
Native 960x540 pixels shown at 3x; language lines are whole native pixels; text is rendered sharp
at 3x (as the game does); glow is smooth (Art Bible: lighting may be smooth)."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 3
CYAN = (107, 219, 242)
ROOT = "/Users/mac/Documents/GitHub.nosync/English-Game/"
bg_full = Image.open(sys.argv[1]).convert("RGBA")
OUT = sys.argv[2]
font = ImageFont.truetype(ROOT + "art/ui/fonts/CormorantGaramond.ttf", 19 * S)
try:
    font.set_variation_by_name("SemiBold")
except Exception:
    pass
small = ImageFont.truetype(ROOT + "art/ui/fonts/CormorantGaramond.ttf", 10 * S)

WORDS = [("SHATTER", 2, "hover"), ("OBSERVE", 1, "idle"), ("STABILIZE", 1, "off"), ("BIND", 2, "retain"), ("ERODE", 1, "idle")]
# 11x11 placeholder family marks (Claude's, only to show the slot filled; the art group designs the real ones)
GLYPH = {
    "SHATTER": [".....X.....", "..X..X..X..", "...X...X...", "....X.X....", ".XX.....XX.", "....X.X....", "...X...X...", "..X..X..X..", ".....X.....", "...........", "..........."],
    "OBSERVE": [".....X.....", "....X.X....", "...X...X...", "..X.....X..", ".X...X...X.", "X...XXX...X", ".X...X...X.", "..X.....X..", "...X...X...", "....X.X....", ".....X....."],
    "STABILIZE": ["...XXXXX...", "..X.....X..", ".X.......X.", "X....X....X", "X...XXX...X", "X....X....X", ".X.......X.", "..X.....X..", "...XXXXX...", "...........", "..........."],
    "BIND": ["....XXX....", "..XX...XX..", ".X.......X.", ".X..XXX..X.", "X..X...X..X", "X..X...X..X", ".X..XXX..X.", ".X.......X.", "..XX...XX..", "....XXX....", "..........."],
    "ERODE": [".....X.....", "...........", "....X.X....", "...........", "...X.X.X...", "...........", "..X.X.X.X..", "...........", ".X.X.X.X.X.", "...........", "X.X.X.X.X.X"],
}
FAMILY = {"SHATTER": "FORCE", "OBSERVE": "PERCEPTION", "STABILIZE": "PROTECTION", "BIND": "CONTROL", "ERODE": "DECAY"}


def bar_bg():
    crop = bg_full.crop((0, 412 * S, 960 * S, 540 * S)).copy()
    shade = Image.new("RGBA", crop.size)
    d = ImageDraw.Draw(shade)
    for y in range(crop.size[1]):
        t = y / crop.size[1]
        a = int(255 * (0.0 + 0.85 * min(1.0, t * 1.6)))
        d.line([(0, y), (crop.size[0], y)], fill=(5, 8, 10, a))
    return Image.alpha_composite(crop, shade)


class Pen:
    def __init__(self, size):
        self.sharp = Image.new("RGBA", size)
        self.glow = Image.new("RGBA", size)
        self.d = ImageDraw.Draw(self.sharp)
        self.g = ImageDraw.Draw(self.glow)

    def px(self, x, y, a=1.0, glow=True):
        c = CYAN + (int(255 * a),)
        r = [x * S, y * S, x * S + S - 1, y * S + S - 1]
        self.d.rectangle(r, fill=c)
        if glow:
            self.g.rectangle(r, fill=CYAN + (int(255 * a),))

    def hline(self, x0, x1, y, a=1.0, step=1):
        for x in range(x0, x1 + 1, step):
            self.px(x, y, a)

    def vline(self, x, y0, y1, a=1.0):
        for y in range(y0, y1 + 1):
            self.px(x, y, a)

    def text(self, x, y, s, a=1.0, f=None):
        f = f or font
        self.d.text((x * S, y * S), s, font=f, fill=CYAN + (int(255 * a),))
        self.g.text((x * S, y * S), s, font=f, fill=CYAN + (int(255 * a),))

    def glyph(self, x, y, rows, a=1.0):
        for j, row in enumerate(rows):
            for i, c in enumerate(row):
                if c == "X":
                    self.px(x + i, y + j, a)

    def diamond(self, cx, cy, r, a=1.0, filled=True):
        for dy in range(-r, r + 1):
            w = r - abs(dy)
            for dx in range(-w, w + 1):
                if filled or abs(dx) == w:
                    self.px(cx + dx, cy + dy, a)


def word_width(w):
    return int(font.getlength(w) / S)


def draw_word(p, x, y, word, cost, state, level):
    """level 0 = as delivered (B), 1 = + glow, 2 = + instrument detail, 3 = + inscription & hover crown."""
    a = {"idle": 0.86, "hover": 1.0, "retain": 0.86, "off": 0.45}[state]
    tw = word_width(word)
    W = tw + 34
    base = y + 28
    if level >= 2:
        p.glyph(x + 6, y + 9, GLYPH[word], a * 0.9)
    else:
        p.vline(x + 11, y + 10, y + 20, a * 0.8)
        p.hline(x + 6, x + 16, y + 15, a * 0.8)
    p.text(x + 23, y + 1, word, a)
    # baseline
    if state == "hover":
        p.hline(x + 1, x + W - 2, base, a)
    else:
        p.hline(x + 1, x + 9, base, a * 0.8)
        p.hline(x + W - 10, x + W - 2, base, a * 0.8)
    p.vline(x + 1, base - 3, base, a * 0.8)
    p.vline(x + W - 2, base - 3, base, a * 0.8)
    if level >= 2:
        # Precise-instrument detail: a dim ruler between the two ends, nodes at the ends, a hairline echo.
        if state != "hover":
            if level >= 3:
                half = cost * 4 + 3
                gap0, gap1 = x + W // 2 - half, x + W // 2 + half
                p.hline(x + 11, gap0, base, a * 0.28, step=2)
                p.hline(gap1, x + W - 12, base, a * 0.28, step=2)
            else:
                p.hline(x + 11, x + W - 12, base, a * 0.28, step=2)
        p.diamond(x + 1, base, 1, a)
        p.diamond(x + W - 2, base, 1, a)
        p.hline(x + 5, x + W - 6, base + 2, a * 0.22)
    if level >= 3:
        # Inscription: the word's family in tiny letters on the baseline, centred, dim.
        pass
        if state == "hover":
            # Hover crown: a precise arc of nodes over the word.
            cx = x + W // 2
            for i, dx in enumerate([-12, -6, 0, 6, 12]):
                p.px(cx + dx, y - 2 + abs(dx) // 6, a * (1.0 if dx == 0 else 0.6))
            p.diamond(cx, y - 4, 1, a)
    # cost diamonds
    cy = base if level >= 3 else base + 6
    left = x + W // 2 - (cost - 1) * 4
    for i in range(cost):
        p.diamond(left + i * 8, cy, 2, a * 0.9)
    if state == "retain":
        for dx in range(3):
            p.px(x + W - 7 + dx, y + 2, a)
        p.vline(x + W - 7, y + 2, y + 5, a)
        p.vline(x + W - 5, y + 2, y + 5, a)
    if state == "off":
        p.px(x + W - 6, y + 2, 0.6); p.px(x + W - 4, y + 4, 0.6); p.px(x + W - 5, y + 3, 0.6)
        p.px(x + W - 4, y + 2, 0.6); p.px(x + W - 6, y + 4, 0.6)
    return W


def row(level, title):
    img = bar_bg()
    p = Pen(img.size)
    widths = [word_width(w) + 34 for w, _, _ in WORDS]
    gap = 12
    x = (960 - (sum(widths) + gap * (len(widths) - 1))) // 2
    for (w, c, st), W in zip(WORDS, widths):
        draw_word(p, x, 50, w, c, st, level)
        x += W + gap
    if level >= 1:
        # Two layers of light: a tight bloom hugging the strokes and a wide soft haze.
        for radius, boost in ((1.4 * S, 2.6), (5.5 * S, 3.2)):
            glow = p.glow.filter(ImageFilter.GaussianBlur(radius))
            glow.putalpha(glow.split()[3].point(lambda v: min(255, int(v * boost * (1.0 if level >= 2 else 0.8)))))
            img = Image.alpha_composite(img, glow)
    img = Image.alpha_composite(img, p.sharp)
    d = ImageDraw.Draw(img)
    label = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 15 * S // 2)
    box = d.textbbox((14 * S, 8 * S), title, font=label)
    d.rectangle((box[0] - 12, box[1] - 8, box[2] + 12, box[3] + 8), fill=(8, 10, 14, 235))
    d.text((14 * S, 8 * S), title, font=ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 15 * S // 2), fill=(235, 235, 235, 255))
    return img


titles = [
    "0  美术组的 B（原样）",
    "1  + 发光（程序加，设计稿里本来就没画）",
    "2  + 发光 + 精密仪器感（端点菱形、刻度虚线、双线、真正的词类符号）",
    "3  + 2 + 专注菱形嵌进基线正中（像一条线上的节点）+ 悬停时头顶一圈节点",
]
rows = [row(i, t) for i, t in enumerate(titles)]
h = rows[0].size[1]
out = Image.new("RGBA", (rows[0].size[0], h * 4 + 12 * 3), (12, 14, 18, 255))
for i, r in enumerate(rows):
    out.paste(r, (0, i * (h + 12)))
out.convert("RGB").save(OUT)
# crop of the middle words, larger, to see the detail
crop = out.crop((560 * S // 2, 0, 2880 - 560 * S // 2, out.size[1]))
crop.convert("RGB").save(OUT.replace(".png", "_zoom.png"))
print(out.size)
