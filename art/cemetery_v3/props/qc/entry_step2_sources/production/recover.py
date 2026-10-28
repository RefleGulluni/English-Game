from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-entry-step2-20261028');V=W/'staged/qc/entry_step2_sources';V.mkdir(parents=True,exist_ok=True)
code=(R/'art/cemetery_v3/props/source/round2/recover_all.py').read_text();defs=code[code.index('def edges('):code.index('res={}')].replace('range(6,25)','range(2,25)').replace('mn=max(4,p-2);mx=p+2','mn=max(2,p-1);mx=p+1').replace('.30*(length-p)**2','2.0*(length-p)**2');exec(defs)
allgen=[]
for p in sorted(W.glob('generation_batch_*.json')):allgen+=json.loads(p.read_text())
for record in allgen:
 n=record['name'];p=Path(record['path']);dest=V/n;dest.mkdir(exist_ok=True);shutil.copy2(p,dest/'01_generated_original.png');(dest/'generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));a=np.array(Image.open(p).convert('RGB'));c=a.astype(int);fg=~((c[:,:,0]>170)&(c[:,:,2]>150)&(c[:,:,1]<110)&(c[:,:,0]-c[:,:,1]>70)&(c[:,:,2]-c[:,:,1]>65));yy,xx=np.where(fg);zx=edges(a,fg,1);zy=edges(a,fg,0);px,acx=period(zx);py,acy=period(zy);print(n,'period',px,py,'peaks',acx,acy)
 xs=fit(zx,max(0,int(xx.min())-px),min(a.shape[1],int(xx.max())+px+1),px);ys=fit(zy,max(0,int(yy.min())-py),min(a.shape[0],int(yy.max())+py+1),py);out=np.zeros((len(ys)-1,len(xs)-1,4),np.uint8)
 for y in range(len(ys)-1):
  for x in range(len(xs)-1):
   sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
   if fg[sy,sx]:out[y,x,:3]=a[sy,sx];out[y,x,3]=255
 im=Image.fromarray(out);bb=im.getbbox();im=im.crop(bb);im.save(dest/'02_restored_cells.png');data={'source':str(p),'period':[px,py],'autocorrelation_peaks':[acx,acy],'x_boundaries':xs,'y_boundaries':ys,'crop_after_restoration':list(bb),'native_size':list(im.size),'method':'One painted cell -> center source point -> one native pixel. No global resize, no averaging.'};(dest/'grid.json').write_text(json.dumps(data,indent=2))
 ov=Image.fromarray(a);d=ImageDraw.Draw(ov)
 for x in xs:d.line((x,ys[0],x,ys[-1]),fill='#FF8080')
 for y in ys:d.line((xs[0],y,xs[-1],y),fill='#FF8080')
 cx=int((xx.min()+xx.max())/2);cy=int((yy.min()+yy.max())/2);ov.crop((cx-120,cy-120,cx+120,cy+120)).save(dest/'grid_check_1x.png');print(' native',im.size)
# Only QC, each restored sprite is native pasted without fit scaling.
b=Image.new('RGBA',(3*320,3*320),'#403D43');d=ImageDraw.Draw(b)
for k,r in enumerate(allgen):
 im=Image.open(V/r['name']/'02_restored_cells.png');x=k%3*320;y=k//3*320;b.alpha_composite(im,(x+(320-im.width)//2,y+286-im.height));d.text((x+4,y+297),r['name'],fill='white')
b.resize((1920,1920),Image.Resampling.NEAREST).save(W/'restored_all_2x.png')
