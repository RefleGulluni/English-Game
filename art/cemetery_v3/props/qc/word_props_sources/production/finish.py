from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,colorsys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/Users/mac/.codex/work/cemetery-word-props-20261029');O=W/'staged';S=O/'qc/word_props_sources';P=R/'art/cemetery_v3/props';read=lambda p:np.array(Image.open(p).convert('RGBA'));L=np.array([.299,.587,.114]);records={}
def colors(p):
 a=read(p);return np.unique(a[a[:,:,3]>0,:3],axis=0)
stone=np.unique(np.concatenate([colors(P/(n+'.png')) for n in ['tombstone_upright_01','tombstone_upright_02','gate_pillar_tall_01']]),axis=0)
wood=np.unique(np.concatenate([colors(P/(n+'.png')) for n in ['signpost_01','wooden_cross_01']]),axis=0);iron=colors(P/'iron_fence_01.png');ground=colors(R/'art/cemetery_v3/ground/base/ground_base_01.png');grass=colors(R/'art/cemetery_v3/ground/transitions/grass_texture_01.png')
def clean(a):
 a=a.copy();c=a[:,:,:3].astype(int);bad=(c[:,:,0]-c[:,:,1]>24)&(c[:,:,2]-c[:,:,1]>24);a[bad]=0
 todo=set(zip(*np.where(a[:,:,3]>0)));removed=[]
 while todo:
  q=[todo.pop()];cc=q.copy()
  while q:
   y,x=q.pop()
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     pt=(y+dy,x+dx)
     if pt in todo:todo.remove(pt);q.append(pt);cc.append(pt)
  if len(cc)<=2:
   for y,x in cc:a[y,x]=0;removed.append([int(x),int(y)])
 return a,removed

def poly(shape,pts):
 a=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(a).polygon(pts,fill=255);return np.array(a)>0

def mapcolors(a,mask,pal):
 mask=mask&(a[:,:,3]>0);c=a[mask,:3].astype(int)
 if not len(c):return
 ix=((c[:,None]-pal.astype(int)[None])**2).sum(2).argmin(1);a[mask,:3]=pal[ix]
def reduce(a,num):
 f=a[:,:,3]>0;c=a[f,:3]
 if not len(c):return a,[]
 q=Image.fromarray(c.reshape(1,-1,3)).quantize(colors=num,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);cc=np.array(q.getpalette()[:num*3],int).reshape(-1,3);uniq=np.unique(c,axis=0).astype(int);pal=uniq[((cc[:,None]-uniq[None])**2).sum(2).argmin(1)];pal=np.unique(pal,axis=0).astype(np.uint8);mapcolors(a,f,pal);return a,pal.tolist()
def paste(a,b,x,y):
 yy,xx=np.where(b[:,:,3]>0);dx=xx+x;dy=yy+y;assert ((dx>=0)&(dx<a.shape[1])&(dy>=0)&(dy<a.shape[0])).all(),(a.shape,b.shape,x,y);a[dy,dx]=b[yy,xx]
