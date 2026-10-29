#!/usr/bin/env python3
"""把开源词典变成游戏词条草稿（D-070，说明见 docs/VOCABULARY_PIPELINE.md）。

用法（在仓库根目录）：
    python3 scripts/tools/vocab/build_word_drafts.py            # 名单里全部的词
    python3 scripts/tools/vocab/build_word_drafts.py bind grave  # 只做这几个

读 data/words/word_list.txt，对每个词写 data/words/entries/<词>.json：
- "dictionary" 一半：音标、词典中文、考试标签、常用程度、变形、WordNet 词义与关系。
  **每次运行都重新生成**（词典是原材料，以它为准）。
- "senses" 一半：游戏里用的词条（释义、标签、书页上的话……），由 AI 写草稿、用户检查。
  **已经存在就一个字都不动**；新词只放一个空的 draft 骨架。

原材料放在 dict_sources/（不提交，下载方法见说明文档）：
    dict_sources/ecdict.csv      ECDICT，MIT 许可
    dict_sources/oewn.xml.gz     Open English WordNet 2024，CC BY 4.0
"""
import csv
import gzip
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCES = ROOT / "dict_sources"
WORDS = ROOT / "data" / "words"
ENTRIES = WORDS / "entries"

# 每个词性最多带几个 WordNet 词义（WordNet 按常用程度排序，后面的多半是生僻义）
MAX_SENSES = 6
EXAM_NAMES = {"zk": "中考", "gk": "高考", "cet4": "四级", "cet6": "六级", "ky": "考研",
              "toefl": "托福", "ielts": "雅思", "gre": "GRE"}
FORM_NAMES = {"p": "past", "d": "past_participle", "i": "ing", "3": "third_person",
              "r": "comparative", "t": "superlative", "s": "plural"}
POS_NAMES = {"n": "noun", "v": "verb", "a": "adjective", "s": "adjective", "r": "adverb"}


