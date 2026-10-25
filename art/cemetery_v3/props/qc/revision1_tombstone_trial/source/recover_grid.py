from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np,json
W=Path('/tmp/english-game-props-revision1-20261025');src=Path('/Users/mac/.codex/generated_images/01a16768-6cb4-7a02-aee2-ae3ac8b12896/exec-e1248d8c-808a-4ef8-b7ba-71a090a52e49.png')
a=np.array(Image.open(src).convert('RGB'));f=a.astype(float);fg=~((a[:,:,0]>180)&(a[:,:,2]>180)&(a[:,:,1]<100))
def signal(axis):
 d=np.abs(np.diff(f,axis=axis)).mean(2)
 m=fg[:,1:]&fg[:,:-1] if axis==1 else fg[1:]&fg[:-1]
 # only central rock, not silhouette or ground edge
 if axis==1:m[:180]=False;m[1020:]=False
 else:m[:,:320]=False;m[:,920:]=False
 return (d*m).sum(0 if axis==1 else 1)/np.maximum(m.sum(0 if axis==1 else 1),1)
def fit(z,lo,hi):
 # Boundary at image coordinate b separates pixels b-1 and b. Dynamic path follows
 # strongest repeated real painted-cell edges, one boundary per 10..14px cell.
 z=(z-np.median(z))/(np.std(z)+1e-6);N=len(z)+1
 score=np.full(N,-1e12);prev=np.full(N,-1,dtype=int)
 for j in range(lo,lo+14):score[j]=z[j-1]*1.4
 for j in range(lo+14,hi):
  best=-1e12
  for length in range(10,15):
   k=j-length
   if k<lo:continue
   s=score[k]+z[j-1]*1.4-0.30*(length-12)**2
   if s>best:best=s;prev[j]=k
  score[j]=max(score[j],best)
 end=max(range(hi-14,hi),key=lambda j:score[j]);bs=[]
 while end>=lo:bs.append(int(end));end=prev[end]
 return sorted(bs)
xs=fit(signal(1),156,1098);ys=fit(signal(0),96,1224)
# Every detected source cell maps to exactly ONE native pixel. No resize call,
# no interpolation, and no global scale ratio. Representative pixel is center.
out=np.zeros((len(ys)-1,len(xs)-1,4),dtype=np.uint8)
for y in range(len(ys)-1):
 for x in range(len(xs)-1):
  xx=(xs[x]+xs[x+1])//2;yy=(ys[y]+ys[y+1])//2;rgb=a[yy,xx]
  if rgb[0]>180 and rgb[2]>180 and rgb[1]<100:continue
  out[y,x,:3]=rgb;out[y,x,3]=255
Image.fromarray(out).save(W/'recovered_cells_unquantized.png')
# Geometric guide only: source grid boundaries over a source crop at original scale.
guide=Image.fromarray(a).copy();d=ImageDraw.Draw(guide)
for x in xs:d.line([(x,96),(x,1224)],fill='#00ffff')
for y in ys:d.line([(156,y),(1098,y)],fill='#00ffff')
guide.crop((300,248,600,548)).save(W/'source_grid_check.png')
(W/'grid_recovery.json').write_text(json.dumps({'source':str(src),'source_size':[a.shape[1],a.shape[0]],'x_boundaries':xs,'y_boundaries':ys,'restored_size':[len(xs)-1,len(ys)-1],'cell_widths':dict(zip(*[v.tolist() for v in np.unique(np.diff(xs),return_counts=True)])),'cell_heights':dict(zip(*[v.tolist() for v in np.unique(np.diff(ys),return_counts=True)])),'mapping':'One painted source cell to one native pixel. Source-cell center nearest selection only; no image resize / rescale.','uncertainty':'Generator painted cells are not a perfect constant-width lattice. Boundary reconstruction inferred from repeated strong edges; source crop overlay supplied for visual audit.'},indent=2))
print('native grid',out.shape,'xwidth',np.unique(np.diff(xs),return_counts=True),'yheight',np.unique(np.diff(ys),return_counts=True))
Image.fromarray(out).resize((out.shape[1]*6,out.shape[0]*6),Image.Resampling.NEAREST).save(W/'recovered_review_6x.png')
