from PIL import Image
from collections import Counter
import numpy as np
LUMA=np.array([.2126,.7152,.0722])
def quiet(lab,pal,roles,passes=2):
 h,w=lab.shape;progress=[]
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
    if len(pts)>3:continue
    options=[k for k in adj if roles[k]==roles[c] and counts[k]>counts[c] and np.linalg.norm(pal[k].astype(float)-pal[c])<=14]
    if options:
     k=max(options,key=lambda k:(adj[k],-np.linalg.norm(pal[k].astype(float)-pal[c])))
     for xx,yy in pts:out[yy,xx]=k
  lab=out;progress.append(float((lab[:,1:]!=lab[:,:-1]).mean()*100))
 return lab,progress
def calibrate(pal,lab,roles):
 weights=np.bincount(lab.ravel(),minlength=len(pal));lum=pal@LUMA;mud=roles=='mud';leaf=~mud
 mean=np.average(lum[mud],weights=weights[mud]);chrom=pal[mud].astype(float)-lum[mud,None];chrom-=np.average(chrom,axis=0,weights=weights[mud])
 fraction=weights[mud].sum()/weights.sum();lo,hi=.05,3.
 for _ in range(40):
  scale=(lo+hi)/2;p=np.empty_like(pal,dtype=float);p[mud]=[61,64,63]+scale*(lum[mud]-mean)[:,None]+.18*chrom
  if leaf.any():p[leaf]=[55,54,51]+.15*(lum[leaf]-np.average(lum[leaf],weights=np.maximum(weights[leaf],1)))[:,None]
  p[mud]+=(np.array([61.,64.,63.])-np.average(p,axis=0,weights=weights))/fraction
  l=p@LUMA;m=np.average(l,weights=weights);sd=np.sqrt(np.average((l-m)**2,weights=weights))
  if sd<9:lo=scale
  else:hi=scale
 p=np.rint(p).clip(0,255).astype('uint8');seen=set()
 for i in range(len(p)):
  if tuple(p[i]) in seen:
   for delta in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
    c=p[i].astype(int)+delta
    if tuple(c) not in seen:p[i]=c;break
  seen.add(tuple(p[i]))
 return p
def cut(cost):
 h,w=cost.shape;dp=cost[0].copy();prev=np.zeros((h,w),int)
 for y in range(1,h):
  row=np.empty(w)
  for x in range(w):
   k=min(range(max(0,x-1),min(w,x+2)),key=lambda k:dp[k]+.05*abs(k-x));row[x]=cost[y,x]+dp[k]+.05*abs(k-x);prev[y,x]=k
  dp=row
 x=int(dp.argmin());p=[x]
 for y in range(h-1,0,-1):x=int(prev[y,x]);p.append(x)
 return np.array(p[::-1])
def match(a,pal):return np.argmin(((a.astype(float)[:,:,None]-pal[None,None].astype(float))**2).sum(3),2)
