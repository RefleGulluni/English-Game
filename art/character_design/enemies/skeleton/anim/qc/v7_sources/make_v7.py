from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,subprocess,sys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-v7-20261027');O=W/'staged';Q=O/'qc';Q.mkdir(parents=True,exist_ok=True)
def load(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rh(a):return hashlib.sha256(a.tobytes()).hexdigest()
protected={str(p):sha(p) for p in S.rglob('*') if p.is_file()};(W/'protected.json').write_text(json.dumps(protected,indent=2));master=load(S/'skeleton_B_right.png');palette=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),np.uint8);allowed={tuple(c) for c in palette};parts={p.stem:load(p) for p in (A/'qc/v5_sources/standing_parts').glob('*.png')};records=json.loads((A/'qc/v5_sources/walk_records.json').read_text());plan=json.loads((A/'qc/v5_sources/parts_plan_before_drawing.json').read_text());footref=json.loads((A/'qc/v5_sources/foot_reference.json').read_text());ids=((master[:,:,:3,None].transpose(0,1,3,2).astype(int)-palette[None,None])**2).sum(3).argmin(2)
# Execute only the pure native compositor functions, with no original producer's file writes or frame generation.
code=(A/'qc/v5_sources/production/build_walk.py').read_text();defs=code[code.index('def put('):code.index('ALL={};tim={};records={}')];scope={'np':np,'M':master,'parts':parts,'footref':footref,'ids':ids,'plan':plan};exec(defs,scope);render=scope['render'];put=scope['put']
upper=parts['head'].copy();mask=parts['thorax'][:,:,3]>0;upper[mask]=parts['thorax'][mask]
# Same fixed source markers used for every frame: top of skull and the original shoulder-top mark.
assert master[0,43,3]==255 and master[11,36,3]==255
V=Q/'v7_sources';V.mkdir(exist_ok=True);Image.fromarray(upper).save(V/'standing_head_neck_thorax.png');checks=[];allframes={};timing={};oldsets={};changed_total=0
for kind,oldname,newname in [('walk','skeleton_B_walk_right_v6','skeleton_B_walk_right_v7'),('start','skeleton_B_walk_start_right',None),('stop','skeleton_B_walk_stop_right','skeleton_B_walk_stop_right_v7')]:
 rn='skeleton_B_walk_right_v5' if kind=='walk' else oldname;rs=records[rn];old=[load(A/'frames'/oldname/f'{k+1:02}.png') for k in range(len(rs))];oldsets[kind]=old;outfs=[]
 if newname:(O/'frames'/newname).mkdir(parents=True,exist_ok=True)
 for k,r0 in enumerate(rs):
  r=dict(r0);static=r.get('exact_standard',False)
  if static:
   base=master.copy();new=master.copy();dy=0;oldhead=0;chest=[0,0];head=[0,0]
  else:
   # Baseline reconstruction must reproduce the approved V5 pixels exactly before any head edit.
   base,_,_=render(r,armblend=r.get('arm_pose_blend',1));assert np.array_equal(base,load(A/'frames'/rn/f'{k+1:02}.png'))
   oldhead=r['head_offset'][1];chest=r['chest_offset'];r['head_offset']=list(chest);new,_,_=render(r,armblend=r.get('arm_pose_blend',1));dy=chest[1];head=r['head_offset']
  delta=(new!=old[k]).any(2);n=int(delta.sum());changed_total+=n
  # No changes below the head/neck. Old/new head silhouettes are the entire permitted edit envelope.
  permit=np.zeros_like(master);own=np.zeros((96,96),np.uint8);put(permit,parts['head'],0,oldhead,own,1);permit2=np.zeros_like(master);put(permit2,parts['head'],*head,own,1);edit=(permit[:,:,3]>0)|(permit2[:,:,3]>0)
  assert not (delta&~edit).any();assert np.array_equal(new[21:],old[k][21:]);assert set(np.unique(new[:,:,3]))<={0,255};assert {tuple(c) for c in new[new[:,:,3]>0,:3]}<=allowed
  if kind=='start':assert n==0
  headtop=int(np.where(new[:,:,3]>0)[0].min());shoulder_y=11+dy;assert headtop==dy and new[shoulder_y,36,3]==255 and shoulder_y-headtop==11
  # Entire upper body uses one transformation; reverse it and compare the source RGBA exactly.
  layer=np.zeros_like(master);dummy=np.zeros((96,96),np.uint8);put(layer,upper,*chest,dummy,1);ys,xs=np.where(layer[:,:,3]>0);undo=np.zeros_like(layer);undo[ys-dy,xs-chest[0]]=layer[ys,xs];assert np.array_equal(undo,upper)
  holes=[]
  for y in range(18+dy,23+dy):
   for x in range(40,51):
    if new[y,x,3]==0 and new[y-1,x,3]==255 and new[y+1,x,3]==255:holes.append([x,y])
  assert not holes
  row={'action':kind,'frame':k+1,'old_head_dy':oldhead,'new_head_dy':dy,'chest_dy':dy,'pelvis_offset':r.get('pelvis_offset',[0,0]),'head_top_y':headtop,'shoulder_source_mark_y':shoulder_y,'head_to_shoulder_distance':11,'changed_pixels':n,'rgba_sha256':rh(new),'body_y21_95_rgba_exact_original':True,'whole_upper_untranslated_sha256':rh(undo),'upper_source_sha256':rh(upper),'neck_gap_count':0}
  if newname:
   dest=O/'frames'/newname/f'{k+1:02}.png'
   if n==0:shutil.copy2(A/'frames'/oldname/f'{k+1:02}.png',dest);row['png_bytes_exact_original']=True
   else:Image.fromarray(new).save(dest);row['png_bytes_exact_original']=False
  checks.append(row);outfs.append(new)
 if newname:
  sheet=Image.new('RGBA',(96*len(outfs),96))
  for k,a in enumerate(outfs):sheet.alpha_composite(Image.fromarray(a),(96*k,0))
  sheet.save(O/(newname+'.png'));t=json.loads((A/'timing.json').read_text())['animations'][oldname].copy();t['sprite_sheet']=newname+'.png';timing[newname]=t
 allframes[kind]=outfs
