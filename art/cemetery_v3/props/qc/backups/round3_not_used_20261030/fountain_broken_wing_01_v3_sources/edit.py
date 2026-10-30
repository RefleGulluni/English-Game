from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');P=R/'art/cemetery_v3/props';W=Path('/Users/mac/.codex/work/shatter-v3-20261030');O=W/'staged';S=O/'qc/fountain_broken_wing_01_v3_sources';S.mkdir(parents=True,exist_ok=True);read=lambda p:np.array(Image.open(p).convert('RGBA'));L=np.array([.299,.587,.114]);a=read(P/'fountain_dry_01.png');b=a.copy();pal=np.unique(a[a[:,:,3]>0,:3],axis=0);lum=pal@L;pool=read(P/'qc/entry_step2_sources/fountain_fullsize_revision/pool_full_native.png');angel=read(P/'qc/entry_step2_sources/fountain_fullsize_revision/angel_full_native.png');under=np.zeros_like(a);under[129:248,31:225]=pool;am=np.zeros((256,256),bool);am[71:209,100:157]=angel[:,:,3]>0
cut={140:104,141:103,142:106,143:110,144:109,145:103,146:101,147:104,148:111,149:108,150:105,151:101,152:103,153:108,154:105,155:102,156:102}
def inner(y):return 140 if y<112 else 141 if y<131 else 142 if y<141 else 143 if y<153 else 144
def shade(v,low=0,high=198):
 ix=np.flatnonzero((lum>=low)&(lum<=high));return pal[ix[np.argmin(abs(lum[ix]-v))]]
removed=np.zeros((256,256),bool);fracture=np.zeros_like(removed);recess=np.zeros_like(removed);crack=np.zeros_like(removed)
for y in range(98,163):
 for x in range(inner(y),157):
  if y>=cut[x] and am[y,x]:removed[y,x]=True
#3extra silhouette chips opening into the fresh fracture, plus dark recesswalls.
notches=[{'missing':[(146,100),(147,102)],'dark':[(145,99),(145,100),(146,99)]},{'missing':[(151,100),(152,102)],'dark':[(150,99),(150,100),(151,99)]},{'missing':[(154,104),(155,101)],'dark':[(153,102),(154,102),(154,103)]}]
for n in notches:
 for x,y in n['missing']:
  if am[y,x]:removed[y,x]=True
b[removed]=under[removed]
for x,end in cut.items():
 for y in range(end-3,end):
  if am[y,x] and not removed[y,x]:b[y,x]=[*shade(np.clip(a[y,x,:3]@L+55+(end-y-1)*8,143,198),130,198),255];fracture[y,x]=True
for n in notches:
 for x,y in n['dark']:
  if am[y,x] and not removed[y,x]:b[y,x]=[*shade(68+(x+y)%2*10,45,95),255];recess[y,x]=True
cracks=[[(143,108),(143,107),(143,106),(142,105),(142,104),(142,103),(141,102),(141,101),(141,100),(142,99),(142,98),(143,104),(144,103),(144,102),(145,102)],[(148,109),(148,108),(148,107),(148,106),(148,105),(148,104),(148,103),(148,102),(147,101),(147,100),(146,99),(145,98),(145,97),(149,103),(149,102),(150,101)],[(153,106),(153,105),(153,104),(153,103),(153,102),(152,101),(152,100),(151,99),(151,98),(150,97),(150,96),(149,95),(153,100),(154,99)]]
for path in cracks:
 for x,y in path:
  if am[y,x] and not removed[y,x]:b[y,x]=[*shade(47,30,65),255];crack[y,x]=True
# Cut actual nonoverlapping cells out of the missing originalwing. Angular
# masks select source art; no new noise, rotation, mirroring or scaling.
available=removed.copy();source_used=np.zeros_like(removed);pieces=np.zeros_like(a);records=[]
def polygon(w,h,pts):
 im=Image.new('L',(w,h));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
def connected(m):
 todo=set(zip(*np.where(m)))
 if not todo:return False
 q=[todo.pop()]
 while q:
  y,x=q.pop()
  for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
   p=(y+dy,x+dx)
   if p in todo:todo.remove(p);q.append(p)
 return not todo

