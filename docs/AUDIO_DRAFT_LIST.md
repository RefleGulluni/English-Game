# Broken Graveyard — Audio Draft List

本批为原创合成的声音草稿，可在Godot审阅页Audio Drafts中逐个试听。它们不是实录Foley，也未完成人工听审；通过后再调整音色、空间和混音。所有声音保留源码，未引入第三方采样。

| 候选 | 文件 | 秒 | 峰值dBFS | 接入/用途 |
| --- | --- | --- | --- | --- |
| Bone scatter | [bone_scatter.wav](../audio/enemies/bone_scatter.wav) | 0.85 | -13.3 | 独立候选；collapse已包含散落，避免重复叠加 |
| Skeleton collapse | [skeleton_collapse.wav](../audio/enemies/skeleton_collapse.wav) | 1.10 | -11.06 | enemy_collapsed |
| Bone reassembly tension | [bone_reassembly_tension.wav](../audio/enemies/bone_reassembly_tension.wav) | 0.95 | -21.22 | enemy_reassembled |
| Echo absorb | [echo_absorb.wav](../audio/loot/echo_absorb.wav) | 0.66 | -18.77 | Echo视觉飞行收束时播放 |
| Special Loot clink | [special_loot_clink.wav](../audio/loot/special_loot_clink.wav) | 0.58 | -19.69 | special_loot_spawned |
| Pickup | [pickup.wav](../audio/loot/pickup.wav) | 0.35 | -23.52 | loot_picked_up |
| OBSERVE invoke | [observe_invoke.wav](../audio/words/observe_invoke.wav) | 0.55 | -23.25 | word_sigil_invoked，word_id=OBSERVE |
| SHATTER invoke | [shatter_invoke.wav](../audio/words/shatter_invoke.wav) | 0.65 | -15.17 | word_sigil_invoked，word_id=SHATTER |
| ERODE invoke | [erode_invoke.wav](../audio/words/erode_invoke.wav) | 0.85 | -17.85 | word_sigil_invoked，word_id=ERODE |

导入：48kHz、16bit、mono PCM，无循环；音量保守，最大峰值约-11dBFS。Audio Bus使用契约SFX，缺失时回Master。本轮不改project.godot或新建共享Audio Bus规则。

合成源：art_source/production/broken_graveyard_p01/tools/build_audio.py；确定性随机种子9019。骨头/铁钉以短暂不规则接触表现，Echo为空气收束，Word分别表现对焦、断裂和磨蚀。没有上行奖励音阶、金币叮当、史诗冲击或持续音乐。

试听需检查：骨声是否过于合成、clink是否能被环境听见但不刺耳、Echo是否像回响而非奖励、三词是否有不同触感。尚未在不同耳机/音箱上完成可听性验收。
