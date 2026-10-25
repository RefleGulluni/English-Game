from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,colorsys,hashlib
W=Path('/tmp/english-game-props-complete-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');D=W/'restored';S=W/'staged';S.mkdir(exist_ok=True)
notes={};mapping={};stats={}
def palette_clean(im,n):
 a=np.array(im.convert('RGBA'));fg=a[:,:,3]>0
 bad=(a[:,:,0].astype(int)-a[:,:,1].astype(int)>28)&(a[:,:,2].astype(int)-a[:,:,1].astype(int)>28)
 a[bad]=0;fg=a[:,:,3]>0
 patch=Image.fromarray(a[fg,:3].reshape(1,-1,3));q=patch.quantize(44,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);p=np.array(q.getpalette(),dtype=np.uint8).reshape(-1,3);active=p[np.unique(np.array(q))]
 out=np.zeros_like(a)
 for y,x in zip(*np.where(fg)):
  c=a[y,x,:3].astype(int);out[y,x,:3]=active[((active.astype(int)-c)**2).sum(1).argmin()];out[y,x,3]=255
 # Remove tiny disconnected background debris, don't add any texture.
 seen=set();deleted=[]
 for yy,xx in zip(*np.where(out[:,:,3]>0)):
  if (yy,xx) in seen:continue
  stack=[(yy,xx)];seen.add((yy,xx));comp=[]
  while stack:
   y,x=stack.pop();comp.append((y,x))
   for dy,dx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
    ny,nx=y+dy,x+dx
    if 0<=ny<out.shape[0] and 0<=nx<out.shape[1] and out[ny,nx,3] and (ny,nx) not in seen:seen.add((ny,nx));stack.append((ny,nx))
  if len(comp)<=2:
   for y,x in comp:out[y,x]=0;deleted.append([int(x),int(y)])
 notes[n]={'quantized_colors':44,'no_dithering':True,'removed_magenta_cells':int(bad.sum()),'removed_tiny_islands':deleted}
 return out

def shorten(a,delta,cut):
 # Native geometry edit: remove one middle span, move far end by integer vector.
 # Never interpolate / scale pixels; all output colors and pixels originate in source.
 dx,dy=delta;v=np.array([dx,dy]);norm=float(v@v);out=np.zeros_like(a)
 # Mapping output coordinate to its source; cross-section lies between painted stones.
 for y in range(a.shape[0]):
  for x in range(a.shape[1]):
   if x*dx+y*dy<=cut:sx,sy=x,y
   else:sx,sy=x+dx,y+dy
   if 0<=sy<a.shape[0] and 0<=sx<a.shape[1]:out[y,x]=a[sy,sx]
 return out

def poly_mask(shape,pts):
 m=Image.new('L',(shape[1],shape[0]),0);ImageDraw.Draw(m).polygon(pts,fill=255);return np.array(m)>0

def darken_ground(a,n):
 out=a.copy();before=[];after=[];changed=0;lut={}
 for rgb in np.unique(a[a[:,:,3]>0,:3],axis=0):
  r,g,b=[int(z) for z in rgb];h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
  # Yellow/ochre/olive grass + warm soil only; gray stone chips retain their light.
  if 12<=h*360<=82 and s>.20:
   lum=.299*r+.587*g+.114*b;fac=.58 if lum>85 else .70
   nr,ng,nb=[round(c*fac) for c in [r,g,b]]
   avg=(nr+ng+nb)/3;nr=round(nr*.83+avg*.17);ng=round(ng*.83+avg*.17);nb=round(nb*.83+avg*.17)
   mask=np.all(a[:,:,:3]==rgb,axis=2)&(a[:,:,3]>0);out[mask,:3]=[nr,ng,nb];count=int(mask.sum());changed+=count;before.extend([lum]*count);after.extend([.299*nr+.587*ng+.114*nb]*count);lut['#%02X%02X%02X'%(r,g,b)]='#%02X%02X%02X'%(nr,ng,nb)
 notes.setdefault(n,{})['ground_darkening']={'changed_pixels':changed,'affected_mean_luma_before':float(np.mean(before)) if before else 0,'affected_mean_luma_after':float(np.mean(after)) if after else 0,'palette_map':lut}
 return out

