from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,subprocess,sys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-v6-20261027');O=W/'staged';Q=O/'qc';D=O/'frames/skeleton_B_walk_right_v6';D.mkdir(parents=True,exist_ok=True);Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rh(a):return hashlib.sha256(a.tobytes()).hexdigest()
def load(p):return np.array(Image.open(p).convert('RGBA'))
protected={str(p):sha(p) for p in S.rglob('*') if p.is_file()};(W/'protected.json').write_text(json.dumps(protected,indent=2));old=[load(A/'frames/skeleton_B_walk_right_v5'/f'{k+1:02}.png') for k in range(8)];fs=[];patches=[];checks=[];palette=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),np.uint8);allowed={tuple(c) for c in palette};sheet=Image.new('RGBA',(768,96))
for k,src in enumerate(old):
 out=src.copy();target=D/f'{k+1:02}.png';shutil.copy2(A/'frames/skeleton_B_walk_right_v5'/f'{k+1:02}.png',target)
 if k in [1,5]:
  for x in range(40,51):
   assert out[20,x,3]==0 and out[19,x,3]==255 and out[21,x,3]==255
   out[20,x]=src[21,x];patches.append({'frame':k+1,'target':[x,20],'source_same_frame':[x,21],'before_rgba':src[20,x].tolist(),'after_rgba':out[20,x].tolist()})
  Image.fromarray(out).save(target)
 changed=(out!=src).any(2);ys,xs=np.where(changed);assert len(xs)==(11 if k in [1,5] else 0)
 assert np.array_equal(out[:20],src[:20]) and np.array_equal(out[21:],src[21:]);assert set(np.unique(out[:,:,3]))<={0,255};assert {tuple(c) for c in out[out[:,:,3]>0,:3]}<=allowed
 # Joint-only scan: natural silhouette background and gaps between limbs are not filled.
 assert all((out[y,43:51,3]>0).any() for y in range(17,24))
 holes=[]
 for y in range(18,23):
  for x in range(40,51):
   if out[y,x,3]==0 and out[y-1,x,3]==255 and out[y+1,x,3]==255:holes.append([x,y])
 assert not holes
 file_same=sha(target)==protected[str(A/'frames/skeleton_B_walk_right_v5'/f'{k+1:02}.png')]
 if k not in [1,5]:assert file_same
 checks.append({'frame':k+1,'changed_pixels_vs_v5':len(xs),'changes_bbox':None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'unchanged_file_bytes_vs_v5':file_same,'rgba_sha256':rh(out),'head_y0_19_rgba_exact_v5':True,'body_y21_95_rgba_exact_v5':True,'neck_joint_has_no_1row_background_gap':True,'alpha_values':np.unique(out[:,:,3]).tolist(),'colors':len(np.unique(out[out[:,:,3]>0,:3],axis=0))})
 fs.append(out);sheet.alpha_composite(Image.fromarray(out),(96*k,0))
sheet.save(O/'skeleton_B_walk_right_v6.png')
flat=[0,0,0]+palette.flatten().tolist();flat += [0]*(768-len(flat))
def gif(path,arr,loop):
 pp=[]
 for a in arr:
  ix=np.zeros((96,96),np.uint8)
  for j,c in enumerate(palette):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=j+1
  im=Image.fromarray(ix).convert('P');im.putpalette(flat);pp.append(im.resize((768,768),Image.Resampling.NEAREST))
 opt={'loop':0} if loop else {};pp[0].save(path,save_all=True,append_images=pp[1:],duration=[100]*len(arr),transparency=0,disposal=2,optimize=False,**opt);g=Image.open(path);assert g.n_frames==len(arr)
 for k,a in enumerate(arr):
  g.seek(k);b=np.array(g.convert('RGBA'));expected=np.repeat(np.repeat(a,8,axis=0),8,axis=1);fg=expected[:,:,3]>0;assert np.array_equal(b[:,:,3],expected[:,:,3]) and np.array_equal(b[fg],expected[fg]) and g.info['duration']==100

gif(Q/'skeleton_B_walk_right_v6_8x.gif',fs,True);start=[load(A/'frames/skeleton_B_walk_start_right'/f'{k+1:02}.png') for k in range(3)];stop=[load(A/'frames/skeleton_B_walk_stop_right'/f'{k+1:02}.png') for k in range(3)];gif(Q/'skeleton_B_right_v6_start_walk_stop_8x.gif',start+fs+fs+stop,False)
b=Image.new('RGBA',(4*112,2*116),'#403D3F');dr=ImageDraw.Draw(b)
for k,a in enumerate(fs):x=k%4*112;y=k//4*116;b.alpha_composite(Image.fromarray(a),(x+8,y));dr.text((x+8,y+99),str(k+1),fill='white')
b.resize((b.width*4,b.height*4),Image.Resampling.NEAREST).save(Q/'skeleton_B_walk_right_v6_contact_4x.png')
b=Image.new('RGBA',(8*32,2*36),'#403D3F');dr=ImageDraw.Draw(b)
for row,arr in enumerate([old,fs]):
 for k,a in enumerate(arr):x=k*32;y=row*36;b.alpha_composite(Image.fromarray(a).crop((34,9,63,36)),(x,y));dr.text((x,y+27),f'{"v5" if row==0 else "v6"} {k+1}',fill='white')
