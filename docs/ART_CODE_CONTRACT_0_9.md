# 0.9 M01 · 程序 / 美术接入契约

**Gameplay owns state. Art owns presentation. One Godot project is the integration center.**

本仓库的程序分支与美术分支可以使用独立 worktree，隔离文件写入；它们仍是同一 Git 项目，不是重新制作两套不同工程。不要两组同时覆盖同一份工作目录。程序不会擅自导入美术分支尚待验收的概念图。

## 文件所有权

| 程序负责 | 美术负责替换/交付 |
|---|---|
| `scenes/world/world_broken_graveyard.tscn`：演员、碰撞、入口、相机、系统引用 | `art/environments/env_broken_graveyard_visual.tscn` |
| `scenes/enemies/GraveSkeleton.tscn` 的 Logic/Hitbox/锚点 | `art/enemies/enm_skeleton_visual.tscn` |
| `scenes/player/Player.tscn` 的移动/碰撞 | `art/characters/chr_player_visual.tscn` |
| `scenes/loot/WorldLoot.tscn` 的状态机/交互/数据绑定 | `art/loot/loot_weathered_chisel_visual.tscn`、`loot_highlight_visual.tscn` |
| `scripts/ui/slice_combat_hud.gd` 与 UI 控件逻辑 | `art/ui/combat_hud_theme.tres`，后续正式 Word Action 视觉 |
| `scripts/presentation/presentation_router.gd` 的分发器 | `art/vfx/cemetery_presentation.tscn` 的 `audio_cues` / `vfx_cues` 资源绑定；`audio/*` 与 `art/vfx/*` 成品 |

首轮占位为纯几何 debug presentation，没有生成正式美术。美术替换这些独立场景/Theme，不需要修改 CombatState。新源文件放 `art_source/` 时请使用清晰版本命名，避免把未确认概念图当成运行时成品；本程序提交不触碰已有 art worktree 内容。

## 必须保留的结构

```text
GraveSkeleton
├── Logic                 程序：HP/Structure/重组数据绑定
├── VisualRoot
│   └── GraveSkeletonVisual  美术可替换
├── Hitbox                程序
├── VFXRoot               美术扩展挂点
├── AudioRoot             美术扩展挂点
└── LootAnchor            程序：掉落位置

WorldLoot
├── VisualRoot
├── InteractionArea
├── HighlightRoot
├── AudioRoot
└── DataBinding
```

允许在 VisualRoot 下换 Sprite2D、AnimatedSprite2D、AnimationPlayer、shader 或子 PackedScene；不要删除 Logic/碰撞/Anchor，或用动画回调修改 HP、Echo、库存、重组倒计时。

Skeleton 视觉子场景可实现 `present(snapshot: Dictionary)`，接收独立副本：`mode = standing/remains/cleared`、HP、Structure、Integrity、`reassemble_in`。读取快照改变视觉即可，不回写业务状态；若只用全局事件，也可不实现该方法。

## 场景坐标与碰撞

测试世界1900×1100，入口约(420,500)，门(480,500)，玩家(220,500)，Skeleton(1060,500)，出口(1700,500)。世界墙体和墓碑碰撞已序列化在 CollisionRoot 中，可在编辑器检查；几何占位支持编辑器预览。逻辑使用俯视2D坐标，Root 是逻辑接触锚点，素材自身的偏移/缩放放在 VisualRoot 子场景，不动 Actor Root 来“修图”。

Collision layer 1为世界、2为玩家。交互半径82、接战半径165，暂定布局不是正式美术尺寸锁定。正式环境图若改变路线/墓碑位置，需要程序组同步碰撞和锚点后复测，不只换图就宣布集成完成。

## 事件接口

运行时可通过 `get_tree().get_first_node_in_group("gameplay_events")` 获取本场景的全局事件总线，监听 `occurred(event_id: StringName, payload: Dictionary)`。Payload 是只读副本，包含递增 `sequence`，无贴图/声音/动画路径。总线是表现输出；不得让美术主动发一个 collapse 事件来决定奖励。

已接入事件：`scene_entered`、`combat_started`、`combat_phase_changed`、`combat_ended`、`enemy_spawned`、`enemy_damaged`、`enemy_structure_changed`、`enemy_exposed`、`enemy_collapsed`、`enemy_reassembled`、`enemy_defeated`、`echo_spawned`、`echo_absorbed`、`special_loot_spawned`、`loot_highlighted`、`loot_picked_up`、`word_sigil_selected`、`word_sigil_invoked`、`word_sigil_retained`、`word_sigil_exhausted`、`observe_started`、`observe_resolved`、`corruption_changed`、`knowledge_stage_changed`。

这里只列本阶段实际使用的接口，不虚构 Keeper/Anchor/Redactor 的完整事件实现。状态机不等待动画播放完成才能发钱，也不依赖音效是否加载成功。

- Enemy：主要字段 `enemy_id`，可带 `position`、`amount`、`value`。
- Echo：`reward_id`、`amount`、`position`、`target`；先提交逻辑数值，再进行视觉飞行。中断表现不能丢奖励。
- Loot：`loot_id`、`instance_id`、`position`；拾取后带 `name`。普通未触发掉落不产生“空奖品”提示。
- Word：`word_id`、`instance_id`。显示状态/可用性以 HUD/CombatState 数据为准，不能靠动画自行消费 Focus。
- Corruption：`family`、`value`、`tier`（Inattention为其真实层级；其他族当前层级0）。

## Audio / VFX 不改核心代码的接入方式

在独立的 `art/vfx/cemetery_presentation.tscn` 上，把事件名作为 key，填入：

```text
audio_cues["enemy_collapsed"] = AudioStream
audio_cues["loot_picked_up"] = AudioStream
vfx_cues["echo_spawned"] = PackedScene
vfx_cues["observe_started"] = PackedScene
```

VFX 推荐2D子场景，可实现 `play_event(event_id, payload)`；由自身控制播放完成后释放。绑定正式 Echo VFX 后自动停用几何 Echo 兜底，避免两套效果叠加。Audio 经配置的 `audio_bus`（默认 SFX，若无该Bus则Master）播放；本阶段没有实现完整混音/自适应音乐，不能把空挂点当成已有音乐成品。

UI Theme 使用独立资源文件；程序只负责状态、文本和点击。正式贴图/动画导入后需复查半透明面板、文本对比度、鼠标命中、长提示滚动、END TURN/DEFLECT 是否仍在视口内。

## 首批交付后联合验收

在同一项目中导入并核对 Import Settings → 接入独立视觉场景/Cue资源 → 检查逻辑锚点与碰撞 → Skeleton倒地/重组/清理三种状态 → 15+5 Echo与视觉中断 → Loot生成/高亮/E拾取 → 状态入库与防重领 → 声音事件与无残留VFX → 回用户验收。此流程通过前不扩展其他场景。
