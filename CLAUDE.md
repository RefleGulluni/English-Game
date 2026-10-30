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
- 整张场景图只用来定构图，不再是最终素材（D-026，Art Bible §15 已加注释）。**地面的正式做法（D-055 / D-056，用户：“以后就用这个方法”）：[docs/GROUND_TERRAIN_METHOD.md](docs/GROUND_TERRAIN_METHOD.md)**：大块无缝底子 + 用户在 Godot 里亲手刷的过渡层（程序画形状、美术画 224×128 纹理、着色器按位置贴）+ 贴花；所有地图、每个地区照此做。知识库对应页 `03_WORLD_AND_LEVELS/English_Game_Ground_Painting_Method.md`。
- 美术素材目录：[art/README.md](art/README.md)（在用 / 参考 / 作废，各自被谁引用）。新增或作废美术文件夹时同步更新。

## 当前进度（2026-10-29 交接）

### 一句话
墓园入口这个房间基本成形，交给用户亲手调（25 + 9 件入口物件 + 8 件词汇物件都是可拖积木；入口 9 件 D-060 是**以后素材的质量标准**；地面可刷五层：底子 / 枯草 / 苔藓 / 泥路 / 石板 + 20 件贴花）。**v3 墓园的战斗已经“能看”**（场景内战斗 D-063、单词栏 D-067、BONE CUT D-066、出口符号 D-065、碎骨骨灰布丝）。**Lexicon**：开合 D-068、程序翻页 D-072（字跟着纸翻）、三层结构四条规则 D-073 都已定。**词库已建成并接进游戏**（D-069～D-071：ECDICT + WordNet 原材料 → 我们自己的 42 个词条 `data/words/`；战斗数字 / 释义 / 符号都读词库）。**开局一个词都不会**（D-075：序章五站各学一个，开发版默认已会 OBSERVE / STABILIZE / BIND / ANCHOR / STRIKE；新墓园单词栏只放 USABLE 能力词，9 张牌）。**第一条学词路线 SHATTER 已能完整玩通（D-078 / D-079）**：浮词小星 → 事件「碎翼天使」→ 骷髅战借词 → 事件「裂开的石板」→ 进牌。**下一个大目标**：Lexicon 正式设计（学会动效 + 两万词 + 成为游戏招牌），见“接下来”第 1 条。

