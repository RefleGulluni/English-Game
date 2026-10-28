from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil,copy
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-combat-step2-20261028');D=W/'delivery';HA=R/'art/character_design/anim';SA=R/'art/character_design/enemies/skeleton/anim';J=json.loads((W/'results.json').read_text());P=json.loads((W/'parts_plan_before_compositing.json').read_text());poses=json.loads((W/'pose_records.json').read_text());entries=json.loads((W/'timing_entries.json').read_text());protected=json.loads((W/'protected.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert all(Path(p).exists() and sha(p)==h for p,h in protected.items()),'Existing artwork changed during production; stop before publication'
oldattack=SA/'skeleton_B_attack_right.png';oldsha=sha(oldattack)
# Archive generated sources and native extraction records under the new batch, not the old trial folder.
for kind,names in [('hero',['cast_left','hit_left','hit_right']),('skeleton',['attack_left','attack_right_v2','dust_left','dust_right'])]:
 q=D/kind/'qc';src=q/'combat_step2_sources';src.mkdir(parents=True,exist_ok=True)
 for name in names:
  dest=src/'generation'/name;dest.mkdir(parents=True,exist_ok=True)
  for suffix in ['_generated.png','_prompt.txt','_restored.png','_grid.json','_gridcheck.png','_ref8x.png','_anchor4x.png']:
   if (W/(name+suffix)).exists():shutil.copy2(W/(name+suffix),dest/(name+suffix))
 if kind=='skeleton':
  for tag in ['short_high','short_mid']:
   dest=src/'generation'/tag;dest.mkdir(parents=True,exist_ok=True)
   for suffix in ['_generated.png','_prompt.txt','_restored.png','_grid.json']:
    shutil.copy2(W/(tag+suffix),dest/(tag+suffix))
  for name in ['short_cut_contact8x.png','recover_high.py','recover_mid.py']:shutil.copy2(W/name,src/name)
 for name in ['generation.json','parts_plan_before_compositing.json','pose_records.json','tone_records.json','results.json','protected.json','recover.py','boundary_defs.txt','build.py','tone.py','export_verify.py','publish.py']:
  shutil.copy2(W/name,src/name)
 (src/'generation_manifest.json').write_text(json.dumps({'tool':'built-in image_gen (no CLI fallback)','actions':names,'selected_pixels':{'cast_left':'pose arms2/3/4/6 + approved left standing body','hit_left':'generated pose study only; final pixels all from left standing, lamp positions in raw study rejected','hit_right':'generated pose study only; final pixels all from right standing','attack_left':'far right arm poses3/4/5/6/7 + left standing body; no mirroring','dust_left':'native small ash fragments from generated frame3/4, body from matching standard','dust_right':'native small ash fragments from generated frame3/4, body from matching standard','attack_right_v2':'only frame5 uses short_mid source arm; frame6 uses four-pose source frame3; frames1–4,7–9 byte-copied from accepted attack'},'unused_studies':['short_high (overhead pose rejected)','attack_right_v2 original four-pose source frame2 (insufficient downward arc)'],'no_art_resizing_rotation_mirror':True,'status':'step2_pending_user_review'},indent=2))
# QC-only forearm anatomy comparison.
import numpy as np
ref=Image.open(R/'art/character_design/enemies/skeleton/skeleton_B_right.png').convert('RGBA');b=Image.new('RGBA',(3*112,112),'#403d43');dr=ImageDraw.Draw(b);b.alpha_composite(ref,(8,12));dr.line((40,46,40,59),fill='#aaaaaa');dr.text((2,1),'Stand: 13px',fill='white')
for i,k in enumerate([5,6]):
 im=Image.open(D/f'skeleton/frames/skeleton_B_attack_right_v2/{k:02}.png').convert('RGBA');b.alpha_composite(im.crop((48,0,144,96)),((i+1)*112+8,12));rr=poses['skeleton_B_attack_right_v2'][i];el=rr['elbow_marker'];tip=rr['tip'];xoff=(i+1)*112+8-48;dr.line((el[0]+xoff,el[1]+12,tip[0]+xoff,tip[1]+12),fill='#aaaaaa');dr.text(((i+1)*112+2,1),f'F{k}: {rr["forearm_projected_length"]:.2f}px',fill='white')
b.resize((b.width*8,b.height*8),Image.Resampling.NEAREST).save(D/'skeleton/qc/skeleton_B_attack_right_v2_forearm_compare_8x.png')

