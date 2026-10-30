from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/Users/mac/.codex/work/veil-ghost-20261030');S=W/'staged/qc/veil_ghost_sources';S.mkdir(parents=True,exist_ok=True)
code=(R/'art/cemetery_v3/props/source/round2/recover_all.py').read_text();defs=code[code.index('def edges('):code.index('res={}')].replace('range(6,25)','range(3,45)').replace('mn=max(4,p-2);mx=p+2','mn=max(2,p-1);mx=p+1').replace('.30*(length-p)**2','2.0*(length-p)**2');exec(defs)
records=[]
for p in sorted(W.glob('generation_*.json')):records+=json.loads(p.read_text())
for r in records:
 n=r['name'];d=S/n
 if (d/'grid.json').exists():continue
 d.mkdir(exist_ok=True);shutil.copy2(r['path'],d/'01_generated_original.png');(d/'generation.json').write_text(json.dumps(r,indent=2));a=np.array(Image.open(r['path']).convert('RGB'));c=a.astype(int);fg=~((c[:,:,0]>170)&(c[:,:,2]>150)&(c[:,:,1]<110)&(c[:,:,0]-c[:,:,1]>70)&(c[:,:,2]-c[:,:,1]>65));yy,xx=np.where(fg)
 zx=edges(a,fg,1);zy=edges(a,fg,0);px,acx=period(zx);py,acy=period(zy)
 # Compare inferred pitch with actual source pixels in grid-check crop.
 xs=fit(zx,max(0,int(xx.min())-px),min(a.shape[1],int(xx.max())+px+1),px);ys=fit(zy,max(0,int(yy.min())-py),min(a.shape[0],int(yy.max())+py+1),py)
 out=np.zeros((len(ys)-1,len(xs)-1,4),np.uint8)
 for y in range(len(ys)-1):
  for x in range(len(xs)-1):
   sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
   if fg[sy,sx]:out[y,x]=[*a[sy,sx],255]
 im=Image.fromarray(out);bb=im.getbbox();im=im.crop(bb);im.save(d/'02_restored_cells.png');m={'source_size':[a.shape[1],a.shape[0]],'period':[px,py],'peaks':[acx,acy],'x_boundaries':xs,'y_boundaries':ys,'crop':bb,'native_size':list(im.size),'method':'actual painted cell boundary -> source center -> one native pixel; no full-image scaling or averaging'};(d/'grid.json').write_text(json.dumps(m,indent=2))
 ov=Image.fromarray(a);dr=ImageDraw.Draw(ov)
 for x in xs:dr.line((x,ys[0],x,ys[-1]),fill='#FF8080')
 for y in ys:dr.line((xs[0],y,xs[-1],y),fill='#FF8080')
 cx=int(np.median(xx));cy=int(np.median(yy));ov.crop((cx-120,cy-120,cx+120,cy+120)).save(d/'grid_check_1x.png')
 print(n,'pitch',px,py,'native',im.size,'peaks',acx,acy)
