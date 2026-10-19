# English Game 0.9 — Art Direction & Visual Bible

> **Document Type：美术执行规格 / Visual Bible / 0.9 Production Art Guide**  
> **适用对象：美术执行组、视觉设计对话、UI/VFX/音频资产制作人员**  
> **上位依据：English Game 0.9 总体设计归档**  
> **目的：统一 0.9 的视觉、角色、场景、UI、VFX、Loot、Lexicon、音频语言，并给出第一批可直接执行的资产清单与生成提示词。**

---

# 0. 文档使用原则

本文件不是自由发挥参考，而是 0.9 阶段的视觉执行约束。

美术执行组必须优先保证：

1. **统一性高于单张图“惊艳”**
2. **可进入 Godot 高于纯概念图效果**
3. **角色/怪物/场景在 3/4 Top-Down 视角下可辨识**
4. **英语词与 Word Sigil 必须像力量，不像学习 App**
5. **世界先成立，UI 后出现**
6. **Loot 先作为世界物件存在，再作为系统奖励存在**
7. **避免泛用 AI Dark Fantasy 质感**
8. **所有核心资产必须考虑后续拆层、动画、Shader、VFX 和复用**

禁止把该项目做成：

- 像素 Roguelike；
- 照片级写实 RPG；
- 卡通/Q版暗黑游戏；
- 高饱和手游；
- 传统卡牌 UI；
- VHS / RGB Glitch 风；
- “英语学习 App + 暗黑皮肤”。

---

# 1. 总体 Art Direction

## 1.1 视觉定义

> **3/4 Top-Down 2.5D Painterly Semi-Realistic Dark Fantasy**  
> **with Geometric Language Surrealism**

中文：

> **3/4 斜俯视 2.5D 风格化手绘半写实暗黑幻想 + 几何语言超现实主义**

核心美术哲学：

> **The world is painterly and broken. Language is precise and structured.**  
> **世界是手绘的、破碎的；语言是精确的、有结构的。**

世界侧：

- 手绘质感；
- 可信材质；
- 真实空间逻辑基础；
- 低饱和；
- 雾；
- 磨损；
- 不完整；
- 柔和而不干净的笔触。

语言侧：

- 几何；
- 精确；
- 稳定；
- 清晰；
- 节点；
- 环；
- 线；
- 结构闭合；
- Concept Family 专属语义纹样。

两者必须形成视觉冲突。

---

# 2. 镜头与空间规则

## 2.1 相机

推荐：

> **3/4 Top-Down / Isometric-ish，但非严格 45° 等距。**

要求：

- 玩家可看到角色正面与侧面信息；
- 不做 RTS 超远镜头；
- 不做严格方格地图；
- 场景必须有前中后景；
- 角色在屏幕中应具备清楚剪影；
- 重要 Loot 可在地面中被自然发现。

## 2.2 Micro Exploration Scene

目标：

> **小而密。**

普通场景：

- 视觉入口清楚；
- 一眼能看懂主构图；
- 10–25 秒可直接走过；
- 30 秒～3 分钟实际探索；
- 0–2 个主要可交互对象；
- 不做空旷长路；
- 不做大地图式垃圾搜刮。

场景中允许：

- 前景遮挡；
- 雾；
- 局部光；
- 被墓碑/栏杆挡住的区域；
- 隐藏角落；
- 可调查碑文；
- Loot 实体；
- 战斗区域。

---

# 3. 色彩与光照

## 3.1 总体色彩

世界主基调：

- 深灰；
- 石灰；
- 褪色棕；
- 铁黑；
- 灰蓝；
- 低饱和绿；
- 暗酒红；
- 旧铜。

原则：

> **Low-saturation world, meaningful local color.**

颜色用于：

- 引导注意；
- 表达 Concept；
- 表达危险；
- 表达稳定；
- 表达稀有度。

禁止：

- 整体画面高饱和；
- 蓝紫魔法铺满；
- 橙光/紫光/红光作为默认高级感。

## 3.2 光照

世界光：

- 不追求摄影级物理正确；
- 优先服务构图与概念表达。

例如：

- Anchor 周围光可比现实更稳定；
- Fracture 可破坏光影对应关系；
- Redactor 附近可让色彩和光层被“拿走”。

---

# 4. 角色风格比例

## 4.1 人类

倾向：

> **65% 写实 / 35% 风格化**

要求：

- 6.5～7 头身；
- 正常人体结构；
- 轮廓优先；
- 服装结构清楚；
- 脸部不依赖微观写实；
- 3/4 Top-Down 缩放后依然可认。

## 4.2 场景

倾向：

> **50% 写实 / 50% Painterly**

材质可信，但形状和光影可为构图服务。

## 4.3 怪物

原则：

> **Fracture 越深，越远离真实。**

视觉梯度：

> Reality → Stylization → Conceptual Distortion → Unreadable Structure

---

# 5. 主角 Visual Guide

## 5.1 身份

> **初醒的 Wordbearer / 旧世界幸存者**

一句话：

> **A worn survivor whose true power is not what they carry, but what they understand.**

## 5.2 视觉关键词

- 克制；
- 磨损；
- 实用；
- 低调；
- 有辨识度；
- 非传奇英雄；
- 非现代穿越者；
- 非重甲骑士。

## 5.3 服装

建议：

- 长外套或短斗篷；
- 皮革 + 布料；
- 少量金属扣件；
- 功能腰带；
- 小型包袋；
- 耐用靴；
- 时代感模糊。

禁止：

- 巨大肩甲；
- 金色装饰；
- 发光披风；
- 满身 Rune；
- 开局即传奇英雄感。