### 新的正式 Broken Graveyard（分支 `feature/broken-graveyard-v3`）
- `scenes/world/broken_graveyard_v3.tscn` + `scripts/world/v3/`：v3 画面层 + 0.9 的规则接线（照搬 `scripts/world/broken_graveyard.gd`）。走动 → 原地开战（不黑屏）→ 骨堆 → 掉落 → 出口选路 → 换房间（快速淡黑）→ 换区域（慢淡黑 + 发光区域名）。截图模式 `-- --capture=<目录>` 自动打完一整圈。
- 零件：`hero_b1.gd` + **可拖入的主角场景 `scenes/player/hero_b1.tscn`**（帧打包在 `hero_b1_frames.tres`，交付新动画后运行 `scripts/tools/bake_hero_b1.gd` 重新打包）；`cemetery_room.gd`（按布局数据建房间，支持 `prop_dir`、物件名带子目录、不给碰撞时按物件的脚自动生成一条）；`room_exit.gd`（出口 + 语言层符号）；`screen_fade.gd`；**`skeleton_b.gd`（正式骷髅「余裹者」，2026-10-28 接入）**：待机、开战时朝主角走上来（起步 → 整步走 → 停步，每步 40 px）、受击、散架 → 骨堆 → 重组，打完是变暗的骨堆；攻击暂时还是“往前探一下”，等攻击动画。旧的灰色占位 `skeleton_placeholder.gd` 留作参考。
- **战斗表现（D-063 / D-066 / D-067）**：`combat_view.gd` 画全部战斗界面（底部薄单词栏、头顶英文意图、悬停预览、词先出现再飞向敌人、每个词一种像素几何、命中停顿、四周冷雾 `combat_vignette.gdshader`）；骷髅 `stand_off()` 横着走到主角斜对面（左右约 120 px），`hold_for()` 让受击等字打到再播。单词栏 = B 基线 + 衬线字 + 第 3 档（发光、节点菱形、刻度、悬停合拢）+ 用词消失特效；词类符号读 `art/ui/word_sigil_v3/glyphs/`；界面默认暖色、青蓝只给语言（P 切冷色对比）；提示框双细线框。动画：主角 `cast()` 在出手帧放几何、`take_hit()`；骷髅 `attack()` 播 v1（蓄力时整体前移 40 px，命中帧主角受击）、非攻击行动 `shed()` 抖落骨灰；新动画打包：`bake_hero_b1.gd` 的 TIMED 列表（打包后要把 `hero_b1_frames.tres` 头部的 uid 改回 `uid://nlcofgiekvkk`）。截图模式 `--mirror` 让主角站右边。
- 灰盒 / 待办：出口路线是写死的（**用户说先不接**随机算法 `cemetery_director`，等用户说再接）；第 2 房间与 Veiled Walk 是占位；凿子掉落物太小；Tab 打开的 Lexicon 开合已是正式样子，书里的内容（右页 4 个示例词、左页星座取自设计图）还是灰盒；L 是旧的文字词表。
- 960×540 由场景启动时设置，`project.godot` 没改（改了会裁切 1280×720 的 0.8 完整一局；等 `main.tscn` 切到新场景时再一起改）。
- 32 套 smoke 测试全部通过（`for t in tests/*_smoke.gd; do /Applications/Godot.app/Contents/MacOS/Godot --headless --path . --script res://$t; done`，看输出里的 `: PASS`；macOS 没有 `timeout` 命令）。

### 关卡结构（知识库 `03_WORLD_AND_LEVELS/English_Game_Scene_Structure_and_Transitions.md`）
- D-022：场景不无缝拼接，单屏房间；同区域换房间快速淡黑（约 0.4 秒），换区域慢淡黑 + 区域名（约 2～3 秒）；从哪边出去就从对侧进来。
- D-023：出口即选路，出口上方有发光符号。**符号已通过（D-065）**：美术组 9 个 15×15 `art/ui/exit_glyphs_v3/`，`room_exit.gd` 直接读 PNG；“未理解”版（`understood = false`）还没接规则。
- D-024：**随机路线算法管“发生什么”，区域管“长什么样”**。一局 6 层 → 4 个区域（外墓园 1～2 层 / 雾中墓径 3～4 / 黑雾深处 5 / 哀悼礼拜堂 6 Boss）；World Bible 的 7 个场景变成房间类型（Entry 固定第一间、各区域战斗房、休息 = Sheltered Grave、事件 = Ossuary 类、Boss = Mourning Chapel）；区域只偏向某些敌人，不锁定。区域英文名待定。

