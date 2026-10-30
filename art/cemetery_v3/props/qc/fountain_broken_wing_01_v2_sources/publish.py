from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,subprocess,importlib.util
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');P=R/'art/cemetery_v3/props';W=Path('/Users/mac/.codex/work/broken-wing-v2-20261030');O=W/'staged';Q=O/'qc';S=Q/'fountain_broken_wing_01_v2_sources';n='fountain_broken_wing_01';B=P/'qc/backups/before_broken_wing_v2_20261030';read=lambda p:np.array(Image.open(p).convert('RGBA'));L=np.array([.299,.587,.114]);m=json.loads((S/'edit_metrics.json').read_text());a=read(P/'fountain_dry_01.png');b=read(O/(n+'.png'));pieces=read(S/'pieces_layer.png');pm=pieces[:,:,3]>0;removed=np.array(Image.open(S/'removed_wing_mask.png'))>0;edge=np.array(Image.open(S/'stump_fracture_mask.png'))>0;diff=(a!=b).any(2)
assert int(diff.sum())==m['changed_pixels'];assert not(diff&~(pm|removed|edge)).any();assert set(np.unique(b[:,:,3]))<={0,255};assert not b[b[:,:,3]==0].any()
# Verify source pixel coordinates map to exactly one destination cell each,
# with only recorded integer row translations (and original-palette relight).
mp=m['pieces'][0];mapping=mp['source_to_piece_xy_map'];assert len({tuple(x[:2]) for x in mapping})==len(mapping);assert len({tuple(x[2:]) for x in mapping})==len(mapping);mp['actual_bbox_size']=[mp['bbox_exclusive'][2]-mp['bbox_exclusive'][0],mp['bbox_exclusive'][3]-mp['bbox_exclusive'][1]]
for p in m['pieces']:
 im=read(S/(p['name']+'.png'));mask=im[:,:,3]>0;box=p['bbox_exclusive'];p['mean_luma']=round(float((im[mask,:3]@L).mean()),3);p['max_luma']=round(float((im[mask,:3]@L).max()),3)
# The medium chunks onrim are records of object occlusion, not pool repaint.
face=a[78:94,114:130];assert (pieces[pm,:3]@L).max()<=(face[face[:,:,3]>0,:3]@L).max();assert np.array_equal(a[72:170,100:140],b[72:170,100:140])
sp=importlib.util.spec_from_file_location('pc',R/'scripts/tools/pixel_check.py');pc=importlib.util.module_from_spec(sp);sp.loader.exec_module(pc);ps=pc.measure(O/(n+'.png'));bs=pc.measure(P/(n+'_base.png'));assert ps['alpha_ok'] and bs['alpha_ok'] and not ps['cyan'] and not bs['cyan'];m.update(prop_pixel_check=ps,base_pixel_check=bs,source_pixel_mapping_one_to_one=True,final_png_sha256=hashlib.sha256((O/(n+'.png')).read_bytes()).hexdigest(),self_review='viewed full512x256 sidebyside at1x without labels; shoulder silhouette clearly shorter and large pale feathered fragment visible left-front of pedestal; user ingame acceptance still pending');(S/'edit_metrics.json').write_text(json.dumps(m,indent=2))
r=subprocess.run(['python3',str(R/'scripts/tools/pixel_check.py'),str(O/(n+'.png')),str(P/(n+'_base.png'))],cwd=R,text=True,capture_output=True,check=True);(Q/(n+'_pixel_check.txt')).write_text(r.stdout)
# Rebuild the2x contextualQC with hero onfront-right, leaving largeleft chunk
# unobscured. Runtime hero sprite itself is unchanged.
g=Image.open(R/'art/cemetery_v3/ground/base/ground_base_01.png').convert('RGBA');scene=Image.new('RGBA',(480,340))
for y in range(0,340,g.height):
 for x in range(0,480,g.width):scene.paste(g,(x,y))
