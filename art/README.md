# art/ 目录说明

更新：2026-10-25（Claude）。**打开这个文件夹先看这里。** 新增、作废或挪动文件夹时，请同步更新本文件。

所有游戏美术素材都在 `art/` 里，按“批次”存放，新旧混在一起。下面按状态分三类：

- ✅ **在用**：当前方向（像素 v3），新内容以它为准；
- 📎 **参考**：不进游戏，或马上会被替换，只作对照 / 记录；
- ⛔ **作废**：旧方向，**不要参考、不要沿用**。没删除，是因为旧的 0.8 / 0.9 版本还在引用它们。

画风唯一标准：知识库 `01_CURRENT_CANON/English_Game_Art_Direction_Bible_v3_Pixel_World_SpecLocked_CLEAN.md`。
**怎么做像素素材、怎么验收：[docs/PIXEL_ASSET_PIPELINE.md](../docs/PIXEL_ASSET_PIPELINE.md)**；一键检查：`python3 scripts/tools/pixel_check.py <文件>`。

## ✅ 在用

| 文件夹 | 内容 | 制作 | 用在哪里 |
|---|---|---|---|
| `character_design/` | **主角 B1**：四方向站姿（`hero_B1_*.png`，游戏里的正面是 `hero_B1_front_straight.png`）、全部动画（`anim/`）、Lexicon 书的设计图（`lexicon_book_sheet.png`）。**墓园骷髅** `enemies/skeleton/`：选定 B「余裹者」`skeleton_B.png` + 骨堆（D-037），A / C 留作精英参考；B 四方向已通过（D-041）。`hero_B1.png` 是设定图，**一个像素都不改** | 角色设计组 | 可拖入的主角 `scenes/player/hero_b1.tscn`（帧由 `scripts/tools/bake_hero_b1.gd` 打包） |
| `cemetery_v3/backdrop/` | **墓园入口远景条**（天空 + 天际线 + 礼拜堂）与**前景枯枝**（D-042）；礼拜堂放大版 `entry_backdrop_02` 制作中 | 美术组 | 入口灰盒 `scenes/prototypes/cemetery_entry/` |
| `cemetery_v3/ground/trial/` | 地面试样（D-035）：质感好但太暖，拼接失败；地面已改为瓦片 + 贴花（D-043），这块只作颜色质感对照 | 美术组 | 试走房间 `-- --plate=` |
| `cemetery_v3/ground/base/` | **在用**：两块 224×128 大块无缝泥地底子（D-049 / D-054） | 美术组 | 刷路房间 `Ground/Base`（`ground_base_tileset.tres`） |
| `cemetery_v3/ground/decals/` | **在用**：20 件地面贴花（D-054），已做成可拖的积木 `scenes/props/cemetery/decals/`（`scripts/tools/bake_ground_decals.gd`，2026-10-28） | 美术组 | 刷路房间 `Ground/Decals` |
| `cemetery_v3/ground/transitions/` | **在用**：`path_texture_01.png` 碎石泥路、`grass_texture_01.png` 枯草苔藓地、`paving_texture_01.png` 旧石板路（D-056 / D-057 / D-061）；`masks/` 是 Claude 程序生成的形状和瓦片集；`qc/*failed_candidate*` 是作废的 16 块整图记录 | 美术组 + Claude | 刷路房间 `Ground/Path`、`Ground/Grass`、`Ground/Paving`；方法 `docs/GROUND_TERRAIN_METHOD.md` |
| `cemetery_v3/ground/tiles/` | **作废**：32×32 泥地瓦片试样（失败记录，制作手册第 9 条） | 美术组 | 无 |
| `cemetery_v3/props/` | **墓园物件**（墓碑、十字碑、墓穴、盖板、矮墙、墙柱、铁栏），每件有立体部分 + `_base` 底座贴花。**第 2 版 9 件已通过（D-029）**，第 1 版在 `qc/backups/round1/`。墙分两个家族、同一排不混用：A 乱石墙 `low_wall_01`；B 条石墙 `low_wall_broken_01` + `wall_pillar_01`（也作门柱）+ 铁栏。补件（D-030）：A 加了乱石断墙 `low_wall_rubble_broken_01`、乱石嵌柱 `low_wall_rubble_pillar_01`（墙的变化段）；B 加了完整条石墙 `low_wall_ashlar_01`（有重复感，作次要变体）。条石墙主力 `low_wall_ashlar_02` 已通过（D-032，有效宽 240）。第二批墓碑家族与小物件 12 件已通过（D-033）。每件都有对应的积木场景 `scenes/props/cemetery/<名字>.tscn`（D-034）。补件的来源与拼装图在 `qc/wall_family_sources/`、`qc/wall_family_*` | 角色设计组 | 试走房间 `scenes/prototypes/props_v3/props_v3_room.tscn` |
| `ui/word_sigil_v3/` | **战斗里的词标志**：设计稿（`design/`，用户选 B 基线 + 衬线字 + 第 3 档精致度）与 9 个 11×11 **词类符号** `glyphs/family_*.png`（2026-10-28 通过） | 美术组 | `scripts/world/v3/combat_view.gd`（单词栏、提示框） |
| `ui/exit_glyphs_v3/` | **出口符号** 9 个 15×15（战斗 / 精英 / 事件 / 未知 / 遗物 / 休息 / 最终 / 换区域 / 未理解），底下共用一条“门槛”（D-065 通过）；`source/` 是美术组的几何源和备份 | 美术组 | `scripts/world/v3/room_exit.gd` |
| `ui/fonts/` | 长段可读英文用的字体 CormorantGaramond（含授权 `OFL.txt`） | — | Lexicon 灰盒、区域名过渡 |

