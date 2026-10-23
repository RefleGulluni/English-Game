# English Game — Claude 工作说明

Godot 4.7 项目。一款以“理解即力量”为核心的回合制 Roguelike：玩家（Wordbearer）在概念、语言与现实断裂（The Fracture）的世界里，靠真正理解的英语单词获得行动能力。第一个 Biome 是 Cemetery。

运行方式、当前切片范围和历史系统见 [README.md](README.md)。

## 设计文档（Obsidian，只读参考）

位于 `/Users/mac/Library/Mobile Documents/iCloud~md~obsidian/Documents/English Game/`：

- `English_Game_World_Bible_v1.md` — 世界观总纲（玩法哲学、概念、角色、Cemetery 怪物与场景顺序）。
- `English_Game_Art_Direction_Bible_v3_Pixel_World_SpecLocked_CLEAN.md` — **当前最高优先级的美术规范**（用户手动保存的最新清理版）。
- `..._v3_Pixel_World.md` 与 `..._v3_Pixel_World_SpecLocked.md` — v3 的早期版本，已被 `_CLEAN` 替代，不要再引用。
- `English_Game_Art_Direction_Reset_Brief_v2.md` — 已被 v3 替代，仅作历史参考。

该文件夹里还有许多过时文件。不要自行扫描整个文件夹，按需阅读上面列出的文件，或等用户指定。

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
  当前 `project.godot` 仍是 1280×720 视口；改成 960×540 原生 + 整数缩放前需征得用户同意。
- 仍待定：正式调色板、描边强度、Camera zoom、地面瓦片尺寸（预计 32 px 左右）。

## 当前进度（2026-10-23）

- 像素美术方向的决定与 Godot 实现细节：[docs/PIXEL_V3_VALIDATION.md](docs/PIXEL_V3_VALIDATION.md)。主角与 Lexicon：[docs/HERO_DESIGN.md](docs/HERO_DESIGN.md)。

- 美术方向已换代到 v3。**Pixel Validation Room** 原型：[scenes/prototypes/pixel_room/pixel_room.tscn](scenes/prototypes/pixel_room/pixel_room.tscn)（SubViewport 原生分辨率 + 整数缩放 + Y-Sort + 碰撞 + 接触阴影 + 语言层；按键切换尺寸、分辨率、语言风格，F 全屏）。地面目前是程序生成的占位。
  用户不熟悉 Godot 编辑器操作：需要看效果时，直接用 `Godot --path . <scene>` 在后台为用户启动窗口，并提醒先点击画面、按 F 全屏。
- 第二批素材 `art/cemetery_pixel_v1/` 已在 [scenes/prototypes/graveyard_room/graveyard_room.tscn](scenes/prototypes/graveyard_room/graveyard_room.tscn) 中验证（T 切换 瓦片 / 地面板 / 目标图）。
  **用户实机结论（2026-10-22）：地面用整张 Ground Decoration Plate；所有高物件独立（Y-Sort + 角色在后方时物件半透明 + 碰撞）**。双网格瓦片效果明显不如地面板，降为可选方案。
  物件 = 立体部分 + 平面“底座贴花”（`*_base.png`，地面层、与物件同原点）；已交付并验证，树不再漂浮。v3 `_CLEAN` 文档已由 Claude 直接更新（用户授权）。
  已实现并经用户确认的规则：
  - 角色在高物件后方时，**整个物件（立体部分 + 底座）一起**渐变为半透明；两层重叠且颜色相同的像素只保留在底座里，避免叠加出深色带。
  - 有底座的物件不再加程序接触阴影；Y-Sort 排序点在立体部分真正落地的位置（不是 PNG 底边）。
  - 枯树碰撞是覆盖树根的椭圆（用户指定范围）。
  - 用户不喜欢角色描边（代码保留，默认关闭，O 键切换）。
  - 已知问题：横向伸展很宽的物体（如低矮的树枝）与角色处于同一深度时，前后关系难以分辨。可考虑的美术规则：树枝长在角色头顶以上（离地约 100 px 以上）。
