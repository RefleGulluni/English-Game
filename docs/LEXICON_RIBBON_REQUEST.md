# 发给：Codex 角色设计组 — Lexicon 书签：一张“书脊里没有书签”的摊开书 + 两个流苏

日期：2026-10-31。需求方：Claude（程序），用户拍板（知识库决策日志 D-092）。

摊开书 `art/character_design/lexicon/lexicon_open_clean.png` 在游戏里用得很好，谢谢！这次只要一点小改动。

## 1. 为什么要

书里新加了一个功能：在单词页上点一个相关的词，书会哗哗翻到那个词的那一页。**书签留在原来那一页**，所以：

- 平时：书签躺在书脊里，流苏垂在书底正中（就是你们原画的样子，不变）；
- 跳走以后：书脊里看不到书签了，流苏改成从**左边（或右边）那叠书页底下**垂出来；
- 翻回来：书签又躺回书脊。

现在“书脊里没有书签”的那张图是 Claude 用程序把带子抹掉的，书脊颜色补得不对（缝线右边出现一条发浅、一块一块的带子），快速翻页时一直看得到，用户觉得别扭。所以请你们出这张图，原画是你们画的，你们改最准。

## 2. 要做的两样东西

### A. `lexicon_open_clean_no_ribbon.png`（256×128）

- 以 `lexicon_open_clean.png` 为底子**直接改像素**，不要重新生成；
- **只去掉书签**：书脊里那根带子（大约 x 129～137，从书页顶 y≈13 一直到书底）、它跨过封皮下沿的那一段，以及书底下垂着的流苏（大约 x 132～142，y 117～123）；
- **书脊的缝线和上面的结（大约 x 126）一个像素都不动**；
- 去掉带子后，那一条书脊应该和缝线左边一样，是纸页往书脊里卷进去的自然明暗（可以参考缝线左边的渐变），不要出现一条发浅或一块一块的带子；
- 书的其他任何像素都不改。用同一套颜色，不加新颜色。

### B. 两个流苏：`lexicon_ribbon_tassel_left.png`、`lexicon_ribbon_tassel_right.png`

- 书签从一叠书页底下伸出来、跨过封皮下沿、垂下来的样子：一小段带子 + 流苏；
- `_left` 是挂在**左边那叠书页**下面的，`_right` 是挂在右边的。**不要左右镜像**，各自画（可以有一点点自然的不同，比如往外侧微微偏）；
- 画布 16×16，透明底，只有 Alpha 0 / 255；带子最上面的那个像素放在画布第一行的正中（x = 8），程序会把这一点对准封皮下沿；
- 颜色、粗细、流苏的样子和原画书底的流苏一致（就用原画里那几种棕色）。

## 3. 交付

| 文件 | 内容 |
|---|---|
| `art/character_design/lexicon/lexicon_open_clean_no_ribbon.png` | A |
| `art/character_design/lexicon/lexicon_ribbon_tassel_left.png` / `_right.png` | B |
| `art/character_design/lexicon/qc/ribbon_diff_6x.png` | A 和原图的差异：改过的像素标出来，6 倍 |
| `art/character_design/lexicon/qc/ribbon_spine_6x.png` | 原图和 A 的书脊并排，6 倍 |
| `art/character_design/lexicon/qc/ribbon_tassels_on_book_4x.png` | A 加上左右流苏各挂一次的合成，4 倍 |
| `art/character_design/lexicon/qc/ribbon_QA.md` | 改了哪些像素、颜色数、有没有新颜色；**没做到或拿不准的地方如实写出** |

`lexicon_open_clean.png` 原样保留，不删不改。不要修改仓库里其他任何文件。完成后停下，等用户看。