## 5.4 标志物

建议加入：

> **Lexicon Strap / Fragment Pendant / 旧金属书页扣件**

平时不起眼。

与 Anchor / Word Sigil 共鸣时轻微响应。

## 5.5 生成 Prompt（概念图）

**Prompt：**

> 3/4 top-down game character concept for a painterly semi-realistic dark fantasy roguelike, a worn Wordbearer survivor, adult human, practical layered long coat and short weathered mantle, leather and cloth construction, muted charcoal, faded brown and cold gray-blue palette, subtle old metal fasteners, functional belt and small pouches, modest worn sword, no heroic armor, no oversized fantasy weapon, restrained silhouette with one distinctive lexicon fragment pendant or strap, believable human proportions around 6.5 to 7 heads tall, designed to remain readable from an isometric-ish 3/4 top-down camera, painterly textures, grounded materials, dark fantasy mood, subtle geometric language motifs only when activated, production-ready character sheet aesthetic

**Negative Prompt / 禁止项：**

> pixel art, anime, chibi, MMORPG armor, giant pauldrons, glowing full-body runes, cyberpunk, sci-fi, photorealistic face, superhero pose, ornate royal clothing, high saturation, giant sword, heavy plate armor, generic AI fantasy hero, front-facing portrait only

---

# 6. Eleanor Visual Guide

## 6.1 身份

> **药剂师 + 研究者 + 生存者**

一句话：

> **A woman who survived by turning chaos into order.**

## 6.2 视觉气质

- 成熟；
- 可信；
- 稳定；
- 克制；
- 有经验；
- 温和但不天真。

建议年龄感：

> 30 岁上下或略成熟。

## 6.3 服装

- 中长研究外套；
- 围裙式结构；
- 一侧工具包；
- 药瓶；
- 手写笔记袋；
- 旧铜扣；
- 深酒红 / 暖褐 / 暗金；
- 低饱和。

不要：

- “漂亮女药剂师”模板；
- 少女巫师；
- 高饱和药水商店 NPC；
- 夸张女巫帽；
- 纯贤者长袍。

## 6.4 语言痕迹

Eleanor 不应满身活跃 Word Sigil。

她更适合：

> 已沉积成生活习惯的稳定 Concept Marks。

这些 marks：

- 旧；
- 稳；
- 像使用痕迹；
- 不抢视觉中心。

## 6.5 Prompt

> mature female apothecary-researcher survivor in a painterly semi-realistic dark fantasy world, practical long work coat with apron-like construction, muted warm brown, deep burgundy and aged copper palette, tools and small potion bottles arranged for real use, subtle ink and chemical stains on hands and sleeves, calm experienced posture, intelligent but not aristocratic, subtle stable concept marks integrated into worn clothing rather than glowing magic, readable silhouette for 3/4 top-down 2.5D game, grounded materials, low saturation, warm restrained human presence in a broken world, production-ready character concept

**Negative：**

> teenage anime alchemist, witch hat, glamorous sorceress, revealing costume, high fantasy princess, neon potions, excessive glowing runes, cyberpunk, photorealistic fashion portrait, steampunk overload, high saturation

---

# 7. The Redactor Visual Guide

## 7.1 本质

> **删除、断开、抹除获得形体。**

一句话：

> **It does not destroy things. It removes the fact that they were there.**

## 7.2 核心关键词

- Absence；
- Precision；
- Silence；
- Missing Continuity；
- Redaction；
- controlled removal。

## 7.3 形体

建议：

- 保留高挑人形；
- 身体有缺失；
- 某些区域不是黑，而是“不存在”；
- 轮廓不连续；
- 衣物和身体边缘偶尔不匹配；
- 面部不可完全稳定；
- 动作中间过程缺失。

不是：

- 黑雾魔王；
- 骷髅王；
- 巨大铠甲 Boss；
- RGB 故障人；
- 赛博朋克 Glitch。

## 7.4 环境反应

Redactor 到来：

- 色彩减少；
- 声音减少；
- 文本缺失；
- 几何结构被删；
- UI 断裂；
- 光影出现“东西已经不在，但关系还残留”的感觉。

## 7.5 Prompt

> towering humanoid conceptual antagonist for a painterly semi-realistic dark fantasy game, known as The Redactor, elegant but deeply unsettling, human-like silhouette with precise missing sections as if parts of existence were cleanly removed, discontinuous outline, partial facial features that cannot fully stabilize, black, gray-white and nearly desaturated cold tones, no smoke monster aesthetic, no digital RGB glitch, movement implied through missing continuity rather than teleportation, surrounding architecture and lettering partially erased with clean absence, painterly broken world contrasted by precise redaction shapes, minimal controlled presence, quiet terrifying authority, 3/4 top-down readable silhouette, dark fantasy concept art

**Negative：**

> RGB glitch, VHS, cyberpunk, television static, black smoke demon, horned devil, armored dark lord, giant scythe, red glowing eyes cliché, explosive magic, neon, gore, zombie, generic boss armor

---

# 8. Cemetery Biome Visual Identity

核心气质：

> **“看不清、杀不净、拖不起。”**

生态主题：

> 死亡之后，有某种东西没有正确结束。

视觉递进：

> **实体残留 → 形体残留 → 情绪残留 → 职责残留**

## 8.1 环境关键词

- wet stone；
- leaning gravestones；
- rusted iron fences；
- dead trees；
- collapsed mausoleums；
- low fog；
- distant chapel silhouette；
- old candles；
- broken inscriptions；
- scattered bones；
- low saturation；
- quiet weathering。

