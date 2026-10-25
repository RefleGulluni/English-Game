# English Game — Claude 工作说明

Godot 4.7 项目。一款以“理解即力量”为核心的回合制 Roguelike：玩家（Wordbearer）在概念、语言与现实断裂（The Fracture）的世界里，靠真正理解的英语单词获得行动能力。第一个 Biome 是 Cemetery。

运行方式、当前切片范围和历史系统见 [README.md](README.md)。

## 设计知识库（Obsidian）

位于 `/Users/mac/Library/Mobile Documents/iCloud~md~obsidian/Documents/English Game/`，2026-10-24 由用户整理为分层结构：
`00_HOME`（入口）/ `01_CURRENT_CANON`（当前最高标准）/ `02_SYSTEMS`（专项）/ `03_WORLD_AND_LEVELS` / `90_ARCHIVE`（研发历史）/ `95_ORIGINS`（最初灵感）。

- **先读 `00_HOME/English_Game_Knowledge_Base_Entry_Guide_v2_FULL.md`**：文档分级、阅读顺序、冲突优先级、任务型索引（做什么读什么）。
- **`00_HOME/English_Game_Decision_Log.md`**：所有已拍板决定的时间线。**用户每拍板一个影响设计或制作的决定，就在末尾追加一条**，并更新对应文档。
- 冲突优先级：Current Canon → Current Systems → World/Level → High-Value Archive → Origins → Superseded。美术永远以 `01_CURRENT_CANON/..._SpecLocked_CLEAN.md` 为准。**冲突时不要自己融合出第三个版本，列出来问用户。**
- 旧 ≠ 不重要：`95_ORIGINS/.../NPC.md`、Core Framework v1.4.3、Mini Run 0.4 / 0.8 等仍保存核心思想。
- 系统整合参考（2026-10-24 由 Claude 建立）：`02_SYSTEMS/02_Learning/` 下的 Learning System Current Reference 与 Lexicon Interface Design、`02_SYSTEMS/05_AI_NPC/`、`02_SYSTEMS/06_Character_and_Animation/`。
- **2026-10-24 起 Claude 获授权直接维护知识库**：可以新增文档、给过时段落加修订注释、标 Superseded；**不删除历史文档**，大改前先备份（备份在 `/Users/mac/Documents/English Game KB Backups/`）。Codex 方向组也维护知识库，同时改同一文件前先请用户协调。
- 分工：知识库放“是什么、为什么”；本仓库 `docs/` 放给美术组的具体需求、像素规格、验收数据和实现说明。仓库里拍板的事要回写到知识库（Entry Guide §38.5）。

## 美术方向（v3 摘要，细节以 Art Direction Bible v3 `_CLEAN` 为准）

- **The world is pixel and broken. Language is precise and luminous.** 语言层（Word Sigil、Lexicon、True Words）与世界**同一像素密度**，靠发光、唯一的饱和青蓝色、精确几何、不受雾 / 阴影 / 环境色影响与世界区分。长段可读英文用清晰字体（`art/ui/fonts/CormorantGaramond.ttf`）。
- **主角原生 96 px，原生画面 960×540**，整数缩放、nearest、避免半像素。`project.godot` 仍是 1280×720；新场景在启动时自己设 960×540（见下文），改 `project.godot` 前需征得用户同意。
- 场景分层：地面板（只含平面信息）/ 底座贴花 / 不可见逻辑碰撞 / 独立高物件（Y-Sort、遮挡、后方整件半透明）/ 角色 / 前景 / 光雾 / 语言层。角色和物件不画地面投影，接触阴影在 Godot 做；不加角色描边。
- Fracture 只表现为“关系错误”，永远不破坏像素网格，禁止 glitch。
- **画风锚点**：主角 B1 = **精致程度**的标准；北极星图 `art/pixel_test/source/graveyard_P_reference.png` = **感觉**的参照（明暗、冷暖、饱和度、像素密度），**不是颜色仓库**，每个地区有自己的颜色（D-027）。主角放进北极星图：`docs/reference/northstar_with_hero_B1.png`。
- **像素素材怎么做、怎么验收：[docs/PIXEL_ASSET_PIPELINE.md](docs/PIXEL_ASSET_PIPELINE.md)**（必读）。一句话：单件生成大方块像素风 → 找到真实像素格、一格还原一个像素 → 逐块整理 → 先一件试样进游戏 → 再批量。要拼接的零件以同家族已有零件为底子改出来。检查工具：`python3 scripts/tools/pixel_check.py <文件>`（颜色数、相邻像素换色比例与主角对比；主角 44 色 / 88%）。
- 整张场景图只用来定构图，不再是最终素材（D-026，Art Bible §15 已加注释）。地面板的真像素做法还没验证。
- 美术素材目录：[art/README.md](art/README.md)（在用 / 参考 / 作废，各自被谁引用）。新增或作废美术文件夹时同步更新。