def extract(w,h,points,prefer_y):
 shape=polygon(w,h,points);best=None
 for y in range(99,163-h+1):
  for x in range(140,157-w+1):
   m=shape&available[y:y+h,x:x+w];cnt=int(m.sum())
   if cnt<max(5,int(shape.sum()*.52)) or not connected(m):continue
   yy,xx=np.where(m)
   if xx.max()-xx.min()+1<3 or yy.max()-yy.min()+1<3:continue
   score=cnt-abs(y-prefer_y)*.018
   if best is None or score>best[0]:best=(score,x,y,m)
 assert best is not None,(w,h,prefer_y)
 _,x,y,m=best;assert not source_used[y:y+h,x:x+w][m].any();available[y:y+h,x:x+w][m]=False;source_used[y:y+h,x:x+w][m]=True
 return a[y:y+h,x:x+w].copy(),m,[x,y,x+w,y+h]

specs=[
 ('medium_feather_A',13,12,[(0,0),(9,1),(12,6),(7,11),(1,8),(3,5)],[154,169],'floor_dense',108),
 ('medium_feather_B',12,13,[(0,2),(8,0),(11,8),(4,12),(0,6)],[167,183],'floor_dense',132),
 ('step_small_A',8,7,[(1,0),(7,0),(6,6),(0,6)],[142,179],'pedestal_step',121),
 ('step_small_B',8,7,[(0,0),(7,1),(6,6),(0,5)],[145,195],'pedestal_step',128),
 ('dense_small_A',7,7,[(0,0),(6,1),(5,6),(0,6)],[174,174],'floor_dense',145),
 ('dense_small_B',8,7,[(0,0),(7,1),(6,6),(1,6)],[155,185],'floor_dense',139),
 ('dense_small_C',7,7,[(1,0),(6,0),(6,6),(0,5)],[158,197],'floor_outer',150),
 ('rim_small_A',8,7,[(0,1),(6,0),(7,5),(1,6)],[187,190],'pool_rim',115),
 ('rim_small_B',8,7,[(0,0),(7,1),(6,6),(0,5)],[165,212],'pool_rim',134),
 ('outer_small_A',6,6,[(0,0),(5,0),(4,5),(0,4)],[94,195],'floor_outer',153),
 ('outer_small_B',6,6,[(0,1),(5,0),(5,5),(0,4)],[83,184],'floor_outer',105)
]
for name,w,h,pts,xy,loc,sy in specs:
 src,m,box=extract(w,h,pts,sy);p=np.zeros_like(src)
 for y,x in zip(*np.where(m)):
  v=float(src[y,x,:3]@L);top=y==0 or not m[y-1,x];side=y>=h-2 or not m[min(h-1,y+1),x] or x==w-1 or not m[y,min(w-1,x+1)]
  if top:target=np.clip(v+70,165,198)
  elif side:target=np.clip(v+3,65,115)
  else:target=np.clip(v+34,110,184)
  p[y,x]=[*shade(target,60,198),255]
 px,py=xy;dst=pieces[py:py+h,px:px+w];assert not((dst[:,:,3]>0)&m).any(),name;dst[m]=p[m];b[py:py+h,px:px+w][m]=p[m];Image.fromarray(p).save(S/(name+'.png'));yy,xx=np.where(m);records.append({'name':name,'class':'medium' if name.startswith('medium') else 'small','source_crop':box,'source_mask_pixels':[[int(x),int(y)] for y,x in zip(*np.where(m))],'destination':xy,'bbox_exclusive':[px+int(xx.min()),py+int(yy.min()),px+int(xx.max())+1,py+int(yy.max())+1],'pixel_count':int(m.sum()),'location':loc})
