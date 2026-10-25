from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
W=Path('/tmp/english-game-props-batch2-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';S=W/'staged';S.mkdir(exist_ok=True)
def arr(im):return np.array(im.convert('RGBA'))
def palette(n):
 a=arr(Image.open(O/(n+'.png')));return np.unique(a[a[:,:,3]>0,:3],axis=0).astype(int)
P=palette('tombstone_upright_01');B=palette('tombstone_upright_01_base');C=palette('tombstone_cross_01')
def clean(a,p=P):
 a=a.copy();bad=(a[:,:,0].astype(int)-a[:,:,1].astype(int)>28)&(a[:,:,2].astype(int)-a[:,:,1].astype(int)>28);a[bad]=0
 for y,x in zip(*np.where(a[:,:,3]>0)):
  c=a[y,x,:3].astype(int);a[y,x,:3]=p[((p-c)**2).sum(1).argmin()]
 a[a[:,:,3]==0]=0
 return a

def load(n):return arr(Image.open(W/'recovered'/n/'restored_native.png'))
def poly(a,pts):
 m=Image.new('L',(a.shape[1],a.shape[0]),0);ImageDraw.Draw(m).polygon(pts,fill=255);return np.array(m)>0

def stat(a):
 m=a[:,:,3]>0;q=m[:,:-1]&m[:,1:];v=np.any(a[:,:-1,:3]!=a[:,1:,:3],axis=2);yy,xx=np.where(m)
 return dict(colors=len(np.unique(a[m,:3],axis=0)),adjacent_change=round(100*float((v&q).sum())/max(1,int(q.sum())),6),bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],height=int(yy.max()-yy.min()+1),opaque=int(m.sum()))
records={}
def family_palette(a):
 rgb=a[a[:,:,3]>0,:3].astype(int);rgb=rgb[~((rgb[:,0]-rgb[:,1]>28)&(rgb[:,2]-rgb[:,1]>28))]
 union=np.unique(np.vstack([P,C,palette('tombstone_upright_02')]),axis=0)
 nearest=((rgb[:,None,:]-union[None,:,:])**2).sum(2).argmin(1);used,counts=np.unique(nearest,return_counts=True)
 return union[used[np.argsort(counts)[-50:]]]

def richer_old_palette(a):
 # Keep six additional EXISTING cross-stone colors where source material hue/detail needs them.
 # This reduces loss from merging; it neither adds pixels nor invents texture.
 rgb=a[a[:,:,3]>0,:3].astype(int);rgb=rgb[~((rgb[:,0]-rgb[:,1]>28)&(rgb[:,2]-rgb[:,1]>28))];u,ct=np.unique(rgb,axis=0,return_counts=True)
 pal=P.copy();candidates=np.array([c for c in C if not np.any(np.all(P==c,axis=1))])
 for _ in range(min(6,len(candidates))):
  dist=((u[:,None,:]-pal[None,:,:])**2).sum(2).min(1);ds=((u[:,None,:]-candidates[None,:,:])**2).sum(2);gains=((dist[:,None]-np.minimum(dist[:,None],ds))*ct[:,None]).sum(0);i=int(gains.argmax());pal=np.vstack([pal,candidates[i]]);candidates=np.delete(candidates,i,axis=0)
 return pal