禁止：

- 万圣节墓园；
- 紫色魔雾；
- 高饱和幽灵光；
- 大量哥特尖塔堆砌；
- 纯黑背景；
- 满地发光蘑菇。

---

# 9. Grave Skeleton

## 9.1 概念

> **肉体结束了，但结构不肯结束。**

## 9.2 视觉

- 骨骼可信；
- 旧布条；
- 铁钉；
- 墓葬线；
- 缝合痕迹；
- 少量 Fracture 结构；
- 骨头之间像被某种东西强制维持。

## 9.3 动作

- 僵硬；
- 关节停顿；
- 某些动作像被拉线牵动；
- 受击时局部骨件短暂错位。

## 9.4 死亡

第一次 HP 归零：

- 骨架散开；
- 武器落地；
- Bone Remains 留下；
- 仍有细微牵引结构试图重组。

永久处理：

- 牵引彻底断开。

## 9.5 Loot

- 实体；
- 从骨堆中滚出来；
- 旧金属 / 骨饰 / Chisel 等。

## 9.6 Prompt

> grave skeleton enemy for a painterly semi-realistic dark fantasy roguelike, believable old human bones held together unnaturally by burial cords, rusted iron nails, torn funeral cloth and subtle fractured structural lines, not a generic fantasy skeleton warrior, stiff asymmetric posture, worn grave weapon, visual emphasis on forced reassembly and unfinished burial structure, muted bone, rust, gray and brown palette, readable silhouette from 3/4 top-down view, modular 2D game asset concept, dark cemetery atmosphere

**Negative：**

> cartoon skeleton, glowing green eyes, pirate skeleton, ornate armor, flaming skull, Diablo clone, excessive magic glow, cute, pixel art, anime skeleton

---

# 10. Veil Ghost

## 10.1 概念

> **身体结束了，但存在感还没散。**

## 10.2 视觉

- 人形薄；
- 与雾融合；
- 面部不完整；
- 衣物和身体边界模糊；
- 不靠透明度单一表现。

FADED：

- 身体“不连续”；
- 局部先消失；
- 轮廓与背景混合。

REVEALED：

- OBSERVE 后部分轮廓被重新定义。

## 10.3 Loot

- 不“啪”地落地；
- 悬浮在其原本位置；
- 像残响凝结。

## 10.4 Prompt

> veil ghost enemy for a painterly semi-realistic dark fantasy cemetery, a human presence that is failing to leave the world correctly, thin unstable silhouette partially merging into fog, fragmented continuity in torso and limbs, incomplete face, faded funeral clothing indistinguishable from the body in places, not simply transparent, visual states suitable for FADED and REVEALED through reconstruction of contour, subtle memory-trace geometry, muted cold gray and blue palette, 3/4 top-down readable game silhouette, restrained supernatural design

---

# 11. Mourning Wraith

## 11.1 概念

> **死亡结束了，但情绪没有结束。**

## 11.2 视觉

- 被悲伤拉长的人形；
- 下垂；
- 拖延；
- 重；
- 湿布般悬垂；
- 几乎看不出原本的人；
- 哭泣/哀悼痕迹抽象化。

## 11.3 动作

> 慢，但一直在靠近。

攻击更像：

- 环境变重；
- 空气压低；
- 亮度下降；
- UI 产生压迫感。

## 11.4 死亡

- 不是轻快消散；
- 情绪结构塌下；
- 像长期悬挂的湿布终于失去支撑。

## 11.5 Prompt

> mourning wraith for a painterly semi-realistic dark fantasy roguelike, elongated grieving humanoid form, drooping weight, soaked hanging funeral cloth merging with an almost erased body, slow oppressive movement, hollow head shape and subtle tear-like conceptual traces, human identity mostly lost beneath lingering grief, low-saturation cold charcoal and muted blue-gray, no bright ghost glow, readable from 3/4 top-down, cinematic but production-oriented enemy concept

---

# 12. Mourning Keeper

## 12.1 概念

> **职责没有结束。**

本来是：

- 守墓者；
- 哀悼者；
- 封印者。

Fracture 后：

> 过度执行职责，不允许任何东西真正离开。

## 12.2 视觉

- 庄严；
- 直；
- 稳；
- 不需要巨大体型；
- 长袍；
- 杖；
- Funeral Bell；
- Seal；
- 墓葬面具；
- Keeper Script。

两阶段：

### Veiled Mourning

- 克制；
- 稳定；
- 封印；
- 少量能量。

### Grave Awakening

- Seal 破裂；
- 墓园响应；
- Bell 与 Remains 被唤醒；
- 仍保持庄严，而不是发疯。

## 12.3 Prompt

> Mourning Keeper boss for a painterly semi-realistic dark fantasy cemetery, solemn grave guardian and ritual mourner corrupted by over-executed duty, tall but not oversized, upright ceremonial silhouette, weathered layered funeral robes, grave staff, small ritual funeral bell, sealing plates and a restrained burial mask, visually stable and authoritative compared to other undead, muted ash, black, aged bronze and dark cloth, phase-two design reveals broken seals and awakened cemetery structures without turning into a berserk monster, strong 3/4 top-down silhouette, elegant oppressive boss concept

---

# 13. Word Sigil Visual System

## 13.1 核心

> **Word 是力量，不是卡牌。**

不做传统矩形卡片。

战斗底部显示：

> 悬浮的 Word Sigil / Lexicon Fragment。

默认信息：

- Word；
- Focus Cost；
- 极短机制提示。

详细信息：