## 当前进度（2026-10-25 交接）

### 一句话
新的正式 Broken Graveyard 灰盒已能从头玩到尾；墓园正式美术找到了可行的方法：角色组用新流程做的第一批 9 件物件和全部墙补件已通过，下一批是墓碑家族与小物件。

### 新的正式 Broken Graveyard（分支 `feature/broken-graveyard-v3`）
- `scenes/world/broken_graveyard_v3.tscn` + `scripts/world/v3/`：v3 画面层 + 0.9 的规则接线（照搬 `scripts/world/broken_graveyard.gd`）。走动 → 原地开战（不黑屏）→ 骨堆 → 掉落 → 出口选路 → 换房间（快速淡黑）→ 换区域（慢淡黑 + 发光区域名）。截图模式 `-- --capture=<目录>` 自动打完一整圈。
- 零件：`hero_b1.gd` + **可拖入的主角场景 `scenes/player/hero_b1.tscn`**（帧打包在 `hero_b1_frames.tres`，交付新动画后运行 `scripts/tools/bake_hero_b1.gd` 重新打包）；`cemetery_room.gd`（按布局数据建房间，支持 `prop_dir`、物件名带子目录、不给碰撞时按物件的脚自动生成一条）；`room_exit.gd`（出口 + 语言层符号）；`screen_fade.gd`；`skeleton_placeholder.gd`（代码画的灰色占位骷髅）。
- 灰盒 / 待办：占位骷髅；0.9 战斗 HUD 缩到 0.75 倍并半透明（战斗表现还没设计）；出口路线是写死的（**用户说先不接**随机算法 `cemetery_director`，等用户说再接）；第 2 房间与 Veiled Walk 是占位；凿子掉落物太小；Lexicon 用的是原型的灰盒书（Tab），L 是旧的文字词表。
- 960×540 由场景启动时设置，`project.godot` 没改（改了会裁切 1280×720 的 0.8 完整一局；等 `main.tscn` 切到新场景时再一起改）。
- 28 套 smoke 测试全部通过（`for t in tests/*_smoke.gd; do /Applications/Godot.app/Contents/MacOS/Godot --headless --path . --script res://$t; done`，看输出里的 `: PASS`；macOS 没有 `timeout` 命令）。

### 关卡结构（知识库 `03_WORLD_AND_LEVELS/English_Game_Scene_Structure_and_Transitions.md`）
- D-022：场景不无缝拼接，单屏房间；同区域换房间快速淡黑（约 0.4 秒），换区域慢淡黑 + 区域名（约 2～3 秒）；从哪边出去就从对侧进来。
- D-023：出口即选路，出口上方有发光符号（符号外观待设计）。
- D-024：**随机路线算法管“发生什么”，区域管“长什么样”**。一局 6 层 → 4 个区域（外墓园 1～2 层 / 雾中墓径 3～4 / 黑雾深处 5 / 哀悼礼拜堂 6 Boss）；World Bible 的 7 个场景变成房间类型（Entry 固定第一间、各区域战斗房、休息 = Sheltered Grave、事件 = Ossuary 类、Boss = Mourning Chapel）；区域只偏向某些敌人，不锁定。区域英文名待定。

