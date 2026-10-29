from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,subprocess,importlib.util
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');P=R/'art/cemetery_v3/props';W=Path('/Users/mac/.codex/work/word-props-revision-20261029');O=W/'staged';Q=O/'qc';S=Q/'word_props_revision_sources';details=json.loads((S/'cleanup_index.json').read_text());metrics=json.loads((Q/'word_props_revision_metrics.json').read_text());B=P/'qc/backups/before_word_props_revision_20261029'
ns=['raven_ground_01','tombstone_raven_01','tombstone_mossy_01','grave_bell_01','bell_frame_01','crypt_sealed_01','old_well_01','fresh_grave_mound_01']
paths=[(O/(n+suffix+'.png')) if (O/(n+suffix+'.png')).exists() else (P/(n+suffix+'.png')) for n in ns for suffix in ['', '_base']]
result=subprocess.run(['python3',str(R/'scripts/tools/pixel_check.py'),*[str(p) for p in paths]],cwd=R,text=True,capture_output=True,check=True);(Q/'word_props_pixel_check.txt').write_text(result.stdout)
# Update current two metrics; accepted six entries remain byte-for-byte equal in data.
old_metrics=json.loads((P/'qc/word_props_metrics.json').read_text());current=json.loads(json.dumps(old_metrics))
for n in ['crypt_sealed_01','fresh_grave_mound_01']:
 for k in ['prop','base']:current[n][k]=metrics[n][k]
 current[n]['canvas']=details[n]['canvas'];current[n]['origin']=details[n]['origin'];bb=metrics[n]['prop']['bbox'];current[n]['visible_height_px']=bb[3]-bb[1];current[n]['source']='qc/word_props_revision_sources/'+details[n]['source'];current[n]['revision']=2
(Q/'word_props_metrics.json').write_text(json.dumps(current,indent=2))
manifest=json.loads((P/'props_manifest.json').read_text());before_manifest=json.loads(json.dumps(manifest))
for n in ['crypt_sealed_01','fresh_grave_mound_01']:
 a=manifest['items'][n];a['canvas']=details[n]['canvas'];a['origin']=details[n]['origin'];bb=metrics[n]['prop']['bbox'];a['visible_height_px']=bb[3]-bb[1];a['source_record']='qc/word_props_revision_sources/cleanup_index.json';a['revision']=2;a['status']='pending_user_review'
manifest['items']['crypt_sealed_01']['door_aperture']={'bbox_exclusive':details['crypt_sealed_01']['door_canvas_bbox_exclusive'],'size':[57,102],'measurement':'between inside lintel and threshold; frame exterior approx70x108; no sprite scaling'}
oldqa=(P/'qc/word_props_QA.md').read_text();m=details['fresh_grave_mound_01'];c=details['crypt_sealed_01'];box=c['prop_bbox'];rows=[]
for n in ['crypt_sealed_01','fresh_grave_mound_01']:
 for k in ['prop','base']:
  d=metrics[n][k];rows.append(f"| `{n}` {'立体' if k=='prop' else '底座'} | {d['size']} | {d['colors']} | {d['change']}% | {d['cyan']} | {d['alpha_ok']} |")