> Hover / Inspect 展开。

## 13.2 Concept Family Geometry

### Decay

- 裂纹；
- 侵蚀；
- 粉化；
- 结构塌陷。

### Control

- 环；
- 束线；
- 结；
- 闭合节点。

### Revelation

- 透镜；
- 射线；
- 对焦；
- 精确展开。

### Toxicity

- 渗透；
- 扩散；
- 内部传播。

### Restoration

- 缝合；
- 回环；
- 重新闭合。

### Memory

- 回声；
- 重复；
- 残影结构。

### Mourning

- 下垂；
- 钟形；
- 长尾回响。

## 13.3 Prompt

> game UI concept for a “Word Sigil” system in a painterly semi-realistic dark fantasy roguelike, no traditional rectangular cards, English word itself is the visual center, floating lexical fragment with precise geometric semantic structures, focus-cost node integrated into the sigil edge, restrained dark fantasy UI, crisp language geometry contrasted against soft painterly world, examples ERODE with eroding fractured geometry, BIND with tightening rings and knots, OBSERVE with lens and focusing structure, production-ready HUD concept, elegant readable typography, minimal clutter

**Negative：**

> trading card layout, Hearthstone card, poker card frame, school vocabulary flashcard, colorful mobile game UI, giant icons, Chinese translation under every word, neon sci-fi HUD, cluttered stats

---

# 14. Knowledge Stage Visual Evolution

## ENCOUNTERED

> **词存在。**

- 不稳定；
- Concept Pattern 残缺；
- 字形边缘不完整。

## RECOGNIZED

> **词稳定。**

- 拼写稳定；
- 基础 Pattern 成形。

## UNDERSTOOD

> **概念完整。**

- Pattern 闭合；
- Concept Seal 成形。

## USABLE

> **概念回应你。**

- Invocation Ring 完整；
- Focus Node 激活；
- Target Response 可用。

原则：

> 不是“灰→蓝→紫→金”。

而是：

> **Fragmentation → Stability → Semantic Structure → Invocation**

---

# 15. Lexicon Concept Map

## 15.1 视觉定义

> **远看像概念星图，近看像破碎书页与符文结构。**

Lexicon 不是：

- 单词列表；
- 词典；
- 技能树；
- 学习 App。

## 15.2 三层

### Far View

- Concept Region；
- Anchor Word；
- 黑暗未知区；
- 主要连接。

### Cluster View

- Word Nodes；
- 语义连线；
- 一个词可跨多个 Family。

### Word Detail

- Meaning Fragment；
- World Contexts；
- Concept Links；
- Invocation；
- Memory Trace。

## 15.3 Prompt

> dark fantasy lexicon concept map UI, a broken language universe rather than a dictionary, viewed as a hybrid of semantic star map and fractured ancient knowledge pages, precise geometric English word sigils connected by thin semantic lines, dark unexplored regions with incomplete fragment silhouettes, painterly broken parchment-like spatial fragments suspended in a deep subdued background, zoomable concept clusters, elegant readable typography, no conventional skill tree boxes, no spreadsheet, no school vocabulary app, subtle geometric structure and memory-trace feeling

---

# 16. Lexicon Anchor Visual Guide

## 16.1 定义

> **保存“玩家是谁”的地方，而不是普通复活点。**

## 16.2 外观

- 黑色 / 旧石质结构；
- 巨大竖立碎片；
- 残缺环；
- 精确 Word-Sigil 刻痕；
- Fracture 裂口；
- 中央有明显“缺失”。

周围：

- 雾退开；
- 空间变稳定；
- 线条更精确；
- 声音杂质减少。

禁止：

- 蓝色水晶；
- 篝火；
- 圣光祭坛；
- 常规存档点。

## 16.3 Prompt

> monumental Lexicon Anchor in a painterly semi-realistic dark fantasy underground chamber, not a crystal and not a shrine, a massive broken vertical black-stone knowledge structure with incomplete concentric rings, precise geometric word-sigil engravings, thin restrained luminous lines, visible fractured gaps and one major missing central segment, surrounding air unusually stable and quiet, fog receding from it, ancient but not conventionally magical, grounded architectural weight mixed with impossible language geometry, 3/4 top-down 2.5D game environment concept

---

# 17. True Words / Fracture / Corruption VFX

## 17.1 True Words

关键词：

> Order / Precision / Structure

视觉：

- 清晰；
- 精确；
- 完整；
- 干净；
- 不靠大量粒子。

## 17.2 Fracture

关键词：

> Broken Connection

表现：

- 结构错位；
- 缺字；
- 阴影和物体不一致；
- 断线；
- 重复；
- 不连续。

禁止：

- RGB；
- VHS；
- TV static；
- cyber glitch。

## 17.3 Corruption

### Decay

- 表面磨损；
- 粉化；
- 字体被时间侵蚀。

### Obscurity

- 信息雾化；
- 边缘不确定；
- 非简单屏幕变黑。

### Inattention

- 注意焦点轻微不稳定；
- 非关键反馈略漂；
- 不影响核心可读性。

---

# 18. Loot Visual System

核心：

> **Loot first exists as a thing in the world, then as a stat in the UI.**

## 18.1 Echo

- 自动吸收；
- 不需要玩家拾取；
- 轻粒子；
- 流向玩家；
- 不像金币。

## 18.2 Special Loot

- 世界实体；
- 玩家手动拾取；
- 微弱高光；
- 不用巨大光柱。

## 18.3 稀有度

原则：

> **Rarity is expressed through identity, structure, and world reaction—not just brightness.**

### Common

