# Broken Graveyard P01 — Production Preparation

日期：2026-10-19（Asia/Shanghai）。仅 Broken Graveyard Vertical Slice。方向依据：已验收 Round 02，不新增 Style Exploration。

## 本轮结论

已把已通过的视觉方向转为实际透明贴图、20 件 Cutout 骨架、独立场景/Theme、27 种词与状态组合的可编辑 Sigil 控件、独立 VFX、9 个可试听音效候选，并在同一 Godot 项目内运行。不是把概念图直接铺成可玩背景。

**这是一批生产准备与首次美术运行验证，不等于整条正式联合验收已完成。**程序 HUD 仍使用其原有 Word Action 按钮，正式 Sigil 工厂接入需要程序组修改自己负责的脚本；本轮没有越界改动。音效为原创合成候选，未完成人工听审。主角底图暂为单角度静态 Base Look，不声称已有完整八向步行动画。

## 九项交付索引

| 交付 | 可审阅结果 | 真正进入 Godot 的文件/源 |
| --- | --- | --- |
| 1. Grave Skeleton Production Sheet | ../art_source/production/broken_graveyard_p01/reviews/skeleton_production_sheet.png | art/enemies/skeleton_parts/：20 张 RGBA PNG；art/enemies/enm_skeleton_visual.tscn；skeleton_cutout.gd |
| 2. Remains / Collapse / Reassembly | reviews/bone_remains_pose.png、reassembly_midpoint.png、skeleton_collapse_reassembly.gif | 同一套骨件；skeleton_pose_manifest.json；editable/skeleton_standing.ora 与 skeleton_remains.ora |
| 3. Layer Breakdown | reviews/environment_layer_breakdown.png；审阅页可开关图层 | art/environments/env_broken_graveyard_visual.tscn；modules/ 的独立模块；editable/broken_graveyard_layers.ora |
| 4. Chisel Game-Scale Asset | reviews/clasp_chisel_vfx_sheet.png；reviews/in_game/pickup_prompt.png | art/loot/textures/weathered_chisel.png；loot_weathered_chisel_visual.tscn |
| 5. Word Sigil State Sheet | reviews/word_sigil_nine_states.png：三词×九状态 | art/ui/word_sigil.tscn、word_sigil.gd、fonts/；背景透明的原生 Control，字体与几何可独立改 |
| 6. Quiet / Responding Clasp | reviews/clasp_chisel_vfx_sheet.png；clasp_responding_transparent.png | art/characters/textures/lexicon_clasp_quiet.png、lexicon_clasp.tscn；亮缝单独由几何绘制 |
| 7. Echo / Loot VFX Draft | reviews/echo_loot_vfx.gif；审阅页可播放 | art/vfx/echo_absorb.tscn、loot_glint.tscn；Loot 初次1.65秒轻反光另在 Chisel 子场景中 |
| 8. Audio Draft List | AUDIO_DRAFT_LIST.md；审阅页9个试听按钮 | audio/enemies/、audio/loot/、audio/words/，9张48kHz单声道PCM WAV |
| 9. 导入/分层/接口说明 | 本文、ART_P01_INTEGRATION_REQUEST.md | source_manifest.json、environment_layout.json、qc/ 记录、tools/ 可编辑处理与合成源码 |

上表未写完整前缀的 reviews/、editable/、tools/、JSON 均位于 art_source/production/broken_graveyard_p01/。

## 在 Godot 中如何查看

打开 **/Users/mac/Documents/GitHub/English-Game-art/project.godot**，不要在程序组原目录写入。

- F6 运行 art/previews/production_review.tscn：Skeleton 动作按钮、环境图层开关、九状态 Sigil、扣件/Chisel/VFX、音效试听五页。
- F5 运行现有默认入口：真实 M01 世界、战斗、骨堆、掉落、E 拾取及 Run Bag。
- 截图与 GIF 全部来自实际资产/实际 Godot 渲染；原始生成图在 raw/，不是这些检查结果的替代。

编辑器/MCP说明：原编辑器的 MCP 端口仍可能占用9876。本轮所有导入、运行、截图都显式指定独立 art worktree 路径；未通过指向原项目的 MCP 执行写操作。端口占用提示与项目脚本错误分开记录，不能把它当作美术项目已经接通 MCP。

## 资产、透明与导入参数

