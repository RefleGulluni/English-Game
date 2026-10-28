from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,colorsys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-entry-step2-20261028');O=W/'staged';V=O/'qc/entry_step2_sources';P=R/'art/cemetery_v3/props';records={};load=lambda p:np.array(Image.open(p).convert('RGBA'))
def clean(a):
 a=a.copy();c=a[:,:,:3].astype(int);bad=(c[:,:,0]-c[:,:,1]>22)&(c[:,:,2]-c[:,:,1]>22);a[bad]=0
 # Remove only detached1-2px contamination, not meaningful connected bark/grain.
 todo=set(zip(*np.where(a[:,:,3]>0)))
 while todo:
  q=[todo.pop()];cc=q.copy()
  while q:
   y,x=q.pop()
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     pt=(y+dy,x+dx)
     if pt in todo:todo.remove(pt);q.append(pt);cc.append(pt)
  if len(cc)<=2:
   for y,x in cc:a[y,x]=0
 return a

def polygon(shape,points):
 im=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0

def native_map(a,fn):
 coords=[]
 for y,x in zip(*np.where(a[:,:,3]>0)):
  xy=fn(int(x),int(y))
  if xy is not None:coords.append((y,x,*xy))
 minx=min(t[2] for t in coords);miny=min(t[3] for t in coords);maxx=max(t[2] for t in coords);maxy=max(t[3] for t in coords);b=np.zeros((maxy-miny+1,maxx-minx+1,4),np.uint8)
 for sy,sx,x,y in coords:b[y-miny,x-minx]=a[sy,sx]
 return b,[minx,miny]

def remove_rows(a,rows):return a[[y for y in range(a.shape[0]) if y not in rows]].copy()

def paste(a,p,dx,dy):
 ys,xs=np.where(p[:,:,3]>0);xx=xs+dx;yy=ys+dy;assert ((xx>=0)&(xx<a.shape[1])&(yy>=0)&(yy<a.shape[0])).all(),('CLIP',dx,dy,p.shape,a.shape);a[yy,xx]=p[ys,xs]

def palette_of(path):
 a=load(path);return np.unique(a[a[:,:,3]>0,:3],axis=0)
iron=palette_of(P/'iron_fence_01.png');ground=palette_of(R/'art/cemetery_v3/ground/base/ground_base_01.png');lumvec=np.array([.299,.587,.114]);groundlum=ground@lumvec;grass=palette_of(R/'art/cemetery_v3/ground/transitions/grass_texture_01.png');grasslum=grass@lumvec

def recolor(a,pm,family):
 a=a.copy();fg=a[:,:,3]>0;orig=a[:,:,:3].astype(float)
 if family=='iron':
  ys,xs=np.where(fg);rgb=a[ys,xs,:3].astype(int);ix=((rgb[:,None]-iron.astype(int)[None])**2).sum(2).argmin(1);a[ys,xs,:3]=iron[ix]
 # Grade only restrained earth-toned base pixels, leaving pale wood/stone/iron/glass highlights.
 lum=orig@lumvec;earth=fg&~pm&(lum<125)&((orig[:,:,0]-orig[:,:,1])<28)&((orig[:,:,0]-orig[:,:,2])<55)
 ys,xs=np.where(earth);target=np.clip(lum[earth]*.65+15,28,93);ix=((groundlum[None]-target[:,None])**2).argmin(1);a[ys,xs,:3]=ground[ix]
 # Press the yellow dried grass at wooden grave/sign bases into the actual muted grass/moss ground ramp.
 if family=='wood':
  for y,x in zip(*np.where(fg&~pm)):
   h,s,v=colorsys.rgb_to_hsv(*(orig[y,x]/255))
   if 35<=h*360<=105 and s>.20:
    target=float(np.clip(lum[y,x]*.45+16,40,81));gi=int(np.argmin((grasslum-target)**2));a[y,x,:3]=grass[gi]
 # No saturated cyan in glass or material. Desaturate such sampled source colors before merge.
 for y,x in zip(*np.where(fg)):
  rgb=a[y,x,:3];h,s,v=colorsys.rgb_to_hsv(*(rgb/255))
  if 160<=h*360<=260 and s>=.35 and v>.3:
   grey=round(float(rgb@lumvec));a[y,x,:3]=[grey,grey,max(0,grey-7)]
 # Merge近似色 using a finite source-color palette, never dithering or synthesized texture.
 rgb=a[fg,:3];q=Image.fromarray(rgb.reshape(1,-1,3)).quantize(colors=48,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);cent=np.array(q.getpalette()[:144],int).reshape(-1,3);uniq=np.unique(rgb,axis=0).astype(int);pal=uniq[((cent[:,None]-uniq[None])**2).sum(2).argmin(1)];pal=np.unique(pal,axis=0).astype(np.uint8);ix=((rgb.astype(int)[:,None]-pal.astype(int)[None])**2).sum(2).argmin(1);a[fg,:3]=pal[ix];return a,pal.tolist(),int(earth.sum())

