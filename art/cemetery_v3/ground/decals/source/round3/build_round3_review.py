"""Section8 review using exactly the previous native480x270 composition."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,ast,zipfile,sys,subprocess,hashlib
S=Path(__file__).resolve().parent;D=S.parents[1];G=D.parent;R=G.parents[2];Q=D/'qc'
tree=ast.parse((D/'source/round2/build_round2_review.py').read_text())
assignments={t.id:n.value for n in tree.body if isinstance(n,ast.Assign) for t in n.targets if isinstance(t,ast.Name)}
positions=ast.literal_eval(assignments['positions']);layout=ast.literal_eval(assignments['layout'])
tiles=[Image.open(G/f'base/ground_base_{i:02d}.png').convert('RGBA') for i in [1,2]]
floor=Image.new('RGBA',(480,270));rng=np.random.default_rng(1048)
for y in range(0,270,128):
 for x in range(0,480,224):floor.alpha_composite(tiles[int(rng.integers(2))],(x,y))
for n,(x,y) in positions.items():
 im=Image.open(D/f'{n}.png').convert('RGBA');floor.alpha_composite(im,(x-im.width//2,y-im.height//2))
P=R/'art/cemetery_v3/props';area=floor.copy();draw=[]
for n,(x,y) in layout:
 im=Image.open(P/f'{n}_base.png').convert('RGBA');area.alpha_composite(im,(x-im.width//2,y-im.height));draw.append(((x,y),Image.open(P/f'{n}.png').convert('RGBA')))
draw.append(((214,216),Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA')))
for (x,y),im in sorted(draw,key=lambda item:item[0][1]):area.alpha_composite(im,(x-im.width//2,y-im.height))
for k in [2,6]:area.resize((480*k,270*k),Image.Resampling.NEAREST).save(Q/f'decals_round3_test_area_{k}x.png')
names=[f'decal_puddle_{i:02d}.png' for i in [1,2,3]]+['decal_dead_flowers_01.png']
compare=Image.new('RGB',(1440,1232),(35,37,34));dr=ImageDraw.Draw(compare)
with zipfile.ZipFile(Q/'backups/before_round3.zip') as z:
 for i,n in enumerate(names):
  dr.text((4,i*308+4),n+' / ROUND2 left : ROUND3 right /6x',fill=(220,218,201))
  for j,im in enumerate([Image.open(z.open('decals/'+n)).convert('RGBA'),Image.open(D/n).convert('RGBA')]):
   patch=tiles[0].crop((40,40,160,88));patch.alpha_composite(im,((120-im.width)//2,(48-im.height)//2));compare.paste(patch.resize((720,288),Image.Resampling.NEAREST).convert('RGB'),(j*720,i*308+20))
compare.save(Q/'decals_round3_before_after_6x.png')
res=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py')]+[str(D/(n+'.png')) for n in positions],cwd=R,text=True,capture_output=True,check=True)
(Q/'round3_pixel_check.txt').write_text(res.stdout)
fingerprints=json.loads((S/'accepted_fingerprints.json').read_text());assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in fingerprints.items())
with zipfile.ZipFile(Q/'backups/before_round3.zip') as z:
 checks={n:np.array_equal(np.array(Image.open(z.open('decals/'+n)).convert('RGBA'))[:,:,3],np.array(Image.open(D/n).convert('RGBA'))[:,:,3]) for n in names}
assert all(checks.values())
(Q/'round3_verification.json').write_text(json.dumps({'accepted16_and2_bases_byte_identical':True,'changed4_alpha_identical':checks,'native_area':[480,270],'native_decal_count':20,'round2_composition_preserved':True,'status':'SECTION8_COLOR_FIXES_PENDING_USER_IN_GAME_REVIEW'},indent=2)+'\n')
print(res.stdout)