### 墓园美术（`art/cemetery_v3/`）
- 美术组两轮整图背景（`design/`、`style_test/`）未通过：是“被像素化的写实画”。构图方向 A 残墙院落 / B 雾坡 / C 下沉尚未正式选。
- **角色组物件第一批 9 件（第 2 版）已通过（D-029）**，在 `props/`，第 1 版在 `props/qc/backups/round1/`。墙分两个家族、同一排不混用：A 乱石墙 `low_wall_01`；B 条石墙 `low_wall_broken_01` + `wall_pillar_01`（作门柱）+ `iron_fence_01`。
- **墙补件已验收（D-030）**：A 加了乱石断墙、乱石嵌柱（像墙上隆起的一段，作变化段）；B 的完整条石墙 `low_wall_ashlar_01` 同一块石头重复，**保留作次要变体**（用户：有瑕疵的素材也不浪费）。
- **条石墙主力 `low_wall_ashlar_02` 通过（D-032）**：有效宽 240（画布 288）；02 接 01 或断墙间隔 187，01 接 02 间隔 181。
- **进行中**：第二批墓碑家族（5 种新形状 + 3 件歪斜 / 断裂）与 4 件小物件，需求 `docs/CEMETERY_PROPS_BATCH2.md`（**等用户转发**）。
- 试走验收房间：`scenes/prototypes/props_v3/props_v3_room.tscn`（WASD、T 色调、F 全屏；在脚本 `LAYOUT` 加一行即可摆新物件）。地面暂用 `cemetery_pixel_v1` 样板地面板。
- 待办：墓穴碰撞（现在主角能走进坑里）；墓园物件偏暖黄，等真像素地面出来再整体看；墓园子调色板等物件齐了从实际用色里整理。
- 之后的顺序：第二批“墓碑家族”（更多形状 + 歪斜 / 断裂）与小物件 → Grave Skeleton 设计（`docs/SKELETON_DESIGN_REQUEST.md`，**尚未发出**）→ 美术组做真像素地面。
- 多样性（D-028）：形状家族 × 状态 × 换颜色（调色板替换）× 下沉深浅 × 摆放规则。**像素画不能旋转、不能左右镜像。**

### 主角 B1 与动画（[docs/HERO_DESIGN.md](docs/HERO_DESIGN.md)；知识库 `02_SYSTEMS/06_Character_and_Animation/`）
- 原版 `art/character_design/hero_B1.png` 是设定图，**一个像素都不改**；游戏正面用 `hero_B1_front_straight.png`；背 / 左 / 右分别画，不镜像。只做 4 个方向。
- 已通过：四方向待机（4 × 500 ms）+ 行走（8 × 100 ms）、翻开 Lexicon（仅正面）。动画通用规则见 [docs/HERO_ANIMATION_REQUEST.md](docs/HERO_ANIMATION_REQUEST.md) 第 7 节。主角接触阴影 36×14、比脚底高 3 px。
- 主角战斗动作：等战斗表现设计后再写需求。

### 正式游戏代码（[docs/CODE_STATUS_REPORT_2026-10-24.md](docs/CODE_STATUS_REPORT_2026-10-24.md)）
- 完整的一局是 0.8 Mini Run（`scenes/ui/legacy_combat.tscn`）；`main.tscn` 指向 0.9 试玩版（`scenes/world/world_broken_graveyard.tscn`）。规则层（`combat_state`、`learning_schedule`、`run_manager`、`pacing_director`、`scripts/loot/*`、事件契约）留用。
- 词汇写死在 `scripts/run/cemetery_words.gd`（14 个词）→ 要改成 Word Sense 数据文件。
- 旧原型：`scenes/prototypes/graveyard_room/`（v3 画面层的起点，Lexicon 灰盒）、`pixel_room/`（尺寸对比）。v3 之前写的运行时文档（如 `docs/MODULAR_2_5D_CONTRACT.md`）美术约定与 v3 冲突时以 v3 为准。

### Lexicon
- 实体书；学会的单词永远不会丢失；灰盒已定：开合约 0.45 秒、大号书、背景压暗、主角转向镜头翻书。
- 游戏会有 15,000～20,000+ 个单词：星图总览 → 星座 → 单词页 + 搜索 + 按阶段筛选。界面设计见知识库 `02_SYSTEMS/02_Learning/English_Game_Lexicon_Interface_Design.md`（[提案] 尚未确认）。

### Git 状态
- `main` 与 GitHub 同步（含交接记录）。当前工作都在分支 **`feature/broken-graveyard-v3`**（2026-10-25 起，十几个提交，**未合回 main、未推送**）。
- **Claude 推送不了 GitHub**；推送由用户在 GitHub Desktop 里点 Push origin。
- `.import` 文件：Godot 导入时自动生成，素材的 `.import` 一般随素材一起提交。

