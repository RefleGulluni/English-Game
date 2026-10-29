"""Native source-pixel cleanup and palette operations only; never synthesize texture."""
from PIL import Image
from collections import Counter
import numpy as np
LUMA=np.array([.2126,.7152,.0722])
def groups(mask):
 seen=set();h,w=mask.shape
 for y,x in zip(*np.where(mask)):
  if (x,y) in seen:continue
  todo=[(x,y)];seen.add((x,y));pts=[]
  while todo:
   xx,yy=todo.pop();pts.append((xx,yy))
   for ny in range(max(0,yy-1),min(h,yy+2)):
    for nx in range(max(0,xx-1),min(w,xx+2)):
     if mask[ny,nx] and (nx,ny) not in seen:seen.add((nx,ny));todo.append((nx,ny))
  yield pts
def small_lichen(mask):
 keep=np.zeros_like(mask)
 for pts in groups(mask):
  center=np.mean(pts,axis=0);ordered=sorted(pts,key=lambda p:np.linalg.norm(np.array(p)-center))
  for x,y in ordered[:2]:keep[y,x]=True
 return keep
def quiet(lab,pal,passes=2):
 progress=[];h,w=lab.shape
 for _ in range(passes):
  counts=np.bincount(lab.ravel(),minlength=len(pal));seen=np.zeros(lab.shape,bool);out=lab.copy()
  for y in range(h):
   for x in range(w):
    if seen[y,x]:continue
    c=int(lab[y,x]);todo=[(x,y)];seen[y,x]=True;pts=[];adj=Counter()
    while todo:
     xx,yy=todo.pop();pts.append((xx,yy))
     for nx,ny in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
      if not(0<=nx<w and 0<=ny<h):continue
      k=int(lab[ny,nx])
      if k==c and not seen[ny,nx]:seen[ny,nx]=True;todo.append((nx,ny))
      elif k!=c:adj[k]+=1
    if c>=30 or len(pts)>3:continue
    choices=[k for k in adj if k<30 and counts[k]>counts[c] and np.linalg.norm(pal[k].astype(float)-pal[c])<=14]
    if choices:
     k=max(choices,key=lambda k:(adj[k],-np.linalg.norm(pal[k].astype(float)-pal[c])))
     for xx,yy in pts:out[yy,xx]=k
  lab=out;progress.append(float((lab[:,1:]!=lab[:,:-1]).mean()*100))
 return lab,progress
def calibrated(pal,lab):
 counts=np.bincount(lab.ravel(),minlength=32);lum=pal[:30]@LUMA
 mean=np.average(lum,weights=counts[:30]);chrom=pal[:30].astype(float)-lum[:,None];chrom-=np.average(chrom,axis=0,weights=counts[:30])
 fraction=counts[:30].sum()/counts.sum();lo,hi=.1,3.
 for _ in range(45):
  scale=(lo+hi)/2;p=np.empty((32,3),float)
  p[:30]=[59,69,55]+scale*(lum-mean)[:,None]+.10*chrom
  p[30:]=[[96,101,96],[103,106,100]]
  p[:30]+=(np.array([59.,69.,55.])-np.average(p,axis=0,weights=counts))/fraction
  value=p@LUMA;m=np.average(value,weights=counts);sd=np.sqrt(np.average((value-m)**2,weights=counts))
  if sd<11.5:lo=scale
  else:hi=scale
 p=np.rint(p).clip(0,255).astype('uint8');seen=set()
 for i in range(len(p)):
  if tuple(p[i]) in seen:
   for delta in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
    c=p[i].astype(int)+delta
    if tuple(c) not in seen:p[i]=c;break
  seen.add(tuple(p[i]))
 return p
