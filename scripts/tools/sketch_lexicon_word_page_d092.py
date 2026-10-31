"""Lexicon word page as agreed in D-092: the left page is the word (word, forms, meaning, the page's
line, close in meaning / opposite, mix-ups, family), the right page is you and the word (how you
learned it). Drawn on the real open book for a usable word (the fullest case), a recognized one and
one only seen. Run from the repo root."""
import sys
sys.argv = [sys.argv[0]]
exec(open('scripts/tools/sketch_lexicon_word_page.py').read().rsplit("sheet()", 1)[0])

# met = ink and can be opened; unmet = faint pencil, cannot
REL = {
	"shatter": {"forms": "shatters  ·  shattered  ·  shattering",
		"close": [("crumble", True, "bit by bit, not all at once")],
		"opposite": [("mend", False, "")],
		"mixup": [("scatter", True), ("shutter", False)],
		"family": [("shatterproof", False)]},
	"scatter": {"forms": "scatters  ·  scattered  ·  scattering",
		"close": [("spread", False, "wider, and gentler")],
		"opposite": [("gather", False, "")],
		"mixup": [("shatter", True), ("splatter", False)],
		"family": []},
}
WORDS["decay"] = {"stage": "ENCOUNTERED", "ipa": "/dɪˈkeɪ/   verb", "sense": None, "fight": None, "line": None,
	"trace": [("seen", "In passing · Broken Graveyard", None), ("recognized", None, None),
		("understood", None, None), ("usable", None, None)],
	"crumbs": "sky  ›  Breaking  ›  Wearing away  ›  ROT"}
WORDS["scatter"]["line"] = None


def label(d, y, s):
	T(d, 34, y, s, 2.6, PENCIL, 170)


def dotted(d, x, y, width):
	yy = (y + PADT) * S
	for xx in range(int(x * S), int((x + width) * S), 3 * S):
		d.line([(xx, yy), (xx + S, yy)], fill=FAINT + (255,), width=max(1, S // 2))


def rel_word(d, x, y, w, met, size=3.6):
	T(d, x, y, w, size, INK if met else FAINT, 255 if met else 230)
	return x + len(w) * size * 0.43 + 2.5


def fight_box(d, W, top):
	box = (145, top, 233, top + 16)
	for (cx, cy, sx, sy) in [(box[0], box[1], 1, 1), (box[2], box[1], -1, 1), (box[0], box[3], 1, -1), (box[2], box[3], -1, -1)]:
		d.line([(cx * S, (cy + PADT) * S), ((cx + 4 * sx) * S, (cy + PADT) * S)], fill=INK + (200,), width=S // 2)
		d.line([(cx * S, (cy + PADT) * S), (cx * S, (cy + 4 * sy + PADT) * S)], fill=INK + (200,), width=S // 2)
	T(d, 148, top + 5, "IN A FIGHT", 2.8, PENCIL)
	T(d, 231, top + 5, "costs " + W["cost"], 2.8, PENCIL, anchor='rs')
	T(d, 148, top + 10.5, W["fight"][0], 3.8, INK); T(d, 148, top + 15, W["fight"][1], 3.8, INK)


def final(w):
	im = spread(); W = WORDS[w]; R = REL.get(w)
	im = up(im); d = ImageDraw.Draw(im)
	seen_only = W["stage"] == "ENCOUNTERED"
	T(d, 32, 19, W["crumbs"], 3.2, PENCIL, 170)
	if seen_only:
		T(d, 34, 33, "dec", 12, PENCIL); dotted(d, 51, 33, 16)
	else:
		word(d, 34, 33, w, 12)
	T(d, 34, 40, W["ipa"] if not seen_only else "", 3.8, PENCIL, font=IPA)
	figure(d, 92, 25, 1.2, "")
	T(d, 102, 40, "BREAK" if not seen_only else "ROT", 2.6, PENCIL, 160, anchor='ms')
	y = 45
	if R:
		T(d, 34, y, R["forms"], 2.9, PENCIL, 190)
	d.line([(34 * S, (y + 2.5 + PADT) * S), (114 * S, (y + 2.5 + PADT) * S)], fill=PENCIL + (110,), width=max(1, S // 2))
	y = 52
	if W["sense"]:
		for r in W["sense"]:
			T(d, 34, y, r, 4.6, INK); y += 5.8
	else:
		dotted(d, 34, y, 78); dotted(d, 34, y + 5.5, 52)
		T(d, 34, y + 10, "the meaning, once you understand it", 2.8, PENCIL, 140); y += 15
	if W["line"]:
		y += 1
		for r in W["line"]:
			T(d, 36, y, r, 3.7, INK, 185); y += 4.8
	y += 3
	if seen_only:
		for name in ["CLOSE IN MEANING", "DON'T MIX UP", "FAMILY"]:
			label(d, y, name); dotted(d, 64, y, 46); y += 6.5
		T(d, 74, y + 2, "written in once you recognise it", 2.8, PENCIL, 140, anchor='ms')
	else:
		label(d, y, "CLOSE IN MEANING")
		for name, met, note in R["close"]:
			y += 5; x = rel_word(d, 36, y, name, met)
			T(d, x, y, note, 3.2, PENCIL if met else FAINT, 200)
		for name, met, note in R["opposite"]:
			y += 5; T(d, 36, y, "opposite", 2.6, CYAN_INK if False else PENCIL, 200)
			d.line([(36 * S, (y + 0.8 + PADT) * S), (46 * S, (y + 0.8 + PADT) * S)], fill=PENCIL + (160,), width=max(1, S // 3))
			rel_word(d, 50, y, name, met)
		y += 7; label(d, y, "DON'T MIX UP")
		x = 64
		for name, met in R["mixup"]:
			x = rel_word(d, x, y, name, met, 3.4) + 1
		if R["family"]:
			y += 6; label(d, y, "FAMILY")
			x = 64
			for name, met in R["family"]:
				x = rel_word(d, x, y, name, met, 3.4) + 1
	# right page: you and the word
	T(d, 146, 28, "How you learned it", 5.6, INK)
	trace_line(im, d, 147, 37, W)
	if W["fight"]:
		fight_box(d, W, 86)
	return im


def sheet():
	cell = up(base()).size
	head = 70
	words = [("shatter", "能用的词（最满的情况）"), ("scatter", "刚认得的词"), ("decay", "只见过一面的词")]
	out = Image.new('RGB', (cell[0] * 2 + 30, (cell[1] + head) * 2), (24, 22, 26))
	d = ImageDraw.Draw(out)
	for k, (w, sub) in enumerate(words):
		c, r = k % 2, k // 2
		x, y = c * (cell[0] + 30), r * (cell[1] + head)
		d.text((x + 20, y + 16), sub + "  " + w, font=ImageFont.truetype(CJK, 34), fill=(230, 220, 200))
		im = final(w)
		out.paste(im, (x, y + head), im)
		im.save(OUT + 'D092_%s.png' % w)
	d.text((cell[0] + 50, cell[1] + head + 60), "D-092 单词页：左页讲“这个词”，右页讲“你和它”。\n\n墨色 = 见过、可以点过去\n淡铅笔 = 没见过、点不了\n铅笔虚线 = 还没学到这一步\n\n能用的词：in a fight 放不下左页，\n挪到右页底部。",
		font=ImageFont.truetype(CJK, 30), fill=(200, 190, 170), spacing=12)
	out.save(OUT + 'D092_sketches.png')


sheet()
print("ok")
