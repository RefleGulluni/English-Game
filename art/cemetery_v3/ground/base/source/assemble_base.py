from pathlib import Path
from PIL import Image,ImageDraw
from collections import Counter
import numpy as np,json
B=Path(__file__).resolve().parents[1];S=B/'source';Q=B/'qc'

def registered_cells(src,stem,w=224,h=128):
 im=Image.open(src).convert('RGB');a=np.array(im)
 xs=[round(i*im.width/w) for i in range(w+1)];ys=[round(i*im.height/h) for i in range(h+1)]
 xc=[(l+r-1)//2 for l,r in zip(xs,xs[1:])];yc=[(l+r-1)//2 for l,r in zip(ys,ys[1:])]
 cells=Image.fromarray(a[np.ix_(yc,xc)]);cells.save(S/f'{stem}_restored_cells.png')
 (S/f'{stem}_grid.json').write_text(json.dumps({'source_file':Path(src).name,'source_size':list(im.size),'native_size':[w,h],'x_boundaries':xs,'y_boundaries':ys,'x_centers':xc,'y_centers':yc,'method':'Registered edit preserves input224x128 logical layout; one center sample per visible source block, no image resize or averaging. Check grid overlay for local drift.'},indent=2)+'\n')
 grid=im.copy();dr=ImageDraw.Draw(grid)
 for x in xs[1:-1]:dr.line((x,0,x,im.height-1),fill=(225,70,160))
 for y in ys[1:-1]:dr.line((0,y,im.width-1,y),fill=(225,70,160))
 grid.save(S/f'{stem}_grid_overlay.png')
 return cells

def quiet(im,pal):
 a=np.array(im.convert('RGB')).astype(int);pal=np.asarray(pal,dtype=np.uint8)
 lab=np.argmin(((a[:,:,None,:]-pal.astype(int)[None,None,:,:])**2).sum(3),axis=2)
 for _ in range(2):
  counts=np.bincount(lab.reshape(-1),minlength=len(pal));seen=np.zeros(lab.shape,bool);out=lab.copy();H,W=lab.shape
  for y in range(H):
   for x in range(W):
    if seen[y,x]:continue
    c=int(lab[y,x]);stack=[(x,y)];seen[y,x]=1;comp=[];neigh=Counter()
    while stack:
     xx,yy=stack.pop();comp.append((xx,yy))
     for nx,ny in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
      if not(0<=nx<W and 0<=ny<H):continue
      nc=int(lab[ny,nx])
      if nc==c and not seen[ny,nx]:seen[ny,nx]=1;stack.append((nx,ny))
      elif nc!=c:neigh[nc]+=1
    if len(comp)>3:continue
    choices=[k for k in neigh if counts[k]>counts[c] and np.linalg.norm(pal[k].astype(int)-pal[c].astype(int))<=18]
    if not choices:continue
    k=max(choices,key=lambda k:(neigh[k],-np.linalg.norm(pal[k].astype(int)-pal[c].astype(int))))
    for xx,yy in comp:out[yy,xx]=k
  lab=out
 return pal[lab]

def cut_path(cost):
 # Minimum-error integer cut. Pixels on either side come from original artwork;
 # no blended colors or procedural texture are synthesized.
 H,W=cost.shape;dp=cost[0].copy();prev=np.zeros((H,W),int)
 for y in range(1,H):
  new=np.zeros(W)
  for x in range(W):
   options=range(max(0,x-1),min(W,x+2));best=min(options,key=lambda k:dp[k]+.05*abs(k-x))
   new[x]=cost[y,x]+dp[best]+.05*abs(best-x);prev[y,x]=best
  dp=new
 x=int(np.argmin(dp));path=[x]
 for y in range(H-1,0,-1):x=int(prev[y,x]);path.append(x)
 return np.array(path[::-1])

def fill(tiles,name,seed=1048):
 H,W=128,224;rng=np.random.default_rng(seed);ids=rng.integers(0,len(tiles),size=(5,5));canvas=np.zeros((640,1120,3),np.uint8)
 for y in range(5):
  for x in range(5):canvas[y*H:y*H+H,x*W:x*W+W]=tiles[ids[y,x]]
 Image.fromarray(canvas[:540,:960]).resize((1920,1080),Image.Resampling.NEAREST).save(Q/name)
 return ids.tolist()

if __name__=='__main__':
 pal=json.loads((S/'02_cleanup_metadata.json').read_text())['palette']
 edit=registered_cells(S/'04_seam_repair_generated.png','04')
 e=quiet(edit,pal);old=np.array(Image.open(S/'03_half_offset_native.png').convert('RGB'))
 err=((old.astype(float)-e.astype(float))**2).mean(2)
 l=cut_path(err[:,76:101])+76;r=cut_path(err[:,124:149])+124
 t=cut_path(err[32:57,:].T)+32;b=cut_path(err[72:97,:].T)+72
 yy,xx=np.indices((128,224));mask=((xx>=l[:,None])&(xx<=r[:,None]))|((yy>=t[None,:])&(yy<=b[None,:]))
 # Keep a narrow original wrap fringe; repair reaches close to the edge, not a
 # broad flat frame. Edge values retain source material grain, not one base color.
 mask[[0,-1],:]=False;mask[:,[0,-1]]=False
 out=old.copy();out[mask]=e[mask]
 # Identical opposing1px edge profiles, sampled from the existing soil. Four
 # corner points agree. This is not a uniform-color border.
 out[:,-1]=out[:,0];out[-1,:]=out[0,:];out[-1,-1]=out[0,0]
 Image.fromarray(out).convert('RGBA').save(B/'ground_base_01.png')
 Image.fromarray((mask*255).astype('uint8')).save(S/'05_repair_selection_mask.png')
 Image.fromarray(e).save(S/'04_repair_palette_matched.png')
 fill([out],'base_01_only_fill_2x.png')
 (S/'05_seam_assembly.json').write_text(json.dumps({'method':'AI center-seam edit; irregular minimum-error cross cuts choose existing pixels from source/edit.1px opposing textured edge profiles paired; no flat frame.','selected_edit_pixels':int(mask.sum()),'left_cut':l.tolist(),'right_cut':r.tolist(),'top_cut':t.tolist(),'bottom_cut':b.tolist(),'main_size':[224,128]},indent=2)+'\n')
 print('Main base written, colors',len(np.unique(out.reshape(-1,3),axis=0)))
