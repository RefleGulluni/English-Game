from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,copy
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-collapse-left-212-20261028');O=W/'staged';Q=O/'qc';V=Q/'collapse_left_sources';F=O/'frames/skeleton_B_collapse_left';F.mkdir(parents=True,exist_ok=True);L=V/'layers';L.mkdir(exist_ok=True)
load=lambda p:np.array(Image.open(p).convert('RGBA'))
master=load(S/'skeleton_B_left.png');front=load(A/'skeleton_B_collapse_front.png');end=front[:,-96:].copy();pal=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),np.uint8)
def crop(a):
 ys,xs=np.where(a[:,:,3]>0);return a[ys.min():ys.max()+1,xs.min():xs.max()+1].copy()
def maskpoly(shape,points):
 im=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0

def masked(a,m):
 b=np.zeros_like(a);b[m]=a[m];return b

def put(a,p,dx=0,dy=0):
 ys,xs=np.where(p[:,:,3]>0);xx=xs+dx;yy=ys+dy;k=(xx>=0)&(xx<a.shape[1])&(yy>=0)&(yy<a.shape[0]);a[yy[k],xx[k]]=p[ys[k],xs[k]]

def fitrows(a,target):
 h=a.shape[0];need=h-target
 if need<=0:return a,list(range(h)),[]
 # Native editing of redundant internal bone/cloth rows, never smooth/noninteger image scaling.
 # Preserve skull silhouette, hand/foot ends. Source rows and every retained RGBA pixel remain explicit.
 candidates=list(range(23,max(24,h-10)));removed=[]
 for f in np.linspace(0,len(candidates)-1,need):
  i=round(f);r=candidates[i]
  while r in removed:r+=1
  removed.append(r)
 keep=[i for i in range(h) if i not in removed];assert len(keep)==target
 return a[keep].copy(),keep,sorted(removed)
raws={k:crop(load(V/f'palette_native_{k:02}.png')) for k in range(1,10)};frames=[master.copy()];record=[{'frame':1,'duration_ms':100,'source':'skeleton_B_left.png','exact_standing':True}];heads=[];earlymaps={};earlyheads={}
# First five poses retain the accepted WIP2 sequence; only native proportion/placement cleanup.
for k,target in [(2,94),(3,88),(4,80),(5,76)]:
 raw=raws[k];b,keep,removed=fitrows(raw,target);ox=48-b.shape[1]//2;oy=96-b.shape[0];a=np.zeros((96,96,4),np.uint8);put(a,b,ox,oy);frames.append(a)
 # The approved sketch has one skull in its upper-left. This mask is before row registration.
 hm=np.zeros(raw.shape[:2],bool);hm[:min(23,raw.shape[0]),:min(21,raw.shape[1])]=True;hp=masked(raw,hm)[keep];hc=np.zeros_like(a);put(hc,hp,ox,oy);earlyheads[k]=hc
 earlymaps[k]={'row_lookup':keep,'removed_internal_rows':removed,'offset':[ox,oy],'native_source_crop_size':[raw.shape[1],raw.shape[0]]}
 record.append({'frame':k,'duration_ms':[100,110,90,80,70][k-1],'source':f'WIP2 cell {k}','approved_early_pose':True,**earlymaps[k]})
# Keep and expose the exact first-five native frame sources before any landing work.
for k,a in enumerate(frames):Image.fromarray(a).save(V/f'preserved_first5_{k+1:02}.png')
# One head only: precisely split final heap into a skull layer plus a skull-free body.
hmask=np.zeros((96,96),bool);hmask[64:86,63:85]=True;hmask[86:89,70:84]=True;hmask &= end[:,:,3]>0
H=masked(end,hmask);B=end.copy();B[hmask]=0;assert np.array_equal(np.where(hmask[:,:,None],H,B),end)
Image.fromarray(H).save(V/'canonical_single_skull.png');Image.fromarray(B).save(V/'canonical_headless_heap.png')
# Explicit non-overlapping native groups: no whole heap is pasted behind a second skull.
yy,xx=np.indices((96,96));remaining=B[:,:,3]>0;groups={}
def take(n,m):
 global remaining
 m=m&remaining;groups[n]=masked(B,m);remaining&=~m
