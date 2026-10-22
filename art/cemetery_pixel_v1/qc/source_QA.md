# 场景目标图 QA

| 文件 | 原生尺寸 | 可见色数 | Alpha |
|---|---:|---:|---|
| `source/visual_target_960x540.png` | 960×540 | 64 | [255] |
| `source/visual_target_generated_reference.png` | 960×540 | 64 | [255] |

先用内置 image_gen 生成整体目标，再按它的画法制作地板和独立素材。原生成构图保留在 `source/visual_target_generated_reference.png`。

`visual_target_960x540.png` 用最终地板与独立物件重新合成，主角直接使用已确认 96 px 原图，修正 AI 原图中人物和墓碑偏大的比例。布局坐标见 `source/preview_placement.json`，仅用于美术预览。

构图：左下两座墓碑夹出入口 → 旧墓区 → 中右空地 → 坍塌墓穴 → 右上出口。静态图不含 Godot 接触阴影、雾、灯光或真实 Y-Sort。

检查：PNG 原生分辨率；所有可见像素均在共享调色板内；Alpha 仅 0/255；使用 nearest 采样，无抗锯齿或抖色。技术检查不替代 Godot 中的美术验收。
