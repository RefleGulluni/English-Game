"""Center-sample observed cell intervals; never resize generated art.
Only QC previews use integer nearest-neighbor enlargement.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]

def restore(path,prefix):
 im=Image.open(path).convert('RGB'); a=np.asarray(im,dtype=np.float64)
 boundaries=[]; traces=[]
 for axis in [1,0]:
  d=np.abs(np.diff(a,axis=axis)).mean(axis=(0,2) if axis==1 else (1,2))
  cand=[i for i in range(1,len(d)-1) if d[i]>=d[i-1] and d[i]>d[i+1]]
  peaks=[]
  for i in sorted(cand,key=lambda i:-d[i]):
   if all(abs(i-j)>=6 for j in peaks): peaks.append(i)
  peaks.sort()
  fills=[]
  for l,r in zip(peaks,peaks[1:]):
   if r-l>9:
    mid=max(range(l+5,r-4),key=lambda i:d[i]);fills.append(mid)
  edges=[0]+[i+1 for i in sorted(peaks+fills)]+[im.width if axis==1 else im.height]
  boundaries.append(edges);traces.append({'inserted_weak_boundary_peaks':fills})
 xs,ys=boundaries
 xc=[(l+r-1)//2 for l,r in zip(xs,xs[1:])];yc=[(l+r-1)//2 for l,r in zip(ys,ys[1:])]
 raw=Image.fromarray(np.asarray(im)[np.ix_(yc,xc)])
 raw.save(ROOT/'source'/f'{prefix}_restored_cells.png')
 data={'source_size':list(im.size),'native_size':list(raw.size),'x_boundaries':xs,'y_boundaries':ys,'x_sample_centers':xc,'y_sample_centers':yc,'weak_boundaries':traces,'method':'Observed global axis color-change peaks, min distance 6; weak missing boundary selected within 5px margins. Each cell sampled at one integer center; no averaging/resizing. Global axes do not model local cell drift.'}
 (ROOT/'source'/f'{prefix}_grid.json').write_text(json.dumps(data,indent=2)+'\n')
 grid=im.copy();dr=ImageDraw.Draw(grid)
 for x in xs[1:-1]:dr.line((x,0,x,im.height-1),fill=(210,45,150))
 for y in ys[1:-1]:dr.line((0,y,im.width-1,y),fill=(210,45,150))
 grid.save(ROOT/'source'/f'{prefix}_grid_overlay.png')
 return raw,data

if __name__=='__main__':
 raw,data=restore(ROOT/'source/01_generated_original_NOT_ACCEPTED.png','03')
 raw.crop((5,2,245,137)).save(ROOT/'source/04_native_crop_240x135.png')
 raw.resize((raw.width*6,raw.height*6),Image.Resampling.NEAREST).save(ROOT/'qc/restored_before_cleanup_6x.png')
 print(raw.size,data['weak_boundaries'])
