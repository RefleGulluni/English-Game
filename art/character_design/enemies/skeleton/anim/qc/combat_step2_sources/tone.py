from pathlib import Path
from PIL import Image
import numpy as np,json
W=Path('/tmp/english-combat-step2-20261028');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');L=np.array([.299,.587,.114]);ALL={};records={}
for n in ['hero_B1_cast_left','skeleton_B_attack_left','skeleton_B_attack_right_v2']:
 kind='hero' if n.startswith('hero') else 'skeleton';direction='left' if 'left' in n else 'right';ref=R/('art/character_design/hero_B1_'+direction+'.png' if kind=='hero' else 'art/character_design/enemies/skeleton/skeleton_B_'+direction+'.png');m=np.array(Image.open(ref).convert('RGBA'));pal=np.unique(m[m[:,:,3]>0,:3],axis=0).astype(int)
 if kind=='skeleton':
  if direction=='right':arm=np.array(Image.open(R/'art/character_design/enemies/skeleton/anim/qc/v5_sources/standing_parts/near_right_arm.png'));pal=np.unique(arm[arm[:,:,3]>0,:3],axis=0).astype(int)
  else:v=m[22:53,48:57];pal=np.unique(v[v[:,:,3]>0,:3],axis=0).astype(int)
 frames=sorted((W/'staged/frames'/n).glob('*.png'));nr=len(frames);rr=[]
 for p in frames:
  k=int(p.stem);a=np.array(Image.open(p));lp=W/'staged/qc/combat_step2_sources'/n/f'{k:02}_moving_arm.png'
  if not lp.exists() or k in [1,nr]:continue
  layer=np.array(Image.open(lp));mask=layer[:,:,3]>0
  if n=='skeleton_B_attack_left':
   # Far arm is behind the chest: tone only pixels that are actually visible outside the standing chest silhouette.
   fromcode=(W/'build.py').read_text();defs=fromcode[fromcode.index('def load('):fromcode.index('# Hero left caster:')];scope={'np':np,'Image':Image,'ImageDraw':__import__('PIL.ImageDraw',fromlist=['Draw']),'O':W/'staged','W':W,'ALL':{}};exec(defs,scope)
   plan=json.loads((W/'parts_plan_before_compositing.json').read_text())[n];body=scope['rowpose'](m,plan['upper'][k-1],plan['pelvis'][k-1]);bm=np.zeros(a.shape[:2],bool);bm[:,32:128]=body[:,:,3]>0;mask &= ~bm
  row=[]
  for lo,hi in [(0,20),(20,45),(45,65),(65,96)]:
   reg=a[lo:hi];fg=reg[:,:,3]>0;target=mask[lo:hi]&fg
   if not target.any():continue
   base=m[lo:hi];mean=(base[base[:,:,3]>0,:3]@L).mean();rgb=reg[target,:3].astype(int);best=None
   for delta in range(-65,66):
    ix=(((rgb+delta)[:,None]-pal[None])**2).sum(2).argmin(1);c=pal[ix];sm=(reg[fg,:3]@L).sum()-(rgb@L).sum()+(c@L).sum();diff=sm/fg.sum()-mean;key=(max(0,abs(diff)-1.8),abs(delta))
    if best is None or key<best[0]:best=(key,delta,c,diff)
   reg[target,:3]=best[2];a[lo:hi]=reg;row.append({'y':[lo,hi-1],'added_arm_palette_shift':best[1],'luma_delta_after':float(best[3])})
  Image.fromarray(a).save(p);rr.append({'frame':k,'bands':row})
 records[n]=rr
(W/'tone_records.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=1))