md=['# 战斗动画第2步 QA · 七条交付','', '2026-10-28。依据 COMBAT_ANIMATION_REQUEST.md §11；第1步主角右侧施法、骷髅右侧攻击已由用户通过，本轮保留其原文件。状态：文件自查完成，等待游戏内验收。','', '## 文件和时机','', '|动画|帧格 / 横条|帧数|时长|关键帧（1基 / 0基 / 开始时间）|','|---|---|---:|---:|---|']
for n,r in J.items():
 t=r['timing'];fw=t['frame_size'][0];kf=t['key_frame'];md.append(f'|{n}|{fw}×96 / {fw*t["frames"]}×96|{t["frames"]}|{t["duration_ms"]}ms|{kf["type"]}: {kf["frame"]} / {kf["frame_index"]} / {kf["time_ms"]}ms|')
md+=['', '全部不循环。施法、受击、抖灰锚点(48,96)；攻击锚点(80,96)。timing.json 每条均明确 frame_size、anchor、逐帧 durations_ms；frame字段为1基、frame_index为0基，不可混用。骷髅攻击以各条160×96覆盖顶层96×96默认值。','',
'主角左施法沿用右侧的90/100/100/120/100/90/80/80ms，第4帧290ms出词。近侧左手抬掌，远侧右手提灯，近侧左髋仍挂包；没有镜像、换手或添加青蓝印记。',
'两条主角受击为40/70/130/100ms。第1帧按通用合同保持站姿且触发hit；40ms后腰部先退2px，第3帧头颈肩跟上2px、腰部回1px，末帧回到标准。方向以敌人在面前为准：朝左则往右缩，朝右则往左缩。握灯的完整手臂单独与肩部同移，提手始终在手指下方；灯底比手晚拍摆1px，未让握灯手跟着腰部错位。',
'骷髅左攻击沿用右侧9帧、1010ms、第5帧520ms命中。远侧右臂从胸前伸出、近侧左臂保持垂下；右肩的布与钉子、左胫的裹布按左侧站姿保留，未镜像右侧。骨盆先向身后坐，上身随后，收回的布边晚一拍。',
'抖灰两方向均6帧700ms，100/80/100/140/180/100ms，第2帧开始抖落。骨盆先被扯1px，完整头颈胸晚一帧跟上、上下同移；三簇深褐骨灰从肩/肋缝/布褶下落，到脚边消失。颗粒取自独立生成稿的原生小灰块，局部裁选≤3×3的碎片，未随机撒点或绘制烟云。颗粒避开原脚像素。它们是本条抖灰中的附着落尘，**没有提前做第3步独立fx素材**。','',
'## 右侧攻击对比版','',
'`skeleton_B_attack_right_v2.png` 与原版同为9帧、同一时长表。**只有第5、6帧不同**；第1～4、7～9帧的独立PNG文件直接复制原版，文件SHA和RGBA都相同。原 `skeleton_B_attack_right.png`、原逐帧图、原GIF和原timing条目不改。',
'第5帧采用重新生成的高位切入短臂，第6帧向前下方落下；两帧尖端从(91,31)移到(96,45)，下降14px，骨尖路径为斜向下划，未画运动弧线、速度线或拖影。肩/肘有清楚弯折，没有握长矛的手或额外武器。蓄力、收回均原样保留。',
'站姿前臂参考：肘标记(32,34)→腕/断口末端(32,47)，13px。新第5帧肘(82,23)→尖(91,31)投影长度12.04px；第6帧肘(84,37)→尖(96,45)投影长度14.42px。离散角度、前后压缩和1～2px尖茬会改变端点投影，但没有把骨干拉长成原版的长骨刃。未删斜骨段的行列，也没有旋转位图来凑角度。源图与带标记对比见 `skeleton_B_attack_right_v2_forearm_compare_8x.png`。','',
'命中帧位置（相对脚底锚点）：',
'- 左侧攻击：尖(14,23)，偏移 **(-66,-73)**；按原版40px程序前进。',
'- 右侧短臂对比：第5帧尖(91,31)，偏移 **(+11,-65)**；第6帧尖(96,45)，偏移 **(+16,-51)**。timing新条目记录程序前进参考范围60～80px。',
'- **短臂的实际水平伸距明显小于原版65px。** 以第5帧+11计算，整体前移60～80后，骨尖只到原站点前方71～91px。不能据此宣称一定碰到中心相隔120px的主角；需要在游戏内结合双方前侧轮廓、斜向高低差与命中判定核对。本轮未擅改前冲距离、命中帧或站位。','',
'## 像素、配色、连接与脚','',
'46个帧图全部Alpha仅0/255；无新增颜色、饱和青蓝、发光、符文、白闪、投影、拖影。主角颜色来自四张现行标准图；骷髅来自已有48色。骨头、皮肤、衣服的生成色都归并到该角色既有材质色；只整理新手臂的明暗，没给头脸做整张调色。',
'每帧以对应站姿的完整像素组为基础重建，不读取旧行走作为下半身。头、颈、胸的原像素组统一移动；有手臂遮住胸口的自然遮挡，不重新画肋骨。所有源颈像素的目标位置逐帧均保持不透明；除有意分离的骨灰碎片外，人物各帧都是一个8邻域连通件。',
'主角原图y78～95、骷髅原图y84～95的不透明脚像素逐帧RGBA均相同，最低像素均y95；骨灰不会覆盖靴或趾骨。动作站定不使用行走每帧后退5/7px的规则。腰部由原像素的连续布褶/腰绳连接，没有一整行透明接缝。',
'全部7条GIF均已解码核对：帧数、原生8倍不透明RGBA、透明遮罩、逐帧时长都与PNG/timing相符；GIF没有另补停顿或改变节奏。','',
'## 首尾与标准图 SHA256','',
'RGBA哈希包含透明像素；PNG文件SHA是压缩后的文件字节哈希。攻击160×96先将96×96标准原样放到(32,0)后比较，其余透明。首帧、末帧均严格相等。','']
for n,r in J.items():
 assert protected[str(R/r['standard_file'])]==r['standard_png_sha256_before']
 md += [f'### {n}','',f'- 标准文件：`{r["standard_file"]}`',f'- 标准PNG文件SHA（制作前后相同）：`{r["standard_png_sha256_before"]}`',f'- 原96×96 RGBA：`{r["standard_rgba_sha256"]}`',f'- 匹配画布后的标准RGBA：`{r["padded_standard_rgba_sha256"]}`',f'- 首帧RGBA：`{r["first_frame_rgba_sha256"]}`',f'- 末帧RGBA：`{r["last_frame_rgba_sha256"]}`','']
