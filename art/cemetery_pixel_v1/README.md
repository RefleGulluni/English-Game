# English Game · Cemetery Pixel v1 · Batch 2

唯一美术规范：`English_Game_Art_Direction_Bible_v3_Pixel_World_SpecLocked_CLEAN.md`。

96 px 主角 / 960×540 原生画面 / 32 px 地面格 / 64 色共享调色板 / 左上光源 / 3/4 俯视。语言本体同像素密度、精确且发光；本批不新增语言符文素材。

先看 `qc/batch2_overview.png` 和 `qc/batch2_QA.md`；动画看 `qc/walk_side_preview.gif`。

交付目录：source（目标图与来源）、terrain（两套16块双网格图集、12块基础变体）、decals（8）、path（8）、props（5及原点/占地说明）、player_anim（6帧与横排）、plates（平面整图对照）、qc（检查和预览）、tools（可复验的清理与检查流程）。

Godot 交接：全部使用 nearest、整数位置/缩放；Dual-Grid 索引及接缝说明见 terrain_QA；物件原点见 props/NOTES；动画原点 (40,96)，6帧120ms循环，向左镜像。正式动画像素精修和引擎验收尚未完成，本批用于房间与生产方式验证。

生成方法：内置 image_gen，手写提示词保存在 source/prompts.json 与 source/bases.prompt.txt，原始来源索引 source/generation_manifest.json。脚本只做提取、材质采样拼装、边缘修复、调色板规整与预览检查；不修改原有素材和 Godot 文件。
