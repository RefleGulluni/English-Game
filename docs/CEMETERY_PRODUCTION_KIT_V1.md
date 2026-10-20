# Cemetery Production Kit v1

范围仅 Broken Graveyard / Cemetery 可复用资产。3/4 Top-Down 2.5D，Painterly Semi-Realistic Dark Fantasy + Geometric Language Surrealism。已验收的概念图保留为 Visual Target，不作为本轮最终地图底图。

## 打开与检查

- 美术工程：`/Users/mac/Documents/GitHub/English-Game-art/project.godot`。
- F5：运行联合接入后的游戏；程序团队负责正式世界、碰撞、运动桥和玩法回归。
- 单独资源浏览：打开 `art/cemetery_kit_v1/previews/kit_catalog.tscn`，F6。可切地面材质、替换 Prop、移动主角、播放 Skeleton 动作和独立 VFX。这是资源采样器，不含游戏结算。
- 动画：`art/cemetery_kit_v1/player/player_rig.tscn`、`art/cemetery_kit_v1/skeleton/skeleton_rig.tscn` 的 AnimationPlayer。由程序组与美术组本轮共同接入。

## 十项交付 / 导入说明

| 交付 | 游戏资源 / 可编辑源 | 透明与拆层 | 尺寸、使用方式 |
|---|---|---|---|
| 1. Cemetery Tile Sheet | `art/cemetery_kit_v1/terrain/cemetery_tileset.tres`；`terrain_mapping.json`；`reviews/01_cemetery_tile_sheet.png` | 六材质基础不透明；80 张混合边缘保留透明；与所有道具、雾、光分开 | 单格256纹理像素，TileMapLayer scale0.5 →128世界单位。source0六材质×四相位；source1五材质×16 NESW边缘。明确映射，不宣称已有Godot terrain_connect。 |
| 2. Wall Module Sheet | `art/cemetery_kit_v1/structures/*.tscn`；`editable/wall_structures.ora`；`reviews/02_wall_module_sheet.png` | 每个PNG独立透明；墙、栏、门基座分开 | 六石结构、正面/纵深铁栏与门、独立立柱，共13scene。直墙/低墙约256单位宽；栏杆192单位宽；详见manifest。使用Prop/结构Scene，非整张背景。 |
| 3. Graveyard Prop Sheet | `art/cemetery_kit_v1/props/*.tscn`；`editable/cemetery_props.ora`；`reviews/03_graveyard_prop_sheet.png` | 18件独立RGBA；无烘焙地面、雾或光 | 8墓碑61–113单位高、2树235/270高、8小物12–38高。全体脚底原点，Sprite2D等比缩放。放入可排序Prop层。 |
| 4. Foreground Asset Sheet | `art/cemetery_kit_v1/foreground/`；`editable/foreground_layers.ora`；`reviews/04_foreground_asset_sheet.png` | 左/右大枝、近墓沿、近铁栏4独立scene；fog_edge为独立RGBA | 枝150高、墓沿63高、栏125高；近景scene已有克制暗色。前景遮挡与淡化由程序实现，雾另放FogLayer，不随地面变透明。 |
| 5. Player Rig Sheet | `art/cemetery_kit_v1/player/parts/*.png`；`player_rig.tscn`；`editable/player_rig_parts.ora`；`reviews/05_player_rig_sheet.png` | 正向20件+背向头/躯干/肩披/裙摆4件，共24透明PNG | 118单位整人体目标，脚底(0,0)。Skeleton2D/Bone2D、可编辑AnimationPlayer，Idle/Walk/Turn。正背3/4加左右镜像，不宣称完整八方向独绘；肩披与腰以下裙摆使用不同锚点。 |
| 6. Grave Skeleton Rig Sheet | 复用 `art/enemies/skeleton_parts/*.png`；`art/cemetery_kit_v1/skeleton/skeleton_rig.tscn`；`editable/skeleton_rig_parts.ora`；`reviews/06_grave_skeleton_rig_sheet.png` | 20个完整透明部件，头/肋/骨盆/上下臂腿/手足/武器/旧布/绳/钉分开 | 约125单位高；实际关节层级和7段动画轨道。保留墓葬绳、铁钉、旧布与错位牵引，不替换为普通骷髅兵。 |
| 7. Bone Remains Sheet | 同一Skeleton独立骨件；Skeleton场景的collapse/remains/reassembly；P01 `skeleton_pose_manifest.json`保留参考；`reviews/07_bone_remains_sheet.png` | 骨头不是一张不可拆骨堆；绳线、散骨尘独立 | collapse→remains微小局部牵引→reassembly；cleared释放牵引。不持续发光。静态dressing骨堆`props/bone_cluster`不替代可重组骨件。 |
| 8. Weathered Chisel Transparent Asset | `art/loot/textures/weathered_chisel.png`；`art/loot/loot_weathered_chisel_visual.tscn`；`reviews/08_weathered_chisel_asset.png` | 真实独立RGBA；高光不是烘焙在金属上 | 延续P01约11单位宽的小尺度（斜向包围约14）；一次短促clink+约1.65秒轻反光，无Loot Beam。大尺寸目录预览不代表世界内尺度。 |
| 9. VFX Source Sheet | `art/cemetery_kit_v1/vfx/*.png`；`bone_scatter.tscn`、`dust_burst.tscn`；`editable/vfx_sources.ora`；`reviews/09_vfx_source_sheet.png` | Echo碎片、反光细片、尘、碎骨、绳牵引、Sigil片6独立透明源；雾另层 | 运行参考：Echo3–5单位、碎骨3–5、金属细片2–4、尘20–30；按纹理形状保持等比。独立Node2D/VFX或粒子纹理，不参与奖励。程序负责Cue表，不重复Loot高光。 |
| 10. Word Sigil UI Assets | `art/cemetery_kit_v1/ui/observe.tscn`、`shatter.tscn`、`erode.tscn`；27个单状态PNG；原生源 `art/ui/word_sigil.gd`；`reviews/10_word_sigil_ui_assets.png` | 原生Control透明，语义几何和词作为同一视觉结构；PNG真实透明、straight alpha | 原生建议220×124，最小208×118；PNG440×248供2倍采样回退。9状态齐备。PNG不烘FocusCost，动态成本由原生节点/能量室显示，不能用固定贴图冒充实际成本。 |

