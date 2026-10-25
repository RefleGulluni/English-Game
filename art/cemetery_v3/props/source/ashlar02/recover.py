from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
W=Path('/tmp/english-game-ashlar02-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game')
old=(R/'art/cemetery_v3/props/source/round2/recover_all.py').read_text();exec(old[old.index('def edges('):old.index('res={}')])
g=json.loads((W/'generation.json').read_text());a=np.array(Image.open(g['source']).convert('RGB'));fg=~((a[:,:,0]>170)&(a[:,:,2]>150)&(a[:,:,1]<110)&(a[:,:,0].astype(int)-a[:,:,1].astype(int)>70)&(a[:,:,2].astype(int)-a[:,:,1].astype(int)>65));yy,xx=np.where(fg)
zx=edges(a,fg,1);zy=edges(a,fg,0);px,acx=period(zx);py,acy=period(zy);xs=fit(zx,max(0,int(xx.min())-px),min(a.shape[1],int(xx.max())+px+1),px);ys=fit(zy,max(0,int(yy.min())-py),min(a.shape[0],int(yy.max())+py+1),py)
out=np.zeros((len(ys)-1,len(xs)-1,4),dtype=np.uint8)
for y in range(len(ys)-1):
 for x in range(len(xs)-1):
  sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
  if fg[sy,sx]:out[y,x,:3]=a[sy,sx];out[y,x,3]=255
Image.fromarray(out).save(W/'restored.png');record={'source':g['source'],'source_size':[a.shape[1],a.shape[0]],'native_size':[out.shape[1],out.shape[0]],'period':[px,py],'autocorrelation_peaks':[acx,acy],'x_boundaries':xs,'y_boundaries':ys,'method':'One detected painted source cell to one native pixel using center-point selection. No image resize, interpolation or mean sampling.'};(W/'grid.json').write_text(json.dumps(record,indent=2));print('grid',out.shape,'period',px,py,acx,acy)
p=Image.fromarray(out).copy();bg=Image.new('RGBA',p.size,'#403D3F');bg.alpha_composite(p);dr=ImageDraw.Draw(bg)
for y in range(0,p.height,5):dr.line([(0,y),(p.width-1,y)],fill='#806060');dr.text((0,y),str(y),fill='white')
bg.resize((bg.width*6,bg.height*6),Image.Resampling.NEAREST).save(W/'native_rows_6x.png')
ov=Image.fromarray(a)
d=ImageDraw.Draw(ov)
for x in xs:d.line([(x,ys[0]),(x,ys[-1])],fill='#FF8080')
for y in ys:d.line([(xs[0],y),(xs[-1],y)],fill='#FF8080')
ov.crop((700,400,1020,640)).save(W/'grid_check_1x.png')