b.resize((b.width*16,b.height*16),Image.Resampling.NEAREST).save(Q/'skeleton_B_walk_right_v6_neck_compare_16x.png')
(Q/'skeleton_B_walk_right_v6_verification.json').write_text(json.dumps({'modified_frames':[2,6],'total_changed_pixels':22,'patches':patches,'frames':checks,'gif_decoded_rgba_alpha_timing_exact':True,'durations_ms':[100]*8},indent=2))
files=sorted(D.glob('*.png'));z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1.png'),*map(str,files)],text=True,capture_output=True);assert z.returncode==0;(Q/'skeleton_B_walk_right_v6_pixel_check.txt').write_text(z.stdout+z.stderr)
md=['# 右侧行走 V6 · 颈骨连接 QA','', '依据 `docs/SKELETON_ANIMATION_REQUEST.md` §18.1，只修 V5 行走第 2、6 帧的头肩连接；其他六帧、起步、停步、重组、标准图和旧版均不覆盖。','', '## 改动','', '第 2、6 帧胸廓 dy=1、头 dy=0，y20 的 x40～50 原为透明。各补一行 11 个像素，颜色逐像素取同帧 y21 的原有颈骨 / 连接边缘。**总计新增 22 个不透明像素**，没有移动头、胸廓或其他零件。','', '| 帧 | 改动像素 | 范围 | 其余部分 |','|---|---:|---|---|']
for r in checks:md.append(f'| {r["frame"]} | {r["changed_pixels_vs_v5"]} | {"x40～50, y20" if r["changed_pixels_vs_v5"] else "无"} | {"其余 RGBA 完全相同" if r["changed_pixels_vs_v5"] else "RGBA 与 PNG 文件字节均同 V5"} |')
md+=['','## 核对','', '- 八帧都检查了头肩连接区：颈部各行有连接像素，没有“上下一行不透明、中间一行透明”的横缝。只扫描关节连接，保留正常轮廓外背景与骨间空隙。','- 每帧 y0～19、y21～95 均与 V5 RGBA 相同；头、胸廓、布、腿、脚、手臂和锁脚没有改动。','- 新版仍为 8×100 ms、768×96，每格 96×96，锚点 (48,96)；颜色取自既有调色板，alpha 只有 0/255，无新色、青蓝、模糊、光晕或投影。','- 六个未修帧直接复制 V5 文件，文件 SHA256 也相同；两处只填原透明像素。','- 8 倍 GIF 与起步→两圈行走→停步预览已重解码核对像素、透明遮罩、帧数和时长。起步 / 停步引用原 PNG，未重画。','', '## 逐像素补色','', '| 帧 | x,y | 颜色来源 | 实际 RGBA |','|---|---|---|---|']
for p in patches:md.append(f'| {p["frame"]} | {p["target"]} | {p["source_same_frame"]} | {p["after_rgba"]} |')
md+=['','## RGBA 哈希','', '| 帧 | RGBA SHA256 |','|---|---|']
for r in checks:md.append(f'| {r["frame"]} | `{r["rgba_sha256"]}` |')
md+=['','[8 倍 GIF](skeleton_B_walk_right_v6_8x.gif) · [头颈 16 倍对比](skeleton_B_walk_right_v6_neck_compare_16x.png) · [逐帧 4 倍](skeleton_B_walk_right_v6_contact_4x.png) · [起步 / 行走 / 停步连播](skeleton_B_right_v6_start_walk_stop_8x.gif) · [像素检查](skeleton_B_walk_right_v6_pixel_check.txt) · [完整数据](skeleton_B_walk_right_v6_verification.json)。','', '只修改连接缝，V5 已记录的帧差与旧固定分段灰度未达项没有借本次顺手重画，仍按 V5 QA 如实保留。','', '## 后续三个方向的连接检查','', '逐帧扫描头颈、颈胸、胸腰、髋腿根等标记连接区，尤其检查相邻刚性块位移不同的帧；不能只验证每块底稿的哈希。连接拉开时，用同部位原生像素补柔性颈骨 / 连接，不改变骨头身份与衣料归属，不把正常四肢间隙误填。','', '原文件保护：发布只会在备份后追加 `timing.json` 的 V6 条目，旧动画条目与旧文件保持原样。备份：`qc/backups/before_v6_20261027/timing.json`。交付后停止，等待游戏验收。']
(Q/'skeleton_B_walk_right_v6_QA.md').write_text('\n'.join(md)+'\n');src=Q/'v6_sources';src.mkdir(exist_ok=True);shutil.copy2(W/'make_v6.py',src/'make_v6.py');shutil.copy2(W/'protected.json',src/'protected.json')
assert all(Path(p).exists() and sha(p)==h for p,h in protected.items());newfiles=[p for p in O.rglob('*') if p.is_file()];assert all(not (A/p.relative_to(O)).exists() for p in newfiles)
backup=A/'qc/backups/before_v6_20261027/timing.json';assert not backup.exists();backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(A/'timing.json',backup);oldtime=json.loads((A/'timing.json').read_text());newtime=json.loads(json.dumps(oldtime));entry=oldtime['animations']['skeleton_B_walk_right_v5'].copy();entry['sprite_sheet']='skeleton_B_walk_right_v6.png';newtime['animations']['skeleton_B_walk_right_v6']=entry
for p in newfiles:dest=A/p.relative_to(O);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(A/'timing.json').write_text(json.dumps(newtime,ensure_ascii=False,indent=2)+'\n');assert sha(backup)==protected[str(A/'timing.json')];assert all(newtime['animations'][n]==t for n,t in oldtime['animations'].items());assert [p for p,h in protected.items() if sha(p)!=h]==[str(A/'timing.json')]
print('Published V6: frames2/6 each +11 neck pixels; other6 PNGs byte-identical; all prior artwork unchanged, timing backup+append only.')
