from pathlib import Path
from PIL import Image
import numpy as np
from collections import deque

def components(a):
 todo=set(zip(*np.where(a[:,:,3]>0)));cs=[]
 while todo:
  p=todo.pop();q=[p];c=[p]
  while q:
   y,x=q.pop()
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     n=(y+dy,x+dx)
     if n in todo:todo.remove(n);q.append(n);c.append(n)
  cs.append(c)
 return sorted(cs,key=len,reverse=True)
if __name__=='__main__':
 s=Path('/tmp/english-game-skeleton-other3-20261027/staged')
 for d in ['left','front','back']:
  print(d)
  for k,p in enumerate(sorted((s/'frames'/f'skeleton_B_walk_{d}_v5').glob('*.png'))):
   a=np.array(Image.open(p));cs=components(a);print(k+1,[(len(c),min(x for y,x in c),min(y for y,x in c)) for c in cs])
