from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,subprocess,importlib.util
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');P=R/'art/cemetery_v3/props';W=Path('/Users/mac/.codex/work/broken-wing-angel-20261030');O=W/'staged';Q=O/'qc';S=Q/'fountain_broken_wing_01_sources';n='fountain_broken_wing_01';m=json.loads((S/'edit_metrics.json').read_text());read=lambda p:np.array(Image.open(p).convert('RGBA'));L=np.array([.299,.587,.114]);original=read(P/'fountain_dry_01.png');new=read(O/(n+'.png'));shards=read(S/'shards_layer.png');sm=shards[:,:,3]>0;under=read(S/'underlying_pool_native.png');removed=np.array(Image.open(S/'removed_wing_mask.png'))>0;fracture=np.array(Image.open(S/'fracture_mask.png'))>0
# Revalidate from saved final sprite; don't rely only on working arrays.
diff=(original!=new).any(2);assert int(diff.sum())==m['changed_pixel_count'];assert not (diff&~(removed|fracture|sm)).any();assert np.array_equal(original[sm],under[sm]);assert np.array_equal(new[removed],under[removed]);visible_pool=(original==under).all(2)&(under[:,:,3]>0);assert not (diff&visible_pool&~sm).any();assert (O/(n+'_base.png')).read_bytes()==(P/'fountain_dry_01_base.png').read_bytes()
#7actual disconnected chunks, with no arbitrary pixel noise outside them.
todo=set(zip(*np.where(sm)));components=[]
while todo:
 q=[todo.pop()];cc=q.copy()
 while q:
  y,x=q.pop()
  for dy in [-1,0,1]:
   for dx in [-1,0,1]:
    pt=(y+dy,x+dx)
    if pt in todo:todo.remove(pt);q.append(pt);cc.append(pt)
 components.append(len(cc))
assert len(components)==7
face=original[78:94,114:130];face_max=float((face[face[:,:,3]>0,:3]@L).max());shardmax=float((shards[sm,:3]@L).max());assert shardmax<=face_max
sp=importlib.util.spec_from_file_location('pc',R/'scripts/tools/pixel_check.py');pc=importlib.util.module_from_spec(sp);sp.loader.exec_module(pc);pstats=pc.measure(O/(n+'.png'));bstats=pc.measure(O/(n+'_base.png'));assert pstats['alpha_ok'] and bstats['alpha_ok'] and not pstats['cyan'] and not bstats['cyan']
result=subprocess.run(['python3',str(R/'scripts/tools/pixel_check.py'),str(O/(n+'.png')),str(O/(n+'_base.png'))],cwd=R,text=True,capture_output=True,check=True);(Q/(n+'_pixel_check.txt')).write_text(result.stdout)
m.update(prop_pixel_check=pstats,base_pixel_check=bstats,actual_shard_components=len(components),shard_component_sizes=sorted(components,reverse=True),shard_max_luma=round(shardmax,3),face_max_luma=round(face_max,3),visible_pool_pixels_changed_outside_shards=0,source_under_wing_restored_exact=True,final_png_sha256=hashlib.sha256((O/(n+'.png')).read_bytes()).hexdigest());(S/'edit_metrics.json').write_text(json.dumps(m,indent=2))
# Reference provenance: generated local-cut guide only; all runtime pixels
# derive from the original wing, its palette, and the original pool layer.
g=json.loads((W/'generation_reference.json').read_text());shutil.copy2(g['path'],S/'local_wing_cut_guide_generated.png');shutil.copy2(W/'generation_reference.json',S/'generation_reference.json');shutil.copy2(W/'wing_reference_12x.png',S/'wing_reference_12x.png');shutil.copy2(P/'fountain_dry_01.png',S/'parent_fountain.png');shutil.copy2(P/'fountain_dry_01_base.png',S/'parent_base.png');shutil.copy2(P/'qc/entry_step2_sources/fountain_fullsize_revision/angel_full_native.png',S/'parent_angel_native.png');shutil.copy2(P/'qc/entry_step2_sources/fountain_fullsize_revision/pool_full_native.png',S/'parent_pool_native.png');shutil.copy2(W/'edit.py',S/'edit.py');shutil.copy2(W/'before.json',S/'before.json')
rows=[]
for s in m['shards']:
 x0,y0,x1,y1=s['bbox_exclusive'];rows.append(f"| {s['name']} | {x1-x0}×{y1-y0} | x{x0}～{x1-1}, y{y0}～{y1-1} | {s['pixel_count']} |")
