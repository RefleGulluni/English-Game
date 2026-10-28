from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-collapse-rb-213-20261028');V=W/'staged/qc/collapse_rb_sources';palette=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),np.uint8)
code=(R/'art/cemetery_v3/props/source/round2/recover_all.py').read_text();defs=code[code.index('def edges('):code.index('res={}')].replace('range(6,25)','range(2,16)').replace('mn=max(4,p-2);mx=p+2','mn=max(2,p-1);mx=p+1').replace('.30*(length-p)**2','2.0*(length-p)**2');exec(defs)
rawnames={'right':'exec-e2521860-20c8-46f5-80dd-dd6e94287a2c.png','back':'exec-0f044177-8730-4c54-adb4-8daf276e5adc.png'}
def foreground(a):
 c=a.astype(int);return ~((c[:,:,0]>170)&(c[:,:,2]>150)&(c[:,:,1]<110)&(c[:,:,0]-c[:,:,1]>70)&(c[:,:,2]-c[:,:,1]>65))
for d,fn in rawnames.items():
 source=Path('/Users/mac/.codex/generated_images/01a16768-6cb4-7a02-aee2-ae3ac8b12896')/fn;dest=V/d;dest.mkdir(exist_ok=True);shutil.copy2(source,dest/'generated_early_fall.png');a=np.array(Image.open(source).convert('RGB'));h,w=a.shape[:2];cols,rows=(2,3) if d=='right' else (3,2);f=foreground(a)
 # Choose empty gutter rows close to expected boundaries instead of slicing through a falling limb.
 ycuts=[0]
 for i in range(1,rows):
  target=round(i*h/rows);lo=max(ycuts[-1]+1,target-90);hi=min(h-1,target+90);counts=f.sum(1);candidates=[y for y in range(lo,hi) if counts[y]==0];cut=min(candidates,key=lambda y:abs(y-target)) if candidates else target;ycuts.append(cut)
 ycuts.append(h);xcuts=[round(i*w/cols) for i in range(cols+1)];board=Image.new('RGBA',(cols*128,rows*128),'#403D43');dr=ImageDraw.Draw(board);records=[]
 for k in range(6):
  x0,x1=xcuts[k%cols:k%cols+2];y0,y1=ycuts[k//cols:k//cols+2];ar=a[y0:y1,x0:x1];fg=foreground(ar);yy,xx=np.where(fg);zx=edges(ar,fg,1);zy=edges(ar,fg,0);px,acx=period(zx);py,acy=period(zy);print(d,k+1,'detected',px,py,'peaks',acx,acy)
  # Inspectable approx-4px painted cells, same native restoration used by accepted left.
  px=py=4;xs=fit(zx,max(0,int(xx.min())-px),min(ar.shape[1],int(xx.max())+px+1),px);ys=fit(zy,max(0,int(yy.min())-py),min(ar.shape[0],int(yy.max())+py+1),py);out=np.zeros((len(ys)-1,len(xs)-1,4),np.uint8)
  for y in range(len(ys)-1):
   for x in range(len(xs)-1):
    sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
    if fg[sy,sx]:out[y,x,:3]=ar[sy,sx];out[y,x,3]=255
  Image.fromarray(out).save(dest/f'grid_restored_{k+1:02}.png');rgb=out[out[:,:,3]>0,:3].astype(int);ix=((rgb[:,None]-palette.astype(int)[None])**2).sum(2).argmin(1);out[out[:,:,3]>0,:3]=palette[ix];im=Image.fromarray(out);bb=im.getbbox();im=im.crop(bb);im.save(dest/f'palette_crop_{k+1:02}.png');print(' native',im.size)
  board.alpha_composite(im,(k%cols*128+(128-im.width)//2,k//cols*128+111-im.height));dr.text((k%cols*128+4,k//cols*128+113),str(k+1),fill='white');records.append({'frame':k+1,'source':str(source),'source_cell_box':[x0,y0,x1,y1],'painted_period_estimate':[4,4],'autocorrelation_peaks':[acx,acy],'x_boundaries':xs,'y_boundaries':ys,'native_crop_box':list(bb),'native_size':list(im.size),'mapping':'Detected painted-block boundary -> center source pixel -> one native pixel. No full-image resize.'})
 (dest/'restoration_grid.json').write_text(json.dumps(records,indent=2));board.resize((board.width*4,board.height*4),Image.Resampling.NEAREST).save(W/f'{d}_recovered_4x.png')