assert [r['frame'] for r in checks if r['action']=='walk' and r['changed_pixels']]==[2,4,6,8]
assert [r['frame'] for r in checks if r['action']=='stop' and r['changed_pixels']]==[1,2]
assert np.array_equal(allframes['start'][0],master) and np.array_equal(allframes['stop'][-1],master)
flat=[0,0,0]+palette.flatten().tolist();flat += [0]*(768-len(flat))
def gif(path,frames,loop):
 pp=[]
 for a in frames:
  ix=np.zeros((96,96),np.uint8)
  for j,c in enumerate(palette):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=j+1
  im=Image.fromarray(ix).convert('P');im.putpalette(flat);pp.append(im.resize((768,768),Image.Resampling.NEAREST))
 opt={'loop':0} if loop else {};pp[0].save(path,save_all=True,append_images=pp[1:],duration=[100]*len(frames),transparency=0,disposal=2,optimize=False,**opt);g=Image.open(path);assert g.n_frames==len(frames)
 for k,a in enumerate(frames):
  g.seek(k);b=np.array(g.convert('RGBA'));e=np.repeat(np.repeat(a,8,axis=0),8,axis=1);fg=e[:,:,3]>0;assert np.array_equal(b[:,:,3],e[:,:,3]) and np.array_equal(b[fg],e[fg]) and g.info['duration']==100
