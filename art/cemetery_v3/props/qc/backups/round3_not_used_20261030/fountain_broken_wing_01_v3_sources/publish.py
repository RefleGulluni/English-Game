from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,subprocess,importlib.util
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');P=R/'art/cemetery_v3/props';W=Path('/Users/mac/.codex/work/shatter-v3-20261030');O=W/'staged';Q=O/'qc';S=Q/'fountain_broken_wing_01_v3_sources';B=P/'qc/backups/before_broken_wing_v3_20261030';n='fountain_broken_wing_01';read=lambda p:np.array(Image.open(p).convert('RGBA'));L=np.array([.299,.587,.114]);m=json.loads((S/'edit_metrics.json').read_text());a=read(P/'fountain_dry_01.png');b=read(O/(n+'.png'));parts=read(S/'pieces_layer.png');pm=parts[:,:,3]>0;diff=(a!=b).any(2)
allowed=pm.copy()
for fn in ['removed_wing_mask','fracture_mask','recess_mask','crack_mask']:allowed |=np.array(Image.open(S/(fn+'.png')))>0
assert int(diff.sum())==m['changed_pixels'];assert not(diff&~allowed).any();assert np.array_equal(a[72:170,100:140],b[72:170,100:140]);assert not b[b[:,:,3]==0].any()
# Confirm29 distinct fragments/dustgroups, no accidentally joined large wing.
todo=set(zip(*np.where(pm)));components=[]
while todo:
 q=[todo.pop()];cc=q.copy()
 while q:
  y,x=q.pop()
  for dy in [-1,0,1]:
   for dx in [-1,0,1]:
    p=(y+dy,x+dx)
    if p in todo:todo.remove(p);q.append(p);cc.append(p)
 yy,xx=zip(*cc);components.append({'pixels':len(cc),'size':[int(max(xx)-min(xx)+1),int(max(yy)-min(yy)+1)]})
assert len(components)==29;assert max(max(c['size']) for c in components)<=14
# Every retained crackpath, including its branches, is one continuous8-neighbor
# line. All source cells used for debris are from actually removed wing areas.
crackmask=np.array(Image.open(S/'crack_mask.png'))>0;removed=np.array(Image.open(S/'removed_wing_mask.png'))>0
crackchecks=[]
for path in m['crack_paths']:
 pts={(y,x) for x,y in path if crackmask[y,x]};todo=pts.copy();q=[todo.pop()]
 while q:
  y,x=q.pop()
  for dy in [-1,0,1]:
   for dx in [-1,0,1]:
    pt=(y+dy,x+dx)
    if pt in todo:todo.remove(pt);q.append(pt)
 assert not todo;crackchecks.append({'pixels':len(pts),'connected':True})
used=np.array(Image.open(S/'source_cells_used_mask.png'))>0;assert not (used&~removed).any();assert int(used.sum())==int(pm.sum());assert .8<=m['pieces_area_ratio_of_removed']<=1.2
# Final frame identity of the1x compare: original / exactv2 / savedv3.
board=read(Q/(n+'_1x_compare.png'));assert board.shape[:2]==(256,768)
base=Image.open(P/'fountain_dry_01_base.png').convert('RGBA')
for k,im in enumerate([Image.fromarray(a),Image.open(W/'v2_comparison_source.png').convert('RGBA'),Image.fromarray(b)]):
 c=Image.new('RGBA',(256,256),'#403d40');c.alpha_composite(base);c.alpha_composite(im);assert np.array_equal(board[:,k*256:(k+1)*256],np.array(c))
sp=importlib.util.spec_from_file_location('pc',R/'scripts/tools/pixel_check.py');pc=importlib.util.module_from_spec(sp);sp.loader.exec_module(pc);ps=pc.measure(O/(n+'.png'));bs=pc.measure(P/(n+'_base.png'));assert ps['alpha_ok'] and bs['alpha_ok'] and not ps['cyan'] and not bs['cyan'];face=a[78:94,114:130];faceMax=float((face[face[:,:,3]>0,:3]@L).max());pieceMax=float((parts[pm,:3]@L).max());assert pieceMax<=faceMax
m.update(prop_pixel_check=ps,base_pixel_check=bs,actual_connected_components=components,crack_paths_checked=crackchecks,fragment_max_luma=round(pieceMax,3),face_max_luma=round(faceMax,3),v2_reference_png_sha256=hashlib.sha256((W/'v2_comparison_source.png').read_bytes()).hexdigest(),final_png_sha256=hashlib.sha256((O/(n+'.png')).read_bytes()).hexdigest(),native_three_panel_check_exact=True);(S/'edit_metrics.json').write_text(json.dumps(m,indent=2));shutil.copy2(W/'v2_comparison_source.png',S/'v2_comparison_source.png');shutil.copy2(W/'edit.py',S/'edit.py');shutil.copy2(W/'before.json',S/'before.json')
r=subprocess.run(['python3',str(R/'scripts/tools/pixel_check.py'),str(O/(n+'.png')),str(P/(n+'_base.png'))],cwd=R,text=True,capture_output=True,check=True);(Q/(n+'_pixel_check.txt')).write_text(r.stdout)
#Context2x: keep hero front-right so the rightfallzone can be seen above him.
g=Image.open(R/'art/cemetery_v3/ground/base/ground_base_01.png').convert('RGBA');scene=Image.new('RGBA',(480,340))
for y in range(0,340,g.height):
 for x in range(0,480,g.width):scene.paste(g,(x,y))
