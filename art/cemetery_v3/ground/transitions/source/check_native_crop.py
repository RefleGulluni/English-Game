"""Exhaustive integer128x128 crop feasibility, without modifying native art."""
from pathlib import Path
from PIL import Image
import numpy as np,json
S=Path(__file__).resolve().parent;a=np.array(Image.open(S/'01_path_atlas_restored_cells.png').convert('RGB')).astype(int);r,g,b=np.moveaxis(a,2,0);mask=~((r>g+45)&(b>g+40))
rows=json.loads((S/'layout_contract.json').read_text())['tiles'];expected=np.array([[r[k]=='P' for k in ['tl','tr','bl','br']] for r in rows]);best=None
for cy in range(mask.shape[0]-127):
 for cx in range(mask.shape[1]-127):
  m=mask[cy:cy+128,cx:cx+128]
  samples=np.array([[m[r['y']*32+dy,r['x']*32+dx] for dx,dy in [(1,1),(30,1),(1,30),(30,30)]] for r in rows])
  bad=int((samples!=expected).sum());errors=[]
  for row in rows:
   x=row['x']*32;y=row['y']*32;t=m[y:y+32,x:x+32]
   sides=[(t[0],row['tl']+row['tr']),(t[-1],row['bl']+row['br']),(t[:,0],row['tl']+row['bl']),(t[:,-1],row['tr']+row['br'])]
   for edge,code in sides:
    if code[0]==code[1]:continue
    # Measurement only: three-sample majority excludes a lone gravel speck.
    smooth=np.convolve(np.pad(edge.astype(float),(1,1),mode='edge'),np.ones(3)/3,mode='valid')>.5
    changes=np.where(smooth[:-1]!=smooth[1:])[0]+1
    proper=[int(z) for z in changes if bool(smooth[z-1])==(code[0]=='P') and bool(smooth[z])==(code[1]=='P')]
    errors.append(min([abs(z-16) for z in proper],default=32))
  score=(bad,sum(d>4 for d in errors),sum(errors))
  if best is None or score<best['score']:best={'crop':[cx,cy,cx+128,cy+128],'score':score,'bad_corner_samples':bad,'transition_edges_outside_tolerance':sum(d>4 for d in errors),'transition_edge_count':len(errors),'worst_midpoint_error':max(errors),'midpoint_errors':errors}
print(json.dumps(best,indent=2))