表内 `editable/`、`reviews/` 均相对 `art_source/production/cemetery_kit_v1/`。每个可见运行PNG的实际像素/世界尺寸/scene见 `art/cemetery_kit_v1/module_manifest.json`；Player建议尺寸见 `player_parts_manifest.json`。

## 地形拼接与排序约束

六材质：wet stone path / broken stone path / muddy ground / mossy stone / cracked graveyard floor / puddle-damp edge。原始绘制来自image_gen材质图集，裁出材质后仅做确定性边界修正；基础六材质左右/上下端点均值差0。此数值确认无跳变，不代表没有周期重复：同材质大面积仍有可识别重复，需要实际布置中使用连贯材质块与边缘覆盖。

source0 atlas坐标(x=材质0..5,y=相位0..3)；不同相位不能不加混合就硬拼。实际地图优先固定phase0。source1 atlas坐标(x=NESW边缘mask,y=材质行)，以mud底层覆盖，N=1/E=2/S=4/W=8；相邻不是同材质即设bit。材质行顺序见terrain_mapping。两个TileMapLayer的tile_size均256、scale均0.5；不要把tile_size改128却保留256 region造成格间覆盖。

Props脚底原点用于Y-sort。结构Sprite始终等比，不能把横向铁栏整张旋转90度或拉长变形。纵深栏杆带SocketA/B，可按真实斜向连续拼装；这些socket是素材脚底近似接合点，程序按实际放置生成/检查碰撞。门基座与门扇分开；当前不能把静态Gate贴图当成已经完成的开合动画。

## 运行接口与职责

`PlayerVisual.present_motion(velocity: Vector2, facing: Vector2)`；Skeleton保留`present(snapshot)`并支持相同运动接口。动画读快照/真实事件，不写HP、Structure、Integrity、Echo、Focus、Loot或Run State。Skeleton攻击只听`enemy_attack_started`，不再仅因进入ENEMY_TURN就误播。

Word控制器`set_presentation({word_id,instance_id,focus_cost,state,enabled,reason})`，9状态IDLE/HOVERED/SELECTED/INVOKING/USED/RETAINED/ECHO_COPY/EXHAUSTED/DISABLED。`invocation_requested(instance_id)`只是请求，程序判定是否消耗Focus。未制作的其他词仍保留可操作的原有呈现，不隐去现有能力。

`bone_scatter`/`dust_burst`和P01特效使用`play_event(id,payload)`，自动释放，只读世界position。Word效果优先payload.position，其次world_player group/祖先Player，兼容世界分层。Echo仍先提交数值，再播放飞行，表现中断不能丢奖励。

## 源文件、导出与授权

- 原始可恢复源：`art_source/production/cemetery_kit_v1/raw/*.png`+手写`*.prompt.txt`，14次内置image_gen；原始生成目录也保留原件。`source_provenance.json`记录原件路径。
- 分层编辑包：7个OpenRaster `.ora`，共92层；每层是独立完整资产，**不是**虚构的原始笔触/PSD历史。完整分辨率单件PNG、裁切坐标和源图集同时保留。Krita/GIMP等支持ORA的软件可继续编辑。
- 游戏导出：`art/cemetery_kit_v1/`；Skeleton与Chisel沿用已验收P01透明源；source目录已有`.gdignore`阻止误导入，但源文件进入Git备份。
- 地形与所有道具/角色/VFX均可分开重用；contact shadow、雾、灯光为Godot独立层。精确UI/VFX几何是原生可编辑结构，不是用程序几何替代角色/场景绘画。
- 无外部商业素材包、无拷贝其他游戏精灵；图像均由项目参考与内置生成工具生产。使用适用服务条款，不宣称排他版权。字体沿用Cormorant Garamond，SIL OFL原文保留在`art/ui/fonts/OFL.txt`。
- 最大新增源不足7MB，已评估当前规模；未更改仓库LFS策略、`.gitignore`或上传大型PSD/AVI。`.godot/`缓存不提交，必要`.import`/`.uid`保留。

## 版本与回滚

美术worktree `/Users/mac/Documents/GitHub/English-Game-art`，分支 `feature/mini-run-0.9-art`。Kit开始前稳定点`1d5952e`，备份分支`backup/art-before-cemetery-kit-v1-1d5952e`。程序工作在独立`English-Game` / `feature/mini-run-0.9-code`，双方通过增量提交整合，不同时写同一目录。

分块提交：`e58ee55`地形；`8928556`主角拆件；`77ef5bf`结构/Props/前景；`1c5d8d4`VFX/UI/分层源；`98654d9`旧预览兼容。程序最终接入提交与联合验证记录见本文件同目录 `CEMETERY_KIT_V1_VALIDATION.md`。

如不采用这一轮，先保留当前分支，在新分支/独立worktree从`1d5952e`查看P01；不要在共享分支强制reset。单独撤销资产会使已整合程序的资源路径失效，整套回退必须和程序接入一并评估。

改动旧文件前外部可恢复备份：`/Users/mac/Documents/GitHub/English-Game-art-backups/pre-cemetery-kit-v1-1d5952e/`。这轮未推送GitHub，未合并main；本地提交不等于用户验收。
