"""Lexicon sky, D-088: sketches of the four closer levels (region, cluster, constellation, word
page) on the real open book, in the chosen look (A, ink wash). Run from the repo root."""
import math, random, sys
sys.argv = [sys.argv[0]]
exec(open('scripts/tools/sketch_lexicon_sky.py').read().split("ST={")[0])  # shared helpers

RIGHT = (140, 14 + PADT, 232, 102 + PADT)

def page():
    im = base(); blank(im, LEFT); blank(im, RIGHT); tabs(im); return im

def figure(im, pts, links):
    P = [(x, y + PADT) for x, y in pts]
    for a, b, k in links:
        col = {'pencil': PENCIL, 'ink': INK, 'cyan': (70, 150, 170)}[k]
        line(im, P[a], P[b], col, dash=(k == 'pencil'))
    for i, p in enumerate(P):
        ks = [l[2] for l in links if i in l[:2]] or ['pencil']
        star(im, p, max(ks, key=['pencil', 'ink', 'cyan'].index))

def finish(im, name, crumbs, left_text, right):
    big = up(im).convert('RGBA'); d = ImageDraw.Draw(big)
    text(d, (30, 17 + PADT), crumbs, 18, PENCIL, 230)
    for s, (x, y), size, col in left_text:
        text(d, (x, y + PADT), s, size, col, 230)
    y = 22 + PADT
    for s, col, size, gap in right:
        text(d, (144, y), s, size, col); y += gap
    tab_labels(d)
    bg = Image.new('RGBA', (big.width + 60, big.height + 60), (24, 26, 28, 255)); bg.paste(big, (30, 30), big)
    bg.convert('RGB').save(f'docs/reference/lexicon_sky/{name}.png'); return bg

CYANTXT = (40, 130, 150)
# 2. a region: its clusters
im = page()
spots = {'Shattering': (48, 40, 0.65, 11), 'Cutting': (92, 36, 0.4, 12), 'Crushing': (56, 78, 0.35, 13), 'Wearing away': (94, 76, 0.2, 14)}
for nm, (x, y, dens, seed) in spots.items():
    wash(im, x, y + PADT, 12, dens, seed, tint=0.87)
figure(im, [(44, 38), (49, 35), (53, 40), (48, 44)], [(0, 1, 'cyan'), (1, 2, 'ink'), (2, 3, 'pencil')])
figure(im, [(89, 34), (95, 37)], [(0, 1, 'ink')])
figure(im, [(54, 77), (59, 80)], [(0, 1, 'pencil')])
figure(im, [(93, 75)], [])
a = finish(im, 'zoom_2_region', 'sky  >  Breaking', [(s, (x - 12, y + 9), 22, PENCIL) for s, (x, y, _, _) in spots.items()],
    [('Breaking', INK, 40, 13), ('4 of 9 clusters found', INK, 24, 9), ('', INK, 10, 6),
     ('Shattering  · 3 constellations', INK, 22, 8), ('Cutting  · 1', PENCIL, 22, 8), ('Crushing  · 1', PENCIL, 22, 8), ('Wearing away  · 1', PENCIL, 22, 12),
     ('the ink is darker where you know more', PENCIL, 19, 8)])
# 3. a cluster: its constellations
im = page()
for x, y, dens, seed in [(47, 41, 0.6, 21), (91, 36, 0.45, 22), (63, 74, 0.3, 23), (97, 82, 0.2, 24)]:
    wash(im, x, y + PADT, 11, dens, seed, tint=0.88)
figure(im, [(40, 38), (47, 34), (54, 39), (50, 46), (43, 48)], [(0, 1, 'cyan'), (1, 2, 'ink'), (2, 3, 'pencil'), (3, 4, 'pencil')])
figure(im, [(84, 34), (90, 31), (97, 35), (93, 41)], [(0, 1, 'ink'), (1, 2, 'ink'), (2, 3, 'pencil')])
figure(im, [(56, 74), (63, 70), (70, 76)], [(0, 1, 'ink'), (1, 2, 'pencil')])
figure(im, [(94, 80), (100, 84)], [(0, 1, 'pencil')])
b = finish(im, 'zoom_3_cluster', 'sky  >  Breaking  >  Shattering',
    [('SHATTER', (36, 54), 22, INK), ('SPLINTER', (82, 47), 22, INK), ('CRACK', (55, 84), 22, PENCIL), ('CRUMBLE', (88, 91), 22, PENCIL)],
    [('Shattering', INK, 40, 13), ('to break into many pieces', PENCIL, 22, 9), ('', INK, 10, 5),
     ('SHATTER  · 5 stars, 1 usable', INK, 22, 8), ('SPLINTER  · 4 stars', INK, 22, 8), ('CRACK  · 3 stars', PENCIL, 22, 8), ('CRUMBLE  · 2 stars', PENCIL, 22, 8)])
