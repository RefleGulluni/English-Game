from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');P=R/'art/cemetery_v3/props';W=Path('/Users/mac/.codex/work/broken-wing-v2-20261030');O=W/'staged';S=O/'qc/fountain_broken_wing_01_v2_sources';S.mkdir(parents=True,exist_ok=True);read=lambda p:np.array(Image.open(p).convert('RGBA'));L=np.array([.299,.587,.114]);a=read(P/'fountain_dry_01.png');b=a.copy();pool=read(P/'qc/entry_step2_sources/fountain_fullsize_revision/pool_full_native.png');angel=read(P/'qc/entry_step2_sources/fountain_fullsize_revision/angel_full_native.png');under=np.zeros_like(a);under[129:248,31:225]=pool;am=np.zeros((256,256),bool);am[71:209,100:157]=angel[:,:,3]>0;pal=np.unique(a[a[:,:,3]>0,:3],axis=0);lum=pal@L
cut={140:106,141:107,142:104,143:106,144:109,145:107,146:105,147:108,148:106,149:104,150:107,151:106,152:105,153:107,154:105,155:106,156:105}
def inner(y):return 140 if y<112 else 141 if y<131 else 142 if y<141 else 143 if y<153 else 144
removed=np.zeros((256,256),bool);edge=np.zeros_like(removed)
for y in range(101,163):
 for x in range(inner(y),157):
  if y>=cut[x] and am[y,x]:removed[y,x]=True
b[removed]=under[removed]
def shade(v,target_min=0,target_max=198):
 ids=np.flatnonzero((lum>=target_min)&(lum<=target_max));return pal[ids[np.argmin(abs(lum[ids]-v))]]
for x,end in cut.items():
 for y in range(end-3,end):
  if am[y,x]:
   v=float(a[y,x,:3]@L);target=np.clip(v+55+(end-y-1)*8,142,198);b[y,x]=[*shade(target,130,198),255];edge[y,x]=True
# Main recognizable26px feathered wing portion. Integer row translations
# reassemble a lean; original pixels aren't rotated, mirrored or rescaled.
src=[140,107,157,133];x0,y0,x1,y1=src;main=np.zeros((26,30,4),np.uint8);mainmap=[]
for y in range(26):
 shift=y//2
 for x in range(17):
  sx=x0+x;sy=y0+y
  if not am[sy,sx] or sx<inner(sy):continue
  # Keep only the visible original wing, not any adjacent statue or pool.
  if not removed[sy,sx]:continue
  v=float(a[sy,sx,:3]@L);target=np.clip(v+(18 if v<65 else 42),65,190)
  if y<2:target=np.clip(v+58,160,198)
  main[y,x+shift]=[*shade(target,65,198),255];mainmap.append([sx,sy,x+shift,y])
# Native feather-tip shape is retained; missing cells remain transparent.
mainxy=[92,178];records=[];pieces=np.zeros_like(a)
def paste_piece(n,p,xy,extra):
 global b
 px,py=xy;m=p[:,:,3]>0;h,w=p.shape[:2];assert not((pieces[py:py+h,px:px+w,3]>0)&m).any();pieces[py:py+h,px:px+w][m]=p[m];b[py:py+h,px:px+w][m]=p[m];Image.fromarray(p).save(S/(n+'.png'));yy,xx=np.where(m);records.append({'name':n,'bbox_exclusive':[px+int(xx.min()),py+int(yy.min()),px+int(xx.max())+1,py+int(yy.max())+1],'pixel_count':int(m.sum()),**extra})
paste_piece('main_wing_chunk',main,mainxy,{'source_crop':src,'source_to_piece_xy_map':mainmap,'assembly':'each native row translated floor(y/2)px, not rotated or mirrored','location':'front-left pool floor next to pedestal, broad feather surfaces on dark mud','length_px':26})
def poly(h,w,pts):
 im=Image.new('L',(w,h));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
