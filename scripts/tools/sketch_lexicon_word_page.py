"""Lexicon word page layout sketches (after D-091): the page as it is now, A "dictionary entry"
and B "specimen page", each for a full word (shatter, usable) and a sparse one (scatter,
recognized). Drawn on the real open book. Run from the repo root."""
import sys
from PIL import Image, ImageDraw, ImageFont
sys.argv = [sys.argv[0]]
exec(open('scripts/tools/sketch_lexicon_sky.py').read().split("def tabs")[0])  # base(), blank(), line(), star(), up() ...

CJK = '/System/Library/Fonts/Hiragino Sans GB.ttc'
IPA = '/System/Library/Fonts/Supplemental/Times New Roman.ttf'
FAINT = (170, 156, 140)
CYAN_INK = (70, 150, 170)
OUT = 'docs/reference/lexicon_sky/word_page/'
RIGHT = (134, 14 + PADT, 236, 104 + PADT)
MARKS = [["..###..", ".#...#.", ".#...#.", ".#...#.", "..###..", "....##.", ".....##"],
	[".#####.", "..#.#..", "...#...", "...#...", "..#.#..", ".#.#.#.", ".#####."],
	["..###..", ".#...#.", "#.....#", "#...#.#", ".#..###", "..#..#.", "......."],
	[".......", ".......", "a.b.c.d", ".......", ".......", ".......", "......."]]

WORDS = {
	"shatter": {"stage": "USABLE", "ipa": "/ˈʃæt.ə(ɹ)/   verb", "sense": ["to break something suddenly into", "many small pieces"],
		"fight": ["Breaks 8 structure; where none is", "left, takes 2 armour and deals 3."], "cost": "2 focus",
		"line": ["What is shattered cannot be put", "back the same way twice."],
		"trace": [("seen", "By a broken cross · Broken Graveyard", None),
			("recognized", "The Broken Wing · Broken Graveyard", "“The wing did not fall. It was shattered.”"),
			("understood", "A skeleton fight · Broken Graveyard", "“The fallen bones shattered at your word.”"),
			("usable", "The Cracked Slab · Broken Graveyard", "“The slab bursts into a hundred pieces.”")],
		"near": "scatter  ·  crumble", "confused": "easily confused: scatter, shutter", "crumbs": "sky  ›  Breaking  ›  Breaking apart  ›  BREAK"},
	"scatter": {"stage": "RECOGNIZED", "ipa": "/ˈskæt.ə(ɹ)/   verb", "sense": None, "fight": None, "line": None,
		"trace": [("seen", "By a fallen urn · Broken Graveyard", None),
			("recognized", "A skeleton fight · Broken Graveyard", "“The bones scatter across the stones.”"),
			("understood", None, None), ("usable", None, None)],
		"near": "shatter  ·  crumble", "confused": None, "crumbs": "sky  ›  Breaking  ›  Breaking apart  ›  BREAK"},
}
FIGURE = [(0, 0), (6, -5), (13, -2), (17, 6), (9, 9)]  # the BREAK constellation, small
FIG_WORDS = ["shatter", "scatter", "crumble", "break", "split"]
FIG_STAGE = {"shatter": "cyan", "scatter": "pencil", "crumble": "ink"}  # break / split: not met


def T(d, x, y, s, size, col, alpha=255, anchor='ls', font=FONT):
	d.text((x * S, (y + PADT) * S), s, font=ImageFont.truetype(font, int(size * S)), fill=col + (alpha,), anchor=anchor)


def spread():
	im = base()
	blank(im, LEFT); blank(im, RIGHT)
	px = im.load()
	for i, rows in enumerate(MARKS):  # the four marks, as in game
		for y, row in enumerate(rows):
			for x, ch in enumerate(row):
				if ch != '.':
					col = {'a': (176, 162, 146), 'b': PENCIL, 'c': INK, 'd': (75, 150, 166)}.get(ch, (150, 136, 120))
					px[198 + i * 9 + x, 14 + PADT + y] = col + (255,)
	return im