qa=f'''# 碎翼天使喷泉 — QA / 2026-10-30

状态：**制作与离线检查完成，等待用户验收**。新文件 `fountain_broken_wing_01.png` 和 `_base.png`；256×256，原点(128,256)，与入口原版完全一致。没有改原版入口喷泉、底座、游戏房间或积木。

## 改动与原图保护

正式素材从 `fountain_dry_01.png` 的原生RGBA复制出发。保留上半截翼的羽毛、天使脸/头/身体/衣褶、雕像基座、池沿与缺口、苔藓；只修改断翼和池底7块碎片。

- 翼尖下半截从约y121～126开始断开，实际移除区域在x141～156、y123～162附近，按原翅膀alpha和内缘逐像素选区。原翼从约y84延伸至y160，剩下约一半；上部y<118完全不动。断口有多个高低不齐的凹凸石茬，深浅断面只在2～3px薄带内，保留原羽毛沟槽，没有把整只翼抹掉。
- 删除翼尖的 **{m['wing_removed_pixel_count']}** 个像素位置，以同一个原池子底稿 `pool_full_native.png`、原整数坐标(31,129)恢复；高于池沿的部分恢复透明。不是猜画池壁。露出的位置仍是原池子本来的像素。
- 断口整理范围约x141～156、y118～125，薄带 **{m['fracture_band_pixels']}** 个选区像素；从原羽翼颜色提取较浅的原图石色，表示没有被风吹黑的石芯，未加光。
- 碎片 **7块**、共 **{m['shard_pixel_count']}** 个像素。全部落在原池底（与同位置原始pool层逐像素一致），没有覆盖天使、基座或池沿。两块大的直接选取原断掉羽翼的纹理和羽毛刻槽，整数移到池底，整理破碎轮廓与浅断面；没有旋转或镜像。
- 实际RGBA不同像素 **{m['changed_pixel_count']}**，总bbox含端点 **{m['changed_bbox_inclusive']}**。选区以外不同像素 **0**；原先可见池子（碎片处除外）不同像素 **0**；断翼下恢复的背景与原pool底稿一致。
- `_base` **直接字节复制** `fountain_dry_01_base.png`，既有地面泥贴花没改。所有断口和池内碎片都在本体图中，仍按同一个池脚排序。

精确逐列断口位置、碎片独立原生PNG、碎片原始羽翼选区、实际变化蒙版和校验见 `fountain_broken_wing_01_sources/edit_metrics.json` 及同目录PNG；没把整个bbox都当作改过。

##7块碎片

坐标从0起，范围含首尾；尺寸是单块的包围盒，边缘不填满矩形。大块保留羽毛纹路，最小块为1×2px的小石芯，不额外撒随机杂点。

| 碎片 | 原生大小 | 最终位置 | 实际像素 |
|---|---|---|---:|
{chr(10).join(rows)}

碎片最高亮度 **{shardmax:.3f}**（Y=0.299R+0.587G+0.114B），低于原天使脸部最高亮度 **{face_max:.3f}**；相较池泥更干净、偏浅，但没有白光。新增颜色 **0种**，所有新出现的断面颜色都取自原喷泉色表。

## 数字与交付

| 文件 | 画布 | 不透明颜色 | 水平相邻换色 | Alpha | 饱和青蓝 |
|---|---|---:|---:|---|---:|
| 本体 | {pstats['size']} | {pstats['colors']} | {pstats['change']}% | 0/255 | {pstats['cyan']} |
| 底座 | {bstats['size']} | {bstats['colors']} | {bstats['change']}% | 0/255 | {bstats['cyan']} |

`pixel_check.py` 已运行，文本报告为 `fountain_broken_wing_01_pixel_check.txt`。底座数值是入口已通过版本的原样数值，本次没有为提高换色比例去动它。无抗锯齿、半透明、光晕、地面投影、统一黑描边、可读字母。

- `fountain_broken_wing_01_compare_6x.png`：左原版、右碎翼版，同画布nearest6倍；标签仅在QC的透明留白上。
- `fountain_broken_wing_01_vs_hero_2x.png`：正式泥地上摆碎翼喷泉，主角站池前，nearest2倍。主角书上的青蓝是原主角图自带，不在喷泉里。
- `fountain_broken_wing_01_sources/detail_check_6x.png`：翼部对照和池底碎片特写，便于核对形状。

## 来源、备份与如实说明

按“同家族以已有像素为底子改”制作；内置image_gen仅对翼部小裁片生成了局部断口参考，原图/提示词在 `generation_reference.json` 和 `local_wing_cut_guide_generated.png`。**没有重新生成整座喷泉，也没有拿生成图替换原雕像。** 正式改动采用父图原生像素、局部选区、原色表断面整理和整数移动；不缩放、旋转或镜像原画，也不生成随机纹理。

原版PNG SHA256：`{m['source_png_sha256']}`。
原版底座PNG SHA256：`{m['source_base_png_sha256']}`。
两者修改前后完全一致；新底座也与这个底座哈希完全一致。完整保护审计在 `fountain_broken_wing_01_preservation.json`。manifest仅新增本变体，旧条目逐值相同；修改前manifest在 `backups/before_broken_wing_20261030/`。

最小的1～2px碎片在1倍下只读成干净石屑，羽毛纹理主要靠两块大碎片；这点不冒称每块都能辨认是羽毛。断口显不显眼、玩家能否一眼联系shattered，还需要用户在第2房间里判断。检查图是离线拼摆，不冒称游戏里已经验收。

完成后停下，等用户验收。
'''
(Q/(n+'_QA.md')).write_text(qa)
# Install new files only, then append exactly one manifestitem.
manifest=json.loads((P/'props_manifest.json').read_text());prior=json.loads(json.dumps(manifest));assert n not in manifest['items']
manifest['items'][n]={'prop':n+'.png','base':n+'_base.png','canvas':[256,256],'origin':[128,256],'visible_height_px':Image.open(O/(n+'.png')).getbbox()[3]-Image.open(O/(n+'.png')).getbbox()[1],'family':'stone','variant_of':'fountain_dry_01','source_record':'qc/'+n+'_sources/edit_metrics.json','qa':'qc/'+n+'_QA.md','status':'pending_user_review','flat_base_only':False,'no_auto_trim':True,'shattered_wing':True,'fallen_fragments':7}
for suffix in ['', '_base']:
 dst=P/(n+suffix+'.png');assert not dst.exists();shutil.copy2(O/dst.name,dst)