### 墓园美术（`art/cemetery_v3/`）
- 美术组两轮整图背景（`design/`、`style_test/`）未通过：是“被像素化的写实画”。构图方向 A 残墙院落 / B 雾坡 / C 下沉尚未正式选。
- **角色组物件第一批 9 件（第 2 版）已通过（D-029）**，在 `props/`，第 1 版在 `props/qc/backups/round1/`。墙分两个家族、同一排不混用：A 乱石墙 `low_wall_01`；B 条石墙 `low_wall_broken_01` + `wall_pillar_01`（作门柱）+ `iron_fence_01`。
- **墙补件已验收（D-030）**：A 加了乱石断墙、乱石嵌柱（像墙上隆起的一段，作变化段）；B 的完整条石墙 `low_wall_ashlar_01` 同一块石头重复，**保留作次要变体**（用户：有瑕疵的素材也不浪费）。
- **条石墙主力 `low_wall_ashlar_02` 通过（D-032）**：有效宽 240（画布 288）；02 接 01 或断墙间隔 187，01 接 02 间隔 181。
- **第二批 12 件通过（D-033）**：墓碑家族 5 种新形状 + 3 件歪斜 / 断裂，4 件小物件（不挡路）。
- **物件积木（D-034）**：每件一个场景 `scenes/props/cemetery/<名字>.tscn`（脚本 `scripts/world/v3/cemetery_prop.gd`：原点 = 脚 = Y 排序点；只在主角真被像素挡住时半透明；`flat` 平躺物件不挡人）。由 `scripts/tools/bake_cemetery_props.gd` 从 manifest 生成，**已存在的不覆盖**（用户手调过碰撞）。`CemeteryRoom` 有同名积木就用积木。**用户负责调碰撞**（说明 `docs/PROP_COLLISION_GUIDE.md`），Claude 负责遮挡等程序问题；改完由 Claude 检查提交。新素材入库：`--import` → 跑生成工具。
- 试走验收房间：`scenes/prototypes/props_v3/props_v3_room.tscn`（WASD、T 色调、F 全屏；在脚本 `LAYOUT` 加一行即可摆新物件）。地面暂用 `cemetery_pixel_v1` 样板地面板。
- 待办：墓园物件偏暖黄，等真像素地面出来再整体看；墓园子调色板等物件齐了从实际用色里整理。
- **地面（定型，D-043 → D-057）**：试过整张生成图、32×32 小块、美术画 16 块边角都失败（记录见制作手册第 9、12 条），最终做法见 [docs/GROUND_TERRAIN_METHOD.md](docs/GROUND_TERRAIN_METHOD.md)：`ground/base/` 两块 224×128 底子 + `ground/decals/` 20 件贴花 + `ground/transitions/` 的路面 / 草地 / 旧石板纹理（石板第一版“砖墙”未通过，第二版 D-061 通过；**验收地面纹理拿亮度标准差和已通过地面比**：路 8.2 / 草 14.2 / 底子 9.5 / 石板 13），形状由 Claude 的程序画，用户在刷路房间 `scenes/prototypes/ground_paint/ground_paint_room.tscn` 里亲手刷（`Ground/Base`、`Grass`、`Path`、`Paving`）。**用户刷过的场景是用户的作品，生成工具只补缺的层，不覆盖**。旧的 `-- --plate=<PNG>` 试走方式仍可用。
- **从“地板”到“场景”**：一个场景 = 构图（四周密、中间空、出口）+ 高低差（台阶、挡土墙）+ 地面 + 物件 + 远景 + 前景 + 光雾。**先由用户画房间草图**，Claude 翻译成素材清单、用积木和色块先搭灰盒房间。第一张：**墓园入口**（D-036：下方小路走来 → 中间围墙大门 → 上方墓园展开、远处雾中礼拜堂；每局从词典锚点出发）。
  - 墓园入口灰盒：`scenes/prototypes/cemetery_entry/cemetery_entry_greybox.tscn`（按用户草图：弯路 → 铁栏 + 高门柱大门 → 石板广场 → 干涸喷泉 + 哀悼天使 → 两条小路通向两侧出口；H 开关占位说明，V 看“更低视角”试验版）。**房间从 y = -256 到 1350（`TOP`，D-062 往上加长，原有坐标不变；`CemeteryRoom` 的 layout 可给 `size`、`top`、`grass_top`），镜头只上下跟随**（D-038 → D-044）。场景里：`Ground`（`Base` / `Grass` / `Path` / `Paving` / `Decals`，用户亲手刷）+ `Props`（全部物件积木，用户亲手摆；运行时搬进 Y 排序层，场景没有 `Props` 时才用脚本里的 `LAYOUT`）。喷泉脚底在 (480, 200)；顶部是美术组的远景条 `art/cemetery_v3/backdrop/entry_backdrop_03.png`（天空 + 天际线 + 礼拜堂）放在 `TOP`，下面压一层 Claude 的地平线雾 `scripts/world/v3/horizon_fog.gdshader`（平滑、下沿起伏、缓慢飘动，远处墓碑越远越朦胧）；下角是正式前景枯枝；门柱中心 408 / 552，柱脚门洞净空 92。一次性工具：`build_cemetery_entry_ground.gd`（补缺的地面层）、`build_cemetery_entry_props.gd`（物件放进场景）、`extend_cemetery_entry_top.gd`（往上加长），都不覆盖用户的作品。
  - 素材清单 `docs/CEMETERY_ENTRY_ASSET_LIST.md`：礼拜堂、高门柱、入口其余 9 件（铁门两扇、喷泉、枯树两棵、倒路灯、路牌、木十字架两种）**全部通过**；喷泉按用户意思用生成时的原始大小（池 194×119、天使 57×138，画布 256×256，不删行列——删行穿过斜边会出“横切一刀”）。
