from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
W=Path('/tmp/english-lexicon-20261029');O=W/'staged';O.mkdir(exist_ok=True);L=np.array([.299,.587,.114])
def load(n):
 a=np.array(Image.open(W/f'{n}_reference.png').convert('RGBA'));fg=a[:,:,:3].max(2)>0;a[~fg]=0;return a
closed=load('closed');op=load('open');rgb=closed[:,:,:3].astype(int);cyan=(rgb[:,:,1]>rgb[:,:,0]+20)&(rgb[:,:,2]>rgb[:,:,0]+20)&(closed[:,:,3]>0)
mask=np.zeros_like(closed);mask[cyan]=[255,255,255,255]
# The original hand-painted symbol pixels supply the exact engraving geometry and the program glow mask.
for c in np.unique(closed[cyan,:3],axis=0):
 l=float(c@L);dst=[34,23,18] if l<140 else ([55,41,26] if l<220 else [91,67,45]);closed[(closed[:,:,:3]==c).all(2)&cyan,:3]=dst
Image.fromarray(closed).save(O/'lexicon_closed_clean.png');Image.fromarray(mask).save(O/'lexicon_sigil_mask.png')
rgb=op[:,:,:3].astype(int);cyan=(rgb[:,:,1]>rgb[:,:,0]+20)&(rgb[:,:,2]>rgb[:,:,0]+20)&(op[:,:,3]>0);inside=np.zeros(op.shape[:2],bool);inside[14:110,27:119]=True;inside[13:109,142:235]=True
lum=rgb@L;remove=cyan|((lum<145)&inside)
# Explicit cleanup masks over the original constellation paths, including pale pencil underdrawing.
paths=[[(42,22),(69,36),(78,25)],[(69,36),(69,56),(94,50),(69,36)],[(42,22),(46,40),(59,58),(52,73),(74,81),(88,67),(100,79),(87,90),(74,81)],[(69,56),(88,67)],[(33,60),(52,73)],[(96,51),(114,55)],[(165,33),(165,50),(148,57),(148,75),(158,88)],[(165,50),(179,55),(179,35)],[(179,55),(163,71),(180,77),(196,71),(179,55)],[(196,71),(206,55),(205,40),(196,31),(208,21),(217,30),(205,40)],[(196,71),(214,83),(185,93)]]
pm=Image.new('L',(256,128));pd=ImageDraw.Draw(pm)
for points in paths:
 pd.line(points,fill=255,width=5)
 for x,y in points:pd.ellipse((x-3,y-3,x+3,y+3),fill=255)
remove|=np.array(pm)>0
valid=(op[:,:,3]>0)&~remove&(lum>=158)&(lum<=225)
# Local native pixel cleanup only: each replacement RGB is selected from real, untouched nearby parchment pixels.
rep=[]
for y,x in np.argwhere(remove):
 choices=[]
 for radius in range(2,13):
  yy,xx=np.where(valid[max(0,y-radius):min(128,y+radius+1),max(0,x-radius):min(256,x+radius+1)])
  if len(yy)>=5:
   yy+=max(0,y-radius);xx+=max(0,x-radius);cs=op[yy,xx,:3];med=np.median(cs,axis=0);d=((cs.astype(float)-med)**2).sum(1)+((yy-y)**2+(xx-x)**2)*.15;idx=int(np.argmin(d));choices=cs[idx];break
 assert len(choices)==3,(y,x);rep.append({'xy':[int(x),int(y)],'before':op[y,x,:3].tolist(),'after':choices.tolist()})
for r in rep:x,y=r['xy'];op[y,x,:3]=r['after']
Image.fromarray(op).save(O/'lexicon_open_clean.png');(W/'clean_edits.json').write_text(json.dumps({'closed_sigil_pixels':int(cyan.sum()),'open_edits':rep,'method':'native cleanup using existing source pixels; no resizing, rotation or mirroring'},indent=2))
pal=set()
for n in ['closed','open']:
 a=load(n);r=a[:,:,:3].astype(int);cy=(r[:,:,1]>r[:,:,0]+20)&(r[:,:,2]>r[:,:,0]+20);pal|=set(map(tuple,a[(a[:,:,3]>0)&~cy,:3]))
(W/'world_palette.json').write_text(json.dumps(sorted(pal),indent=2,default=int));print('world palette',len(pal),'open pixels cleaned',len(rep),'symbol pixels',int((mask[:,:,3]>0).sum()))
