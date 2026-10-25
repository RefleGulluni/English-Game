from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
W=Path('/tmp/english-game-props-batch2-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game')
s=(R/'art/cemetery_v3/props/source/round2/recover_all.py').read_text();exec(s[s.index('def edges('):s.index('res={}')])
def period(z):
 z=z-z.mean();ac=np.correlate(z,z,'full')[len(z)-1:];ac/=max(ac[0],1)
 peaks=[k for k in range(6,min(80,len(ac)-1)) if ac[k]>=ac[k-1] and ac[k]>=ac[k+1]]
 best=max(peaks,key=lambda k:ac[k]);near=[k for k in peaks if ac[k]>.80*ac[best]]
 return min(near),[(k,round(float(ac[k]),3)) for k in peaks]
def recover(name,path,p_override=None):
 a=np.array(Image.open(path).convert('RGB'));fg=~((a[:,:,0]>170)&(a[:,:,2]>150)&(a[:,:,1]<110)&(a[:,:,0].astype(int)-a[:,:,1].astype(int)>70)&(a[:,:,2].astype(int)-a[:,:,1].astype(int)>65));yy,xx=np.where(fg);zx=edges(a,fg,1);zy=edges(a,fg,0)
 px,acx=period(zx);py,acy=period(zy)
 if p_override:px=py=p_override
 xs=fit(zx,max(0,int(xx.min())-px),min(a.shape[1],int(xx.max())+px+1),px);ys=fit(zy,max(0,int(yy.min())-py),min(a.shape[0],int(yy.max())+py+1),py);out=np.zeros((len(ys)-1,len(xs)-1,4),dtype=np.uint8)
 for y in range(len(ys)-1):
  for x in range(len(xs)-1):
   sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
   if fg[sy,sx]:out[y,x,:3]=a[sy,sx];out[y,x,3]=255
 d=W/'recovered'/name;d.mkdir(parents=True,exist_ok=True);Image.fromarray(out).save(d/'restored_native.png')
 rec={'source':str(path),'source_size':[a.shape[1],a.shape[0]],'native_size':[out.shape[1],out.shape[0]],'period':[px,py],'acf_peaks':[acx,acy],'x_boundaries':xs,'y_boundaries':ys};(d/'grid.json').write_text(json.dumps(rec,indent=2));ov=Image.fromarray(a);dr=ImageDraw.Draw(ov)
 for x in xs:dr.line([(x,ys[0]),(x,ys[-1])],fill='#FF8080')
 for y in ys:dr.line([(xs[0],y),(xs[-1],y)],fill='#FF8080')
 cx=int((xx.min()+xx.max())/2);cy=int((yy.min()+yy.max())/2);ov.crop((cx-120,cy-120,cx+120,cy+120)).save(d/'grid_check_1x.png');print(name,'native',out.shape,'period',px,py)
 return out
if __name__=='__main__':
 g=json.loads((W/'tilt_generation.json').read_text());a=recover('tombstone_upright_01_tilted',g['source']);Image.fromarray(a).resize((a.shape[1]*6,a.shape[0]*6),Image.Resampling.NEAREST).save(W/'tilt_restored_6x.png')