def savepair(n,a,mask,canvas,foot=12,cut=None,source=None):
 # Each selection pixel goes to exactly one integer destination; no interpolation.
 pal=family_palette(a) if n=='tombstone_small_01' else richer_old_palette(a) if n=='obelisk_01' else P
 a=clean(a,pal);prop=a.copy();base=a.copy();prop[~mask]=0;base[mask]=0;base=clean(base,B)
 bbox=Image.fromarray(prop).getbbox();foot=max(foot,a.shape[0]-bbox[3]+2);dx=(canvas[0]-a.shape[1])//2;dy=canvas[1]-foot-bbox[3]
 pi=Image.new('RGBA',canvas);bi=Image.new('RGBA',canvas);pi.alpha_composite(Image.fromarray(prop),(dx,dy));bi.alpha_composite(Image.fromarray(base),(dx,dy));pi.save(S/(n+'.png'));bi.save(S/(n+'_base.png'))
 records[n]={'source':source or n,'canvas':canvas,'origin':[canvas[0]//2,canvas[1]],'offset':[dx,dy],'native_edit':cut,'prop':stat(arr(pi)),'base':stat(arr(bi))}

# Flat top has 71px of stone already; dirt is a separate layer.
a=load('tombstone_flat_01');m=poly(a,[(0,0),(86,0),(86,65),(71,65),(70,69),(58,71),(29,71),(18,68),(0,65)]);savepair('tombstone_flat_01',a,m,(112,112))
a=load('tombstone_pointed_01');a=np.concatenate([a[:63],a[71:]],axis=0);m=poly(a,[(0,0),(56,0),(56,76),(46,76),(45,84),(16,84),(11,81),(0,79)]);savepair('tombstone_pointed_01',a,m,(96,112),cut={'remove_native_rows':[63,71],'reason':'Shorten unlettered shaft by8px, preserve pointed crown and carved marks.'})
a=load('tombstone_small_01');a=np.concatenate([a[:29],a[34:]],axis=0);m=poly(a,[(0,0),(55,0),(55,34),(53,38),(5,38),(0,35)]);savepair('tombstone_small_01',a,m,(80,64),foot=12,cut={'remove_native_rows':[29,34],'reason':'Shorten one blank panel strip, no scaling.'})
a=load('obelisk_01');a=np.concatenate([a[:40],a[78:]],axis=0);m=poly(a,[(0,0),(83,0),(83,109),(68,109),(68,120),(16,120),(15,115),(0,115)]);savepair('obelisk_01',a,m,(112,160),foot=20,cut={'remove_native_rows':[40,78],'reason':'Remove38native shaft rows, retaining apex, long cracks, taper and all plinth courses.'})
a=load('grave_slab_01');m=poly(a,[(8,32),(116,0),(127,1),(148,27),(151,36),(44,61),(17,49)]);savepair('grave_slab_01',a,m,(192,112),foot=28)
a=load('rubble_pile_01');m=poly(a,[(0,0),(55,0),(55,12),(43,16),(9,16),(0,13)]);savepair('rubble_pile_01',a,m,(80,48),foot=14)
# Tiny objects: use the coarser regenerated true cells, not a resize of v1.
for n,raw,cut,canvas in [('grave_vase_01','grave_vase_01_v2',(9,16),(48,64)),('candles_01','candles_01_v2',None,(64,48)),('grave_lantern_01','grave_lantern_01_v2',(20,22),(48,64))]:
 a=load(raw)
 if cut:a=np.concatenate([a[:cut[0]],a[cut[1]:]],axis=0)
 a=clean(a)
 # All vase/lamp pixels are object; candle rock has a shallow ground facing edge.
 m=np.ones(a.shape[:2],bool)
 if n=='candles_01':m[-2:]=False
 # Reuse a distinct native mud-chip selection from approved bases as contact decal.
 bbox=Image.fromarray(a).getbbox();dx=(canvas[0]-a.shape[1])//2;dy=canvas[1]-12-bbox[3]
 pi=Image.new('RGBA',canvas);pi.alpha_composite(Image.fromarray(np.where(m[:,:,None],a,0).astype('uint8')),(dx,dy));bi=Image.new('RGBA',canvas)
 old=Image.open(O/('tombstone_cross_01_base.png' if n=='grave_lantern_01' else 'tombstone_upright_01_base.png')).convert('RGBA')
 boxes={'grave_vase_01':(32,96,62,105),'candles_01':(19,98,68,108),'grave_lantern_01':(31,113,63,123)};b=old.crop(boxes[n]);ba=arr(b);bw,bh=b.size;bm=poly(ba,[(0,bh//2),(3,2),(bw//3,1),(bw//2,0),(bw*2//3,2),(bw-5,1),(bw-1,bh//2),(bw-3,bh-2),(bw-7,bh-1),(bw//2,bh-2),(bw//3,bh-1),(4,bh-2)]);ba[~bm]=0;b=Image.fromarray(ba);bi.alpha_composite(b,((canvas[0]-b.width)//2,canvas[1]-(20 if n=='grave_lantern_01' else 16)));base=a.copy();base[m]=0;bi.alpha_composite(Image.fromarray(clean(base,B)),(dx,dy));pi.save(S/(n+'.png'));bi.save(S/(n+'_base.png'))
 records[n]={'source':raw,'canvas':canvas,'origin':[canvas[0]//2,canvas[1]],'offset':[dx,dy],'native_edit':{'remove_native_rows':cut,'contact_decal_from':'tombstone_cross_01_base.png' if n=='grave_lantern_01' else 'tombstone_upright_01_base.png','crop':boxes[n],'decal_offset':[(canvas[0]-b.width)//2,canvas[1]-(20 if n=='grave_lantern_01' else 16)]},'prop':stat(arr(pi)),'base':stat(arr(bi))}

# New fallen perspectives: shorten a middle span by whole-cell selection/translation.
def span(n,start,end,dy):
 a=clean(load(n),C if 'cross' in n else P);left=Image.fromarray(a[:,:start]);right=Image.fromarray(a[:,end:]);out=Image.new('RGBA',(a.shape[1]-(end-start),a.shape[0]));out.alpha_composite(left,(0,0));out.alpha_composite(right,(start,dy));return out
crossfrag=span('fallen_cross_fragment_v3',24,51,-6)
ua=clean(load('fallen_upright02_fragment_v3'));upperfrag=Image.fromarray(np.concatenate([ua[:13],ua[25:]],axis=0))
crossfrag.save(W/'cross_fragment_final_native.png');upperfrag.save(W/'upper_fragment_final_native.png')
# Broken02: keep all surviving original stone pixels below a worn native fracture.
n='tombstone_upright_02_broken';parent=arr(Image.open(O/'tombstone_upright_02.png'));a=parent.copy();h,w=a.shape[:2];border=[64,64,63,63,64,65,65,64,63,62,62,63,63,64,65,65,64,64,63,63,64,64,65,64,63,63,64,65,65,64,64,63,63,64,65,65,64,64,64,65]
for x in range(w):
 edge=border[x-29] if 29<=x<69 else 66;a[:edge,x]=0
# The top2px weathered lip comes from parent's existing light gray/olive crown, copied natively.
for x in range(30,68):
 edge=border[x-29]
 for j in range(2):
  sx=30+(x-30)%38;sy=33+j
  if a[edge+j,x,3] and parent[sy,sx,3]:a[edge+j,x]=parent[sy,sx]
pi=Image.new('RGBA',(144,144));pi.alpha_composite(Image.fromarray(a),(24,32));bi=Image.new('RGBA',(144,144));bi.alpha_composite(Image.open(O/'tombstone_upright_02_base.png').convert('RGBA'),(24,32));bi.alpha_composite(upperfrag,(4,111));pi.save(S/(n+'.png'));bi.save(S/(n+'_base.png'));records[n]={'source':'fallen_upright02_fragment_v3','parent':'tombstone_upright_02','canvas':[144,144],'origin':[72,144],'parent_offset':[24,32],'surviving_parent_below_y':67,'native_edit':{'fracture_y':border,'fracture_lip_parent_crop':[30,33,68,35],'fragment_remove_native_rows':[13,25],'fragment_offset':[4,111]},'prop':stat(arr(pi)),'base':stat(arr(bi))}
# Cross: remove screen-left arm only. Rest of cross remains byte-identical.
n='tombstone_cross_01_broken';parent=arr(Image.open(O/'tombstone_cross_01.png'));a=parent.copy();a[39:72,:38]=0
# Taper the worn root at x38..40; use existing dark moss edge immediately beside it.
a[42:61,38]=parent[42:61,39];a[60:65,38]=0
pi=Image.new('RGBA',(112,144));pi.alpha_composite(Image.fromarray(a),(8,16));bi=Image.new('RGBA',(112,144));bi.alpha_composite(Image.open(O/'tombstone_cross_01_base.png').convert('RGBA'),(8,16));bi.alpha_composite(crossfrag,(14,113));pi.save(S/(n+'.png'));bi.save(S/(n+'_base.png'));records[n]={'source':'fallen_cross_fragment_v3','parent':'tombstone_cross_01','canvas':[112,144],'origin':[56,144],'parent_offset':[8,16],'native_edit':{'remove_arm_rect':[0,39,38,72],'root_edit_x':38,'fragment_remove_columns':[24,51],'fragment_right_translation_y':-6,'fragment_offset':[14,113]},'prop':stat(arr(pi)),'base':stat(arr(bi))}
# Tilt was completed and visually gated before the batch.
n='tombstone_upright_01_tilted';records[n]=json.loads((W/'tilt_gate.json').read_text());records[n].update({'source':n,'canvas':[112,112],'origin':[56,112],'prop':stat(arr(Image.open(S/(n+'.png')))),'base':stat(arr(Image.open(S/(n+'_base.png'))))})
(W/'finish_records.json').write_text(json.dumps(records,indent=2));print('\n'.join(f'{n}: H{v["prop"]["height"]} C{v["prop"]["colors"]} change{v["prop"]["adjacent_change"]:.3f}%' for n,v in records.items()))
# B1 beside every asset, registration uses same footline rather than canvas bottom.
hero=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');panel=Image.new('RGBA',(800,630),'#403D3F');d=ImageDraw.Draw(panel)
for k,(n,v) in enumerate(records.items()):
 x=(k%4)*200;y=(k//4)*210;pi=Image.open(S/(n+'.png')).convert('RGBA');bi=Image.open(S/(n+'_base.png')).convert('RGBA');pi2=bi.copy();pi2.alpha_composite(pi);bottom=v['prop']['bbox'][3];panel.alpha_composite(hero,(x-12,y+170-96));panel.alpha_composite(pi2,(x+60+(140-pi.width)//2,y+170-bottom));d.text((x+2,y+184),n.replace('tombstone_','ts_'),fill='#BEB7A9')
panel.resize((1600,1260),Image.Resampling.NEAREST).save(W/'all_finished_2x.png')
