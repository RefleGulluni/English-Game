# 第一批词汇与词条样子（草稿）

2026-10-29。方向见知识库决策日志 D-069 与 `02_SYSTEMS/02_Learning/English_Game_Learning_System_Current_Reference.md` §3、§8。名单用户已挑（按 Claude 推荐 + 用户加的 raven、moss、bell）。**词条属性用户已同意（D-070）**：在第一版字段上加考试标签与常用程度、音标、词的关系、星座、书页上的一句话，能力词再加词类符号。

## 1. 第一批名单（43 个）

| 用途 | 词 |
|---|---|
| 能力词（10） | strike, shatter, deflect, bind, observe, restore, reveal, anchor, seal, mend |
| 敌人词（10） | erode, wither, conceal, linger, haunt, mourn, reassemble, scatter, decay, crumble |
| 墓园里的东西（13） | grave, shroud, bone, lantern, chapel, gate, statue, fountain, fog, epitaph, raven, moss, bell |
| 气氛词（5） | grief, silence, memory, hollow, remains |

- 中文是大概意思，不是正式释义；考试标签（四级 / 六级 / 考研 / 雅思）以后由工具从词典数据自动填，不手写。
- 现有代码里的词（`cemetery_words.gd` 12 个、`combat_content.gd` 的战斗词、`learning_schedule.gd` 的家族）都在这份名单里，迁移时不丢。

## 2. 一个词条分两半

- **内容**（这个文件说的）：词本身是什么、在墓园里怎么出现、怎么考、能干什么。跟游戏一起打包，所有玩家一样。
- **玩家进度**（存档）：学到哪个阶段（ENCOUNTERED → RECOGNIZED → UNDERSTOOD → USABLE）、熟悉度、怎么学会的（Memory Trace）。每个玩家不一样，见知识库 §8。

## 3. 内容字段

| 字段 | 意思 |
|---|---|
| `id` | 词 + 词义，如 `bind#restrain`（一个词有几个词义就有几条） |
| `lemma` / `pos` / `forms` | 原形、词性、变形（变形以后从词典自动填） |
| `sense` | 游戏里显示的英文释义：短、白话 |
| `zh` | 中文：默认不显示，Lexicon 里可以点开 |
| `role` | ability / enemy / thing / mood |
| `family` | 概念家族（DECAY、HIDDEN、PARTS……），同家族的词互相带 |
| `regions` | 在哪些地区出现、比重多少；不合的地区不出现 |
| `appears` | 世界里在哪里遇到它（物件、墓志铭、敌人意图、对白） |
| `stage_lines` | 四个阶段各自看到的样子：没学会时看到的提示越来越清楚 |
| `challenge` | 推进阶段时的小考：语境里认出来 / 新语境里用对 |
| `confusable` | 容易混的词，答错时用来判断错在哪 |
| `effect` | 只有能力词有：效果种类 + 数字 |
| `exam` / `frequency` | 考试标签（四级 / 六级 / 考研 / 雅思）和常用程度：学习模式靠它调比重。**词典自动填** |
| `phonetic` | 音标（发音音频以后再加）。**词典自动填** |
| `relations` | 近义、反义、同一家人（erode → erosion）：Lexicon 星座的线靠它连。词典给底子，AI 整理 |
| `constellation` | 学会后亮在书里哪一片星座 |
| `page_line` | Lexicon 单词页上一句世界口吻的话。AI 写草稿，用户挑 |
| `sigil` | 只有能力词有：单词栏上的词类符号（9 个之一，D-067），出手时的几何 |
| `status` | draft（AI 写的草稿）/ approved（检查过） |

先不加：常用搭配（以后）、发音音频（以后）、玩家笔记（属于进度，不放词条）。

## 4. 四个样子

### 4.1 bind（能力词）

```
id: bind#restrain          lemma: bind   pos: verb   forms: binds, bound, binding
sense: to tie or hold something so it cannot move
zh: 捆住；束缚
role: ability              family: CONTROL（沿用现在战斗代码）
regions: cemetery 1.0（以后各地区通用）
appears:
  - 物件：门柱上缠着锈铁链的铁门（gate）
  - 墓志铭：“Bound to this ground until the bell is rung.”
stage_lines:
  ENCOUNTERED: 词形残缺，只看得出 b_nd
  RECOGNIZED:  “让什么东西动不了”
  UNDERSTOOD:  “束缚目标：它下一次移动或攻击被推迟”
  USABLE:      可以用来出手
challenge:
  recognize: 看铁门的锁链，选出 bind 的意思（4 选 1）
  produce:   骷髅要重组时，从 bind / scatter / echo 里选能阻止它的词
confusable: bend（形近）, find（形近）, hold（近义但更弱）
phonetic: /baɪnd/        exam: （工具填）
relations: 近义 tie, restrain；反义 release, free；一家人 bound, binding
constellation: 束缚（CONTROL）
page_line: "Some things are held not by chains, but by the words that name them."
sigil: control
effect: { type: delay_intent, turns: 1, cost: 2 }（和现在游戏里一样）
status: draft
```

