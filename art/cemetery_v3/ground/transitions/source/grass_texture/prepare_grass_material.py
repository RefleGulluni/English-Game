"""Native vegetation material: preserve straw/moss/soil while quieting close shades."""
from pathlib import Path
from PIL import Image
from collections import Counter
import numpy as np,json
S=Path(__file__).resolve().parent
im=Image.open(S/'01_material_restored_cells.png').convert('RGB');w,h=im.size;assert w>=224 and h>=128
x=(w-224)//2;y=(h-128)//2;crop=(x,y,x+224,y+128);im=im.crop(crop);im.save(S/'02_crop_native.png')
q=im.quantize(colors=32,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB');a=np.array(q);pal=np.unique(a.reshape(-1,3),axis=0);L=pal@np.array([.2126,.7152,.0722]);r,g,b=pal.astype(int).T
roles=np.full(len(pal),'soil',dtype='U6');roles[(g>r+1)&(g>b+7)]='moss';roles[(r>=g)&(g>b+9)&(L>=53)]='straw'
lab=np.argmin(((a.astype(float)[:,:,None,:]-pal[None,None,:,:])**2).sum(3),axis=2)
def rate(l):return float((l[:,1:]!=l[:,:-1]).mean()*100)
progress=[rate(lab)]
for iteration in range(3):
 if rate(lab)<=72:break
 counts=np.bincount(lab.ravel(),minlength=len(pal));seen=np.zeros(lab.shape,bool);out=lab.copy()
 for yy in range(128):
  for xx in range(224):
   if seen[yy,xx]:continue
   c=int(lab[yy,xx]);todo=[(xx,yy)];seen[yy,xx]=1;pts=[];adj=Counter()
   while todo:
    cx,cy=todo.pop();pts.append((cx,cy))
    for nx,ny in [(cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)]:
     if not(0<=nx<224 and 0<=ny<128):continue
     k=int(lab[ny,nx])
     if k==c and not seen[ny,nx]:seen[ny,nx]=1;todo.append((nx,ny))
     elif k!=c:adj[k]+=1
   if len(pts)>3:continue
   choices=[k for k in adj if roles[k]==roles[c] and counts[k]>counts[c] and np.linalg.norm(pal[k].astype(float)-pal[c])<=18]
   if not choices:continue
   k=max(choices,key=lambda k:(adj[k],-np.linalg.norm(pal[k].astype(float)-pal[c])))
   for cx,cy in pts:out[cy,cx]=k
 lab=out;progress.append(rate(lab))
used,counts=np.unique(lab,return_counts=True);old=pal[used].astype(float);lum=L[used];role=roles[used];new=np.empty_like(old)
for kind,center,scale in [('moss',[58,66,48],.45),('soil',[56,58,47],.48),('straw',[88,84,63],.48)]:
 m=role==kind
 if not m.any():continue
 mean=float(np.average(lum[m],weights=counts[m]));new[m]=np.array(center)+scale*(lum[m]-mean)[:,None]
highlight=(role=='straw')&(lum>=125)
if highlight.any():
 hm=float(np.average(lum[highlight],weights=counts[highlight]));d=np.clip(.12*(lum[highlight]-hm),-2,2);new[highlight]=np.array([107,103,77])+d[:,None]
# Keep the explicitly requested straw highlights fixed while calibrating the
# much larger moss/soil/ordinary-straw mass to the dark green overall average.
fraction=counts[~highlight].sum()/counts.sum();error=np.array([67.,71.,55.])-np.average(new,axis=0,weights=counts);new[~highlight]+=error/fraction
new=np.rint(new).clip(0,255).astype('uint8');seen=set()
for i in range(len(new)):
 if tuple(new[i]) in seen:
  for delta in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
   n=new[i].astype(int)+np.array(delta)
   if tuple(n) not in seen:new[i]=n;break
 seen.add(tuple(new[i]))
lookup=pal.copy()
for k,c in zip(used,new):lookup[k]=c
source_progress=progress.copy();material_progress=[rate(lab)]
# Compare near-colors in the delivered, desaturated palette as well. This
# preserves the exact straw/moss/soil mask and does not erase a short strand.
for iteration in range(3):
 if rate(lab)<=72:break
 counts0=np.bincount(lab.ravel(),minlength=len(pal));visited=np.zeros(lab.shape,bool);result=lab.copy()
 for yy in range(128):
  for xx in range(224):
   if visited[yy,xx]:continue
   c=int(lab[yy,xx]);todo=[(xx,yy)];visited[yy,xx]=1;pts=[];adj=Counter()
   while todo:
    cx,cy=todo.pop();pts.append((cx,cy))
    for nx,ny in [(cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)]:
     if not(0<=nx<224 and 0<=ny<128):continue
     k=int(lab[ny,nx])
     if k==c and not visited[ny,nx]:visited[ny,nx]=1;todo.append((nx,ny))
     elif k!=c:adj[k]+=1
   if len(pts)>5:continue
   choices=[k for k in adj if roles[k]==roles[c] and counts0[k]>counts0[c] and np.linalg.norm(lookup[k].astype(float)-lookup[c])<=(12 if iteration<2 else 18)]
   if choices:
    k=max(choices,key=lambda k:(adj[k],-np.linalg.norm(lookup[k].astype(float)-lookup[c])))
    for cx,cy in pts:result[cy,cx]=k
 lab=result;material_progress.append(rate(lab));progress.append(rate(lab))
used,counts=np.unique(lab,return_counts=True);old=pal[used].astype(float);lum=L[used];role=roles[used];highlight=(role=='straw')&(lum>=125)
new=lookup[used].astype(float);fraction=counts[~highlight].sum()/counts.sum();new[~highlight]+=(np.array([67.,71.,55.])-np.average(new,axis=0,weights=counts))/fraction
new=np.rint(new).clip(0,255).astype('uint8');seen=set()
for i in range(len(new)):
 if tuple(new[i]) in seen:
  for delta in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
   n=new[i].astype(int)+np.array(delta)
   if tuple(n) not in seen:new[i]=n;break
 seen.add(tuple(new[i]))
for k,c in zip(used,new):lookup[k]=c
clean=lookup[lab];Image.fromarray(clean).save(S/'02_cleaned_native.png');Image.fromarray(clean).resize((1344,768),Image.Resampling.NEAREST).save(S/'02_cleaned_6x.png')
shift=np.roll(clean,(64,112),axis=(0,1));Image.fromarray(shift).save(S/'03_half_offset_native.png');Image.fromarray(shift).resize((1344,768),Image.Resampling.NEAREST).save(S/'03_half_offset_6x.png')
meta={'restored_size':[w,h],'crop_xyxy':list(crop),'size':[224,128],'colors':len(np.unique(clean.reshape(-1,3),axis=0)),'horizontal_change_progress':progress,'source_palette_merge_progress':source_progress,'delivered_palette_merge_progress':material_progress,'mean_rgb':clean.mean((0,1)).tolist(),'palette':new.tolist(),'palette_roles':role.tolist(),'highlight_palette_indices':np.where(highlight)[0].tolist(),'palette_mapping':[{'from':c.astype(int).tolist(),'to':n.tolist(),'material':str(k),'highlight':bool(v)} for c,n,k,v in zip(old,new,role,highlight)],'method':'32color no-dither reduction; directed near-color merging within SAME material class only: <=3px source components/distance18RGB up to3passes; <=5px delivered-palette components/distance12RGB for2passes plus1 distance18RGB pass if still over72%. Exact material class mask preserved. Dark mean67,71,55; straw highlights fixed near107,103,77. No added strands, noise, blur or resampling. Half-offset112,64.'}
(S/'02_cleanup_metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print({k:v for k,v in meta.items() if k not in ['palette','palette_mapping','method','palette_roles']})
print('Material pixel fractions:',{kind:float(counts[role==kind].sum()/counts.sum()) for kind in set(role)})
