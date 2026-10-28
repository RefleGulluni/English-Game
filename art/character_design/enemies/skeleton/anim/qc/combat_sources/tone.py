from pathlib import Path
from PIL import Image
import numpy as np,json
W=Path('/tmp/english-combat-trial-20261028');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');L=np.array([.299,.587,.114]);records={}
for name,ref,folder,layer in [('hero_B1_cast_right','art/character_design/hero_B1_right.png','hero_layers','casting_arm'),('skeleton_B_attack_right','art/character_design/enemies/skeleton/skeleton_B_right.png','skeleton_layers','attacking_arm')]:
 m=np.array(Image.open(R/ref).convert('RGBA'));pal=np.unique(m[m[:,:,3]>0,:3],axis=0).astype(int);rows=[]
 if name.startswith('skeleton'):arm=np.array(Image.open(R/'art/character_design/enemies/skeleton/anim/qc/v5_sources/standing_parts/near_right_arm.png'));pal=np.unique(arm[arm[:,:,3]>0,:3],axis=0).astype(int)
 for p in sorted((W/'staged/frames'/name).glob('*.png')):
  a=np.array(Image.open(p).convert('RGBA'));k=int(p.stem);n=len(list((W/'staged/frames'/name).glob('*.png')))
  if k in [1,n]:rows.append({'frame':k,'changes':[]});continue
  mask=np.array(Image.open(W/'staged/qc/combat_sources'/folder/f'{k:02}_{layer}.png'))[:,:,3]>0;changed=[]
  for y0,y1 in [(0,20),(20,45),(45,65),(65,96)]:
   band=m[y0:y1];base=band[band[:,:,3]>0,:3]@L;mean=base.mean();fb=a[y0:y1,:,3]>0;target=mask[y0:y1]&fb
   if not target.any():continue
   rgb=a[y0:y1,:,:3][target].astype(int);ids=[];best=None
   for delta in range(-55,56):
    proposed=rgb+delta;dist=((proposed[:,None]-pal[None])**2).sum(2);ix=dist.argmin(1);v=pal[ix];sm=(a[y0:y1,:,:3][fb]@L).sum()-(rgb@L).sum()+(v@L).sum();diff=sm/fb.sum()-mean;key=(max(0,abs(diff)-1.8),abs(delta))
    if best is None or key<best[0]:best=(key,delta,v,diff)
   v=best[2];reg=a[y0:y1,:,:3];reg[target]=v;changed.append({'band':[y0,y1],'generated_arm_palette_shift':best[1],'band_luma_delta_after':round(float(best[3]),3)})
  Image.fromarray(a).save(p);rows.append({'frame':k,'changes':changed})
 records[name]=rows
 frames=[Image.open(p) for p in sorted((W/'staged/frames'/name).glob('*.png'))];fw=frames[0].width;strip=Image.new('RGBA',(fw*len(frames),96));board=Image.new('RGBA',(4*(fw+8),((len(frames)+3)//4)*112),'#403d43')
 for k,im in enumerate(frames):strip.alpha_composite(im,(k*fw,0));board.alpha_composite(im,(k%4*(fw+8),k//4*112))
 strip.save(W/'staged'/(name+'.png'));board.resize((board.width*3,board.height*3),Image.Resampling.NEAREST).save(W/(name+'_tone3x.png'))
(W/'tone_records.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=1))

# Preserve the rigid pelvis; choose only the flexible hanging cloth's existing material colors when the now-raised hand leaves the waist band.
m=np.array(Image.open(R/'art/character_design/enemies/skeleton/skeleton_B_right.png'));v=m[48:65,44:61];pal=np.unique(v[v[:,:,3]>0,:3],axis=0).astype(int);clothrecords=[]
for p in sorted((W/'staged/frames/skeleton_B_attack_right').glob('*.png')):
 a=np.array(Image.open(p));base=m[45:65];mean=(base[base[:,:,3]>0,:3]@L).mean();reg=a[45:65];fg=reg[:,:,3]>0;d=(reg[fg,:3]@L).mean()-mean
 if abs(d)<=2:continue
 yy,xx=np.indices(reg.shape[:2]);mask=fg&(yy>=3)&(xx>=78)&(xx<92);rgb=reg[mask,:3].astype(int);best=None
 for delta in range(-12,13):
  ix=(((rgb+delta)[:,None]-pal[None])**2).sum(2).argmin(1);c=pal[ix];sm=(reg[fg,:3]@L).sum()-(rgb@L).sum()+(c@L).sum();diff=sm/fg.sum()-mean;key=(max(0,abs(diff)-1.8),abs(delta))
  if best is None or key<best[0]:best=(key,delta,c,diff)
 reg[mask,:3]=best[2];a[45:65]=reg;Image.fromarray(a).save(p);clothrecords.append({'frame':int(p.stem),'region':'flexible lower shroud y48..64, x78..91 (160canvas)','palette_from':'standard shroud y48..64 x44..60','palette_shift':best[1],'waist_mean_delta':float(best[3])})
(W/'cloth_tone_records.json').write_text(json.dumps(clothrecords,indent=2))
