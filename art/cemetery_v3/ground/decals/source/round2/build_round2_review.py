"""Section7 review: existing PNGs, original pixel scale, integer placement."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,zipfile,datetime,subprocess,sys
S=Path(__file__).resolve().parent;D=S.parents[1];G=D.parent;R=G.parents[2];Q=D/'qc'
positions={
 'decal_puddle_01':(148,108),'decal_puddle_02':(264,44),'decal_puddle_03':(369,258),
 'decal_moss_01':(243,99),'decal_moss_02':(66,39),'decal_moss_03':(19,184),
 'decal_pebbles_01':(166,37),'decal_pebbles_02':(432,145),'decal_bone_bits_01':(161,242),
 'decal_ruts_01':(387,182),'decal_roots_01':(71,209),'decal_dead_flowers_01':(277,142),
 'decal_cracked_slab_01':(454,82),'decal_leaves_02':(410,222),
 'decal_wet_mud_01':(52,251),'decal_wet_mud_02':(421,113),
 'decal_dead_grass_01':(25,113),'decal_dead_grass_02':(148,74),'decal_leaves_01':(250,238),'decal_loose_slab_01':(332,208),
}
tiles=[Image.open(G/f'base/ground_base_{i:02d}.png').convert('RGBA') for i in [1,2]]
def ground(w,h,seed=1048):
 out=Image.new('RGBA',(w,h));rng=np.random.default_rng(seed)
 for y in range(0,h,128):
  for x in range(0,w,224):out.alpha_composite(tiles[int(rng.integers(2))],(x,y))
 return out
def enlargement(im,k,path):im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST).save(path)
outputs=['decals_round2_test_area_2x.png','decals_round2_test_area_6x.png','decals_round2_contact_4x.png','decals_round2_before_after_6x.png','decals_round2_edges_4x.png','round2_pixel_check.txt','round2_verification.json']
existing=[Q/n for n in outputs if (Q/n).exists()]
if existing:
 with zipfile.ZipFile(Q/f'backups/review_before_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in existing:z.write(p,p.name)
floor=ground(480,270);footprints={}
for n,(x,y) in positions.items():
 im=Image.open(D/f'{n}.png').convert('RGBA');px=x-im.width//2;py=y-im.height//2
 assert px>=0 and py>=0 and px+im.width<=480 and py+im.height<=270,n
 floor.alpha_composite(im,(px,py));mask=Image.new('L',floor.size);mask.paste(im.getchannel('A'),(px,py));footprints[n]=np.array(mask)>0
layout=[('tombstone_upright_01',(82,174)),('tombstone_pointed_01',(350,145)),('tombstone_cross_01',(290,259))]
P=R/'art/cemetery_v3/props';cover=Image.new('RGBA',floor.size);draw=[]
for n,(x,y) in layout:
 im=Image.open(P/f'{n}_base.png').convert('RGBA');cover.alpha_composite(im,(x-im.width//2,y-im.height));draw.append(((x,y),Image.open(P/f'{n}.png').convert('RGBA')))
draw.append(((214,216),Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA')))
for (x,y),im in sorted(draw,key=lambda item:item[0][1]):cover.alpha_composite(im,(x-im.width//2,y-im.height))
area=floor.copy();area.alpha_composite(cover)
enlargement(area,2,Q/'decals_round2_test_area_2x.png');enlargement(area,6,Q/'decals_round2_test_area_6x.png')
enlargement(floor,2,Q/'decals_round2_floor_only_2x.png')

manifest=json.loads((S/'round2_manifest.json').read_text());newnames=[r['file'][:-4] for r in manifest['assets']]
allnames=newnames+[n for n in positions if n not in newnames]
sheet=Image.new('RGB',(1440,1540),(34,37,33));dr=ImageDraw.Draw(sheet)
bg=ground(960,540)
for i,n in enumerate(allnames):
 x=i%3*480;y=i//3*220;im=Image.open(D/f'{n}.png').convert('RGBA')
 tx=17+(i%5)*161;ty=10+(i%4)*100;patch=bg.crop((tx,ty,tx+120,ty+48))
 patch.alpha_composite(im,((120-im.width)//2,(48-im.height)//2))
 sheet.paste(patch.resize((480,192),Image.Resampling.NEAREST).convert('RGB'),(x,y+24))
 suffix=' / retained' if n not in newnames else ''
 dr.text((x+4,y+4),n.replace('decal_','')+f' {im.width}x{im.height} /4x'+suffix,fill=(220,218,203))
sheet.save(Q/'decals_round2_contact_4x.png')

# Compare the two replaced families; same soil patch under both versions.
compare=Image.new('RGB',(1080,1190),(34,37,33));dr=ImageDraw.Draw(compare)
with zipfile.ZipFile(Q/'backups/before_round2.zip') as z:
 for i,n in enumerate(['decal_puddle_01','decal_puddle_02','decal_moss_01','decal_moss_02']):
  dr.text((5,i*290+5),n+' / OLD left : ROUND2 right /6x',fill=(220,218,203))
  for j,im in enumerate([Image.open(z.open(f'decals/{n}.png')).convert('RGBA'),Image.open(D/f'{n}.png').convert('RGBA')]):
   patch=bg.crop((40,40,130,84));patch.alpha_composite(im,((90-im.width)//2,(44-im.height)//2))
   compare.paste(patch.resize((540,264),Image.Resampling.NEAREST).convert('RGB'),(j*540,i*290+24))
compare.save(Q/'decals_round2_before_after_6x.png')

edge=Image.new('RGB',(1440,3080),(34,37,33));dr=ImageDraw.Draw(edge)
for i,n in enumerate(newnames):
 im=Image.open(D/f'{n}.png').convert('RGBA');dr.text((4,i*220+4),n.replace('decal_','')+' / SAME PNG on3 soil positions /4x',fill=(220,218,203))
 for j,(tx,ty) in enumerate([(0,0),(105,41),(228,128)]):
  patch=bg.crop((tx,ty,tx+120,ty+48));patch.alpha_composite(im,((120-im.width)//2,(48-im.height)//2));edge.paste(patch.resize((480,192),Image.Resampling.NEAREST).convert('RGB'),(j*480,i*220+24))
edge.save(Q/'decals_round2_edges_4x.png')

protected=json.loads((S/'protected_accepted_assets.json').read_text());checks={}
checks['accepted_base_and6_decals_byte_identical']={p:hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in protected.items()}
assert all(checks['accepted_base_and6_decals_byte_identical'].values())
mask=np.array(cover.getchannel('A'))>0
checks['native_area_size']=[480,270];checks['native_decal_count']=len(positions);checks['draw_order']='base, all decals, all prop bases, then y-sorted props+hero'
checks['decals']={n:{'center':list(pos),'visible_fraction_after_props':float((footprints[n]&~mask).sum()/footprints[n].sum())} for n,pos in positions.items()}
checks['status']='SECTION7_REPLACED4_ADDED10_READY_FOR_IN_GAME_REVIEW'
args=[sys.executable,str(R/'scripts/tools/pixel_check.py')]+[str(D/f'{n}.png') for n in positions]
res=subprocess.run(args,cwd=R,capture_output=True,text=True,check=True);(Q/'round2_pixel_check.txt').write_text(res.stdout)
(Q/'round2_verification.json').write_text(json.dumps(checks,indent=2)+'\n')
print(res.stdout)
print('Visibility after props:',{n:round(v['visible_fraction_after_props'],3) for n,v in checks['decals'].items() if v['visible_fraction_after_props']<1})
