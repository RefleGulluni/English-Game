from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
S=Path(__file__).resolve().parent;B=S.parent.parent;REPO=B.parents[2];Q=B/'qc'
raw=Image.open(S/'02_restored_cells.png').convert('RGB');a=np.array(raw).astype(int)
keep=(a[:,:,0]<110)&(a[:,:,1]<115)&(a[:,:,2]<130)&(a.max(2)-a.min(2)<60)
yy,xx=np.where(keep);bbox=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
# Native crop, not a resize: omit the lowest19 rows of the oversized generated mass.
# This is the plain base meant to disappear into fog, not an architectural roof.
crop=(bbox[0],bbox[1],bbox[2],bbox[1]+93)
a=a[crop[1]:crop[3],crop[0]:crop[2]];keep=keep[crop[1]:crop[3],crop[0]:crop[2]]
h,w=keep.shape
out=np.zeros((h,w,4),np.uint8)
light=a.mean(2)>64
out[keep&~light]=(45,49,56,255);out[keep&light]=(53,58,66,255)
# Keep exactly3 dark source windows, discard all other doorway/window marks.
window_boxes=[(61,52,63,64),(17,74,20,93),(90,77,93,96)]
window=np.zeros(keep.shape,bool)
for x0,y0,x1,y1 in window_boxes:
 x0-=crop[0];x1-=crop[0];y0-=crop[1];y1-=crop[1]
 window[max(0,y0):min(h,y1),max(0,x0):min(w,x1)]=True
window&=(a[:,:,0]<38)&(a[:,:,1]<43)&(a[:,:,2]<49)&keep
out[window]=(33,37,44,255)
# Align the actual topmost cross pixel, not the off-center nave's bounding box.
tip_y=int(np.where(keep.any(1))[0][0]);tip_x=int(round(np.where(keep[tip_y])[0].mean()))
xpos=480-tip_x;ypos=3
# Discrete material ramps (opaque colors, no soft-alpha/gradient) toward old land.
ramps=[(62,(53,58,66)),(72,(61,67,75)),(82,(68,74,82)),(88,(72,78,86)),(92,(74,80,88)),(95,(75,81,89))]
for y in range(h):
 gy=ypos+y
 c=None
 for gy0,col in ramps:
  if gy>=gy0:c=col
 if c is not None:
  out[y,keep[y],:3]=c
  if gy<84:
   out[y,window[y],:3]=tuple(max(0,k-7) for k in c)
chapel=Image.fromarray(out);chapel.save(S/'03_chapel_cleaned_native.png')
# Recompose the exact accepted sky/skyline layers, removing the old small chapel.
sky=Image.open(B/'source/sky_native.png').convert('RGBA')
land=Image.open(B/'source/skyline_repaired_native.png').convert('RGBA')
base=sky.copy();base.alpha_composite(land)
old=Image.open(B/'entry_backdrop_01.png').convert('RGBA')
meta_old=json.loads((B/'source/assembly_metadata.json').read_text())
oldchapel=Image.open(B/'source/chapel_cleaned_native.png').convert('RGBA')
oldmask=Image.new('RGBA',(960,100));oldmask.alpha_composite(oldchapel,tuple(meta_old['chapel']['placement_top_left']))
old_visible=(np.array(oldmask)[:,:,3]>0)&(np.array(land)[:,:,3]==0)
removed_old=np.any(np.array(old)!=np.array(base),axis=2)
assert not (removed_old&~old_visible).any(),'Accepted source layers no longer match01 outside old chapel'
placed=Image.new('RGBA',(960,100));placed.alpha_composite(chapel,(xpos,ypos));p=np.array(placed)
footprint=p[:,:,3]>0
# Preserve old side slope pixels at the nave edges; let central body cross ridge
# as explicitly clarified by user. Only inside the new chapel footprint changes.
ygrid,xgrid=np.indices((100,960));land_alpha=np.array(land)[:,:,3]>0
front=land_alpha&((xgrid<439)|(xgrid>523))
slopes=Image.new('1',(960,100));dr=ImageDraw.Draw(slopes)
dr.polygon([(428,59),(439,65),(442,75),(448,86),(453,96),(428,96)],fill=1)
dr.polygon([(528,64),(519,69),(515,82),(510,96),(528,96)],fill=1)
front|=np.array(slopes).astype(bool)
front&=footprint
p[front]=(76,82,90,255)
final=base.copy();final.alpha_composite(Image.fromarray(p));final.save(B/'entry_backdrop_02.png')
visible=footprint&~front
vx,vy=None,None
yv,xv=np.where(visible);vb=[int(xv.min()),int(yv.min()),int(xv.max()+1),int(yv.max()+1)]
# Explicit coverage/difference masks support the claim that accepted background is reused.
mask=np.zeros((100,960,4),np.uint8);mask[visible]=(255,80,160,255);Image.fromarray(mask).save(S/'04_visible_chapel_mask.png')
allowed=old_visible|footprint
changed=np.any(np.array(old)!=np.array(final),axis=2)
assert not (changed&~allowed).any(),'Unrelated accepted pixels changed'
Image.fromarray(np.where(changed[:,:,None],np.array([255,80,160,255],np.uint8),np.array([0,0,0,0],np.uint8))).save(S/'04_change_mask_vs_01.png')
final.resize((1920,200),Image.Resampling.NEAREST).save(Q/'entry_backdrop_02_2x.png')
chapel.resize((w*6,h*6),Image.Resampling.NEAREST).save(Q/'chapel_02_native_6x.png')
comparison=Image.new('RGBA',(960,200));comparison.alpha_composite(old);comparison.alpha_composite(final,(0,100));comparison.resize((1920,400),Image.Resampling.NEAREST).save(Q/'backdrop_01_vs_02_2x.png')
grey=Image.open(REPO/'docs/reference/cemetery_entry_greybox.png').convert('RGBA').crop((0,0,960,540));grey.alpha_composite(final);grey.resize((1920,1080),Image.Resampling.NEAREST).save(Q/'backdrop_02_on_greybox_2x.png')
# All source/accepted assets are still identical to the pre-edit hashes.
hashes=json.loads((Q/'backups/before_chapel_02/protected_asset_hashes.json').read_text())
for rel,expected in hashes.items():assert hashlib.sha256((B/rel).read_bytes()).hexdigest()==expected,rel
metadata={'generated_native_bbox':bbox,'native_crop_xyxy':crop,'native_crop_size':[w,h],'placement_top_left':[xpos,ypos],'steeple_tip':[xpos+tip_x,ypos+tip_y],'visible_bbox_xyxy':vb,'visible_size':[vb[2]-vb[0],vb[3]-vb[1]],'opaque_material_ramp_world_y':ramps,'three_source_window_boxes':window_boxes,'changed_pixels_vs_01':int(changed.sum()),'unrelated_background_pixels_changed':int((changed&~allowed).sum()),'protected_assets_hashes_unchanged':True,'composition_note':'User clarified: chapel body crosses ridge, lower mass extends to95 for runtime fog. Original side slope color occludes only lateral chapel footprint. No new fog baked in.'}
(S/'05_assembly_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps(metadata,indent=2))