- **骷髅选定 B「余裹者」（D-037）**：斜披破裹尸布、右肩两枚铁钉、黑 X 缝线；A / C 留作精英骷髅参考。文件在 `art/character_design/enemies/skeleton/`，四方向站姿通过（D-041）。**动画全部通过**（需求 `docs/SKELETON_ANIMATION_REQUEST.md`，每条用最高 `_vN` 版本，帧在 `anim/`，`timing.json` 由角色组维护）：待机 `_v2`（“几乎不动、偶尔被扯一下”）、受击 `_v2`、行走右 `_v7` / 左正背 `_v5` + 每个方向的 `walk_start_*`、`walk_stop_*`、四个方向的散架（都落成同一个骨堆）、骨堆待机、重组 `_v5`（黑缝线牵头骨、布分 6 帧拉起）。试看房间 `scenes/prototypes/skeleton_anim/skeleton_anim_preview.tscn`（绕圈走每段 40 px 整数倍，转弯起步 / 停步；H 受击；空格 散架 → 重组；V 切最初版对比），帧条播放 `scripts/world/v3/sprite_strip.gd`。**攻击动画**等战斗表现设计后再写。骨头是全画面最亮的颜色，以后看要不要压暗。
- 多样性（D-028）：形状家族 × 状态 × 换颜色（调色板替换）× 下沉深浅 × 摆放规则。**像素画不能旋转、不能左右镜像。**
- **词汇物件 8 件全部通过（D-074 → D-077）**：地上的渡鸦、碑顶渡鸦、苔藓盖名墓碑、坟头小铃、钟架、老井、封死的墓室（返修后门 57×102、整座 176×191，墓园最大地标）、新坟 + 铁锹（返修后深褐湿土）。积木在 `scenes/props/cemetery/`；试看 `props_v3_room.tscn -- --words`。需求 `docs/CEMETERY_WORD_PROPS_REQUEST.md`。**定尺寸教训**：人要穿过 / 走进的东西先按“门 ≥ 主角身高”倒推。老井的“有毒”只靠周围寸草不生，摆在草地边上才明显。
- **雾中墓径底子 `ground/base/veiled_base_01/02` 第二版通过（D-084）**：以外墓园底子一对一换成更暗更冷更湿的色表 + 低对比湿斑（第一版整张重新生成，像灰色迷彩，未通过）；已接进 `vw_1`、`vw_2`（layout `ground_tiles`，去掉了冷蓝调色）。**四个区域明暗方向 D-085**：不一路变暗，黑雾深处靠雾和暗角、礼拜堂烛光亮回来。
- **雾中墓径厚苔藓地 `moss_texture_01` 第二版通过（D-077）**：第一版像鱼鳞（需求写了“一团团苔藓垫”的错），第二版平软连续。刷路房间 `Ground/Moss`，形状 `masks/ground_moss_masks_01`。地面着色器 `ground_path.gdshader` 新增 `macro_strength`（大范围明暗起伏，整像素）：只对苔藓地开 0.08，其余已通过地面默认 0；刷路房间按 M 全部对比，用户以后决定推广。**生成工具 `build_ground_paint_room.gd` 重存瓦片集会丢掉 uid，跑完把未改的 `*_tileset.tres` 用 git checkout 还原。**