hands=maskpoly(B.shape,[(13,82),(31,83),(32,92),(15,94)])|maskpoly(B.shape,[(62,84),(83,83),(84,96),(62,96)])
take('hands',hands)
take('shoulder_pins',(xx<32)&(yy<83))
take('rib_spine',(xx>=32)&(yy<80))
take('shroud',maskpoly(B.shape,[(27,65),(36,67),(45,75),(63,81),(65,86),(54,88),(31,82),(25,75)]))
take('long_bones_pelvis',np.ones((96,96),bool));assert not remaining.any()
for n,a in groups.items():Image.fromarray(a).save(V/('heap_group_'+n+'.png'))
# Intermediate airborne torso, shoulder and limp complete arms from APPROVED frame5, no grounded hands.
r5=raws[5];keep=earlymaps[5]['row_lookup'];ox,oy=earlymaps[5]['offset'];n5=r5.shape;hm5=np.zeros(n5[:2],bool);hm5[:23,:21]=True
am=np.zeros(n5[:2],bool);am[30:67,:17]=True;am[35:66,40:50]=True
upper=maskpoly(n5,[(18,5),(34,5),(45,15),(47,36),(32,42),(14,39),(11,29),(13,18)])
pelvis=np.zeros(n5[:2],bool);pelvis[44:60,15:40]=True
fallmask=(am|upper|pelvis)&~hm5;fall=masked(r5,fallmask)[keep];fallc=np.zeros_like(end);put(fallc,fall,ox,oy)
# Airborne head from accepted frame5. One head travels right and down; no bitmap rotation/mirroring.
hp5=crop(earlyheads[5]);Image.fromarray(hp5).save(V/'skull_pose_droop.png')
# Existing WIP2 contains a drawn sideways skull. Extract JUST that one, never its second skull/body.
r6=raws[6];rollmask=maskpoly(r6.shape,[(13,10),(20,10),(25,13),(29,18),(27,25),(22,28),(14,27),(8,23),(8,16)])&(r6[:,:,3]>0);roll=crop(masked(r6,rollmask));Image.fromarray(roll).save(V/'skull_pose_roll.png')
# Exact canonical skull is the landing view; no different heap or fade/dissolve.
canon=crop(H);canonbbox=Image.fromarray(H).getbbox();headposes=[(hp5,(40,43),'droop'),(hp5,(51,57),'droop'),(roll,(62,72),'roll'),(canon,(71,78),'land'),(canon,(73,74),'bounce'),(canon,(73,75),'settle')]
# Per-stage body ownership: limbs drop once; arms are replaced by the one ground-hand group only on landing.
bodyposes=[{'long_bones_pelvis':(0,0),'shroud':(-3,-9)}, {'long_bones_pelvis':(0,0),'shroud':(-2,-6)}, {'long_bones_pelvis':(0,0),'shroud':(0,-4),'shoulder_pins':(0,-1),'rib_spine':(0,-2),'hands':(0,0)}, {'long_bones_pelvis':(0,0),'shroud':(0,-2),'shoulder_pins':(0,0),'rib_spine':(0,0),'hands':(0,0)}, {'long_bones_pelvis':(0,0),'shroud':(0,-1),'shoulder_pins':(0,0),'rib_spine':(0,0),'hands':(0,0)}, {'long_bones_pelvis':(0,0),'shroud':(0,0),'shoulder_pins':(0,0),'rib_spine':(0,0),'hands':(0,0)}]
for i,((hp,center,pose),body) in enumerate(zip(headposes,bodyposes)):
 k=i+6;a=np.zeros_like(end);bl=np.zeros_like(end)
 for n,(dx,dy) in body.items():put(bl,groups[n],dx,dy)
 if i<2:
  # No supported crouch: upper/arms remain disconnected and descend above already fallen long bones.
  put(bl,fallc,4 if i==0 else 8,10 if i==0 else 20)
 # Remove only isolated 1-3px segmentation crumbs in the skull-free falling body.
 if i<2:
  todo=set(zip(*np.where(bl[:,:,3]>0)))
  while todo:
   seed=todo.pop();cc=[seed];queue=[seed]
   while queue:
    sy,sx=queue.pop()
    for dy in [-1,0,1]:
     for dx in [-1,0,1]:
      pt=(sy+dy,sx+dx)
      if pt in todo:todo.remove(pt);queue.append(pt);cc.append(pt)
   if len(cc)<=5:
    for sy,sx in cc:bl[sy,sx]=0
 hx=center[0]-hp.shape[1]//2;hy=center[1]-hp.shape[0]//2;hl=np.zeros_like(end);put(hl,hp,hx,hy);put(a,bl);put(a,hl)
 frames.append(a);dd=L/f'{k:02}';dd.mkdir(exist_ok=True);Image.fromarray(bl).save(dd/'body_no_skull.png');Image.fromarray(hl).save(dd/'single_skull.png');record.append({'frame':k,'source':'approved WIP2 native limb groups + partitioned canonical heap','single_skull_pose':pose,'skull_center':[center[0],center[1]],'skull_bbox':list(Image.fromarray(hl).getbbox()),'skull_layer_count':1,'body_groups':{n:list(v) for n,v in body.items()},'airborne_torso_arms':i<2})
