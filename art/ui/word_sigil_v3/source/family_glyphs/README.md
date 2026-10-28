# 九类符号来源

按用户批准的 Word Sigil 第3档制作的原生几何字符。所有9张成品是11×11纯白透明PNG，程序负责染色、发光；没有用生成图代替精确1px路径，也没有抄Claude的占位图案。

- `build_family_glyphs.py`：手工定义的整数路径和端点，导出PNG、放大表和原生词旁检查。
- `family_glyphs_geometry.json`：正式几何定义及点阵；`godot_family_rows.json`为同一成品的大写类名行表。
- `protected_files.json`：覆盖QA之外需保护的既有文件哈希。
- `before_step2_QA.zip`：编辑共享QA前的完整恢复本。
- `before_native_readability_review.zip`、`before_rebuild_*.zip`：内部初稿／修改前的恢复记录，不是额外待选方案。

总表3×3按FORCE,DIRECT,DECAY / TOXICITY,PERCEPTION,CONTROL / REACTION,PROTECTION,RESTORATION排列。生成脚本不会修改任何运行时文件或第一步方案。重跑后若变了图形，需要重新核对和更新共享QA与Godot行表。
