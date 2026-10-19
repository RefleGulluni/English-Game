# English Game 0.9 · 第一阶段交付 / Broken Graveyard

本次只交付正式执行文档的 Milestone 01，不代表全量 0.9 已完成。来源为用户提供的只读 `English_Game_0.9_Gameplay_Implementation_Spec.md`，不修改该设计文档。固定目标：**Broken Graveyard 可实际游玩**。

## 已实现的正式逻辑

- 同一个 Godot 项目内的探索小场景，8 方向移动、围墙/墓碑碰撞、靠近入口的 ENTER、清理后的 LEAVE。
- 统一交互接口 `can_interact(player)` / `get_prompt()` / `interact(player)`。E 是唯一世界交互键，Prompt 仅在可交互范围内出现。
- 接近 Skeleton 后原场景软锁输入，镜头推进、Combat HUD 展开，不切换战斗页面；战斗结束镜头/HUD/移动/交互恢复。
- `CombatState` 仍负责原有 Word Action、Focus、手牌、Mulligan、Retain、Intent、Structure、Armor、EXPOSED、状态、反应及伤害计算。没有重写第二套战斗规则。
- TurnController 负责 EXPLORATION / COMBAT_ENTER / PLAYER_TURN / ENEMY_TURN / ROUND_RESOLVE / COMBAT_END / DEFEAT。反应窗口等待真实选择，Lexicon 开关不消耗该窗口。
- Skeleton HP0 进入 Integrity 10 的 Bone Remains；**3 个完整回合**后恢复半 HP/Structure。SHATTER -8、STRIKE -3，BIND 每个骨堆阶段最多延迟一次。
- 第一次倒地立即提交 15 Echo，并发出世界生成/吸收事件；清理骨堆另给 5 Echo。骨堆重组再倒地不会反复刷钱或重新 Roll。
- Special Loot 独立 seeded RNG。先触发概率、再过滤合法 Ecology 池，再进行池内加权；Affinity 接口不改变总触发概率。本轮只放入 Chisel，没有实现全量 Build/Relic。
- 掉落实例经过 SPAWNING / IDLE / HIGHLIGHTED / PICKING_UP / COLLECTED；只在解除软锁后、玩家足够近时按 E 才入库。站远、战斗软锁、重复键或重复实例 ID 都不能重复领奖。
- Run State 保存本局 Echo、库存、Relic 身份和奖励/拾取防重账本。Chisel 没有未经定义的数值效果。
- 永久知识继续沿用 0.8 Learning Schedule 的本地保存、单 Primary Target、Stage/Spacing/权限；本轮不新增学习题、不做完整动态图鉴。Lexicon 只显示已遇见词及已获得的含义，不暴露未知敌人资料或未知答案。
- 美术/音频/VFX 独立场景与事件接口；关掉表现层不会抹掉已经结算的 Echo 或库存。奖励由真实 CombatState 转换驱动，不由美术事件驱动。

## 用户已确认的两个衔接决定

1. 首次倒地即可生成掉落，但骨堆尚未清理时仍在回合制战斗。清理后解除软锁，玩家再自由接近手动拾取。不强制拾取才能退出战斗。
2. Weathered Chisel 先实现真实掉落、拾取、Run State 入库；设计未给出的战斗效果不自行创造。

## 固定规则、临时值、占位内容

设计已定：Integrity 10、3 completed rounds、SHATTER 8 / STRIKE 3、BIND 一次延迟、首次 15 Echo / 清理再 5 Echo。

继承/暂定的测试值：Skeleton HP24 / Structure12 / Armor0，沿用旧版 Intent Pattern；移动速度180逻辑单位/秒，触发半径165，拾取半径82，镜头过渡0.65秒，Echo占位飞行约0.5秒。世界大小1900×1100、碰撞位置和演员尺寸均为测试布局，正式环境资产接入时需联合校准。

普通 Special Loot 起测概率 **10%** 已实现并单独测试。首次交付为了验收，`qa_force_chisel=true` 在 debug 运行时强制合法 Chisel；F2 可重开普通10%模式。Release 不走强制掉落。等待用户验收后再将默认验收开关关闭，不在开发中悄悄变成永久保底。

占位：玩家几何形体、Skeleton/骨堆/清理状态、墓园环境、Chisel、小型 Echo 点、拾取光圈、按钮式 Word Action、HUD Theme。**没有正式贴图、正式动画、音效、音乐或粒子资源**。空 Audio/VFX 接入口不等同已完成音画成品。

