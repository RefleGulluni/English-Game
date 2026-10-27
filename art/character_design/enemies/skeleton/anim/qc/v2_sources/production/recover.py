from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-skeleton-v2-20261027');s=(R/'art/cemetery_v3/props/source/round2/recover_all.py').read_text();exec(s[s.index('def edges('):s.index('res={}')].replace('range(6,25)','range(2,20)').replace('mn=max(4,p-2);mx=p+2','mn=max(2,p-1);mx=p+1').replace('.30*(length-p)**2','3.0*(length-p)**2'))
G={'ground':('exec-4c8c6e74-edc8-4415-ae60-08ee1525b198.png',4,2,7),'rise':('exec-725ae79a-79d0-41e0-affa-e061789940e3.png',3,2,4),'settle':('exec-5ebe924b-1e62-4031-907e-cdb0049d8a60.png',3,2,3)}
for mode,(name,rows,cols,p) in G.items():
 path=Path('/Users/mac/.codex/generated_images/01a16768-6cb4-7a02-aee2-ae3ac8b12896')/name;raw=np.array(Image.open(path).convert('RGB'));H,WW=raw.shape[:2];D=W/mode;D.mkdir(exist_ok=True);records=[];board=Image.new('RGBA',(cols*160,rows*150),'#403D3F');dr=ImageDraw.Draw(board)
 for i in range(rows*cols):
  ox=round(i%cols*WW/cols);oy=([0,322,652][i//cols] if mode=='rise' else round(i//cols*H/rows));ey=([322,652,H][i//cols] if mode=='rise' else round((i//cols+1)*H/rows));ar=raw[oy:ey,ox:round((i%cols+1)*WW/cols)];c=ar.astype(int);fg=~((c[:,:,0]>170)&(c[:,:,2]>150)&(c[:,:,1]<110)&(c[:,:,0]-c[:,:,1]>70)&(c[:,:,2]-c[:,:,1]>65));yy,xx=np.where(fg);zx=edges(ar,fg,1);zy=edges(ar,fg,0);xs=fit(zx,max(0,int(xx.min())-p),min(ar.shape[1],int(xx.max())+p+1),p);ys=fit(zy,max(0,int(yy.min())-p),min(ar.shape[0],int(yy.max())+p+1),p);out=np.zeros((len(ys)-1,len(xs)-1,4),np.uint8)
  for y in range(out.shape[0]):
   for x in range(out.shape[1]):
    sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
    if fg[sy,sx]:out[y,x,:3]=ar[sy,sx];out[y,x,3]=255
  Image.fromarray(out).save(D/f'frame_{i+1:02}.png');records.append({'frame':i+1,'source':str(path),'crop_offset':[ox,oy],'x_boundaries':xs,'y_boundaries':ys,'period':p,'native_size':[out.shape[1],out.shape[0]]});print(mode,i+1,out.shape[:2]);board.alpha_composite(Image.fromarray(out),(i%cols*160+5,i//cols*150+130-out.shape[0]));dr.text((i%cols*160+5,i//cols*150+134),str(i+1),fill='white')
 (D/'grid.json').write_text(json.dumps(records,indent=2));board.resize((board.width*3,board.height*3),Image.Resampling.NEAREST).save(W/(mode+'_native_3x.png'))
