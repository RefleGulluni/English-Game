from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil,copy
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-combat-trial-20261028');D=W/'delivery';HA=R/'art/character_design/anim';SA=R/'art/character_design/enemies/skeleton/anim';data=json.loads((W/'final_results.json').read_text());plan=json.loads((W/'plan.json').read_text());entries=json.loads((W/'timing_entries.json').read_text());protected=json.loads((W/'protected.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert all(Path(p).exists() and sha(p)==h for p,h in protected.items()),'Existing files changed during work; stop publication'
# Explicit neck occupancy check after each independent rigid-body displacement.
import numpy as np
neck_checks=[]
for kind,name,ref in [('hero','hero_B1_cast_right','art/character_design/hero_B1_right.png'),('skeleton','skeleton_B_attack_right','art/character_design/enemies/skeleton/skeleton_B_right.png')]:
 m=np.array(Image.open(R/ref).convert('RGBA'));fw=96 if kind=='hero' else 160;ox=0 if kind=='hero' else 32
 for k,row in enumerate(plan[kind]):
  a=np.array(Image.open(D/kind/'frames'/name/f'{k+1:02}.png').convert('RGBA'));dx,dy=(row['body_dx'],0) if kind=='hero' else row['upper'];ys,xs=np.where(m[15:22,40:51,3]>0);ys+=15;xs+=40;assert (a[ys+dy,xs+ox+dx,3]==255).all();neck_checks.append({'actor':kind,'frame':k+1,'missing_original_neck_pixels':0})
# QA includes all actual deviations rather than declaring trial accepted.
md=['# 战斗动画第1步 · 右侧双试样 QA','', '日期：2026-10-28。依据 COMBAT_ANIMATION_REQUEST.md 全文；只交主角右侧施法和骷髅右侧攻击。状态：文件自查完成，等待用户在正式游戏内验收。','', '## 动作与 timing','',
'- 主角 `hero_B1_cast_right.png`：8帧，768×96，每格96×96，锚点(48,96)，总长760ms。时长90/100/100/120/100/90/80/80ms；**第4帧出手**，0基索引3，动画开始后290ms。左手收至胸前→抬掌调用词→停住→收回。所有词共用；没有魔法特效或额外青蓝。',
'- 骷髅 `skeleton_B_attack_right.png`：9帧，1440×96，每格160×96，锚点(80,96)，总长1010ms。时长100/130/150/140/60/70/140/120/100ms；**第5帧命中**，0基索引4，开始后520ms。骨盆先坐回，头颈胸晚一帧跟上；手臂被往后扯，随后两帧快速前划，再顿挫收回。',
'- 两条均不循环；8倍GIF使用同一时长表、不额外补停顿。GIF已解码检查帧数、每帧时长、不透明RGBA和透明遮罩。',
'- `timing.json` 的 frame / release_frame / hit_frame 为**1基**；frame_index / release_frame_index / hit_frame_index 为**0基**。骷髅旧 timing 顶层仍是96×96旧动作默认值；**新攻击条目有自己的 frame_size=[160,96] 和 anchor=[80,96]，接入时必须按此条目覆盖**，没有改任何旧条目。','',
'## 站姿、左右和关节','',
'主角朝右时，提灯的右手在近侧，施法的左手从远侧胸前伸出，在灯的上方露出手掌。近侧手一直提灯；灯提手保持在手指下方，灯底按0/0/0/0/+1/0/-1/0px的额外摆幅滞后，不是整灯水平滑动。腰书和挎包没有重设计；此右侧标准图没有可见青蓝印记，所有帧均不补印记。',
'骷髅用近侧右臂出招，肩部两钉、右肩至左胫的裹尸布、包住的胸口和骨盆均以右侧标准图为来源。动作帧从同一完整站姿重建，没有读取旧行走帧或拼接旧上下半身。头、颈、胸保持同一竖直位移；没有重新画头骨或肋骨。',
'所有帧两脚像素均固定：主角y78～95、骷髅y84～95与站姿完全相同，最低不透明行均y95。没有7px/5px的行走锁脚位移，因为这是站定出手。颈部源像素覆盖逐帧核对为0缺失，整个人每帧均为1个8邻域连通件，没有漂浮头、手或骨刃组件。该连通性检查不替代关节是否自然的游戏内判断。','',
'## 命中骨尖','',
'第5帧骨尖坐标 **(145,26)**，相对脚底锚点 **(+65,-70)**。命中水平前伸65px，符合60～70px目标；没有把身体画到画布前方，整个人往前40px由程序做。40+65=105px的尖端前伸，能否准确碰到距离约120px的主角前侧轮廓，还需结合主角碰撞、双方斜向高低差在游戏内核对。',
'骨刃来自本人的断前臂尖茬，不持剑；肘端和尖茬间保留暗色组织牵连。蓄力和回收时腕手折向身体，命中时只见前臂骨尖。命中姿势的骨臂被结构扯得较长，是否仍一眼读作自身骨头、是否有“持械”的错觉，是本次试样需要用户判断的一项。','',
'## 原图与像素来源','',
'使用内置 image_gen：两张独立动作稿（主角4×2、骷髅3×3），另补一张骨刃命中稿；不是单行生成。提示词、原图、观测格线、中心取样后的原生动作稿均在各自 qc/combat_sources。原生采样边界跟随实际块边并受站姿模板的格距约束，生成网格局部仍可能有推断误差；未声称生成稿每格完美。没有整图缩小、插值、旋转、镜像或程序生成新纹理。',
'最终保留站姿的头颈胸、腰部配件和脚，选取动作稿中有用的手臂像素，在原生网格用整数位移重组完整姿势；肩部原骨帽收短到连接所需的像素范围，避免同时残留一截垂臂。提灯下半段与布自由边的轻微倾斜通过原生行/列像素错位表达，不旋转位图。',
'主角仅用四张现行标准图已有颜色；骷髅仅用已有48色。生成手臂先归并至对应人物的既有色，随后只在手臂选取同部位的明暗，避免生成稿偏白；骷髅第4～6帧下垂的自由布片选用原布的较暗色，腰骨与头胸源像素不做全身调色。没有半透明、光晕、发光、符文、速度线、拖影或闪白。','',
'## 首尾 RGBA 与标准文件哈希','',
'RGBA哈希为原生数组行优先全部字节的SHA256，包含透明像素；文件SHA为PNG文件字节的SHA256。骷髅比较时把96×96站姿原样贴到160×96的(32,0)，其他像素为透明；不能把两个不同大小的数组直接比较。','']
for kind,d in data.items():
 md += [f'### {d["name"]}','',f'- 标准PNG：`{d["reference"]}`',f'- 标准文件SHA256（前后相同）：`{d["standard_file_sha256"]}`',f'- 原96×96站姿RGBA SHA256：`{d["standard_rgba_sha256"]}`']
 if kind=='skeleton':md.append(f'- 原样补透明边后的160×96站姿RGBA SHA256：`{d["padded_standard_rgba_sha256"]}`')
 md += [f'- 第1帧RGBA SHA256：`{d["first_frame_rgba_sha256"]}`',f'- 末帧RGBA SHA256：`{d["last_frame_rgba_sha256"]}`','- 首帧、末帧均与对应站姿逐像素相同。','']
