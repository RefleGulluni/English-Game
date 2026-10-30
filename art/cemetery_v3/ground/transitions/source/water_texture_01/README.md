# 积水纹理01：倒影重复自查未通过，已停止

当前状态WATER_STOPPED_REFLECTION_REPETITION，water_texture_01.png保留供检查，不是已通过素材，未接入游戏。

输入只来自三件已通过积水贴花的原生水面像素（保存标签3，排除湿泥／岸边／亮点）和已通过veiled_base_01.png。输入副本和水面选区保存在本目录，原文件未改。01_surface_color_sources.json记录实取颜色与像素数；02_substrate_mapping.json记录底泥压暗压平；03_authored_surface.json记录手工雾影／沉物区域与水色色表；build_water.py导出原生候选及检查图。

本轮没有图像生成、提示词或新逐格还原图：所有输入已经是正式原生像素，不需再还原。没有程序随机造泥纹、模糊源画、复制小水洼轮廓拼大图、添加波纹／高光点／发光。色场区域是固定手工指定，柔和过渡只选择邻近的离散水色色阶。

目检发现3×3中倒影有重复／斜向明暗节奏，已按要求停止，等待用户判断后续。完整QA在../../qc/water_texture_QA.md，来源索引manifest.json，停止报告前恢复包../../qc/backups/water_before_visual_stop.zip。
