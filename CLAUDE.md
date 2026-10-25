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

- **The world is pixel and broken. Language is precise and luminous.**（2026-10-22 用户实机选择后修订，v3 原句为 “smooth and precise”）
  语言层（Word Sigil、Lexicon、True Words）与世界使用**同一像素密度**，靠发光、唯一的饱和青蓝色、精确几何、不受雾/阴影/环境色影响、平稳动画与世界区分。
  例外：需要阅读学习的长段英文（释义、例句、对话）使用清晰易读的字体。
- North Star：Cemetery 像素对比测试图的 P 版本。
- 屏幕上世界元素像素密度必须一致：整数缩放、nearest 过滤、避免半像素。
- 角色、敌人、NPC 严格真像素 + 帧动画；AI 生成的“伪像素”必须先整理（网格 → 调色板 → 边缘）再入库。
- 场景分层：远景大图 / 平面 Ground Decoration Plate / 不可见逻辑 TileMap（碰撞、导航）/ 独立高物件（Y-Sort、碰撞、遮挡）/ 角色 / 前景 / 光雾 VFX / 平滑语言层。
- Ground Plate 只能包含平面信息；有高度、要交互、要遮挡的东西必须是独立素材。
- 推荐生产方法：先整体生成一张场景，再拆出高物件并补全地面。
- Fracture 只表现为“关系错误”，**永远不破坏像素网格**，禁止 glitch 类效果；Redactor 是干净的缺失。
- 角色素材不画地面投影，接触阴影与统一光色在 Godot 中处理。
- Cemetery 地面：湿泥 + 稀疏枯草为主；石板只作为残缺小路（“曾经有秩序，现在秩序正在失效”）。
- **已实机选定（2026-10-22）：主角原生高度 96 px，原生画面 960×540**（1080p 屏幕 2 倍、4K 4 倍；主角约占屏幕高度 18%）。测试素材在 `art/pixel_test/size_96/`，共享调色板 `art/pixel_test/shared_palette.gpl`。
  当前 `project.godot` 仍是 1280×720 视口（原型用 SubViewport 实现 960×540）；改 `project.godot` 前需征得用户同意。
- 仍待定：正式调色板、Camera zoom、每类房间地面板数量与生成流程（描边：用户偏好不加）。

## 当前进度（2026-10-24 交接）

### 一句话
设计知识库已理顺；像素 v3 美术方向、主角 B1 与第一批动画、Lexicon 灰盒都已在原型里验证通过；正式游戏代码已通读，**规则层可留用、画面层要按 v3 重做**。下一步是把两者接成新的正式 Broken Graveyard。

### 正式游戏代码（[docs/CODE_STATUS_REPORT_2026-10-24.md](docs/CODE_STATUS_REPORT_2026-10-24.md)）
- **完整的一局游戏是 0.8 Mini Run**（`scenes/ui/legacy_combat.tscn`，README 叫它 legacy，但它功能最全：六层墓地路线、学习导演、12 张牌、六种敌人含两阶段 Boss）。主场景 `main.tscn` 指向 0.9 美术接入单场景试玩版（`scenes/world/world_broken_graveyard.tscn`）。两者共用同一套规则代码。
- 绿（留用）：`scripts/combat/combat_state.gd` 等战斗规则、`scripts/run/learning_schedule.gd` 等学习调度、`run_state` / `run_manager` / `pacing_director`、`scripts/loot/*`、事件契约；**28 套 smoke 测试全部通过**（`for t in tests/*_smoke.gd; do Godot --headless --path . --script res://$t; done`）。
- 黄（要改）：词汇写死在 `scripts/run/cemetery_words.gd`（14 个词，以 lemma 为单位）→ 要改成 Word Sense 数据文件；Lexicon 只是文字弹窗（`slice_combat_hud.gd` 的 `show_lexicon()`）；战斗界面是卡牌按钮。
- 红（重做）：0.9 切片的画面层（1280×720、128 格瓦片、旧主角骨骼拆件动画）。

