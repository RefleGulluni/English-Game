"""V2: keep generated geometry; desaturate and calibrate palette, no grain added."""
from pathlib import Path
from PIL import Image
import numpy as np,json
S=Path(__file__).resolve().parent
im=Image.open(S/'01_material_restored_cells.png').convert('RGB');w,h=im.size
x=(w-224)//2;y=(h-128)//2;crop=(x,y,x+224,y+128);im=im.crop(crop);im.save(S/'02_crop_native.png')
a=np.array(im.quantize(colors=32,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB'))
pal,inv,weights=np.unique(a.reshape(-1,3),axis=0,return_inverse=True,return_counts=True)
L=np.array([.2126,.7152,.0722]);lum=pal@L;r,g,b=pal.astype(float).T
roles=np.full(len(pal),'stone',dtype='U8');roles[(g-b>19)&(r-g<8)]='moss';roles[(r-g>=8)&(g-b>13)]='mud'
new=np.empty_like(pal,dtype=float)
v=84+(lum-np.average(lum,weights=weights))
for k in range(len(pal)):
 delta={'stone':[.5,0,-3.5],'moss':[-2,3,-12],'mud':[3,0,-9]}[roles[k]]
 new[k]=v[k]+np.array(delta)
for _ in range(30):
 new+=(np.array([85.,84.,80.])-np.average(new,axis=0,weights=weights))
 value=new@L;mean=np.average(value,weights=weights);std=np.sqrt(np.average((value-mean)**2,weights=weights))
 new+=(value-mean)[:,None]*(13/std-1)
 new=np.minimum(np.maximum(new,[58,58,50]),[118,116,108])
new=np.rint(new).astype('uint8');taken=set()
for k in range(len(new)):
 if tuple(new[k]) in taken:
  for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)]:
   c=new[k].astype(int)+d
   if tuple(c) not in taken:new[k]=c;break
 taken.add(tuple(new[k]))
out=new[inv].reshape(128,224,3);Image.fromarray(out).save(S/'02_cleaned_native.png')
Image.fromarray(out).resize((1344,768),Image.Resampling.NEAREST).save(S/'02_cleaned_6x.png')
shift=np.roll(out,(64,112),axis=(0,1));Image.fromarray(shift).save(S/'03_half_offset_native.png')
Image.fromarray(shift).resize((1344,768),Image.Resampling.NEAREST).save(S/'03_half_offset_6x.png')
meta={'crop_xyxy':crop,'restored_size':[w,h],'palette':new.tolist(),'roles':roles.tolist(),'palette_mapping':[{'from':p.tolist(),'to':n.tolist(),'material':str(k)} for p,n,k in zip(pal,new,roles)],'mean_rgb':out.mean((0,1)).tolist(),'luma_std':float((out@L).std()),'method':'32-color no-dither reduction then injective palette remap by material; RGB mean85,84,80 and Rec709 brightness std13. No art resizing, filtering, added noise or geometry drawing. Half-offset112,64.'}
(S/'02_cleanup_metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print({k:v for k,v in meta.items() if k not in ['palette','roles','palette_mapping']})