### 主角 B1 与动画（[docs/HERO_DESIGN.md](docs/HERO_DESIGN.md)；知识库 `02_SYSTEMS/06_Character_and_Animation/`）
- 原版 `art/character_design/hero_B1.png` 是设定图，**一个像素都不改**；游戏正面用 `hero_B1_front_straight.png`；背 / 左 / 右分别画，不镜像。只做 4 个方向。
- 已通过：四方向待机（4 × 500 ms）+ 行走（8 × 100 ms）、翻开 Lexicon（仅正面）。动画通用规则见 [docs/HERO_ANIMATION_REQUEST.md](docs/HERO_ANIMATION_REQUEST.md) 第 7 节。主角接触阴影 36×14、比脚底高 3 px。
- 主角战斗动作：等战斗表现设计后再写需求。

### 正式游戏代码（[docs/CODE_STATUS_REPORT_2026-10-24.md](docs/CODE_STATUS_REPORT_2026-10-24.md)）
- 完整的一局是 0.8 Mini Run（`scenes/ui/legacy_combat.tscn`）；`main.tscn` 指向 0.9 试玩版（`scenes/world/world_broken_graveyard.tscn`）。规则层（`combat_state`、`learning_schedule`、`run_manager`、`pacing_director`、`scripts/loot/*`、事件契约）留用。
- 词汇写死在 `scripts/run/cemetery_words.gd`（14 个词）→ 要改成 Word Sense 数据文件。
- 旧原型：`scenes/prototypes/graveyard_room/`（v3 画面层的起点，Lexicon 灰盒）、`pixel_room/`（尺寸对比）。v3 之前写的运行时文档（如 `docs/MODULAR_2_5D_CONTRACT.md`）美术约定与 v3 冲突时以 v3 为准。

### Lexicon
- 实体书；学会的单词永远不会丢失；灰盒已定：大号书、背景压暗、主角转向镜头翻书。
- **开合动画（D-068，2026-10-29 按用户的翻法修订，用户已通过）**：书升起、封面正对玩家（符印暗刻）→ 符印亮起 → 书往后仰、立在书脊上，封面之间的缝透青蓝光 → **左右封面同时倒下**摊平 → 星座从书脊亮起、词浮现；书脊全程在屏幕正中；**用户实机调定：翻开约 2.3 秒、合上约 1.8 秒**（倒放，最后又看到封面；“书出现 / 消失”与其余步骤分开计时，常量 `OPEN_RISE` 等），可随时打断。用户对这本书要“从容、有分量”，以后界面动画起点定慢一些。程序已做：`scripts/prototypes/graveyard_room/lexicon_overlay.gd`（v3 墓园按 Tab；1 / 2 / 3 键快 / 正常 / 慢；截图 `-- --capture=<目录> --lexicon`），书的动作现在是灰盒色块，角色组的干净书、符印遮罩、`lexicon_tip_up.png`（3 帧）、`lexicon_covers_fall.png`（5～6 帧）放进 `art/character_design/lexicon/` 后自动换上。需求 `docs/LEXICON_BOOK_ANIMATION_REQUEST.md`；角色组已交全部帧（2026-10-29），已自动换上。用户：“lexicon 是咱们游戏里面很重要的东西，要花很多精力”。符印：三角形 + 中心点一起亮，外圈从上顶点顺时针画出来（`_split_sigil` 按“每个方向最外 3 px”分出外圈；翻开约 2.8 秒，合上和翻开一样慢；书缝的光 `_seam` 找真正的缝 `_find_seam`，中间亮两端淡 + 照亮页边 + 柔光 + 光尘）。星座已改为先一颗颗亮星星、再一条条连线（`_split_sky` 把星和线分开，星座有自己的时钟 `_sky`）。**翻页改为程序计算并通过（D-072）**：两个跨页先画进隐藏的 SubViewport（按窗口真实分辨率，字才清楚），翻页时按书的一像素列绕书脊投影（外边领先、书脊一侧跟上，所以纸是弯的；过竖直露出下一页的对页；站起变暗偏棕；外边下方投影），0.8 秒；D 往后、A 往回各自计算；V 切回角色组 6 帧条带对比。书页内容暂取词库前几个词（每页 4 个，阶段轮流，灰盒）。铅笔字（RECOGNIZED）不动，“不稳”画在笔画里（`_pencil`）。角色组两轮翻页素材已提交（摊开书修整继续用）。未学会的星座以后由程序用铅笔色画。
- 游戏会有 15,000～20,000+ 个单词：星图总览 → 星座 → 单词页 + 搜索 + 按阶段筛选。界面设计见知识库 `02_SYSTEMS/02_Learning/English_Game_Lexicon_Interface_Design.md`；**§4 四条规则已定（D-073）**：总览只画星座（亮度 = 学了多少）、没见过的词不出现、快捷入口（搜索 / 最近 / 复习 / 按阶段）、搜索守权限；翻页只在一层之内；一个词一跨页；星座由语义标签生成。**D-080（用户通过）**：约一千个星座放不下一个跨页 → 书页是看向一整片星空的**窗口**（拖动、分级缩放），星座之上加约 12 个手工定的**天区**；用户要求**放在书上不能突兀**（像画 / 透在书页上，不像贴了个地图软件）。