### 像素 v3 原型（新画面的零件都在这里）
- [scenes/prototypes/graveyard_room/graveyard_room.tscn](scenes/prototypes/graveyard_room/graveyard_room.tscn)：960×540 SubViewport + 整数缩放、整张地面板、独立物件 + 底座贴花 + 后方半透明、Y-Sort、接触阴影、B1 四方向待机 / 行走、**Tab 打开 Lexicon**（`lexicon_overlay.gd` + 主角翻书动画）。T 切换地面、O 描边、F 全屏。截图模式 `-- --capture=<目录>` 会按游戏速度逐帧拍行走和 Lexicon。
- 已确认规则：整个物件（立体 + 底座）一起半透明；有底座的物件不加程序阴影；Y-Sort 点在立体部分落地处；枯树碰撞是树根椭圆；**不加角色描边**；主角接触阴影 36×14、比脚底高 3 px。
- 已知问题：低矮横伸的树枝与角色同深度时前后难辨（可考虑规则：树枝在离地约 100 px 以上）。
- 更早的 [scenes/prototypes/pixel_room/pixel_room.tscn](scenes/prototypes/pixel_room/pixel_room.tscn) 是尺寸 / 分辨率 / 语言风格对比用的。细节：[docs/PIXEL_V3_VALIDATION.md](docs/PIXEL_V3_VALIDATION.md)。

### 主角 B1 与动画（[docs/HERO_DESIGN.md](docs/HERO_DESIGN.md)；知识库 `02_SYSTEMS/06_Character_and_Animation/`）
- 原版 `art/character_design/hero_B1.png` 是设定图，**一个像素都不改**；游戏里的正面用正对镜头的 `hero_B1_front_straight.png`；背 / 左 / 右为 `hero_B1_back/left/right.png`（左右不镜像）。
- **只做 4 个方向**，斜走显示侧面。
- 已通过：四方向待机（4 × 500 ms）+ 行走（8 × 100 ms）、翻开 Lexicon（仅正面，6 × 70 ms + 看书循环，合书 = 倒放）。文件在 `art/character_design/anim/`，graveyard_room 自动加载。
- 动画通用规则：[docs/HERO_ANIMATION_REQUEST.md](docs/HERO_ANIMATION_REQUEST.md) 第 7 节（整帧绘制、提灯挂手、侧面锁脚 / 正背面原地踏步、呼吸只动上半段、与站姿四段亮度差 ≤ 2、头部复用站姿像素）。
- 验收流程：先读 QA → 脚本核对（半透明、新颜色、着地行 y=95、待机首帧 = 站姿、标准图哈希、四段亮度）→ 截图模式出游戏内 GIF → 开窗口让用户走走停停。**用户在游戏里的直觉很准**，数字检查和用户实看缺一不可。
- 已知小问题：侧面行走比站姿亮 4～6 灰度，用户看不出，暂不处理。旧主角素材（`art/cemetery_pixel_v1/player_anim/`、`art/cemetery_kit_v1/player/`）作废。

### Lexicon
- 实体书（World Bible §8.1）；书封符号定稿；**学会的单词永远不会丢失**。
- 灰盒已定：开合约 0.45 秒、大号书、背景压暗、主角转向镜头翻书。
- **游戏会有 15,000～20,000+ 个单词**：结构为“星图总览 → 星座 → 单词页”+ 搜索 + 按阶段筛选；ENCOUNTERED 显示为残缺但认得出的字形。界面设计见知识库 `02_SYSTEMS/02_Learning/English_Game_Lexicon_Interface_Design.md`（其中 [提案] 尚未确认）。

### 已废弃
`art/cemetery_kit_v2/`、`scenes|scripts/prototypes/terrain_v2/`（Stone/Mud Dual-Grid 研发记录）；0.9 切片的骨骼拆件美术。`docs/MODULAR_2_5D_CONTRACT.md` 等运行时文档写于 v3 之前，美术约定与 v3 冲突时以 v3 为准，改代码前与用户确认。

