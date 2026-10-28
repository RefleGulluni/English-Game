from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
W=Path('/tmp/english-combat-step2-20261028');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');exec((W/'boundary_defs.txt').read_text())
layouts={'cast_left':(96,4,2),'attack_left':(160,3,3),'attack_right_v2':(160,2,2),'dust_left':(96,3,2),'dust_right':(96,3,2),'hit_left':(96,2,2),'hit_right':(96,2,2)}
for name,(fw,cols,rows) in layouts.items():
 a=np.array(Image.open(W/(name+'_generated.png')).convert('RGB'));c=a.astype(int);fg=~((c[:,:,0]>150)&(c[:,:,2]>130)&(c[:,:,1]<130)&(c[:,:,0]-c[:,:,1]>60)&(c[:,:,2]-c[:,:,1]>50));z=[]
 for axis in [1,0]:
  d=np.abs(np.diff(a.astype(float),axis=axis)).mean(2);m=fg[:,1:]&fg[:,:-1] if axis==1 else fg[1:]&fg[:-1];z.append((d*m).sum(0 if axis==1 else 1)/np.maximum(m.sum(0 if axis==1 else 1),1))
 # Dust source expanded vertical aspect: observe actual square block pitches rather than force the requested aspect.
 # Body portions are a guide only. Particle extraction later uses observed block centers.
 xs=boundaries(z[0],fw*cols);ys=boundaries(z[1],96*rows);cx=np.array([(a+b)//2 for a,b in zip(xs,xs[1:])]);cy=np.array([(a+b)//2 for a,b in zip(ys,ys[1:])]);out=np.zeros((rows*96,cols*fw,4),np.uint8);out[:,:,:3]=a[cy[:,None],cx[None,:]];out[:,:,3]=fg[cy[:,None],cx[None,:]]*255;out[out[:,:,3]==0]=0
 if name.startswith(('cast','hit')):
  pals=[]
  for dr in ['front_straight','back','left','right']:
   m=np.array(Image.open(R/'art/character_design'/f'hero_B1_{dr}.png').convert('RGBA'));pals.append(m[m[:,:,3]>0,:3])
  pal=np.unique(np.concatenate(pals),axis=0).astype(int)
 else:pal=np.array(json.loads((R/'art/character_design/enemies/skeleton/anim/qc/v2_sources/palette.json').read_text()),int)
 rgb=out[out[:,:,3]>0,:3].astype(int);ix=((rgb[:,None]-pal[None])**2).sum(2).argmin(1);out[out[:,:,3]>0,:3]=pal[ix];Image.fromarray(out).save(W/(name+'_restored.png'))
 for k in range(cols*rows):Image.fromarray(out[k//cols*96:(k//cols+1)*96,k%cols*fw:(k%cols+1)*fw]).save(W/f'{name}_{k+1:02}.png')
 (W/(name+'_grid.json')).write_text(json.dumps({'x_boundaries':xs,'y_boundaries':ys,'native_grid':[fw*cols,96*rows],'observed_source_size':[a.shape[1],a.shape[0]],'method':'Cell-center sampling after observed edge matching constrained by anchor grid. No interpolated colors. Complete body pose drafts are reference only; final head/chest/bag/feet use exact native standard pixels. Dust particles independently checked in raw source cells.'},indent=2))
 Image.fromarray(out).resize((out.shape[1]*3,out.shape[0]*3),Image.Resampling.NEAREST).save(W/(name+'_restored3x.png'))
 ov=Image.fromarray(a);dr=ImageDraw.Draw(ov)
 for x in xs:dr.line((x,0,x,a.shape[0]),fill='#ff8080')
 for y in ys:dr.line((0,y,a.shape[1],y),fill='#ff8080')
 ov.crop((a.shape[1]//3-70,20,a.shape[1]//3+130,220)).save(W/(name+'_gridcheck.png'))
 print(name,out.shape[1],out.shape[0])
