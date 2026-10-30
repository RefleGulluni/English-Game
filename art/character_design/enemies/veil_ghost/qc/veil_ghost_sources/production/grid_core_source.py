from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json
W=Path('/tmp/english-game-props-complete-20261025');G=json.loads((W/'generation.json').read_text());D=W/'restored';D.mkdir(exist_ok=True)
def edges(a,fg,axis):
 d=np.abs(np.diff(a.astype(float),axis=axis)).mean(2);m=fg[:,1:]&fg[:,:-1] if axis==1 else fg[1:]&fg[:-1]
 z=(d*m).sum(0 if axis==1 else 1)/np.maximum(m.sum(0 if axis==1 else 1),1)
 return z

def period(z):
 z=z-z.mean();ac=np.correlate(z,z,'full')[len(z)-1:];ac/=max(ac[0],1)
 peaks=[k for k in range(6,25) if ac[k]>=ac[k-1] and ac[k]>=ac[k+1]]
 best=max(peaks,key=lambda k:ac[k]);near=[k for k in peaks if ac[k]>.80*ac[best]]
 return min(near),[(k,round(float(ac[k]),3)) for k in peaks]
def fit(z,lo,hi,p):
 z=(z-np.median(z))/(np.std(z)+1e-6);N=len(z)+1;score=np.full(N,-1e12);prev=np.full(N,-1,dtype=int);mn=max(4,p-2);mx=p+2
 for j in range(lo,min(lo+mx,hi)):score[j]=z[max(0,j-1)]*1.4
 for j in range(lo+mx,hi):
  for length in range(mn,mx+1):
   k=j-length
   if k<lo:continue
   s=score[k]+z[j-1]*1.4-.30*(length-p)**2
   if s>score[j]:score[j]=s;prev[j]=k
 end=max(range(max(lo,hi-mx),hi),key=lambda j:score[j]);bs=[]
 while end>=lo:bs.append(int(end));end=prev[end]
 return sorted(bs)
res={}
for n,pth in G['raw'].items():
 a=np.array(Image.open(pth).convert('RGB'));fg=~((a[:,:,0]>170)&(a[:,:,2]>150)&(a[:,:,1]<110)&(a[:,:,0].astype(int)-a[:,:,1].astype(int)>70)&(a[:,:,2].astype(int)-a[:,:,1].astype(int)>65));yy,xx=np.where(fg)
 zx=edges(a,fg,1);zy=edges(a,fg,0);px,acx=period(zx);py,acy=period(zy)
 xs=fit(zx,max(0,int(xx.min())-px),min(a.shape[1],int(xx.max())+px+1),px);ys=fit(zy,max(0,int(yy.min())-py),min(a.shape[0],int(yy.max())+py+1),py)
 out=np.zeros((len(ys)-1,len(xs)-1,4),dtype=np.uint8)
 for y in range(len(ys)-1):
  for x in range(len(xs)-1):
   sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
   if fg[sy,sx]:out[y,x,:3]=a[sy,sx];out[y,x,3]=255
 Image.fromarray(out).save(D/(n+'.png'))
 ov=Image.fromarray(a);dr=ImageDraw.Draw(ov)
 for x in xs:dr.line([(x,ys[0]),(x,ys[-1])],fill='#FF8080')
 for y in ys:dr.line([(xs[0],y),(xs[-1],y)],fill='#FF8080')
 # A 240x240 original-pixel crop, no scale, to audit grid inference.
 cx=int((xx.min()+xx.max())/2);cy=int((yy.min()+yy.max())/2);ov.crop((cx-120,cy-120,cx+120,cy+120)).save(D/(n+'_grid_check.png'))
 rec={'source':pth,'source_size':[a.shape[1],a.shape[0]],'period':[px,py],'autocorrelation_peaks':[acx,acy],'x_boundaries':xs,'y_boundaries':ys,'native_size':[out.shape[1],out.shape[0]],'mapping':'Detected painted cell -> center source point -> one native pixel. No global resize, no interpolation.'}
 (D/(n+'_grid.json')).write_text(json.dumps(rec,indent=2));res[n]=rec
 print(n,'source',a.shape,'period',px,py,'native',out.shape[:2], 'peaks',acx,acy)
(W/'recovery_index.json').write_text(json.dumps(res,indent=2))
# Preview only, integer nearest.
sheet=Image.new('RGBA',(600,600),'#403D3F');dr=ImageDraw.Draw(sheet)
for k,n in enumerate(res):
 im=Image.open(D/(n+'.png'));x=k%3*200;y=k//3*200;sheet.alpha_composite(im,(x+(200-im.width)//2,y+165-im.height));dr.text((x+2,y+174),n,fill='white')
sheet.resize((1200,1200),Image.Resampling.NEAREST).save(W/'restored_review_2x.png')