## 接下来可以做的事（按建议顺序）

1. 验收第二批墓碑家族与小物件 → 发骷髅设计需求。
2. 新墓园灰盒：接随机路线算法（用户说等他说再接）；墓穴碰撞；换上正式物件。
   - **关卡制作方向（D-031）**：地面由 AI 整体生成；单体素材做成可拖入的“积木”场景（图片 + 底座贴花 + 遮挡 + 默认碰撞），由用户在编辑器里摆房间、调碰撞，手工房间组成随机算法的房间池。**用户说先攒够素材再做这个试验**，不要提前做。
3. **词汇数据化**：`cemetery_words.gd` → Word Sense 数据文件（学习系统参考 §2、§7、§8）。
4. **Lexicon 正式界面第一版**：先请用户拍板界面设计文档里的 [提案]。
5. **战斗表现设计**（Word Sigil、HUD、场景内软锁定）→ 主角战斗动作需求。
6. 其他场景：Abandoned Station、Eleanor's Shop（AI NPC 地基见知识库 AI NPC 参考 §10）。

## 团队分工

- **Claude**：全部程序；参与方向决定；给各组写需求（附图片路径、同时写上限和下限）、在 Godot 里验收；**主动维护知识库**（用户拍板就记）。
- **Codex 角色设计组**：主角、角色、敌人、NPC 及动画，**以及场景物件**（D-026）。交付到 `art/character_design/`、`art/cemetery_v3/props/`。QA 会如实写出没做到的地方，值得认真读。
- **Codex 美术组**：地面与整体构图（构图图只定位置和空间）。等物件标准定下后再给它写真像素地面的需求。
- **Codex 方向组**：维护知识库设计文档；同时改同一文件前先请用户协调。
- **每个组就是一个对话**：同一组的多件事排先后顺序，不并行开两个对话；只有对话太长时才给同一组换新对话（开场模板见制作手册 §10）。**写好的需求要等用户转发，不要默认已经发出。**
- 用户在各组之间转达消息；给某组的文字开头标明“发给：xxx”，写成可直接转发的中文。
- `addons/godot_ai/` 是用户装的 Godot MCP 插件，还没接到 Claude Code。`art_source/backups/` 是美术组的备份，未提交，处理前问用户。

## 协作约定

- 用户用中文交流，不是程序或美术专业出身：解释用通俗语言，给明确建议而不是罗列选项。用户希望听到直接、大胆的意见。
- 用户不熟悉 Godot 编辑器操作：需要看效果时，直接用 `Godot --path . <scene>` 在后台为用户启动窗口，并提醒先点击画面、按 F 全屏。
- 给 Codex 各组的消息写成可直接转发的文字，开头标明“发给：xxx”。
- 美术素材由 Codex 生成并写入同一个仓库（常在 `art/` 下，附 `qc/*_QA.md` 检查记录）。**写入素材文件夹前先查看里面已有什么**，不要覆盖 Codex 的交付。
- 未经用户确认，不要修改 `scenes/main.tscn`、`project.godot` 与 `main` 分支；新实验放在 `prototypes/` 子目录下。
- 仓库实际位于 **`~/Documents/GitHub.nosync/English-Game`**（`.nosync` 让 iCloud 不同步它；不要挪回 iCloud 同步目录）。iCloud 后来把替身改名成了 `GitHub 2`，**`~/Documents/GitHub` 现在是空壳，不要用**。Godot 项目列表已指向 `.nosync`；GitHub Desktop 若找不到仓库，让用户点 Locate 选 `.nosync` 路径。
- Godot 可执行文件：`/Applications/Godot.app/Contents/MacOS/Godot`。可以用 `--path . <scene> -- <args>` 运行场景并在脚本里截图验证效果。
  截图模式偶尔卡住（例如脚本报错时窗口一直黑着），用后台运行 + 限时（`sleep N; kill`）跑；给用户开新窗口前先 `pkill -f <场景名>` 关掉旧窗口。
- 写给美术组的规则要考虑透视：侧面的“脚锁地面”不能照搬到正面 / 背面（俯视角下前后被压缩），这次因此返工过一轮。规格冲突时，宁可让美术组在 QA 里指出，也不要让它自己猜。
