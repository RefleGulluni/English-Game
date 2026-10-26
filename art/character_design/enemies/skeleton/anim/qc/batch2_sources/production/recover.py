from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-skeleton-batch2-20261026');s=(R/'art/cemetery_v3/props/source/round2/recover_all.py').read_text();exec(s[s.index('def edges('):s.index('res={}')].replace('range(6,25)','range(2,20)').replace('mn=max(4,p-2);mx=p+2','mn=max(2,p-1);mx=p+1').replace('.30*(length-p)**2','3.0*(length-p)**2'))
G={'left':('exec-1a47c403-5689-4d76-b56a-e4361398687f.png',4,2,3),'front':('exec-7334b156-d886-4676-a37a-142becea43d3.png',2,4,5),'back':('exec-ab89fa44-938d-4be8-981e-aecd164443b2.png',2,4,5),'reassemble':('exec-d7f91c1b-5fbc-4281-a326-ac379671c96c.png',4,3,4)}
for mode,(name,rows,cols,p) in G.items():
 path=Path('/Users/mac/.codex/generated_images/01a16768-6cb4-7a02-aee2-ae3ac8b12896')/name;a=np.array(Image.open(path).convert('RGB'));H,WW=a.shape[:2];D=W/mode;D.mkdir(exist_ok=True);records=[];board=Image.new('RGBA',(cols*144,rows*144),'#403D3F');dr=ImageDraw.Draw(board)
 for i in range(rows*cols):
  ox=round(i%cols*WW/cols);oy=([0,278,563,876][i//cols] if mode=='reassemble' else round(i//cols*H/rows));ey=([278,563,876,H][i//cols] if mode=='reassemble' else round((i//cols+1)*H/rows));ar=a[oy:ey,ox:round((i%cols+1)*WW/cols)];c=ar.astype(int);fg=~((c[:,:,0]>170)&(c[:,:,2]>150)&(c[:,:,1]<110)&(c[:,:,0]-c[:,:,1]>70)&(c[:,:,2]-c[:,:,1]>65));yy,xx=np.where(fg);zx=edges(ar,fg,1);zy=edges(ar,fg,0);xs=fit(zx,max(0,int(xx.min())-p),min(ar.shape[1],int(xx.max())+p+1),p);ys=fit(zy,max(0,int(yy.min())-p),min(ar.shape[0],int(yy.max())+p+1),p);out=np.zeros((len(ys)-1,len(xs)-1,4),dtype=np.uint8)
  for y in range(out.shape[0]):
   for x in range(out.shape[1]):
    sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
    if fg[sy,sx]:out[y,x,:3]=ar[sy,sx];out[y,x,3]=255
  Image.fromarray(out).save(D/f'frame_{i+1:02}.png');records.append({'frame':i+1,'source':str(path),'source_crop_offset':[ox,oy],'x_boundaries':xs,'y_boundaries':ys,'nominal_cell_period':p,'native_size':[out.shape[1],out.shape[0]]});print(mode,i+1,out.shape[:2]);board.alpha_composite(Image.fromarray(out),(i%cols*144+30,i//cols*144+125-out.shape[0]));dr.text((i%cols*144+5,i//cols*144+130),str(i+1),fill='white')
 (D/'grid.json').write_text(json.dumps(records,indent=2));board.resize((board.width*3,board.height*3),Image.Resampling.NEAREST).save(W/(mode+'_recovered_3x.png'))
