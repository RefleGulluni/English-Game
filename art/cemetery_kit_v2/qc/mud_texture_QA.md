# Mud texture — 第二项待确认

日期：2026-10-21
生成：内置 image_gen，直接使用已确认的 terrain/stone_texture_src.png 作笔触和风格参考。参考图不作为编辑目标；石板文件未修改。

## 交付
- terrain/mud_texture_src.png：1254×1254，原生生成 PNG，逐字节复制保存，非放大图。
- terrain/mud_texture.png：384×384，RGB 不透明 PNG，原图经 Lanczos 缩小；未额外调色、涂抹或修补接缝。
- qc/mud_texture_2x2.png：768×768，四张实际交付纹理按原像素直接重复，无间隔、遮盖或边缘混合。
- qc/stone_mud_compare.png：768×384；左侧为已确认的 stone_texture.png，右侧为 mud_texture.png；均按 384×384 原像素摆放，无色彩增强。
- qc/mud_texture_QA.md：本记录与最终提示词。

## 视觉检查
已查看实际交付纹理的 2×2 平铺图，检查水平、垂直接缝与中央四角交汇，未见明显方形拼接线或材质断裂。
已查看并排对比图：泥地明显更暗，略偏暖棕；石板偏冷灰。两者保留相近尺度的概括性手绘笔触。
泥地不含石块、碎石、规则几何、车辙、脚印、裂缝或物件。没有明确的结构和视觉焦点。
光照视觉检查：未见方向性光照渐变、镜面高光或投影；湿感仅靠压低色值表达。笔触有轻微斜向，与参考石板表面的绘画手法相近，不表现为凹凸沟纹。
整体仍可辨认绘画笔触，是否达到用户期望的“安静”程度有待本轮审阅。

## 数值核对
以最终 384×384 PNG 的 sRGB 转换到 D65 CIELAB 后逐像素统计，平均 L*：
- 石板：46.10
- 泥地：34.28
- 泥地低约 11.82 个 L* 单位。

RGB 均值（0–255）：
- 石板：(107.79, 110.17, 103.21)
- 泥地：(88.05, 79.44, 67.65)

泥地左右边缘 RGB 平均绝对差为 2.712/255，上下为 2.457/255；内部相邻像素横向为 1.194/255、纵向为 1.411/255。该统计仅辅助诊断，边缘像素并非完全一致，不能单独证明无缝；本次结论来自实际平铺图的视觉检查。
已验证高清源图缩小后逐像素等于 mud_texture.png，且 2×2 四个象限逐像素等于 mud_texture.png。
未做引擎内或 64/96 网格裁块验收。当前未制作 edge_brushes，需用户确认泥地后继续。

## Final prompt

Use case: stylized-concept. Asset: ONE full bleed opaque seamless square mud ground texture, not a scene or contact sheet. Input image is STYLE AND BRUSHWORK REFERENCE ONLY: approved cool grey wet flagstone stone_texture_src.png. Create its companion mud_texture, painted by the same artist at the same scale. Match the reference's restrained simplified matte hand-painted brushwork, using only a few soft broad quiet low contrast color patches and sparse simplified brush strokes of comparable size to the marks INSIDE its stone slabs. Do NOT copy slab boundaries, polygon shapes or joints. Mud is an unstructured continuous surface, no identifiable shapes or directional pattern, no islands of detail. Color: very desaturated dark grey-brown warm taupe, slightly warmer/browner than reference, visibly darker. Aim mean sRGB around (79,74,67), small gentle variations around this, no orange or saturated brown. Damp soil expressed through subdued dense matte color only, no puddles. 40% believable material 60% painterly simplification. This gets repeated hundreds of times behind game characters; favor plainness, quietness and extreme restraint, no focal feature. Absolutely uniform ambient illumination over whole image, no broad light/dark gradient or vignette, no directional light, no highlights, reflections, specularity, raised ridges, shadows or ambient occlusion. CRITICAL truly seamless repeat on BOTH axes: opposite edges continue identical material color and brushwork with NO square seams. Full square native high resolution suitable for later downsampling to 384x384, no borders or labels. NO rocks, pebbles, stones, gravel, cracks, slab shapes, cells, cobbles, dry mud polygons, regular patterns, tracks, footprints, tire ruts, ripples, furrows, streaks, grass, moss, debris, grit, sand grains, photographic microtexture or PBR. Just soft calm wet mud with a small number of broad understated painterly marks, consistent density throughout.

