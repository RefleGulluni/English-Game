# Broken Graveyard Modular 2.5D 接入契约

范围仅 Broken Graveyard。画风保持 Painterly Semi-Realistic Dark Fantasy。
Gameplay owns state. Art owns presentation. 不合并 main，不自动 push。

## 所有权与运行结构

程序工作区 `English-Game`、美术工作区 `English-Game-art` 是同一仓库的隔离分支。
程序拥有主世界/碰撞/交互/状态机；美术拥有 `art/`、`audio/`、`art_source/`、独立视觉场景和动画资源。
用明确提交整合到同一个运行工程；不要互相覆盖未提交文件。

```text
BrokenGraveyard (Y-sort)
├── Environment (Y-sort)
│   ├── GroundTileMap (TileMapLayer, z=-20)
│   ├── GroundBlendLayer (TileMapLayer, z=-19, 独立材质边缘)
│   ├── StructureLayer (Y-sort)
│   ├── PropLayer (Y-sort)
│   ├── ForegroundLayer (z=5)
│   ├── FogLayer (z=20, 独立移动雾)
│   └── LightingLayer (CanvasModulate + PointLight2D)
├── CharacterLayer (Y-sort)
│   ├── Player / VisualRoot / PlayerVisual
│   └── GraveSkeleton / Logic + VisualRoot + Hitbox + VFXRoot + AudioRoot + LootAnchor
├── LootLayer / WorldLoot (Y-sort)
├── VFXLayer / PresentationRouter
├── CollisionRoot + Gate
├── Entrance / Exit / Camera2D / Systems
└── CombatHUD
```

各 Y-sort 分组保持同一坐标原点和 z=0，使角色和物件跨组按脚底实际世界 y 排序。
禁止给整个角色层指定一个永远高于 Props 的 z。Foreground 专用于刻意前景遮挡；遮住角色时只淡化覆盖物到部分透明，不隐藏玩家，也不淡化地面。

## 地形和 Props

地形目标格宽128世界单位，纹理清晰度不等于碰撞格宽。
TileMapLayer按 `128 / TileSet.tile_size.x` 等比缩放；地形不得包含墓碑、树、角色、拾取物或永久烘焙雾光。
地图保存真实可编辑 cell 数据，而不是一张预览图片或仅运行时临时画图。

`scripts/build/build_cemetery_map.gd` 是一次性地图构建工具，不从玩法调用。它会覆盖程序所属的环境场景；重新执行前必须备份编辑器中已手动修改的地图。
Props通过独立 PackedScene 接入。新Kit场景以脚底(0,0)为原点，直接使用世界尺寸；旧P01单Sprite通过 `cemetery_prop.gd` 等比适配，不拉扁墙栏。碰撞由程序层提供，不能直接从图片透明度推算。

## 角色 Rig 与动画桥

- PlayerVisual：`present_motion(velocity: Vector2, facing: Vector2)`；移动来自 CharacterBody2D 的实际速度。锁定时速度为0，但保留上次朝向。
- SkeletonVisual：保留 `present(snapshot: Dictionary)`；`standing/remains/cleared`、HP、Structure、Integrity、重组倒计时只读。预留 `present_motion`，不擅自新增敌人寻路或战斗位移规则。
- 脚底原点(0,0)，向上绘制。Player约118，Skeleton约125世界像素。接触阴影在脚底，随演员排序、受环境色和局部光影响。
- 使用真实 AnimationPlayer 属性轨道；Skeleton2D/Bone2D或有层级关节的等价cutout rig都可。空 Skeleton2D / 空 AnimationPlayer 不算完成。
- 第一阶段片段命名：Player `idle/walk/turn`；Skeleton `idle/walk/attack/hit/collapse/remains/reassembly`。
- 动画结束不能修改HP、Structure、Focus、重组倒计时、Echo、Loot或Run State。丢失动画/VFX也不得丢奖励或锁住回合。

## 事件更新

`enemy_attack_started` 来自真正结算敌人招式的只读信号，字段 `enemy_id/position/action/kind`。不要再用 ENEMY_TURN 阶段变化判断“攻击已经发生”：BIND可跳过行动，DEFLECT可能尚在等待输入。
`enemy_damaged` 的 component 可为 `hp/structure/integrity`，只播表现，不重复结算伤害。死亡/重组状态优先于Hit或Walk，不能被后来的短促受击姿态覆盖。
`word_sigil_invoked` 携带玩家世界position；特效不能依靠固定 `get_parent()` 深度定位演员。玩家可通过 `world_player` group找到，但不得回写其逻辑。

沿用15+5 Echo、一尸一次Special Roll、独立世界Loot、E手动拾取与Run入库。第一轮仍用明确标注的强制Chisel验收模式；普通概率保持10%。

## 验收

主交付为Godot实际渲染的连续10–20秒片段，不用静态截图合成流程。录制驱动只执行真实移动/交互和合法手牌操作，不能改HP、Focus或注入假牌。
同时检查 TileMap 可编辑、6种地形、物件可复用、实际遮挡/淡化、Idle/Walk/朝向、Skeleton各动画轨道、回合锁定、3完整回合重组、Echo防重领、手动拾取、HUD可点击与表现移除不影响逻辑。