specs=[
 {'name':'floor_medium_left','crop':[144,114,153,120],'shape':[(1,0),(6,0),(8,2),(7,4),(5,5),(1,4),(0,2)],'at':[87,190],'on_rim':False},
 {'name':'floor_medium_right','crop':[143,128,151,133],'shape':[(2,0),(6,0),(7,2),(5,4),(1,4),(0,2)],'at':[167,193],'on_rim':False},
 {'name':'rim_medium_front','crop':[144,138,152,144],'shape':[(1,0),(5,0),(7,2),(6,5),(2,5),(0,3)],'at':[110,209],'on_rim':True},
 {'name':'rim_medium_right','crop':[143,120,150,126],'shape':[(1,0),(5,0),(6,2),(5,5),(2,5),(0,3)],'at':[177,201],'on_rim':True}
]
for s in specs:
 x0,y0,x1,y1=s['crop'];t=a[y0:y1,x0:x1];h,w=t.shape[:2];m=poly(h,w,s['shape']);d=np.zeros_like(t)
 for y,x in zip(*np.where(m)):
  v=float(t[y,x,:3]@L);target=v+(8 if s['on_rim'] else 30)
  if y==0 or (y>0 and not m[y-1,x]):target=v+56
  # A darker sideface distinguishes rubble laid onto the bright rim.
  elif y==h-1 or (y<h-1 and not m[y+1,x]):target=v+1
  d[y,x]=[*shade(np.clip(target,75,198),65,198),255]
 paste_piece(s['name'],d,s['at'],{'source_crop':s['crop'],'location':'pool rim' if s['on_rim'] else 'front half pool floor','on_rim':s['on_rim']})
pm=pieces[:,:,3]>0;allowed=removed|edge|pm;diff=(a!=b).any(2);assert not(diff&~allowed).any();assert np.array_equal(a[71:101,:],b[71:101,:]);assert np.array_equal(a[72:170,100:140],b[72:170,100:140]);assert np.array_equal(b[removed&~pm],under[removed&~pm]);assert not(set(map(tuple,b[b[:,:,3]>0,:3]))-set(map(tuple,pal)));b[b[:,:,3]==0]=0
Image.fromarray(b).save(O/'fountain_broken_wing_01.png');Image.fromarray(pieces).save(S/'pieces_layer.png');Image.fromarray(removed.astype(np.uint8)*255).save(S/'removed_wing_mask.png');Image.fromarray(edge.astype(np.uint8)*255).save(S/'stump_fracture_mask.png');Image.fromarray(diff.astype(np.uint8)*255).save(S/'actual_diff_mask.png')
yy,xx=np.where(diff);metrics={'canvas':[256,256],'origin':[128,256],'new_colors':0,'changed_pixels':int(diff.sum()),'changed_bbox_inclusive':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],'removed_wing_pixels':int(removed.sum()),'stump_fracture_pixels':int(edge.sum()),'stump_end_y_by_column':cut,'retained_wing_height_range_px':[20,25],'original_wing_height_px':77,'pieces':records,'pieces_total':len(records),'medium_pieces':4,'rim_pieces':2,'outside_masks_changed':0,'no_rotation_mirror_scaling':True,'body_face_protected_region':[100,72,140,170],'original_fountain_png_sha256':hashlib.sha256((P/'fountain_dry_01.png').read_bytes()).hexdigest(),'original_base_png_sha256':hashlib.sha256((P/'fountain_dry_01_base.png').read_bytes()).hexdigest(),'base_unchanged':True};(S/'edit_metrics.json').write_text(json.dumps(metrics,indent=2))
base=Image.open(P/'fountain_dry_01_base.png').convert('RGBA');old=base.copy();old.alpha_composite(Image.fromarray(a));new=base.copy();new.alpha_composite(Image.fromarray(b));c=Image.new('RGBA',(512,256),'#403d40');c.alpha_composite(old,(0,0));c.alpha_composite(new,(256,0));c.save(O/'qc/fountain_broken_wing_01_1x_compare.png');c.resize((3072,1536),Image.Resampling.NEAREST).save(O/'qc/fountain_broken_wing_01_compare_6x.png');new.resize((1536,1536),Image.Resampling.NEAREST).save(S/'final_6x.png')
# Shoulder and big fragment closeup is supportingQC only, not1x acceptance.
z=Image.new('RGBA',(140,140),'#454540');z.alpha_composite(new.crop((100,80,160,170)),(0,0));z.alpha_composite(new.crop((130,170,190,225)),(70,0));z.resize((840,840),Image.Resampling.NEAREST).save(S/'details_6x.png')
print(json.dumps({k:v for k,v in metrics.items() if k!='pieces'},indent=2))
