from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,subprocess,sys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-collapse-left-212-20261028');O=W/'staged';Q=O/'qc';V=Q/'collapse_left_sources';F=O/'frames/skeleton_B_collapse_left';load=lambda p:np.array(Image.open(p).convert('RGBA'));rh=lambda a:hashlib.sha256(a.tobytes()).hexdigest();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
master=load(S/'skeleton_B_left.png');front=load(A/'skeleton_B_collapse_front.png');end=front[:,-96:];rem=np.zeros_like(end);rem[48:]=load(S/'skeleton_B_remains.png');assert np.array_equal(end,rem)
fs=[load(p) for p in sorted(F.glob('*.png'))];records=json.loads((V/'frame_records.json').read_text());timing=json.loads((V/'timing_entry.json').read_text());allowed={tuple(c) for c in json.loads((A/'qc/v2_sources/palette.json').read_text())};assert len(fs)==12 and np.array_equal(fs[0],master) and np.array_equal(fs[-1],end);metrics=[]
for k,a in enumerate(fs):
 assert a.shape==(96,96,4) and set(np.unique(a[:,:,3]))<={0,255};fg=a[:,:,3]>0;colors={tuple(c) for c in a[fg,:3]};assert colors<=allowed;assert np.where(fg)[0].max()==95
 if k<5:assert np.array_equal(a,load(V/f'preserved_first5_{k+1:02}.png'))
 body=load(V/'layers'/f'{k+1:02}'/'body_no_skull.png');head=load(V/'layers'/f'{k+1:02}'/'single_skull.png');assert (head[:,:,3]>0).any();rebuilt=body.copy();mask=head[:,:,3]>0;rebuilt[mask]=head[mask];assert np.array_equal(rebuilt,a),(k,'layer reconstruction')
 ys,xs=np.where(mask);bbox=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1];center=[round((bbox[0]+bbox[2]-1)/2,1),round((bbox[1]+bbox[3]-1)/2,1)]
 neighbor=fg[:,:-1]&fg[:,1:];change=(a[:,:-1,:3]!=a[:,1:,:3]).any(2);lum=a[:,:,:3]@np.array([.299,.587,.114]);metrics.append({'frame':k+1,'duration_ms':timing['durations_ms'][k],'rgba_sha256':rh(a),'colors':len(colors),'neighbor_change_pct':round(float((neighbor&change).sum()/neighbor.sum()*100),4),'alpha_values':[int(v) for v in np.unique(a[:,:,3])],'new_colors':0,'bottom_y':95,'skull_layer_instances':1,'single_skull_bbox':bbox,'single_skull_center':center,'skull_source_rgba_sha256':rh(head),'body_no_skull_rgba_sha256':rh(body),'head_plus_body_equals_final':True})
# Decode the exported GIF, verifying every visible RGB/alpha and each frame's actual duration.
g=Image.open(Q/'skeleton_B_collapse_left_8x.gif');assert g.n_frames==12
for k,a in enumerate(fs):
 g.seek(k);decoded=np.array(g.convert('RGBA'));expected=np.repeat(np.repeat(a,8,0),8,1);assert np.array_equal(decoded[:,:,3],expected[:,:,3]);assert np.array_equal(decoded[decoded[:,:,3]>0],expected[expected[:,:,3]>0]);assert g.info['duration']==timing['durations_ms'][k]
# Skull count/trajectory view: one bounded head region in each final native frame, plus its exact separate layer.
board=Image.new('RGBA',(4*112,3*116),'#403D43');d=ImageDraw.Draw(board)
for k,(a,m) in enumerate(zip(fs,metrics)):
 x=k%4*112+8;y=k//4*116;board.alpha_composite(Image.fromarray(a),(x,y));x0,y0,x1,y1=m['single_skull_bbox'];d.rectangle((x+x0-1,y+y0-1,x+x1,y+y1),outline='#EAAD77',width=1);d.text((x,y+98),f'{k+1}  ONE SKULL',fill='#FFE0BE')
board.resize((1792,1392),Image.Resampling.NEAREST).save(Q/'skeleton_B_collapse_left_skull_track_4x.png')
# Bone destination map. Source identity markers and final occlusion explicitly numbered.
b=Image.new('RGBA',(440,140),'#403D43');d=ImageDraw.Draw(b);positions=[(8,0,fs[0]),(162,0,fs[4]),(326,0,fs[-1])]
for x,y,a in positions:b.alpha_composite(Image.fromarray(a),(x,y))
startpoints=[(48,7),(57,18),(48,28),(48,45),(46,66),(53,79),(54,52)];endpoints=[(73,76),(22,71),(49,70),(44,85),(43,80),(50,92),(22,87)];cols=['#EFBB83','#D29B79','#D5C9AB','#BF9A85','#B7B28C','#BAA78F','#D6BD9A']
for i,(sp,ep,c) in enumerate(zip(startpoints,endpoints,cols)):
 for ox,p in [(8,sp),(326,ep)]:
  x,y=ox+p[0],p[1];d.ellipse((x-3,y-3,x+3,y+3),fill='#302C31',outline=c);d.text((x-1,y-2),str(i+1),fill=c)
 d.line((8+sp[0]+4,sp[1],135,sp[1]),fill=c);d.line((290,ep[1],326+ep[0]-4,ep[1]),fill=c)
