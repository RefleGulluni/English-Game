from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,re,subprocess,sys
W=Path('/tmp/english-game-skeleton-v5-20261027');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';O=W/'staged';Q=O/'qc';V=Q/'v5_sources';tim=json.loads((W/'new_timing.json').read_text());rec=json.loads((W/'walk_records.json').read_text());met=json.loads((Q/'skeleton_B_anim_v5_metrics.json').read_text());vf=json.loads((Q/'skeleton_B_anim_v5_verification.json').read_text());locks=json.loads((Q/'skeleton_B_walk_right_v5_lock.json').read_text());protected=json.loads((W/'protected.json').read_text());master=np.array(Image.open(S/'skeleton_B_right.png').convert('RGBA'));refs=json.loads((W/'foot_reference.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rh(a):return hashlib.sha256(a.tobytes()).hexdigest()
# Verify the complete planted sole, not just the tracked toe.
for k,r in enumerate(locks):
 role=r['support_anatomical_leg'];name='near_right_leg' if role=='right' else 'far_left_leg_shroud';src=np.array(Image.open(V/'standing_parts'/(name+'.png')));base=refs[role];sy=base['bottom'];xs=np.where(src[sy,:,3]>0)[0]
 if role=='left':xs=xs[(xs>=48)&(xs<76)]
 dx=r['local'][0]-base['toe'];actual=xs+dx;a=np.array(Image.open(O/'frames/skeleton_B_walk_right_v5'/f'{k+1:02}.png'));assert all(a[95,x,3]==255 for x in actual);r['entire_actual_sole_x']=actual.tolist();r['entire_world_sole_x']=(actual+5*k).tolist();r['whole_sole_opaque']=True
(Q/'skeleton_B_walk_right_v5_lock.json').write_text(json.dumps(locks,indent=2))
# Actual hand landmark in the pose, distinct from the pre-draw target.
for n,rs in rec.items():
 for rr in rs:
  if rr.get('exact_standard'):rr.update({'near_hand_landmark':[33,55],'pelvis_offset':[0,0],'chest_offset':[0,0],'head_offset':[0,0]});continue
  blend=rr.get('arm_pose_blend',1);sx=round((7+rr.get('near_arm_swing',0))*blend);rr['near_hand_landmark']=[33+rr['chest_offset'][0]+sx,55];rr['far_hand_visibility']='occluded; target only, no invented visible hand'
