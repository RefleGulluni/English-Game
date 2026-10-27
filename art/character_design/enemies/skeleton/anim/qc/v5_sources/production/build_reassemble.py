from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-v5-20261027')
# Load only native source-anatomy helpers, never an old walking action or its frames.
v4=(A/'qc/v4_sources/production/build.py').read_text();prefix=v4[:v4.index('# Side walk:')].replace('/tmp/english-game-skeleton-v4-20261027',str(W)).replace("V=Q/'v4_sources'","V=Q/'v5_sources'");exec(prefix)
sec=v4[v4.index('# Native B reconstruction helpers'):v4.index('# A direct 1px stitched line')];exec(sec)
oldrec=json.loads((A/'qc/v4_sources/records.json').read_text())['skeleton_B_reassemble_front_v4'];oldt=json.loads((A/'timing.json').read_text())['animations']['skeleton_B_reassemble_front_v4'];old=[load(A/'frames/skeleton_B_reassemble_front_v4'/f'{k+1:02}.png') for k in range(42)];original=stand['front'].copy()
# One continuous material selection, with the actual holes/visible bones left out.
poly=Image.new('1',(96,96));ImageDraw.Draw(poly).polygon([(31,19),(40,19),(49,28),(55,38),(53,44),(62,57),(68,80),(63,85),(54,75),(46,68),(42,59),(38,55),(39,44),(35,35),(32,29)],fill=1);roi=np.array(poly,bool);ci=codes(original);core=(original[:,:,3]>0)&(ci>=37);rim=dilate(core,1);cm=roi&(original[:,:,3]>0)&~rim;cloth=strip(original,cm);Image.fromarray(cloth).save(V/'front_shroud_source.png')
# Fill only newly uncovered cloth areas with B's own exposed ribs/bone surfaces.
bare=np.zeros_like(original)
for y in range(20,38):
 for x in range(49,63):
  if original[y,x,3] and ci[y,x] not in [20,21,23,25,*range(26,34),36]:
   xx=x-11
   if xx>=0:bare[y,xx]=original[y,x]
back=stand['back'];bi=codes(back)
for y in range(17,40):
 for x in range(29,53):
  if back[y,x,3] and bi[y,x] not in [20,21,23,25,*range(26,34),36]:
   xx=x+3
   if bare[y,xx,3]==0:bare[y,xx]=back[y,x]
Image.fromarray(bare).save(V/'front_under_shroud_ribs.png')
# Reconstruct original material ownership exactly enough to remove cloth, not the standing bones.
realstand=stand['front'].copy();real_m=m.copy();real_bodybase=bodybase.copy();stand['front']=cloth.copy();m=cloth.copy();bodybase=cloth.copy();bodybase[hm]=0

def old_cloth_projection(index):
 j=index-6
 if not 0<=j<21:return np.zeros_like(cloth)
 r=oldrec[index];ld=r['pelvis_delta_y'];ud=r['thorax_delta_y'];stage=0 if j==0 else 1 if j<=2 else 2 if j<=6 else 3 if j<=8 else 4 if j<=11 else 5
 lower,_,_=rise_layers(ld,0 if j==0 else 1);_,upper,_=rise_layers(ud,stage);out=lower.copy();put(out,upper)
 if j in [18,19]:
  tgt=crooked_standard(True,2,1,2);zone=np.zeros((96,96),bool);zone[50 if j==18 else 40:]=True;zone[20:62,25:39]=False;zone[20:62,60:73]=False;out[zone]=tgt[zone]
 if j==20:out=crooked_standard(True,2,1,2)
 return out
clothproj=[old_cloth_projection(k) for k in range(42)];stand['front']=realstand;m=real_m;bodybase=real_bodybase
G={p.stem:load(p) for p in (A/'qc/v2_sources/bone_groups').glob('*.png')};order=['small_bones','pelvis','right_leg','left_leg','ribs','left_arm','right_arm','rib_tip','shoulder_nails','shroud','skull'];offsets={n:[0,0] for n in G}
# Ground offsets already approved in V4, kept exactly.
for r in oldrec[:6]:
 if 'group_offsets' in r:offsets.update(r['group_offsets'])

def floor_layers(index):
 r=oldrec[index];active=r.get('ground_groups',[]);full=np.zeros_like(original);noshroud=np.zeros_like(original)
 for n in order:
  if n not in active:continue
  p=G[n];dx,dy=offsets.get(n,[0,0]);put(full,p,dx,dy)
  if n!='shroud':put(noshroud,p,dx,dy)
 return full,noshroud