frames.append(end.copy());record.append({'frame':12,'source':'accepted front collapse final frame','exact_common_heap':True,'skull_layer_count':1,'skull_bbox':list(canonbbox)})
durations=[100,110,90,80,70,70,70,80,100,130,180,200];assert len(frames)==12
for k,(a,dur) in enumerate(zip(frames,durations)):
 record[k]['duration_ms']=dur;Image.fromarray(a).save(F/f'{k+1:02}.png')
 if k<5:
  hh=np.zeros_like(a)
  if k==0:hh[:15]=a[:15]
  else:hh=earlyheads[k+1]
  dd=L/f'{k+1:02}';dd.mkdir(exist_ok=True);bb=a.copy();bb[hh[:,:,3]>0]=0;Image.fromarray(bb).save(dd/'body_no_skull.png');Image.fromarray(hh).save(dd/'single_skull.png')
 if k==11:
  dd=L/'12';dd.mkdir(exist_ok=True);Image.fromarray(B).save(dd/'body_no_skull.png');Image.fromarray(H).save(dd/'single_skull.png')
sheet=Image.new('RGBA',(96*12,96))
for k,a in enumerate(frames):sheet.paste(Image.fromarray(a),(k*96,0))
sheet.save(O/'skeleton_B_collapse_left.png');(V/'frame_records.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));(V/'timing_entry.json').write_text(json.dumps({'frames':12,'durations_ms':durations,'loop':False,'sprite_sheet':'skeleton_B_collapse_left.png','hold_last_frame':True},indent=2))
board=Image.new('RGBA',(4*112,3*116),'#403D43');dr=ImageDraw.Draw(board)
for k,a in enumerate(frames):x=k%4*112+8;y=k//4*116;board.alpha_composite(Image.fromarray(a),(x,y));dr.text((x,y+99),str(k+1),fill='white')
board.resize((1792,1392),Image.Resampling.NEAREST).save(Q/'skeleton_B_collapse_left_contact_4x.png')
# Exact palette transparent 8x GIF. Every native pixel becomes an integer 8x8 block.
flat=[0,0,0]+pal.flatten().tolist();flat += [0]*(768-len(flat));ims=[]
for a in frames:
 ix=np.zeros((96,96),np.uint8)
 for k,c in enumerate(pal):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=k+1
 assert np.array_equal(ix>0,a[:,:,3]>0);im=Image.fromarray(ix).convert('P');im.putpalette(flat);ims.append(im.resize((768,768),Image.Resampling.NEAREST))
ims[0].save(Q/'skeleton_B_collapse_left_8x.gif',save_all=True,append_images=ims[1:],duration=durations,transparency=0,disposal=2,optimize=False)
print('Built12',sum(durations),'ms; canonical skull bbox',canonbbox)