for kind,name in [('walk','skeleton_B_walk_right_v7'),('stop','skeleton_B_walk_stop_right_v7')]:
 fs=allframes[kind];gif(Q/(name+'_8x.gif'),fs,kind=='walk');b=Image.new('RGBA',(4*112,((len(fs)+3)//4)*116),'#403D3F');d=ImageDraw.Draw(b)
 for k,a in enumerate(fs):x=k%4*112;y=k//4*116;b.alpha_composite(Image.fromarray(a),(x+8,y));d.text((x+8,y+99),str(k+1),fill='white')
 b.resize((b.width*4,b.height*4),Image.Resampling.NEAREST).save(Q/(name+'_contact_4x.png'))
gif(Q/'skeleton_B_right_v7_start_walk_stop_8x.gif',allframes['start']+allframes['walk']*2+allframes['stop'],False)
b=Image.new('RGBA',(8*32,2*40),'#403D3F');d=ImageDraw.Draw(b)
for row,fs in enumerate([oldsets['walk'],allframes['walk']]):
 for k,a in enumerate(fs):x=k*32;y=row*40;b.alpha_composite(Image.fromarray(a).crop((32,0,62,30)),(x,y));d.text((x,y+30),('v6' if row==0 else 'v7')+' '+str(k+1),fill='white')
b.resize((b.width*16,b.height*16),Image.Resampling.NEAREST).save(Q/'skeleton_B_right_v7_neck_compare_16x.png')
verification={'frames':checks,'upper_body_rgba_sha256':rh(upper),'neck_distance_all14_frames':11,'start_unchanged':True,'walk_changed_frames':[2,4,6,8],'stop_changed_frames':[1,2],'all_pixels_y21_95_unchanged':True,'all_changes_inside_old_or_new_head_mask':True,'all_gifs_decoded_rgba_alpha_and_timing_exact':True}
(Q/'skeleton_B_right_v7_verification.json').write_text(json.dumps(verification,indent=2));(V/'timing_entries.json').write_text(json.dumps(timing,indent=2));(V/'protected.json').write_text(json.dumps(protected,indent=2));shutil.copy2(W/'make_v7.py',V/'make_v7.py')
paths=sorted((O/'frames').glob('*/*.png'));z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1.png'),*map(str,paths)],capture_output=True,text=True);assert z.returncode==0;(Q/'skeleton_B_right_v7_pixel_check.txt').write_text(z.stdout+z.stderr)
md=['# 右侧 V7 · 固定头颈胸关系 QA','', '依据 `docs/SKELETON_ANIMATION_REQUEST.md` §18.3。头、颈与胸廓取站姿的同一完整源像素组，使用同一个竖直位移；上身仍跟在骨盆后面一帧。头部不再有独立竖直相位。','', '## 交付与范围','', '- `skeleton_B_walk_right_v7.png`：8 帧 / 768×96 / 8×100 ms。只改第 2、4、6、8 帧的头部位置与颈部露出关系。','- `skeleton_B_walk_stop_right_v7.png`：3 帧 / 384×96 / 3×100 ms。只改前两帧；末帧仍为原站姿，PNG 文件字节也相同。','- 起步原来已头胸同步，三帧与旧文件 RGBA 完全相同，因此继续用 `skeleton_B_walk_start_right.png`，不另存重复版本。','- 每帧 y21～95 的 RGBA 与原动作完全相同；骨盆、腿、脚、布、手臂、腰部连接与锁脚保持原样。所有变化都在原头部 / 新头部的范围内。','', '旧 V6 两行临时加长的颈骨不再单独拉伸，改由站姿完整头颈胸组保持原来连接。源层本来分在头部与胸部里的边缘像素，现在随同一变换移动，不会分离。没有新增左右偏头。','', '## 14 帧实测','', '按需求的口径，固定比较原图头顶与同一个肩顶部标记：头顶源像素 (43,0)，肩部标记源像素 (36,11)。两者同移，因此差值始终 11 px；该值是需求中的“头顶到肩顶距离”，不是另行推算的解剖颈骨长度。','', '| 动作 | 帧 | 头 dy | 胸 dy | 头顶 y | 肩部标记 y | 距离 | 修改像素 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for r in checks:md.append(f'| {r["action"]} | {r["frame"]} | {r["new_head_dy"]} | {r["chest_dy"]} | {r["head_top_y"]} | {r["shoulder_source_mark_y"]} | 11 | {r["changed_pixels"]} |')
md+=['','行走上身 dy 为 `0,1,1,0,0,1,1,0`；骨盆 dy 仍为 `2,2,0,0,2,2,0,0`，上身保持原有晚一帧的减幅响应。起步、停步均列在表内，不能只检查循环八帧。','', '## 源像素与连接检查','', f'完整头颈胸源层 RGBA SHA256：`{rh(upper)}`。每帧撤销统一位移后均与此源层 RGBA 完全相同。','', '所有头、胸像素保持站姿颜色；没有缩放、旋转、重画肋骨或单独拉长 / 压短颈骨。颈部连接逐行检查，没有“上下是不透明、中间一行透明”的缝。原动作基线先用同一源像素重建并与 V5 原帧逐像素对齐，之后只改头的纵向位移；V6 的临时补行被完整源组覆盖。','', '行走未改变的第 1、3、5、7 帧直接复制 V6 PNG，文件字节相同。停步第 3 帧直接复制原停步 PNG。全部 11 个新帧 alpha 只有 0/255，颜色来自原 48 色。','', '## 预览 / 数据','', '[右侧行走 8 倍 GIF](skeleton_B_walk_right_v7_8x.gif) · [停步 8 倍 GIF](skeleton_B_walk_stop_right_v7_8x.gif) · [起步→行走→停步连播](skeleton_B_right_v7_start_walk_stop_8x.gif) · [颈部 16 倍对照](skeleton_B_right_v7_neck_compare_16x.png) · [验证 JSON](skeleton_B_right_v7_verification.json) · [像素检查](skeleton_B_right_v7_pixel_check.txt)。','', 'GIF 均已重解码逐帧核对 RGBA、透明遮罩、帧数与时长。旧版本、起步、重组和标准图不覆盖；`timing.json` 先备份到 `qc/backups/before_v7_20261027/timing.json`，再追加行走 / 停步 V7 两条，旧条目不变。','', '后续另外三个方向使用同一条规则：头、颈、胸上下同移；骨盆与完整上身可以错拍，颈部不能再单独伸缩。每帧同时核对源像素、头肩距离与关节连接区。','', '本次只修头胸纵向同步，没有扩修 V5 已记录的帧差 / 固定分段灰度未达项。未改 Godot 组装；交付后停下，等待游戏验收。']
(Q/'skeleton_B_right_v7_QA.md').write_text('\n'.join(md)+'\n')
assert all(Path(p).exists() and sha(p)==h for p,h in protected.items());files=[p for p in O.rglob('*') if p.is_file()];assert all(not (A/p.relative_to(O)).exists() for p in files);backup=A/'qc/backups/before_v7_20261027/timing.json';assert not backup.exists();backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(A/'timing.json',backup);oldtime=json.loads((A/'timing.json').read_text());newtime=json.loads(json.dumps(oldtime));assert not set(timing)&set(oldtime['animations']);newtime['animations'].update(timing)
for p in files:dest=A/p.relative_to(O);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(A/'timing.json').write_text(json.dumps(newtime,ensure_ascii=False,indent=2)+'\n');assert sha(backup)==protected[str(A/'timing.json')];assert all(newtime['animations'][n]==t for n,t in oldtime['animations'].items());assert [p for p,h in protected.items() if sha(p)!=h]==[str(A/'timing.json')]
print('PUBLISHED V7 walk+stop; 14 frames checked (original start retained), every head/shoulder distance11; y21..95 unchanged; all old files preserved except backed-up timing append.')
