from pathlib import Path
from PIL import Image
import numpy as np,json
T=Path(__file__).resolve().parents[1];S=T/'source';Q=T/'qc'
PAL=[(28,32,32),(33,38,37),(38,43,42),(43,48,46),(48,53,50),(54,58,54),(59,62,56),(46,47,40),(55,53,43),(64,59,47),
(39,43,42),(51,56,54),(63,68,65),(72,77,72),(82,86,78),(93,96,86),(105,106,93),(58,61,51),
(30,36,40),(36,43,48),(43,51,57),(51,59,65),(61,68,73),(69,75,78),(77,82,83),
(52,49,39),(66,60,44),(79,71,51),(93,82,59),(106,94,70),(60,57,47)]
(S/'shared_palette.json').write_text(json.dumps({'colors':PAL,'groups':{'mud':[0,10],'stone':[10,18],'water':[18,25],'grass_leaves':[25,31]},'no_dither':True},indent=2)+'\n')
pal=np.array(PAL,dtype=np.uint8);a=np.array(Image.open(S/'mud_restored_cells.png').convert('RGB')).astype(int)
label=np.argmin(((a[:,:,None,:]-pal[:10].astype(int)[None,None,:,:])**2).sum(3),axis=2)
# Calm dark fissures and brightest clods by merging to existing nearby mud tones.
label[label<2]=2;label[(label==6)]=5
clean=pal[label]
Image.fromarray(clean).save(S/'mud_cleaned_native.png')
candidates=[]
for y in range(4,a.shape[0]-35,8):
 for x in range(4,a.shape[1]-35,8):
  patch=clean[y:y+32,x:x+32];gray=patch.mean(2)
  warm=(label[y:y+32,x:x+32]>=8).sum()
  candidates.append((float(gray.std()),x,y,int(warm),float(gray.mean())))
candidates.sort();chosen=[]
# 4 quiet, 4 gently varied patches, with similar mean value and no overlap.
for group in [0,1]:
 pool=candidates if group==0 else sorted(candidates,key=lambda z:abs(z[0]-4.8))
 for std,x,y,warm,mean in pool:
  if not (44<mean<53) or warm>60:continue
  if any(abs(x-u[1])<32 and abs(y-u[2])<32 for u in chosen):continue
  chosen.append((std,x,y,warm,mean))
  if len(chosen)==(4 if group==0 else 8):break
assert len(chosen)==8
# One-pixel compatible edge profiles sampled from the same source material.
_,ex,ey,_,_=chosen[0]
h=clean[ey+15,ex:ex+32].copy();v=clean[ey:ey+32,ex+15].copy()
# Restrict edge relief to neighboring existing mud tones, rather than uniform frame.
for edge in [h,v]:
 ids=np.argmin(((edge[:,None,:].astype(int)-pal[2:5].astype(int)[None,:,:])**2).sum(2),axis=1)+2
 edge[:]=pal[ids];edge[0]=pal[3];edge[-1]=pal[3]
tiles=[];meta=[]
for i,(std,x,y,warm,mean) in enumerate(chosen):
 p=clean[y:y+32,x:x+32].copy()
 p[0]=h;p[-1]=h;p[:,0]=v;p[:,-1]=v
 im=Image.fromarray(p).convert('RGBA');im.save(T/f'ground_mud_{i+1:02d}.png');tiles.append(p)
 change=(p[:,:-1]!=p[:,1:]).any(2).mean()*100
 meta.append({'id':i+1,'source_crop':[x,y,x+32,y+32],'role':'quiet' if i<4 else 'subtle_feature','source_std':std,'tile_mean':float(p.mean()),'horizontal_change_percent':round(float(change),2)})
for a1 in tiles:
 for a2 in tiles:
  assert np.array_equal(a1[:,-1],a2[:,0]);assert np.array_equal(a1[-1],a2[0])
rng=np.random.default_rng(1043);ids=rng.choice(8,size=(17,30),p=[.175]*4+[.075]*4)
canvas=np.zeros((544,960,3),np.uint8)
for yy in range(17):
 for xx in range(30):canvas[yy*32:yy*32+32,xx*32:xx*32+32]=tiles[ids[yy,xx]]
Image.fromarray(canvas[:540]).resize((1920,1080),Image.Resampling.NEAREST).save(Q/'tiles_random_fill_2x.png')
atlas=Image.new('RGBA',(128,64))
for i,p in enumerate(tiles):atlas.alpha_composite(Image.fromarray(p).convert('RGBA'),((i%4)*32,(i//4)*32))
atlas.resize((1024,512),Image.Resampling.NEAREST).save(Q/'mud_tiles_8x.png')
(S/'mud_build_metadata.json').write_text(json.dumps({'tiles':meta,'horizontal_edge':h.tolist(),'vertical_edge':v.tolist(),'all64_ordered_mud_pairs_both_axes_exact':True,'random_seed':1043,'random_ids':ids.tolist(),'weights':[.175]*4+[.075]*4},indent=2)+'\n')
print(meta)
