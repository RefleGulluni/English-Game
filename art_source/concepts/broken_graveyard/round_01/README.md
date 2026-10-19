# Broken Graveyard — Style Exploration Round 01

日期：2026-10-19（Asia/Shanghai）  
状态：等待用户确认；禁止据此扩产。  
基线：`ebee97f471b0d9dd39df56f90a7ee17125f734f8`  
分支：`feature/mini-run-0.9-art`

## 本轮范围

仅 Broken Graveyard 的风格与概念探索。优先遵循用户这次缩小的范围，不执行 Visual Bible 第 41、42 节的完整清单。未制作 Ghost、Wraith、Keeper、Redactor、序章或其他墓园场景。

## 候选与比较

| 候选 | 文件 | 观察 | 判断 |
| --- | --- | --- | --- |
| A 湿石与骨白 | candidate_a.png | 湿石与骨材质细节较丰富；地面信息密、局部偏写实渲染；Sigil 图形压过英文 | 保留对照，不能直接锁为生产风格 |
| B 初稿 | candidate_b_v1.png | 更深的泥土、锈铁，但与 A 差异偏小，笔触仍不充分 | 留作历史，不作为本轮主选项 |
| B 修正版 | candidate_b_v2.png | 更明确的笔触、地面细节有所归并，词居于几何中央 | 推荐继续方向，等待确认 |

同一套镜头、主角服装、Skeleton、Chisel 与墓园布局构成对照。对照并非严格单变量实验：B 修正版同时修正了英文与几何的主次。三张图均为 1536×1024；上部游戏镜头、下部放大造型参照。上部并非实际 Godot 截图。

## 已展示与未成立的内容

已展示：主角 Base Look（包含正侧与背侧参照）、Grave Skeleton、Bone Remains、Broken Graveyard、Weathered Chisel、少量 Echo 片段、基础 HUD、OBSERVE / SHATTER / ERODE 的视觉草案。

未验证：动画连续性、骨架牵引与永久断开的区别、Echo 流向与吸收反馈、Chisel 的轻微高光节奏、实际镜头中的发现距离、靠近时 PICK UP、完整 HUD 的 Intent 内容与状态、字体验证、Focus 节点与真实消耗绑定、Godot 缩放与遮挡、任何音效。静态图混合呈现崩解与掉落意向，不代表多个事件实际同时发生或修改了机制。

两图仍需改进：中心地面可继续减噪；Echo 线条应再轻一些；主角局部材质仍偏精细；Sigil 在本轮只是形态草案，生产时需以可编辑几何与真实字体重建。不能从这些静态概念推断完整 Loot 体验已经成立。

## 确认后才启动的生产安排

先锁定镜头、比例、光向、色板、角色身份及材质笔触。再建立 Master Character Sheet，以已确认图为主动参考制作 Cutout 部件与必要遮挡补全；角色/骨件/武器、地面/前景/背景、接触阴影、雾、Echo、Loot 高光、Sigil、HUD 分开。

视觉系统预期采用 Cutout/Bone Animation + Shader/VFX + 少量关键逐帧效果，具体依程序组约定接口落实。不改战斗、掉落概率、学习、地图或存档机制。共用场景、配置和接口的变更先协调。

待验证体验：

1. 进入墓园：世界优先，探索 HUD 克制。
2. 遭遇 Skeleton：显示必要战斗信息，语言几何与世界笔触形成对照。
3. 打散：骨件与武器依次落地，Bone Remains 可保留未断牵引。
4. Echo：薄片沿细小弧线流向玩家，自动吸收；独立于 Special Loot。
5. Special Loot：是否掉落由程序决定；Chisel 留在骨堆旁，仅短暂金属高光和轻 clink。
6. 玩家靠近后手动拾取：对象附近出现 PICK UP；响应程序事件，不能用视觉脚本自行发放奖励。

声音在方向确认后制作/选取：Skeleton collapse（干骨落地与布料）、Echo absorb（空气收束与柔和共鸣）、Special Loot clink（骨/金属物理撞击加极轻共鸣）、Pickup（克制触感确认）、Word Sigil invocation（结构对焦/断裂/侵蚀）。本轮没有音频文件或试听，不使用金币声或持续满铺音乐。

## 文件、来源与可编辑性

- 此目录：概念原始栅格、完整生成提示词、参考文档快照、来源记录与评审。
- candidate_a.prompt.txt：A 实际使用提示词。
- candidate_b.prompt.txt：B 初始规范；candidate_b.reference.prompt.txt 才是 B 初稿实际调用文本，以 A 为参考。
- candidate_b_v2.prompt.txt：B 修正实际调用文本，以 B 初稿为参考。
- reference_visual_bible.md：用户文档的只读内容快照，原文档未修改。
- art_source/.gdignore：使概念与制作源目录不被 Godot 导入；不影响 Git 追踪。
- 当前仅有 PNG 栅格原始图和可编辑文本，不存在 PSD/KRA 分层文件；不声称已交付分层生产源。生成工具没有返回分层工程文件。
- 后续生产的可编辑源保存在 art_source/，运行导出资源计划保存在 assets/art/（尚未创建）；可编辑源、导出 PNG、绑定与动画资源必须成套留存。

来源：OpenAI 内置 image_gen；无第三方图片、字体或音效素材输入。生成日期为 2026-10-19；工具未提供模型精确版本或 seed，不能承诺逐像素复现。参考链见 manifest.json。AI 来源不等于已完成商用权利核验；适用账户条款与最终素材授权应在外发/上传前核对，不声称独占或版权保证。本轮不推送 GitHub。

固定提示词约束：3/4 top-down 2.5D、6.5–7 头身、低饱和、左上漫射光/右下接触阴影；世界 painterly/broken、语言 precise/structured；灰蓝/炭灰/褪棕/骨白/铁黑/苔绿/旧铜。禁止 Pixel、Anime、Q 版、传统卡牌、词汇学习卡、Loot 光柱、RGB/VHS glitch。所有正向和禁止项均已保存于对应完整提示词。

## 验证与回退

已人工查看三图，检查镜头、造型、色彩、禁用项和形态差异；已核对文件尺寸与 SHA-256。尚未做 Godot 接入或运行验证，也未改动运行资源。无需为本轮只新增概念文件的改动运行程序机制测试。

所有文件均新建，没有覆盖既有文件；B 初稿保留。概念提交之外的程序组工作不受影响。若不采用，保持本提交存档，并从基线 ebee97f 建另一候选分支，或对本次单独提交执行非破坏性的 git revert；不 reset 共享分支，不永久删除源图。
