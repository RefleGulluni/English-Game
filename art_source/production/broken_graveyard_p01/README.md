# Broken Graveyard P01

正式交付说明：[ART_BROKEN_GRAVEYARD_P01.md](../../../docs/ART_BROKEN_GRAVEYARD_P01.md)。

- raw/：8份内置image_gen原始图、完整实际提示词、布局参考、完整物件裁切；没有把已验收场景概念图裁切当运行地图。
- editable/：Skeleton站立、骨堆与墓园分层的3份OpenRaster；源PNG继续保留。
- reviews/：实际Godot截图/GIF、Chisel尺度、九状态、实机通关截图。
- qc/：裁切、alpha、引入/运行/接口验证记录；initial/rejected日志明确是已修正的历史过程。
- tools/：裁切/透明清理、可编辑分层打包、环境布局序列化、原创音效合成源码。
- skeleton_pose_manifest.json：20部件站立/骨堆变换、贴图路径；单位为逻辑像素，rad旋转，Actor接触Root不动。
- environment_layout.json：各独立模块的位置、尺寸、图层与遮挡策略，不改碰撞。
- audio_manifest.json：9个候选WAV时长、峰值和来源说明。
- source_manifest.json：源参考、文件清单、sha256及许可记录。

美术运行资源放在art/与audio/。本目录由art_source/.gdignore排除Godot导入，仍由Git追踪。processed/和逐帧截图等可重建临时工作目录在验证后移至Trash，不删除原始生成图、运行PNG或分层源。

图像使用内置image_gen生成；精确模型版本/seed未提供。模块/骨件来自主动引用的已验收Round02图；原图透明处理使用generate2dsprite技能处理器。Sigil/雾/响应是可编辑Godot几何与Shader，不是预烘焙大图。