### Git 状态
- `main` 与 GitHub 同步（含交接记录）。当前工作都在分支 **`feature/broken-graveyard-v3`**（2026-10-25 起，几十个提交，**未合回 main、未推送**）。
- **Claude 推送不了 GitHub**；推送由用户在 GitHub Desktop 里点 Push origin。
- `.import` 文件：Godot 导入时自动生成，素材的 `.import` 一般随素材一起提交。

## 接下来可以做的事（按建议顺序）

1. **新墓园的“第一局”：让学词在世界里发生**（用户已同意方向；先做第 1 步时，单词栏已改好）。目标：开局只会 5 个词 → 在世界里遇到新词（物件旁浮词、敌人意图）→ 玩着玩着学会（事件、战斗）→ 学会新能力词加进牌 → 走完 6 层打 Boss → 翻书看这一局学了什么。顺序：
   - ~~单词栏只放会的词~~ **已做**：`scripts/run/lexicon_progress.gd`（玩家的能力词进度，存 `user://lexicon_progress.json`，没有存档就发 5 个起始词；`COPIES` 定张数 STRIKE 3 / OBSERVE 2 / BIND 2 / 其余 1；ERODE、TOXIC 仍由 0.8 `learning_schedule` 决定）；`deck_state.reset` 接受 `deck_cards`；ANCHOR 效果 = 挡下一次侵蚀（`CombatState.anchored`）；开发键 `-`（或 F5）回到 5 个词、`=`（或 F6）全学会（Mac 上 F5 是语音听写）；测试 `tests/starting_words_smoke.gd`。0.8 完整一局仍用 12 张 `STARTER`。**难度未调**：后台模拟只用 5 个词打骷髅 3 场赢 2 场（7 / 11 回合），输的一场骨堆反复重组拖 37 回合；学会 SHATTER 后 3 场全赢。调数值前先用后台模拟（不要跑截图模式的长战斗，用户会停掉），再请用户实机玩。
   - ~~写“学词在世界里怎么发生”的设计~~ **已定并搭了灰盒（D-078，`docs/FIRST_WORD_ROUTE_SHATTER.md`）**：SHATTER 四步（碎墓碑浮词 → 事件「碎翼天使」选意思 → 骷髅战骨堆时借来一张铅笔 SHATTER → 事件「裂开的石板」从自己的词里选），每次遭遇只前进一格（`lexicon_progress.advance`）。新墓园改为 5 个房间 `bg_1 → bg_2 → bg_3 → vw_1 → vw_2`（写死，不接随机路线）。零件：`scripts/world/v3/word_world.gd`（物件浮词、事件文字框、前进提示）、`event_spot.gd`、剧本卡 `data/events/cemetery/*.json`、书页读真实进度（`lexicon_overlay.set_progress / show_word`）。截图自查 `-- --capture=<目录> --route`。**学会永久、牌组动态**（用户澄清）：会 ≠ 每局都在牌里，牌组怎么组成以后设计。用户已走过一遍。**D-079（用户通过）**：骷髅可以以骨堆登场、走近才重组开战（layout `"dormant": true`，`skeleton_b.lie_dormant() / rise()`；`bg_1`、`vw_2` 是骨堆，`bg_3` 站着）；事件物件上方有淡淡呼吸的“事件”出口符号（`event_spot.show_mark`），走近变淡、做完熄灭。**世界里的词怎么被发现（用户：“提示太好了”）**：没见过的词 = 物件上方会闪的青蓝小星（远处可见），第一次走近字母逐个写出、青蓝冷却成铅笔灰（`word_world._draw_float`）；第一个词挂在 `bg_1` 路边的断十字架 `tombstone_cross_01_broken` 上。**教训**：提示要“一般人走过去就能发现”，不能只靠很近才出现的淡字。待讨论（用户提的，下一步重点）：**学会单词的动效按阶段分轻重**、**Lexicon 正式设计要承载两万词**、Lexicon 要成为游戏最让人记住的地方——先出草图再做。骨堆的进一步想法（学会 SHATTER 后能在它爬起来之前先打碎）记在 D-079，未定。
   - **事件房 + 随机路线**：已和用户讲过做法（事件 = 房间 + 一件物件 + 一张“剧本卡”数据；走近按 E，场景内文字框，选项是会的词；用标签挑事件，同 D-070）。0.8 已有 7 个墓园事件（`scripts/run/cemetery_content.gd` POOL，弹窗式）和随机路线 `cemetery_director.gd`。**用户还没说接路线**；先做一个事件房灰盒试样（建议“被遮住的墓志铭”或用钟架做“余音不散的钟”）时再问。
   - **下一步：Lexicon 正式设计**（用户 2026-10-29：“lexicon 是咱们游戏很特色的地方，要给玩家留下深刻的印象”）。三件事一起设计，**先出草图给用户看再做**：① ~~学会单词的动效按阶段分轻重~~ **已做（D-081 暂定，用户实机看后再调）**：见过 = 腰间书一闪；认得 / 理解 = 右下角探出一角书页（`word_world._draw_slip`，战斗中 `holding` 等到战后）；能用 = `lexicon_overlay.ceremony()`，任意键跳过；**D-082**：能用时主角原地停约 0.8 秒、仪式排队不丢（`_rites`）；见过的词 = 整词写出、后半笔画被擦（`word_erased.gdshader`）；专注力有几颗画几颗、悬停时要花的闪烁、提示框小数目用菱形；**D-083**：仪式不能打断，只能按住空格 / Esc 0.6 秒跳过，玩家第一次的仪式不能跳过（存档 `ceremonies_seen`）；**书页角待和用户讨论再精修**；原设想（见过很轻 → 能用是一场可跳过的小仪式：书自己打开、字母依次亮青蓝、星座里那颗星亮起连线、词飞进单词栏）；② 能承载两万词的界面（D-073：星图总览 → 星座 → 单词页 + 搜索 / 最近 / 复习 / 按阶段）；③ 让它成为招牌（“你的书”的手写痕迹、属于你的星空、书是活的、序章被抹掉再写回）。书页现在已读真实进度（`lexicon_overlay.set_progress`），但还是每页 4 个的灰盒列表。
   - 事件房格式已在 SHATTER 路线里做出（`data/events/cemetery/*.json` 剧本卡 + `event_spot.gd` + `word_world.open_event`）；0.8 的 7 个墓园事件以后照此搬。
