from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,collections,math
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-combat-fx-20261028');N=W/'native';O=W/'staged';O.mkdir(exist_ok=True);V=O/'qc/combat_fx_sources';V.mkdir(parents=True,exist_ok=True);pal=np.array(json.loads((R/'art/character_design/enemies/skeleton/anim/qc/v2_sources/palette.json').read_text()),int);L=np.array([.299,.587,.114]);ALL={};records={}
def load(p):return np.array(Image.open(p).convert('RGBA'))
def comps(mask):
 todo=set(zip(*np.where(mask)));cs=[]
 while todo:
  q=[todo.pop()];c=q.copy()
  while q:
   y,x=q.pop()
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     pt=(y+dy,x+dx)
     if pt in todo:todo.remove(pt);q.append(pt);c.append(pt)
  cs.append(c)
 return sorted(cs,key=len,reverse=True)
def clean(a):
 a=a.copy();rgb=a[:,:,:3].astype(int);bad=(rgb[:,:,0]-rgb[:,:,1]>22)&(rgb[:,:,2]-rgb[:,:,1]>22)&(a[:,:,3]>0);orig=a.copy()
 # Restore only contaminated samples lying BETWEEN two intact material pixels; otherwise drop background spill.
 for y,x in zip(*np.where(bad)):
  bridged=False
  for dy,dx in [(1,0),(0,1),(1,1),(1,-1)]:
   p=(y-dy,x-dx);q=(y+dy,x+dx)
   if 0<=p[0]<a.shape[0] and 0<=p[1]<a.shape[1] and 0<=q[0]<a.shape[0] and 0<=q[1]<a.shape[1] and orig[p][3] and orig[q][3] and not bad[p] and not bad[q]:a[y,x]=orig[p];bridged=True;break
  if not bridged:a[y,x]=0
 a[a[:,:,3]==0]=0;return a

def mapcolors(a,allowed):
 a=a.copy();fg=a[:,:,3]>0;rgb=a[fg,:3].astype(int);ix=((rgb[:,None]-allowed[None])**2).sum(2).argmin(1);a[fg,:3]=allowed[ix];return a

def put(a,b,x,y):
 yy,xx=np.where(b[:,:,3]>0);assert ((xx+x>=0)&(xx+x<a.shape[1])&(yy+y>=0)&(yy+y<a.shape[0])).all(),('clip',x,y,b.shape,a.shape);a[yy+y,xx+x]=b[yy,xx]

def export(n,fs):
 ALL[n]=fs;D=O/'frames'/n;D.mkdir(parents=True,exist_ok=True);fw=fs[0].shape[1];fh=fs[0].shape[0];sheet=Image.new('RGBA',(len(fs)*fw,fh));board=Image.new('RGBA',(len(fs)*(fw+4),fh+12),'#403d43');dr=ImageDraw.Draw(board)
 for k,a in enumerate(fs):
  Image.fromarray(a).save(D/f'{k+1:02}.png');sheet.paste(Image.fromarray(a),(fw*k,0));board.alpha_composite(Image.fromarray(a),(k*(fw+4),1));dr.text((k*(fw+4)+1,fh+3),str(k+1),fill='white')
 sheet.save(O/(n+'.png'));board.resize((board.width*8,board.height*8),Image.Resampling.NEAREST).save(W/(n+'_contact8x.png'))
# Select actual native broken pieces, never resize an entire generated bone.
selections={
 'fx_bone_chip_a':[(0,1,8,6),(1,1,8,8),(1,0,6,8),(7,5,15,11)],
 'fx_bone_chip_b':[(0,5,8,13),(0,0,8,8),(0,4,8,12),(6,17,14,25)],
 'fx_bone_chip_c':[(3,0,9,6),(0,0,6,6),(1,2,7,8),(0,0,7,6)]}