md+=['## 分段亮度与逐帧数据','', '仅统计不透明像素，亮度=0.299R+0.587G+0.114B。下表“均值（与对应站姿差）”；四段绝对差均≤2，抖灰表也包含落灰像素。完整高光比例、颜色数、脚检查、逐帧PNG/RGBA哈希、连通件和帧差见每条 *_metrics.json；pixel_check.py 原始输出见 *_pixel_check.txt。','']
for n,r in J.items():
 md += [f'### {n}','', '|帧|头0～19|胸20～44|腰45～64|腿65～95|与前帧变化像素|','|---:|---:|---:|---:|---:|---:|']
 for f in r['frames']:md.append('|'+str(f['frame'])+'|'+'|'.join(f'{b["mean_luma"]:.2f} ({b["delta"]:+.2f})' for b in f['bands'])+f'|{f["changed_pixels_previous"]}|')
md+=['','## 零件表 / 生成记录','',
'每帧的骨盆、完整上身、两臂归属、固定脚、布所属腿、灯摆幅、颗粒源片与轨迹均记录在 `combat_step2_sources/parts_plan_before_compositing.json` 和 `pose_records.json`。零件表在最终原生合成前列好，之后将左侧上身的竖直响应减为0，仅保留横向错拍以稳定这个视角的露骨亮度；头与胸始终同步。',
'使用内置 image_gen 分别生成7条动作稿，未把不同动作塞在同一张稿里；角色稿采用多行网格。右侧短臂又尝试两张单独接触姿势：过头顶一张未采用，胸前高位一张用于第5帧。第6帧仍用四姿势稿第3格。提示词、原稿、实际块边取样表和原生恢复图均保留。未做整图非整数缩小、插值、旋转或镜像。',
'最终保留对应方向的站姿身份像素，只选用生成稿里的新手臂姿态和小灰块。受击稿仅作姿态参考（左侧稿把远侧灯画错位置，未采用）；受击最终用原站姿像素完整摆动，灯和包仍在正确侧。左侧施法时原来贴在包缘的手部少数像素，及左侧骷髅远手离开后的少数像素，用已有衣/布色补回，避免出现多一只手。没有新绘制程序纹理。','',
'## 还需要用户判断','',
'- 短臂对比版的命中伸距与原版差很多，前冲60～80px能否和具体战斗站位贴合，须实机核对；未用加长前臂或偷偷移动脚来弥补。',
'- 左侧攻击的出招臂在远侧，蓄力的一部分会被胸和近臂挡住，轮廓与右侧不会一样；是否足够有张力仍请游戏内看。',
'- 相邻帧约1000像素是行走过渡的软目标，本批若干帧超过该值（最大约1509），快挥击、1～2px肩部缩动会产生较大帧差。完整数值已列出，没有靠补拖影或缩小动作刷到阈值。',
'- 分段均值稳定不代表高光面积完全相同。攻击展开了新的浅骨面，高光面积随姿态变化；数据原样记录，头脸没有重画或闪白。抖灰颗粒刻意很小、很暗，在不同地面和环境光下的可见度须游戏内看。',
'- 没有接入Godot场景、脚本、碰撞或改程序特效；没有替用户认定通过。第3步独立碎骨/骨灰/布丝素材仍未制作。','',
'## 保护与停止点','',
'制作前记录3398个既有文件，发布前全部复核。两处timing.json各备份到 `qc/backups/before_combat_step2_20261028/timing.json` 后仅追加3条主角/4条骷髅条目；旧条目逐字段完全不变。旧标准图、旧动画、右侧原版攻击与上批QA不覆盖。为遵守“不改旧文件”，本批QA另存 `combat_step2_QA.md`，上批 `combat_anim_QA.md` 保留。','',f'原版 `skeleton_B_attack_right.png` 文件SHA256（前后相同）：`{oldsha}`。','', '本轮到此停止，等待用户在游戏内验收七条动画和右侧对比。','']
# Links are absolute so the cross-actor index works from either animation folder.
index=['# 战斗动画第2步交付索引','', '七条均待用户游戏内验收。右侧原版保留。','']
for n,r in J.items():
 root=HA if n.startswith('hero') else SA;t=r['timing'];index.append(f'- [{n} · 8倍GIF]({root}/qc/{n}_8x.gif) · [PNG]({root}/{n}.png) · [逐帧图]({root}/qc/{n}_contact_4x.png) — {t["frames"]}帧 / {t["duration_ms"]}ms')
