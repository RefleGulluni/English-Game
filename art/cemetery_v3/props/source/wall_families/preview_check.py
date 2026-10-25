from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np,subprocess,sys,hashlib
W=Path('/tmp/english-game-wall-families-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';S=W/'staged'
new=list(json.loads((W/'recipes.json').read_text()))
def im(n,suf=''):return Image.open((S if n in new else O)/(n+suf+'.png')).convert('RGBA')
def assembly(size,objects,hero_xy=None):
 p=Image.new('RGBA',size,'#403D3F')
 # Ground first, then masonry, finally free standing gate pillars over joins.
 for base in [True,False]:
  for n,x,y in objects:
   a=im(n,'_base' if base else '');p.alpha_composite(a,(x-a.width//2,y-a.height))
 if hero_xy:
  h=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');p.alpha_composite(h,(hero_xy[0]-48,hero_xy[1]-96))
 return p
Aobjs=[('low_wall_01',120,140),('low_wall_rubble_pillar_01',268,140),('low_wall_01',416,140),('low_wall_rubble_broken_01',564,140)]
Ap=assembly((780,178),Aobjs,(700,140));ImageDraw.Draw(Ap).text((12,155),'A: original rubble + embedded rubble pillar + original rubble + broken rubble',fill='#BEB7A9');Ap.save(W/'family_A_native.png');Ap.resize((1560,356),Image.Resampling.NEAREST).save(W/'wall_family_A_assembly_2x.png')
Bobjs=[('low_wall_ashlar_01',131,140),('low_wall_ashlar_01',259,140),('low_wall_broken_01',387,140),('wall_pillar_01',60,140),('iron_fence_01',131,300),('wall_pillar_01',50,300),('wall_pillar_01',202,300)]
Bp=assembly((680,335),Bobjs,(570,140));ImageDraw.Draw(Bp).text((12,155),'B: gate pillar + ashlar + ashlar + original broken ashlar',fill='#BEB7A9');ImageDraw.Draw(Bp).text((12,314),'B: original gate pillar + original iron + original gate pillar',fill='#BEB7A9');Bp.save(W/'family_B_native.png');Bp.resize((1360,670),Image.Resampling.NEAREST).save(W/'wall_family_B_assembly_2x.png')
joints=[(Ap,193,140,'A wall / embedded pillar'),(Ap,341,140,'A embedded pillar / wall'),(Ap,489,140,'A wall / rubble break'),(Bp,192,140,'B ashlar / ashlar'),(Bp,320,140,'B ashlar / ashlar break'),(Bp,69,140,'B gate pillar / wall'),(Bp,63,300,'B gate pillar / iron'),(Bp,195,300,'B iron / gate pillar')]
j=Image.new('RGBA',(224,228),'#403D3F');d=ImageDraw.Draw(j)
for k,(p,x,y,label) in enumerate(joints):
 tx=k%4*56;ty=k//4*114;j.alpha_composite(p.crop((x-26,y-98,x+26,y+4)),(tx+2,ty+10));d.text((tx+2,ty+1),str(k+1),fill='#BEB7A9')
j.resize((1792,1824),Image.Resampling.NEAREST).save(W/'wall_joints_8x.png')
checks={};A=np.array(im('low_wall_01'));AB=np.array(im('low_wall_rubble_broken_01'));AP=np.array(im('low_wall_rubble_pillar_01'));B=np.array(im('low_wall_broken_01'));BF=np.array(im('low_wall_ashlar_01'))
checks['A_broken_left_half_exact']=bool(np.array_equal(AB[:,:89],A[:,:89]));checks['A_broken_join_exact']=bool(np.array_equal(AB[:,21],A[:,168]));checks['A_pillar_left_join_exact']=bool(np.array_equal(AP[32:,21],A[:,168]));checks['A_pillar_right_join_exact']=bool(np.array_equal(AP[32:,168],A[:,21]));checks['A_pillar_lower_courses_exact']=bool(np.array_equal(AP[81:],A[49:]));checks['A_pillar_base_integer_shift_exact']=bool(np.array_equal(np.array(im('low_wall_rubble_pillar_01','_base'))[32:],np.array(im('low_wall_01','_base'))));checks['B_repeat_join_exact']=bool(np.array_equal(BF[:,21],BF[:,148]));checks['B_full_to_broken_join_exact']=bool(np.array_equal(BF[:,148],B[:,21]));checks['B_intact_prefix_exact']=bool(np.array_equal(BF[:,21:43],B[:,21:43]));assert all(checks.values()),checks
# New colors must be literal source colors, not synthesized palettes or noisy brushes.
for n in new:
 parent='low_wall_broken_01' if n=='low_wall_ashlar_01' else 'low_wall_01'
 allowed=set()
 for suf in ['','_base']:
  ar=np.array(im(parent,suf));allowed|={tuple(c) for c in ar[ar[:,:,3]>0,:3]}
 for suf in ['','_base']:
  ar=np.array(im(n,suf));colors={tuple(c) for c in ar[ar[:,:,3]>0,:3]};assert colors<=allowed,(n,colors-allowed)
(W/'interface_checks.json').write_text(json.dumps({'checks':checks,'joint_atlas_labels':[x[3] for x in joints]},indent=2));print(checks)
files=[S/(n+suf+'.png') for n in new for suf in ['','_base']];z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),*[str(p) for p in files]],capture_output=True,text=True);print(z.stdout);assert z.returncode==0,z.stdout;(W/'pixel_check_wall_families.txt').write_text(z.stdout)