## 本次明确未做

其他六个 Cemetery 微场景、第二 Biome、Mourning Keeper、新职业体系、完整 Build 系统、全量 Relic、Crafting、完整 AI NPC、全序章、全量 Lexicon 动态视觉。仓库中的历史 0.7/0.8 数据和测试保留，不表示本分支开发了这些 0.9 内容。

Run State 是本局内存状态：退出/重开会开始新局，不提供中途断点续玩。永久 Lexicon 与之分开保存。跨场景 unresolved 只暴露 SkeletonLogic 的 `unresolved_snapshot()`，不模拟尚未开发的离场/返场重组系统。

## 验收走法

1. F5 运行默认入口。WASD/方向键向东靠近门，看到 ENTER 后按 E。
2. 继续接近 Skeleton，确认初始手牌（可点至多两张换牌）。观察 Intent，使用 Word Action、Retain、结束回合及 DEFLECT。
3. HP0 后观察 15 Echo 自动吸收及骨堆旁的 Chisel。此时 E 拾取仍被软锁拦住。
4. 可直接清理骨堆，也可故意结束三个回合验证重组；清理骨堆后总 Echo 为20，并恢复自由移动。
5. 走近 Chisel，看到 PICK UP 按 E。Tab 查看 Run Bag，应为 Weathered Chisel ×1；再按 E 不应重复获得。
6. 可不拾取就继续探索；向东到 LEAVE 接口会给出切片完成提示，不跳转到未开发场景。
7. F2 重开普通10%模式，允许某次完全不出特殊物品；不应显示空掉落结算或阻止退出战斗。失败时可从提示重开，清理后可按 R 重玩。

## 自动化与画面检查

四个新增 suite 加二十三个历史 suite。历史 UI suite 显式加载 legacy 场景；新入口单独测试，不把新世界伪装为旧页面。

- `slice_combat_smoke.gd`：真实核心的HP0/骨堆/三次完成回合/半血重组/BIND限次/两种伤害，Echo/拾取账本与Run重置。该 suite 有明确标识的数值/卡牌单元测试 fixture。
- `slice_loot_smoke.gd`：10,000 Seeds 普通触发 **1008/10000**，Affinity 不改变触发结果，强制模式仍不能越过 Ecology 合法性。
- `slice_world_smoke.gd`：实际物理移动与 E 交互、原场景接战、正常手牌/Focus 的完整通关、实体掉落、手动入库、防重领、继续探索、表现替换接口。正常通关没有注入卡牌、HP 或 Focus；模型单元测试与它区分。
- `slice_lifecycle_smoke.gd`：反应窗口及 Lexicon、不出掉落仍能退出、失败/真实场景重开。反应单元用显式 fixture，不冒充自然抽牌。
- 图形运行检查世界、Combat、骨堆、PICK UP、Run Bag、DEFLECT；检查 END TURN/反应按钮确实在视口内，而不只程序调用按钮信号。

测试默认不读写真实玩家知识存档。固定 Seed 可由世界场景的 `seed_value` 配置；debug F2 提供两种掉落模式。存档写失败/原文件损坏会显示知识存档警告，不用空数据覆盖原件。

## 已知问题与限制

- 当前自动化和实际渲染检查未发现阻断这条玩法链的程序问题，但不等于最终平衡/美术已通过验收。
- 有时 CLI 快速退出或部分旧 UI suite 结束时，用户原有 Godot AI 插件会报18个ObjectDB/5个脚本资源退出提示；在未使用新世界的旧0.8场景也能复现，资源路径均指向 `addons/godot_ai`。本次保留用户插件，不越界修改其生命周期代码。
- 正式资产、音效可听性、动画时序、正式VFX性能、非桌面分辨率需要首批资产接入后再验收。当前画面检查以1280×720桌面为基线。

## 下一步 / 范围锁

先由用户验收 Broken Graveyard；等待美术组交付已认可的环境、Skeleton/骨堆、Chisel、Echo、基础HUD/Word Action资源。按 `ART_CODE_CONTRACT_0_9.md` 接入同一个项目、复测尺寸/碰撞/事件/拾取。**在本切片验收前不推进 Veiled Walk、其他 Biome 或全量0.9。**