def warp_cloth(k,upper_delta):
 if k>=4:return None
 cut=[40,48,58,68,78][k];top=[65,57,49,41,35][k];bottom=[85,86,87,88,89][k];out=np.zeros_like(cloth);srcrows=list(range(19,cut));n=bottom-top+1
 rows=[srcrows[min(len(srcrows)-1,round(t*(len(srcrows)-1)/max(1,n-1)))] for t in range(n)]
 last=cloth[rows[-1]];xs=np.where(last[:,3]>0)[0];bottomdx=60-int(np.median(xs)) if len(xs) else 2;topdx=[-3,-1,0,1,2][k]
 for j,sy in enumerate(rows):
  yy=top+j;dx=round(topdx+(bottomdx-topdx)*j/max(1,n-1))
  for sx in np.where(cloth[sy,:,3]>0)[0]:
   xx=sx+dx
   if 0<=xx<96 and 0<=yy<96:out[yy,xx]=cloth[sy,sx]
 return out
fs=[a.copy() for a in old];records=[];D=V/'reassembly_cloth_layers';D.mkdir(exist_ok=True)
for idx in range(12,23):
 a=old[idx].copy();floorfull,floornone=floor_layers(idx);floorcloth=np.zeros_like(a);put(floorcloth,G['shroud'],*offsets['shroud']);r={'frame':idx+1,'source_v4_frame':idx+1}
 # Remove old ground cloth wherever it is actually visible. Restore only the original bone layer behind it.
 fc=(floorcloth[:,:,3]>0)&(a==floorcloth).all(2);a[fc]=floornone[fc]
 if idx<=17:
  k=idx-12;proj=clothproj[idx];erase=(proj[:,:,3]>0)&(a==proj).all(2);a[erase]=0
  # Existing skeleton stays. A tiny stationary bare-rib source fills only holes made by lifting off the old cloth.
  rib=np.zeros_like(a);put(rib,bare,2,oldrec[idx]['thorax_delta_y']);fg=rib[:,:,3]>0;fill=erase&fg;a[fill]=rib[fill]
  # Still-grounded material recedes from its raised corner toward the left-shin end.
  rem=G['shroud'].copy();cutx=[30,37,44,51,58,96][k];rem[:,:cutx]=0;remaining=np.zeros_like(a);put(remaining,rem,*offsets['shroud']);put(a,remaining)
  lift=warp_cloth(k,oldrec[idx]['thorax_delta_y'])
  if lift is None:
   lift=proj.copy()
   if k==4:lift[78:]=0
  put(a,lift);Image.fromarray(lift).save(D/f'{idx+1:02}_raised.png');Image.fromarray(remaining).save(D/f'{idx+1:02}_on_floor.png');r.update({'cloth_lift_stage':k+1,'ground_material_cutoff_x':cutx,'raised_top_y':int(np.where(lift[:,:,3]>0)[0].min()) if (lift[:,:,3]>0).any() else None,'same_canonical_cloth_source':True})
 else:r['ground_shroud_already_lifted']=True
 fs[idx]=a;records.append(r)
# No changes to the approved late black-thread section, standard endpoints, or other animations.
assert np.array_equal(fs[0],old[0]) and np.array_equal(fs[-1],old[-1]);assert all(np.array_equal(fs[k],old[k]) for k in range(23,42))
n='skeleton_B_reassemble_front_v5';save(n,fs,oldt['durations_ms'],False,records)
# The reused helper's save signature is simple and stores no final QA; write timings explicitly.
t={n:{'frames':42,'durations_ms':oldt['durations_ms'],'loop':False,'sprite_sheet':n+'.png','hold_last_frame':True}};(W/'reassemble_timing.json').write_text(json.dumps(t,indent=2));(W/'reassemble_records.json').write_text(json.dumps(records,indent=2))
b=Image.new('RGBA',(7*112,6*116),'#403D3F');dr=ImageDraw.Draw(b)
for k,a in enumerate(fs):x=k%7*112;y=k//7*116;b.alpha_composite(Image.fromarray(a),(x+8,y));dr.text((x+8,y+99),str(k+1),fill='white')
b.resize((b.width*3,b.height*3),Image.Resampling.NEAREST).save(W/(n+'_3x.png'));print('reassembly cloth: six states built, original 42 frames and timings retained')