- **主角已定稿（2026-10-23）**：B1，记录世界的男性旅人。决定过程、文件清单、已知问题与待办见 [docs/HERO_DESIGN.md](docs/HERO_DESIGN.md)。
  - **标准图就是原版 `art/character_design/hero_B1.png`，一个像素都不改**（包括书上的青蓝小印记）。`hero_B1_book*.png`（v1～v4）都是废稿。
  - 四方向：`hero_B1_front/back/left/right.png` + `hero_B1_turnaround.png`，已接受。右侧偏弱（偏驼、提灯看不清），做动画时顺手修。
  - 高清参考：`reference/hero_B1_concept_hires.png`（检查走样用，不是游戏素材）。
  - 旧主角素材（`art/cemetery_pixel_v1/player_anim/` 等）作废。**下一步：主角动画。**
- **Lexicon = 主角腰间的实体书**（World Bible 第 6、8.1、12.1、36 节）：打开的界面就是翻开的书，书页四种状态对应四个学习阶段。
  **学会的单词永远不会丢失**。书封符号：三个节点 = Concept/Language/Reality，底边断开 = Fracture，外圈 = Lexicon，中心点 = 主角（已写入 World Bible §8.1）。
  大书封用完整符号（`lexicon_book_sheet.png` 质量很好，保留）；角色身上的小印记是它的“缩写”，不要求一样。
- `art/cemetery_kit_v2/` 与 `scenes/prototypes/terrain_v2/`、`scripts/prototypes/terrain_v2/` 是已废弃的 Stone/Mud Dual-Grid 研发记录，不进入正式生产。
- [docs/MODULAR_2_5D_CONTRACT.md](docs/MODULAR_2_5D_CONTRACT.md) 等运行时文档写于 v3 之前；其中的美术相关约定若与 v3 冲突，以 v3 为准，并在修改代码前与用户确认。

## 接下来可以做的事（2026-10-23 交接时）

1. **主角动画**：待机 → 四方向行走 → 翻书（打开 Lexicon）→ 战斗动作。先给角色设计组写需求，交付后放进 graveyard_room 实机验收（顺手修右侧图）。
2. **Lexicon 界面**设计（书页星图、单词卡片、四个学习阶段的显示）。
3. 其他验证场景：Abandoned Station、Eleanor's Shop。
4. 接手正式游戏代码：先读 README 与 `docs/` 运行时文档，出一份现状报告；把 `project.godot` 改为 960×540 原生 + 整数缩放（需用户同意）。
5. 未定设想：锚点上的符号带着缺失的底边，靠近时三角补全 = 锚定。

## 团队分工（2026-10-22 起）

- **Claude**：全部程序（Godot 代码、场景、原型与正式游戏）；参与部分方向决定；为美术组撰写素材需求与提示词，并在 Godot 中验收素材。
- **Codex 角色设计组**（2026-10-23 新开）：主角与角色设计，交付到 `art/character_design/`。
- **Codex 美术组**：按需求生成素材，交付到 `art/` 并附 `qc/*_QA.md`。
- **Codex 方向组**：维护 Obsidian 中的设计文档（World Bible、Art Direction Bible 等）。文档修改建议写成可直接转发给方向组的文字。
- 用户在三方之间转达消息。给某一组的文字要明确标注“发给谁”。
- 过渡期：此前由 Codex 程序组编写的正式游戏代码，接手前先阅读 README 与 `docs/` 中的运行时文档；若工作区有不是本人做的未提交改动（例如 `project.godot`、`addons/godot_ai/`），先向用户确认来源再处理。

## 协作约定

- 用户用中文交流，不是程序或美术专业出身：解释用通俗语言，给明确建议而不是罗列选项。用户希望听到直接、大胆的意见。
- 美术素材由 Codex 生成并写入同一个仓库（常在 `art/` 下，附 `qc/*_QA.md` 检查记录）。**写入素材文件夹前先查看里面已有什么**，不要覆盖 Codex 的交付。
- 未经用户确认，不要修改 `scenes/main.tscn`、`project.godot` 与 `main` 分支；新实验放在 `prototypes/` 子目录下。
- Godot 可执行文件：`/Applications/Godot.app/Contents/MacOS/Godot`。可以用 `--path . <scene> -- <args>` 运行场景并在脚本里截图验证效果。
