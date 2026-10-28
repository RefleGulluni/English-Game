"""Restore-derived pixel material; palette only, no drawn or resampled texture."""
from pathlib import Path
from PIL import Image
import numpy as np,json
S=Path(__file__).resolve().parent
im=Image.open(S/'03_material_restored_cells.png').convert('RGB').crop((16,8,240,136))
im.save(S/'04_crop_native.png')
a=np.array(im.quantize(colors=32,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB'))
pal,inv,weights=np.unique(a.reshape(-1,3),axis=0,return_inverse=True,return_counts=True)
lum=pal@np.array([.2126,.7152,.0722]);roles=np.where(lum<53,'joint',np.where(lum<76,'moss_mud','stone'))
new=np.empty_like(pal,dtype=float)
for k in range(len(pal)):
 l=lum[k]
 if roles[k]=='joint':new[k]=np.array([47,48,43])+.28*(l-45)
 elif roles[k]=='moss_mud':new[k]=np.array([59,63,48])+.5*(l-63)
 else:new[k]=np.array([98,97,93])+.77*(l-100)
stone=roles=='stone'
for _ in range(30):
 error=np.array([85.,84.,80.])-np.average(new,axis=0,weights=weights)
 new[stone]+=error/(weights[stone].sum()/weights.sum())
 new[stone]=np.minimum(new[stone],[118,116,108])
new=np.rint(new).astype('uint8');taken=set()
for k in range(len(new)):
 if tuple(new[k]) in taken:
  for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)]:
   c=new[k].astype(int)+d
   if tuple(c) not in taken:new[k]=c;break
 taken.add(tuple(new[k]))
out=new[inv].reshape(128,224,3)
Image.fromarray(out).save(S/'04_cleaned_native.png')
Image.fromarray(out).resize((1344,768),Image.Resampling.NEAREST).save(S/'04_cleaned_6x.png')
shift=np.roll(out,(64,112),axis=(0,1))
Image.fromarray(shift).save(S/'05_half_offset_native.png')
Image.fromarray(shift).resize((1344,768),Image.Resampling.NEAREST).save(S/'05_half_offset_6x.png')
meta={'crop_xyxy':[16,8,240,136],'palette':new.tolist(),'roles':roles.tolist(),'palette_mapping':[{'from':p.tolist(),'to':n.tolist(),'material':str(r)} for p,n,r in zip(pal,new,roles)],'mean_rgb':out.mean((0,1)).tolist(),'horizontal_change':float(np.any(out[:,1:]!=out[:,:-1],2).mean()*100),'method':'One center per observed cell, integer crop;32-color median cut without dithering; one-to-one material palette remap, no new texture, no filtering. Half offset112,64.'}
(S/'04_cleanup_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
print({k:v for k,v in meta.items() if k not in ['palette','roles','palette_mapping']})