md += ['## 逐帧零件表','', '骨盆、完整上身的位移相对于原96像素站姿；脚均不动；破布始终在左腿，未换腿。','', '|骷髅帧|骨盆 dx,dy|头颈胸 dx,dy|右臂|下摆|','|---:|---|---|---|---|']
for r in plan['skeleton']:md.append(f'|{r["f"]}|{r["pelvis"]}|{r["upper"]}|{r["phase"]}|'+('晚半拍自由边移动1px' if r['f'] in [4,5,6,7,8] else '站姿位置')+'|')
md+=['','|主角帧|完整上身前倾 dx|左手|右手/灯提手（画布）|灯底额外 dx|','|---:|---:|---|---|---:|']
hr=json.loads((W/'hero_pose_records.json').read_text())
for r,h in zip(plan['hero'],hr):md.append(f'|{r["f"]}|{r["body_dx"]}|{r["phase"]}|{h["lantern_grip"]} / {h["handle_top"]}|{r["lamp_bottom_dx"]}|')
md+=['','## 分段平均亮度实测','', '灰度=0.299R+0.587G+0.114B，仅统计不透明像素。每格写“均值（相对站姿差值）”；全部分段绝对差值≤2。完整颜色数、高光比例、帧差、RGBA哈希见各自 *_metrics.json；pixel_check 原始输出另附。','']
for kind,d in data.items():
 md += [f'### {d["name"]}','', '|帧|头 y0～19|胸 y20～44|腰 y45～64|腿 y65～95|与前帧变化像素|','|---:|---:|---:|---:|---:|---:|']
 for f in d['frames']:md.append('|'+str(f['frame'])+'|'+'|'.join(f'{b["mean_luma"]:.2f} ({b["delta"]:+.2f})' for b in f['bands'])+f'|{f["changed_pixels_from_previous"]}|')
