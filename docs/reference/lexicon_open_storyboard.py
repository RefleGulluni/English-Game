"""Storyboard for the Lexicon open / close animation (Claude, 2026-10-28). Book art from
art/character_design/lexicon_book_sheet.png; panel 3's half-open cover is only a squashed stand-in:
the real in-between frames are for the character group to draw (pixel art is never scaled)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = "/Users/mac/Documents/GitHub.nosync/English-Game/"
sheet = Image.open(ROOT + "art/character_design/lexicon_book_sheet.png").convert("RGBA")
closed = sheet.crop((31, 52, 129, 172))
opened = sheet.crop((174, 52, 417, 172))
W, H, S = 300, 170, 2
font = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 22)
small = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 17)


def is_cyan(p):
    r, g, b, a = p
    return a and b > 110 and g > 100 and b > r + 40


def split_cyan(img, keep=lambda x, y: True):
    base, lang = img.copy(), Image.new("RGBA", img.size)
    bp, lp = base.load(), lang.load()
    for y in range(img.height):
        for x in range(img.width):
            p = bp[x, y]
            if is_cyan(p):
                bp[x, y] = (196, 180, 160, 255) if img is opened else (52, 40, 34, 255)
                if keep(x, y):
                    lp[x, y] = p
    return base, lang


def glow(layer, strength):
    g = layer.filter(ImageFilter.GaussianBlur(3))
    g.putalpha(g.split()[3].point(lambda v: min(255, int(v * strength))))
    return g


def panel(book, at, dim, lang=None, glow_k=0.0):
    img = Image.new("RGBA", (W, H), (34, 38, 44, 255))
    img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (6, 8, 10, int(255 * dim))))
    layer = Image.new("RGBA", (W, H))
    layer.paste(book, at, book)
    img = Image.alpha_composite(img, layer)
    if lang is not None:
        l2 = Image.new("RGBA", (W, H)); l2.paste(lang, at, lang)
        if glow_k:
            img = Image.alpha_composite(img, glow(l2, glow_k))
        img = Image.alpha_composite(img, l2)
    return img.resize((W * S, H * S), Image.NEAREST)


cb, cl = split_cyan(closed)
ob, _ = split_cyan(opened)
_, half_lines = split_cyan(opened, lambda x, y: x < 75 and y < 70)
_, all_lines = split_cyan(opened)
cx = lambda w: (W - w) // 2
squashed = cb.resize((cb.width // 2, cb.height), Image.NEAREST)  # stand-in only
spread = Image.new("RGBA", opened.size)
spread.paste(ob.crop((0, 0, opened.width // 2 + 4, opened.height)), (0, 0))
spread.paste(squashed, (opened.width // 2, 0), squashed)

panels = [
    (panel(cb, (cx(cb.width), 60), 0.3), "① 合着的书从主角手边升起", "背景开始压暗 · 程序 · 0～0.15 秒"),
    (panel(cb, (cx(cb.width), 25), 0.6, cl, 4.0), "② 封面符印亮起", "青蓝发光一闪 · 程序 · 0.15～0.3 秒"),
    (panel(spread, (cx(opened.width), 25), 0.6), "③ 封面翻开（中间帧）", "角色组画 4～6 帧 · 0.3～0.5 秒（此格是示意）"),
    (panel(ob, (cx(opened.width), 25), 0.6, half_lines, 2.5), "④ 星座连线一条一条亮起", "程序 · 0.5～0.7 秒"),
    (panel(ob, (cx(opened.width), 25), 0.6, all_lines, 1.6), "⑤ 摊开，词浮现，可以操作", "全程约 0.7 秒，随时按 Tab 倒回"),
    (panel(cb, (cx(cb.width), 60), 0.3), "⑥ 合上：倒着播一遍", "更快，约 0.4 秒；连线先收、再合封面、书落下"),
]
cols, gap, cap = 3, 14, 64
pw, ph = W * S, H * S
out = Image.new("RGB", (cols * pw + (cols + 1) * gap, 2 * (ph + cap) + 3 * gap), (14, 16, 20))
d = ImageDraw.Draw(out)
for i, (img, t1, t2) in enumerate(panels):
    x = gap + (i % cols) * (pw + gap); y = gap + (i // cols) * (ph + cap + gap)
    out.paste(img.convert("RGB"), (x, y))
    d.text((x + 4, y + ph + 8), t1, font=font, fill=(236, 232, 224))
    d.text((x + 4, y + ph + 36), t2, font=small, fill=(150, 160, 170))
out.save(ROOT + "docs/reference/lexicon_open_storyboard.png")
print(out.size)