im=Image.open(P/(n+'_base.png')).convert('RGBA');im.alpha_composite(Image.fromarray(b));scene.alpha_composite(im,(112,34));scene.alpha_composite(Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA'),(202,230));scene.resize((960,680),Image.Resampling.NEAREST).save(Q/(n+'_vs_hero_2x.png'))
# Keep all provenance and this revision's script separate from v1 sources.
shutil.copy2(W/'edit.py',S/'edit.py');shutil.copy2(W/'before.json',S/'before.json');shutil.copy2(P/'fountain_dry_01.png',S/'parent_fountain.png');shutil.copy2(P/'fountain_dry_01_base.png',S/'parent_base.png')
rows=[]
for p in m['pieces']:
 x0,y0,x1,y1=p['bbox_exclusive'];rows.append(f"| {p['name']} | {x1-x0}×{y1-y0} | x{x0}～{x1-1}，y{y0}～{y1-1} | {p['pixel_count']} | {'池沿' if p.get('on_rim') else '池底前方/底座前缘'} |")
oldqa=(P/'qc'/(n+'_QA.md')).read_text();qa=f'''# §3 第二版：肩部断翼与显眼的大块羽翼 — 2026-10-30

**当前交付以本节为准；第一版记录在下方保留。** 覆盖本体与相关QC，256×256、原点(128,256)不变。原版 `fountain_dry_01.png`、原版底座和本变体底座都不改。

##1倍自查

新增 `fountain_broken_wing_01_1x_compare.png`，**512×256原生并排，左原版、右返修版，无箭头/说明文字、无放大**。已实际查看这张1倍图：右侧天使肩背只剩小茬，长翼的外轮廓消失；底座左前方的大片浅色羽毛状断翼能直接看见。大块的第一稿过暗、靠底座右侧时仍混在一起，已调整成最终前方位置和更宽的羽毛选区，没有用6倍特写代替这项自查。能否让未被告知的玩家主动发现仍由用户在游戏判断，未宣称游戏内通过。

##肩部断点

原可见翼约y84～160，高约77px。新断口末端在y104～109，只留约20～25px的小茬，约原长1/4～1/3。移除原翼 **{m['removed_wing_pixels']}** 个像素位置；新鲜断面选区48px，使用原图较浅石色，在肩侧形成高低不同的断茬，不画发光裂纹。断下后露出的空隙/池壁按原池子底稿、原坐标恢复，不重新猜画背景。

断翼/新断面大致x140～156、y101～162。头脸、胸、手、衣褶等保护区x100～139、y72～169逐像素一致；余下所有不在碎块/断翼蒙版内的像素不同数量为0。碎块挡到的底座前缘和池沿是本次需求明确允许的物件遮挡，并非改画池沿本身。

##1大块+4块中等碎片

主块使用原翼x140～156、y107～132的宽羽毛部分，以每一原生行向右整数移 `floor(y/2)` px 重拼倾角。每个源像素对应一个目标像素，没有调用旋转、镜像或插值缩放；映射表逐像素保存在 `edit_metrics.json`。从原色表整理新鲜断面和羽毛沟槽明暗，保持原羽毛纹理分组。

最终主块包围盒 **27×26px**（26px长、横向错位后27px宽），比“18～26”参考宽1px；位于池底前方、底座左前缘，底端在y203，未被前池沿遮住。保留更宽的羽毛面是为了1倍能认出来，没有把旧翼等比放大。共有384个实体像素，明显大于第一版的9×6/6×9小片。

再放4块约5～10px的中等碎片，2块在池底前半部，2块在亮池沿上；第一版细小碎屑不继续堆叠，避免拿数量充可读性。两块池沿碎片用本身较暗的断侧面与浅断面区分于亮石面，不加投影或光效。

| 碎块 | 实际包围盒 | 位置（含首尾） | 实体像素 | 落点 |
|---|---|---|---:|---|
{chr(10).join(rows)}

##最终像素检查

- 新增颜色 **0种**，全部来自原喷泉色表；本体 **{ps['colors']}色 / {ps['change']}%** 水平相邻换色；Alpha仅0/255，透明RGB归零，饱和青蓝0。
- 底座为第一版已经字节复制的原版底座，本轮**未写入**：{bs['colors']}色 / {bs['change']}%，其数值不为凑密度而改动。
- 相对完整原版，改变 **{m['changed_pixels']}** 个RGBA像素，bbox含首尾 **{m['changed_bbox_inclusive']}**；许可蒙版以外改变 **0**。实际变化蒙版、残翼蒙版、碎块独立PNG和源→目标坐标映射在 `fountain_broken_wing_01_v2_sources/`。
- `pixel_check.py`输出更新到 `fountain_broken_wing_01_pixel_check.txt`；本体PNG哈希 `{m['final_png_sha256']}`。
- 不重新生成整件；本轮完全按需求以原图原生像素局部选择、重拼和原色表整理，没有程序随机生纹理。角色及原喷泉不改变大小或方向。

##交付与保护

1倍比较图之外，6倍并排图和2倍主角池前图都换成第二版。2倍检查图让主角站池前偏右，避免把左前的大碎翼挡住。脚本/来源、指标与说明均保留；第一版来源目录不覆盖。

第一版本体按用户说明已在git，不另做本体备份；修改前manifest和旧QC另外留在 `qc/backups/before_broken_wing_v2_20261030/`。manifest只更新碎翼变体的返修信息，原喷泉项和其他条目逐值相同。父图SHA256仍为 `{m['original_fountain_png_sha256']}`；原底座及新变体底座仍同为 `{m['original_base_png_sha256']}`。完整保护审计见 `fountain_broken_wing_01_v2_preservation.json`。

大块经过逐行重拼，不能声称是原翼一整块未经处理地平移；这是为表现落地倾角采用的原生像素重组。其余材质与未遮挡区域保持原样。离线1倍检查通过我的视觉自查，游戏内的识别效果仍等用户验收。

完成后停下，等用户验收。

---

# 第一版历史记录（下方半截翼/7小片描述不代表当前版本）

''';(Q/(n+'_QA.md')).write_text(qa+oldqa)
manifest=json.loads((P/'props_manifest.json').read_text());prior=json.loads(json.dumps(manifest));item=manifest['items'][n];item.update(source_record='qc/'+n+'_v2_sources/edit_metrics.json',revision=2,fallen_fragments=5,major_wing_fragment_bbox=[92,178,119,204],major_wing_fragment_size=[27,26],rim_fragments=2,retained_wing_height_px=[20,25],status='pending_user_review')
# Exactly one runtime sprite overwritten; base and all sourceparents untouched.
shutil.copy2(O/(n+'.png'),P/(n+'.png'))
for p in Q.iterdir():
 dst=P/'qc'/p.name
 if dst.exists():assert (B/'qc'/p.name).exists(),('missingQCbackup',dst)
 if p.is_dir():shutil.copytree(p,dst)
 else:shutil.copy2(p,dst)
(P/'props_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for k,v in prior.items():
 if k=='items':
  for name,value in v.items():
   if name!=n:assert manifest[k][name]==value
 else:assert manifest[k]==v
before=json.loads((W/'before.json').read_text());changed=[];missing=[]
for rel,h in before.items():
 p=R/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(rel)
expected={'art/cemetery_v3/props/'+n+'.png','art/cemetery_v3/props/props_manifest.json'};expected|={'art/cemetery_v3/props/qc/'+p.name for p in Q.iterdir() if 'art/cemetery_v3/props/qc/'+p.name in before};assert set(changed)==expected,(changed,expected);assert not missing
assert hashlib.sha256((P/'fountain_dry_01.png').read_bytes()).hexdigest()==m['original_fountain_png_sha256'];assert hashlib.sha256((P/(n+'_base.png')).read_bytes()).hexdigest()==m['original_base_png_sha256'];assert (P/(n+'.png')).read_bytes()==(O/(n+'.png')).read_bytes()
(P/'qc'/(n+'_v2_preservation.json')).write_text(json.dumps({'preexisting_files_checked':len(before),'changed_existing_files':changed,'missing_files':missing,'original_fountain_and_base_unchanged':True,'variant_base_unchanged':True,'other_manifest_items_unchanged':True,'outside_allowed_masks_changed':0,'final_sprite_exact_measured_bytes':True},indent=2));shutil.copy2(W/'publish.py',P/'qc'/(n+'_v2_sources')/'publish.py');print('Publishedv2. Protected',len(before),'preexisting files; onlyvariant/QA/manifest updated.')
