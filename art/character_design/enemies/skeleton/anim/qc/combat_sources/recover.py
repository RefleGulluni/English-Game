from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
W=Path('/tmp/english-combat-trial-20261028');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game')
def boundaries(z,n):
 length=len(z)+1;p=length/n;z=(z-np.median(z))/(np.std(z)+1e-6);prev={0:(0,[])}
 for k in range(1,n):
  expected=k*p;now={}
  for j in range(max(1,round(expected)-2),min(length-1,round(expected)+2)+1):
   best=None
   for b,(score,path) in prev.items():
    if j<=b:continue
    val=score+z[j-1]-.8*((j-b)-p)**2-.12*(j-expected)**2
    if best is None or val>best[0]:best=(val,path+[j])
   now[j]=best
  prev=now
 end=max(prev,key=lambda j:prev[j][0]-.8*(length-j-p)**2)
 return [0]+prev[end][1]+[length]
for name,fw,cols,rows in [('hero',96,4,2),('skeleton',160,3,3)]:
 a=np.array(Image.open(W/(name+'_generated.png')).convert('RGB'));c=a.astype(int);fg=~((c[:,:,0]>150)&(c[:,:,2]>130)&(c[:,:,1]<130)&(c[:,:,0]-c[:,:,1]>60)&(c[:,:,2]-c[:,:,1]>50))
 z=[]
 for axis in [1,0]:
  d=np.abs(np.diff(a.astype(float),axis=axis)).mean(2);m=fg[:,1:]&fg[:,:-1] if axis==1 else fg[1:]&fg[:-1];z.append((d*m).sum(0 if axis==1 else 1)/np.maximum(m.sum(0 if axis==1 else 1),1))
 xs=boundaries(z[0],fw*cols);ys=boundaries(z[1],96*rows);cx=np.array([(a+b)//2 for a,b in zip(xs,xs[1:])]);cy=np.array([(a+b)//2 for a,b in zip(ys,ys[1:])]);out=np.zeros((rows*96,cols*fw,4),np.uint8);out[:,:,:3]=a[cy[:,None],cx[None,:]];out[:,:,3]=fg[cy[:,None],cx[None,:]]*255;out[out[:,:,3]==0]=0
 if name=='hero':pal=np.unique(np.concatenate([np.array(Image.open(R/'art/character_design'/('hero_B1_'+d+'.png')).convert('RGBA')).reshape(-1,4) for d in ['front_straight','back','left','right']]),axis=0);pal=pal[pal[:,3]>0,:3]
 else:pal=np.array(json.loads((R/'art/character_design/enemies/skeleton/anim/qc/v2_sources/palette.json').read_text()))
 rgb=out[out[:,:,3]>0,:3].astype(int);ix=((rgb[:,None]-pal.astype(int)[None])**2).sum(2).argmin(1);out[out[:,:,3]>0,:3]=pal[ix];Image.fromarray(out).save(W/(name+'_restored.png'));Image.fromarray(out).resize((out.shape[1]*3,out.shape[0]*3),Image.Resampling.NEAREST).save(W/(name+'_restored3x.png'))
 (W/(name+'_grid.json')).write_text(json.dumps({'x_boundaries':xs,'y_boundaries':ys,'expected_native_grid':[fw*cols,96*rows],'method':'Observed cell-edge energy aligned to reference cell pitch using monotonic boundaries; cell-center samples; no wholeimage resize, interpolation or averaging; palette nearest canonical colors.'},indent=2))
 for k in range(cols*rows):
  cell=out[k//cols*96:(k//cols+1)*96,k%cols*fw:(k%cols+1)*fw];Image.fromarray(cell).save(W/f'{name}_{k+1:02}.png')
 # Source-pixel grid overlay to expose local inference.
 ov=Image.fromarray(a);dr=ImageDraw.Draw(ov)
 for x in xs:dr.line((x,0,x,a.shape[0]),fill='#ff8080')
 for y in ys:dr.line((0,y,a.shape[1],y),fill='#ff8080')
 ov.crop((a.shape[1]//3-80,20,a.shape[1]//3+120,220)).save(W/(name+'_gridcheck.png'))
 print(name,'native canvas',out.shape[1],out.shape[0])
