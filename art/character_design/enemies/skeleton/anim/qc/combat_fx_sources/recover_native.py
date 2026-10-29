from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-combat-fx-20261028');V=W/'native';V.mkdir(exist_ok=True)
# Real observed painted-cell pitch, never the requested logical output size.
settings={'fx_bone_chip_a':(2,2,20,21),'fx_bone_chip_b':(2,2,14,14),'fx_bone_chip_c':(2,2,30,31),'fx_bone_dust':(3,2,12.5,12.5),'fx_shroud_threads':(3,2,10,10.3)}
def foreground(a):
 c=a.astype(int);return ~((c[:,:,0]>170)&(c[:,:,2]>150)&(c[:,:,1]<110)&(c[:,:,0]-c[:,:,1]>70)&(c[:,:,2]-c[:,:,1]>65))
def edges(a,fg,axis):
 d=np.abs(np.diff(a.astype(float),axis=axis)).mean(2);m=fg[:,1:]&fg[:,:-1] if axis==1 else fg[1:]&fg[:-1];return (d*m).sum(0 if axis==1 else 1)/np.maximum(m.sum(0 if axis==1 else 1),1)
def fit(z,lo,hi,p):
 z=(z-np.median(z))/(np.std(z)+1e-6);N=len(z)+1;score=np.full(N,-1e12);prev=np.full(N,-1,int);mn=max(2,math.floor(p)-2);mx=math.ceil(p)+2
 for j in range(lo,min(lo+mx,hi)):score[j]=z[max(0,j-1)]*1.4
 for j in range(lo+mx,hi):
  for length in range(mn,mx+1):
   k=j-length
   if k<lo:continue
   s=score[k]+z[j-1]*1.4-.4*(length-p)**2
   if s>score[j]:score[j]=s;prev[j]=k
 end=max(range(max(lo,hi-mx),hi),key=lambda j:score[j]);bs=[]
 while end>=lo:bs.append(int(end));end=prev[end]
 return sorted(bs)
for n,(cols,rows,px,py) in settings.items():
 a=np.array(Image.open(W/(n+'_generated.png')).convert('RGB'));h,w=a.shape[:2];D=V/n;D.mkdir(exist_ok=True);records=[];board=Image.new('RGBA',(cols*64,rows*64),'#403d43');dr=ImageDraw.Draw(board)
 for k in range(cols*rows):
  x0,x1=round(k%cols*w/cols),round((k%cols+1)*w/cols);y0,y1=round(k//cols*h/rows),round((k//cols+1)*h/rows);ar=a[y0:y1,x0:x1];fg=foreground(ar)
  if not fg.any():records.append({'frame':k+1,'blank':True});Image.new('RGBA',(1,1)).save(D/f'{k+1:02}.png');continue
  yy,xx=np.where(fg);zx=edges(ar,fg,1);zy=edges(ar,fg,0);xs=fit(zx,max(0,int(xx.min())-math.ceil(px)),min(ar.shape[1],int(xx.max())+math.ceil(px)+1),px);ys=fit(zy,max(0,int(yy.min())-math.ceil(py)),min(ar.shape[0],int(yy.max())+math.ceil(py)+1),py);out=np.zeros((len(ys)-1,len(xs)-1,4),np.uint8)
  for y in range(len(ys)-1):
   for x in range(len(xs)-1):
    sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
    if fg[sy,sx]:out[y,x,:3]=ar[sy,sx];out[y,x,3]=255
  im=Image.fromarray(out);bb=im.getbbox();im=im.crop(bb);im.save(D/f'{k+1:02}.png');ox=(64-im.width)//2;oy=(64-im.height)//2;board.alpha_composite(im,(k%cols*64+ox,k//cols*64+oy));dr.text((k%cols*64+1,k//cols*64+55),str(k+1),fill='white')
  rec={'frame':k+1,'source_cell':[x0,y0,x1,y1],'observed_painted_pitch':[px,py],'x_boundaries':xs,'y_boundaries':ys,'crop_after_restore':list(bb),'native_size':list(im.size),'method':'Observed painted square cell -> center source pixel -> one native pixel. No wholeimage resize or averaging.'};records.append(rec)
  overlay=Image.fromarray(ar);dd=ImageDraw.Draw(overlay)
  for x in xs:dd.line((x,ys[0],x,ys[-1]),fill='#ff8080')
  for y in ys:dd.line((xs[0],y,xs[-1],y),fill='#ff8080')
  cx=(int(xx.min())+int(xx.max()))//2;cy=(int(yy.min())+int(yy.max()))//2;overlay.crop((max(0,cx-80),max(0,cy-80),cx+80,cy+80)).save(D/f'{k+1:02}_gridcheck.png')
 (D/'grid.json').write_text(json.dumps(records,indent=2));board.resize((board.width*6,board.height*6),Image.Resampling.NEAREST).save(W/(n+'_native6x.png'));print(n,[r.get('native_size','blank') for r in records])