### Git 状态
- `main` 已包含到 0.9 + 像素原型 + 主角 + 代码报告的全部工作，**2026-10-24 已推送到 GitHub**。
- 当前分支 `chore/handoff-notes`：只多了几条交接记录与 `.gitignore`（忽略 `art_source/backups/`），**尚未合回 main**。下一阶段开新分支前可先把它合进 main。
- **Claude 推送不了 GitHub**（这台机器的命令行没有 GitHub 登录）；推送由用户在 GitHub Desktop 里点 Push origin。用户切分支时若 GitHub Desktop 问“changes 怎么处理”，先查 `git status` 再告诉用户选哪个。
- 另一个工作区 `~/Documents/GitHub/English-Game-art`（分支 `feature/mini-run-0.9-art`）有 2 个提交和 19 处未提交改动，都是已作废的骨骼拆件美术，没动过。

## 接下来可以做的事（按建议顺序）

1. **新的正式 Broken Graveyard**（2026-10-25 第一版灰盒，分支 `feature/broken-graveyard-v3`）：`scenes/world/broken_graveyard_v3.tscn` + `scripts/world/v3/`。v3 画面层 + 0.9 的规则接线（照搬 `scripts/world/broken_graveyard.gd`），走动 → 原地开战 → 骨堆 → 掉落 → 出口选路 → 换房间（快速淡黑）→ 换区域（慢淡黑 + 区域名），截图模式 `-- --capture=<目录>` 会自动打完一整圈。
   - 960×540 + 整数缩放由场景自己在启动时设置，**`project.godot` 没改**（改了会让 1280×720 的 0.8 完整一局被裁切；等 `main.tscn` 切到新场景时再一起改）。
   - 灰盒部分：代码画的占位骷髅（等角色组交付，需求见 `docs/SKELETON_DESIGN_REQUEST.md`）、0.9 战斗 HUD 缩到 0.75 倍、出口符号与第 2 房间 / Veiled Walk 内容都是占位、出口路线是写死的（还没接 `cemetery_director` 的随机节点）、掉落物凿子是 0.9 的 11 px 素材几乎看不见。
   - 场景切换规则见知识库 D-022 / D-023 与 `03_WORLD_AND_LEVELS/English_Game_Scene_Structure_and_Transitions.md`。
   - 注意：iCloud 把 `~/Documents/GitHub` 替身改名成了 `GitHub 2`，原位置变成一个只有空文件夹的真目录；仓库请用 `~/Documents/GitHub.nosync/English-Game`。
2. **词汇数据化**：把 `cemetery_words.gd` 的词搬到数据文件，以 Word Sense 为单位（学习系统参考 §2、§7、§8）。现在只有 14 个词，越早越便宜。
3. **Lexicon 正式界面第一版**：书 + 真实学习数据 + 星座结构；先请用户拍板界面设计文档里的 [提案]。
4. **战斗表现设计**（Word Sigil、HUD、场景内软锁定）→ 再给角色设计组写主角战斗动作需求。
5. 其他像素验证场景：Abandoned Station、Eleanor's Shop（做 Eleanor 时一并打好 AI NPC 地基：角色状态、知识边界、结构化记忆，见知识库 AI NPC 参考 §10）。
6. 未定设想：锚点上的符号带着缺失的底边，靠近时三角补全 = 锚定。

## 团队分工（2026-10-22 起）

- **Claude**：全部程序（Godot 代码、场景、原型与正式游戏）；参与部分方向决定；为美术组撰写素材需求与提示词，并在 Godot 中验收素材。
- **Codex 角色设计组**（2026-10-23 新开）：主角与角色设计，**也负责主角动画**，交付到 `art/character_design/`（动画在 `anim/`，QA 在 `anim/qc/hero_B1_anim_QA.md`，累计记录）。它的 QA 会如实写出没做到的地方，值得认真读。
  2026-10-25 起**也负责场景物件**（墓碑、墙、铁栏、墓穴……）：按主角的真像素标准在原生尺寸上逐个制作，交付到 `art/cemetery_v3/props/`（D-026，需求 `docs/CEMETERY_PROPS_PIXEL_REQUEST.md`）。**先做物件，通过后再做骷髅设计**（`docs/SKELETON_DESIGN_REQUEST.md`，截至 2026-10-25 尚未发出）。
  2026-10-24 决定暂不新开动画组；等到敌人 / NPC 动画要和主角动画同时做时，再开“怪物 / NPC 组”。对话太长时给同一组开新对话，先读 HERO_DESIGN 与 HERO_ANIMATION_REQUEST 即可接上。
