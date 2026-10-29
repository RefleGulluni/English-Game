#!/usr/bin/env python3
"""检查游戏词条（D-070，说明见 docs/VOCABULARY_PIPELINE.md）。

用法（在仓库根目录）：
    python3 scripts/tools/vocab/check_words.py              # 检查全部，最后列出每个词在各地区的重合数
    python3 scripts/tools/vocab/check_words.py --html 文件  # 另外生成一页给人抽查的词卡

有错误时退出码为 1（以后可以放进测试）。“提醒”不算错误。
"""
import argparse
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORDS = ROOT / "data" / "words"
GLYPHS = ROOT / "art" / "ui" / "word_sigil_v3" / "glyphs"
ROLES = {"ability", "enemy", "thing", "mood"}
STAGES = ["ENCOUNTERED", "RECOGNIZED", "UNDERSTOOD", "USABLE"]
STATUS = {"draft", "approved"}
EXAM_NAMES = {"zk": "中考", "gk": "高考", "cet4": "四级", "cet6": "六级", "ky": "考研",
              "toefl": "托福", "ielts": "雅思", "gre": "GRE"}
MAX_SENSE = 80       # 游戏里显示的英文释义：短
MAX_PAGE_LINE = 110  # 书页上一行半以内


def check_sense(lemma, s, entry, tags, sigils, errors, notes):
    where = f"{lemma} / {s.get('id', '?')}"

    def err(msg):
        errors.append(f"{where}：{msg}")

    if not str(s.get("id", "")).startswith(f"{lemma}#") or s["id"] == f"{lemma}#":
        err("id 要写成 词#词义，如 bind#restrain")
    if s.get("role") not in ROLES:
        err(f"role 只能是 {'/'.join(sorted(ROLES))}")
    if s.get("status") not in STATUS:
        err("status 只能是 draft / approved")
    if not s.get("sense"):
        err("缺英文释义 sense")
    elif len(s["sense"]) > MAX_SENSE:
        err(f"英文释义太长（{len(s['sense'])} > {MAX_SENSE}）")
    if not s.get("zh"):
        err("缺中文 zh")
    if not s.get("tags"):
        err("至少要有一个标签")
    for t in s.get("tags", []):
        if t not in tags:
            err(f"标签 {t} 不在 data/words/tags.json 里")
    synsets = {w["synset"] for w in entry["dictionary"]["wordnet"]}
    if s.get("wordnet") and s["wordnet"] not in synsets:
        err(f"wordnet {s['wordnet']} 不是这个词在词典里的词义")
    if not s.get("wordnet"):
        notes.append(f"{where}：没有对应的 WordNet 词义（近义、反义只能手写）")
    for stage in STAGES:
        if not s.get("stage_lines", {}).get(stage):
            err(f"缺阶段 {stage} 的样子")
    for kind in ("recognize", "produce"):
        if not s.get("challenge", {}).get(kind):
            err(f"缺小考 {kind}")
    if not s.get("confusable"):
        err("缺容易混的词 confusable")
    line = s.get("page_line", "")
    if not line:
        err("缺书页上的话 page_line")
    elif len(line) > MAX_PAGE_LINE:
        err(f"书页上的话太长（{len(line)} > {MAX_PAGE_LINE}）")
    if s.get("role") == "ability":
        if s.get("sigil") not in sigils:
            err(f"能力词要有词类符号 sigil（{'/'.join(sorted(sigils))}）")
        if not isinstance(s.get("effect"), dict) or "type" not in s["effect"] or "cost" not in s["effect"]:
            err("能力词要有 effect：至少写 type 和 cost")
        elif s["effect"].get("proposed"):
            notes.append(f"{where}：效果是提案，等战斗设计定")
    elif "sigil" in s or "effect" in s:
        err("只有能力词有 sigil / effect")
    if s.get("status") == "approved" and "【" in json.dumps(s, ensure_ascii=False):
        err("已通过的词条里还有【提案】/【待…】标记")


def overlap(sense, liked):
    return len(set(sense.get("tags", [])) & set(liked))