- 实体；
- 旧；
- 简单；
- 轻反光。

### Rare

- 更完整 Concept Pattern；
- 稳定共鸣。

### Epic

- 轻环境反应；
- 轻悬浮 / 结构变化。

### Legendary

- 明显规则感；
- 世界产生响应；
- 不是更亮而已。

### Boss Exclusive

> 优先继承 Boss 身份。

---

# 19. Echo / Loot VFX Prompt

## Echo

> subtle dark fantasy echo-energy pickup effect, not coins, thin translucent memory-like fragments rising from defeated enemies and gently pulling toward the player in smooth curved streams, restrained pale spectral light, soft particle trails, sense of resonance returning to its proper place, designed for 3/4 top-down painterly game, minimal visual noise, no bright arcade sparkle

## Skeleton Loot

> small weathered relic emerging physically from a collapsed pile of bones in a dark cemetery, old metal or bone object rolling slightly free after combat, barely noticeable restrained highlight, physically grounded, no loot beam, no floating UI marker, painterly semi-realistic dark fantasy, designed to create the feeling “wait, something dropped”

---

# 20. Boss Exclusive Visual Rule

Boss Exclusive：

- 不能凭空生成；
- 必须从 Boss 身上真实留下；
- 声音和视觉继承 Boss；
- 不显示成通用“橙色传奇”。

例：

### Keeper’s Funeral Bell

- 从 Keeper 手中脱落；
- 滚到石阶；
- 声音停止；
- 余响很长。

### Seal of the Unburied

- 从胸前 / 仪式结构上裂下；
- Seal Pattern 仍在轻微响应。

### The Last Mourner

- 更像 Keeper 最核心的 Mourning 结构残留；
- 不等于普通装备。

---

# 21. Combat HUD

原则：

> **常驻少，动态多。**

常驻：

- HP；
- Armor；
- Focus；
- Corruption；
- Word Sigil；
- 敌人 HP；
- Structure；
- Intent。

详细信息：

> OBSERVE / Hover / Inspect。

Relic：

> 只在触发时短暂抢注意力。

禁止：

- 右边长期挂十几个 Relic 图标；
- 敌人头顶满屏数值；
- 中文释义常驻 Word 下方；
- 学习题风格 UI。

---

# 22. Exploration HUD

原则：

> **HUD should appear as a response to attention, not as a permanent layer over the world.**

探索：

- 极简 HP；
- 必要状态；
- 对象附近显示 EXAMINE / PICK UP / OPEN；
- 目标短暂出现；
- 不常驻 Mini-map；
- 不常驻 Build 百分比；
- 不常驻 Relic 列表。

---

# 23. 音频 Art Direction

## 23.1 总原则

> **Silence is part of the soundtrack.**

> **Echo sounds like resonance returning, not currency being collected.**

> **Words sound like structures being invoked, not spells being cast.**

> **Fracture removes continuity. Redactor removes sound itself.**

## 23.2 World Audio

Cemetery：

- 风；
- 铁栏；
- 湿泥；
- 雨；
- 远钟；
- 枯枝；
- 布料；
- 不确定远处动静。

不要持续满铺 BGM。

## 23.3 Echo

声音：

- 空气牵引；
- 收束；
- 柔和确认；
- 多个 Echo 合并动态音色。

禁止金币音。

## 23.4 Loot “叮”

结构：

> 物理 Foley + Concept Resonance

Skeleton：

> bone / metal clink + 极轻共鸣。

目标：

> 玩家听见就有“掉东西了”的条件反射。

## 23.5 Word Audio

### Decay
干、碎、磨损。

### Control
张力、闭合。

### Revelation
对焦、清晰。

### Toxicity
渗透、内部活动。

### Restoration
缝合、重新对齐。

### Memory
残响、重复。

### Mourning
长尾、钟、低频。

## 23.6 Anchor

不是“响”。

而是：

> 越靠近，杂音越少。

## 23.7 Fracture

不是 glitch。

是：

> 声音连续性缺失。

## 23.8 Redactor

> Absence.

它出现时：

- 音乐层被拿掉；
- 环境声被拿掉；
- 预期的冲击声不出现。

---

# 24. 音乐制作 Brief

建议：

> AI 辅助生成 + 人工筛选/剪辑 + Stem 化 + Godot 动态混音。

Cemetery Music 不建议生成一首完整永远循环的 BGM。

拆为：

- Ambient Bed；
- Low Drone；
- Mourning Motif；
- Combat Layer；
- Grave Pressure Layer；
- Boss Bell Layer。

## 24.1 Cemetery Ambient Prompt

> sparse dark fantasy cemetery ambience for a painterly semi-realistic roguelike, restrained and atmospheric rather than cinematic trailer music, perceived slow pulse around 70–90 BPM without a constant explicit beat, low drones, distant aged metal bell appearing only occasionally, incomplete mourning motif that never fully resolves, large spaces of silence, subtle organic textures, no heroic harmony, no constant choir, no lush orchestral wall, leave dynamic space for footsteps, Echo absorption, loot drops and ghost sound effects, designed to be split into loopable stems

## 24.2 Mourning Keeper Boss Prompt

> dark ritual boss music built from the cemetery’s previously heard distant mourning motifs, restrained low percussion, aged funeral bell as a structural motif rather than constant impact, solemn and inevitable instead of bombastic, phase one controlled and ceremonial, phase two expands existing layers rather than changing genre, long unresolved harmonic tails, sparse strings or low drones, no heroic trailer brass, no epic choir wall, no fast action-metal rhythm, designed as separate adaptive stems for Godot

