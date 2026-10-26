from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
S=Path(__file__).resolve().parent;B=S.parent.parent;Q=B/'qc';R=B.parents[2]
# The edit retains the source99x93 logical layout at a larger displayed scale.
# Check those registered block boundaries and sample one center per cell.
im=Image.open(S/'01_roof_edit_generated.png').convert('RGBA');raw=np.array(im)
xs=[round(i*im.width/99) for i in range(100)];ys=[round(i*im.height/93) for i in range(94)]
xc=[(l+r-1)//2 for l,r in zip(xs,xs[1:])];yc=[(l+r-1)//2 for l,r in zip(ys,ys[1:])]
cells=raw[np.ix_(yc,xc)]
assert np.array_equal(cells,np.array(Image.open(S/'02_restored_edit_cells.png')))
(S/'02_grid.json').write_text(json.dumps({'source_size':list(im.size),'native_grid':[99,93],'x_boundaries':xs,'y_boundaries':ys,'x_centers':xc,'y_centers':yc,'note':'Registered enlarged99x93 edit grid; each cell takes one integer center pixel. Only binary side-roof silhouettes used, no image resize/averaging. Generated central tower/colors/soft edges are discarded.'},indent=2)+'\n')
grid=im.copy();dr=ImageDraw.Draw(grid)
for x in xs[1:-1]:dr.line((x,0,x,im.height-1),fill=(40,215,190,255))
for y in ys[1:-1]:dr.line((0,y,im.width-1,y),fill=(40,215,190,255))
grid.save(S/'02_grid_overlay.png')
# Binary alpha only; generated antialiasing/soft alpha never enters runtime sprite.
shape=cells[:,:,3]>=128
left=[int(np.where(shape[:,x])[0][0]) for x in range(13,40)]
right=[int(np.where(shape[:,x])[0][0]) for x in range(73,94)]
assert (np.diff(left)<=0).all(),left
assert (np.diff(right)>=0).all(),right
old=Image.open(B/'entry_backdrop_02.png').convert('RGBA');a=np.array(old)
sky=Image.open(B/'source/sky_native.png').convert('RGBA');land=Image.open(B/'source/skyline_repaired_native.png').convert('RGBA');base=sky.copy();base.alpha_composite(land);bg=np.array(base)
church=Image.open(B/'source/chapel_02/03_chapel_cleaned_native.png').convert('RGBA')
m=json.loads((B/'source/chapel_02/05_assembly_metadata.json').read_text());x0,y0=m['placement_top_left']
placed=Image.new('RGBA',(960,100));placed.alpha_composite(church,(x0,y0));foot=np.array(placed)[:,:,3]>0
Y,X=np.indices((100,960))
# Preserve exact original tower pixels, including its outer buttresses.
roof_rois=((X>=439)&(X<=472)|(X>=490)&(X<=522))&(Y<64)
protected_tower=foot&(X>=466)&(X<499)&(Y<64)
remove=foot&roof_rois&~protected_tower
out=a.copy();out[remove]=bg[remove]
newroof=np.zeros((100,960),bool)
# Integer upward positioning makes the modest side halls readable above fog.
# It uses the edited native silhouette, never a stretch or a procedural texture.
shift=-8
for lo,hi in [(13,47),(64,97)]:
 for lx in range(lo,hi):
  wx=x0+lx
  for ly in range(93):
   wy=y0+ly+shift
   if 0<=wy<64 and shape[ly,lx] and roof_rois[wy,wx] and not protected_tower[wy,wx]:
    # Continue the roof across the old empty gap, without adding a second tower.
    if (wx<=465 or wx>=499) or wy>=(47 if wx<480 else 49):newroof[wy,wx]=True
out[newroof]=(45,49,56,255)
# Requested exact replacement, no lower ramp and no baked fog.
lower=foot&(Y>=64);out[lower]=(76,82,90,255)
result=Image.fromarray(out);result.save(B/'entry_backdrop_03.png')
allowed=roof_rois|lower
changed=np.any(out!=a,axis=2)
assert not (changed&~allowed).any()
assert np.array_equal(out[protected_tower],a[protected_tower])
assert (out[lower,:3]==np.array([76,82,90])).all()
assert set(np.unique(out[:,:,3]))=={255}
mask=np.zeros_like(out);mask[changed]=(255,80,160,255);Image.fromarray(mask).save(S/'04_change_mask_vs_02.png')
roofmask=np.zeros_like(out);roofmask[newroof]=(45,49,56,255);Image.fromarray(roofmask).save(S/'03_roof_native_mask.png')
result.resize((1920,200),Image.Resampling.NEAREST).save(Q/'entry_backdrop_03_2x.png')
compare=Image.new('RGBA',(960,200));compare.alpha_composite(old);compare.alpha_composite(result,(0,100));compare.resize((1920,400),Image.Resampling.NEAREST).save(Q/'backdrop_02_vs_03_2x.png')
result.crop((432,0,528,100)).resize((768,800),Image.Resampling.NEAREST).save(Q/'chapel_03_detail_8x.png')
grey=Image.open(R/'docs/reference/cemetery_entry_greybox.png').convert('RGBA').crop((0,0,960,540));grey.alpha_composite(result);grey.resize((1920,1080),Image.Resampling.NEAREST).save(Q/'backdrop_03_on_greybox_2x.png')
hashes=json.loads((Q/'backups/before_chapel_03/protected_hashes.json').read_text())
for rel,h in hashes.items():assert hashlib.sha256((B/rel).read_bytes()).hexdigest()==h
meta={'version':'03','tower_protected_source_pixels_xyxy':[466,0,499,64],'tower_protected_pixel_count':int(protected_tower.sum()),'tip_preserved':[480,3],'roof_edit_rois_xyxy':[[439,0,473,64],[490,0,523,64]],'roof_shape_integer_y_shift':-8,'left_roof_native_top_y_outside_to_inside':left,'right_roof_native_top_y_inside_to_outside':right,'lower_chapel_world_y_min':64,'lower_exact_rgb':[76,82,90],'lower_replaced_pixel_count':int(lower.sum()),'changed_pixels_vs_02':int(changed.sum()),'outside_allowed_changes':int((changed&~allowed).sum()),'protected_asset_hashes_unchanged':True,'note':'Only sampled generated side-roof silhouettes are used. Accepted02 tower/cross/core pixels are copied exactly; accepted backgrounds remain outside roof/body changes. No fog added.'}
(S/'05_assembly_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta,indent=2))