im=base.copy();im.alpha_composite(Image.fromarray(b));scene.alpha_composite(im,(112,34));scene.alpha_composite(Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA'),(154,230));scene.resize((960,680),Image.Resampling.NEAREST).save(Q/(n+'_vs_hero_2x.png'))
rows=[]
for p in m['pieces']:
 x0,y0,x1,y1=p['bbox_exclusive'];rows.append(f"| {p['name']} | {p['class']} | {x1-x0}×{y1-y0} | x{x0}～{x1-1}, y{y0}～{y1-1} | {p['pixel_count']} | {p['location']} |")
oldqa=(P/'qc'/(n+'_QA.md')).read_text();chipPixels=sum(p['pixel_count'] for p in m['chips']);qa=f'''# §4 第三版：shatter碎成许多块 — 2026-10-30

**当前版本以本节为准，第二版/第一版记录在下方保留。** 覆盖同名本体与QC；256×256、原点(128,256)不变。回到完整原版的原生像素来改，没有沿用第二版27×26的大块。原版喷泉、原底座、变体底座和其他既有素材保持不变。

## 1倍三张自查

`fountain_broken_wing_01_1x_compare.png` 是**768×256**，从左至右：**完整原版 / 第二版（断下一大块） / 第三版（四散碎块）**。没有文字箭头，三个256×256画布原生贴合，未缩放。中间面板取覆盖前的实际第二版PNG并留档，对三个面板重新解码校验RGBA完全一致。

已直接看这张1倍图：第二版是左前一块长的羽翼，第三版没有完整断翼，右下散开成数块大小不同的浅断面石片，肩部也更残破。第3版的“碎”主要由多个独立碎块及方向性分布表达，裂纹细节不能冒称1倍下像特写一样清楚。是否让未被告知的玩家认出shatter，仍需用户在游戏判断。

## 肩部：尖茬、崩缺和分叉裂纹

- 原来肩边的小茬继续保留，末端改为y101～111的几个长短不同尖角；不是第二版接近平直的一条切口。突出的端部和凹处形成高低差。
- **3处崩缺**：每处从原生轮廓/断口取走1～2px，内侧用原图较暗石色表示凹进去的断面；相邻断脊提到原图浅石色。缺口坐标和暗面坐标逐项列在本轮 `edit_metrics.json` 的 `notches`。
- **3条1px深色裂纹**：从端部往肩背延伸、带短分叉；已对每条实际可见裂纹做8邻接检查，各自连续，不是几颗孤立黑点。不发光，没有青蓝。裂纹和碎茬大致x140～154、y95～110。
- 肩部破损之外的头脸、胸、手、衣褶（保护区x100～139、y72～169）逐像素不变。原翼尖消失后，仍由同一份原池子底稿、同一坐标恢复背景。

## 地上：2中块+9小块+18组石屑

不再保留27×26主块。两块中块分别为**12×11、12×13px**，取自原羽翼的不同位置，保留羽毛刻槽。9块小块为6～8px左右的斜四边形/楔形、不规则尖角形；轮廓用原有像素裁出，不是圆卵石。每块上/左有较亮的新断面，右/下是较暗的侧面，旧羽毛沟槽仍保留深浅。

实际碎片层有**29个互不相连的8邻接组成部分**：11个石块 + 18组1～2px石屑，最大连通块只有13px尺度，已检查没有接成一整只翼。2块在底座台阶上、2块在池沿；其余落池底。密集区在原翅膀正下方、天使右侧，向前方和左侧变稀。没有额外溅到池外，所以底座贴花完全不改。

| 碎块 | 类别 | 实际包围盒 | 位置（含首尾） | 实体像素 | 落点 |
|---|---|---|---|---:|---|
{chr(10).join(rows)}

18组石屑共{chipPixels}px，具体源坐标和目的坐标在metrics的 `chips` 中。碎块+石屑总面积 **{m['pieces_pixels']}px**；移除的原翼 **{m['removed_wing_pixels']}px**；比例 **{m['pieces_area_ratio_of_removed']*100:.2f}%**，约86%。不是声称面积严格守恒到100%；未表现的细粉约14%，没有为了补齐数字撒随机噪点。

**所有碎块源像素互不重复**：在原来移除的翼部区域内选择不同的原生小片，每片仅整数平移；源mask和源crop逐项记录。没有拿同一块羽毛复制成许多块，没有旋转、镜像、缩放、逐行斜切或放大。本轮只重新选择边缘与用原色表整理断面亮暗，不重新生成整座喷泉或程序生随机纹理。

## 像素/保护检查

- 本体 **{ps['colors']}色 / {ps['change']}%** 水平相邻换色，新增色 **0种**；Alpha只有0/255，透明RGB归零，饱和青蓝0。碎片最高亮度 **{pieceMax:.3f}**，低于天使脸的最高亮度 **{faceMax:.3f}**。亮面是原图石色，不是白光。
- 原底座和变体底座本轮未写入；仍为{bs['colors']}色/{bs['change']}%，与入口原底座逐字节相同。
- 相对完整父图，改变RGBA像素 **{m['changed_pixels']}**，总范围含首尾 **{m['changed_bbox_inclusive']}**；只发生在断翼/断面/崩口/裂纹和碎片遮挡蒙版内。许可范围外变化 **0**。台阶和池沿只有新碎片压住的像素改变，其余原像素不动。
- 重新运行 `pixel_check.py`，输出为 `fountain_broken_wing_01_pixel_check.txt`。三组独立蒙版、源像素选用图、最终差异图和精确指标在 `fountain_broken_wing_01_v3_sources/`；修改本体PNG哈希 `{m['final_png_sha256']}`。
- 6倍原版/第三版图、2倍主角池前图已换新；1倍图是三张。2倍图仅离线摆放，不冒称已经在Godot里验收。

## 来源、登记与限制

原版PNG哈希 `{m['original_png_sha256']}`；原版和变体底座哈希 `{m['base_png_sha256']}`。本轮覆盖前的第二版仅作为三张图中间对照保存在新来源目录；按用户说明第二版已在git，不另做本体备份。修改前manifest/旧QC在 `backups/before_broken_wing_v3_20261030/`。manifest只更新这个变体的第三版碎块计数和来源，其他条目不变；完整审计见 `fountain_broken_wing_01_v3_preservation.json`。

自查能区分“第二版一整块”和“第三版许多块”。1px裂纹/石屑在游戏里仍是细节，不能代替主体碎块的轮廓；最终教学语义能否被玩家立即识别，由用户看第2房间决定。没有改房间场景、碰撞或任何其他通过素材。

完成后停下，等用户验收。

---

# 第二版/第一版历史记录（以下旧碎块数量和形状不代表第三版）

''';(Q/(n+'_QA.md')).write_text(qa+oldqa)
manifest=json.loads((P/'props_manifest.json').read_text());prior=json.loads(json.dumps(manifest));item=manifest['items'][n]
for key in ['major_wing_fragment_bbox','major_wing_fragment_size']:item.pop(key,None)
item.update(revision=3,source_record='qc/'+n+'_v3_sources/edit_metrics.json',fallen_fragments=11,medium_fragments=2,small_fragments=9,dust_groups=18,rim_fragments=2,step_fragments=2,retained_wing_height_px=[17,27],crack_paths=3,fracture_notches=3,debris_area_ratio=m['pieces_area_ratio_of_removed'],status='pending_user_review')
shutil.copy2(O/(n+'.png'),P/(n+'.png'))
for p in Q.iterdir():
 d=P/'qc'/p.name
 if d.exists():assert (B/'qc'/p.name).exists(),('missing_backup',d)
 if p.is_dir():shutil.copytree(p,d)
 else:shutil.copy2(p,d)
(P/'props_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for k,v in prior.items():
 if k=='items':
  for nm,entry in v.items():
   if nm!=n:assert manifest[k][nm]==entry
 else:assert manifest[k]==v
before=json.loads((W/'before.json').read_text());changed=[];missing=[]
for rel,h in before.items():
 p=R/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(rel)
expected={'art/cemetery_v3/props/'+n+'.png','art/cemetery_v3/props/props_manifest.json'};expected|={'art/cemetery_v3/props/qc/'+p.name for p in Q.iterdir() if 'art/cemetery_v3/props/qc/'+p.name in before};assert set(changed)==expected,(changed,expected);assert not missing
assert hashlib.sha256((P/'fountain_dry_01.png').read_bytes()).hexdigest()==m['original_png_sha256'];assert hashlib.sha256((P/(n+'_base.png')).read_bytes()).hexdigest()==m['base_png_sha256'];assert (P/(n+'.png')).read_bytes()==(O/(n+'.png')).read_bytes()
(P/'qc'/(n+'_v3_preservation.json')).write_text(json.dumps({'existing_files_checked':len(before),'changed_existing_files':changed,'missing_files':missing,'parent_original_and_base_unchanged':True,'variant_base_unchanged':True,'other_manifest_entries_unchanged':True,'outside_allowed_masks_changed':0,'source_fragment_pixels_reused':0,'native_three_panel_exact':True,'measured_runtime_bytes_exact':True},indent=2));shutil.copy2(W/'publish.py',P/'qc'/(n+'_v3_sources')/'publish.py');print('Publishedv3. Protected',len(before),'preexisting files; originalfountain and basesunchanged.')
