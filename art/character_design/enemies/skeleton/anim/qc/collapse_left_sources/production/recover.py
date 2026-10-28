from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-collapse-left-212-20261028');V=W/'staged/qc/collapse_left_sources';V.mkdir(parents=True,exist_ok=True)
(W/'protected.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file()},indent=2))
source=Path('/Users/mac/.codex/generated_images/01a16768-6cb4-7a02-aee2-ae3ac8b12896/exec-3e54a21c-a0d6-4d3e-bb09-ff9b473042cb.png');shutil.copy2(source,V/'approved_wip2_source.png');a=np.array(Image.open(source).convert('RGB'));h,w=a.shape[:2]
code=(R/'art/cemetery_v3/props/source/round2/recover_all.py').read_text();defs=code[code.index('def edges('):code.index('res={}')].replace('range(6,25)','range(2,16)').replace('mn=max(4,p-2);mx=p+2','mn=max(2,p-1);mx=p+1').replace('.30*(length-p)**2','2.0*(length-p)**2');exec(defs)
pal=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),np.uint8);records=[];board=Image.new('RGBA',(3*128,3*128),'#403D43');dr=ImageDraw.Draw(board)
# Painted rows are not mathematically equal height. These boundaries lie in the empty magenta gutters.
ycuts=[0,490,960,h];xcuts=[0,round(w/3),round(2*w/3),w]
for k in range(9):
 x0,x1=xcuts[k%3:k%3+2];y0,y1=ycuts[k//3:k//3+2];ar=a[y0:y1,x0:x1];c=ar.astype(int);fg=~((c[:,:,0]>170)&(c[:,:,2]>150)&(c[:,:,1]<110)&(c[:,:,0]-c[:,:,1]>70)&(c[:,:,2]-c[:,:,1]>65));yy,xx=np.where(fg);zx=edges(ar,fg,1);zy=edges(ar,fg,0);px,acx=period(zx);py,acy=period(zy);px=py=4;print(k+1,'period',px,py,'peaks',acx,acy)
 xs=fit(zx,max(0,int(xx.min())-px),min(ar.shape[1],int(xx.max())+px+1),px);ys=fit(zy,max(0,int(yy.min())-py),min(ar.shape[0],int(yy.max())+py+1),py);out=np.zeros((len(ys)-1,len(xs)-1,4),np.uint8)
 for y in range(len(ys)-1):
  for x in range(len(xs)-1):
   sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
   if fg[sy,sx]:out[y,x,:3]=ar[sy,sx];out[y,x,3]=255
 Image.fromarray(out).save(V/f'grid_restored_{k+1:02}.png');rgb=out[out[:,:,3]>0,:3].astype(int);ix=((rgb[:,None]-pal.astype(int)[None])**2).sum(2).argmin(1);out[out[:,:,3]>0,:3]=pal[ix];Image.fromarray(out).save(V/f'palette_native_{k+1:02}.png');im=Image.fromarray(out);bb=im.getbbox();im=im.crop(bb);print('native',im.size)
 board.alpha_composite(im,(k%3*128+max(0,(128-im.width)//2),k//3*128+111-im.height));dr.text((k%3*128+4,k//3*128+113),str(k+1),fill='white');records.append({'frame':k+1,'source_box':[x0,y0,x1,y1],'period':[px,py],'x_boundaries':xs,'y_boundaries':ys,'native_size':list(out.shape[1::-1]),'mapping':'One painted grid cell -> center sample -> one native pixel. No image resize.'})
(V/'restoration_grid.json').write_text(json.dumps(records,indent=2));board.resize((1920,1920),Image.Resampling.NEAREST).save(W/'restored_review_5x.png')
