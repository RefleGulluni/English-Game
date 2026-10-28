from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
W=Path('/tmp/english-combat-trial-20261028');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game')
exec((W/'recover.py').read_text().split('for name,fw,cols,rows in')[0])
a=np.array(Image.open(W/'hit_generated.png').convert('RGB'));c=a.astype(int);fg=~((c[:,:,0]>150)&(c[:,:,2]>130)&(c[:,:,1]<130)&(c[:,:,0]-c[:,:,1]>60)&(c[:,:,2]-c[:,:,1]>50));zs=[]
for axis in [1,0]:
 d=np.abs(np.diff(a.astype(float),axis=axis)).mean(2);m=fg[:,1:]&fg[:,:-1] if axis==1 else fg[1:]&fg[:-1];zs.append((d*m).sum(0 if axis==1 else 1)/np.maximum(m.sum(0 if axis==1 else 1),1))
xs=boundaries(zs[0],160);ys=boundaries(zs[1],96);cx=np.array([(a+b)//2 for a,b in zip(xs,xs[1:])]);cy=np.array([(a+b)//2 for a,b in zip(ys,ys[1:])]);out=np.zeros((96,160,4),np.uint8);out[:,:,:3]=a[cy[:,None],cx[None,:]];out[:,:,3]=fg[cy[:,None],cx[None,:]]*255;out[out[:,:,3]==0]=0
pal=np.array(json.loads((R/'art/character_design/enemies/skeleton/anim/qc/v2_sources/palette.json').read_text()),int);rgb=out[out[:,:,3]>0,:3].astype(int);ix=((rgb[:,None]-pal[None])**2).sum(2).argmin(1);out[out[:,:,3]>0,:3]=pal[ix];Image.fromarray(out).save(W/'hit_restored.png');(W/'hit_grid.json').write_text(json.dumps({'x_boundaries':xs,'y_boundaries':ys,'native_size':[160,96],'sampling':'One actual grid cell center point per native pixel; matched to observed edge positions.'},indent=2))
Image.fromarray(out).resize((1280,768),Image.Resampling.NEAREST).save(W/'hit_restored8x.png')
