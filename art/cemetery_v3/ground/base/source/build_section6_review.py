"""Current section6 review, integer placement and nearest integer previews only."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,zipfile,io,hashlib,datetime,subprocess,sys
S=Path(__file__).resolve().parent;B=S.parent;G=B.parent;R=B.parents[3];Q=B/'qc';D=G/'decals'
tiles=[Image.open(B/f'ground_base_{i:02d}.png').convert('RGBA') for i in [1,2]]
names=['decal_puddle_01','decal_puddle_02','decal_wet_mud_01','decal_wet_mud_02','decal_moss_01','decal_moss_02','decal_dead_grass_01','decal_dead_grass_02','decal_leaves_01','decal_loose_slab_01']
decals={n:Image.open(D/f'{n}.png').convert('RGBA') for n in names}
def ground(w,h,seed=1048):
 rng=np.random.default_rng(seed);out=Image.new('RGBA',(w,h));ids=[]
 for y in range(0,h,128):
  row=[]
  for x in range(0,w,224):
   k=int(rng.integers(2));row.append(k+1);out.alpha_composite(tiles[k],(x,y))
  ids.append(row)
 return out,ids
def save2(im,name):im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST).save(Q/name)
def dress(bg,layout,hero):
 out=bg.copy();P=R/'art/cemetery_v3/props';draw=[]
 for name,(x,y) in layout:
  base=Image.open(P/f'{name}_base.png').convert('RGBA');out.alpha_composite(base,(x-base.width//2,y-base.height))
  draw.append(((x,y),Image.open(P/f'{name}.png').convert('RGBA')))
 draw.append((hero,Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA')))
 for (x,y),im in sorted(draw,key=lambda k:k[0][1]):out.alpha_composite(im,(x-im.width//2,y-im.height))
 return out

# Preserve QC generated earlier in this section when the review is rerun.
targets=['base_fill_2x.png','base_01_only_fill_2x.png','base_test_area_2x.png','base_vs_trial_2x.png','base_only_with_props_2x.png','base_only_vs_trial_2x.png','base_center_repair_8x.png','base_wrap_junction_8x.png','decal_contact_4x.png','decal_edges_4x.png','verification.json','pixel_check.txt']
present=[Q/n for n in targets if (Q/n).exists()]
with zipfile.ZipFile(Q/f'backups/review_before_section6_build_{datetime.datetime.now():%Y%m%d_%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in present:z.write(p,p.name)

full,ids=ground(960,540);save2(full,'base_fill_2x.png')
single=Image.new('RGBA',(960,540))
for y in range(0,540,128):
 for x in range(0,960,224):single.alpha_composite(tiles[0],(x,y))
save2(single,'base_01_only_fill_2x.png')

bare,_=ground(480,270)
layout=[('tombstone_upright_01',(84,168)),('tombstone_pointed_01',(350,142)),('tombstone_cross_01',(280,251))]
placements=[(151,69),(405,201),(58,228),(372,103),(126,121),(199,42),(26,193),(374,250),(146,240),(305,178)]
floor=bare.copy()
for n,(x,y) in zip(names,placements):
 im=decals[n];floor.alpha_composite(im,(x-im.width//2,y-im.height//2))
area=dress(floor,layout,(208,211));save2(area,'base_test_area_2x.png')
save2(dress(bare,layout,(208,211)),'base_only_with_props_2x.png')

# Both panels preserve the same native pixel scale. Old ground is only240x135;
# the neutral left margin is a label area, not invented extended old ground.
old=Image.open(G/'trial/ground_trial_01.png').convert('RGBA')
oldview=dress(old,[('tombstone_upright_01',(46,129)),('rubble_pile_01',(197,130))],(128,132))
compare=Image.new('RGBA',(736,302),(35,37,35,255));draw=ImageDraw.Draw(compare)
draw.text((8,8),'OLD TRIAL 240x135',fill=(215,211,193));draw.text((256,8),'NEW BASE + 10 DECALS 480x270',fill=(215,211,193))
compare.alpha_composite(oldview,(0,99));compare.alpha_composite(area,(256,32));save2(compare,'base_vs_trial_2x.png')
local=Image.new('RGBA',(480,135));local.alpha_composite(oldview)
local.alpha_composite(dress(bare.crop((0,0,240,135)),[('tombstone_upright_01',(46,129)),('rubble_pile_01',(197,130))],(128,132)),(240,0))
save2(local,'base_only_vs_trial_2x.png')

# Native patch contact sheet, enlarged4x; labels are in the QC margin only.
sheet=Image.new('RGB',(1000,400),(35,37,35));draw=ImageDraw.Draw(sheet)
for i,n in enumerate(names):
 col=i%5;row=i//5;x=col*200;y=row*200;im=decals[n]
 patch=full.crop((23+i*47,24+i*25,23+i*47+48,24+i*25+36))
 # Large footprints use a96x36 receiving patch at2x; all previews state scale.
 scale=4 if im.width<=46 else 2
 pw=48 if scale==4 else 96
 patch=full.crop((23+i*47,24+i*25,23+i*47+pw,24+i*25+36))
 patch.alpha_composite(im,((pw-im.width)//2,(36-im.height)//2))
 patch=patch.resize((pw*scale,36*scale),Image.Resampling.NEAREST)
 sheet.paste(patch.convert('RGB'),(x+4,y+30))
 draw.text((x+5,y+4),n.replace('decal_',''),fill=(220,216,200))
 draw.text((x+5,y+181),f'{im.width}x{im.height} canvas / {scale}x',fill=(220,216,200))
sheet.save(Q/'decal_contact_4x.png')

# Each identical decal on three naturally different receiving patches. No
# position-dependent color replacement or alpha blending is applied.
edges=Image.new('RGB',(1152,920),(35,37,35));dr=ImageDraw.Draw(edges)
for i,n in enumerate(names):
 im=decals[n];y=i*92;dr.text((4,y+3),n.replace('decal_',''),fill=(220,216,200))
 for j,(tx,ty) in enumerate([(0,0),(110,46),(330,114)]):
  patch=full.crop((tx,ty,tx+96,ty+18+im.height));patch.alpha_composite(im,((96-im.width)//2,8))
  pic=patch.resize((384,patch.height*4),Image.Resampling.NEAREST)
  # Show the entire larger patches on their own expanded row below instead.
  edges.paste(pic.convert('RGB'),(j*384,y+18))
# Fixed rows must fit the largest decal; avoid overlap/clipping.
edges=Image.new('RGB',(1152,2200),(35,37,35));dr=ImageDraw.Draw(edges)
for i,n in enumerate(names):
 im=decals[n];y=i*220;dr.text((4,y+3),n.replace('decal_','')+' / same asset on 3 patches /4x',fill=(220,216,200))
 for j,(tx,ty) in enumerate([(0,0),(110,46),(330,114)]):
  patch=full.crop((tx,ty,tx+96,ty+48));patch.alpha_composite(im,((96-im.width)//2,(48-im.height)//2))
  edges.paste(patch.resize((384,192),Image.Resampling.NEAREST).convert('RGB'),(j*384,y+20))
edges.save(Q/'decal_edges_4x.png')

show=Image.new('RGBA',(448,256))
for y in range(2):
 for x in range(2):show.alpha_composite(tiles[(x+y)%2],(x*224,y*128))
show.crop((200,104,248,152)).resize((384,384),Image.Resampling.NEAREST).save(Q/'base_wrap_junction_8x.png')
tiles[0].crop((88,44,136,84)).resize((384,320),Image.Resampling.NEAREST).save(Q/'base_center_repair_8x.png')

arr=[np.array(im) for im in tiles];checks={}
for i,a in enumerate(arr,1):
 checks[str(i)]={'size':[224,128],'opposite_lr_exact':bool(np.array_equal(a[:,0],a[:,-1])),'opposite_tb_exact':bool(np.array_equal(a[0],a[-1])),'mean_rgb':a[:,:,:3].mean(axis=(0,1)).tolist(),'horizontal_change':float(np.any(a[:,1:,:3]!=a[:,:-1,:3],axis=2).mean()*100)}
checks['variant_four_edges_exact']=all(np.array_equal(arr[0][r],arr[1][r]) for r in [0,-1]) and np.array_equal(arr[0][:,0],arr[1][:,0]) and np.array_equal(arr[0][:,-1],arr[1][:,-1])
mapping=json.loads((S/'10_section6_color_mapping.json').read_text());lookup={tuple(m['from']):tuple(m['to']) for m in mapping['mapping']}
with zipfile.ZipFile(Q/'backups/before_section6_recolor/base_and_qc_before_recolor.zip') as z:
 for i,a in enumerate(arr,1):
  orig=np.array(Image.open(z.open(f'ground_base_{i:02d}.png')).convert('RGBA'))
  expected=np.array([lookup[tuple(c)] for c in orig[:,:,:3].reshape(-1,3)],np.uint8).reshape(a.shape[:2]+(3,))
  checks[str(i)]['exact_palette_lookup_texture_unchanged']=bool(np.array_equal(a[:,:,:3],expected) and np.array_equal(a[:,:,3],orig[:,:,3]))
protected=json.loads((S/'protected_previous_assets.json').read_text())
checks['protected_trial_tiles_unchanged']=all(hashlib.sha256((G/p).read_bytes()).hexdigest()==h for p,h in protected.items())
checks['random_seed']=1048;checks['fill_tile_ids']=ids
checks['area_decal_centers']={n:list(p) for n,p in zip(names,placements)}
checks['status']='REPETITION_ACCEPTED_BY_USER_SECTION6; RECOLOR_AND10_DECALS_READY_FOR_IN_GAME_REVIEW'
assert checks['variant_four_edges_exact'] and checks['protected_trial_tiles_unchanged']
assert all(checks[str(i)][k] for i in [1,2] for k in ['opposite_lr_exact','opposite_tb_exact','exact_palette_lookup_texture_unchanged'])
(Q/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
command=[sys.executable,str(R/'scripts/tools/pixel_check.py')]+[str(B/f'ground_base_{i:02d}.png') for i in [1,2]]+[str(D/f'{n}.png') for n in names]
result=subprocess.run(command,cwd=R,text=True,capture_output=True,check=True);(Q/'pixel_check.txt').write_text(result.stdout)
print(result.stdout);print('All palette, edge, protected-file assertions passed.')
