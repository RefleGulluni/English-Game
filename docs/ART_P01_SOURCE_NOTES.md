# P01 — 源文件、授权与存储记录

## 素材来源

图像：OpenAI内置image_gen，依据用户Visual Bible和已通过的Round02概念主动引用制作。原始文件、完整提示词与布局参考在art_source/production/broken_graveyard_p01/raw/。精确生成模型版本和seed未提供，不承诺逐像素重现。没有引入其他作者的图片参考，也没有从概念大图切出最终场景。

音效：本批9个WAV均由本项目保存的build_audio.py原创合成，确定性种子9019；无第三方采样。属于可试听的合成Foley/Resonance草稿，不冒充真实骨骼/金属录音。

字体：Cormorant Garamond，来自Google Fonts官方仓库：https://github.com/google/fonts/tree/main/ofl/cormorantgaramond 。版权信息为Cormorant Project Authors。SIL Open Font License1.1原文完整保存在art/ui/fonts/OFL.txt；授权文件保留原始格式。

AI生成素材的对外使用应按适用账户条款复核，不以“AI生成”推断独占权。本轮没有推送GitHub或对外发布；没有把未知来源的商业素材混入包中。

## 可编辑源与运行导出

- editable/skeleton_standing.ora：20个独立部件层。
- editable/skeleton_remains.ora：20个同源部件层。
- editable/broken_graveyard_layers.ora：45个对象/地面层，按前/中/后景分组；雾仍是外部可编辑Shader，未烘入ORA地面。
- skeleton_pose_manifest.json：每个部件的两套局部变换、运行贴图路径。动画实现仍在art/enemies/skeleton_cutout.gd，不以合成GIF作为动画源。
- environment_layout.json与build_environment.py：逻辑世界尺寸、模块摆放、可复用节点与遮挡策略。
- art/ui/word_sigil.gd、art/characters/lexicon_clasp.gd、art/environments/fog.gdshader与art/vfx/cemetery_effect.gd：可编辑的状态/几何/响应/雾/VFX来源。
- 原始图、独立crop源、运行透明PNG同时保留。PNG输出不替代这些分层、变换和代码源。

以上相对生产目录的文件位于art_source/production/broken_graveyard_p01/。source_manifest.json保存运行文件sha256与来源链；qc/package_validation.json记录透明与分层包验证。

## 存储评估与清理

本批最大单文件为墓园OpenRaster，约9.6MB（9.2MiB）；音效为短单声道WAV，未引入大型PSD/长音频/视频。此次保持现有Git存储规则，没有擅自安装LFS或更改整个仓库的.gitattributes。后续源文件规模增加时，再由双方协商LFS。

.godot/继续忽略；必要的源.import配置和.gd/.gdshader的.uid随资源保存。art_source/.gdignore只阻止Godot导入制作源，不阻止Git归档。

processed/重复副本和可重建逐帧截图已移入Trash；原始源图、透明导出、分层源、审阅截图/GIF和验证记录保留。未清理或改动用户原始文档与程序组目录。

## Git记录

- 4175f70：本轮前已通过的Round02。
- 7b08127：将程序组c202492引入独立美术分支的接入基线。
- 0943629：透明骨件、可复用纹理、分层源与处理源码。
- 运行场景与表现适配、审阅报告分别另行提交；最终提交号见本轮交付消息。

回退到保留M01程序依赖的无本批美术状态：按顺序revert本批美术提交，目标7b08127。原始状态还有backup/art-before-production-prep-4175f70分支与仓库外pre-production-c202492备份，不对共享分支执行破坏性reset。