| 类型 | 源/导出 | 透明与锚点 | 导入要求 |
| --- | --- | --- | --- |
| Skeleton20部件 | raw/skeleton_parts.png、独立 crop、两份 ORA；运行 PNG 在 art/enemies/skeleton_parts/ | RGBA，关节留重叠余量；Actor Root不动，所有变换在视觉子场景；各部件局部坐标在 pose manifest | 2D lossless，修复alpha边缘，mipmap，Linear with Mipmaps；不可用Nearest当像素画 |
| Bone Remains | 同一套骨件与 fallen pose | 仍有灰褐绳钉，偶发0.65逻辑像素内局部牵引；cleared 时牵引消失、骨件变暗静止 | Cutout变换与稀薄独立VFX；不持续发光 |
| 主角/扣件 | 单角度Base PNG、quiet扣件PNG、clasp脚本 | 主角脚接触原点约(0,0)，视觉身高118逻辑像素；扣件仅约5.6像素宽 | Base暂时静态；Invocation响应约0.72秒；Anchor接口本阶段不存在，不伪称已绑定 |
| Chisel | 单件透明PNG | 主体包围宽11逻辑像素，斜向总长约14像素；无阴影/高光烘入图片；不放大解决发现问题 | 初次spawn反光1.65秒；近距离仅极轻边缘强调，不做光圈/光柱 |
| 环境 | ground.png + 墓碑A/B、枯植被、rubble、fence、wall、post/rail模块；ORA含独立对象层 | 地面不透明；模块RGBA；前/中/后景与雾分开 | 1900×1100逻辑坐标；原碰撞与Actor Root未动，14墓碑对应已有碰撞，不额外增墓碑 |
| 雾 | fog.gdshader | 单独透明Polygon/Shader层，只覆盖边缘少量 | 不烘入地面，强度可调；性能/不同显卡仍需更广验证 |
| Sigil | .gd几何 + OFL字体 + .tscn | 完全透明背景；Word、结构、Focus能量节点分开；不使用卡框/右上角数字 | 实际cost由程序数据传入；审阅页演示cost1，不能当真实数值定义 |
| Echo/响应 | 独立2D场景与cemetery_effect.gd | 细小回忆片沿弧线到payload.target，自动释放；没有奖励回写 | 使用play_event(id,payload)，正式Echo绑定后旧几何兜底自动停用 |
| WAV候选 | 9WAV + 可编辑合成脚本 | 无第三方采样；候选不代表最终Foley | 48kHz/16bit/mono、无循环；峰值和时长见audio_manifest；人工听审待做 |

前景遮挡采用接近角色时减透明度的独立表现，不改变碰撞。单个环境模块位置、大小与遮挡策略见 environment_layout.json。图层/路线若要改变，仍须程序组同步碰撞复测，不能仅换图宣布通过。

## 当前 Cutout 动作实现

Idle：头部约0.4像素轻动，躯干保持站位。Attack：前臂和武器克制前摆后回位。Hit：短暂局部受击色温反馈。Collapse：20部件在0.58秒内过渡到同源散落姿态。Remains：少量局部骨端牵引，长停顿。Reassembly：约0.8秒回到原姿态。Cleared：断开牵引、骨堆静止变暗。

当前为 Cutout 局部变换/Tween 预备绑定，不宣称已完成高精度全身 Bone2D 解剖约束；后续可在同一 present(snapshot) 接口下升级关节层级，不需要改战斗机制。动画没有回调HP、Integrity、Focus、Echo、库存或倒计时。

## 已接入与待程序组绑定

已在美术拥有的视觉场景上替换贴图/Shader/Theme、绑定Audio/VFX cue。Skeleton读取只读快照；角色响应word_sigil_invoked；掉落不依赖动画完成；Echo逻辑入账后飞行。

尚待程序组：把其 scripts/ui/slice_combat_hud.gd 的Button工厂接到新的Sigil控件，仍保留Mulligan、Retain、禁用理由、DEFLECT与键鼠命中。具体可直接实施的接口在 ART_P01_INTEGRATION_REQUEST.md。该项未完成前，实机图里的文字按钮不是正式Word Sigil效果。PLACEHOLDER ART字样是程序已有提示字符串，也未越界改动。

## 验证

- 原有 slice_world_smoke 图形运行：30项通过，包括实际物理接近、E交互、同场景接战、正常手牌通关、15+5Echo、实体掉落、手动入库、防重复领取、按钮在视口内与截图。
- 新增 art/previews/art_contract_smoke.gd：39项通过，检查20独立部件、散落/重组/清理状态、表现不改奖励、27种词/状态组合、禁用优先、扣件事件与归静、VFX自动释放。
- 原有 slice_combat_smoke、slice_loot_smoke（普通触发1008/10000）、slice_lifecycle_smoke（9项）：通过。
- 透明部件逐项strict QC；首次等分裁切失败的记录保留，最终采用完整物件空隙裁切，无切断的部件。
- 已检查实际1280×720截图、全九状态表、源PNG alpha、文件引用与OpenRaster层内容。

未验证：音效人工听审、非桌面分辨率/更多显卡、最终关节约束、八向角色动画、真实玩家对Loot发现距离的反馈、程序正式Sigil绑定后的键鼠/长提示复测。现有实际测试布局仍显得规则，未将其误认为最终场景构图要求；后续坐标调整需要程序组联合验收。

## Git、备份与范围

本轮前概念提交4175f70。引入程序M01 c202492形成接入基线 **7b08127**；仅在 feature/mini-run-0.9-art 上工作。原目录程序分支及未提交Godot AI配置没有操作。未改main、未强推、未推送GitHub。

备份：/Users/mac/Documents/GitHub/English-Game-art-backups/pre-production-c202492/。含原占位场景/Theme、关键修正前源与前次截图；制作前另有backup/art-before-production-prep-4175f70分支。原始生成图、已验收概念及本轮分层源均保留。

撤销本批美术可按本批独立提交执行git revert，目标是接入基线7b08127；若需要完全回到概念阶段，则选择4175f70另建分支。不要reset共享分支。

未制作Ghost、Wraith、Mourning Keeper、Redactor、Eleanor或其他场景。正式联合验收完成前仍不扩展。