md += ['','## 未完全做到 / 游戏内验收重点','',
'- 动作相邻帧的约1000像素变化是行走过渡的软目标，本次主角最大1180、骷髅最大1510，没有把快挥击用慢插帧压平。头骨、脚和衣服身份保持一致；是否显得跳仍请实际看。',
'- 骷髅命中时横着露出更多浅骨面，胸段灰度>170的像素比例比站姿高约14个百分点；四段平均亮度都已压至差值≤2，头脸源像素不重画，但不能把“均值稳定”说成高光面积完全相同。详细比例见metrics。',
'- 骨盆与肩头的错拍幅度只有1～2px，强调“被牵着”的程度、掌势是否像调用词、骨尖是否够有力以及40px程序前进后的命中点，需要用户在游戏内判断。',
'- 未改Godot场景、资源、战斗脚本或碰撞；没有替用户认定试样通过。左侧、受击、抖尘和现实反应这一轮均未做。','',
'## 文件保护与停止点','',
'制作前记录3253个既有文件的SHA256；交付前全数复核。只允许骷髅timing.json追加新条目，修改前备份到其 qc/backups/before_combat_trial_20261028/timing.json。主角此前无timing.json，本次新建。所有标准图和已通过动画不覆盖。两个QA和逐帧图均为新文件。交付后停止，等待用户游戏内验收。','']
for kind in ['hero','skeleton']:
 dest=D/kind;Q=dest/'qc';(Q/'combat_anim_QA.md').write_text('\n'.join(md)+'\n',encoding='utf8');(Q/'combat_sources/neck_checks.json').write_text(json.dumps(neck_checks,indent=2));shutil.copy2(W/'protected.json',Q/'combat_sources/protected_before.json');(Q/'combat_sources/generation_manifest.json').write_text(json.dumps({'tool':'built-in image_gen','action':data[kind]['name'],'prompt_files':[kind+'_prompt.txt']+(['skeleton_hit_prompt.txt'] if kind=='skeleton' else []),'raw':[kind+'_generated.png']+(['hit_generated.png'] if kind=='skeleton' else []),'final':'../../'+data[kind]['name']+'.png','status':'trial_pending_user_review','source':'standing pixel groups + native restored pose arm pixels; no old walk frames'},indent=2))
# reach diagram is QC annotation only, never part of runtime art.
a=Image.open(D/'skeleton/frames/skeleton_B_attack_right/05.png').convert('RGBA');b=Image.new('RGBA',(160,112),'#403d43');b.alpha_composite(a);dr=ImageDraw.Draw(b);dr.line((80,99,145,99),fill='#bbbbbb');dr.text((82,101),'65 px',fill='white');dr.line((80,92,80,100),fill='#bbbbbb');dr.line((145,26,145,100),fill='#bbbbbb');b.resize((1280,896),Image.Resampling.NEAREST).save(D/'skeleton/qc/skeleton_B_attack_right_reach_8x.png')
# No file in the deliveries may overwrite an existing artifact; timing append handled separately.
for kind,root in [('hero',HA),('skeleton',SA)]:
 for p in (D/kind).rglob('*'):
  if p.is_file():assert not (root/p.relative_to(D/kind)).exists(),root/p.relative_to(D/kind)
backup=SA/'qc/backups/before_combat_trial_20261028/timing.json';assert not backup.exists();backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SA/'timing.json',backup);old=json.loads((SA/'timing.json').read_text());new=copy.deepcopy(old);assert not set(entries['skeleton'])&set(old['animations']);new['animations'].update(entries['skeleton'])
assert not (HA/'timing.json').exists()
for kind,root in [('hero',HA),('skeleton',SA)]:
 for p in (D/kind).rglob('*'):
  if p.is_file():target=root/p.relative_to(D/kind);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);assert sha(p)==sha(target)
(SA/'timing.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n');(HA/'timing.json').write_text(json.dumps({'version':1,'frame_size':[96,96],'anchor':[48,96],'animations':entries['hero']},ensure_ascii=False,indent=2)+'\n');assert all(new['animations'][k]==v for k,v in old['animations'].items())
changed=[p for p,h in protected.items() if sha(p)!=h];assert changed==[str(SA/'timing.json')],changed
pres={'protected_files':len(protected),'changed_existing_files':changed,'old_skeleton_timing_entries':len(old['animations']),'new_skeleton_timing_entries':len(new['animations']),'all_old_timing_entries_unchanged':True,'all_standard_and_old_animation_hashes_unchanged':True,'new_hero_timing_created':True,'no_godot_scene_changes':True}
for root in [HA,SA]:(root/'qc/combat_preservation_check.json').write_text(json.dumps(pres,indent=2)+'\n')
print(json.dumps(pres,indent=2))