# 4. a constellation: its words
im = page()
wash(im, 66, 56 + PADT, 34, 0.35, 31, tint=0.9)
pts = [(40, 36), (60, 30), (84, 40), (72, 62), (50, 70), (90, 80)]
figure(im, pts, [(0, 1, 'cyan'), (1, 2, 'ink'), (2, 3, 'ink'), (3, 4, 'pencil'), (3, 5, 'pencil')])
c = finish(im, 'zoom_4_constellation', 'sky  >  Breaking  >  Shattering  >  SHATTER',
    [('shatter', (30, 39), 26, CYANTXT), ('splinter', (54, 22), 24, INK), ('fragment', (87, 37), 24, INK), ('scatter', (75, 61), 24, PENCIL),
     ('crumble', (38, 73), 24, (165, 152, 138)), ('debris', (92, 82), 24, PENCIL)],
    [('shatter', CYANTXT, 40, 11), ('usable  · met 3 times', PENCIL, 20, 9), ('to break suddenly into', INK, 24, 7), ('many small pieces', INK, 24, 11),
     ('“The wing did not fall.', PENCIL, 21, 7), ('It was shattered.”', PENCIL, 21, 7), ('— The Broken Wing', PENCIL, 18, 10), ('open the page  ›', PENCIL, 20, 8)])
# 5. the word page: one word, one spread
im = page()
figure(im, [(108, 28), (113, 25), (117, 29)], [(0, 1, 'cyan'), (1, 2, 'ink')])  # its star, small, in the corner
big = up(im).convert('RGBA'); d = ImageDraw.Draw(big)
text(d, (30, 17 + PADT), 'sky  >  Breaking  >  Shattering  >  SHATTER  >  shatter', 18, PENCIL, 230)
for o in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
    d.text((34 * S + o[0] * 2, 36 * S + PADT * S + o[1] * 2), 'shatter', font=ImageFont.truetype(FONT, 72), fill=CYAN + (28,))
text(d, (34, 36 + PADT), 'shatter', 72, CYANTXT)
rows = [('/ˈʃæt.ə/   verb', PENCIL, 22, 9), ('to break suddenly into', INK, 28, 8), ('many small pieces', INK, 28, 12),
        ('seen  ·  recognized  ·  understood  ·  usable', PENCIL, 18, 10),
        ('What is shattered cannot be put', INK, 21, 7), ('back the same way twice.', INK, 21, 7)]
y = 56 + PADT
for s, col, size, gap in rows:
    text(d, (34, y), s, size, col); y += gap
y = 22 + PADT
for s, col, size, gap in [('Where you met it', INK, 30, 10),
        ('“The wing did not fall. It was shattered.”', PENCIL, 20, 6), ('— The Broken Wing · Broken Graveyard', PENCIL, 17, 9),
        ('“The fallen bones shattered at your word.”', INK, 20, 6), ('— A skeleton fight · Broken Graveyard', PENCIL, 17, 9),
        ('“The slab bursts into a hundred pieces.”', INK, 20, 6), ('— The Cracked Slab', PENCIL, 17, 11),
        ('Near it', INK, 26, 8), ('splinter · fragment · scatter · crumble', PENCIL, 20, 8),
        ('easily confused: scatter, shutter', PENCIL, 18, 8)]:
    text(d, (144, y), s, size, col); y += gap
tab_labels(d)
bg = Image.new('RGBA', (big.width + 60, big.height + 60), (24, 26, 28, 255)); bg.paste(big, (30, 30), big)
bg.convert('RGB').save('docs/reference/lexicon_sky/zoom_5_word_page.png'); e = bg
out = Image.new('RGB', (a.width, a.height * 4), (24, 26, 28))
for i, v in enumerate([a, b, c, e]):
    out.paste(v.convert('RGB'), (0, i * a.height))
out.save('docs/reference/lexicon_sky/zoom_levels_2_to_5.png'); print(out.size)