## 24.3 Redactor Audio Prompt

> minimal conceptual horror sound design representing absence and deliberate deletion, not digital glitch, use interrupted continuity, missing transients, abruptly cut reverberation tails, disappearing environmental layers, near-silence as tension, precise dry removals rather than explosive impacts, unsettling clean gaps where sound should exist, suitable for The Redactor in a dark fantasy language-based world

---

# 25. Prologue Key Scene Art Direction

0.9 中序章流程完整，但只部分达到高完成度。

重点精修：

1. Abandoned Station
2. Lexicon Anchor
3. The Redactor / Erasure / Return

---

# 26. Scene 01 — Abandoned Station

情绪：

> **Familiar → Empty → Slightly Wrong**

视觉：

- 冷灰；
- 湿润；
- 旧站台；
- 长椅；
- 灯管；
- 铁轨；
- 远处微弱异常暖/暗红；
- 普通英文标识。

关键 Fracture：

> `WAY OUT` → `WAY  UT`

不要大特效。

## Prompt

> abandoned underground station for a 3/4 top-down 2.5D painterly semi-realistic dark fantasy game, originally ordinary modern-or-timeless transit architecture now empty and damp, wet platform floor, old benches, faded EXIT and PLATFORM signs, dead fluorescent fixtures, dark tunnel, restrained cold gray-blue palette with a tiny distant muted red-warm anomaly, subtle evidence of missing letters and wrong continuity rather than obvious horror, cinematic composition but production-usable modular environment, low saturation, no monsters in foreground, first-scene atmosphere of familiarity becoming quietly wrong

---

# 27. Scene 02 — Fractured Passage

情绪：

> **Unease → Impossible → Contact → Temporary Stability**

视觉重点：

- 重复编号；
- 空间尺度不合理；
- 门位置改变；
- 文字与物理结构同步失效；
- 第一次 Word Fragment；
- 精确语言结构短暂稳定现实。

---

# 28. Scene 03 — Eleanor’s Shop

情绪：

> **Relief → Curiosity → Trust, but not certainty**

环境：

- 暖褐；
- 旧铜；
- 暗酒红；
- 药瓶；
- 手写纸；
- 工具；
- Fragment；
- 修补家具；
- Anchor 上方的人工秩序。

## Prompt

> Eleanor’s underground apothecary and research refuge in a painterly semi-realistic dark fantasy world, 3/4 top-down 2.5D interior, warm restrained amber, aged copper, deep burgundy and dark wood against the cold broken world outside, practical glass bottles, handwritten research notes, preserved fragments, repaired furniture, real working tools, subtle stable geometric markings integrated into the floor and walls around an unseen deeper Lexicon Anchor, lived-in survival workspace rather than magical shop, low saturation, intimate human order carved out of chaos

---

# 29. Scene 04 — Lexicon Anchor

情绪：

> **Silence → Recognition → Connection → Unanswered Meaning**

场景重点：

- 向地下走；
- 杂音减少；
- Anchor 第一次出现；
- 语言结构比世界更稳定；
- Concept Map 仅显示极少 Fragment。

---

# 30. Scene 05 — The Redactor Encounter

情绪：

> **Confidence → Unease → Powerlessness → Erasure**

表现顺序：

- 声音先缺失；
- 文字缺失；
- 墙面“被拿走”；
- Redactor 远处出现；
- UI 少量断裂；
- Word Sigil 尝试反抗；
- Redactor 删除 Sigil 一部分；
- 场景越来越少。

---

# 31. Scene 06 — Erasure

不显示：

> YOU DIED

视觉层级被删除：

1. 武器细节；
2. 服装纹理；
3. 阴影；
4. 轮廓；
5. Word Fragment；
6. 声音；
7. 身份。

最后：

> 1～2 秒真正空白。

---

# 32. Scene 07 — Return to Anchor

重构：

> **Knowledge → Identity → Body**

先出现：

- Word Sigil；
- Fragment；
- Concept Link；

再出现：

- 玩家轮廓；
- 服装；
- 身体。

这里第一次真正体现：

> **The world forgets. You do not.**

---

# 33. Cemetery Vertical Slice — 7 Scene Art Scope

## A+ — Broken Graveyard

最高优先。

验证：

- Skeleton；
- Bone Remains；
- Echo；
- Loot；
- “叮”；
- PICK UP；
- Combat → Exploration 连续性。

## A — Veiled Walk

验证：

- Ghost；
- FADED；
- REVEALED；
- OBSERVE；
- Word Sigil；
- HUD 信息层。

## A — Cemetery Entry

必须漂亮。

可作为未来 Screenshot 候选。

## A — Black Mist Well

验证：

- Mystery；
- 不透明风险；
- 雾；
- Wraith；
- Corruption。

## B — Sheltered Grave

Recovery。

重点：

> 安静。

## B — Forgotten Ossuary

World Build：

- Explorer；
- Scavenger；
- Scholar。

## A+ — Mourning Chapel

Boss 汇总。

---

# 34. Cemetery Entry Prompt

> wide 3/4 top-down 2.5D painterly semi-realistic dark fantasy cemetery entrance, layered composition with foreground rusted iron fence and dead branches, midground worn gravestones and muddy paths, low moving fog, distant ruined mourning chapel silhouette, old stone, faded moss, muted gray-blue, ash-brown and iron-black palette, subtle candle traces, no bright magic, player-sized readable path, cinematic but modular game environment, strong depth without full 3D realism, restrained gothic atmosphere, world feels old, wet and quietly wrong

---

# 35. Broken Graveyard Prompt

