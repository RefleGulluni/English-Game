# §4原生软泥返修

revise_native.py：只读已通过ground_base_01/02.png，使用一套注入式39→39色表，保留原生像素位置；在手工列出的不规则多边形与2–4px叶屑区域，用同色表附近色阶作低对比变化。区域边缘距离只控制选择哪个色阶，不模糊／平均原图，不生成随机纹理。外圈8px锁定为纯换色结果。

01_common_palette.json保存每对原色→新色；01_recolored_01/02_native.png是零几何改动的纯换色中间稿；02_authored_features.json记录全部手工区域／强弱，02_authored_shade_mask_*.png仅为过程可视化；03_revision_metrics.json记录局部改动比例及数值。

build_review.py只读取当前素材，导出原生随机混铺、半屏同位置新旧对照、物件／苔藓／积水对照与接边检查，不做游戏调色。完整关系见manifest.json；已通过素材保护哈希见protected_approved_assets.json。两脚本重跑后须重新目检和更新手写QA，构建默认只记录pending状态。

没有图像生成、素材重新取样、抗锯齿、随机噪点、世界位置明暗或运行时修改。新旧素材不要求互相接边，01／02新素材之间必须接边。