def word(d, x, y, w, size, centred=False):
	st = WORDS[w]["stage"]
	col = {"USABLE": CYAN_INK, "RECOGNIZED": PENCIL}.get(st, INK)
	T(d, x, y, w, size, col, anchor='ms' if centred else 'ls')


def figure(d, ox, oy, scale, w, names=False, big=False):
	"""The word's constellation, drawn on the enlarged page: its own star bright, met neighbours as
	stars, unmet ones only a faint ring (no name). Positions in book pixels."""
	pts = [((ox + x * scale) * S, (oy + y * scale + PADT) * S) for x, y in FIGURE]
	for k in range(1, len(pts)):
		a, b = FIG_WORDS[k - 1], FIG_WORDS[k]
		if a in FIG_STAGE and b in FIG_STAGE:
			pencil = 'pencil' in (FIG_STAGE[a], FIG_STAGE[b])
			(x0, y0), (x1, y1) = pts[k - 1], pts[k]
			n = 14 if big else 6
			for t in range(n):
				if pencil and t % 2:
					continue
				d.line([(x0 + (x1 - x0) * t / n, y0 + (y1 - y0) * t / n), (x0 + (x1 - x0) * (t + 1) / n, y0 + (y1 - y0) * (t + 1) / n)],
					fill=(PENCIL if pencil else INK) + (200,), width=max(2, S // 2))
	g = 1.6 if big else 1.0
	for k, (x, y) in enumerate(pts):
		n = FIG_WORDS[k]
		kind = FIG_STAGE.get(n)
		if kind == 'cyan':
			for r, al in [(1.9, 40), (1.3, 80)]:
				d.ellipse([x - r * S * g, y - r * S * g, x + r * S * g, y + r * S * g], fill=CYAN + (al,))
			r = 0.75 * S * g; d.ellipse([x - r, y - r, x + r, y + r], fill=(225, 248, 255, 255))
		elif kind:
			r = (0.9 if kind == 'ink' else 0.7) * S * g
			d.ellipse([x - r, y - r, x + r, y + r], fill=(INK if kind == 'ink' else PENCIL) + (255,))
		else:
			r = 0.6 * S * g
			d.ellipse([x - r, y - r, x + r, y + r], outline=FAINT + (255,), width=max(1, S // 3))
		if kind and (names or n == w):
			size = 3.4 if big else 2.8
			T(d, x / S + 2.5 * g, y / S - PADT + 1.2, n, size, CYAN_INK if kind == 'cyan' else (INK if n == w else PENCIL), 255 if n == w else 180)


def now(w):
	"""The page as it is in game today (D-091)."""
	im = spread(); W = WORDS[w]
	im = up(im); d = ImageDraw.Draw(im)
	T(d, 32, 19, W["crumbs"] + "  ›  " + w, 3.4, PENCIL, 200)
	word(d, 34, 46, w, 13)
	T(d, 34, 54, W["ipa"], 4.0, PENCIL, font=IPA)
	y = 62
	for r in W["sense"] or []:
		T(d, 34, y, r, 5.0, INK); y += 6.5
	if W["fight"]:
		y += 1.5; T(d, 34, y, "in a fight", 3.4, PENCIL); y += 5.5
		for r in W["fight"]:
			T(d, 34, y, r, 4.2, INK); y += 5.5
	if W["line"]:
		y = max(y + 3, 88)
		for r in W["line"]:
			T(d, 34, y, r, 4.2, INK, 190); y += 5.5
	T(d, 146, 24, "How you learned it", 6.0, INK)
	y = 33
	for name, where, quote in W["trace"]:
		T(d, 146, y, name, 3.8, INK if where else PENCIL, 255 if where else 110)
		if where:
			T(d, 146 + len(name) * 1.9 + 3, y, "— " + where.split(" · ")[0] + " · " + where.split(" · ")[1], 3.4, PENCIL)
		y += 6
		if quote:
			T(d, 149, y - 0.5, quote, 4.0, INK, 215); y += 6.5
	T(d, 146, 84, "Near it", 5.0, INK); T(d, 146, 91, W["near"], 4.0, PENCIL)
	if W["confused"]:
		T(d, 146, 99, W["confused"], 3.4, PENCIL)
	return im


def empty_lines(d, x, y, width, rows, note):
	"""Ruled pencil lines where something will be written once the word is known."""
	for k in range(rows):
		yy = (y + k * 6 + PADT) * S
		for xx in range(int(x * S), int((x + width) * S), 3 * S):
			d.line([(xx, yy), (xx + S, yy)], fill=FAINT + (255,), width=max(1, S // 2))
	T(d, x, y + rows * 6 - 1, note, 3.0, PENCIL, 150)


def trace_line(im, d, x, top, W, quotes=True, step=None):
	"""The Memory Trace as a path: a thread down the page, a knot for each stage."""
	y = top
	nodes = []
	for name, where, quote in W["trace"]:
		nodes.append((name, where, quote, y))
		y += 7 + (6.5 if (quote and quotes) else 0)
	yl = [(n[3] - 1.5) for n in nodes]
	reached = [n for n in nodes if n[1]]
	px = im
	# the thread: ink while walked, dotted pencil ahead
	for k in range(len(nodes) - 1):
		a, b = yl[k], yl[k + 1]
		walked = nodes[k + 1][1] is not None
		for yy in range(int(a * S) + 2 * S, int(b * S) - S):
			if walked or (yy // (2 * S)) % 2 == 0:
				d.line([(x * S, yy + PADT * S), (x * S + S // 2, yy + PADT * S)], fill=(INK if walked else FAINT) + (255,))
	for (name, where, quote, yy), ly in zip(nodes, yl):
		cx, cy = x * S + S // 4, (ly + PADT) * S
		col = {"usable": CYAN_INK}.get(name, INK) if where else FAINT
		r = 1.2 * S if where else 0.8 * S
		d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (255,) if where else None, outline=col + (255,), width=max(1, S // 3))
		T(d, x + 4, yy, name, 3.8, INK if where else PENCIL, 255 if where else 110)
		if where:
			T(d, x + 4 + len(name) * 1.85 + 2.5, yy, where, 3.2, PENCIL)
		if quote and quotes:
			T(d, x + 4, yy + 5.5, quote, 4.0, INK, 215)


def variant_a(w):
	"""A, dictionary entry: the word at the top beside its little constellation; a rule; meaning;
	"in a fight" in a bracketed box; the page's line as an epigraph at the foot. Right: the trace
	as a thread with knots, neighbours at the foot."""
	im = spread(); W = WORDS[w]
	im = up(im); d = ImageDraw.Draw(im)
	T(d, 32, 19, W["crumbs"], 3.4, PENCIL, 170)
	word(d, 34, 36, w, 13)
	T(d, 34, 44, W["ipa"], 4.0, PENCIL, font=IPA)
	figure(d, 90, 30, 1.25, w)
	T(d, 101, 46, "BREAK", 2.8, PENCIL, 160, anchor='ms')
	# rule
	d.line([(34 * S, (49 + PADT) * S), (114 * S, (49 + PADT) * S)], fill=PENCIL + (120,), width=max(1, S // 2))
	if W["sense"]:
		y = 56
		for r in W["sense"]:
			T(d, 34, y, r, 5.0, INK); y += 6.5
	else:
		empty_lines(d, 34, 56, 78, 2, "the meaning is written here once you understand it")
	box = (33, 70, 115, 86)
	if W["fight"]:
		for (cx, cy, sx, sy) in [(box[0], box[1], 1, 1), (box[2], box[1], -1, 1), (box[0], box[3], 1, -1), (box[2], box[3], -1, -1)]:
			d.line([(cx * S, (cy + PADT) * S), ((cx + 4 * sx) * S, (cy + PADT) * S)], fill=INK + (200,), width=S // 2)
			d.line([(cx * S, (cy + PADT) * S), (cx * S, (cy + 4 * sy + PADT) * S)], fill=INK + (200,), width=S // 2)
		T(d, 36, 75, "IN A FIGHT", 2.8, PENCIL)
		T(d, 113, 75, "costs " + W["cost"], 2.8, PENCIL, anchor='rs')
		T(d, 36, 80.5, W["fight"][0], 4.0, INK); T(d, 36, 85, W["fight"][1], 4.0, INK)
	else:
		T(d, 74, 79, "what it does in a fight: once it is yours", 3.0, PENCIL, 130, anchor='ms')
	if W["line"]:
		T(d, 74, 93, "~", 4.0, PENCIL, 150, anchor='ms')
		T(d, 74, 98, W["line"][0], 4.0, INK, 190, anchor='ms'); T(d, 74, 103, W["line"][1], 4.0, INK, 190, anchor='ms')
	T(d, 146, 30, "How you learned it", 6.0, INK)
	trace_line(im, d, 147, 40, W)
	T(d, 146, 94, "Near it", 4.4, INK); T(d, 162, 94, W["near"], 3.8, PENCIL)
	if W["confused"]:
		T(d, 146, 101, W["confused"], 3.2, PENCIL)
	return im


def variant_b(w):
	"""B, specimen page: the word as a title, centred, with its constellation drawn large below it
	(its star bright, its met neighbours named); the meaning under the figure. Right: the trace
	(sentences shorter), then "in a fight", then the neighbours."""
	im = spread(); W = WORDS[w]
	im = up(im); d = ImageDraw.Draw(im)
	T(d, 74, 19, W["crumbs"], 3.2, PENCIL, 160, anchor='ms')
	word(d, 74, 35, w, 12, centred=True)
	T(d, 74, 42, W["ipa"], 3.8, PENCIL, anchor='ms', font=IPA)
	figure(d, 50, 62, 2.4, w, names=True, big=True)
	if W["sense"]:
		T(d, 74, 88, " ".join(W["sense"]), 4.4, INK, anchor='ms')
	else:
		empty_lines(d, 40, 86, 68, 1, "")
		T(d, 74, 92, "the meaning comes once you understand it", 3.0, PENCIL, 140, anchor='ms')
	if W["line"]:
		T(d, 74, 99, " ".join(W["line"]), 3.4, INK, 170, anchor='ms')
	T(d, 146, 30, "How you learned it", 6.0, INK)
	trace_line(im, d, 147, 39, W, quotes=True)
	if W["fight"]:
		T(d, 146, 86, "In a fight", 4.4, INK); T(d, 236 - 6, 86, W["cost"], 3.0, PENCIL, anchor='rs')
		T(d, 146, 92, W["fight"][0] + " " + W["fight"][1], 3.4, INK)
	T(d, 146, 101, "Near it:  " + W["near"], 3.4, PENCIL)
	return im


def sheet():
	rows = [("现在（游戏里）", now), ("A  词条：词和它的小星座在顶上，下面释义、战斗作用框、页脚一句", variant_a),
		("B  标本页：词居中当标题，星座画大放中间，释义在下", variant_b)]
	cell = up(base()).size
	head = 70
	W_ = cell[0] * 2 + 30; H_ = (cell[1] + head) * len(rows)
	out = Image.new('RGB', (W_, H_), (24, 22, 26))
	d = ImageDraw.Draw(out)
	cj = ImageFont.truetype(CJK, 34)
	for r, (title, fn) in enumerate(rows):
		y = r * (cell[1] + head)
		d.text((20, y + 16), title, font=cj, fill=(230, 220, 200))
		for c, w in enumerate(["shatter", "scatter"]):
			im = fn(w)
			out.paste(im, (c * (cell[0] + 30), y + head), im)
		for c, sub in enumerate(["能用的词 SHATTER", "刚认得的词 scatter"]):
			d.text((c * (cell[0] + 30) + cell[0] - 300, y + head + 8), sub, font=ImageFont.truetype(CJK, 24), fill=(120, 100, 80))
	out.save(OUT + 'layout_sketches.png')
	for name, fn in [("A", variant_a), ("B", variant_b)]:
		fn("shatter").save(OUT + 'layout_%s_shatter.png' % name)


sheet()
print("ok")
