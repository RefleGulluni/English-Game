from pathlib import Path
from PIL import Image
from collections import Counter
import numpy as np,json,colorsys
B=Path(__file__).resolve().parents[1];S=B/'source'
raw=Image.open(S/'01_restored_cells.png').convert('RGB')
# Source250x139 cannot provide256 native columns; use the authorized224x128 crop.
crop=(13,5,237,133);im=raw.crop(crop)
q=im.quantize(colors=40,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
a=np.array(q);pal=np.unique(a.reshape(-1,3),axis=0);lab=np.argmin(((a[:,:,None,:].astype(int)-pal.astype(int)[None,None,:,:])**2).sum(3),axis=2)
def rate(l):return float((l[:,1:]!=l[:,:-1]).mean()*100)
progress=[rate(lab)]
for passno in range(2):
 seen=np.zeros(lab.shape,bool);new=lab.copy();H,W=lab.shape
 counts=np.bincount(lab.reshape(-1),minlength=len(pal))
 for y in range(H):
  for x in range(W):
   if seen[y,x]:continue
   col=int(lab[y,x]);stack=[(x,y)];seen[y,x]=1;comp=[];neighbor=Counter()
   while stack:
    xx,yy=stack.pop();comp.append((xx,yy))
    for nx,ny in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
     if not (0<=nx<W and 0<=ny<H):continue
     nc=int(lab[ny,nx])
     if nc==col and not seen[ny,nx]:seen[ny,nx]=1;stack.append((nx,ny))
     elif nc!=col:neighbor[nc]+=1
   if len(comp)>3:continue
   options=[c for c in neighbor if counts[c]>counts[col] and np.linalg.norm(pal[c].astype(int)-pal[col].astype(int))<=18]
   if not options:continue
   c=max(options,key=lambda c:(neighbor[c],-np.linalg.norm(pal[c].astype(int)-pal[col].astype(int))))
   for xx,yy in comp:new[yy,xx]=c
 lab=new;progress.append(rate(lab))
clean=Image.fromarray(pal[lab]).convert('RGB');clean.save(S/'02_cleaned_crop_native.png')
# Move both axes by half. Outer wraps now are original interior neighbors;
# the discontinuities needing repair are the middle cross.
a=np.array(clean);shift=np.roll(a,(64,112),axis=(0,1));off=Image.fromarray(shift)
off.save(S/'03_half_offset_native.png');off.resize((1344,768),Image.Resampling.NEAREST).save(S/'03_half_offset_6x.png')
im.save(S/'02_crop_native.png')
(S/'02_cleanup_metadata.json').write_text(json.dumps({'crop_xyxy':crop,'native_size':[224,128],'fallback_reason':'Actual restored source250x139; no256 columns.224x128 explicitly authorized.','palette':pal.tolist(),'horizontal_change_progress':progress,'method':'40color no-dither quantization,2 directed small-component merges toward already more common neighboring material tones;area<=3,distance<=18RGB; avoids simultaneous color-swapping distance; no texture generation, blur or resize.','half_offset_xy':[112,64]},indent=2)+'\n')
print('Palette',len(pal),'change progress',progress)