for p in Q.iterdir():
 dst=P/'qc'/p.name;assert not dst.exists(),dst
 if p.is_dir():shutil.copytree(p,dst)
 else:shutil.copy2(p,dst)
(P/'props_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for k,v in prior.items():
 if k=='items':
  for name,item in v.items():assert manifest[k][name]==item
 else:assert manifest[k]==v
before=json.loads((W/'before.json').read_text());changed=[];missing=[]
for rel,h in before.items():
 p=R/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(rel)
assert changed==['art/cemetery_v3/props/props_manifest.json'],changed;assert not missing
assert hashlib.sha256((P/'fountain_dry_01.png').read_bytes()).hexdigest()==m['source_png_sha256'];assert (P/(n+'_base.png')).read_bytes()==(P/'fountain_dry_01_base.png').read_bytes()
assert (P/(n+'.png')).read_bytes()==(O/(n+'.png')).read_bytes()
(P/'qc'/(n+'_preservation.json')).write_text(json.dumps({'preexisting_files_checked':len(before),'changed_existing_files':changed,'missing_files':missing,'parent_fountain_unchanged':True,'parent_base_unchanged':True,'new_base_exact_parent_copy':True,'all_old_manifest_entries_unchanged':True,'outside_edit_masks_changes':0,'visible_pool_changes_outside_shards':0,'final_runtime_exact_staged_pixels':True},indent=2))
shutil.copy2(W/'publish.py',P/'qc'/(n+'_sources')/'publish.py');print('Published brokenwing variant. Protected',len(before),'preexisting files; onlymanifest changed.')