### 4.2 erode（敌人词）

```
id: erode#wear_away        lemma: erode  pos: verb   forms: erodes, eroded, eroding
sense: to wear something away slowly
zh: 侵蚀；慢慢磨掉
role: enemy                family: DECAY
regions: cemetery 1.0（雨水、风化），其他地区少量
appears:
  - 物件：字被磨平的墓碑（epitaph 看不清）
  - 敌人意图：骷髅头顶的 ERODE
stage_lines:
  ENCOUNTERED: 头顶只看到“er—”和一团灰
  RECOGNIZED:  “它要慢慢削弱什么”
  UNDERSTOOD:  “护甲 -4，腐朽 +12，可以用 STABILIZE 挡”
  USABLE:      能在对白和事件里选它作答
challenge:
  recognize: 墓碑上的字被雨水磨平了——哪个词形容这件事？
  produce:   敌人要 ERODE 你，选出能抵消它的词
confusable: corrode（近义，化学的）, wither（同家族，但用于生命）
phonetic: /ɪˈrəʊd/       exam: （工具填）
relations: 近义 wear away, corrode；反义 build up；一家人 erosion
constellation: 腐朽（DECAY）
page_line: "Rain is patient. Every name here will be smooth stone one day."
effect: —（敌人词没有玩家效果；战斗数字写在敌人数据里）
status: draft
```

### 4.3 lantern（墓园里的东西）

```
id: lantern#lamp           lemma: lantern  pos: noun   forms: lanterns
sense: a lamp in a case with a handle, carried or hung
zh: 提灯；灯笼
role: thing                family: LIGHT
regions: cemetery 0.8, abandoned_station 0.5
appears:
  - 物件：倒在路边的路灯 / 守墓人的提灯
  - 事件：“A lantern still burns on a grave no one visits.”
stage_lines:
  ENCOUNTERED: 走近时物件上方浮出词形
  RECOGNIZED:  看一眼就知道是“那盏灯”
  UNDERSTOOD:  事件里能读懂和它有关的句子
  USABLE:      对白里能用它回答
challenge:
  recognize: 走到物件旁，从 3 张图里选出 lantern
  produce:   守墓人问“What do you need to see in the fog?”
confusable: lamp（近义）, candle（同场景）
phonetic: /ˈlæntən/      exam: （工具填）
relations: 近义 lamp；同场景 candle, light
constellation: 光（LIGHT）
page_line: "Some lanterns are lit not to show the way, but to show that someone still remembers."
effect: —
status: draft
```

### 4.4 grief（气氛词）

```
id: grief#sorrow           lemma: grief  pos: noun
sense: deep sadness, especially after someone dies
zh: 悲痛
role: mood                 family: GRIEF（和 mourn 同家族）
regions: cemetery 1.0
appears:
  - 墓志铭：“Here lies the grief of a whole village.”
  - 哀悼天使雕像的说明文字
  - 敌人：哀悼者类敌人的描述
stage_lines:
  ENCOUNTERED: 墓志铭里这个词是糊的
  RECOGNIZED:  “一种很重的难过”
  UNDERSTOOD:  能分清 grief 和 mourn（一个是感情，一个是表达）
  USABLE:      对白里能用
challenge:
  recognize: 读天使雕像的说明，选出 grief 的意思
  produce:   mourn 和 grief 填空，分清动词和名词
confusable: mourn（同家族，动词）, sorrow（近义）, greed（形近）
phonetic: /ɡriːf/        exam: （工具填）
relations: 近义 sorrow；一家人 grieve, grievous；同家族 mourn
constellation: 哀悼（GRIEF）
page_line: "The village left. Its grief stayed, and learned the names of every stone."
effect: —
status: draft
```

## 5. 还没定的

- 星座怎么分（现在按概念家族先分，等 Lexicon 正式界面时再定）；
- 原材料是否用 ECDICT + WordNet；谁写草稿（建议 AI 写、工具检查、用户抽查）；
- 能力词的效果数字由战斗设计定，表里只是举例。
