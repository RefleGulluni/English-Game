from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');P=R/'art/cemetery_v3/props';W=Path('/Users/mac/.codex/work/broken-wing-angel-20261030');O=W/'staged';S=O/'qc/fountain_broken_wing_01_sources';S.mkdir(parents=True,exist_ok=True);read=lambda p:np.array(Image.open(p).convert('RGBA'));L=np.array([.299,.587,.114]);a=read(P/'fountain_dry_01.png');b=a.copy();pool=read(P/'qc/entry_step2_sources/fountain_fullsize_revision/pool_full_native.png');angel=read(P/'qc/entry_step2_sources/fountain_fullsize_revision/angel_full_native.png');under=np.zeros_like(a);under[129:248,31:225]=pool;am=np.zeros(a.shape[:2],bool);am[71:209,100:157]=angel[:,:,3]>0
pal=np.unique(a[a[:,:,3]>0,:3],axis=0);pallum=pal@L
# Explicit native selection follows wing inner edge and never the robe.
# Remove the hanging lower feather half only, with a varied tooth-height.
cut_y={141:123,142:121,143:123,144:124,145:122,146:126,147:124,148:121,149:123,150:125,151:123,152:122,153:124,154:122,155:121,156:122}
wingmask=np.zeros((256,256),bool)
for y in range(119,163):
 xmin=141 if y<131 else 142 if y<141 else 143 if y<153 else 144
 for x in range(xmin,157):
  if y>=cut_y[x] and am[y,x]:wingmask[y,x]=True
b[wingmask]=under[wingmask]
# A2-3px fresh cleavage band on the retained original feathers; per-cell
# shade comes from existing feather values, with3 larger fracture facets.
fracture=np.zeros((256,256),bool)
for x,end in cut_y.items():
 for y in range(end-3,end):
  if am[y,x] and a[y,x,3]>0:
   v=float(a[y,x,:3]@L);depth=end-1-y
   target=np.clip(v+44+depth*10,138,198)
   candidates=np.flatnonzero((pallum>=130)&(pallum<=198));ix=candidates[np.argmin(abs(pallum[candidates]-target))];b[y,x,:3]=pal[ix];b[y,x,3]=255;fracture[y,x]=True
#7 fallen pieces, extracted from this actual removed wing; no rotation or
# mirror. Large pieces keep6-9px-long feather grooves rather than flat fill.
def poly(h,w,pts):
 im=Image.new('L',(w,h));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
specs=[
 {'name':'feather_large_1','crop':[143,133,152,139],'points':[(1,0),(6,0),(8,2),(7,4),(5,5),(1,5),(0,3)],'at':[158,183]},
 {'name':'feather_large_2','crop':[142,145,148,154],'points':[(1,0),(4,0),(5,2),(5,6),(3,8),(1,7),(0,4)],'at':[175,191]},
 {'name':'medium','crop':[147,128,152,132],'points':[(1,0),(3,0),(4,2),(2,3),(0,2)],'at':[89,190]},
 {'name':'small_a','crop':[144,139,147,141],'points':[(0,0),(2,0),(1,1),(0,1)],'at':[99,200]},
 {'name':'small_b','crop':[150,134,152,137],'points':[(0,0),(1,1),(1,2),(0,2)],'at':[164,201]},
 {'name':'small_c','crop':[145,148,146,150],'points':[(0,0),(0,1)],'at':[82,196]},
 {'name':'small_d','crop':[149,141,151,143],'points':[(0,0),(1,0),(1,1),(0,1)],'at':[171,184]}
]
shards=np.zeros_like(a);records=[]
for i,s in enumerate(specs):
 x0,y0,x1,y1=s['crop'];t=a[y0:y1,x0:x1].copy();h,w=t.shape[:2];m=poly(h,w,s['points']);m &=t[:,:,3]>0;d=np.zeros_like(t)
 # Fresh clean stone: relight from native feather shading without adding
 # noise. Keep engraved feather darks; top-left cleavededge is pale.
 for y,x in zip(*np.where(m)):
  v=float(t[y,x,:3]@L)
  edge=y==0 or x==0 or (y>0 and not m[y-1,x])
  target=np.clip(v+43+(15 if edge else 0),115,184)
  eligible=np.flatnonzero((pallum>=106)&(pallum<=184));c=pal[eligible[np.argmin(abs(pallum[eligible]-target))]];d[y,x]=[*c,255]
 px,py=s['at'];area=shards[py:py+h,px:px+w];assert not((area[:,:,3]>0)&m).any();area[m]=d[m];b[py:py+h,px:px+w][m]=d[m];Image.fromarray(d).save(S/(s['name']+'.png'));records.append({**s,'pixel_count':int(m.sum()),'bbox_exclusive':[px,py,px+w,py+h],'max_luma':float((d[m,:3]@L).max())})