## 📎 参考

| 文件夹 | 内容 | 说明 |
|---|---|---|
| `pixel_test/` | 最早的像素尺寸测试（64 / 96 / 128 px）。**北极星参考图**：`source/graveyard_P_reference.png` | 北极星是画风“感觉”的参照（明暗、冷暖、饱和度、像素密度），不是颜色仓库（D-027） |
| `cemetery_pixel_v1/` | 第一批像素样板：整张地面板、5 件物件与底座、双网格地形 | 灰盒墓园（`scenes/world/broken_graveyard_v3.tscn`）和 graveyard_room 原型**暂时**在用；正式地面和物件做好后替换 |
| `cemetery_v3/design/` | 美术组第一轮墓园背景 A / B / C | 未通过（像“被像素化的写实画”）；构图可参考，画法与颜色不要沿用 |
| `cemetery_v3/style_test/` | 美术组风格统一样品 V1 / V2 | 未通过（整体偏蓝、V2 有分区补丁）；只作记录 |

## ⛔ 作废（旧方向）

| 文件夹 | 内容 | 为什么还在 |
|---|---|---|
| `cemetery_kit_v1/` | 旧的 128 px 瓦片墓园、骨骼拆件主角与骷髅 | 0.9 试玩版（`scenes/world/world_broken_graveyard.tscn`）与其构建脚本在用 |
| `cemetery_kit_v2/` | Stone / Mud 双网格地形实验 | 旧原型 `scripts/prototypes/terrain_v2/` 在用 |
| `characters/` | 0.9 旧主角（骨骼拆件） | 旧 `scenes/player/Player.tscn` 在用 |
| `enemies/` | 0.9 骨骼拆件骷髅 | 旧 `scenes/enemies/GraveSkeleton.tscn` 在用 |
| `environments/` | 0.9 旧墓园场景模块、雾 | 旧预览脚本在用 |
| `loot/` | 0.9 掉落物（凿子，11 px，几乎看不见） | 新灰盒墓园**临时借用**（`scenes/loot/WorldLoot.tscn`），等新掉落物 |
| `ui/`（字体以外） | 0.9 战斗界面主题、Word Sigil | 新灰盒墓园**临时借用**旧战斗面板（`scenes/ui/CombatHUD.tscn`），等战斗表现设计 |
| `vfx/` | 0.9 特效 | 0.9 试玩版在用 |
| `previews/` | 0.9 美术预览与检查脚本 | 只服务旧素材 |

**以后的整理计划**：新墓园正式替换 0.9 试玩版、`main.tscn` 切换之后，把所有 ⛔ 文件夹统一挪进 `art/_archive/`。挪动要在 Godot 编辑器里做，或先改掉引用，否则旧场景会报“找不到文件”。

## 仓库里的其他相关位置

| 位置 | 内容 |
|---|---|
| `art_source/concepts/`、`art_source/production/` | 0.9 时期的原始概念图与生产源文件（Godot 不导入） |
| `art_source/backups/` | 美术组 2026-10-22 的本地备份，**未提交**，不要动 |
| `docs/reference/` | Claude 给各组做的对照图（主角放进北极星图、细节密度对比、实机截图） |
| `docs/*_REQUEST.md`、`docs/*_REVISION_*.md` | 给各组的需求与返修要求 |

## 给各组的约定

- 交付放在需求文档指定的文件夹，并附 `qc/` 检查图和 `*_QA.md`。
- **不要覆盖别人的交付**；返修前先把旧版备份到 `qc/backups/`。
- 写入素材文件夹前，先看看里面已经有什么。
