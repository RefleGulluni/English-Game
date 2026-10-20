# Broken Graveyard Modular 2.5D Rebuild · 第一轮交付

工程：`English-Game`；程序分支：`feature/mini-run-0.9-code`。不合并 main，不自动上传 GitHub。
仅重构 Broken Graveyard 的场景生产、角色动画和美术接入，不扩展敌人、Biome、Boss 或玩法系统。

## 验收入口

打开本工程 `project.godot`，F5运行。WASD/方向键移动，E进入/拾取，L词典，Tab背包。
进入后接近Skeleton、确认手牌，使用原有Word Action/Retain/DEFLECT。
本轮debug仍保留强制Weathered Chisel验收模式；F2可选择普通10%模式。

主验收为 `captures/broken-graveyard-modular.mp4` 的连续实机录制：Idle → Walk → 前景遮挡 → 接近Skeleton → 软锁定 → 攻击/受击 → Collapse → Bone Remains → Echo → 凿子实体 → 清理骨堆 → 恢复移动 → PICK UP → 背包入库。
由Godot Movie Maker实际渲染，自动操作脚本执行真实移动和合法手牌，不改HP/Focus、不注入假牌，不剪接静态图，不倍速。
录制关闭永久知识写入，并显式强制这次凿子掉落；不代表普通模式必掉。
另附 `captures/broken-graveyard-reassembly.mp4`（16秒），验证自然经历3完整回合后的重组，不增加第二次掉落或Echo。

## 正式完成的程序与接入

- GroundTileMap：135个真实可编辑底层cell；GroundBlendLayer用独立透明边缘过渡，实际使用6种材质。128世界单位一格，256纹理按0.5缩放，不使用整幅背景作为地图主体。
- StructureLayer / PropLayer：独立PackedScene，8种墓碑、墙体、沿真实socket拼接的铁栏、树、骨/石/旧布/枯草；脚底pivot和跨分组Y-sort。
- CharacterLayer / LootLayer / ForegroundLayer / VFXLayer / FogLayer / LightingLayer独立。前景栏杆、枝叶真实覆盖演员，覆盖时部分淡化以保持可读性。
- CanvasModulate与PointLight2D是真实场景节点，可在编辑器调整；接触阴影、场景色与局部光实际作用于角色。雾由独立shader运行，不烘焙进地面。
- Player：真实Skeleton2D/Bone2D，上下肢关节层级；AnimationPlayer包含idle / walk / turn。Walk有腿、前臂、外套和肩披轨道；正/背上身切换加左右镜像。进入战斗时朝向敌人。
- Grave Skeleton：20独立骨件的Skeleton2D/Bone2D cutout；AnimationPlayer包含idle / walk / attack / hit / collapse / remains / reassembly。骨盆/胸腔/肩臂错相，重组先骨盆后头部，绳索跟随骨件。动画不修改战斗状态。
- Skeleton攻击事件只在招式真正结算时产生；BIND跳过行动不误播，等待DEFLECT时不提前认定攻击已发生。结构伤害也触发受击表现。
- OBSERVE / SHATTER / ERODE接入已通过的独立Word Sigil控件，保留其他词的可用文字控件，不伪造缺少的全量语义美术。
- 原有HP/Structure、软锁定、回合、3完整回合重组、15+5 Echo、一尸一次Special Roll、实体Loot、E拾取、Run State与防重领保持不变。移除表现不影响奖励。

结构与资产所有权详见 `MODULAR_2_5D_CONTRACT.md`。主地图源：`scenes/world/cemetery_modular_environment.tscn`；光源：`scenes/world/cemetery_lighting.tscn`；两套Rig：`art/cemetery_kit_v1/player/player_rig.tscn`、`skeleton/skeleton_rig.tscn`。
可在Godot里直接查看关节和AnimationPlayer关键帧，不是空节点或运行时整图平移。

## 哪些仍是第一轮 / 占位

角色拆件、地形和Props已是实际接入资产，但整体调色、接缝/重复掩饰、关节接缝及步态仍需试玩后的美术精修，不宣称最终成品质量。
当前声音沿用P01候选；混音、环境声和脚步声不是最终版本。门洞有实际交互/碰撞，但门扇开合动画未完成。
粒子/Word世界特效为首轮表现，不是全量Lexicon动态视觉。未实现湿地角色倒影（可选项），没有法线贴图或完整光照遮挡系统。
主角使用前/背两套加镜像，不是完整8方向独立绘制；Skeleton有Walk片段，但本关未新增敌人巡逻或寻路。

## 数值与已知限制

128格宽、118左右主角尺度、125左右Skeleton尺度是本次美术接入基准；移动180、交互82、接战165仍是测试值。HP24/Structure12/Integrity10及15+5 Echo沿用M01，未进行新一轮平衡。
Weathered Chisel仍只掉落、拾取、入Run Bag，没有擅自增加战斗效果。
地面局部纹理重复仍可识别；前景淡化按包围区域，不是逐像素遮挡判定。动作已能运行，但不等于经过最终手工动画精修。
没有新增断档续跑存盘；永久知识沿用0.8机制，当前Run库存仍随重开清空。
原有未提交Godot AI/MCP配置保持不动。CLI退出时插件偶有ObjectDB/resource清理警告，旧基线亦存在；不能将其当成已修复的游戏Bug或隐去不报。

## 调试与边界

最终28套smoke测试全部通过；握柄修正后模块检查扩展为48项，美术接口39项、独立资源127项均通过。检查真实地形、排序、socket碰撞、遮挡、真实骨骼轨道、腿部运动、背面/镜像和锁定，以及合法牌组实际通关。武器握柄真正附在持械手骨上，并验证四个攻击时间点不会脱手；攻击位移与接触阴影一起镜像，不控制玩法位置。
另以实际三次完整回合验证自然重组：HP恢复12、Structure恢复6、Echo仍15、Special Roll仍一次。
1280×720是本轮实机检查基准；更小窗口和其他宽高比未作为全面验收覆盖。
在用户验收前不扩展Ghost/Wraith/Boss、新场景、第二Biome或全序章。

## 回滚与后续

修改前备份保留于 `/Users/mac/Documents/Game-Backups/broken-graveyard-modular-20261020.9wtlmS/`；另有before-rig保存P01 wrappers/脚本。独立Git提交保留程序和美术各增量。
地图与Rig构建工具是生产工具，不在玩法运行时调用；重新生成会覆盖对应程序场景，手工改图/改关键帧后请先备份，不要直接重跑。
下一步仅根据本片段和实机试玩反馈调整关节、步态、遮挡、材质重复和提示可读性；通过后再讨论其他0.9内容。