for n,boxes in selections.items():
 fs=[];rr=[]
 for k,box in enumerate(boxes):
  source=clean(load(N/n/f'{k+1:02}.png'));x0,y0,x1,y1=box;b=source[y0:y1,x0:x1].copy();cc=comps(b[:,:,3]>0);keep=np.zeros(b.shape[:2],bool)
  for y,x in cc[0]:keep[y,x]=True
  b[~keep]=0
  if n=='fx_bone_chip_b':
   # Retain the actual outside curved rib wall, trim excess interior thickness; no new curve or rotated image.
   wall=np.zeros(b.shape[:2],bool)
   if k in [0,2]:
    for x in range(b.shape[1]):
     ys1=np.where(b[:,x,3]>0)[0];wall[ys1[-3:],x]=True
   else:
    for y in range(b.shape[0]):
     xs1=np.where(b[y,:,3]>0)[0];wall[y,xs1[:3] if k==1 else xs1[-3:]]=True
   b[~wall]=0
  b=mapcolors(b,pal)
  if n=='fx_bone_chip_b':
   # The selected outer rib wall is largely its shadow edge: use the existing lit-bone ramp for this smaller exposed break.
   ramp=pal[(pal@L>=115)&(pal@L<=240)];fg=b[:,:,3]>0;target=100+.65*(b[fg,:3]@L);ix=((ramp@L)[None]-target[:,None])**2;b[fg,:3]=ramp[ix.argmin(1)]
  ys,xs=np.where(b[:,:,3]>0);dx=8-round(float(xs.mean()));dy=8-round(float(ys.mean()));a=np.zeros((16,16,4),np.uint8);put(a,b,dx,dy);assert max(xs.max()-xs.min()+1,ys.max()-ys.min()+1)<=8;fs.append(a);rr.append({'frame':k+1,'source_native':str((N/n/f'{k+1:02}.png').relative_to(W)),'selected_broken_piece_xyxy':list(box),'largest_component_only':True,'integer_placement':[dx,dy],'meaning':'one knobby bone terminal and short broken shaft' if n.endswith('a') else 'a curved corner broken off the rib, preserving inner concavity' if n.endswith('b') else 'angular porous fracture corner; no whole-bone scaling'})
 export(n,fs);records[n]=rr
# Ash: the actual generated gritty clumps, remapped to the skeleton's darker palette.
n='fx_bone_dust';dustpal=pal[(pal@L>=35)&(pal@L<=120)];fs=[];rr=[];grid=json.loads((N/n/'grid.json').read_text())
for k in range(6):
 a=np.zeros((32,48,4),np.uint8)
 if k==5:fs.append(a);rr.append({'frame':6,'transparent':True});continue
 b=mapcolors(clean(load(N/n/f'{k+1:02}.png')),dustpal);rec=grid[k];xs=rec['x_boundaries'];ys=rec['y_boundaries'];bb=rec['crop_after_restore'];sw=rec['source_cell'][2]-rec['source_cell'][0];sh=rec['source_cell'][3]-rec['source_cell'][1];px=float(np.mean(np.diff(xs)));py=float(np.mean(np.diff(ys)));pivotx=round((sw/2-(xs[0]+xs[1])/2)/px)-bb[0];pivoty=round((sh-1-(ys[0]+ys[1])/2)/py)-bb[1];ox,oy=24-pivotx,31-pivoty
 if k==0:
  fy,fx=np.where(b[:,:,3]>0);bottom=int(fy.max());bottomxs=fx[fy==bottom];ox=24-int(np.median(bottomxs));oy=31-bottom
 fy,fx=np.where(b[:,:,3]>0);cx=(fx.min()+fx.max())/2+ox;cy=(fy.min()+fy.max())/2+oy;winx=max(0,min(8,round(cx-19.5)));winy=max(0,min(8,round(cy-11.5)));pieces=[]
 for c in comps(b[:,:,3]>0):
  yy=np.array([p[0] for p in c]);xx=np.array([p[1] for p in c]);x0,x1=int(xx.min()),int(xx.max())+1;y0,y1=int(yy.min()),int(yy.max())+1;dx=max(winx-(x0+ox),min(0,winx+40-(x1+ox)));dy=max(winy-(y0+oy),min(0,winy+24-(y1+oy)));piece=np.zeros((y1-y0,x1-x0,4),np.uint8)
  for y,x in c:piece[y-y0,x-x0]=b[y,x]
  put(a,piece,x0+ox+dx,y0+oy+dy);pieces.append({'source_component_bbox':[x0,y0,x1,y1],'integer_translation':[ox+dx,oy+dy],'size':len(c),'native_outlier_nudge':[dx,dy]})
 if k==0:assert a[31,24,3]==255
 bounds=Image.fromarray(a).getbbox();assert bounds[2]-bounds[0]<=40 and bounds[3]-bounds[1]<=24
 fs.append(a);rr.append({'frame':k+1,'source_native':f'native/{n}/{k+1:02}.png','source_to_emission_offset':[ox,oy],'actual_bbox':bounds,'components':pieces,'palette_luma_cap':120})