> compact hand-composed micro exploration scene for a 3/4 top-down painterly dark fantasy roguelike, broken graveyard with tilted headstones, muddy stone path, scattered bones, one Grave Skeleton encounter zone, enough clear space for turn-based combat lock-in, subtle environmental storytelling, layered foreground and background, low fog, restrained cold palette, a collapsed bone pile area designed so a tiny physical relic could visibly remain after Echo particles are absorbed, modular production-ready environment rather than promotional illustration

---

# 36. Veiled Walk Prompt

> narrow cemetery path for a 3/4 top-down 2.5D painterly dark fantasy game, layered fog and gravestones create partial visual obstruction, a Veil Ghost can merge naturally into mist and become visually redefined after OBSERVE, low saturation cold gray-blue, worn stone, iron fence silhouettes, subtle memory traces, clean combat space without obvious arena walls, atmospheric but readable gameplay composition, no bright ghost glow

---

# 37. Black Mist Well Prompt

> dangerous mystery micro-scene in a painterly semi-realistic dark fantasy cemetery, ancient stone well surrounded by unusually heavy black-gray mist, environmental clues suggest depth and danger without explicit UI rewards, subtle mourning remnants, wet stones, restrained ominous composition, enough room for player to approach, inspect, retreat or descend deeper, distant suggestion of a Mourning Wraith rather than visible full monster, low saturation, no purple magical fog, 3/4 top-down gameplay-ready layout

---

# 38. Mourning Chapel Prompt

> ruined mourning chapel boss arena in a 3/4 top-down painterly semi-realistic dark fantasy cemetery, solemn stone architecture, broken ritual seals, old funeral bells, graves responding around the perimeter, central space designed for Mourning Keeper boss combat, low fog, aged bronze, ash-gray and deep black cloth accents, visually connects all cemetery motifs seen earlier, ceremonial rather than giant gothic spectacle, strong readable silhouette and combat space, phase-two elements capable of awakening without changing the scene into bright magical chaos

---

# 39. 资产生产原则

所有生成/绘制资产需要考虑：

- 是否可拆前景/中景/后景；
- 是否可透明背景；
- 是否可做 Sprite / Cutout；
- 是否可重复使用；
- 是否能从 3/4 视角看清；
- 是否符合统一光向；
- 是否符合统一色板；
- 是否能进入 Godot；
- 是否需要 Shader 而不是烘死在图片里；
- 是否需要 VFX 独立层。

禁止直接把一整张概念图当最终游戏场景。

---

# 40. Godot 落地建议

## 40.1 外部资产制作

适合在外部制作：

- 角色主体；
- 怪物主体；
- 墓碑；
- 树；
- 墙；
- 建筑；
- 道具；
- Loot；
- UI 图形；
- Word Sigil 基础纹样；
- 静态 Concept Art。

## 40.2 Godot 内实现

优先在 Godot 中实现：

- 雾；
- 动态光；
- Shader；
- Fracture；
- Ghost Fade；
- Echo 吸收；
- Loot 高光；
- Word Sigil 激活；
- Corruption HUD 影响；
- Parallax；
- 粒子；
- 屏幕空间轻微 Distortion；
- 战斗 HUD 动态进出；
- 动态音乐 Stem 混音。

不要把这些全部预烘焙进静态图。

---

# 41. 第一批资产清单（Production Batch 01）

## 41.1 必做角色/敌人

1. 主角 Base Concept
2. Eleanor Base Concept
3. The Redactor Base Concept
4. Grave Skeleton
5. Veil Ghost
6. Mourning Wraith
7. Mourning Keeper Phase 1
8. Mourning Keeper Phase 2

## 41.2 必做场景

1. Abandoned Station Key Frame
2. Eleanor’s Shop Key Frame
3. Lexicon Anchor Key Frame
4. Redactor Encounter Key Frame
5. Cemetery Entry
6. Broken Graveyard
7. Veiled Walk
8. Black Mist Well
9. Mourning Chapel

## 41.3 必做 UI / System Art

1. Word Sigil Template
2. ERODE Sigil
3. BIND Sigil
4. OBSERVE Sigil
5. Knowledge Stage 4-state visual
6. Lexicon Concept Map
7. Combat HUD
8. Exploration HUD
9. Loot interaction prompt
10. Relic icon / object visual language

## 41.4 必做 VFX

1. Echo absorption
2. Special Loot subtle highlight
3. Ghost FADED
4. Ghost REVEALED
5. Fracture
6. Redactor erasure
7. Corruption — Decay
8. Corruption — Obscurity
9. Corruption — Inattention
10. Word Sigil invocation
11. Anchor reconstruction

## 41.5 必做 Loot Objects

1. Weathered Chisel
2. Bitter Vial
3. Second Thought
4. Grave-Seeker’s Compass
5. Bonepicker’s Charm
6. Margin Notes
7. Rot-Stained Purse
8. The Cartographer’s Debt
9. Keeper’s Funeral Bell
10. Seal of the Unburied
11. The Last Mourner
12. Child’s Burial Coin
13. Half-Remembered Name
14. Unsent Epitaph

---

# 42. 第一批音频清单

## Core SFX

1. Echo absorption
2. Skeleton special-loot clink
3. Ghost loot resonance
4. Wraith loot residual hum
5. Common pickup
6. Rare pickup
7. Boss Exclusive pickup
8. Word Sigil activation
9. ERODE invocation
10. BIND invocation
11. OBSERVE focus/reveal
12. Lexicon open
13. Lexicon close
14. Anchor proximity
15. Anchor reconstruction
16. Fracture continuity break
17. Redactor deletion
18. Skeleton reassembly
19. Ghost fade
20. Wraith pressure

