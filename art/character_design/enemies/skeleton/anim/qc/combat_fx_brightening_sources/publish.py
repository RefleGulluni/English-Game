from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,colorsys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');D=R/'art/character_design/enemies/skeleton/anim';W=Path('/tmp/english-fx-brighter-20261029');O=W/'staged';Q=O/'qc';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected=json.loads((W/'protected.json').read_text());results=json.loads((W/'results.json').read_text());assert all(sha(D/p)==h for p,h in protected.items())
table=[]
for n,r in results.items():
 for f in r['frames']:
  fmt=lambda x:'—' if x is None else f'{x:.2f}'
  table.append(f"| {n.removeprefix('fx_')} | {f['frame']} | {fmt(f['min_luma'])} | {fmt(f['median_luma'])} | {fmt(f['max_luma'])} | {f['opaque_pixels']} | {' / '.join(map(str,f['component_pixel_counts'])) if 'threads' in n else '—'} |")
append='''

## 改亮（2026-10-29，第 3 步可见度返修）

按用户新要求及需求 §12.2 执行，本节替代上文骨灰最高亮度 120、布丝长度 4～10 px 的旧限制。碎骨三条已通过，本次未修改。

### 新的亮度

仅计不透明像素，公式为 0.299R+0.587G+0.114B。整条骨灰最低 **107.75**、中位 **138.42**、最高 **161.98**；整条布丝最低 **160.13**、中位 **161.24**、最高 **164.24**。每个非空骨灰帧的中位也都在 130～150 内。

骨灰只用骷髅现有 48 色集合中的 6 个中间骨色：#8A663A、#927240、#A67C42、#A98651、#B59665、#BE9E6D。四像素以上的颗粒簇，在下缘保留一个 107.75 亮度的暗像素；依然满足最低 100、最高 170。没有使用骨头最亮的奶白色。

布丝使用现有裹尸布亮色 #B99D6F、#BA9E71、#BDA174。逐根沿原线端点增加 2 px，保留原来所有像素的位置；每根现在长 **8～12 px**，仍为 1 px 宽连续线，没有 2×2 实心块。各帧根数仍为 4 / 4 / 4 / 3 / 2 / 0，消失顺序和轨迹保持不变；新增端点坐标见 `combat_fx_brightening_edits.json`。

| 素材 | 帧 | 最低亮度 | 中位亮度 | 最高亮度 | 不透明像素数 | 每根布丝长度 |
|---|---|---|---|---|---|---|
'''+ '\n'.join(table)+'''

### 不变项及检查

- 骨灰六帧的 Alpha 遮罩与覆盖前逐像素相同，只换 RGB；所有颗粒形状、位置、发射点 (24,31) 和最大 40×24 包围盒保持不变。
- 布丝仅改颜色及端点长度。单帧画布 32×32、骨灰画布 48×32，均为六帧；末帧 RGBA 全为零。
- 新增颜色 0、半透明像素 0、青蓝像素 0；不画光晕或发光。已有透明像素 RGB 仍为零。
- 每个非空布丝连通段 8～12 px，最长不超过 12 px。原生单帧已同步更新到 `frames/`，与条带重新提取结果相同。
- 同名 8 倍 GIF、8 倍逐帧接触表、metrics 和 pixel_check 报告已更新。GIF 重新解码检查帧数、每帧颜色及 Alpha，末帧全透明；时长照旧。
- **timing.json 完全没有修改**，帧数、节奏、锚点保持原值。三张碎骨条带、碎骨 GIF/QC、所有角色标准图及动画未改动。逐文件 SHA256 核对见 `combat_fx_brightening_preservation.json`。

### 实机背景检查

[新旧可见度检查图（3 倍）](combat_fx_visibility_ingame_3x.png)。使用原始 `docs/reference/reality_fx_ingame_v1.png` 的第一幅实机画面，将骨灰第 3 帧和布丝第 3 帧贴在骷髅右侧、墓穴石头前。左右采用完全相同的位置、同一截图，左为备份旧版，右为改亮版。

原截图的骷髅约为每原生像素 6 个截图像素；第一幅 800×760 截图以 nearest 呈现为 400×380，再将素材 nearest 放大 3 倍贴入，人物与素材比例一致。没有锐化、调亮背景或加描边；具体裁切、缩放及粘贴坐标见 `combat_fx_brightening_placements.json`。检查图中的青蓝线条来自原游戏截图，交付的两条 FX 没有青蓝色。

截图对比可看出泥地、墓穴前的骨灰与布丝；尚未重新在游戏里触发验证，动态叠加和雾下效果仍待用户验收。截图是静态检查，不把它当作游戏内验收通过。

### 备份

覆盖前的两张条带、对应原生单帧、GIF、接触表、metrics、pixel_check 和本 QA，全部按原路径保留于 `backups/before_combat_fx_brightening_20261029/`；另备份 timing.json 供字节对照，但未改它。原始生成稿及上一轮还原记录保持不动。执行记录见 `combat_fx_brightening_sources/`。
'''
oldqa=(D/'qc/combat_fx_QA.md').read_text();(Q/'combat_fx_QA.md').write_text(oldqa+append)
sources=Q/'combat_fx_brightening_sources';sources.mkdir(exist_ok=True)
for n in ['revise.py','publish.py','protected.json']:shutil.copy2(W/n,sources/n)
files={str(p.relative_to(O)):p for p in O.rglob('*') if p.is_file()};overwritten=[rel for rel in files if (D/rel).exists()]
backup=D/'qc/backups/before_combat_fx_brightening_20261029';assert not backup.exists();backup.mkdir(parents=True)
for rel in overwritten+['timing.json']:
 b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/rel,b);assert sha(b)==protected[rel]
