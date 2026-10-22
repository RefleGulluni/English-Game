# Broken Graveyard 第二批交付检查

**状态：素材已交付，技术像素检查通过；Godot 视觉与空间验收待 Claude。**

- 检查 PNG 45 张（包含原始生成目标的清理版参考）；实际可见色并集 64，调色板上限 64。
- 调色板外颜色 0；非二值 Alpha 0；原生尺寸检查通过。
- 双网格 256 组合法邻接对比无错缝；基础变体 96 组互接无错缝。
- 动画 6 帧、固定画布/脚底、strip、4× GIF 均已检查。
- 原有 pixel_test 文件校验 33 个，变化 0。未改 Godot 场景或工程配置。

重点复核：动画仍有轻微衣物/持剑细节闪动，属于生产方式验证稿；草地/积水主观重复感、原点碰撞和人物落地感需实机确认。技术通过不等于美术终验通过。

完整统计 `batch2_QA.json`；分项记录 `palette/source/terrain/decals/path/props/player_anim/plates_QA.md`；总览 `batch2_overview.png` 为 2× nearest。

本批生成期间的可恢复备份位于仓库 `art_source/backups/cemetery_pixel_v1_batch2/`。原始 image_gen 输出保留在默认生成目录，路径与手写提示词在 source/ 中。临时处理文件、布局导引在交付前移入废纸篓，未删除用户原始素材。
