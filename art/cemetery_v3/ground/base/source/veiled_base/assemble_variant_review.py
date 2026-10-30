from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,zipfile,datetime,subprocess,sys
S=Path(__file__).resolve().parent;B=S.parents[1];Q=B/'qc';R=B.parents[3]
exec(compile((S/'material_ops.py').read_text(),str(S/'material_ops.py'),'exec'))
existing=[B/'veiled_base_02.png']+list(Q.glob('veiled_base_*'))+list(S.glob('07_*'));existing=[p for p in existing if p.is_file()]
if existing:
 with zipfile.ZipFile(Q/f'backups/veiled_variant_before_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in existing:z.write(p,str(p.relative_to(B)))
meta=json.loads((S/'05_final_palette.json').read_text());pal=np.array(meta['palette'],np.uint8);roles=np.array(meta['roles'])
old=np.array(Image.open(B/'veiled_base_01.png').convert('RGB'));raw=np.array(Image.open(S/'06_variant_restored_cells.png').convert('RGB'));assert raw.shape==old.shape==(128,224,3)
lab,progress=quiet(match(raw,pal),pal,roles);edit=pal[lab];cost=((old.astype(float)-edit.astype(float))**2).mean(2)
l=cut(cost[:,8:33])+8;r=cut(cost[:,191:216])+191;t=cut(cost[8:25].T)+8;b=cut(cost[103:120].T)+103
yy,xx=np.indices((128,224));mask=(xx>=l[:,None])&(xx<=r[:,None])&(yy>=t[None,:])&(yy<=b[None,:]);out=old.copy();out[mask]=edit[mask]
Image.fromarray(out).convert('RGBA').save(B/'veiled_base_02.png');Image.fromarray((mask*255).astype('uint8')).save(S/'07_variant_selection_mask.png')
(S/'07_variant_assembly.json').write_text(json.dumps({'method':'AI interior redraw in shared36-color palette,quiet adjacent near-shades,irregular native min-error cuts retaining all original8px margins. No flips,rotations,resizing or procedural texture.','quiet_progress':progress,'selected_pixels':int(mask.sum()),'changed_pixels':int(np.any(old!=out,2).sum()),'left_cut':l.tolist(),'right_cut':r.tolist(),'top_cut':t.tolist(),'bottom_cut':b.tolist()},indent=2)+'\n')
images=[old,out];ids=np.random.default_rng(20261030).integers(0,2,(3,3));assert len(np.unique(ids[:2,:2]))==2
mixed=np.empty((384,672,3),np.uint8)
for y in range(3):
 for x in range(3):mixed[y*128:y*128+128,x*224:x*224+224]=images[ids[y,x]]
Image.fromarray(mixed).save(Q/'veiled_base_mix_3x3_1x.png');Image.fromarray(mixed).resize((1344,768),Image.Resampling.NEAREST).save(Q/'veiled_base_mix_3x3_2x.png')
bare=mixed[:270,:480];Image.fromarray(bare).resize((960,540),Image.Resampling.NEAREST).save(Q/'veiled_base_fill_2x.png')
for i,a in enumerate(images,1):
 Image.fromarray(a).resize((1344,768),Image.Resampling.NEAREST).save(Q/f'veiled_base_{i:02}_6x.png')
 Image.fromarray(np.tile(a,(3,3,1))).save(Q/f'veiled_base_{i:02}_repeat_3x3_1x.png')
# Raw native materials and assets only,without engine grading,fog or shader noise.
scene=Image.fromarray(bare).convert('RGBA');outer=np.array(Image.open(B/'ground_base_01.png').convert('RGBA'));moss=np.array(Image.open(B.parent/'transitions/moss_texture_01.png').convert('RGBA'))
scene.alpha_composite(Image.fromarray(np.tile(outer,(3,1,1))[:270,:96]),(384,0))
scene.alpha_composite(Image.fromarray(moss[22:84,25:131]),(239,187))
puddle=Image.open(B.parent/'decals/decal_puddle_02.png').convert('RGBA');scene.alpha_composite(puddle,(330-puddle.width//2,218-puddle.height//2))
for name,foot in [('tombstone_upright_01',(96,157)),('tombstone_upright_02',(286,161)),('tombstone_small_01',(264,245))]:
 for suffix in ['_base','']:
  im=Image.open(R/f'art/cemetery_v3/props/{name}{suffix}.png').convert('RGBA');scene.alpha_composite(im,(foot[0]-im.width//2,foot[1]-im.height))
hero=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');scene.alpha_composite(hero,(190-hero.width//2,190-hero.height))
scene.resize((960,540),Image.Resampling.NEAREST).save(Q/'veiled_base_with_props_2x.png')
comparison=np.concatenate([outer[:,:,:3],old,moss[:,:,:3]],axis=1);Image.fromarray(comparison).resize((1344,256),Image.Resampling.NEAREST).save(Q/'veiled_base_material_compare_2x.png')
for seed in range(4):
 # All4 combinations at a cross,not only one chosen random fill.
 corner=np.concatenate([np.concatenate([images[seed//2],images[seed%2]],1),np.concatenate([images[1-seed%2],images[1-seed//2]],1)],0)
 Image.fromarray(corner[104:152,200:248]).resize((384,384),Image.Resampling.NEAREST).save(Q/f'veiled_base_junction_{seed}_8x.png')
checks={'status':'VEILED_BASE_STOPPED_VISIBLE_MIX_REPETITION','images':{},'random_seed':20261030,'mixed_ids':ids.tolist(),'bare_native_size':[480,270],'repeat_native_size':[672,384],'scale':2,'same_8px_margin':bool(np.array_equal(old[:8],out[:8]) and np.array_equal(old[-8:],out[-8:]) and np.array_equal(old[:,:8],out[:,:8]) and np.array_equal(old[:,-8:],out[:,-8:])),'same_four_edges':bool(np.array_equal(old[0],out[0]) and np.array_equal(old[-1],out[-1]) and np.array_equal(old[:,0],out[:,0]) and np.array_equal(old[:,-1],out[:,-1])),'variant_changed_pixels':int(np.any(old!=out,2).sum()),'variant_changed_fraction':float(np.any(old!=out,2).mean()),'all_ordered_adjacencies_exact':all(np.array_equal(a[:,0],b[:,-1]) and np.array_equal(a[0],b[-1]) for a in images for b in images),'props_preview':'480x270 native3approved tombstones+bases,hero,puddle02,moss106x62rectangle at239,187;right96px outer-cemetery base strip. Comparison edges are not runtime terrain borders. No scene changes or grading.'}
for i,a in enumerate(images,1):
 p=B/f'veiled_base_{i:02}.png';v={'mean_rgb':a.mean((0,1)).tolist(),'luma_std':float((a@LUMA).std()),'colors':len(np.unique(a.reshape(-1,3),axis=0)),'horizontal_change':float(np.any(a[:,1:]!=a[:,:-1],2).mean()*100),'all_alpha_255':set(Image.open(p).getchannel('A').getdata())=={255},'opposite_edges_exact':bool(np.array_equal(a[0],a[-1]) and np.array_equal(a[:,0],a[:,-1])),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};checks['images'][p.name]=v
 assert 30<=v['colors']<=40 and 8<=v['luma_std']<=10 and v['all_alpha_255'] and v['opposite_edges_exact']
 assert all(lo<=value<=hi for value,lo,hi in zip(v['mean_rgb'],[58,61,60],[63,66,65]))
assert checks['same_four_edges'] and checks['same_8px_margin'] and checks['all_ordered_adjacencies_exact']
lock=json.loads((S/'protected_approved_assets.json').read_text());checks['approved_images_unchanged']=all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in lock.items());assert checks['approved_images_unchanged']
result=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(B/'veiled_base_01.png'),str(B/'veiled_base_02.png')],cwd=R,text=True,capture_output=True,check=True)
(Q/'veiled_base_pixel_check.txt').write_text(result.stdout);(Q/'veiled_base_verification.json').write_text(json.dumps(checks,indent=2)+'\n');print(checks);print(result.stdout)