def read_word_list():
    words = []
    for line in (WORDS / "word_list.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            lemma, role, pos = line.split()
            words.append({"lemma": lemma, "role": role, "pos": pos})
    return words


def read_ecdict(wanted):
    found = {}
    with open(SOURCES / "ecdict.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["word"] in wanted:
                found[row["word"]] = row
    return found


def read_wordnet(wanted):
    """一遍读完 WordNet：要的词的词义，加上把关系目标翻回单词用的对照表。"""
    entries = {}        # lemma -> [(pos, [pron], [(sense_id, synset_id, [(rel, target)])])]
    sense_lemma = {}    # sense id -> lemma（反义、同一家人指向的是 sense）
    entry_lemma = {}    # entry id -> lemma（近义词是 synset 的 members）
    synsets = {}
    with gzip.open(SOURCES / "oewn.xml.gz") as f:
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag == "LexicalEntry":
                lemma_el = el.find("Lemma")
                lemma = lemma_el.get("writtenForm")
                entry_lemma[el.get("id")] = lemma
                senses = []
                for s in el.findall("Sense"):
                    sense_lemma[s.get("id")] = lemma
                    if lemma in wanted:
                        rels = [(r.get("relType"), r.get("target")) for r in s.findall("SenseRelation")]
                        senses.append((s.get("id"), s.get("synset"), rels))
                if lemma in wanted:
                    prons = [(p.get("variety") or "", p.text) for p in lemma_el.findall("Pronunciation")]
                    entries.setdefault(lemma, []).append((lemma_el.get("partOfSpeech"), prons, senses))
                el.clear()
            elif el.tag == "Synset":
                synsets[el.get("id")] = {
                    "members": el.get("members", "").split(),
                    "lexfile": el.get("lexfile"),
                    "definition": (el.findtext("Definition") or "").strip(),
                    "examples": [e.text for e in el.findall("Example") if e.text],
                    "hypernyms": [r.get("target") for r in el.findall("SynsetRelation")
                                  if r.get("relType") == "hypernym"],
                }
                el.clear()
    return entries, sense_lemma, entry_lemma, synsets


def unique(items, skip):
    out = []
    for item in items:
        if item and item != skip and item not in out:
            out.append(item)
    return out


def wordnet_part(lemma, entries, sense_lemma, entry_lemma, synsets):
    senses, prons = [], []
    for pos, entry_prons, entry_senses in entries.get(lemma, []):
        prons += entry_prons
        for sense_id, synset_id, rels in entry_senses[:MAX_SENSES]:
            syn = synsets[synset_id]
            hyper = []
            for h in syn["hypernyms"]:
                hyper += [entry_lemma.get(m, m) for m in synsets[h]["members"][:2]] if h in synsets else []
            senses.append({
                "synset": synset_id,
                "pos": POS_NAMES.get(pos, pos),
                "category": syn["lexfile"],
                "definition": syn["definition"],
                "examples": syn["examples"][:2],
                "synonyms": unique([entry_lemma.get(m, m) for m in syn["members"]], lemma),
                "antonyms": unique([sense_lemma.get(t) for r, t in rels if r == "antonym"], lemma),
                "family": unique([sense_lemma.get(t) for r, t in rels if r in ("derivation", "pertainym")], lemma),
                "broader": unique(hyper, lemma),
            })
    return senses, prons


def phonetic(prons, ecdict_row):
    # WordNet 的是标准 IPA（分英美）；ECDICT 的是旧式写法，只在 WordNet 没有时用
    by_variety = {}
    for variety, text in prons:
        by_variety.setdefault(variety, text)
    if by_variety:
        return {"uk": by_variety.get("GB") or by_variety.get(""), "us": by_variety.get("US")}
    old = (ecdict_row or {}).get("phonetic")
    return {"uk": old, "us": None, "note": "ECDICT 旧式音标"} if old else {}


def dictionary_part(word, ecdict_row, wn_senses, prons):
    row = ecdict_row or {}
    forms = {}
    for part in (row.get("exchange") or "").split("/"):
        if ":" in part:
            key, value = part.split(":", 1)
            if key in FORM_NAMES:
                forms[FORM_NAMES[key]] = value
    tags = (row.get("tag") or "").split()
    return {
        "phonetic": phonetic(prons, row),
        "zh": (row.get("translation") or "").replace("\\n", "\n").splitlines(),
        "exam": [t for t in tags if t in EXAM_NAMES],
        "frequency": {
            "bnc_rank": int(row.get("bnc") or 0) or None,
            "modern_rank": int(row.get("frq") or 0) or None,
            "collins_stars": int(row.get("collins") or 0),
            "oxford_3000": row.get("oxford") == "1",
        },
        "forms": forms,
        "wordnet": wn_senses,
        "missing": [name for name, ok in (("ecdict", ecdict_row), ("wordnet", wn_senses)) if not ok],
    }


def skeleton(word):
    return [{
        "id": f"{word['lemma']}#",
        "pos": POS_NAMES[word["pos"]],
        "wordnet": "",
        "sense": "",
        "zh": "",
        "role": word["role"],
        "tags": [],
        "appears": [],
        "stage_lines": {"ENCOUNTERED": "", "RECOGNIZED": "", "UNDERSTOOD": "", "USABLE": ""},
        "challenge": {"recognize": "", "produce": ""},
        "confusable": [],
        "relations": {"synonyms": [], "antonyms": [], "family": []},
        "constellation": "",
        "page_line": "",
        "status": "draft",
    }]


def main():
    words = read_word_list()
    only = set(sys.argv[1:])
    if only:
        words = [w for w in words if w["lemma"] in only]
    wanted = {w["lemma"] for w in words}
    print(f"读词典（{len(wanted)} 个词）……")
    ecdict = read_ecdict(wanted)
    wn = read_wordnet(wanted)
    ENTRIES.mkdir(parents=True, exist_ok=True)
    for word in words:
        path = ENTRIES / f"{word['lemma']}.json"
        old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        wn_senses, prons = wordnet_part(word["lemma"], *wn)
        entry = {
            "lemma": word["lemma"],
            "dictionary": dictionary_part(word, ecdict.get(word["lemma"]), wn_senses, prons),
            "senses": old.get("senses") or skeleton(word),
        }
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        d = entry["dictionary"]
        flag = f"  缺：{','.join(d['missing'])}" if d["missing"] else ""
        print(f"{word['lemma']:<11} {'/'.join(EXAM_NAMES[t] for t in d['exam']) or '-':<22} "
              f"WordNet {len(d['wordnet'])} 义  {'已有草稿' if old.get('senses') else '新骨架'}{flag}")


if __name__ == "__main__":
    main()
