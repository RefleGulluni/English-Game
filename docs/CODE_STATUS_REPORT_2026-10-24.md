# 游戏代码现状报告（设计 vs 现状）

日期：2026-10-24。撰写：Claude（接手正式游戏代码前的第一次通读）。
依据：Obsidian 知识库（Entry Guide v2.1、Current Canon、学习系统 / Lexicon / AI NPC / 主角整合参考、决策日志）对照本仓库代码。
**只读，没有修改任何游戏代码、`main.tscn` 或 `project.godot`。**

---

## 1. 一句话结论

**代码分两层：一层是“规则大脑”（战斗、学习、Run、掉落），质量好、28 套测试全部通过，可以留用；另一层是“画面”（场景、角色、界面），是按已经作废的旧美术方向做的，需要按像素 v3 重做。**

---

## 2. 现在能玩到什么

| 入口 | 内容 |
|---|---|
| **主场景**（F5 运行） | 0.9 Broken Graveyard 切片：走路 → 按 E 进门 → 靠近骷髅进入场景内战斗 → 用手牌（Word Action）、Retain、DEFLECT → 骷髅倒下变骨堆（3 回合后重组）→ Echo（15 + 5）→ 掉落凿子实体 → 走过去按 E 拾取 → 进背包。L 打开文字版 Lexicon，Tab 打开背包，R 重玩，F2 是测试面板 |
| **旧版 0.8 场景**（只做回归测试） | 完整的 Mini Run：带种子的六层墓地路线、学习导演、12 张牌的牌组、Ghost / Skeleton / Wraith / Mourning Keeper、恢复节点、遗物三选一、开发面板 |

规模：非原型代码 44 个脚本、约 6,300 行；测试 28 套，**本次全部通过**（2026-10-24 实测）。

---

## 3. 能直接留用的（绿色）

| 系统 | 主要文件 | 与设计的对照 |
|---|---|---|
| 战斗规则 | `scripts/combat/combat_state.gd`、`semantic_effects.gd`、`inattention_rules.gd`、`deck_state.gd` | Focus 3 / Retain / Structure 与 HP 分离 / EXPOSED / 三种 Corruption / Inattention v2 阈值与回落 / ERODE、TOXIC / Bone Remains 重组：**与 Gameplay Spec 一致**。规则层不依赖画面，可以无界面运行测试 |
| 学习调度 | `scripts/run/learning_schedule.gd`、`word_knowledge.gd`、`pacing_config.gd` | 四阶段、Familiarity 与阶段分开、一个 Encounter 只推进一个大阶段、间隔 2 个 Encounter、学习连续上限、四种学习节奏、**跨局保存到本地**：**与 Mini Run 0.8 和学习系统整合参考一致** |
| Run 与节奏 | `run_state.gd`、`run_manager.gd`、`pacing_director.gd` | HP / Corruption 跨战斗保留、Boss 前保证恢复、Risk Floor、功能标签：与 0.8 一致 |
| 掉落 | `scripts/loot/*` | 掉落先是世界里的实体、手动拾取、普通 10% / 测试强制、一具尸体只判定一次、凿子没有被擅自加效果：**与 0.9 Loot 规则一致** |
| 事件契约 | `scripts/systems/gameplay_events.gd` 等 | 使用 Gameplay Spec §7 的事件名（`combat_started`、`enemy_collapsed`、`loot_picked_up`……）：**“程序决定发生了什么，表现层监听事件”的结构是对的** |
| 测试 | `tests/*_smoke.gd` | 28 套，覆盖战斗、学习、地图、UI、切片 |

> 之前的 Codex 程序组做得很扎实：规则和画面是分开的，数值集中在配置里，没定的东西（如凿子效果）也没有乱编。

---

## 4. 需要改的（黄色）