specs={
'iron_gate_leaf_open_01':{'canvas':[96,112],'family':'iron','anchor_x':12,'mode':'upright'},
'iron_gate_leaf_fallen_01':{'canvas':[96,80],'family':'iron','mode':'flat'},
'dead_tree_02':{'canvas':[224,224],'family':'bark','anchor_x':90,'mode':'upright'},
'dead_tree_03':{'canvas':[256,192],'family':'bark','anchor_x':79,'mode':'upright'},
'fallen_lamp_post_01':{'canvas':[128,80],'family':'iron','mode':'flat'},
'signpost_01':{'canvas':[96,80],'family':'wood','anchor_x':13,'mode':'upright'},
'wooden_cross_01':{'canvas':[80,80],'family':'wood','anchor_x':20,'mode':'upright'},
'wooden_cross_02':{'canvas':[80,80],'family':'wood','anchor_x':22,'mode':'upright'},
'fountain_dry_01':{'canvas':[224,224],'family':'stone','mode':'fountain'}
}
for n,spec in specs.items():
 rec={'name':n,'canvas':spec['canvas'],'origin':[spec['canvas'][0]//2,spec['canvas'][1]],'mode':spec['mode'],'family':spec['family'],'no_resize_rotation_mirror':True}
 if n=='fountain_dry_01':
  pool=clean(load(V/'fountain_pool/02_restored_cells.png'));angel=clean(load(V/'fountain_angel/02_restored_cells.png'));columns=list(range(75,119));pool=pool[:,[x for x in range(pool.shape[1]) if x not in columns]];poolrows=list(range(48,69))+list(range(94,100));pool=remove_rows(pool,poolrows);angelrows=[76,79,81,84,87,90,93,96,99,102,105,108,123,126,129,132,134,136];angel=remove_rows(angel,angelrows)
  w,h=spec['canvas'];can=np.zeros((h,w,4),np.uint8);pm=np.zeros((h,w),bool)
  # Use two different accepted official muddy-ground decals, not painted or procedural new ground.
  mud1=load(R/'art/cemetery_v3/ground/decals/decal_wet_mud_01.png');mud2=load(R/'art/cemetery_v3/ground/decals/decal_wet_mud_02.png');paste(can,mud2,45,184);paste(can,mud1,126,192)
  layer=np.zeros_like(can);poolxy=[(w-pool.shape[1])//2,216-pool.shape[0]];anglexy=[w//2-angel.shape[1]//2,poolxy[1]+45-angel.shape[0]];paste(layer,pool,*poolxy);paste(layer,angel,*anglexy);pm=layer[:,:,3]>0;can[pm]=layer[pm];can,pal,soilcount=recolor(can,pm,'stone');prop=np.zeros_like(can);base=np.zeros_like(can);prop[pm]=can[pm];base[~pm]=can[~pm]
  rec.update({'pool_source':'fountain_pool/02_restored_cells.png','angel_source':'fountain_angel/02_restored_cells.png','pool_removed_columns':columns,'pool_removed_rows':poolrows,'angel_removed_rows':angelrows,'pool_placement':poolxy,'angel_placement':anglexy,'basin_outer_native_width':pool.shape[1],'angel_plus_pedestal_native_height':angel.shape[0],'base_from_existing_decals':[['decal_wet_mud_02.png',45,184],['decal_wet_mud_01.png',126,192]],'source_composite':'Separate basin and statue; one-time native removal of straight masonry/floor/robe interiors, integer placement; no repeated stamped stones.'})
 else:
  a=clean(load(V/n/'02_restored_cells.png'));source_size=[a.shape[1],a.shape[0]];edits={}
  if n=='iron_gate_leaf_open_01':
   a,shift=native_map(a,lambda x,y:None if 44<=int(y+.4*x)<49 else (x,y-5) if int(y+.4*x)>=49 else (x,y));edits={'remove_diagonal_pipe_strip':'44 <= floor(y +0.4*x) <49; below strip shifts(0,-5)','post_angle_preserved':True,'hinge_axis_source_x':12,'frame_axis_projected_span_px':31,'estimated_unfolded_axis_span_px':round(31/(2**-.5),2)}
  elif n=='iron_gate_leaf_fallen_01':
   a,shift=native_map(a,lambda x,y:(x,y) if x+.32*y<44 else (x-46,y-9) if x+.32*y>=93 else None);edits={'remove_middle_panel_projection':[44,93],'projection':'x+0.32*y','far_piece_translation':[-46,-9],'one_leaf_after_trim':True}
  elif n=='fallen_lamp_post_01':
   a,shift=native_map(a,lambda x,y:(x,y) if x<34 else (x-18,y+5) if x>=52 else None);edits={'remove_plain_pole_span_x':[34,52],'head_piece_translation':[-18,5]}
  elif n=='signpost_01':
   rows=list(range(44,54));a=remove_rows(a,rows);edits={'remove_plain_stake_rows':rows}
  elif n=='wooden_cross_01':
   rows=[5,8,11]+list(range(34,50));a=remove_rows(a,rows);edits={'remove_plain_upright_rows':rows}
  hh,ww=a.shape[:2];yy,xx=np.indices((hh,ww))
  if spec['mode']=='flat':pm=np.zeros((hh,ww),bool)
  elif n=='iron_gate_leaf_open_01':pm=polygon(a.shape,[(0,0),(ww-1,0),(ww-1,73),(19,73),(18,78),(8,78),(8,73),(0,73)])
  elif n=='dead_tree_02':pm=polygon(a.shape,[(0,0),(ww-1,0),(ww-1,141),(117,141),(117,153),(104,168),(82,168),(68,158),(60,145),(0,145)])
  elif n=='dead_tree_03':pm=polygon(a.shape,[(0,0),(ww-1,0),(ww-1,128),(116,128),(104,140),(75,144),(60,134),(0,129)])
  elif n=='signpost_01':pm=(yy<43)|((yy<55)&(xx>=9)&(xx<21))
  elif n=='wooden_cross_01':pm=(yy<39)|((yy<45)&(xx>=15)&(xx<26))
  elif n=='wooden_cross_02':pm=(yy<41)|((yy<49)&(xx>=18)&(xx<31))
  pm &= a[:,:,3]>0;a,pal,soilcount=recolor(a,pm,spec['family']);w,h=spec['canvas'];ax=spec.get('anchor_x',ww//2);ox=w//2-ax;oy=h-4-hh;prop=np.zeros((h,w,4),np.uint8);base=np.zeros_like(prop);p=a.copy();b=a.copy();p[~pm]=0;b[pm]=0;paste(prop,p,ox,oy);paste(base,b,ox,oy);rec.update({'restored_native_size':source_size,'edited_native_size':[ww,hh],'native_edits':edits,'placement':[ox,oy]})
 rec.update({'palette_rgb':pal,'earth_pixels_remapped_to_official_ground':soilcount});Image.fromarray(prop).save(O/(n+'.png'));Image.fromarray(base).save(O/(n+'_base.png'));combined=base.copy();m=prop[:,:,3]>0;combined[m]=prop[m];assert not ((prop[:,:,3]>0)&(base[:,:,3]>0)).any();Image.fromarray(combined).save(V/n/'04_final_native_with_base.png');Image.fromarray(combined).resize((combined.shape[1]*6,combined.shape[0]*6),Image.Resampling.NEAREST).save(V/n/'04_final_6x.png');rec['prop_bbox']=Image.fromarray(prop).getbbox();rec['base_bbox']=Image.fromarray(base).getbbox();rec['prop_visible_height']=0 if rec['prop_bbox'] is None else rec['prop_bbox'][3]-rec['prop_bbox'][1];(V/n/'cleanup.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));records[n]=rec;print(n,'prop height',rec['prop_visible_height'],'bbox',rec['prop_bbox'],'base',rec['base_bbox'])
(V/'cleanup_index.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