for rel,p in files.items():
 dst=D/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert sha(dst)==sha(p)
changed=[rel for rel,h in protected.items() if not (D/rel).exists() or sha(D/rel)!=h];assert set(changed)==set(overwritten),(changed,overwritten)
assert sha(D/'timing.json')==protected['timing.json']
for n in ['fx_bone_chip_a','fx_bone_chip_b','fx_bone_chip_c']:assert sha(D/(n+'.png'))==protected[n+'.png']
for n in results:
 metric=json.loads((D/'qc'/f'{n}_metrics.json').read_text());strip=np.array(Image.open(D/(n+'.png')).convert('RGBA'));fw=metric['timing']['frame_size'][0];g=Image.open(D/'qc'/f'{n}_8x.gif');assert g.n_frames==6
 for k in range(6):
  a=np.array(Image.open(D/'frames'/n/f'{k+1:02}.png').convert('RGBA'));assert np.array_equal(a,strip[:,k*fw:(k+1)*fw]);g.seek(k);b=np.array(g.convert('RGBA'));e=np.repeat(np.repeat(a,8,0),8,1);fg=e[:,:,3]>0;assert np.array_equal(b[:,:,3],e[:,:,3]) and np.array_equal(b[fg],e[fg]);assert g.info['duration']==metric['timing']['durations_ms'][k]
  for c in set(map(tuple,a[a[:,:,3]>0,:3])):
   h,s,v=colorsys.rgb_to_hsv(*(np.array(c)/255));assert not(160<=h*360<=260 and s>=.35 and v>.3)
 assert not a.any()
report={'date':'2026-10-29','previous_files_checked':len(protected),'changed_existing_files':changed,'only_authorized_overwrites':True,'timing_byte_identical':True,'bone_chips_and_other_existing_files_byte_identical':True,'backup':str(backup.relative_to(D)),'new_statistics':{n:{k:r[k] for k in ['min','median','max','whole_strip_colors']} for n,r in results.items()},'published_sha256':{rel:sha(D/rel) for rel in files}}
(D/'qc/combat_fx_brightening_preservation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'checked':len(protected),'overwritten':len(changed),'published':len(files),'brightness':report['new_statistics'],'timing_unchanged':True,'chips_unchanged':True},indent=2))