for n in json.loads((W/'generation.json').read_text())['raw']:
 a=palette_clean(Image.open(D/(n+'.png')),n);h,w=a.shape[:2]
 if n=='open_grave_01':
  a=shorten(a,(12,7),1250);notes[n]['native_geometry_edit']={'removed_middle_span_vector':[12,7],'cut_projection':1250,'reason':'Shorten one central rim section by integer translation; pit long edge becomes human length without rescaling.'}
 elif n=='wall_pillar_01':
  a=np.concatenate((a[:43],a[63:]),axis=0);h=a.shape[0];notes[n]['native_geometry_edit']={'removed_native_rows':[43,63],'reason':'Remove one complete central stone course at the mortar joint, integer movement only, pillar higher than wall but below hero height.'}
 elif n=='grave_lid_01':
  a=shorten(a,(8,10),1040);notes[n]['native_geometry_edit']={'removed_middle_span_vector':[8,10],'cut_projection':1040,'reason':'Shorten slab middle by integer translation to match grave; no rotation or scaling.'}
 Image.fromarray(a).save(S/(n+'_combined_cells.png'))
 if n=='tombstone_upright_02':
  mask=poly_mask(a.shape,[(10,0),(57,0),(57,66),(53,72),(45,73),(20,69),(13,66),(10,60)]);canvas=(96,112)
 elif n=='tombstone_cross_01':
  mask=poly_mask(a.shape,[(0,0),(67,0),(67,79),(60,82),(60,90),(51,94),(20,93),(10,90),(10,82),(0,79)]);canvas=(96,128)
 elif n=='wall_pillar_01':
  mask=poly_mask(a.shape,[(0,0),(60,0),(60,61),(51,64),(51,74),(42,77),(13,75),(8,72),(8,64),(0,61)]);canvas=(96,128)
 elif n=='iron_fence_01':
  mask=np.indices((h,w))[0]<57
  for cx in [14,36,59,80,103,125]:mask[57:67,cx-2:cx+3]=True
  canvas=(160,104)
 elif n=='low_wall_01':
  mask=poly_mask(a.shape,[(0,0),(165,0),(165,43),(158,43),(158,53),(8,53),(8,43),(0,43)]);canvas=(192,96)
 elif n=='low_wall_broken_01':
  mask=poly_mask(a.shape,[(0,0),(148,0),(148,46),(141,46),(141,51),(8,53),(8,45),(0,45)]);canvas=(176,96)
 elif n=='grave_lid_01':
  mask=poly_mask(a.shape,[(2,11),(33,0),(41,0),(113,72),(114,87),(88,98),(7,34)]);canvas=(160,144)
 elif n=='open_grave_01':
  # The dark pit is always ground-layer. Outer low earth also ground-layer.
  rim=poly_mask(a.shape,[(8,27),(62,2),(184,65),(190,86),(128,114),(12,43)])
  hole=poly_mask(a.shape,[(34,26),(64,13),(161,65),(128,88)])
  mask=rim&~hole;canvas=(224,144)
 prop=a.copy();base=a.copy();prop[~mask]=0;base[mask]=0;base=darken_ground(base,n)
 # World prop color cleanup: eliminate residual magenta fringe; no generated new texels.
 for ar in [prop,base]:
  c=ar[:,:,:3].astype(int);bad=(c[:,:,0]-c[:,:,1]>28)&(c[:,:,2]-c[:,:,1]>28);ar[bad]=0
 # Whole source field fits with integer translation; canvas retains common bottom anchor.
 off=((canvas[0]-w)//2,canvas[1]-h-1);assert min(off)>=0,(n,a.shape,canvas)
 pi=Image.new('RGBA',canvas);bi=Image.new('RGBA',canvas);pi.alpha_composite(Image.fromarray(prop),off);bi.alpha_composite(Image.fromarray(base),off)
 pi.save(S/(n+'.png'));bi.save(S/(n+'_base.png'));mapping[n]={'canvas':canvas,'cell_field':[w,h],'integer_offset':off}
# Accepted first tombstone: body is byte-identical, darken ground only.
n='tombstone_upright_01';old=R/'art/cemetery_v3/props/qc/revision1_tombstone_trial'
pi=Image.open(old/(n+'.png')).convert('RGBA');base=darken_ground(np.array(Image.open(old/(n+'_base.png')).convert('RGBA')),n);pi.save(S/(n+'.png'));Image.fromarray(base).save(S/(n+'_base.png'));mapping[n]={'canvas':pi.size,'accepted_body_unchanged':True}
(W/'cleanup_notes.json').write_text(json.dumps(notes,indent=2));(W/'assembly_mapping.json').write_text(json.dumps(mapping,indent=2))
# Native/2x visual review, no asset scaling.
hero=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');sheet=Image.new('RGBA',(800,456),'#403D3F');dr=ImageDraw.Draw(sheet)
for k,n in enumerate(['tombstone_upright_01',*json.loads((W/'generation.json').read_text())['raw']]):
 x=(k%3)*264;y=k//3*152;sheet.alpha_composite(hero,(x-8,y+34))
 for suf in ['_base','']:
  im=Image.open(S/(n+suf+'.png'));sheet.alpha_composite(im,(x+152-im.width//2,y+132-im.height))
 dr.text((x+2,y+136),n,fill='white')
sheet.resize((1600,912),Image.Resampling.NEAREST).save(W/'staged_review_2x.png')
for n in mapping:
 im=Image.open(S/(n+'.png'));a=np.array(im);yy,xx=np.where(a[:,:,3]>0);print(n,im.size,'body_height',int(yy.max()-yy.min()+1))