index+=['',f'- [右侧原版 / 短臂版并排GIF]({SA}/qc/skeleton_B_attack_right_v1_v2_compare_8x.gif)',f'- [前臂长度标记图]({SA}/qc/skeleton_B_attack_right_v2_forearm_compare_8x.png)',f'- [完整QA]({HA}/qc/combat_step2_QA.md)','']
for kind in ['hero','skeleton']:
 q=D/kind/'qc';(q/'combat_step2_QA.md').write_text('\n'.join(md)+'\n',encoding='utf8');(q/'combat_step2_index.md').write_text('\n'.join(index)+'\n',encoding='utf8')
# Refuse unintended replacements. Only authorized timing appends modify existing files.
for kind,root in [('hero',HA),('skeleton',SA)]:
 for p in (D/kind).rglob('*'):
  if p.is_file():assert not (root/p.relative_to(D/kind)).exists(),root/p.relative_to(D/kind)
updates={};oldcounts={}
for kind,root in [('hero',HA),('skeleton',SA)]:
 backup=root/'qc/backups/before_combat_step2_20261028/timing.json';assert not backup.exists();backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/'timing.json',backup);old=json.loads((root/'timing.json').read_text());new=copy.deepcopy(old);assert not set(entries[kind])&set(old['animations']);new['animations'].update(entries[kind]);assert all(new['animations'][n]==t for n,t in old['animations'].items());updates[kind]=new;oldcounts[kind]=len(old['animations'])
for kind,root in [('hero',HA),('skeleton',SA)]:
 for p in (D/kind).rglob('*'):
  if p.is_file():target=root/p.relative_to(D/kind);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);assert sha(p)==sha(target)
 (root/'timing.json').write_text(json.dumps(updates[kind],ensure_ascii=False,indent=2)+'\n')
changed=[p for p,h in protected.items() if sha(p)!=h];assert set(changed)=={str(HA/'timing.json'),str(SA/'timing.json')};assert sha(oldattack)==oldsha
report={'protected_files':len(protected),'changed_existing_files':changed,'standard_and_existing_animations_unchanged':True,'original_attack_right_file_unchanged':True,'right_v2_only_modified_frames':[5,6],'right_v2_other_frame_png_bytes_exact':True,'timing_old_counts':oldcounts,'timing_new_counts':{k:len(v['animations']) for k,v in updates.items()},'all_old_timing_entries_unchanged':True,'new_animations':7,'total_new_frame_count':sum(r['timing']['frames'] for r in J.values()),'all_gifs_decoded_and_verified':True}
for root in [HA,SA]:(root/'qc/combat_step2_preservation_check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
