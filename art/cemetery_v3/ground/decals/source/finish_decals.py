"""Postprocess generated, observed-grid artwork. No drawing or image scaling.

One source cell is one native pixel. Operations: key, remove <=2px islands,
material palette replacement, integer leaf arrangement, transparent padding.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import json, zipfile, datetime

S=Path(__file__).resolve().parent; D=S.parent; B=D.parent/'base'
SPECS={
 'decal_puddle_01':('puddle_native30','puddle'),
 'decal_puddle_02':('decal_puddle_01','puddle'),
 'decal_wet_mud_01':('mud_native50','mud'),
 'decal_wet_mud_02':('decal_wet_mud_02','mud'),
 'decal_moss_01':('moss_small','moss'),
 'decal_moss_02':('decal_moss_01','moss'),
 'decal_dead_grass_01':('grass_small','grass'),
 'decal_dead_grass_02':('grass_medium','grass'),
 'decal_leaves_01':('decal_leaves_01','leaves'),
 'decal_loose_slab_01':('decal_loose_slab_01','slab'),
}

def components(mask):
 seen=np.zeros(mask.shape,bool); out=[];h,w=mask.shape
 for y,x in zip(*np.where(mask)):
  if seen[y,x]:continue
  stack=[(y,x)];seen[y,x]=1;pts=[]
  while stack:
   yy,xx=stack.pop();pts.append((yy,xx))
   for ny in range(max(0,yy-1),min(h,yy+2)):
    for nx in range(max(0,xx-1),min(w,xx+2)):
     if mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=1;stack.append((ny,nx))
  out.append(pts)
 return sorted(out,key=len,reverse=True)

def crop(a):
 im=Image.fromarray(a.astype('uint8'),'RGBA');return im.crop(im.getbbox())

def finish(name,src,kind):
 a=np.array(Image.open(S/f'{src}_restored_cells.png').convert('RGBA'))
 rgb=a[:,:,:3].astype(float);r,g,b=np.moveaxis(rgb,2,0)
 mask=~((r>g+45)&(b>g+40))
 # Center sampling still encounters a few contaminated border cells.
 mask &= ~((r>g+25)&(b>g+25)&(b>r*.65))
 removed=0
 for pts in components(mask):
  if len(pts)<=2:
   for y,x in pts:mask[y,x]=False;removed+=1
 a[:,:,3]=mask*255;a[~mask]=0
 valid=rgb[mask];L=rgb@np.array([.2126,.7152,.0722]);mid=float(np.median(L[mask]))
 earth=(r>b+7)&(r>=g-2)
 basepal=np.unique(np.array(Image.open(B/'ground_base_01.png').convert('RGB')).reshape(-1,3),axis=0)
 out=rgb.copy(); soil=np.zeros(mask.shape,bool)
 def ramp(center,scale,centerL=mid):return np.asarray(center)+scale*(L-centerL)[:,:,None]
 if kind=='puddle':
  water=(b>=r+3)&(g>=r); wm=float(np.median(L[mask&water]));out=ramp([51,60,64],.70,wm)
  soil=~water
 elif kind=='moss':
  green=(g>r+3)&(g>b+6);gm=float(np.median(L[mask&green]));out=ramp([61,70,49],.55,gm);soil=~green
 elif kind=='mud':
  out=ramp([59,61,51],.40)
  out[:,:,0]+=(r-g)*.08;out[:,:,2]+=(b-g)*.05
 elif kind=='grass':
  straw=(r>g+4)&(g>b+8);sm=float(np.median(L[mask&straw]));out=ramp([91,86,63],.45,sm);soil=~straw
 elif kind=='leaves':
  out=ramp([89,77,53],.42);out[:,:,0]+=(r-g-20)*.08
 elif kind=='slab':
  stone=(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])<35)&(L>73)
  sm=float(np.median(L[mask&stone]));out=ramp([99,101,91],.60,sm);soil=~stone
 if soil.any():
  ids=mask&soil
  em=float(np.median(L[ids]));target=np.array([70,70,60])+.22*(L[ids]-em)[:,None]
  nearest=np.argmin(((target[:,None,:]-basepal[None,:,:])**2).sum(2),axis=1)
  out[ids]=basepal[nearest]
 # Nearest palette reduction without dithering; geometry is unchanged.
 out=np.rint(out).clip(0,255).astype('uint8')
 pixels=Image.fromarray(out[mask][None,:,:]);palim=pixels.quantize(colors=24,dither=Image.Dither.NONE)
 palette=np.unique(np.array(palim.convert('RGB')).reshape(-1,3),axis=0)
 idx=np.argmin(((out.astype(float)[:,:,None,:]-palette[None,None,:,:])**2).sum(3),axis=2)
 a[:,:,:3]=palette[idx];a[~mask]=0
 moves=[]
 if kind=='leaves':
  # Three source leaves, moved whole by integers into a small loose cluster.
  parts=components(mask);leafparts=[p for p in parts if len(p)>=12]
  leafparts.sort(key=lambda p:min(x for y,x in p))
  positions=[(1,2),(10,0),(17,5)];canvas=np.zeros((24,44,4),np.uint8)
  for pts,(tx,ty) in zip(leafparts,positions):
   x0=min(x for y,x in pts);y0=min(y for y,x in pts)
   for y,x in pts:canvas[ty+y-y0,tx+x-x0]=a[y,x]
   moves.append({'source_bbox':[x0,y0,max(x for y,x in pts)+1,max(y for y,x in pts)+1],'dest':[tx,ty]})
  a=canvas
 im=crop(a);native_bbox=list(im.size)
 padded=Image.new('RGBA',(im.width+4,im.height+4));padded.paste(im,(2,2))
 padded.save(D/f'{name}.png')
 # Exact generated cell colors -> material colors can be inspected separately.
 mapping=[]
 for c in np.unique(rgb[mask].astype('uint8'),axis=0):
  y,x=np.argwhere(mask&np.all(rgb==c,axis=2))[0]
  mapping.append({'from':c.tolist(),'to':out[y,x].tolist()})
 return {'file':f'{name}.png','source':f'{src}_generated.png','grid':f'{src}_grid.json',
  'restored':f'{src}_restored_cells.png','material':kind,'canvas':list(padded.size),
  'visible_bbox_size':native_bbox,'removed_isolated_pixels':removed,'leaf_integer_moves':moves,
  'colors':len(padded.convert('RGB').getcolors(100000)) if False else len(np.unique(np.array(padded)[:,:,:3][np.array(padded)[:,:,3]>0],axis=0)),
  'palette_before_reduction':mapping}

if __name__=='__main__':
 existing=list(D.glob('decal_*.png'))
 if existing:
  q=B/'qc/backups';q.mkdir(exist_ok=True)
  with zipfile.ZipFile(q/f'decals_before_finish_{datetime.datetime.now():%Y%m%d_%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
   for p in existing:z.write(p,p.name)
 rows=[finish(n,*v) for n,v in SPECS.items()]
 selected={v[0]+'_generated.png' for v in SPECS.values()}
 unused=[p.name for p in S.glob('*_generated.png') if p.name not in selected]
 (S/'delivery_manifest.json').write_text(json.dumps({'method':'Built-in image_gen, observed cell center samples, binary magenta key, material palette replacement, <=2px isolated cleanup, integer crop/pad only. No scaling, mirroring, rotation, noise, blur or drawn texture.','decals':rows,'unused_raw_sources':unused,'unused_reason':'Early variants had unsuitable native scale or excess soil mass. Retained only as production evidence, not game assets.'},indent=2,default=lambda v:int(v))+'\n')
 print([(r['file'],r['canvas'],r['visible_bbox_size'],r['colors']) for r in rows])
