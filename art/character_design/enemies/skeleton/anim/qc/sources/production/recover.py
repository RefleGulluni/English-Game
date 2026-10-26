from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-skeleton-animation-20261026')
s=(R/'art/cemetery_v3/props/source/round2/recover_all.py').read_text();exec(s[s.index('def edges('):s.index('res={}')].replace('range(6,25)','range(2,20)').replace('mn=max(4,p-2);mx=p+2','mn=max(2,p-1);mx=p+1').replace('.30*(length-p)**2','3.0*(length-p)**2'))
gens={'walk':('/Users/mac/.codex/generated_images/01a16768-6cb4-7a02-aee2-ae3ac8b12896/exec-04d54907-32ff-4b49-855e-e9509528b060.png',4,2),'mid':('/Users/mac/.codex/generated_images/01a16768-6cb4-7a02-aee2-ae3ac8b12896/exec-27e880e3-60a0-470d-adac-2ca342da494a.png',2,2),'collapse':('/Users/mac/.codex/generated_images/01a16768-6cb4-7a02-aee2-ae3ac8b12896/exec-3979d2a7-4f23-47c9-b03e-bae83e214b57.png',3,3)}
for mode,(path,rows,cols) in gens.items():
 a=np.array(Image.open(path).convert('RGB'));HH,WW=a.shape[:2];outdir=W/mode;outdir.mkdir(exist_ok=True);records=[];board=Image.new('RGBA',(cols*144,rows*144),'#403D3F');dr=ImageDraw.Draw(board)
 for i in range(rows*cols):
  ox=round(i%cols*WW/cols);oy=([0,500,965][i//cols] if mode=='collapse' else round(i//cols*HH/rows));ey=([500,965,HH][i//cols] if mode=='collapse' else round((i//cols+1)*HH/rows));a0=a[oy:ey,ox:round((i%cols+1)*WW/cols)];c=a0.astype(int);fg=~((c[:,:,0]>170)&(c[:,:,2]>150)&(c[:,:,1]<110)&(c[:,:,0]-c[:,:,1]>70)&(c[:,:,2]-c[:,:,1]>65));yy,xx=np.where(fg);zx=edges(a0,fg,1);zy=edges(a0,fg,0);px,ax=period(zx);py,ay=period(zy);px=py=(3 if mode=='walk' else (7 if mode=='mid' else 4));xs=fit(zx,max(0,int(xx.min())-px),min(a0.shape[1],int(xx.max())+px+1),px);ys=fit(zy,max(0,int(yy.min())-py),min(a0.shape[0],int(yy.max())+py+1),py)
  ar=np.zeros((len(ys)-1,len(xs)-1,4),dtype=np.uint8)
  for y in range(len(ys)-1):
   for x in range(len(xs)-1):
    sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
    if fg[sy,sx]:ar[y,x,:3]=a0[sy,sx];ar[y,x,3]=255
  Image.fromarray(ar).save(outdir/f'frame_{i+1:02}.png');record={'frame':i+1,'source':path,'crop_offset':[ox,oy],'x_boundaries':xs,'y_boundaries':ys,'period':[px,py],'native_size':[ar.shape[1],ar.shape[0]],'peaks':[ax,ay]};records.append(record);print(mode,i+1,'native',ar.shape,'period',px,py)
  board.alpha_composite(Image.fromarray(ar),(i%cols*144+30,i//cols*144+125-ar.shape[0]));dr.text((i%cols*144+5,i//cols*144+130),str(i+1),fill='white')
 (outdir/'grid.json').write_text(json.dumps(records,indent=2));board.resize((board.width*4,board.height*4),Image.Resampling.NEAREST).save(W/(mode+'_recovered_4x.png'))
