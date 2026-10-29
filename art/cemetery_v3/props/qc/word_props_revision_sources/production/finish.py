from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,colorsys,hashlib
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');P=R/'art/cemetery_v3/props';W=Path('/Users/mac/.codex/work/word-props-revision-20261029');O=W/'staged';S=O/'qc/word_props_revision_sources';L=np.array([.299,.587,.114]);read=lambda p:np.array(Image.open(p).convert('RGBA'))
def maskpoly(shape,pts):
 im=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
def palette(p):
 a=read(p);return np.unique(a[a[:,:,3]>0,:3],axis=0)
def clean(a,remove_small=True):
 a=a.copy();c=a[:,:,:3].astype(int);a[(c[:,:,0]-c[:,:,1]>24)&(c[:,:,2]-c[:,:,1]>24)]=0
 if remove_small:
  todo=set(zip(*np.where(a[:,:,3]>0)))
  while todo:
   q=[todo.pop()];group=q.copy()
   while q:
    y,x=q.pop()
    for dy in [-1,0,1]:
     for dx in [-1,0,1]:
      pt=(y+dy,x+dx)
      if pt in todo:todo.remove(pt);q.append(pt);group.append(pt)
   if len(group)<=2:
    for y,x in group:a[y,x]=0
 a[a[:,:,3]==0]=0;return a

def map_rgb(a,m,pal):
 m &=a[:,:,3]>0;c=a[m,:3].astype(int)
 if len(c):a[m,:3]=pal[((c[:,None]-pal.astype(int)[None])**2).sum(2).argmin(1)]
def reduce(a,num):
 a=a.copy();f=a[:,:,3]>0;rgb=a[f,:3];q=Image.fromarray(rgb.reshape(1,-1,3)).quantize(colors=num,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);cent=np.array(q.getpalette()[:num*3],int).reshape(-1,3);uniq=np.unique(rgb,axis=0).astype(int);pal=uniq[((cent[:,None]-uniq[None])**2).sum(2).argmin(1)];pal=np.unique(pal,axis=0).astype(np.uint8);map_rgb(a,f,pal);return a

def place(a,b,x,y):
 yy,xx=np.where(b[:,:,3]>0);assert ((xx+x>=0)&(xx+x<a.shape[1])&(yy+y>=0)&(yy+y<a.shape[0])).all();a[yy+y,xx+x]=b[yy,xx]
# New warm earth only: original shovel PNG bytes stay untouched.
a=clean(read(S/'mound2/02_restored_cells.png'),remove_small=False);f=a[:,:,3]>0;rgb=a[f,:3].astype(float);target=np.array([65.,50.,38.]);limit=np.array([91.,82.,68.]);rgb*=target/rgb.mean(0)
for _ in range(8):
 rgb=np.clip(rgb, [22,16,11],limit);rgb += target-rgb.mean(0)
rgb=np.clip(rgb,[22,16,11],limit);a[f,:3]=rgb.astype(np.uint8);a=reduce(a,40);base=np.zeros((96,128,4),np.uint8);x=(128-a.shape[1])//2;y=92-a.shape[0];place(base,a,x,y);Image.fromarray(base).save(O/'fresh_grave_mound_01_base.png')
shovel=read(P/'fresh_grave_mound_01.png');combined=base.copy();m=shovel[:,:,3]>0;combined[m]=shovel[m];Image.fromarray(combined).save(S/'fresh_grave_mound_final_native.png');Image.fromarray(combined).resize((768,576),Image.Resampling.NEAREST).save(S/'fresh_grave_mound_final_6x.png');cs=base[base[:,:,3]>0,:3];v=cs@L
records={'fresh_grave_mound_01':{'source':'mound2','native_mound_size':[a.shape[1],a.shape[0]],'placement':[x,y],'canvas':[128,96],'origin':[64,96],'mean_rgb':np.round(cs.mean(0),3).tolist(),'mean_luma':round(float(v.mean()),3),'luma_std':round(float(v.std()),3),'max_rgb':cs.max(0).tolist(),'max_luma':round(float(v.max()),3),'shovel_png_sha256':hashlib.sha256((P/'fresh_grave_mound_01.png').read_bytes()).hexdigest(),'shovel_changed':False}}
assert 60<=cs[:,0].mean()<=70 and 46<=cs[:,1].mean()<=54 and 34<=cs[:,2].mean()<=42;assert v.max()<=np.array([93,88,73])@L
if (S/'crypt2/02_restored_cells.png').exists():
 a=clean(read(S/'crypt2/02_restored_cells.png'));src='crypt2'
else:a=clean(read(S/'crypt/02_restored_cells.png'));src='crypt'
h,w=a.shape[:2];yy,xx=np.indices((h,w))
# Body/base selection is reviewed on the final native image; native facade,
# stairs and columns stay complete, only loose earth goes into base.
if src=='crypt':
 pm=(yy<162)|maskpoly(a.shape,[(27,157),(157,157),(154,174),(136,180),(119,190),(36,190),(30,181),(36,172)])
 door=[66,65,109,165] # temporary first generation, inspect before publishing
else:
 # Filled after inspecting the second source; the generator can change grid.
 pm=(yy<162)|maskpoly(a.shape,[(29,157),(188,157),(187,173),(158,177),(145,190),(41,190),(35,183),(39,174)]);door=[69,63,126,165]
pm &= a[:,:,3]>0;oldpal=np.unique(np.concatenate([palette(P/'crypt_sealed_01.png'),palette(P/'crypt_sealed_01_base.png')]),axis=0);map_rgb(a,a[:,:,3]>0,oldpal)
if src=='crypt2':
 # Existing door crack becomes a dull thin lead/mortar seal, not a bright rim.
 lead=oldpal[np.argmin(((oldpal.astype(int)-[111,105,88])**2).sum(1))]
 for sx in [63,134]:
  for sy in range(60,165):
   if a[sy,sx,3]>0 and a[sy,sx,:3]@L<100:a[sy,sx,:3]=lead
 for sx in range(64,135):
  if a[58,sx,3]>0 and a[58,sx,:3]@L<100:a[58,sx,:3]=lead
a=reduce(a,48)
prop=np.zeros((256,256,4),np.uint8);base=np.zeros_like(prop);ox=(256-w)//2;oy=252-h;p=a.copy();b=a.copy();p[~pm]=0;b[pm]=0;place(prop,p,ox,oy);place(base,b,ox,oy);Image.fromarray(prop).save(O/'crypt_sealed_01.png');Image.fromarray(base).save(O/'crypt_sealed_01_base.png');c=base.copy();m=prop[:,:,3]>0;c[m]=prop[m];Image.fromarray(c).save(S/'crypt_final_native.png');Image.fromarray(c).resize((1536,1536),Image.Resampling.NEAREST).save(S/'crypt_final_6x.png')
records['crypt_sealed_01']={'source':src,'native_size':[w,h],'placement':[ox,oy],'canvas':[256,256],'origin':[128,256],'door_source_bbox_exclusive':door,'door_canvas_bbox_exclusive':[door[0]+ox,door[1]+oy,door[2]+ox,door[3]+oy],'prop_bbox':Image.fromarray(prop).getbbox(),'base_bbox':Image.fromarray(base).getbbox(),'no_resize_rotation_mirror':True}
(S/'cleanup_index.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
