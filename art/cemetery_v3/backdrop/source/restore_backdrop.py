"""Observed-grid center sampling. Never image-resize source artwork.
The axis path follows strong source cell transitions with bounded 5-8-ish intervals;
blank magenta spans are interpolated as empty cells. JSON retains every boundary.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
ROOT=Path(__file__).resolve().parents[1]
SETTINGS={
 'skyline_a':(6.6,6.5),'skyline_b':(6.55,6.4),'skyline_c':(6.0,6.3),'skyline_d':(6.45,6.35),
 'chapel':(8.25,8.6),'branches_left':(6.05,5.98),'branches_right':(6.46,6.3)}

def axis_grid(a,axis,spacing):
 d=np.abs(np.diff(a.astype(float),axis=axis)).mean(axis=(0,2) if axis==1 else (1,2))
 n=a.shape[axis]
 # Normalize observed transition energy; no sampled color is averaged.
 scale=max(float(np.percentile(d,90)),.1)
 energy=np.zeros(n+1);energy[1:n]=np.minimum(d/scale,4)
 lo=int(np.floor(spacing-1.15));hi=int(np.ceil(spacing+1.15))
 best=np.full(n+1,-1e9);prev=np.zeros(n+1,int);best[0]=0
 for end in range(1,n+1):
  for step in range(lo,hi+1):
   start=end-step
   if start<0:continue
   score=best[start]+energy[end]-.65*(step-spacing)**2-.12
   if score>best[end]:best[end]=score;prev[end]=start
 # Permit a short final partial cell. Its edge is the physical source edge.
 ends=range(max(1,n-hi),n+1)
 end=max(ends,key=lambda e:best[e]-.18*(n-e))
 edges=[end]
 while end>0:
  end=int(prev[end]);edges.append(end)
 edges=sorted(set(edges+[n]))
 if edges[-1]-edges[-2]<max(2,spacing*.4):edges.pop(-2)
 return edges

def restore(name):
 im=Image.open(ROOT/'source'/f'{name}_generated.png').convert('RGB');a=np.array(im)
 sx,sy=SETTINGS[name];xs=axis_grid(a,1,sx);ys=axis_grid(a,0,sy)
 xc=[(l+r-1)//2 for l,r in zip(xs,xs[1:])];yc=[(l+r-1)//2 for l,r in zip(ys,ys[1:])]
 raw=Image.fromarray(a[np.ix_(yc,xc)])
 raw.save(ROOT/'source'/f'{name}_restored_cells.png')
 data={'source_size':list(im.size),'native_size':list(raw.size),'estimated_cell_pitch':[sx,sy],
 'x_boundaries':xs,'y_boundaries':ys,'x_centers':xc,'y_centers':yc,
 'method':'Transition-energy boundary path; each interval takes one integer center pixel. No averaging, resizing or interpolation of image colors. Empty magenta spans have inferred invisible grid. Some local grid drift remains.'}
 (ROOT/'source'/f'{name}_grid.json').write_text(json.dumps(data,indent=2)+'\n')
 grid=im.copy();dr=ImageDraw.Draw(grid)
 for x in xs[1:-1]:dr.line((x,0,x,im.height-1),fill=(40,215,190))
 for y in ys[1:-1]:dr.line((0,y,im.width-1,y),fill=(40,215,190))
 grid.save(ROOT/'source'/f'{name}_grid_overlay.png')
 # One grid detail in a meaningful source area.
 region={'chapel':(560,320,900,790),'branches_left':(100,470,500,850),'branches_right':(1080,220,1480,600)}.get(name,(0,440,460,780))
 grid.crop(region).resize(((region[2]-region[0])*2,(region[3]-region[1])*2),Image.Resampling.NEAREST).save(ROOT/'qc'/f'{name}_grid_detail_2x.png')
 print(name,im.size,raw.size)
 return raw
if __name__=='__main__':
 for name in SETTINGS:restore(name)