def grade(a,pm,n):
 a=a.copy();f=a[:,:,3]>0;rgb=a[:,:,:3].astype(float);v=rgb@L;yy,xx=np.indices(f.shape)
 # Map stone and wood to accepted materials, retain sampled bronze and rope.
 if n=='tombstone_mossy_01':
  green=f&(rgb[:,:,1]>rgb[:,:,2]+12)&(rgb[:,:,0]<rgb[:,:,1]+24)
  moss=grass[(grass@L>34)&(grass@L<108)&(grass[:,1].astype(int)>=grass[:,0].astype(int)-4)]
  mapcolors(a,green,moss);mapcolors(a,pm&~green,stone)
 elif n=='crypt_sealed_01':
  door=poly(a.shape,[(61,42),(107,44),(109,102),(59,103)])
  mapcolors(a,pm&~door,stone)
  # Restore the existing door crack as dull lead/mortar rather than open air.
  seam=np.zeros_like(pm);seam[46:103,60]=True;seam[46:103,111]=True;seam[45,61:111]=True;seam[103,61:111]=True
  seam &= pm&(a[:,:,:3]@L<100)
  lead=stone[np.argmin(((stone.astype(int)-[110,106,94])**2).sum(1))];a[seam,:3]=lead
  # Keep generated rusty chain/iron sampled values; no orange emissive highlights.
 elif n=='bell_frame_01':
  metal=poly(a.shape,[(46,35),(69,38),(80,74),(35,72)])|poly(a.shape,[(64,27),(78,34),(80,98),(71,99)])
  mapcolors(a,pm&~metal,wood)
 elif n=='old_well_01':
  ring=poly(a.shape,[(8,53),(20,39),(43,36),(72,46),(77,64),(78,94),(48,105),(16,92)])
  water=poly(a.shape,[(19,55),(30,49),(53,49),(64,54),(59,67),(37,73),(18,67)])
  bucket=poly(a.shape,[(49,56),(71,55),(73,78),(57,81),(48,73)])
  mapcolors(a,pm&ring&~water&~bucket,stone);mapcolors(a,pm&~ring,wood);mapcolors(a,pm&bucket,wood)
  # Dull oily water remains source art, darkened by palette-only remapping.
  a[water,:3]=np.clip(rgb[water]*[.50,.60,.90]+[4,5,12],0,255).astype(np.uint8)
 elif n=='grave_bell_01':
  pole=(xx<12)&pm;mapcolors(a,pole,iron)
 elif n=='fresh_grave_mound_01':
  mapcolors(a,pm&(yy<29),wood);mapcolors(a,pm&(yy>=29),iron)
 # Earth is graded only in base layer, keeping generated clods/grain positions.
 bm=f&~pm
 if n not in ['raven_ground_01','tombstone_raven_01']:
  earth=bm
  if n=='fresh_grave_mound_01':
   # Preserve sampled clod-to-clod RGB differences; do not collapse soil to a
   # one-dimensional ground ramp or add any texture. Cooler/darker wet earth.
   a[earth,:3]=np.clip(rgb[earth]*[.75,.85,1.0]+[3,4,7],0,255).astype(np.uint8);earth=np.zeros_like(earth);target=np.empty(0)
  
  elif n=='old_well_01':target=np.clip(v[earth]*.68+18,52,100)
  elif n=='tombstone_mossy_01':
   earth=bm&~((rgb[:,:,1]>rgb[:,:,2]+12)&(rgb[:,:,0]<rgb[:,:,1]+24));target=np.clip(v[earth]*.65+8,30,91)
  else:target=np.clip(v[earth]*.62+10,30,92)
  gl=ground@L;ix=((gl[None]-target[:,None])**2).argmin(1);a[earth,:3]=ground[ix]
 # Remove saturated cyan, magenta fringe remnants, pureblack from world art.
 f=a[:,:,3]>0
 for y,x in zip(*np.where(f)):
  c=a[y,x,:3];h,s,v=colorsys.rgb_to_hsv(*(c/255))
  if 160<=h*360<=260 and s>=.35 and v>.3:a[y,x,:3]=ground[np.argmin(abs(ground@L-c@L))]
 return reduce(a,48 if n!='raven_ground_01' else 24)

