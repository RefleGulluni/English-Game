# 词条怎么做（词汇流水线）

2026-10-29（D-071）。一句话：**开源词典当原材料 → 工具自动填能填的 → AI 写游戏内容草稿 → 检查工具 + 用户抽查 → 跟游戏一起打包的词库**。玩家完全离线，碰不到原材料。词条有哪些属性见 [VOCABULARY_FIRST_BATCH.md](VOCABULARY_FIRST_BATCH.md)。

## 1. 文件在哪

| 东西 | 位置 | 提交吗 |
|---|---|---|
| 原材料：ECDICT 英汉词典 | `dict_sources/ecdict.csv`（约 63 MB） | 不提交（`.gitignore`；有 `.gdignore`，Godot 不导入） |
| 原材料：Open English WordNet 2024 | `dict_sources/oewn.xml.gz`（约 13 MB） | 不提交 |
| 要做的词 | `data/words/word_list.txt`（原形 用途 词性） | 提交 |
| 标签表 + 地区喜欢的标签 | `data/words/tags.json` | 提交 |
| **词库（成品）** | `data/words/entries/<词>.json`，一个词一个文件 | 提交 |
| 抽查用的词卡页 | `docs/reference/word_cards_batch01.html`（浏览器打开） | 提交 |
| 来源与许可 | `data/words/CREDITS.md` | 提交 |

下载原材料（换电脑或删了以后）：

```bash
mkdir -p dict_sources && touch dict_sources/.gdignore
curl -L -o dict_sources/ecdict.csv https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv
curl -L -o dict_sources/oewn.xml.gz https://github.com/globalwordnet/english-wordnet/releases/download/2024-edition/english-wordnet-2024.xml.gz
```

## 2. 一个词条文件分两半

- `dictionary`：**工具每次重新生成**，以词典为准：音标（WordNet 的 IPA，没有时用 ECDICT 旧式音标）、词典中文、考试标签（中考 / 高考 / 四级 / 六级 / 考研 / 托福 / 雅思 / GRE）、常用程度（BNC 排名、现代语料排名、柯林斯星级、牛津 3000）、变形、WordNet 前几个词义（释义、例句、近义、反义、一家人、上位词）。
- `senses`：游戏用的词条，一个词义一条。**工具永远不改已经写过的**；AI 写草稿（`status: draft`），用户看过改成 `approved`。`wordnet` 字段指向选中的那个词义，近义 / 反义 / 一家人从它带过来再删改。

## 3. 做一批新词

1. 在 `word_list.txt` 加行；
2. `python3 scripts/tools/vocab/build_word_drafts.py`（几秒；只给新词放空骨架）；
3. AI 填 `senses` 草稿（选 WordNet 词义、写释义、标签、阶段、小考、易混、书页上的话；能力词加 `sigil` 和 `effect`，没定的效果标 `"proposed": true`、阶段文字写【提案】）；新标签先加进 `tags.json`；
4. `python3 scripts/tools/vocab/check_words.py --html docs/reference/word_cards_batchNN.html`：错误必须是 0；最后列出每个词和每个地区重合几个标签（0 = 进暂存池，除非 `region_override` 手动加权）；
5. 用户在词卡页抽查 → 改 `status`；
6. Godot 测试 `tests/word_data_smoke.gd` 确认游戏能读。

## 4. 规则

- `approved` 的词条里不能还有【提案】/【待…】（检查工具会报错）。
- 书页上的话必须是原创句子，不引用名人名言、歌词、书里的原文。
- 词典中文只是参考；游戏里显示的 `zh` 由 AI 按选中的词义重写，默认隐藏、Lexicon 里点开。
- 同一个词的不同词义（grave 坟墓 / 严肃的）是不同的词条，各自学习；变形（erode / eroded）共享一个学习状态（0.7 墓园设计 §10）。
