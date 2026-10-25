from pathlib import Path
from PIL import Image
import numpy as np,json,itertools
W=Path('/tmp/english-game-ashlar02-20261025');O=Path('/Users/mac/Documents/GitHub.nosync/English-Game/art/cemetery_v3/props');p=W/'staged/low_wall_ashlar_02.png';a=np.array(Image.open(p).convert('RGBA'));b=np.array(Image.open(O/'low_wall_broken_01.png').convert('RGBA'));fixed={tuple(c) for c in b[:,21,:3][b[:,21,3]>0]};colors=[tuple(c) for c in np.unique(a[a[:,:,3]>0,:3],axis=0)];used=set(fixed);mapping={}
# Match accepted gray/olive stone luminance. Each existing palette color maps once;
# never add spatial pattern / dithering / texture to improve counts.
for rgb in sorted(colors,key=lambda c:sum(int(v) for v in c)):
 if rgb in fixed:mapping[rgb]=rgb;continue
 target=tuple(round(int(c)*.78) for c in rgb);candidates=[]
 for delta in itertools.product(range(-2,3),repeat=3):
  c=tuple(max(0,min(255,t+d)) for t,d in zip(target,delta))
  if c not in used:candidates.append((sum(d*d for d in delta),c))
 mapped=min(candidates)[1];mapping[rgb]=mapped;used.add(mapped)
out=a.copy()
for rgb,new in mapping.items():out[np.all(a[:,:,:3]==rgb,axis=2)&(a[:,:,3]>0),:3]=new
assert len(set(mapping.values()))==len(mapping);assert np.array_equal(out[:,24],b[:,21]);assert np.array_equal(out[:,263],b[:,21]);Image.fromarray(out).save(p)
# Update combined native display.
im=Image.open(W/'staged/low_wall_ashlar_02_base.png').convert('RGBA');im.alpha_composite(Image.fromarray(out));im.save(W/'cleaned_combined.png')
roi=out[40:88,30:258];fg=roi[:,:,3]>0;before=a[40:88,30:258][fg,:3]@np.array([.299,.587,.114]);after=roi[fg,:3]@np.array([.299,.587,.114]);(W/'material_palette_match.json').write_text(json.dumps({'method':'One-to-one palette calibration of non-interface generated stone shades, factor0.78. Fixed interface palette unchanged. No geometry/texture/dithering changes.','palette_map':{'#%02X%02X%02X'%k:'#%02X%02X%02X'%v for k,v in mapping.items()},'wall_face_roi':[30,40,258,88],'mean_luma_before':float(before.mean()),'mean_luma_after':float(after.mean()),'accepted_ashlar01_equivalent_roi_mean':90.29323752181502},indent=2));print('Material mean',before.mean(),'->',after.mean())