2. **词库**（D-069～D-071，[docs/VOCABULARY_PIPELINE.md](docs/VOCABULARY_PIPELINE.md)）：42 个词条草稿通过检查，**用户还没抽查词卡页** `docs/reference/word_cards_batch01.html`；**每个词都必须有书页上的话**（用户定的）。词库面向游戏、不面向玩家（给用户讲解时照这个说）。游戏首次使用时读入内存（`scripts/run/word_library.gd`）；战斗花费 / 释义 / 符号 / 数字（`CombatState.STRIKE_DAMAGE` 等 static var，`CombatContent.SKILLS` 由 `_BASE` + 词库合成）、学会后的释义（`cemetery_words.meaning`）、排程家族（第一个标签）都读词库。待做：reveal / seal / mend 的效果是【提案】、没有战斗逻辑（学会也不进牌）；ERODE“学会后变修饰牌”在词库里怎么表示；0.8 学习界面的例句 / 填空换成 `appears` / `challenge`；第一次导出游戏时确认 `data/words/` 被打包、致谢写上 ECDICT（MIT）与 Open English WordNet（CC BY 4.0），见 `data/words/CREDITS.md`。
3. **等各组交付**：美术组**空闲**（雾中墓径底子已通过）；角色组在做**碎翼天使第三轮**（`docs/BROKEN_WING_ANGEL_REQUEST.md` §4：要“碎”不要“断”，第二版已在 `bg_2`）（词汇物件、苔藓地都已通过）。角色组下一件建议 **Veil Ghost 设计稿**（A / B / C 三选一，雾中墓径的敌人；用户说过“以后再说”，派活前先问）。美术组可做雾中墓径的其他地面（积水地等，照 `docs/GROUND_TERRAIN_METHOD.md` §6）或碎骨 + 翻土坟坑贴花（用户说过**先不做**）。
4. **Lexicon**：开合（D-068）、程序翻页（D-072）、三层结构四条规则（D-073）都已定；正式界面第一版：星图总览 / 星座 / 单词页（先出草图给用户看）。
5. **入口房间**：用户可能还会继续调地面 / 物件 / 碰撞，调完检查再提交（上次 c3009b5）。
6. 新墓园其余：出口符号“未理解”版（`room_exit.gd` 的 `understood`）接规则；第 2 房间、Veiled Walk 是占位。**关卡制作方向（D-031）**：用户刷地面、拖积木摆房间，手工房间组成随机路线的房间池；教用户拖拽摆房间要等素材更多时。
7. 小的待定（见知识库决策日志“待拍板”）：路线总览放哪、四个区域英文名、主角战败动画、墓园构图方向 A / B / C、FORCE 和 PERCEPTION 符号是否太像、骨头是否太亮、词类点缀色、地面明暗起伏要不要推广到外墓园。
8. 其他场景：序章（Abandoned Station → Fractured Passage → Eleanor's Shop → Lexicon Anchor → Redactor → 抹除 → 回到锚点；D-075 定了每站学的词）；AI NPC 地基见知识库 AI NPC 参考 §10。

## 团队分工

- **关卡分工（用户定的）**：用户画房间的主体框架草图，Claude 保留框架、补充细节（比例、有故事的小物件、出口、战斗空地、远景前景），再用积木和色块搭灰盒给用户走。
- **Claude**：全部程序；参与方向决定；给各组写需求（附图片路径、同时写上限和下限）、在 Godot 里验收；**主动维护知识库**（用户拍板就记）。
- **Codex 角色设计组**：主角、角色、敌人、NPC 及动画，**以及场景物件**（D-026）。交付到 `art/character_design/`、`art/cemetery_v3/props/`。QA 会如实写出没做到的地方，值得认真读。
- **Codex 美术组**：地面与整体构图（构图图只定位置和空间）。2026-10-25 用户因旧对话被过时结论污染而**新开了对话**；给它的需求要自带完整背景（见地面试样需求的写法）。
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
