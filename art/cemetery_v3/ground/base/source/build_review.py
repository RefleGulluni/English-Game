from pathlib import Path
from PIL import Image
import numpy as np,json,sys,zipfile
S=Path(__file__).resolve().parent;B=S.parent;G=B.parent;R=B.parents[3];Q=B/'qc'
sys.path.insert(0,str(S));from assemble_base import fill
arr=[np.array(Image.open(B/f'ground_base_{i:02d}.png').convert('RGB')) for i in [1,2]]
# Source-scale sampling/assembly; no rotations, mirrors or texture synthesis.
def ground(w,h):
 rng=np.random.default_rng(1048);out=Image.new('RGBA',(w,h))
 for y in range(0,h,128):
  for x in range(0,w,224):out.alpha_composite(Image.fromarray(arr[int(rng.integers(2))]).convert('RGBA'),(x,y))
 return out
P=R/'art/cemetery_v3/props'
def dress(bg,layout,hero):
 out=bg.copy()
 for name,(x,y) in layout:
  base=Image.open(P/f'{name}_base.png').convert('RGBA');out.alpha_composite(base,(x-base.width//2,y-base.height))
 draw=[]
 for name,foot in layout:draw.append((foot,Image.open(P/f'{name}.png').convert('RGBA')))
 draw.append((hero,Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA')))
 for (x,y),im in sorted(draw,key=lambda k:k[0][1]):out.alpha_composite(im,(x-im.width//2,y-im.height))
 return out
layout=[('tombstone_upright_01',(84,168)),('tombstone_pointed_01',(350,142)),('tombstone_cross_01',(280,251))]
area=dress(ground(480,270),layout,(208,211));area.resize((960,540),Image.Resampling.NEAREST).save(Q/'base_only_with_props_2x.png')
small=[('tombstone_upright_01',(46,122)),('rubble_pile_01',(190,125))]
old=Image.open(G/'trial/ground_trial_01.png').convert('RGBA').crop((0,0,224,128))
new=ground(224,128);compare=Image.new('RGBA',(448,128));compare.alpha_composite(dress(old,small,(128,125)));compare.alpha_composite(dress(new,small,(128,125)),(224,0));compare.resize((896,256),Image.Resampling.NEAREST).save(Q/'base_only_vs_trial_2x.png')
# Preserve before-contrast full-screen evidence directly from the backup.
with zipfile.ZipFile(Q/'backups/base_before_contrast_adjust.zip') as z:
 Image.open(z.open('qc/base_fill_2x.png')).save(Q/'base_fill_before_contrast_2x.png')
# Both-center and wrap-junction details, native pixels enlarged8x.
show=Image.new('RGBA',(224*2,128*2))
for y in range(2):
 for x in range(2):show.alpha_composite(Image.fromarray(arr[(x+y)%2]).convert('RGBA'),(x*224,y*128))
show.crop((200,104,248,152)).resize((384,384),Image.Resampling.NEAREST).save(Q/'base_wrap_junction_8x.png')
Image.open(B/'ground_base_01.png').crop((88,44,136,84)).resize((384,320),Image.Resampling.NEAREST).save(Q/'base_center_repair_8x.png')
# Visible grid overlay check for registered repair sampling.
grid=Image.open(S/'04_grid_overlay.png');grid.crop((600,350,1000,650)).resize((1200,900),Image.Resampling.NEAREST).save(Q/'repair_grid_detail_3x.png')
checks={}
for i,a in enumerate(arr,1):
 checks[str(i)]={'size':[224,128],'opposite_lr_exact':bool(np.array_equal(a[:,0],a[:,-1])),'opposite_tb_exact':bool(np.array_equal(a[0],a[-1])),'colors':len(np.unique(a.reshape(-1,3),axis=0)),'horizontal_change':round(float(np.any(a[:,1:]!=a[:,:-1],axis=2).mean()*100),2)}
checks['variant_four_edges_exact']=all(np.array_equal(arr[0][r],arr[1][r]) for r in [0,-1]) and np.array_equal(arr[0][:,0],arr[1][:,0]) and np.array_equal(arr[0][:,-1],arr[1][:,-1])
checks['status']='NOT_APPROVED_REPEAT_REMAINS_DECALS_NOT_STARTED'
(Q/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
