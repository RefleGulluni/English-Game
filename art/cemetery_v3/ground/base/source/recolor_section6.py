from pathlib import Path
from PIL import Image
import numpy as np,json,zipfile
S=Path(__file__).resolve().parent;B=S.parent
original=[]
with zipfile.ZipFile(B/'qc/backups/before_section6_recolor/base_and_qc_before_recolor.zip') as z:
 for i in [1,2]:original.append(np.array(Image.open(z.open(f'ground_base_{i:02d}.png')).convert('RGBA')))
colors,counts=np.unique(np.concatenate([a[:,:,:3].reshape(-1,3) for a in original]),axis=0,return_counts=True)
mu=np.average(colors,axis=0,weights=counts);L=colors@np.array([.2126,.7152,.0722]);meanL=float(np.average(L,weights=counts))
new=[];roles=[]
for c,l in zip(colors,L):
 if int(c[2])-int(c[0])>=6 and int(c[1])-int(c[0])>=3:center=np.array([64.,70.,72.]);role='cool_wet_sheen'
 elif int(c[0])-int(c[1])>=2 and int(c[0])-int(c[2])>=5:center=np.array([77.,70.,57.]);role='warm_clay'
 else:center=np.array([70.,71.,60.]);role='packed_soil'
 chrom=c.astype(float)-l
 new.append(center+1.2*(l-meanL)+.8*chrom);roles.append(role)
new=np.array(new);offset=np.array([70.,70.,60.])-np.average(new,axis=0,weights=counts);new=np.rint(new+offset).astype(int)
# Keep the color replacement injective: no texture-color classes are merged.
used=set()
for i in range(len(new)):
 c=tuple(new[i])
 if c in used:
  variants=[new[i]+np.array(d) for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1),(1,1,0)]]
  new[i]=next(v for v in variants if tuple(v) not in used)
 used.add(tuple(new[i]))
new=new.clip(0,255).astype('uint8');outs=[]
for i,a in enumerate(original,1):
 rgb=a[:,:,:3];ids=np.argmin(((rgb[:,:,None,:].astype(int)-colors.astype(int)[None,None,:,:])**2).sum(3),axis=2)
 out=a.copy();out[:,:,:3]=new[ids];outs.append(out);Image.fromarray(out).save(B/f'ground_base_{i:02d}.png')
 assert len(np.unique(rgb.reshape(-1,3),axis=0))==len(np.unique(out[:,:,:3].reshape(-1,3),axis=0))
# Monotonic luminance relationship and greater, not flattened, overall variation.
newL=new@np.array([.2126,.7152,.0722]);oldstd=np.sqrt(np.average((L-meanL)**2,weights=counts));newmean=float(np.average(newL,weights=counts));newstd=float(np.sqrt(np.average((newL-newmean)**2,weights=counts)))
assert newstd>oldstd
mapping=[{'from':c.tolist(),'to':n.tolist(),'material':r,'pixel_count':int(k)} for c,n,r,k in zip(colors,new,roles,counts)]
meta={'mapping':mapping,'old_weighted_mean_rgb':mu.tolist(),'new_weighted_mean_rgb':np.average(new,axis=0,weights=counts).tolist(),'old_luminance_std':float(oldstd),'new_luminance_std':newstd,'color_count':len(new),'injective':len(set(map(tuple,new)))==len(colors),'method':'Material-role hue ramps plus1.2x luminance difference; pixel-weighted mean calibrated to70,70,60. Exact39-to39 color lookup, no geometry/texture edits.'}
(S/'10_section6_color_mapping.json').write_text(json.dumps(meta,indent=2)+'\n');print({k:v for k,v in meta.items() if k!='mapping'})