## Music Stems

### Cemetery
- Ambient Bed
- Low Drone
- Mourning Motif
- Combat Layer
- Grave Pressure Layer

### Mourning Keeper
- Phase 1 Stem
- Phase 2 Stem
- Funeral Bell Motif

### Prologue
- Station Ambient
- Fractured Passage Layer
- Eleanor Refuge Layer
- Anchor Silence/Resonance Layer
- Redactor Absence Layer

---

# 43. 美术生成工作流

推荐：

1. 先生成 **Style Exploration**
2. 司令部选定 1 个方向
3. 固定：
   - 比例
   - 色板
   - 光向
   - 镜头
   - 材质
   - 轮廓
4. 再做 Character Sheet / Environment Kit
5. 再生成 Production Assets
6. 进入 Godot 测试
7. 回司令部验收
8. 不合格则回到风格级修正，而不是每张图单独乱修

---

# 44. AI 素材一致性要求

AI 生成资产必须记录：

- Prompt；
- Negative Prompt；
- 参考图；
- 角色固定特征；
- 色板；
- 镜头；
- 光向；
- Seed（如工具支持）；
- 生成工具；
- 日期；
- 许可/商用信息。

同一角色禁止仅靠“重新写一句 Prompt”反复生成。

应先建立：

> **Master Character Sheet**

之后所有动作与视图尽量基于该基准。

---

# 45. 美术验收标准

任何资产进入 0.9 前，至少检查：

## 风格

- 是否属于同一游戏？
- 是否明显 Pixel / Anime / Generic AI Fantasy？
- 是否保持低饱和？
- 是否存在“世界 painterly / 语言 geometric”的区分？

## 游戏性

- 3/4 Top-Down 看得清吗？
- 缩小后剪影是否成立？
- Loot 是否能发现但不刺眼？
- 战斗信息是否清晰？
- 场景是否留足角色和敌人空间？

## 世界观

- True Word 是否像 Order？
- Fracture 是否像 Broken Connection，而不是 glitch？
- Corruption 是否像感知/状态偏转？
- Redactor 是否表达 Absence？
- Anchor 是否表达 Stability / Memory？

## UI

- 是否像游戏，不像学习 App？
- Word 是否是主体？
- 是否过度依赖卡框？
- 是否信息爆炸？

## Production

- 能否拆层？
- 能否进入 Godot？
- 是否需要程序 Shader 而非静态烘焙？
- 是否可复用？
- 是否有版权/商用记录？

---

# 46. 0.9 美术完成度优先级

## A+

- Broken Graveyard
- Mourning Chapel / Mourning Keeper

## A

- Cemetery Entry
- Veiled Walk
- Black Mist Well
- Abandoned Station Key Frame
- Lexicon Anchor
- Redactor / Erasure / Return
- Word Sigil
- Combat HUD

## B

- Sheltered Grave
- Forgotten Ossuary
- Eleanor’s Shop 完整精修
- Lexicon Concept Map 完整动态版本

---

# 47. 最终禁止清单

美术组不得自行改变以下方向：

- 不改为纯 Pixel；
- 不改为全 3D 写实；
- 不改为 Q 版；
- 不改为传统卡牌 UI；
- 不把 Loot 做成手游光柱；
- 不把 Fracture 做成 RGB Glitch；
- 不把 Redactor 做成普通黑暗魔王；
- 不把 Anchor 做成蓝水晶复活点；
- 不让 Word Sigil 常驻中文释义；
- 不让探索 HUD 覆盖大半屏幕；
- 不让 Cemetery 变成紫色魔法墓园；
- 不让 Boss Exclusive 使用统一橙光表达；
- 不把每个世界事件重新做成弹窗卡片；
- 不为了“酷”破坏可读性和 Godot 落地性。

---

# 48. 美术组首轮目标

首轮不要尝试做全游戏。

先回答三个问题：

> **1. English Game 看起来是否已经不像学习软件？**  
> **2. Broken Graveyard 的“Skeleton → Echo → 叮 → Loot → PICK UP”是否有真实游戏感？**  
> **3. Word Sigil / Lexicon / Anchor 是否形成了只属于 English Game 的视觉身份？**

如果这三点成立：

> 继续扩产。

如果不成立：

> 停止量产，回司令部调整 Art Direction。

---

# 49. 核心视觉语句

> **The world is painterly and broken. Language is precise and structured.**

> **Loot first exists as a thing in the world, then as a stat in the UI.**

> **Rarity is expressed through identity, structure, and world reaction—not just brightness.**

> **Words sound like structures being invoked, not spells being cast.**

> **Silence is part of the soundtrack.**

> **True Words = Order.**

> **Fracture = Broken Connection.**

> **Corruption = Distorted Perception / State.**

> **Lexicon is not a dictionary. It is a broken language universe the player repairs.**

> **The Lexicon Anchor does not preserve life. It preserves who the player is.**

---

# 50. 文档状态

> **English Game 0.9 Art Direction & Visual Bible — First Production Edition**

本版本已经足够启动：

- 美术概念设计；
- 第一批角色/怪物；
- Cemetery Asset Kit；
- Word Sigil；
- UI；
- VFX；
- 音频原型；
- 序章关键 Key Frame；
- 0.9 Cemetery Vertical Slice 视觉生产。

后续若实机效果、Godot 落地、资产一致性或玩法可读性出现问题：

> **停止局部无序修改，返回“司令部”重新评估方向。**