def write_html(path, entries, table):
    regions = table["regions"]
    cards = []
    for e in entries:
        d = e["dictionary"]
        for s in e["senses"]:
            score = " · ".join(f"{r} {overlap(s, liked)}" for r, liked in regions.items())
            tags = "".join(f'<span class="tag{" hit" if t in regions.get("cemetery", []) else ""}">{t} {table["tags"].get(t, "")}</span>'
                           for t in s.get("tags", []))
            exam = " ".join(EXAM_NAMES[x] for x in d["exam"]) or "—"
            pron = d["phonetic"].get("uk") or ""
            stages = "".join(f"<li><b>{k}</b> {html.escape(v)}</li>" for k, v in s.get("stage_lines", {}).items())
            appears = "".join(f"<li>{html.escape(a)}</li>" for a in s.get("appears", []))
            rel = s.get("relations", {})
            rel_txt = "；".join(f"{n} {', '.join(rel.get(k, []))}" for k, n in
                               (("synonyms", "近义"), ("antonyms", "反义"), ("family", "一家人")) if rel.get(k))
            effect = ""
            if "effect" in s:
                effect = f'<p class="eff">{s.get("sigil", "")} · {html.escape(json.dumps(s["effect"], ensure_ascii=False))}</p>'
            override = f'<p class="small">手动加权：{html.escape(json.dumps(s["region_override"], ensure_ascii=False))}</p>' if s.get("region_override") else ""
            cards.append(f"""<article data-role="{s.get('role')}">
<header><h2>{e['lemma']}</h2><span class="pron">/{html.escape(pron)}/</span><span class="role">{s.get('role')} · {s.get('pos')}</span></header>
<p class="sense">{html.escape(s.get('sense', ''))}</p>
<p class="zh">{html.escape(s.get('zh', ''))}<span class="small">　词典：{html.escape(' / '.join(d['zh'][:2]))}</span></p>
<p class="line">“{html.escape(s.get('page_line', ''))}”</p>
<div class="tags">{tags}</div>
<p class="small">墓园重合：{score}　考试：{exam}　{s.get('status')}</p>{override}{effect}
<details><summary>在哪遇到 · 四个阶段 · 小考 · 易混</summary>
<ul>{appears}</ul><ol>{stages}</ol>
<p class="small">认出来：{html.escape(s.get('challenge', {}).get('recognize', ''))}<br>用对：{html.escape(s.get('challenge', {}).get('produce', ''))}</p>
<p class="small">易混：{html.escape('，'.join(s.get('confusable', [])))}</p>
<p class="small">{html.escape(rel_txt)}</p></details>
</article>""")
    page = f"""<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Word Cards</title><style>
:root{{--bg:#16130f;--card:#221d17;--ink:#e9dcc4;--dim:#9c8f78;--cyan:#5fd4e8;--line:#3a3128}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,"PingFang SC",sans-serif;padding:24px 16px}}
h1{{font:600 22px Georgia,serif;margin:0 0 4px}} .intro{{color:var(--dim);margin:0 0 16px;max-width:820px}}
.filters button{{background:var(--card);color:var(--ink);border:1px solid var(--line);padding:4px 10px;margin:0 6px 12px 0;cursor:pointer}}
.filters button.on{{border-color:var(--cyan);color:var(--cyan)}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}}
article{{background:var(--card);border:1px solid var(--line);padding:12px 14px}}
header{{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}} h2{{font:600 20px Georgia,serif;margin:0;color:var(--cyan)}}
.pron,.role,.small{{color:var(--dim);font-size:12px}} .role{{margin-left:auto}}
.sense{{margin:6px 0 2px}} .zh{{margin:0 0 6px}} .line{{font:italic 15px Georgia,serif;margin:6px 0}}
.tag{{display:inline-block;font-size:11px;border:1px solid var(--line);padding:0 5px;margin:0 4px 4px 0;color:var(--dim)}}
.tag.hit{{border-color:#a08550;color:#e0c48a}} .eff{{font-size:12px;color:#c9b38a;margin:4px 0}}
details{{margin-top:6px}} summary{{cursor:pointer;color:var(--dim);font-size:13px}} ul,ol{{padding-left:18px;margin:6px 0;font-size:13px}}
</style>
<h1>第一批词条草稿</h1>
<p class="intro">{len(cards)} 个词条。黄色标签 = 墓园喜欢的标签。中文、词典释义、考试标签、音标是词典自动填的；英文释义、标签、书页上的话、阶段、小考、效果是 Claude 写的草稿，等你抽查。点“在哪遇到…”看更多。</p>
<div class="filters"><button class="on" data-f="all">全部</button><button data-f="ability">能力词</button><button data-f="enemy">敌人词</button><button data-f="thing">墓园里的东西</button><button data-f="mood">气氛词</button></div>
<main>{''.join(cards)}</main>
<script>
document.querySelectorAll('.filters button').forEach(b=>b.onclick=()=>{{
 document.querySelectorAll('.filters button').forEach(x=>x.classList.toggle('on',x===b));
 document.querySelectorAll('article').forEach(a=>a.style.display=(b.dataset.f==='all'||a.dataset.role===b.dataset.f)?'':'none');
}});
</script></html>"""
    Path(path).write_text(page, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--html")
    args = parser.parse_args()
    table = json.loads((WORDS / "tags.json").read_text(encoding="utf-8"))
    sigils = {p.stem.removeprefix("family_") for p in GLYPHS.glob("family_*.png") if "sheet" not in p.stem}
    order = [line.split()[0] for line in (WORDS / "word_list.txt").read_text(encoding="utf-8").splitlines()
             if line.split("#")[0].strip()]
    errors, notes, entries = [], [], []
    for lemma in order:
        path = WORDS / "entries" / f"{lemma}.json"
        if not path.exists():
            errors.append(f"{lemma}：名单里有、但还没有词条（先跑 build_word_drafts.py）")
            continue
        entry = json.loads(path.read_text(encoding="utf-8"))
        entries.append(entry)
        if entry["dictionary"].get("missing"):
            notes.append(f"{lemma}：词典里找不到（{', '.join(entry['dictionary']['missing'])}），要全部手写")
        for s in entry["senses"]:
            check_sense(lemma, s, entry, table["tags"], sigils, errors, notes)

    for region, liked in table["regions"].items():
        print(f"\n【{region}】按标签重合个数（0 = 进暂存池，除非手动加权）")
        rows = sorted(((overlap(s, liked), e["lemma"], s) for e in entries for s in e["senses"]),
                      key=lambda r: (-r[0], r[1]))
        for score in sorted({r[0] for r in rows}, reverse=True):
            names = [f"{lemma}{'*' if s.get('region_override', {}).get(region) else ''}"
                     for sc, lemma, s in rows if sc == score and s.get("role") != "ability"]
            if names:
                print(f"  {score}：{' '.join(names)}")
        print("  （能力词不受地区口味限制，不列；* = 手动加权）")
    for n in notes:
        print("提醒", n)
    for e in errors:
        print("错误", e)
    drafts = sum(s.get("status") == "draft" for e in entries for s in e["senses"])
    print(f"\n{len(entries)} 个词、{sum(len(e['senses']) for e in entries)} 个词条（草稿 {drafts}）：错误 {len(errors)}，提醒 {len(notes)}")
    if args.html:
        write_html(args.html, entries, table)
        print("词卡页：", args.html)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