(W/'walk_records.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));shutil.copy2(W/'walk_records.json',V/'walk_records.json')
md=['# 骷髅 B · §17 右侧重画试样 / V5 QA','', '**本次只交右侧行走、起步、停步和正面重组提布，其他三个方向未开工。** 4 条动画 / 56 帧，旧版本全部保留。','', '## 结果与未达项','', '- 行走没有读取旧行走 PNG 或旧帧；唯一角色画面输入是 `skeleton_B_right.png`。所有姿势从该标准图的同一组源像素重新组织成完整帧。','- 胸廓连胸前布、头骨、骨盆的原像素完全锁定。撤销整数位移后，8×3 个底稿层 RGBA 均与标准源层完全相同；没有重画肋骨或逐帧换色。','- 起步首帧、停步末帧与标准图 RGBA 相同。两腿身份和宽破布归属固定，支撑脚每帧后退 5 px，实际脚底已核对。','- **“相邻约 1000 像素”未全部达到。** 起步 / 停步及其边界均在 1000 内；循环内部为 808～1304，闭环为 894。重组提布有 3 次超出，最大 1327。实际值逐项列出，不把它们写成全部达标。','- **旧的固定画布四段灰度 ±2 未全部达到。** 本轮按 §17 不改刚性部件颜色；三个刚性源块自身灰度差为 0，完整人物平均灰度差不超过约 ±1.23。因姿势和遮挡跨分段边界，固定 y 分段仍有较大差值，完整表保留在后面。没有给肋骨重新着色来追均值。','', '## 文件','', '| 动画 | 帧数 | 尺寸 | ms |','|---|---:|---|---:|']
for n,t in tim.items():md.append(f'| `{n}` | {t["frames"]} | {t["frames"]*96}×96 | {sum(t["durations_ms"])} |')
md+=['','每帧 96×96，锚点 (48,96)，全部帧最低不透明行 y95，alpha 仅 0/255。PNG、原生逐帧图、8 倍 nearest GIF、剪影叠图、刚性胸廓对照、腿归属图和源表均已交付。','', '## 动笔前零件表与最终节拍','', '动笔前已保存 [原始计划表](v5_sources/parts_plan_before_drawing.md) 和 [JSON](v5_sources/parts_plan_before_drawing.json)。它们保留制作前方案；第一轮检查后发现所有部件仍在每帧同时动，最终改为骨盆 2 px 的落地 / 经过节拍，胸廓晚 1 帧、头晚 2 帧，各有 1 px 的减幅响应。下表是**实际交付坐标**，不是拿原始计划冒充实测。','', '右侧视角：**近侧是角色右腿（裸骨），远侧是左腿（宽破布与左胫）。** 下表“步幅在前”指向画面右侧迈得更前；“遮挡在前”始终是近侧右腿。这两件事不同，腿在步幅上交叉时不交换材质。','', '| 帧 | 步幅领先 | 支撑 | 遮挡前层 | 宽破布 | 右脚尖 x / 抬高 | 左脚尖 x / 抬高 | 骨盆 dx,dy | 胸 dx,dy | 头 dx,dy | 右手指节定位 | 左手（遮住的目标位置） |','|---|---|---|---|---|---|---|---|---|---|---|---|']
for r in rec['skeleton_B_walk_right_v5']:
 md.append(f'| {r["frame"]} | {r["stride_lead"]} | {r["support"]} | 右腿 | 左胫 | {r["near_toe_x"]} / {r["near_lift"]} | {r["far_toe_x"]} / {r["far_lift"]} | {r["pelvis_offset"]} | {r["chest_offset"]} | {r["head_offset"]} | {r["near_hand_landmark"]} | {r["far_hand_target"]} |')
md+=['','手的定位像素取原图指节 (33,55)，不是不明确的包围盒中心。近侧右手在骨盆旁，以垂下为中心前后约 2 px；肩跟胸廓，手端有悬挂的竖直阻尼。远侧左手被布和躯干遮住，表内只是骨链目标，不把不可见处补画成另一只可见手。','', '骨盆上下跨度 2 px；胸 / 头的位移信号分别是骨盆前 1 / 前 2 帧的减幅状态。右腿抬高最多 4 px、左腿最多 3 px，左脚更低、更像拖行。手臂没有在 y44 与任何旧帧拼接；源骨链按肩、肘、前臂和手的连贯位置整理。','', '起步 / 停步中间姿势同样从标准图重新绘制，并非任意挑两张端点图的像素混合。起步先提骨盆，再向前送右腿；停步从第 8 帧开始收腿、落稳，再回到标准。它们的边界没有重复静止端点帧：起步最后一帧与循环第 1 帧变化 430；循环第 8 帧到停步首帧变化 346。','', '### 起步、停步实际零件表','', '| 动画 / 帧 | 右脚尖 x / 抬高 | 左脚尖 x / 抬高 | 骨盆 | 胸 | 头 | 右手定位 |','|---|---|---|---|---|---|---|']
for n in ['skeleton_B_walk_start_right','skeleton_B_walk_stop_right']:
 for k,r in enumerate(rec[n]):
  static=r.get('exact_standard',False);nt=46 if static else r['near_toe_x'];ft=66 if static else r['far_toe_x'];nl=0 if static else r['near_lift'];fl=2 if static else r['far_lift'];md.append(f'| {"start" if "start" in n else "stop"} / {k+1} | {nt} / {nl} | {ft} / {fl} | {r["pelvis_offset"]} | {r["chest_offset"]} | {r["head_offset"]} | {r["near_hand_landmark"]} |')
md+=['','站姿的远脚最低 y93，因此此表以共同 y95 参考面记作抬高 2；起步首帧与停步末帧仍是原图，未为了这张表移动标准图的远脚。','', '## 胸廓不闪：源像素证明','', '| 刚性块 | 原生不透明像素数 | 源层 RGBA SHA256 | 8 帧撤销位移后的差异 |','|---|---:|---|---:|']
for n in ['thorax','head','pelvis']:
 p=np.array(Image.open(V/'standing_parts'/(n+'.png')));md.append(f'| {n} | {int((p[:,:,3]>0).sum())} | `{rh(p)}` | 0 |')
md+=['','[逐帧 24 个刚性层验证](v5_sources/rigid_part_verification.json) · [标准图 / 八帧胸廓 8 倍](skeleton_B_right_v5_fixed_thorax_8x.png)。','', '核对先把底稿层撤销位移，再比较完整 96×96 RGBA；不是只看颜色数或灰度。胸前布、露出的肋骨、肩钉与缝线都在同一个固定胸廓源层里。合成时会有手臂、头颈和衣料的正常遮挡，但被遮住的底稿没有换图。实际可见且归属胸廓的像素也逐点与源图核对。','', '腰绳和关节是柔性连接，直接采用标准图相邻的原生像素，不把任何旧帧的上半身 / 下半身贴进来。骨段投影按原生行重排，不做整图缩放、旋转或平滑。','', '## 布始终属于同一条腿','', '宽破布、破洞和下摆属于左胫，跟着远侧左腿的投影走；包住小腿和脚踝的部分用当前左腿位置，只有松开的边缘晚半拍。近侧右腿始终在前面遮挡它，交叉时不会把左腿的宽布复制到右脚。标准图原有的细踝部绑带 / 污色另随原部位保留，不当作左胫宽破布迁移。','', '[腿归属可视图](skeleton_B_right_v5_leg_ownership_4x.png)：赭色 = 左腿及其布，绿色 = 右腿。图中标色只用于 QA，不是游戏素材的新颜色。原始源层和逐帧归属见 `v5_sources/standing_parts/`、`v5_sources/walk_layers/`。','', '## 锁脚与相邻帧变化','', '| 帧 | 支撑腿 | 画布脚尖 | 世界位移 | 地面脚尖 |','|---|---|---|---|---|']
for r in locks:md.append(f'| {r["frame"]} | {r["support_anatomical_leg"]} | {r["local"]} | {r["world_translation"]} | {r["world"]} |')
md+=['','每段着地期内地面参考点恒定。整条实际着地脚底也核对为不透明，见 [锁脚 JSON](skeleton_B_walk_right_v5_lock.json)。','', '| 动画 / 相邻帧 | RGBA 改变像素数 |','|---|---:|']
for n in ['skeleton_B_walk_start_right','skeleton_B_walk_right_v5','skeleton_B_walk_stop_right']:
 for k,x in enumerate(vf[n]['consecutive_changed_pixels']):md.append(f'| {n} / {k+1}→{k+2} | {x} |')
for label,x in vf['boundaries'].items():md.append(f'| {label} | {x} |')
md+=['','计数包括颜色、透明变不透明等任一 RGBA 通道变化。循环部分仍高于约 1000 的目标；没有通过删细节、抹平骨纹、改刚性块颜色或像素交替混合来降低它。主循环的最大 1304 与“视觉一定自然”不是同一判断，需在游戏里验收。','', '每一张行走 / 起步 / 停步与站姿的剪影叠图：[14 帧剪影](skeleton_B_right_v5_silhouette_overlays_4x.png)。灰绿为重合、红褐为新轮廓、土黄为原站姿轮廓。','', '## §16.1 六帧拉起裹尸布','', '重组仍为 **42 帧 / 4880 ms**。F13～18 每帧 100 ms，共 600 ms：','', '| 帧 | 提布状态 |','|---|---|','| 13 | 腰绳端的一角离地，布的大部分仍在地上 |','| 14 | 斜向拖起，尾部仍铺在地上 |','| 15 | 部分搭上骨盆与肋骨，胸上端仍裸露 |','| 16 | 上缘继续爬向胸口，尾部最后拖着走 |','| 17 | 主体接近胸口，下摆尚未完全垂稳 |','| 18 | 下摆离地，整片斜布垂下；挂钉留到后段扯正 |','', '[六状态 4 倍](skeleton_B_reassemble_front_v5_cloth_six_4x.png)。上提部分取 B 正面原布的原生像素，地面部分从原骨堆那片斜布逐段收走，不另换成长裙。原图被衣料遮住的骨面没有完整底稿，因此用 B 前 / 背面已经露出的骨面像素补出临时底层，只在本次新露出的区域显示；没有换成另一具宽体骨架。','', 'F19～23 清理旧的地面整片布，避免已经上身后又留着第二整片；原有骨片保留。F1～12 与 F24～42 与 V4 RGBA 相同，黑线拖、吊、收头骨与最后回正均保留。','', '提布相邻变化超过 1000 的实际项目：','', '| 相邻帧 | 变化像素数 |','|---|---:|']
for r in vf['skeleton_B_reassemble_front_v5']['transitions_over1000']:md.append(f'| {r["from"]}→{r["to"]} | {r["changed_pixels"]} |')
md+=['','这些仍是未达目标的拍点，未标为通过。源布、补出的骨面和每帧仍在地面 / 已提起的层保存在 `v5_sources/front_shroud_source.png`、`front_under_shroud_ribs.png`、`reassembly_cloth_layers/`。','', '## 像素、颜色和明暗','', '所有 56 帧 alpha 仅 0/255，颜色都属于既有 48 色；无饱和青蓝、光晕、投影或闪白。行走三条每帧都是标准右侧的 46 色，所有像素直接来自该标准图，未对刚性块或四肢做逐帧调色。','', '| 动画 | 每帧颜色数 | 水平相邻换色比例 |','|---|---:|---:|']
for n,ms in met.items():md.append(f'| `{n}` | {min(r["colors"] for r in ms)}～{max(r["colors"] for r in ms)} | {min(r["horizontal_change_percent"] for r in ms):.2f}%～{max(r["horizontal_change_percent"] for r in ms):.2f}% |')
md+=['','### 固定画布四段灰度（如实保留旧口径）','', '只算不透明像素，Y=0.299R+0.587G+0.114B。头 y0～19、胸 y20～44、腰 y45～64、腿 y65～95。下表是相对站姿的差值；并未全部在 ±2 内。部件在跨固定段边界时，分段的材质占比会变，不能把它等同于该部件被重新着色。每个刚性源块自身灰度差为 0，完整人物平均差在约 ±1.23 内。','', '| 动画 / 帧 | 头 Δ | 胸 Δ | 腰 Δ | 腿 Δ | 整人 Δ |','|---|---:|---:|---:|---:|---:|']
for n,ms in met.items():
 if 'reassemble' in n:continue
 for k,r in enumerate(ms):md.append('| '+n.replace('skeleton_B_','')+f' / {k+1} | '+' | '.join(f'{b["difference"]:+.2f}' for b in r['bands'])+f' | {r["whole_gray_difference"]:+.2f} |')
md+=['','本轮依 §17 保留相同源像素，没有为了旧固定画布统计而改肋骨、头骨、骨盆原色。旧分段目标和新锁像素要求之间的未完全兼容项，留给游戏验收判断，不能声称全部规格自动通过。','', '## 首尾哈希与原件保护','', '哈希为 96×96 解码 RGBA 字节 SHA256；逐帧数据见 metrics。','', '| 动画 | 首帧 RGBA SHA256 | 末帧 RGBA SHA256 |','|---|---|---|']
for n,ms in met.items():md.append(f'| `{n}` | `{ms[0]["rgba_sha256"]}` | `{ms[-1]["rgba_sha256"]}` |')
md+=['',f'右侧标准图 RGBA SHA256：`{rh(master)}`。起步首帧、停步末帧已逐像素确认与它相同；原 PNG 文件哈希前后同为 `{sha(S/"skeleton_B_right.png")}`。重组首尾继续等于原骨堆和原正面图。','',f'开工记录 {len(protected)} 个既有文件的哈希，发布前全部相同。发布只备份并追加 `anim/timing.json`，不覆盖旧动画、标准图、旧 QA；备份位置 `qc/backups/before_v5_20261027/timing.json`。旧 36 条动画条目保留。','', '[metrics](skeleton_B_anim_v5_metrics.json) · [验证结果](skeleton_B_anim_v5_verification.json) · [pixel_check 数字](skeleton_B_anim_v5_pixel_check.txt)。全部 GIF 已重解码核对像素、透明度、帧数和时长。','', '本轮没有新增其他三个方向，没有改 Godot 组装。请重点验收：起停是否顺、手是否自然垂在骨盆旁、肋骨是否稳定、交叉后宽布是否仍属于左胫、六帧提布是否像同一片布被拉上去。完成后停止等待验收。']
(Q/'skeleton_B_anim_v5_QA.md').write_text('\n'.join(md)+'\n')
idx=['# 骷髅 B · §17 右侧重画试样','', '[起步 → 两圈行走 → 停步 8 倍演示](skeleton_B_right_v5_start_walk_stop_8x.gif)','', '| 动画 | PNG | 8 倍 GIF | 逐帧总图 | 原生帧 |','|---|---|---|---|---|']
for n in tim:idx.append(f'| `{n}` | [PNG](../{n}.png) | [GIF]({n}_8x.gif) | [总图]({n}_{"3x" if "reassemble" in n else "4x"}.png) | [frames](../frames/{n}/) |')
idx+=['','[QA / 最终零件表](skeleton_B_anim_v5_QA.md) · [动笔前表](v5_sources/parts_plan_before_drawing.md) · [剪影叠图](skeleton_B_right_v5_silhouette_overlays_4x.png) · [胸廓固定像素](skeleton_B_right_v5_fixed_thorax_8x.png) · [腿和布归属](skeleton_B_right_v5_leg_ownership_4x.png) · [六帧提布](skeleton_B_reassemble_front_v5_cloth_six_4x.png)','', '**未达项**：部分循环 / 提布帧差仍超过约 1000，旧固定画布分段灰度未全部在 ±2 内；数值与原因见 QA。刚性部件没有改色或重画肋骨。','', '只交右侧试样和重组提布，等待游戏验收。'];(Q/'skeleton_B_anim_v5_index.md').write_text('\n'.join(idx)+'\n');shutil.copy2(W/'report_publish.py',V/'production/report_publish.py')
assert all(Path(p).exists() and sha(p)==h for p,h in protected.items());files=[p for p in O.rglob('*') if p.is_file()];assert all(not (A/p.relative_to(O)).exists() for p in files)
old=json.loads((A/'timing.json').read_text());assert len(old['animations'])==36 and not set(old['animations'])&set(tim);backup=A/'qc/backups/before_v5_20261027/timing.json';assert not backup.exists();backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(A/'timing.json',backup);merged=json.loads(json.dumps(old))
for n,t in tim.items():
 if n=='skeleton_B_walk_right_v5':entry=old['animations']['skeleton_B_walk_right_v4'].copy();entry.update(t);entry['movement_px_per_second']=50
 elif n=='skeleton_B_reassemble_front_v5':entry=old['animations']['skeleton_B_reassemble_front_v4'].copy();entry.update(t)
 else:entry=t.copy();entry['hold_last_frame']=True
 merged['animations'][n]=entry
for p in files:dest=A/p.relative_to(O);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(A/'timing.json').write_text(json.dumps(merged,ensure_ascii=False,indent=2)+'\n');assert len(merged['animations'])==40 and all(merged['animations'][n]==t for n,t in old['animations'].items());assert sha(backup)==protected[str(A/'timing.json')];assert [p for p,h in protected.items() if sha(p)!=h]==[str(A/'timing.json')]
p=A/'qc/skeleton_B_anim_v5_verification.json';v=json.loads(p.read_text());v['publication']={'new_actions':4,'new_frames':56,'only_existing_file_modified':'anim/timing.json','backup_matches_original':True,'all_old36_animation_entries_unchanged':True,'all_other_prior_files_unchanged':True};p.write_text(json.dumps(v,indent=2))
paths=sorted(p for n in tim for p in (A/'frames'/n).glob('*.png'));z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1.png'),*map(str,paths)],capture_output=True,text=True);assert z.returncode==0;(A/'qc/skeleton_B_anim_v5_pixel_check.txt').write_text(z.stdout+z.stderr)
for f in ['skeleton_B_anim_v5_index.md','skeleton_B_anim_v5_QA.md']:
 p=A/'qc'/f
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):assert (p.parent/link).exists(),link
manifest={str(p.relative_to(A)):sha(p) for p in A.rglob('*') if p.is_file() and ('_v5' in str(p.relative_to(A)) or 'v5_sources' in str(p.relative_to(A)) or p.name in ['skeleton_B_walk_start_right.png','skeleton_B_walk_stop_right.png']) and not p.name.endswith('_manifest.json')};(A/'qc/skeleton_B_anim_v5_manifest.json').write_text(json.dumps(manifest,indent=2));print('PUBLISHED',len(files),'new files; 4 actions / 56 frames; old files preserved; quantitative exceptions explicitly documented.')