qa=f'''# §5 两件返修 — 2026-10-29

**本节为当前交付；下方首批记录保留作历史。** 用户已在游戏确认6件通过，这6件及其底座、主角/骷髅和动画本轮均不改。只替换墓室立体/底座、新坟底座，共3张运行PNG；铁锹PNG不写入、不换画布、不移动。

## 墓室：重新生成与还原

- 内置image_gen按新比例重新画整件，选定原图 `word_props_revision_sources/crypt2/01_generated_original.png`（1254×1254）。按真实可见方格边界取每格中心，得到206×206原生稿，未把旧版像素放大、拉伸或复制成更大的石块。记录见同目录 `grid.json`、`grid_check_1x.png`。第一稿门偏窄，保留在 `crypt/`，未交付。
- 最终画布 **256×256**，两层原点 **(128,256)**，原生稿整数放在 **(25,46)**。立体bbox半开区间 **{box}**，可见 **{box[2]-box[0]}×{box[3]-box[1]} px**；含脚边土石完整范围206×206。立体宽176，约180；没有为了凑200去横向放大。
- **净门洞57×102 px**：最终画布半开区间 **[94,109,151,211]**，包含x94～150、y109～210；从内侧门楣下到门槛。外铁框约70×108，仅作参考；不能拿框外尺寸冒充净门洞。96px主角放在门槛高度时，头顶留6px，达到需求100～110范围的下端；不是声称净门高110。
- 保留低山墙、两根方柱、两级阶、两道横铁条、锈链和大锁；门缝在既有凹槽处整理成暗铅/灰浆，非发亮描边。门楣只有残断凿痕；没有伪英文字母。石头、锈铁映射到原墓室已有色系，同一套旧化和左上受光。
- 看 `crypt_sealed_01_door_scale_2x.png`：左边保留完整门与旁边96px主角，右边把**相同主角原生图**放入门洞检查净高；淡色测量框只在QC，运行PNG没有框。另有改前/改后同地面对比及和主角并排6倍图。

## 新坟：只换土，铁锹逐像素不动

- 新生成的是**土堆本身**，没有画第二把铁锹。选定 `word_props_revision_sources/mound2/`；初稿像素太细，还原会过长，保留 `mound/` 作弃稿记录，没有缩成64px交付。
- 新原生土稿80×26（含滚到边外的土团，主体约70px长），仅作整数位移放到原128×96画布的 **(24,66)**，底边仍留4px。主土堆连为隆起的长条体积，顶部有压平面与受光的软土团；两侧和下沿是湿暗土，不是另画地面投影；少量土团滚出边缘。土全在 `_base`，立体层依然只有原铁锹。
- 土层完整不透明区实测：平均RGB **{tuple(m['mean_rgb'])}**，平均亮度 **{m['mean_luma']}**、亮度标准差 **{m['luma_std']}**。各通道最高 **{tuple(m['max_rgb'])}**；最亮像素亮度 **{m['max_luma']}**，低于碎石泥路参考(93,88,73)的 **{np.array([93,88,73])@np.array([.299,.587,.114]):.3f}**。比普通泥地更深，暖褐，非橙红；只调生成稿颜色，不用程序随机添土点。
- 铁锹原文件PNG SHA256修改前后相同：`{m['shovel_png_sha256']}`。RGBA SHA256同为 `{metrics['fresh_grave_mound_01']['prop']['rgba_sha256']}`。它的原点、坐标、透明像素和全部颜色都不改。
- `fresh_grave_mound_01_revision_compare_2x.png` 从需求指定的 `ground_paint_room_grass_01.png` 截同一处泥地/碎石路，旧坟和新坟放在相同位置；两边铁锹同图。截图原本是3倍显示，QC只取每3×3块中心还原原视口，再整数2倍预览，不对运行土堆做整体缩放。原生采样片和裁剪坐标留在本轮来源/metrics。

## 像素检查

| 文件/层 | 画布 | 颜色数 | 水平相邻换色 | 饱和青蓝 | Alpha0/255 |
|---|---|---:|---:|---:|---|
{chr(10).join(rows)}

全部透明RGB归零；没有抗锯齿、发光、可读字母、统一黑描边、镜像或旋转。脚本：`scripts/tools/pixel_check.py`；完整输出更新 `word_props_pixel_check.txt`。原图→原生还原→清理→6倍检查及精确提示词都在 `word_props_revision_sources/`，最终实测见 `word_props_revision_metrics.json`。

## 登记、保护与边界

- 覆盖3张运行PNG及两件相关QC；`props_manifest.json`只更新这两件的画布/原点/来源/返修信息，其他条目逐值相同。新坟尺寸保持原128×96，墓室改256×256。
- 修改前备份到 **`qc/backups/before_word_props_revision_20261029/`**，包含原3张/铁锹/manifest、两件旧QC与共用检查文件。旧源图和首批原生恢复图不动。
- 保护审计：6件已通过物件的12张PNG、铁锹PNG、原主角/骷髅及动画和其他已存素材逐文件哈希核对；结果见 `word_props_revision_preservation.json`。登记变化不冒称6件又需返修。
- 墓室176px宽略小于180～200参考，净门高102位于100～110的下端；完整土堆80px包含外围滚土，主体约70px。这些是实际数值，不虚写为190×190、110或64。
- 对比图是离线拼摆和尺寸核对，**尚未代替游戏内验收**；角色碰撞、积木组装、摆位由Claude处理，没有修改任何游戏场景。

两件一起交付，完成后停下，等待用户在游戏验收。

---

# 首批历史记录（下方旧尺寸/旧土色不代表本次返修）

'''
(Q/'word_props_QA.md').write_text(qa+oldqa)
# Copy only the3 runtime PNGs; NEVER write the accepted shovel or6passeditems.
runtime=['crypt_sealed_01.png','crypt_sealed_01_base.png','fresh_grave_mound_01_base.png']
for fn in runtime:shutil.copy2(O/fn,P/fn)
# QC overwrites must have been backed up at task start.
for p in Q.iterdir():
 d=P/'qc'/p.name
 if d.exists():assert (B/'qc'/p.name).exists(),('not backedup',str(d))
 if p.is_dir():shutil.copytree(p,d)
 else:shutil.copy2(p,d)
(P/'props_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Manifest protection: only two existing entries may change.
for k,v in before_manifest.items():
 if k=='items':
  for n,item in v.items():
   if n not in ['crypt_sealed_01','fresh_grave_mound_01']:assert manifest[k][n]==item
 else:assert manifest[k]==v
# Complete preexisting asset audit. Output is explicit about allowedQC changes.
before=json.loads((W/'before.json').read_text());changed=[];missing=[]
for rel,h in before.items():
 p=R/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(rel)
expected={'art/cemetery_v3/props/'+f for f in runtime+['props_manifest.json']}
expected|={'art/cemetery_v3/props/qc/'+p.name for p in Q.iterdir() if ('art/cemetery_v3/props/qc/'+p.name) in before}
assert set(changed)==expected,(changed,expected);assert not missing
for n in ['raven_ground_01','tombstone_raven_01','tombstone_mossy_01','grave_bell_01','bell_frame_01','old_well_01']:
 for suffix in ['','_base']:
  rel='art/cemetery_v3/props/'+n+suffix+'.png';assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==before[rel]
assert hashlib.sha256((P/'fresh_grave_mound_01.png').read_bytes()).hexdigest()==m['shovel_png_sha256']
for fn in runtime:assert (P/fn).read_bytes()==(O/fn).read_bytes()
(P/'qc/word_props_revision_preservation.json').write_text(json.dumps({'existing_files_checked':len(before),'changed_existing_files':changed,'missing_files':missing,'six_accepted_items_12_pngs_unchanged':True,'shovel_png_unchanged':True,'other_manifest_entries_unchanged':True,'installed_pngs_exact_match_measured':True},indent=2))
shutil.copy2(W/'publish.py',P/'qc/word_props_revision_sources/production/publish.py');print('Published3runtimePNGs; accepted6items and shovel unchanged. Files checked:',len(before))
