"""Native crop, no-dither palette cleanup, and half-offset for seam editing."""
from pathlib import Path
from PIL import Image
from collections import Counter
import numpy as np,json
S=Path(__file__).resolve().parent
im=Image.open(S/'02_material_restored_cells.png').convert('RGB');w,h=im.size
assert w>=224 and h>=128
x=(w-224)//2;y=(h-128)//2;crop=(x,y,x+224,y+128);im=im.crop(crop)
im.save(S/'03_crop_native.png')
q=im.quantize(colors=32,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB');a=np.array(q);pal=np.unique(a.reshape(-1,3),axis=0)
lab=np.argmin(((a.astype(float)[:,:,None,:]-pal[None,None,:,:])**2).sum(3),axis=2)
def rate(l):return float((l[:,1:]!=l[:,:-1]).mean()*100)
progress=[rate(lab)]
for passno in range(2):
 if rate(lab)<=70:break
 counts=np.bincount(lab.ravel(),minlength=len(pal));seen=np.zeros(lab.shape,bool);out=lab.copy();H,W=lab.shape
 for yy in range(H):
  for xx in range(W):
   if seen[yy,xx]:continue
   c=int(lab[yy,xx]);stack=[(xx,yy)];seen[yy,xx]=True;pts=[];adj=Counter()
   while stack:
    cx,cy=stack.pop();pts.append((cx,cy))
    for nx,ny in [(cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)]:
     if not(0<=nx<W and 0<=ny<H):continue
     nc=int(lab[ny,nx])
     if nc==c and not seen[ny,nx]:seen[ny,nx]=1;stack.append((nx,ny))
     elif nc!=c:adj[nc]+=1
   if len(pts)>3:continue
   choices=[k for k in adj if counts[k]>counts[c] and np.linalg.norm(pal[k].astype(float)-pal[c])<=18]
   if not choices:continue
   k=max(choices,key=lambda k:(adj[k],-np.linalg.norm(pal[k].astype(float)-pal[c])))
   for cx,cy in pts:out[cy,cx]=k
 lab=out;progress.append(rate(lab))
used,counts=np.unique(lab,return_counts=True);old=pal[used].astype(float);L=old@np.array([.2126,.7152,.0722]);meanL=float(np.average(L,weights=counts));chrom=old-L[:,None];chrom-=np.average(chrom,axis=0,weights=counts)
new=np.array([92.,87.,73.])+.70*(L-meanL)[:,None]+.30*chrom;new=np.rint(new).clip(0,255).astype('uint8')
seen=set()
for i in range(len(new)):
 if tuple(new[i]) in seen:
  for delta in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
   n=new[i].astype(int)+np.array(delta)
   if tuple(n) not in seen:new[i]=n;break
 seen.add(tuple(new[i]))
lookup=pal.copy()
for k,c in zip(used,new):lookup[k]=c
clean=lookup[lab];Image.fromarray(clean).save(S/'03_cleaned_native.png')
shift=np.roll(clean,(64,112),axis=(0,1));Image.fromarray(shift).save(S/'04_half_offset_native.png');Image.fromarray(shift).resize((1344,768),Image.Resampling.NEAREST).save(S/'04_half_offset_6x.png')
Image.fromarray(clean).resize((1344,768),Image.Resampling.NEAREST).save(S/'03_cleaned_6x.png')
meta={'restored_size':[w,h],'crop_xyxy':list(crop),'size':[224,128],'colors':len(np.unique(clean.reshape(-1,3),axis=0)),'horizontal_change_progress':progress,'final_horizontal_change':rate(lab),'mean_rgb':clean.mean(axis=(0,1)).tolist(),'palette':new.tolist(),'palette_mapping':[{'from':c.astype(int).tolist(),'to':n.tolist()} for c,n in zip(old,new)],'method':'32color no-dither reduction; at most2 directed merges of <=3px components into already more common adjacent material colors within18RGB distance; then material palette calibrated to92,87,73 preserving texture categories. No noise, blur or image scaling. Half-offset112,64 for AI cross repair.'}
(S/'03_cleanup_metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print({k:v for k,v in meta.items() if k not in ['palette','palette_mapping','method']})
