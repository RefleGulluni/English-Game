# Word Sigil 第一步设计来源

这是程序可复现的 UI 几何／字形设计稿，不是像素场景物件，也不是交付给引擎加载的一张张词图。遵照需求由程序实时画词框的分工，直接在原生坐标定义几何和少量手工字形；本轮未调用图像生成，没有用生成图代替精确几何或英语拼写。

- `build_designs.py`：绘制三个方向、两种字体、状态／消耗、截图副本合成。
- `design_spec.json`：尺寸、锚点、配色和排布规则。
- `pixel_letters_9px.json`：本轮用到的局部大写字母。
- `protected_existing_files.json`：既有 UI／参考截图保护哈希。
- `backups/` 及 `before_rebuild_*.zip`：内部初稿的恢复记录，不是额外方案。

稿纸说明文字用本机 Hiragino Sans GB，未把系统字体复制进仓库。游戏里的衬线词确实使用项目已有 Cormorant Garamond SemiBold18；9px大写是本轮定义。重画时只输出本目录的设计／QC资料，不修改任何引擎场景或旧UI文件。重画不会自动更新手写QA，请复查后再交付。
