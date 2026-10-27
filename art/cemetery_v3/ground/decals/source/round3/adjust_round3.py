"""Section8: numeric material recolor on existing native artwork only."""
from pathlib import Path
from PIL import Image
import numpy as np,json,zipfile,collections,colorsys,hashlib
S=Path(__file__).resolve().parent;D=S.parents[1];G=D.parent;R=G.parents[2];Q=D/'qc'
rows=json.loads((D/'source/round2/round2_manifest.json').read_text())['assets']
meta={r['file']:r for r in rows}
backup=Q/'backups/before_round3.zip'
basepal=np.unique(np.array(Image.open(G/'base/ground_base_01.png').convert('RGB')).reshape(-1,3),axis=0)
def groups(mask):
 seen=set();out=[]
 for y,x in zip(*np.where(mask)):
  if (y,x) in seen:continue
  work=[(int(y),int(x))];seen.add((y,x));pts=[]
  while work:
   yy,xx=work.pop();pts.append((yy,xx))
   for ny in range(max(0,yy-1),min(mask.shape[0],yy+2)):
    for nx in range(max(0,xx-1),min(mask.shape[1],xx+2)):
     if mask[ny,nx] and (ny,nx) not in seen:seen.add((ny,nx));work.append((ny,nx))
  out.append(pts)
 return sorted(out,key=len,reverse=True)
def mean(a,m):return a[:,:,:3][m].mean(0).tolist()
locked=json.loads((S/'accepted_fingerprints.json').read_text())
assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in locked.items())
results=[]
with zipfile.ZipFile(backup) as z:
 for name in [f'decal_puddle_{i:02d}.png' for i in [1,2,3]]+['decal_dead_flowers_01.png']:
  old=np.array(Image.open(z.open('decals/'+name)).convert('RGBA'));out=old.copy();valid=old[:,:,3]>0;info={'file':name}
  labels=np.zeros(valid.shape,np.uint8)
  if 'puddle' in name:
   row=meta[name];src=np.array(Image.open(D/'source/round2'/row['restored']).convert('RGB')).astype(float)
   x0,y0,x1,y1=row['source_cell_crop'];src=src[y0:y1,x0:x1];src=np.pad(src,((2,2),(2,2),(0,0)))
   r,g,b=np.moveaxis(src,2,0);L=src@np.array([.2126,.7152,.0722]);water=(b>=r-2)&(b>=g-7)&valid
   wm=float(np.median(L[water]));highlight=water&(L>max(wm+18,63))
   # Keep the source glint locations; enlarge singleton glints by one adjacent
   # existing water pixel so each tiny mark has2-6px as explicitly requested.
   selected=np.zeros_like(highlight)
   for component in groups(highlight)[:2]:
    for y,x in component[:6]:selected[y,x]=1
    if len(component)<2:
     y,x=component[0]
     for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
      yy,xx=y+dy,x+dx
      if 0<=yy<water.shape[0] and 0<=xx<water.shape[1] and water[yy,xx] and not selected[yy,xx]:selected[yy,xx]=1;break
   highlight=selected;surface=water&~highlight
   shift=np.clip(.45*(L-L[surface].mean()),-3,3);shift-=shift[surface].mean()
   target=np.rint(np.array([58,62,66])+shift[:,:,None]).clip(0,255).astype('uint8');out[:,:,:3][water]=target[water]
   mud=valid&~water;distance=np.full(valid.shape,1000,int);queue=collections.deque()
   for y,x in zip(*np.where(water)):distance[y,x]=0;queue.append((y,x))
   while queue:
    y,x=queue.popleft()
    for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
     if 0<=yy<valid.shape[0] and 0<=xx<valid.shape[1] and distance[yy,xx]>distance[y,x]+1:
      distance[yy,xx]=distance[y,x]+1;queue.append((yy,xx))
   rim=mud&(distance<=3);outer=mud&~rim
   variation=np.clip(.30*(L-np.median(L[mud])),-2,2)
   soil=np.rint(np.array([58,60,55])+variation[:,:,None]).clip(55,62).astype('uint8');out[:,:,:3][rim]=soil[rim]
   target=np.array([68,69,58])+np.clip(.20*(L-np.median(L[mud])),-3,3)[:,:,None]
   near=basepal[np.argmin(((target[:,:,None,:]-basepal[None,None,:,:])**2).sum(3),axis=2)];out[:,:,:3][outer]=near[outer]
   for component in groups(highlight):
    for i,(y,x) in enumerate(sorted(component,key=lambda p:(p[1],p[0]))):out[y,x,:3]=[103+(i%2)*2,108+(i%2)*2,115+(i%2)*2]
   labels[outer]=1;labels[rim]=2;labels[surface]=3;labels[highlight]=4
   glints=groups(highlight)
   assert 1<=len(glints)<=2 and all(2<=len(c)<=6 for c in glints)
   info.update({'water_mean_rgb':mean(out,surface),'wet_rim_mean_rgb':mean(out,rim),'wet_rim_distance_px':[1,3],'reflection_groups':[{'size':len(c),'pixels_xy':[[x,y] for y,x in c]} for c in glints],'reflection_rgb':np.unique(out[:,:,:3][highlight],axis=0).tolist(),'previous_water_mean_rgb':mean(old,surface)})
   assert np.max(np.abs(np.array(info['water_mean_rgb'])-[58,62,66]))<.51
  else:
   a=old[:,:,:3].astype(float);r,g,b=np.moveaxis(a,2,0);petal=valid&(r>=g+7)&(b>=g+2)
   L=a@np.array([.2126,.7152,.0722]);diff=.65*(L-np.median(L[petal]));color=np.rint(np.array([66,64,64])+diff[:,:,None]).clip(0,255).astype('uint8')
   out[:,:,:3][petal]=color[petal];labels[valid&~petal]=1;labels[petal]=2
   sat=lambda im:float(np.mean([colorsys.rgb_to_hsv(*(c/255))[1] for c in im[:,:,:3][petal]]))
   info.update({'petal_pixels':int(petal.sum()),'previous_petal_mean_rgb':mean(old,petal),'petal_mean_rgb':mean(out,petal),'previous_petal_mean_saturation':sat(old),'petal_mean_saturation':sat(out),'stems_byte_identical':bool(np.array_equal(old[valid&~petal],out[valid&~petal]))})
  assert np.array_equal(old[:,:,3],out[:,:,3]);out[~valid]=0
  Image.fromarray(out).save(D/name);Image.fromarray(out).save(S/name.replace('.png','_recolored_native.png'));Image.fromarray(labels).save(S/name.replace('.png','_material_labels.png'))
  info['alpha_and_dimensions_unchanged']=True;info['canvas']=[out.shape[1],out.shape[0]];info['sha256']=hashlib.sha256((D/name).read_bytes()).hexdigest();results.append(info)
assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in locked.items())
(S/'round3_color_report.json').write_text(json.dumps({'method':'Existing native pixels recolored to user-specified material RGB ranges; alpha/dimensions preserved. Reflection singleton marks extended by one existing water pixel only. No regeneration, resampling, blur or noise. Source material masks from saved round2 cells.','assets':results,'accepted16_and2_bases_byte_identical':True},indent=2)+'\n')
print(json.dumps(results,indent=2))