- **Codex 美术组**：按需求生成素材，交付到 `art/` 并附 `qc/*_QA.md`。2026-10-25 起负责**地面与整体构图**；它两轮墓园背景（`art/cemetery_v3/design/`、`style_test/`）都被判定为“被像素化的写实画”，原因是先生成大图再缩小。
- **画风锚点**：北极星图 `art/pixel_test/source/graveyard_P_reference.png`；主角放进去的效果 `docs/reference/northstar_with_hero_B1.png`。给美术相关组写需求时**一定附图片路径**，不要只引用文字。
- **Codex 方向组**：维护 Obsidian 中的设计文档（World Bible、Art Direction Bible 等）。2026-10-24 起 Claude 也可直接修改知识库（见上文“设计知识库”）。
- **每个组就是一个对话**（用户的说法）。不要建议给同一组同时开两个对话；同一组的多件事排先后顺序。只有对话太长时，才给同一组换一个新对话接着做。
- 用户在三方之间转达消息。给某一组的文字要明确标注“发给谁”。
- 过渡期：此前由 Codex 程序组编写的正式游戏代码，接手前先阅读 README 与 `docs/` 中的运行时文档；若工作区有不是本人做的未提交改动，先向用户确认来源再处理。
- `addons/godot_ai/`（及 `project.godot` 里对应的 autoload / 插件项）是用户自己装的，2026-10-24 已提交。它是连接 Godot 编辑器的 MCP 插件，但还没接到 Claude Code：要用得在 Godot 的 Godot AI 面板里对 Claude Code 点 Configure，再开新对话。
- `art_source/backups/` 是美术组 2026-10-22 留下的素材备份，一直未提交，没有动过；处理前问用户。

## 协作约定

- 用户用中文交流，不是程序或美术专业出身：解释用通俗语言，给明确建议而不是罗列选项。用户希望听到直接、大胆的意见。
- 用户不熟悉 Godot 编辑器操作：需要看效果时，直接用 `Godot --path . <scene>` 在后台为用户启动窗口，并提醒先点击画面、按 F 全屏。
- 给 Codex 各组的消息写成可直接转发的文字，开头标明“发给：xxx”。
- 美术素材由 Codex 生成并写入同一个仓库（常在 `art/` 下，附 `qc/*_QA.md` 检查记录）。**写入素材文件夹前先查看里面已有什么**，不要覆盖 Codex 的交付。
- 未经用户确认，不要修改 `scenes/main.tscn`、`project.godot` 与 `main` 分支；新实验放在 `prototypes/` 子目录下。
- 仓库实际位于 `~/Documents/GitHub.nosync/`（`.nosync` 让 iCloud 不同步它），`~/Documents/GitHub` 是指向它的替身，旧路径照常可用（2026-10-24）。原因：仓库放在 iCloud 同步目录里，大批文件变动时 iCloud 会生成成百上千个“ 2”副本。**不要把仓库挪回 iCloud 同步目录。**
- Godot 可执行文件：`/Applications/Godot.app/Contents/MacOS/Godot`。可以用 `--path . <scene> -- <args>` 运行场景并在脚本里截图验证效果。
  截图模式偶尔卡住（例如脚本报错时窗口一直黑着），用后台运行 + 限时（`sleep N; kill`）跑；给用户开新窗口前先 `pkill -f <场景名>` 关掉旧窗口。
- 写给美术组的规则要考虑透视：侧面的“脚锁地面”不能照搬到正面 / 背面（俯视角下前后被压缩），这次因此返工过一轮。规格冲突时，宁可让美术组在 QA 里指出，也不要让它自己猜。
