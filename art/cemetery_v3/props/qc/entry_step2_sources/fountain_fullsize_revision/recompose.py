from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,zipfile,subprocess,sys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');P=R/'art/cemetery_v3/props';Q=P/'qc';S=Q/'entry_step2_sources';O=S/'fountain_fullsize_revision';O.mkdir(exist_ok=True)
protected={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in P.glob('*.png') if not p.name.startswith('fountain_dry_01')}
files=[P/'fountain_dry_01.png',P/'fountain_dry_01_base.png',P/'props_manifest.json',Q/'entry_props_QA.md']+[p for p in Q.glob('fountain_dry_01*') if p.is_file()]
bak=Q/'backups/fountain_before_fullsize_20261028.zip'
with zipfile.ZipFile(bak,'x',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(P))
old=json.loads((S/'fountain_dry_01/cleanup.json').read_text());pal=np.array(old['palette_rgb'],np.int32)
def load(p):return np.array(Image.open(p).convert('RGBA'))
def prepare(a):
 a=a.copy();c=a[:,:,:3].astype(int);a[(c[:,:,0]-c[:,:,1]>22)&(c[:,:,2]-c[:,:,1]>22)]=0
 a[:,:,3]=np.where(a[:,:,3]>0,255,0);fg=a[:,:,3]>0;colors=a[fg,:3].astype(int);ix=((colors[:,None]-pal[None])**2).sum(2).argmin(1);a[fg,:3]=pal[ix];return Image.fromarray(a)
pool=prepare(load(S/'fountain_pool/02_restored_cells.png'));angel=prepare(load(S/'fountain_angel/02_restored_cells.png'));assert pool.size==(194,119) and angel.size==(57,138)
pool.save(O/'pool_full_native.png');angel.save(O/'angel_full_native.png')
# Entire sources stay intact; foreground is an occlusion mask, not deleted source rows.
px,py=31,129;ax,ay=100,71
prop=Image.new('RGBA',(256,256));prop.alpha_composite(pool,(px,py));prop.alpha_composite(angel,(ax,ay))
front=np.array(pool);front[:78]=0;foreground=Image.fromarray(front);prop.alpha_composite(foreground,(px,py));foreground.save(O/'pool_foreground_occlusion.png')
base=Image.new('RGBA',(256,256))
for name,xy in [('decal_wet_mud_02.png',(32,211)),('decal_wet_mud_01.png',(160,222))]:
 im=Image.open(R/'art/cemetery_v3/ground/decals'/name).convert('RGBA');base.alpha_composite(im,xy)
