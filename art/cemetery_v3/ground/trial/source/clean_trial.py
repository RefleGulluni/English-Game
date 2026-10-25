"""Palette consolidation and conservative mud-only small-fragment cleanup.
No generated texture, dithering, averaging, resizing, or synthesis.
"""
from PIL import Image,ImageDraw
from pathlib import Path
from collections import Counter,deque
import numpy as np,json
ROOT=Path(__file__).resolve().parents[1]

def clean(im,prefix,road_polygon=None,shared_palette=None):
 a=np.asarray(im.convert('RGB'));h,w=a.shape[:2]
 road=Image.new('1',(w,h));dr=ImageDraw.Draw(road)
 if road_polygon:dr.polygon(road_polygon,fill=1)
 road=np.asarray(road).astype(bool)
 # Preserve cool puddles/mineral chips and the bright elongated grass marks.
 af=a.astype(int);r,g,b=af[:,:,0],af[:,:,1],af[:,:,2]
 mineral=(r-g<12)&(g-b<18)&(r>65)
 water=(b>=r-4)&(b>=g-3)
 grass=(r>100)&(r-g>16)&(g-b>22)
 mud=~(road|mineral|water|grass)
 if shared_palette is None:
  # Discrete representative palette of stone/moss/grass/water, no dither.
  q=im.convert('RGB').quantize(colors=38,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
  palette=np.array(list(q.getdata())).reshape(-1,3)
  palette=np.unique(palette,axis=0)
  targets=np.array([(31,26,21),(39,32,25),(46,38,29),(53,43,32),(60,48,35),(67,53,38),(74,59,42),(82,65,45),(91,72,49),(101,80,53)])
  pixels=a.reshape(-1,3).astype(int)
  dirt=np.array([pixels[np.argmin(np.sum((pixels-c)**2,axis=1))] for c in targets],dtype=np.uint8)
  palette=np.unique(np.concatenate((palette,dirt)),axis=0)
 else:palette=np.asarray(shared_palette,dtype=np.uint8)
 def nearest(points,pal):
  flat=points.reshape(-1,3).astype(int)
  out=[]
  for part in np.array_split(flat,16):out.append(np.argmin(((part[:,None,:]-pal.astype(int)[None,:,:])**2).sum(2),axis=1))
  return np.concatenate(out).reshape(points.shape[:-1])
 labels=nearest(a,palette)
 dirt_ids=[i for i,c in enumerate(palette.astype(int)) if c[0]>c[1]+4 and c[1]>c[2]+5 and c[0]<105 and c[0]-c[2]>12]
 # Reduce dirt to a material ramp of ten representative existing colors.
 targets=np.array([(31,26,21),(39,32,25),(46,38,29),(53,43,32),(60,48,35),(67,53,38),(74,59,42),(82,65,45),(91,72,49),(101,80,53)])
 dirt_ids=sorted(set(dirt_ids[np.argmin(((palette[dirt_ids].astype(int)-c)**2).sum(1))] for c in targets))
 dirt_pal=palette[dirt_ids]
 dirt_near=np.array(dirt_ids)[nearest(a,dirt_pal)]
 labels[mud]=dirt_near[mud]
 original=labels.copy()
 # Only consolidate tiny similar-color dirt fragments into their existing neighboring region.
 for passno in range(2):
  seen=np.zeros((h,w),bool);replacement=labels.copy()
  for y in range(h):
   for x in range(w):
    if seen[y,x] or not mud[y,x]:continue
    col=int(labels[y,x]);queue=[(x,y)];seen[y,x]=1;component=[];neighbors=Counter()
    while queue:
     xx,yy=queue.pop();component.append((xx,yy))
     for nx,ny in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
      if not (0<=nx<w and 0<=ny<h and mud[ny,nx]):continue
      nc=int(labels[ny,nx])
      if nc==col and not seen[ny,nx]:seen[ny,nx]=1;queue.append((nx,ny))
      elif nc!=col:neighbors[nc]+=1
    if len(component)>3 or not neighbors:continue
    candidates=[c for c in neighbors if np.linalg.norm(palette[c].astype(int)-palette[col].astype(int))<=22]
    if not candidates:continue
    target=max(candidates,key=lambda c:(neighbors[c],-np.linalg.norm(palette[c].astype(int)-palette[col].astype(int))))
    for xx,yy in component:replacement[yy,xx]=target
  labels=replacement
 out=Image.fromarray(palette[labels].astype(np.uint8)).convert('RGBA')
 mask=Image.fromarray((mud*255).astype('uint8'));mask.save(ROOT/'source'/f'{prefix}_mud_cleanup_mask.png')
 def rate(arr,mask):
  valid=mask[:,:-1]&mask[:,1:]
  changed=np.any(arr[:,:-1]!=arr[:,1:],axis=2)
  return round(100*changed[valid].mean(),2) if valid.any() else None
 stats={'mud_before_percent':rate(a,mud),'mud_after_percent':rate(np.asarray(out)[:,:,:3],mud),'protected_path_after_percent':rate(np.asarray(out)[:,:,:3],road),'changed_by_fragment_merge':int((labels!=original).sum()),'palette':palette.tolist(),'road_polygon':road_polygon}
 return out,stats
if __name__=='__main__':
 im=Image.open(ROOT/'source/04_native_crop_240x135.png').convert('RGB')
 poly=[(0,104),(197,0),(239,0),(239,19),(30,134),(0,134)]
 out,stats=clean(im,'05',poly)
 out.save(ROOT/'ground_trial_01.png')
 (ROOT/'source/05_cleanup.json').write_text(json.dumps(stats,indent=2)+'\n')
 out.resize((1440,810),Image.Resampling.NEAREST).save(ROOT/'qc/ground_trial_cleaned_6x.png')
 print({k:v for k,v in stats.items() if k!='palette'})
