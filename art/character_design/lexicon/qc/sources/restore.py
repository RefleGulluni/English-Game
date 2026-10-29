from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math
W=Path('/tmp/english-lexicon-20261029');V=W/'native';V.mkdir(exist_ok=True)
settings={'fall_topdown':(3,2,2.8,2.8),'tip_mid':(1,1,9.3,9.3),'page_turn':(2,2,3.0,3.0),'open_clean':(1,1,7.2,7.2)}
def fg(a):return ~((a[:,:,0]>170)&(a[:,:,2]>150)&(a[:,:,1]<110)&(a[:,:,0].astype(int)-a[:,:,1]>70)&(a[:,:,2].astype(int)-a[:,:,1]>65))
def edges(a,f,axis):
 d=np.abs(np.diff(a.astype(float),axis=axis)).mean(2);m=f[:,1:]&f[:,:-1] if axis==1 else f[1:]&f[:-1];return (d*m).sum(0 if axis==1 else 1)/np.maximum(m.sum(0 if axis==1 else 1),1)
def fit(z,lo,hi,p):
 z=(z-np.median(z))/(np.std(z)+1e-6);N=len(z)+1;score=np.full(N,-1e12);prev=np.full(N,-1,int);mn=max(2,math.floor(p)-1) if ACTIVE!="page_turn" else 3;mx=math.ceil(p)+1
 for j in range(lo,min(lo+mx,hi)):score[j]=z[max(0,j-1)]*1.1
 for j in range(lo+mx,hi):
  for length in range(mn,mx+1):
   k=j-length
   if k<lo:continue
   s=score[k]+z[j-1]*1.1-.8*(length-p)**2
   if s>score[j]:score[j]=s;prev[j]=k
 end=max(range(max(lo,hi-mx),hi),key=lambda j:score[j]);bs=[]
 while end>=lo:bs.append(int(end));end=prev[end]
 return sorted(bs)
palette=np.array(json.loads((W/'world_palette.json').read_text()),int)
for name,(cols,rows,px,py) in settings.items():
 ACTIVE=name
 raw=np.array(Image.open(W/f'{name}_generated.png').convert('RGBA'));a=raw[:,:,:3];h,w=a.shape[:2];D=V/name;D.mkdir(exist_ok=True);records=[]
 for k in range(cols*rows):
  x0,x1=round(k%cols*w/cols),round((k%cols+1)*w/cols);y0,y1=round(k//cols*h/rows),round((k//cols+1)*h/rows);ar=a[y0:y1,x0:x1];f=fg(ar)
  if name=='open_clean':f=raw[y0:y1,x0:x1,3]>127
  yy,xx=np.where(f);xs=fit(edges(ar,f,1),max(0,int(xx.min())-math.ceil(px)),min(ar.shape[1],int(xx.max())+math.ceil(px)+1),px);ys=fit(edges(ar,f,0),max(0,int(yy.min())-math.ceil(py)),min(ar.shape[0],int(yy.max())+math.ceil(py)+1),py)
  out=np.zeros((len(ys)-1,len(xs)-1,4),np.uint8)
  for y in range(len(ys)-1):
   for x in range(len(xs)-1):
    sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
    if f[sy,sx]:
     c=ar[sy,sx].astype(int)
     # Magenta antialias/spill is outside-world contamination, not a new material color.
     if c[0]-c[1]>45 and c[2]-c[1]>45:continue
     idx=np.argmin(((palette-c)**2).sum(1));out[y,x]=[*palette[idx],255]
  im=Image.fromarray(out);bb=im.getbbox();im=im.crop(bb);im.save(D/f'{k+1:02}.png');cx=np.argmin(abs(np.array(xs)-(ar.shape[1]/2)))-bb[0]
  rec={'frame':k+1,'source_cell':[x0,y0,x1,y1],'observed_grid_pitch':[px,py],'x_boundaries':xs,'y_boundaries':ys,'crop_after_restore':list(bb),'native_size':list(im.size),'source_cell_center_native_x':int(cx),'method':'source painted-cell boundaries; one source center point per native pixel; nearest existing source book palette; no whole-art resize'};records.append(rec)
  overlay=Image.fromarray(ar);d=ImageDraw.Draw(overlay)
  for x in xs:d.line((x,ys[0],x,ys[-1]),fill='#ff8080')
  for y in ys:d.line((xs[0],y,xs[-1],y),fill='#ff8080')
  mx=(int(xx.min())+int(xx.max()))//2;my=(int(yy.min())+int(yy.max()))//2;overlay.crop((max(0,mx-72),max(0,my-72),mx+72,my+72)).save(D/f'{k+1:02}_gridcheck.png')
 (D/'grid.json').write_text(json.dumps(records,indent=2));print(name,[r['native_size'] for r in records])