d.text((8,101),'STANDING',fill='white');d.text((162,101),'WIP2 POSE 5',fill='white');d.text((326,101),'SAME HEAP',fill='white');d.text((8,116),'1 skull / 2 pinned shoulder / 3 ribs+spine / 4 pelvis (hidden)',fill='#E9D7C5');d.text((8,127),'5 shroud / 6 long bones+feet / 7 forearms+hands',fill='#E9D7C5');b.resize((1760,560),Image.Resampling.NEAREST).save(Q/'skeleton_B_collapse_left_map.png')
# Canonical headless source versus single head, to audit the old double-skull failure directly.
b=Image.new('RGBA',(3*104,112),'#403D43');d=ImageDraw.Draw(b)
for k,(fn,label) in enumerate([('canonical_headless_heap.png','BODY: NO SKULL'),('canonical_single_skull.png','ONE SKULL'),(None,'FINAL EXACT')]):
 a=Image.open(V/fn) if fn else Image.fromarray(end);b.alpha_composite(a,(k*104+4,0));d.text((k*104+4,99),label,fill='white')
b.resize((1872,672),Image.Resampling.NEAREST).save(Q/'skeleton_B_collapse_left_head_partition_6x.png')
p=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1.png'),*[str(x) for x in sorted(F.glob('*.png'))]],capture_output=True,text=True);assert p.returncode==0;(V/'pixel_check.txt').write_text(p.stdout)
report={'action':'skeleton_B_collapse_left','spec':'21.2','frame_size':[96,96],'anchor':[48,96],'total_ms':sum(timing['durations_ms']),'first_equals_standing':True,'last_equals_front_collapse_last':True,'last_equals_remains_pasted_0_48':True,'first_rgba_sha256':rh(master),'last_rgba_sha256':rh(end),'first5_native_kept_after_source_recovery':True,'gif_decoded_exact_nearest8x':True,'skull_count_method':'One explicit skull layer per frame; headless body layer checked by masks and visual contact sheets. This is not an automatic anatomical detector.','frames':metrics};(Q/'skeleton_B_collapse_left_metrics.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
# Keep all sources auditable; input WIP2 last four cells remain reference only, never used as whole output frames.
lines=['# 骷髅 B 左侧散架（§21.2，单头骨版）','','本次只交左侧。12 帧，1152×96 横条；每格 96×96、脚底锚点 (48,96)。总长 **1280 ms**，不循环，停在第12帧。','','## 前半段保留什么','','前5帧沿用用户认可的第二稿顺序：站姿 → 垂头、腕松 → 膝部失力 → 关节分开 → 上身与骨盆断开下落。没有重新生成前5个动作。第1帧直接使用左侧标准图。第2～5帧来自原第二稿对应格，只有逐格还原、原48色归色、原生比例与落点整理。','','第二稿是放大的生成图，并非已经交付的96×96帧，所以这里的“保留”指动作及构图，不声称PNG与那张大图逐像素相同。原生还原后，第2～5格高度分别105/96/97/99；为了在96画布中保留持续下坠，分别整理到94/88/80/76高。只选择骨干/布面内部的原生扫描行重新登记，保留每个输出像素的源行号；没有整体平滑缩放、非整数resize、镜像或旋转。行表见 frame_records.json。整理后的前5帧单独留档 preserved_first5_*.png，后半段制作未改变它们。','','## 一个头骨，持续落到同一个位置','','先把公共骨堆分成“无头骨身体”与“唯一头骨”两层，归档 canonical_headless_heap.png / canonical_single_skull.png。后半段没有把带头的整张骨堆贴在掉落头骨后面。每帧只绘制一份头骨；头骨朝右下移动，落地以后换用已画好的滚转视面，再进入最终姿态。没有软件旋转头部图片。','','第6～7帧还在落的胸、肩、手臂来自第5帧原生零件；同时不显示骨堆里的胸/肩/手组，避免同一骨组提前重叠出现。第8帧开始换为落地后的对应组；布比长骨晚落，最后落定。第6～7帧清理了分组后1～5px的孤立暗色碎边，这些不是另画的小骨头。','','头骨轨迹标注图：skeleton_B_collapse_left_skull_track_4x.png。无头骨层与唯一头骨的对照：skeleton_B_collapse_left_head_partition_6x.png。这次用独立头骨选区和最终图逐帧目视复核数量，不把透明像素的连通块数量当作骨头数量。','','|帧|ms|作用|头骨选区中心 x,y|','|---|---:|---|---|']
stages=['原左侧站姿，逐像素相同','颈和手腕失力，头垂下','腿部失力，上身滞后','关节拉开，上身下落','保留第二稿断线的姿态','身体继续坠落，头往右下','肩、手臂及骨盆跟着下落','头骨落到右侧，出现侧滚视面，布仍滞后','头落到骨堆右侧，轻微过冲','头回弹，布继续落定','回弹收回，布归位','公共骨堆，逐像素相同']
for m,stage in zip(metrics,stages):lines.append(f"|{m['frame']}|{m['duration_ms']}|{stage}|{m['single_skull_center']}|")
lines+=['','## 哪块骨头去了哪里','','图号对应 skeleton_B_collapse_left_map.png：1 头骨→右侧；2 右肩与双钉→左侧；3 胸廓/脊柱→中后部拱起骨群；4 骨盆→中部布下；5 斜披裹尸布→中部覆盖；6 长骨/足骨→下缘；7 手臂/手骨→前缘。','', '头骨是这次严格追踪的一份显性对象。其他部位按骨组保持先后与遮挡关系；终态布下面的骨盆、细小肋骨不具备可独立辨认的逐根编号，因此不声称能证明每一根被挡住的小骨在中途的全部位置。请在游戏内继续看第7→8帧的落地换面是否自然。','','## 端点与文件保护','','第1帧与 skeleton_B_left.png 解码RGBA逐像素相同。RGBA SHA-256：`'+rh(master)+'`。','','第12帧与 skeleton_B_collapse_front.png 最后一格逐像素相同，也等于原骨堆贴在(0,48)。RGBA SHA-256：`'+rh(end)+'`。','','本轮没有改标准图、正面散架、骨堆、重组或其他动画。旧文件逐个保留PNG/文件哈希清单，交付前后核对。唯一更新的旧文件是 timing.json：先备份，再追加左侧这一条，原52条保持内容相同。备份：collapse_left_sources/backups/timing_before_left.json。','','## 真像素与逐帧数字','','全部帧：Alpha只有0/255；新增颜色0；无青蓝、光晕、地面投影；最低不透明行均为95。仓库 pixel_check.py 已逐帧运行，原始输出见 collapse_left_sources/pixel_check.txt。GIF已解码核对12帧、每帧时长、透明和可见RGBA全部等于原图nearest 8倍。','','|帧|颜色数|相邻横向换色比例 %|最低行|头骨层份数|','|---|---:|---:|---:|---:|']
for m in metrics:lines.append(f"|{m['frame']}|{m['colors']}|{m['neighbor_change_pct']:.3f}|95|1|")
lines+=['','## 制作来源与实际限制','','初始第二稿由内置image_gen生成；原图中第6、7格含两个头，明确是弃用的失败姿势。本轮仅取其前5格以及第6格左侧独立头骨的已画滚转视面，没有使用其带双头的完整落地格。参考还原图 palette_native_06/07 仍保留在 sources 供复核，它们不是交付动画帧。','','生成色块周期约3～4个显示像素，存在非严格等距边界；本轮按约4px的大块边界逐格恢复，完整边界在restoration_grid.json。这是对实际画格的估计，不是把生成图声称为数学上完全规则的像素网格。','','前5帧原生比例清理、后半段骨组换面及头骨滚动仍需要游戏里判断。头骨只有一份、端点相同、颜色透明等技术检查不能代替动作观感验收。此次未修改Godot工程。交付后停下，等用户验收。']
(Q/'skeleton_B_collapse_left_QA.md').write_text('\n'.join(lines),encoding='utf8')
production=V/'production';production.mkdir(exist_ok=True)
for n in ['recover.py','build.py','qc_deliver.py']:shutil.copy2(W/n,production/n)
shutil.copy2(W/'protected.json',V/'protected_old_files.json')
protected=json.loads((W/'protected.json').read_text());assert all(sha(Path(p))==h for p,h in protected.items()),'Existing skeleton files changed during work.'
backup=V/'backups';backup.mkdir(exist_ok=True);shutil.copy2(A/'timing.json',backup/'timing_before_left.json');old=json.loads((A/'timing.json').read_text());assert len(old['animations'])==52;assert 'skeleton_B_collapse_left' not in old['animations'];new=copy.deepcopy(old) if False else json.loads(json.dumps(old));new['animations']['skeleton_B_collapse_left']=timing
for p in O.rglob('*'):
 if p.is_file():assert not (A/p.relative_to(O)).exists(),str(A/p.relative_to(O))
for p in O.rglob('*'):
 if p.is_file():dst=A/p.relative_to(O);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
(A/'timing.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for p,h in protected.items():
 if Path(p)!=A/'timing.json':assert sha(Path(p))==h,p
published=json.loads((A/'timing.json').read_text());assert len(published['animations'])==53;assert {k:v for k,v in published['animations'].items() if k!='skeleton_B_collapse_left'}==old['animations']
print('DELIVERED: left only,12 frames1280ms, endpoint RGBA exact, alpha/palette/GIF checked. timing52 ->53, previous entries and all old images preserved.')
