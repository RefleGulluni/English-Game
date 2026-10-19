# P01 — 程序组的具体接入事项

这里是交接清单，不是向其他聊天自动发出的消息。程序拥有Gameplay/HUD控制器，本轮美术没有修改这些文件。

## 1. 正式 Word Action 工厂

已准备 res://art/ui/word_sigil.tscn。支持 OBSERVE / SHATTER / ERODE，不用概念图裁切成按钮。其余词暂保留程序原有可用控件，不能为未完成的语义结构隐藏技能。

公开接口：

```gdscript
sigil.set_presentation({
    "word_id": card.name,
    "instance_id": uid,
    "focus_cost": combat.card_cost(card),
    "state": "IDLE", # 以下9态之一，由业务/UI状态决定
    "enabled": reason.is_empty(),
    "reason": reason
})
sigil.invocation_requested.connect(func(id): _press_card(id))
```

九态：IDLE、HOVERED、SELECTED、INVOKING、USED、RETAINED、ECHO_COPY、EXHAUSTED、DISABLED。Hover有自身鼠标反馈，但实际Invocation/Used/Retain/Exhaust等来自数据，控件不自行消费Focus或修改牌堆。disabled覆盖selected；USED/EXHAUSTED/DISABLED不发起点击请求。cost通过下方结构中的能量腔数量显示，没有右上角数字。

接入Mulligan仍走现有_press_card，必须维持至多两张的选择规则。Retain按钮/槽位与禁用原因沿用现有逻辑。组合状态的最终优先级需程序组从实际数据决定；不能用控件动画判断牌是否已使用。原事件中word_sigil_retained可能只有instance_id，需要工厂保留实例映射。

程序更新其占位提示PLACEHOLDER ART时，不应把本批所有动画/声音宣称最终定稿。

## 2. 已可直接使用的视觉子场景

- Skeleton：现有res://art/enemies/enm_skeleton_visual.tscn已实现present(snapshot)，保留外层Logic/Hitbox/VFXRoot/AudioRoot/LootAnchor。
- 主角：现有chr_player_visual.tscn使用Base Look和小扣件，Invocation响应已接；Anchor事件不在M01契约中，本批不臆造。
- Loot：现有loot_weathered_chisel_visual.tscn保持11像素包围宽；首次1.65秒反光在该视觉子场景内部，只影响表现。
- Environment：保留程序1900×1100边界、门/墓碑碰撞、入口/出口和Actor Root；各模块位置在environment_layout.json。禁止为了贴合漂亮截图单独移动Actor Root。
- Presentation：audio_cues与vfx_cues在现有cemetery_presentation.tscn绑定，不需要改分发器或战斗核心。

独立res://art/vfx/loot_glint.tscn也可作为替代高光模块，但当前Chisel子场景已带一次反光；不要再绑定到同一spawn事件造成重复叠加。Echo正式场景已接echo_spawned，自动关闭分发器里的旧几何兜底。

## 3. 下一次联合验收

先接三个正式Sigil控件，保留其他词与Mulligan/Retain/DEFLECT操作；再检查1280×720中的文字、Focus节点、长提示滚动、鼠标命中、键盘焦点、禁用理由、END TURN/DEFLECT边界。随后重新走Skeleton倒地/重组/清理、15+5Echo与表现中断、世界Loot生成/高亮/E拾取、防重领、VFX释放和音效听审。

本批已有实机图形通关与39项美术接口检查，但不能替代以上新HUD接入后的回归。通过前不推进其他敌人与场景。