| 问题 | 现状 | 设计要求 | 建议 |
|---|---|---|---|
| **词汇写死在代码里** | `scripts/run/cemetery_words.gd` 用常量写了 14 个词，以“词”（lemma）为单位 | 学习单位是 **Word Sense**；**新增词 = 新增数据，不是改代码**；要能扩到 15,000～20,000+（学习系统参考 §2、§7.5） | 先把词汇搬到数据文件（每个 Word Sense 一条记录），代码只负责读取。**这是两万词的地基，越早越便宜** |
| **Lexicon 是一段文字** | `slice_combat_hud.gd` 的 `show_lexicon()` 弹出“单词 · 阶段 · 释义”的列表 | 实体书、四阶段书页样子、星图三层缩放（Lexicon 界面设计） | 用已经验证过的 Tab 灰盒原型，接上真实的学习数据 |
| **战斗界面偏“卡牌”** | 手牌是按钮，只有 OBSERVE / SHATTER / ERODE 三个词有 Word Sigil 控件 | “Word 是力量，不是单词卡”，不用扑克牌式卡框（0.9 总体设计 §13）；Semantic Deck“历史上重要，但不等于强制卡牌游戏” | 规则（手牌、Retain、Mulligan）可以保留，**表现**按 Word Sigil 做；具体战斗界面需要单独设计 |
| 旧版 0.8 界面 | `scripts/ui/combat_screen.gd` 1,530 行 | 只做回归测试 | 暂时保留（测试依赖它），不再往里加功能 |
| 学习存档名 | `user://learning_schedule_0_8.json` | — | 正式版前改名并做版本迁移，避免老存档丢失 |
| 无用的旧入口 | `scripts/main.gd` 仍显示 “Combat Prototype 0.1” | — | 已不被主场景使用，可以清理 |

---

## 5. 需要重做的（红色）：画面层

0.9 切片是在**像素方向确定之前**做的，用的是已被取代的美术方向：

| 项目 | 现在的切片 | 当前美术标准（Art Bible CLEAN、决策日志） |
|---|---|---|
| 画面分辨率 | 1280×720 | **960×540 原生 + 整数缩放** |
| 地面 | 128 单位一格的瓦片 + 混合层 | **整张 Ground Decoration Plate**；高物件独立 + 底座贴花 |
| 主角 | 约 118 高的骨骼拆件（Skeleton2D / Bone2D）旧主角，前后两套 + 镜像 | **B1，96 px 真像素帧动画**，四方向，已全部完成 |
| 骷髅 | 骨骼拆件动画 | 帧动画（或混合），像素风 |
| 语言层 | 平滑控件 | 与世界同像素密度、精确发光 |

**好消息：** 新画面的大部分已经在原型里验证过了。`scenes/prototypes/graveyard_room/` 已经有 960×540 原生画面、整数缩放、地面板、独立物件、Y 排序、半透明遮挡、接触阴影、B1 四方向动画和 Lexicon 灰盒。

---

## 6. 两个结构性问题

1. **`main` 分支几乎是空的。** `main` 只到“Combat Prototype 0.1”，之后所有工作（0.3～0.9、像素原型、主角）都在其他分支上，当前分支 `docs/art-kit-v2-request` 比 `main` 多 59 个提交。另外 `feature/mini-run-0.9-art` 被另一个工作区检出。**需要你决定怎么整理**（建议：把当前分支合并进 `main`，以后每完成一个阶段就合一次）。
2. **AI NPC 还没有任何代码**：这符合 0.9 的范围（AI NPC 后端不在 0.9 内）。但按设计，第一版 Eleanor 需要的角色状态、知识边界、结构化记忆和存档结构，**最好在做 Eleanor 场景时一起打好地基**（AI NPC 参考 §10）。

---

## 7. 建议的下一步顺序

| 顺序 | 做什么 | 为什么 | 需要你同意的事 |
|---|---|---|---|
| 1 | **整理 git**：当前分支合并进 `main` | 让 `main` 代表真实进度，之后的工作有干净的起点 | 同意合并 |
| 2 | **新的正式 Broken Graveyard**：用像素原型的画面层 + 现有规则大脑（战斗、学习、掉落、事件） | 一次性把“好的规则”和“对的画面”接起来，这是 0.9 第一优先场景 | 同意把 `project.godot` 改为 960×540 原生 + 整数缩放 |
| 3 | **词汇数据化**：词汇从代码搬到数据文件，以 Word Sense 为单位 | 两万词的地基；现在只有 14 个词，最便宜 | — |
| 4 | **Lexicon 正式界面第一版**：书 + 真实学习数据 + 星座结构 | 灰盒已定好节奏和尺寸 | 星图布局的几个 [提案] 需要拍板 |
| 5 | **战斗表现设计**（Word Sigil、HUD、场景内软锁定）→ 再写主角战斗动画需求 | 先定战斗怎么呈现，再画动作，避免返工 | 战斗界面方向 |

旧的 0.9 切片场景先保留不删，直到新场景通过验收；旧测试继续作为回归保障。