# Differences must be confined to approvedwing and the7shard masks.
shardmask=shards[:,:,3]>0;allowed=wingmask|fracture|shardmask;diff=(b!=a).any(2);assert not(diff&~allowed).any();assert not (diff[:,:141]&~shardmask[:,:141]).any();assert np.array_equal(a[:118, :],b[:118,:]);assert np.array_equal(a[72:105,100:137],b[72:105,100:137])
assert np.array_equal(a[shardmask],under[shardmask]) # all7pieces lie on original pool floor, not statue
newcolors=set(map(tuple,b[b[:,:,3]>0,:3]))-set(map(tuple,a[a[:,:,3]>0,:3]));assert not newcolors;assert set(np.unique(b[:,:,3]))<={0,255};b[b[:,:,3]==0]=0
Image.fromarray(b).save(O/'fountain_broken_wing_01.png');shutil.copy2(P/'fountain_dry_01_base.png',O/'fountain_broken_wing_01_base.png');Image.fromarray(under).save(S/'underlying_pool_native.png');Image.fromarray(wingmask.astype(np.uint8)*255).save(S/'removed_wing_mask.png');Image.fromarray(fracture.astype(np.uint8)*255).save(S/'fracture_mask.png');Image.fromarray(shards).save(S/'shards_layer.png');Image.fromarray(diff.astype(np.uint8)*255).save(S/'actual_diff_mask.png')
ys,xs=np.where(diff);metrics={'canvas':[256,256],'origin':[128,256],'changed_pixel_count':int(diff.sum()),'changed_bbox_inclusive':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],'wing_removed_pixel_count':int(wingmask.sum()),'fracture_band_pixels':int(fracture.sum()),'shard_pixel_count':int(shardmask.sum()),'shards':records,'new_colors':len(newcolors),'outside_approved_masks_changed':0,'face_and_body_check':'x<141 unchanged except explicitly listed pool shards; face/head and upperwing y<118 unchanged','source_png_sha256':hashlib.sha256((P/'fountain_dry_01.png').read_bytes()).hexdigest(),'source_base_png_sha256':hashlib.sha256((P/'fountain_dry_01_base.png').read_bytes()).hexdigest(),'base_byte_exact_copy':True,'cut_y_by_column':cut_y,'wing_inner_boundary_rule':'y119..130 x>=141; y131..140 x>=142; y141..152 x>=143; y153..162 x>=144; intersect original angel alpha','no_resize_rotation_mirror':True};(S/'edit_metrics.json').write_text(json.dumps(metrics,indent=2))
# Nearest preview only, preserve final256x256 runtime canvas.
old=Image.open(P/'fountain_dry_01_base.png').convert('RGBA');old.alpha_composite(Image.fromarray(a));new=Image.open(O/'fountain_broken_wing_01_base.png').convert('RGBA');new.alpha_composite(Image.fromarray(b));c=Image.new('RGBA',(512,256),'#403d40');c.alpha_composite(old,(0,0));c.alpha_composite(new,(256,0));ImageDraw.Draw(c).text((12,24),'ORIGINAL',fill='#d6cbb7');ImageDraw.Draw(c).text((268,24),'BROKEN WING',fill='#d6cbb7');c.resize((3072,1536),Image.Resampling.NEAREST).save(O/'qc/fountain_broken_wing_01_compare_6x.png');new.resize((1536,1536),Image.Resampling.NEAREST).save(S/'final_6x.png')
zoom=Image.new('RGBA',(180,140),'#454540');zoom.alpha_composite(old.crop((100,80,160,170)),(0,0));zoom.alpha_composite(new.crop((100,80,160,170)),(70,0));zoom.alpha_composite(new.crop((75,175,190,207)),(0,100));zoom.resize((1080,840),Image.Resampling.NEAREST).save(S/'detail_check_6x.png');print(json.dumps({k:v for k,v in metrics.items() if k!='shards'},indent=2))