# Authored sparse-to-dense chips. Their source cells are also never duplicated.
chip_positions=[(153,167),(160,165),(168,169),(172,171),(181,183),(181,194),(159,182),(151,187),(163,194),(162,205),(178,201),(137,201),(131,208),(112,192),(100,201),(89,190),(184,198),(166,206)]
chiprecords=[]
for k,(px,py) in enumerate(chip_positions):
 yy,xx=np.where(available);assert len(yy);sy,sx=int(yy[0]),int(xx[0]);count=2 if k%3!=1 and sx+1<157 and available[sy,sx+1] else 1
 for d in range(count):
  assert pieces[py,px+d,3]==0;v=a[sy,sx+d,:3]@L;col=shade(np.clip(v+66 if d==0 else v+8,85,198),65,198);pieces[py,px+d]=[*col,255];b[py,px+d]=[*col,255];available[sy,sx+d]=False;source_used[sy,sx+d]=True
 chiprecords.append({'source_xy':[sx,sy],'destination_xy':[px,py],'pixel_count':count})
pm=pieces[:,:,3]>0;allowed=removed|fracture|recess|crack|pm;diff=(b!=a).any(2);assert not(diff&~allowed).any();assert np.array_equal(a[72:170,100:140],b[72:170,100:140]);assert np.array_equal(b[removed],under[removed]);assert not(set(map(tuple,b[b[:,:,3]>0,:3]))-set(map(tuple,pal)));assert int(pm.sum())==int(source_used.sum());b[b[:,:,3]==0]=0
Image.fromarray(b).save(O/'fountain_broken_wing_01.png')
for label,arr in [('pieces_layer',pieces),('removed_wing_mask',removed.astype(np.uint8)*255),('fracture_mask',fracture.astype(np.uint8)*255),('recess_mask',recess.astype(np.uint8)*255),('crack_mask',crack.astype(np.uint8)*255),('actual_diff_mask',diff.astype(np.uint8)*255),('source_cells_used_mask',source_used.astype(np.uint8)*255)]:Image.fromarray(arr).save(S/(label+'.png'))
yy,xx=np.where(diff);metrics={'canvas':[256,256],'origin':[128,256],'revision':3,'new_colors':0,'changed_pixels':int(diff.sum()),'changed_bbox_inclusive':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],'removed_wing_pixels':int(removed.sum()),'pieces_pixels':int(pm.sum()),'pieces_area_ratio_of_removed':round(float(pm.sum()/removed.sum()),4),'medium_count':2,'small_count':9,'chip_groups':len(chiprecords),'rim_pieces':2,'step_pieces':2,'notches':notches,'crack_paths':cracks,'cut_end_y_by_column':cut,'pieces':records,'chips':chiprecords,'source_cells_reused':0,'outside_allowed_mask_changed':0,'no_scaling_rotation_mirroring':True,'base_unchanged':True,'original_png_sha256':hashlib.sha256((P/'fountain_dry_01.png').read_bytes()).hexdigest(),'base_png_sha256':hashlib.sha256((P/'fountain_dry_01_base.png').read_bytes()).hexdigest()};(S/'edit_metrics.json').write_text(json.dumps(metrics,indent=2))
base=Image.open(P/'fountain_dry_01_base.png').convert('RGBA');panels=[]
for im in [Image.fromarray(a),Image.open(W/'v2_comparison_source.png').convert('RGBA'),Image.fromarray(b)]:c=base.copy();c.alpha_composite(im);panels.append(c)
board=Image.new('RGBA',(768,256),'#403d40')
for k,p in enumerate(panels):board.alpha_composite(p,(256*k,0))
board.save(O/'qc/fountain_broken_wing_01_1x_compare.png')
two=Image.new('RGBA',(512,256),'#403d40');two.alpha_composite(panels[0],(0,0));two.alpha_composite(panels[2],(256,0));two.resize((3072,1536),Image.Resampling.NEAREST).save(O/'qc/fountain_broken_wing_01_compare_6x.png');panels[2].resize((1536,1536),Image.Resampling.NEAREST).save(S/'final_6x.png')
# Crop only for supplementary detail, not native-size acceptance.
z=Image.new('RGBA',(160,150),'#454540');z.alpha_composite(panels[2].crop((132,87,158,114)),(5,3));z.alpha_composite(panels[2].crop((136,160,202,221)),(55,3));z.resize((960,900),Image.Resampling.NEAREST).save(S/'detail_6x.png');print(json.dumps({k:v for k,v in metrics.items() if k not in ['pieces','chips','cut_end_y_by_column','notches','crack_paths']},indent=2))
