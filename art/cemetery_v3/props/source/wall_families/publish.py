from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,subprocess,sys,runpy
W=Path('/tmp/english-game-wall-families-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';Q=O/'qc';S=W/'staged';recipes=json.loads((W/'recipes.json').read_text());new=list(recipes);audit=json.loads((W/'interface_checks.json').read_text());oldmanifest=json.loads((O/'props_manifest.json').read_text());measure=runpy.run_path(str(R/'scripts/tools/pixel_check.py'))['measure']
# Add only new art files; protect all nine accepted pairs and priorQC.
for n in new:
 for suf in ['','_base']:
  dst=O/(n+suf+'.png');assert not dst.exists();shutil.copy2(S/dst.name,dst)
for name in ['wall_family_A_assembly_2x.png','wall_family_B_assembly_2x.png','wall_joints_8x.png']:
 assert not (Q/name).exists();shutil.copy2(W/name,Q/name)
T=Q/'wall_family_sources';T.mkdir(exist_ok=False);metrics={}
hero=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA')
for n,v in recipes.items():
 parent=v['parent'];d=T/n;d.mkdir()
 # No new generation: provenance is original parent generation plus accepted native parent.
 src=Q/'round2_sources'/parent/'01_generated_original.png';shutil.copy2(src,d/'01_inherited_parent_generated_original.png')
 for suf in ['','_base']:shutil.copy2(O/(parent+suf+'.png'),d/('02_parent'+suf+'.png'))
 pi=Image.open(O/(n+'.png')).convert('RGBA');bi=Image.open(O/(n+'_base.png')).convert('RGBA');combined=bi.copy();combined.alpha_composite(pi);combined.save(d/'03_derived_native.png')
 panel=Image.new('RGBA',(pi.width+110,max(160,pi.height+24)),'#403D3F');panel.alpha_composite(hero,(0,40));panel.alpha_composite(combined,(110,136-pi.height));panel.resize((panel.width*6,panel.height*6),Image.Resampling.NEAREST).save(d/'04_vs_hero_6x.png')
 layers=Image.new('RGBA',(pi.width*3,pi.height),'#403D3F')
 for k,im in enumerate([pi,bi,combined]):layers.alpha_composite(im,(pi.width*k,0))
 layers.resize((layers.width*2,layers.height*2),Image.Resampling.NEAREST).save(d/'layers_2x.png')
 (d/'derivation_recipe.json').write_text(json.dumps(v,indent=2))
 metrics[n]={}
 for key,suf in [('prop',''),('base','_base')]:
  path=O/(n+suf+'.png');im=Image.open(path);a=np.array(im);yy,xx=np.where(a[:,:,3]>0);m=measure(path);m.update({'visible_height':int(yy.max()-yy.min()+1),'origin':[im.width//2,im.height],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});metrics[n][key]=m;assert m['alpha_ok'] and m['cyan']==0
# Exact user checker on final paths; source labels explicitly mark inherited, not newly generated.
files=[O/(n+suf+'.png') for n in new for suf in ['','_base']];z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),*[str(p) for p in files]],capture_output=True,text=True);assert z.returncode==0,z.stdout;(Q/'pixel_check_wall_families.txt').write_text(z.stdout)
(Q/'wall_families_metrics.json').write_text(json.dumps({'assets':metrics,'interfaces':audit,'method':'Deterministic native source-pixel derivation; no new generation or raw drawing'},indent=2))
manifest=json.loads(json.dumps(oldmanifest));manifest['version']=3
for n,v in recipes.items():
 manifest['items'][n]={'prop':n+'.png','base':n+'_base.png','canvas':v['canvas'],'origin':v['origin'],'family':'A_rubble' if v['parent']=='low_wall_01' else 'B_ashlar','parent':v['parent'],'joins':v['joins'],'derivation_recipe':'qc/wall_family_sources/'+n+'/derivation_recipe.json'}
manifest['wall_families']={'A_rubble':{'complete':'low_wall_01','broken':'low_wall_rubble_broken_01','embedded_pillar':'low_wall_rubble_pillar_01','stride':148,'assembly_roots':[['low_wall_01',[120,140]],['low_wall_rubble_pillar_01',[268,140]],['low_wall_01',[416,140]],['low_wall_rubble_broken_01',[564,140]]]},'B_ashlar':{'complete':'low_wall_ashlar_01','broken':'low_wall_broken_01','gate_pillar':'wall_pillar_01','iron':'iron_fence_01','complete_stride':128,'masonry_assembly_roots':[['wall_pillar_01',[60,140]],['low_wall_ashlar_01',[131,140]],['low_wall_ashlar_01',[259,140]],['low_wall_broken_01',[387,140]]],'iron_assembly_roots':[['wall_pillar_01',[50,300]],['iron_fence_01',[131,300]],['wall_pillar_01',[202,300]]]},'do_not_mix_families_in_one_run':True}
assert all(manifest['items'][k]==v for k,v in oldmanifest['items'].items());(O/'props_manifest.json').write_text(json.dumps(manifest,indent=2))
# Source scripts copy pixels / masks only; not historical procedural drawing.
d=O/'source/wall_families';d.mkdir(exist_ok=False)
for f in ['build_wall_families.py','preview_check.py','publish.py']:shutil.copy2(W/f,d/f)
(d/'README.md').write_text('Native derivation evidence only. Uses approved A/B source pixels with integer crops, masks and translations. No imagegen calls, new paint or synthesized texture. Recipes in qc/wall_family_sources. Work paths are historical audit paths; do not execute over production.\n')
state=json.loads((W/'original_hashes.json').read_text());allowed={'art/cemetery_v3/props/props_manifest.json'};changed=[p for p,h in state.items() if p not in allowed and (not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h)];assert not changed,changed
(Q/'wall_families_protection.json').write_text(json.dumps({'protected_existing_art_files':len(state)-1,'changed_other_than_manifest':changed,'all_9_approved_pairs_unchanged':True,'backup':'/Users/mac/.codex/backups/English-Game/props-before-wall-families-20261025'},indent=2))
lines=['# 墓园墙体家族补件 QA','', '日期：2026-10-25。新增3件 / 6张PNG，A乱石与B条石分开配套；已通过9件全部保留。','', '## 方法与来源','', '按制作手册§5第8条，不单独生成墙、柱、断墙。此次没有新的image_gen调用，没有原生图形绘制、滤镜纹理、噪点、旋转、镜像或缩放。只用已通过的墙体像素裁取、删除、整数位移和重组。来源生成原图是上一批已有原图，作为继承来源放在 wall_family_sources/各物件/01_inherited_parent_generated_original.png；02为父件原生图，03为派生原生图，04为B1并排6倍。不能把继承原图当作本次另外生成的物件。','', '|新增物件|父件|具体改动|','|---|---|---|','|low_wall_rubble_broken_01|low_wall_01|左端及前89列不变，右半段按石块/灰缝删去上层；从同墙上取两块乱石碎块移到地面base，保留原左上受光。base中父件石色与湿泥色合并到已有颜色的50色子集，没有新颜色。|','|low_wall_rubble_pillar_01|low_wall_01|整段原墙只因画布增高而向下平移32px；中间叠砌同墙上层石块与灰缝，抬高约24px。下部砌层、底线与泥土仍为原墙像素，没有凸出基座；这是带左右墙肩的嵌柱墙段。|','|low_wall_ashlar_01|low_wall_broken_01|保留左侧完整前缀，按原高度35/49/70行继续顶盖、上层条石与下层条石；右端继承原完整前缀及相同接口列，base沿用原暗色泥草。|','', '## pixel_check.py','', '交付最终路径已运行 `python3 scripts/tools/pixel_check.py`；原样结果在 pixel_check_wall_families.txt。','', '|物件|画布 / 底边中心原点|立体可见高|立体 色数/换色|base 色数/换色|Alpha / 青蓝|','|---|---|---:|---|---|---|']
for n,v in metrics.items():
 p=v['prop'];b=v['base'];lines.append(f"|{n}|{p['size']} / ({p['origin'][0]}, {p['origin'][1]})|{p['visible_height']}|{p['colors']} / {p['change']}%|{b['colors']} / {b['change']}%|0/255 / 0|")
lines+=['','对照B1：44色、88%换色。父件调色板/光向不变：A为暖灰乱石与褐色灰缝，B为灰色条石、橄榄苔与地衣。新base继续使用压暗湿泥与枯草；乱石碎块的灰色受光面不是草的亮圈。','', '## 接口检查（含上下文）','', '- A断墙：前89列全部与原A一致，左拼接列x21与原A右列x168 RGBA相同，前三层灰缝保留原y位置，未只贴接口一列。','- A嵌柱：底部原生行81～127与原墙49～95完全相同；两侧接口各自与原墙对应列完全相同，世界高度按新增画布+32抵消。下部横向石块连续，柱子没有独立前凸台阶。','- B完整墙：完整前缀x21～42与原B逐像素相同；接口为x21与148，重复间距128px，两列RGBA相同；右端与原B断墙x21同高同像素。上层/下层灰缝保持同一y，不从A墙借石块。','- 两族的接缝对比见 wall_joints_8x.png；图中1～3为A三处接口，4为B完整重复，5为B完整接B断墙，6为B门柱与墙的覆盖接合，7～8为原门柱与铁栏。门柱处是遮盖接合，不将其误称为逐列平铺。','', '## 实际拼装参数','', '- A：四段根坐标(120,140)、(268,140)、(416,140)、(564,140)，X间隔148；其中嵌柱画布192×128，其余192×96，均按底边中心原点放置。不能按画布几何中心放。','- B：门柱(60,140)，完整墙(131,140)、(259,140)，断墙(387,140)。两块完整墙及完整→断墙X间隔128。门柱最后绘制，遮住墙端少量像素；该门柱本来就是独立门柱。','- B铁栏：门柱(50,300)、铁栏(131,300)、门柱(202,300)。铁栏仍用原素材，不镜像、不改像素。','- 拼装图2倍nearest；接口图8倍nearest。所有base先画在地面层，然后实体；不增加投影、灯光或Y-Sort代码。','', '## 保留与局限','', '- 原9件18张PNG及已有QC/原图均未修改；唯一更新的已有文件是已备份的 props_manifest.json，只添加3项和家族/拼装参数，旧9项内容保持原样。',f'- 除manifest外的 {len(state)-1} 个已有美术文件哈希不变。备份完整保留在 /Users/mac/.codex/backups/English-Game/props-before-wall-families-20261025/。','- 新条石墙的完整源片有限，延展处可见重复的地衣/顶盖纹样。它们是同材质同层高的延长，没有以噪点掩盖重复；在游戏内是否过于规律仍需用户验收。','- A嵌柱采用“整段墙带抬高中央砌层”的结构，左右墙肩是物件的一部分，不能当成窄独立柱再叠到完整墙前面，否则会重复画墙。拼装应以它替换一个148px墙段。','- 顶部断面由既有石头删裁得到，未额外生成破碎新材质；是否需要更重的崩裂造型留待游戏验收。','- 没有在Godot执行本轮验收；未修改场景、程序、旧素材，也未开始墓碑家族、小物件或骷髅。','', '## 拼装图','', '![A家族拼装]('+str(Q/'wall_family_A_assembly_2x.png')+')','', '![B家族拼装]('+str(Q/'wall_family_B_assembly_2x.png')+')','', '[接口8倍检查]('+str(Q/'wall_joints_8x.png')+')']
(Q/'wall_families_QA.md').write_text('\n'.join(lines)+'\n');print(z.stdout);print('published',new,'all existing preserved except additive manifest')