# Reuse the accepted muddy base palette; no recoloring the statue or basin.
oldbase=load(P/'fountain_dry_01_base.png');gp=np.unique(oldbase[oldbase[:,:,3]>0,:3],axis=0).astype(int)
b=np.array(base);fg=b[:,:,3]>0;rgb=b[fg,:3].astype(int);ix=((rgb[:,None]-gp[None])**2).sum(2).argmin(1);b[fg,:3]=gp[ix];b[np.array(prop)[:,:,3]>0]=0;base=Image.fromarray(b)
prop.save(P/'fountain_dry_01.png');base.save(P/'fountain_dry_01_base.png');combined=base.copy();combined.alpha_composite(prop);combined.save(Q/'fountain_dry_01_native.png');combined.save(O/'fullsize_composite_native.png')
for scale in [6,8]:combined.resize((256*scale,256*scale),Image.Resampling.NEAREST).save(Q/f'fountain_dry_01_{scale}x.png')
# Comparison at true native scale on the actual approved ground.
ground=load(R/'art/cemetery_v3/ground/base/ground_base_01.png');scene=Image.fromarray(np.tile(ground,(3,3,1))[:320,:480]);scene.alpha_composite(combined,(112,24))
for path,xy in [('art/character_design/hero_B1_front_straight.png',(32,184)),('art/character_design/enemies/skeleton/skeleton_B.png',(380,184))]:scene.alpha_composite(Image.open(R/path).convert('RGBA'),xy)
for scale in [1,2,6]:scene.resize((480*scale,320*scale),Image.Resampling.NEAREST).save(Q/f'fountain_dry_01_vs_hero_skeleton_{scale}x.png')
combined.resize((1536,1536),Image.Resampling.NEAREST).save(O/'fullsize_composite_6x.png')
# Exact shape completeness / no shifted row maps.
ref=Image.new('RGBA',(256,256));ref.alpha_composite(pool,(px,py));ref.alpha_composite(angel,(ax,ay));ref.alpha_composite(foreground,(px,py));assert np.array_equal(np.array(ref),np.array(prop))
a=np.array(combined);fg=a[:,:,3]>0;rgb=a[fg,:3];pairs=fg[:,1:]&fg[:,:-1];change=np.any(a[:,1:,:3]!=a[:,:-1,:3],2)
record={'canvas':[256,256],'origin':[128,256],'pool_source':'../fountain_pool/02_restored_cells.png','angel_source':'../fountain_angel/02_restored_cells.png','pool_source_size':[194,119],'angel_source_size':[57,138],'pool_deleted_rows':[],'pool_deleted_columns':[],'angel_deleted_rows':[],'angel_deleted_columns':[],'pool_placement':[px,py],'angel_placement':[ax,ay],'front_rim_occlusion':'Reapply unchanged pool pixels for source y>=78 over statue; both complete source images retained. No slicing and reconnecting.','palette':'Nearest existing accepted fountain48-color palette; unchanged palette, no new art colors. Magenta contamination removed as before.','integer_translation_only':True,'prop_bbox':prop.getbbox(),'base_bbox':base.getbbox(),'alpha_values':np.unique(a[:,:,3]).tolist(),'combined_colors':len(np.unique(rgb,axis=0)),'horizontal_change_pct':float(change[pairs].mean()*100),'no_rows_columns_deleted':True,'protected_other_props':len(protected),'protected_other_props_unchanged':all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in protected.items())}
assert record['protected_other_props_unchanged'];(O/'composition.json').write_text(json.dumps(record,indent=2)+'\n');(O/'protected_other_props.json').write_text(json.dumps(protected,indent=2)+'\n')
m=json.loads((P/'props_manifest.json').read_text());item=m['items']['fountain_dry_01'];item.update(canvas=[256,256],origin=[128,256],visible_height_px=prop.getbbox()[3]-prop.getbbox()[1],pool_width_px=194,angel_with_pedestal_height_px=138,source_record='qc/entry_step2_sources/fountain_fullsize_revision/composition.json',status='accepted_D-060_design_fullsize_recomposition_pending_review');(P/'props_manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
result=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(P/'fountain_dry_01.png'),str(P/'fountain_dry_01_base.png')],capture_output=True,text=True,check=True,cwd=R);(Q/'fountain_dry_01_fullsize_pixel_check.txt').write_text(result.stdout)
qa='''\n\n## §7 喷泉原尺寸重新合成（2026-10-28）\n\n9件外观已通过 D-060；本次只修喷泉删行形成的横切。**没有删任何行列**：完整池子194×119、完整天使57×138。画布256×256，原点(128,256)，保持底边中心和底部透明留白。池子整数位置(31,129)，天使(100,71)；重新覆上原池子前沿像素遮住底座最下沿，这属于自然遮挡，没有压缩、裁断、拉伸或拼接上下半池。两张完整原生图及遮挡层见 entry_step2_sources/fountain_fullsize_revision/。\n\n沿用已通过喷泉的48色石材调色板（原还原稿按既有色表归并，清理品红污染），没有重新设计天使、池子或新增纹理。泥贴花按正式地面颜色重排，底座在立体层下方，不画投影。原池沿斜边全部保留，不再有第172/197行删行接口。\n\n交付：fountain_dry_01_native.png、fountain_dry_01_6x.png、fountain_dry_01_8x.png，及 vs_hero_skeleton 的1/2/6倍新正式地面对比图。旧版备份：backups/fountain_before_fullsize_20261028.zip。manifest 只更新喷泉尺寸、原点和来源。此前整批并排图、entry_props_metrics.json 和 fountain_dry_01/cleanup.json 属于 D-060初版历史记录；本次新数据以 fountain_fullsize_revision/composition.json 为准。其他8件和所有已通过PNG均未改，未修改积木场景或碰撞。\n\n本次文件检查：\n\n'''+result.stdout+'\n合成两层颜色数：'+str(record['combined_colors'])+'；合成横向换色率：'+str(round(record['horizontal_change_pct'],2))+'%。Alpha仅0/255，饱和青蓝0。\n\n已检查原生、6倍和角色对比；未代替游戏内摆放验收。完成后停止，等待用户验收。\n'
with (Q/'entry_props_QA.md').open('a',encoding='utf8') as f:f.write(qa)
print(json.dumps(record,indent=2));print(result.stdout)