export(n,fs);records[n]=rr
# Deterministic one-pixel cleanup of the already drawn fibers, not newly generated curves.
def thin(mask):
 im=np.pad(mask.astype(np.uint8),1)
 changed=True
 while changed:
  changed=False
  for phase in [0,1]:
   delete=[]
   for y,x in zip(*np.where(im)):
    if y==0 or x==0 or y==im.shape[0]-1 or x==im.shape[1]-1:continue
    ps=[im[y-1,x],im[y-1,x+1],im[y,x+1],im[y+1,x+1],im[y+1,x],im[y+1,x-1],im[y,x-1],im[y-1,x-1]];B=sum(int(v) for v in ps);A=sum(ps[j]==0 and ps[(j+1)%8]==1 for j in range(8))
    if not (2<=B<=6 and A==1):continue
    cond=(ps[0]*ps[2]*ps[4]==0 and ps[2]*ps[4]*ps[6]==0) if phase==0 else (ps[0]*ps[2]*ps[6]==0 and ps[0]*ps[4]*ps[6]==0)
    if cond:delete.append((y,x))
   if delete:
    for p in delete:im[p]=0
    changed=True
 return im[1:-1,1:-1]>0

def longest_path(points):
 points=set(points)
 def bfs(start):
  dist={start:0};prev={};q=collections.deque([start])
  while q:
   y,x=q.popleft()
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     pt=(y+dy,x+dx)
     if pt in points and pt not in dist:dist[pt]=dist[(y,x)]+1;prev[pt]=(y,x);q.append(pt)
  end=max(dist,key=dist.get);return end,dist,prev
 start=next(iter(points));end,_,_=bfs(start);end2,_,prev=bfs(end);path=[end2]
 while path[-1]!=end:path.append(prev[path[-1]])
 return path[::-1]
n='fx_shroud_threads';clothpal=pal[(pal@L>=78)&(pal@L<=165)];fs=[];rr=[]
for k in range(6):
 a=np.zeros((32,32,4),np.uint8)
 if k==5:fs.append(a);rr.append({'frame':6,'transparent':True});continue
 source=mapcolors(clean(load(N/n/f'{k+1:02}.png')),clothpal);mask=thin(source[:,:,3]>0);cc=[c for c in comps(mask) if len(c)>=4];cc.sort(key=lambda c:np.mean([x for y,x in c]));wanted=[4,4,4,3,2][k];assert len(cc)>=wanted,(k,len(cc));cc=cc[:wanted];centers=([5,12,20,27] if wanted==4 else [7,16,25] if wanted==3 else [11,23]);tops=[7,10,14,20,25];row=[]
 for j,c in enumerate(cc):
  path=longest_path(c);length=min(len(path),6 if k==4 else 10);beg=max(0,(len(path)-length)//2);path=path[beg:beg+length]
  while max(x for y,x in path)-min(x for y,x in path)+1>6 and len(path)>4:path=path[1:]
  ys0=[y for y,x in path];xs0=[x for y,x in path];x0,x1=min(xs0),max(xs0)+1;y0,y1=min(ys0),max(ys0)+1;b=np.zeros((y1-y0,x1-x0,4),np.uint8)
  for y,x in path:b[y-y0,x-x0]=source[y,x]
  px=centers[j]-b.shape[1]//2;py=min(tops[k]+(j%2),32-b.shape[0]);put(a,b,px,py);row.append({'fiber':j+1,'source_native_points_yx':[[int(y),int(x)] for y,x in path],'source_bbox':[x0,y0,x1,y1],'integer_placement':[px,py],'pixel_length':len(path)})
 # Separate unbranched paths and no 2x2 blocks establish one-pixel stroke width.
 counts=[len(c) for c in comps(a[:,:,3]>0)];assert len(counts)==wanted and all(4<=l<=10 for l in counts),(k,counts)
 z=a[:,:,3]>0;assert not (z[:-1,:-1]&z[1:,:-1]&z[:-1,1:]&z[1:,1:]).any()
 fs.append(a);rr.append({'frame':k+1,'fibers':row,'component_pixel_lengths':counts,'no_2x2_filled_blocks':True})
export(n,fs);records[n]=rr
(V/'native_selection_records.json').write_text(json.dumps(records,indent=2,default=lambda v:int(v)));(W/'selection_records.json').write_text(json.dumps(records,indent=2,default=lambda v:int(v)));print({n:[Image.fromarray(a).getbbox() for a in fs] for n,fs in ALL.items()})
