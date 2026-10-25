from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,runpy,subprocess,sys,math
W=Path('/tmp/english-game-props-complete-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';Q=O/'qc';S=W/'staged';G=json.loads((W/'generation.json').read_text());C=json.loads((W/'cleanup_notes.json').read_text());A=json.loads((W/'assembly_mapping.json').read_text());J=json.loads((W/'join_metadata.json').read_text())
names=['tombstone_upright_01','tombstone_upright_02','tombstone_cross_01','open_grave_01','grave_lid_01','low_wall_01','low_wall_broken_01','wall_pillar_01','iron_fence_01']
# Existing production is recoverable both in requested round1 backup and separate snapshot.
assert (Q/'backups/round1/tombstone_upright_01.png').exists();assert Path('/Users/mac/.codex/backups/English-Game/props-before-round2-promotion-20261025').exists()
for n in names:
 for suf in ['','_base']:shutil.copy2(S/(n+suf+'.png'),O/(n+suf+'.png'))
# Full provenance for each of the eight generated standalone objects.
T=Q/'round2_sources';T.mkdir(exist_ok=False)
for n,p in G['raw'].items():
 d=T/n;d.mkdir();shutil.copy2(p,d/'01_generated_original.png');shutil.copy2(W/'restored'/(n+'.png'),d/'02_restored_cells.png');shutil.copy2(W/'restored'/(n+'_grid_check.png'),d/'grid_check_1x.png');shutil.copy2(W/'restored'/(n+'_grid.json'),d/'grid_boundaries.json');shutil.copy2(S/(n+'_combined_cells.png'),d/'03_cleaned_native_geometry.png')
# Accepted first stone retained as its already delivered trial; no re-generation.
H=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA')
def combined(n):
 a=Image.open(O/(n+'_base.png')).convert('RGBA');a.alpha_composite(Image.open(O/(n+'.png')).convert('RGBA'));return a

def place(panel,n,x,y,base=True,prop=True,scale=1):
 for suf in (['_base'] if base else [])+([''] if prop else []):
  a=Image.open(O/(n+suf+'.png')).convert('RGBA')
  if scale!=1:a=a.resize((a.width*scale,a.height*scale),Image.Resampling.NEAREST)
  panel.alpha_composite(a,(x-a.width//2,y-a.height))
# Every object alongside same unmodified B1, exactly1x and2x/6x nearest.
comp=Image.new('RGBA',(840,480),'#403D3F');dr=ImageDraw.Draw(comp)
for k,n in enumerate(names):
 x=k%3*280;y=k//3*160;comp.alpha_composite(H,(x-8,y+40));place(comp,n,x+172,y+136);dr.text((x+3,y+143),n,fill='#BEB7A9')
comp.convert('RGB').save(Q/'props_with_hero_1x.png')
for fac,file in [(2,'props_with_hero_2x.png'),(6,'detail_vs_hero_6x.png')]:comp.resize((comp.width*fac,comp.height*fac),Image.Resampling.NEAREST).convert('RGB').save(Q/file)
# Per-object panels, shared origin; native transparent intermediate besidehero6x.
for n in names:
 d=T/n;d.mkdir(exist_ok=True);im=combined(n);im.save(d/'04_final_native_with_base.png');p=Image.new('RGBA',(max(240,im.width+110),160),'#403D3F');p.alpha_composite(H,(0,40));p.alpha_composite(im,(p.width-im.width,136-im.height));p.resize((p.width*6,960),Image.Resampling.NEAREST).save(d/'05_vs_hero_6x.png')
# Atlas of 9 props8x, no resampling of asset production.
at=Image.new('RGBA',(720,480),'#403D3F');ad=ImageDraw.Draw(at)
for k,n in enumerate(names):
 x=k%3*240;y=k//3*160;place(at,n,x+120,y+137);ad.text((x+4,y+143),n,fill='#BEB7A9')
at.resize((5760,3840),Image.Resampling.NEAREST).convert('RGB').save(Q/'props_8x.png')
# Layer audit, each row shows prop / base / overlay.
lay=Image.new('RGBA',(720,9*160),'#403D3F');ld=ImageDraw.Draw(lay)
for k,n in enumerate(names):
 for col,(ba,pr) in enumerate([(False,True),(True,False),(True,True)]):place(lay,n,col*240+120,k*160+137,ba,pr)
 ld.text((3,k*160+143),n,fill='#BEB7A9')
lay.resize((1440,2880),Image.Resampling.NEAREST).convert('RGB').save(Q/'props_layers_2x.png')
# Source background is never resampled; three full-size northstar panels.
bg=Image.open(R/'art/pixel_test/source/graveyard_P_reference.png').convert('RGBA');panels=[]
layouts=[ [('tombstone_upright_01',940,700),('tombstone_upright_02',1060,1030),('tombstone_cross_01',300,1160)], [('open_grave_01',850,1030),('grave_lid_01',400,1210)], [('low_wall_01',850,650),('wall_pillar_01',1090,650),('low_wall_broken_01',925,985),('iron_fence_01',1000,1210)] ]
for k,layout in enumerate(layouts):
 p=bg.copy()
 for n,x,y in layout:place(p,n,x,y,scale=3)
 hx,hy=([(590,1210),(1080,1210),(550,1210)])[k];p.alpha_composite(H.resize((288,288),Image.Resampling.NEAREST),(hx-144,hy-288));panels.append(p)
ns=Image.new('RGBA',(3762,1290),'#292729');nd=ImageDraw.Draw(ns)
for k,p in enumerate(panels):ns.alpha_composite(p,(k*1254,36));nd.text((k*1254+10,12),['A  Tombstones / cross','B  Human-length grave and slab','C  Wall / broken wall / pillar / iron'][k]+'    New sprites 3x NEAREST',fill='#BEB7A9')
ns.convert('RGB').save(Q/'props_on_northstar.png')
# Repeat and mount tests. Iron mounted on wall deliberately omits iron earth base.
join=Image.new('RGBA',(660,360),'#403D3F');jd=ImageDraw.Draw(join)
place(join,'low_wall_01',140,130);place(join,'low_wall_01',288,130);place(join,'low_wall_broken_01',428,130);place(join,'wall_pillar_01',65,130);jd.text((4,139),'Wall stride148 + broken join / shared end profile',fill='#BEB7A9')
place(join,'iron_fence_01',110,345);place(join,'iron_fence_01',242,345);jd.text((4,351),'Iron stride132',fill='#BEB7A9')
place(join,'low_wall_01',520,345);place(join,'iron_fence_01',513,301,False,True);place(join,'wall_pillar_01',445,345);place(join,'wall_pillar_01',593,345);jd.text((400,351),'Iron mount offsetY -44',fill='#BEB7A9')
join.resize((2640,1440),Image.Resampling.NEAREST).convert('RGB').save(Q/'wall_join_test_4x.png')
# Special first stone before/after: body strictly same; only base palette changes.
old=Image.open(Q/'revision1_tombstone_trial/03_tombstone_with_base_native.png').convert('RGBA');new=combined('tombstone_upright_01');p=Image.new('RGBA',(232,132),'#403D3F');p.alpha_composite(old,(8,0));p.alpha_composite(new,(124,0));ImageDraw.Draw(p).text((8,118),'Accepted trial    Darker base',fill='#BEB7A9');p.resize((1392,792),Image.Resampling.NEAREST).save(Q/'tombstone_01_base_darkening_6x.png')
assert np.array_equal(np.array(Image.open(O/'tombstone_upright_01.png')),np.array(Image.open(Q/'revision1_tombstone_trial/tombstone_upright_01.png')))
measure=runpy.run_path(str(R/'scripts/tools/pixel_check.py'))['measure'];M={};manifest={'version':2,'origin':'bottom_center','no_auto_trim':True,'base_layer':'ground decal / no Y-sort / below actors','prop_layer':'Y-sort / occluding','items':{}}
for n in names:
 M[n]={}
 for suf,key in [('','prop'),('_base','base')]:
  p=O/(n+suf+'.png');im=Image.open(p).convert('RGBA');a=np.array(im);yy,xx=np.where(a[:,:,3]>0);m=measure(p);m.update({'visible_height':int(yy.max()-yy.min()+1),'opaque_bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'origin':[im.width//2,im.height],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});assert m['alpha_ok'] and m['cyan']==0;M[n][key]=m
 manifest['items'][n]={'prop':n+'.png','base':n+'_base.png','canvas':list(im.size),'origin':[im.width//2,im.height],'join':J.get(n),'native_edit':C[n].get('native_geometry_edit')}
# Manually read endpoints on final source-cell geometry. Annotated measurement proof.
measurements={'open_grave_01':{'native_geometry_edge_points':[[64,13],[161,65]],'kind':'long inner opening edge'},'grave_lid_01':{'native_geometry_edge_points':[[10,18],[93,98]],'kind':'long stone slab edge'}}
for n,v in measurements.items():
 v['length_px']=float(math.dist(*v['native_geometry_edge_points']));im=Image.open(S/(n+'_combined_cells.png')).convert('RGBA');p=Image.new('RGBA',im.size,'#403D3F');p.alpha_composite(im);d=ImageDraw.Draw(p);pts=[tuple(x) for x in v['native_geometry_edge_points']];d.line(pts,fill='#E9AB80',width=1)
 for x,y in pts:d.rectangle((x-1,y-1,x+1,y+1),outline='white')
 p.resize((p.width*6,p.height*6),Image.Resampling.NEAREST).save(Q/(n+'_length_measure_6x.png'))
# Run exact requested checker once for EACH deliveryPNG; one combined report and per-item reports.
logs=[]
for n in names:
 cmd=[sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),str(O/(n+'.png')),str(O/(n+'_base.png'))];z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stdout+z.stderr;(T/n/'pixel_check.txt').write_text(z.stdout);logs.append(z.stdout)
(Q/'pixel_check_round2.txt').write_text('\n'.join(logs));(Q/'props_metrics.json').write_text(json.dumps({'user_checker':'scripts/tools/pixel_check.py','assets':M,'joins':J,'length_measurements':measurements},indent=2));(O/'props_manifest.json').write_text(json.dumps(manifest,indent=2))
# Source method and exact prompt records replace outdated round1 procedural workflow.
(Q/'props_prompts.json').write_text(json.dumps({'tool':'built-in image_gen','pipeline':'docs/PIXEL_ASSET_PIPELINE.md','generation':G,'cleanup':C,'assembly':A,'joins':J,'note':'Native cells recovered by actual painted-boundary detection, centers only; no whole-image resize. Native integer edits and palette maps recorded, no procedural new artwork.'},ensure_ascii=False,indent=2))
# New source helpers are non-production recipes; round1 procedural authoring scripts retained as history.
D=O/'source/round2';D.mkdir(exist_ok=True)
for f in ['recover_all.py','clean_and_split.py','join_and_check.py','publish_round2.py']:shutil.copy2(W/f,D/f)
(D/'README.md').write_text('Round2 pipeline evidence. These recipes record the working run, with original working paths for audit; do not bulk-run against production. Raw images / grid lists / native intermediates are in qc/round2_sources. Legacy source/native_pixel_master.py and native_pixel_refinement.py are ROUND1 HISTORY ONLY, not the current source for production.\n')
# Protect outsideart before and after all mutations.
state=json.loads((W/'protected_hashes.json').read_text());ignored_os_metadata=[p for p in state if Path(p).name=='.DS_Store'];state={p:h for p,h in state.items() if Path(p).name!='.DS_Store'};changed=[p for p,h in state.items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h];assert not changed,changed
(Q/'protected_assets_hashes.json').write_text(json.dumps({'outside_art_files_checked':len(state),'changed':changed,'ignored_os_metadata':ignored_os_metadata,'accepted_trial_tombstone_body_unchanged':True,'round1_backup':'backups/round1','before_promotion_backup':'/Users/mac/.codex/backups/English-Game/props-before-round2-promotion-20261025'},indent=2))
# QA concise but complete tables, exact checker numbers and material roles.
lines=['# 墓园物件第一批 · Round2 QA','', '日期：2026-10-25。9件正式物件 / 18张透明PNG。已通过墓碑01转正式，其余8件完成，等待本轮游戏验收。','', '## 流程','', '已读 docs/PIXEL_ASSET_PIPELINE.md 和 CEMETERY_PROPS_REVISION_1.md。使用内置image_gen逐件生成大方块像素风，按源稿重复边界推断真实格，逐格取中心点还原为一个原生像素。没有整图resize、非整数缩放、平滑、均值取色、程序新增纹理或随机噪点。只有QC预览使用整数nearest放大。','', '源稿的格宽不完全均一：以相关峰确定每件主周期，再沿边界追踪；和已验收墓碑采用同一方法。算法推断仍有误差，不能声称恢复生成器未提供的精确原生索引。每件原图、格边列表、网格核对截图、还原图、最终原生图与6倍对比均保留在 `round2_sources/物件名/`。','', '生成时未能稳定得到目标尺寸的候选已弃用。墓穴与盖板最终使用最初的明确像素格源稿，在原生层去掉一段中间长度、远端按整数向量平移；墙柱去掉一整层中部石砌（43～62行）。它们没有缩放、旋转、插值或创造新纹理。具体向量/行范围见 props_prompts.json。原生切接处已肉眼检查，是否能在游戏里觉察重复/接痕仍待验收。','', '## 自查结果','', '交付前逐件运行用户指定的 `python3 scripts/tools/pixel_check.py`；对照固定为 `hero_B1_front_straight.png`。完整原样输出：`pixel_check_round2.txt`；每件同目录也有pixel_check.txt。该脚本换色比例四舍五入为整数。','', '|物件|画布|原点|立体可见高|立体 色数 / 换色%|底座 色数 / 换色%|Alpha / 青蓝|','|---|---|---|---:|---:|---:|---|']
for n,v in M.items():
 p=v['prop'];b=v['base'];lines.append(f"|{n}|{p['size']}|({p['origin'][0]}, {p['origin'][1]})|{p['visible_height']}|{p['colors']} / {p['change']}%|{b['colors']} / {b['change']}%|0/255 / 0|")
lines+=['','主角对照：44色，88%换色。墓碑78/74、十字95、墙54、铁栏67px均在需求范围。柱78px比墙高24px。墓穴与盖板的可见高属于斜向占地，不是直立物件身高。','', f"- 墓穴坑口长边：原生几何坐标(64,13)→(161,65)，约 **{measurements['open_grave_01']['length_px']:.1f}px**，长于主角96px。",f"- 盖板长边：(10,18)→(93,98)，约 **{measurements['grave_lid_01']['length_px']:.1f}px**；与坑口长边相配，略留边沿。",'- 两项量测图分别为 open_grave_01_length_measure_6x.png、grave_lid_01_length_measure_6x.png。透视下不同边长读数有1～3px的端点选择误差。','', '## 枯草压暗 / 第一块转正式','', '墓碑01碑身与已验收试样RGBA逐像素完全相同。只替换base的暖色草/湿泥调色板：高亮暖色降到原亮度约58%，较暗暖色约70%，再略降饱和度；不改变草形状和Alpha，灰色石屑亮度保留。其余8件底座同样按材质暖色调暗，没有把所有材质一起变黑。对比：tombstone_01_base_darkening_6x.png。','', '|底座|受影响像素|暖色平均灰度 前→后|','|---|---:|---:|']
for n in names:
 v=C[n]['ground_darkening'];lines.append(f"|{n}|{v['changed_pixels']}|{v['affected_mean_luma_before']:.1f} → {v['affected_mean_luma_after']:.1f}|")
lines+=['','## 小色块的含义','', '- 墓碑/十字/盖板：灰石面有近灰冷暖差；左上破损的暖灰边是裸露石芯；深灰线为裂纹和凹刻；土褐纵纹为雨水与矿物沉积；灰米色附斑为地衣；橄榄苔沿破口与脚部积水面生长。没有语言青蓝、光晕或glitch。','- 墓穴：石沿、近侧石墙为立体层；凹陷坑底与湿土壁归地面base层；深色不是地面投影。石沿之外的压草/翻土同为base。','- 盖板：整个石板连厚度参与遮挡；其下湿土、松散碎石和草是base。','- 墙/柱：石砌错缝的深线是残损砂浆，块内浅斑是地衣、深斑是湿石，顶边亮色仅受光断面；根脚的湿泥和枯草埋住接触边。','- 铁栏：灰黑色铁芯、暖灰崩落边、局部棕色锈蚀、扣件和锻铁菱花组成细节；镂空背景清理为全透明。','', '## 原点与拼接','', '- 各prop/base画布相同，原点均底边中心，不自动裁切透明留白。base永远绘制在角色脚下，不加入Y-Sort。素材没有固定地面投影；Godot负责接触阴影。','- 完整墙：原生重复间距148px；画布内有效拼接列x=21与168，RGBA完全一致。','- 残墙：画布左拼接列x=21，与完整墙左列RGBA一致。连接时按实际列对齐，不把192px画布宽当作重复间距；见 props_manifest.json。','- 铁栏：原生重复间距132px；拼接列x=12与143，RGBA完全一致。不能镜像物件。','- 铁栏架墙上：参考offsetY=-44px，不画铁栏独立落地base；独立铁栏则配自身base。拼接/架装示意见 wall_join_test_4x.png。','', '## 保留与限制','', '- 第一版按原要求保留在 qc/backups/round1/；本次覆盖前另完整备份到 `/Users/mac/.codex/backups/English-Game/props-before-round2-promotion-20261025/`。已验收试样目录保持原样。',f'- props以外 {len(state)} 个已有美术文件逐文件哈希零变化；主角、动画、design、style_test、cemetery_pixel_v1均未改。没有改Godot场景、代码、需求文档或知识库。','- 残墙换色74%，低于主角88%，保留石头较大的破裂断面，没有为凑数加噪点；这件是否仍显得偏平，需游戏验收。','- 第一块碑身仍保留了用户通过的暖灰/橄榄色；压暗只影响地面base，所以碑身脚部附着苔藓保留原色。新石材也偏暖灰，整体冷暖是否合适以游戏判断。','- 源格不严格等宽，边界推断和原生切接均已留证；数字不替代风格验收。','- 旧 source/native_pixel_master.py、native_pixel_refinement.py 保留为Round1历史，不能重新运行覆盖当前素材。当前流程证据位于 source/round2/ 与 qc/round2_sources/。','- 本轮尚未由用户在Godot里验收。没有开始墓碑家族或小物件第二批。','', '## 预览','', '![与B1并排2倍]('+str(Q/'props_with_hero_2x.png')+')','', '[6倍精致程度对比]('+str(Q/'detail_vs_hero_6x.png')+') · [8倍像素检查]('+str(Q/'props_8x.png')+') · [北极星叠放]('+str(Q/'props_on_northstar.png')+')']
(Q/'props_QA.md').write_text('\n'.join(lines)+'\n')
print('Published 18 PNGs; native geometry lengths',measurements,'protected',len(state))