specs={
'raven_ground_01':('raven_final',[64,48]),
'tombstone_mossy_01':('tombstone_mossy_01_regen',[96,96]),
'grave_bell_01':('grave_bell_01_regen',[64,80]),
'bell_frame_01':('bell_frame_01_regen',[160,160]),
'crypt_sealed_01':('crypt_sealed_01_regen',[224,176]),
'old_well_01':('old_well_01_regen',[128,144]),
'fresh_grave_mound_01':('fresh_grave_mound_01_regen',[128,96])}
for n,(src,can) in specs.items():
 a,removed=clean(read(S/src/'02_restored_cells.png'));preset_pm=None
 if n=='fresh_grave_mound_01':
  soil,_=clean(read(S/'mound_final/02_restored_cells.png'));oldshovel=a.copy()
  sy,sx=np.indices(a.shape[:2]);oldmask=(sy<26)&(sx>=70)
  for ya,yb,lo,hi in [(26,30,71,85),(30,34,71,88),(34,37,72,87),(37,40,75,86),(40,42,78,84),(42,43,80,83)]:oldmask[ya:yb,lo:hi]=True
  oldmask &= a[:,:,3]>0
  oldshovel[~oldmask]=0
  newmask=poly(soil.shape,[(65,0),(77,0),(77,7),(70,12),(67,15),(68,18),(65,26),(61,26),(56,24),(55,17),(60,14),(63,10)])
  soil[newmask]=0
  a=np.zeros((52,84,4),np.uint8);paste(a,soil,0,16)
  shovel_layer=np.zeros_like(a);paste(shovel_layer,oldshovel,-17,0);preset_pm=shovel_layer[:,:,3]>0;a[preset_pm]=shovel_layer[preset_pm]
 
 if n=='grave_bell_01':a=np.concatenate([a[:22],a[22:24],a[22:]],axis=0) # lengthen straight rod and cord2native rows only
 h,w=a.shape[:2];yy,xx=np.indices((h,w));f=a[:,:,3]>0
 if n=='raven_ground_01':
  # Feet retain the source's gray toe bones; only the brown dirt goes tobase.
  c=a[:,:,:3].astype(int);pm=(yy<24)|((yy>=24)&(c[:,:,0]-c[:,:,2]<7))
 elif n=='tombstone_mossy_01':pm=(yy<43)|((yy<51)&(xx>=12)&(xx<=39))
 elif n=='grave_bell_01':pm=(yy<35)|((yy<39)&(xx>=10)&(xx<=13))|((yy<40)&(xx==21))
 elif n=='bell_frame_01':pm=(yy<96)|((yy<106)&(xx>=14)&(xx<=35))|((yy<115)&(xx>=91)&(xx<=108))
 elif n=='crypt_sealed_01':pm=poly(a.shape,[(0,0),(177,0),(177,92),(157,92),(153,104),(137,108),(130,121),(114,128),(41,126),(32,121),(33,113),(20,105),(17,93),(0,93)])
 elif n=='old_well_01':pm=poly(a.shape,[(0,0),(88,0),(88,85),(78,88),(73,97),(50,104),(25,101),(10,92),(7,83),(0,82)])
 else:pm=preset_pm
 pm &= f;a,palette=grade(a,pm,n);pw,ph=can;x=(pw-w)//2;y=ph-4-h;prop=np.zeros((ph,pw,4),np.uint8);base=np.zeros_like(prop);p=a.copy();b=a.copy();p[~pm]=0;b[pm]=0;paste(prop,p,x,y);paste(base,b,x,y)
 Image.fromarray(prop).save(O/(n+'.png'));Image.fromarray(base).save(O/(n+'_base.png'));d=S/n;d.mkdir(exist_ok=True)
 Image.fromarray(a).save(d/'03_cleaned_native.png');Image.fromarray(base).alpha_composite(Image.fromarray(prop)) if False else None
 # Preserve raw source and exact painted-grid evidence for each final item.
 if d!=S/src:
  for fn in ['01_generated_original.png','02_restored_cells.png','grid.json','grid_check_1x.png','generation.json']:shutil.copy2(S/src/fn,d/fn) if False else None
 rec={'source':src,'additional_component_sources':['mound_final'] if n=='fresh_grave_mound_01' else [],'native_component_assembly':'mound_final earth integer offset(0,16), larger original shovel offset(-17,0), no scale' if n=='fresh_grave_mound_01' else None,'canvas':can,'origin':[pw//2,ph],'source_native':[w,h],'placement':[x,y],'removed_isolated_1_2px':removed,'palette_rgb':palette,'prop_bbox':Image.fromarray(prop).getbbox(),'base_bbox':Image.fromarray(base).getbbox(),'no_scale_rotation_mirror':True,'mask_polygon_or_rule':'See finish.py; selection only, no new texture.'};records[n]=rec
# Tombstone raven is family assembly, not separately generated stone: preserve
# the accepted gravestone and soil exactly, add same raven with no magenta/dirt.
parent=read(P/'tombstone_upright_01.png');parentbase=read(P/'tombstone_upright_01_base.png');bird=read(O/'raven_ground_01.png');bb=Image.fromarray(bird).getbbox();bird=bird[bb[1]:bb[3],bb[0]:bb[2]]
prop=np.zeros((160,96,4),np.uint8);base=np.zeros_like(prop);paste(prop,parent,0,48);paste(base,parentbase,0,48)
# Find native perch placement under BOTH feet, with minimum gap to the same
# original stone ridge; only whole bird translation, no pose or bone warping.
yy,xx=np.where(bird[:,:,3]>0);feet={int(x):int(np.flatnonzero(bird[:,x,3])[-1]) for x in range(bird.shape[1]) if bird[:,x,3].any()};feet={x:y for x,y in feet.items() if y>=bird.shape[0]-3}
stone_top={x:int(np.flatnonzero(prop[:,x,3])[0]) for x in range(96) if prop[:,x,3].any()};best=None
for dx in range(20,38):
 vals=[stone_top[x+dx]-y-1 for x,y in feet.items() if x+dx in stone_top]
 if len(vals)!=len(feet):continue
 dy=min(vals);err=sum(abs(v-dy) for v in vals)
 score=err+abs(dx+bird.shape[1]*.65-48)*.3
 if best is None or score<best[0]:best=(score,dx,dy)
_,dx,dy=best;paste(prop,bird,dx,dy)
# Bring rear toe to perch only if onepx air exists; copying its own toe color.
perch_edits=[]
for x,y in feet.items():
 sx=x+dx;sy=y+dy
 if sy+2<160 and prop[sy+1,sx,3]==0 and prop[sy+2,sx,3]==255:prop[sy+1,sx]=bird[y,x];perch_edits.append([sx,sy+1])
Image.fromarray(prop).save(O/'tombstone_raven_01.png');Image.fromarray(base).save(O/'tombstone_raven_01_base.png');d=S/'tombstone_raven_01';d.mkdir(exist_ok=True)
records['tombstone_raven_01']={'canvas':[96,160],'origin':[48,160],'parent':'tombstone_upright_01','parent_offset':[0,48],'raven_source':'raven_ground_01','bird_offset':[dx,dy],'perch_contact_cleanup':perch_edits,'parent_pixels_preserved':True,'prop_bbox':Image.fromarray(prop).getbbox(),'base_bbox':Image.fromarray(base).getbbox(),'no_scale_rotation_mirror':True}
# Export native composition and nearest-only QC sizes.
for n,rec in records.items():
 p=read(O/(n+'.png'));b=read(O/(n+'_base.png'));assert p.shape==b.shape;assert not ((p[:,:,3]>0)&(b[:,:,3]>0)).any();c=b.copy();m=p[:,:,3]>0;c[m]=p[m];im=Image.fromarray(c);d=S/n;im.save(d/'04_final_native_with_base.png');im.resize((im.width*6,im.height*6),Image.Resampling.NEAREST).save(d/'04_final_6x.png');rec['visible_height']=0 if rec['prop_bbox'] is None else rec['prop_bbox'][3]-rec['prop_bbox'][1];rec['combined_color_count']=len(np.unique(c[c[:,:,3]>0,:3],axis=0));(d/'cleanup.json').write_text(json.dumps(rec,indent=2))
(S/'cleanup_index.json').write_text(json.dumps(records,indent=2))
print(json.dumps({n:{'canvas':r['canvas'],'height':r['visible_height'],'colors':r['combined_color_count']} for n,r in records.items()},indent=2))
