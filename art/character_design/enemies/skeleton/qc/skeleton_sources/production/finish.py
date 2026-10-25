from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
W=Path('/tmp/english-game-skeleton-design-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=W/'staged';S.mkdir(exist_ok=True)
sources={'A':('A_standing_v2','A_remains_v3'),'B':('B_standing_v3','B_remains'),'C':('C_standing_v2','C_remains')};records={}
def clean(a):
 a=a.copy();bad=(a[:,:,0].astype(int)-a[:,:,1].astype(int)>28)&(a[:,:,2].astype(int)-a[:,:,1].astype(int)>28);a[bad]=0;a[a[:,:,3]==0]=0;return a

def load(n):return clean(np.array(Image.open(W/'recovered'/n/'restored_native.png').convert('RGBA')))
def maskpoly(a,pts):
 im=Image.new('L',(a.shape[1],a.shape[0]),0);ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0

def move(a,mask,dx,dy):
 # Native hand-selected object/bone groups, no resampling or new texture.
 selected=a.copy();selected[~mask]=0;out=a.copy();out[mask]=0;im=Image.fromarray(out);im.alpha_composite(Image.fromarray(selected),(dx,dy));return np.array(im)

def stat(a):
 m=a[:,:,3]>0;y,x=np.where(m);q=m[:,:-1]&m[:,1:];z=np.any(a[:,:-1,:3]!=a[:,1:,:3],axis=2)
 return {'canvas':[a.shape[1],a.shape[0]],'bbox':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'visible_width':int(x.max()-x.min()+1),'visible_height':int(y.max()-y.min()+1),'lowest_opaque_y':int(y.max()),'colors':len(np.unique(a[m,:3],axis=0)),'adjacent_change':round(100*float(np.sum(q&z))/np.sum(q),6),'opaque':int(m.sum())}

def palette_pair(aa,bb):
 rgb=np.concatenate([aa[aa[:,:,3]>0,:3],bb[bb[:,:,3]>0,:3]]);hist=Image.fromarray(rgb.reshape(1,-1,3));q=hist.quantize(colors=48,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);rep=np.unique(np.array(q.convert('RGB')).reshape(-1,3),axis=0);original=np.unique(rgb,axis=0).astype(int)
 # Representatives are actual sampled source RGBs nearest merged-color bins.
 pal=original[((rep.astype(int)[:,None,:]-original[None,:,:])**2).sum(2).argmin(1)]
 out=[]
 for a in [aa,bb]:
  a=a.copy();m=a[:,:,3]>0;c=a[m,:3].astype(int);a[m,:3]=pal[((c[:,None,:]-pal[None,:,:])**2).sum(2).argmin(1)];out.append(a)
 return *out,pal

for letter,(sn,rn) in sources.items():
 a=load(sn);b=load(rn);edits=[]
 if letter=='B':
  # Whole skull, neck and pin tips settle1px towards shoulders, no waist seam or limb cut.
  m=np.zeros(a.shape[:2],bool);m[:17]=True;a=move(a,m,0,1);edits.append({'standing_upper_region':[0,0,a.shape[1],17],'translation':[0,1],'reason':'Settle skull/neck1native pixel; body remains continuous; source97px becomes96px.'})
 if letter=='A':
  m=np.zeros(b.shape[:2],bool);m[10:,65:]=True;b=move(b,m,-12,3);edits.append({'remains_right_loose_arm_region':[65,10,b.shape[1],b.shape[0]],'translation':[-12,3]})
 if letter=='B':
  left=np.zeros(b.shape[:2],bool);left[16:,:18]=True;b=move(b,left,13,0)
  right=maskpoly(b,[(85,18),(95,18),(95,38),(78,38),(78,27),(85,24)]);b=move(b,right,-14,-3)
  lower=np.zeros(b.shape[:2],bool);lower[28:]=True;b=move(b,lower,0,-4)
  edits.extend([{'remains_left_arm_region':[0,16,18,39],'translation':[13,0]},{'remains_right_arm_polygon':[(85,18),(95,18),(95,38),(78,38),(78,27),(85,24)],'translation':[-14,-3]},{'remains_lower_loose_bone_cluster':[0,28,96,39],'translation':[0,-4]}])
 if letter=='C':
  left=np.zeros(b.shape[:2],bool);left[16:,:14]=True;b=move(b,left,13,1)
  right=np.zeros(b.shape[:2],bool);right[16:,82:]=True;b=move(b,right,-14,-2)
  top=np.zeros(b.shape[:2],bool);top[:5,47:56]=True;b=move(b,top,0,2)
  lower=np.zeros(b.shape[:2],bool);lower[29:]=True;b=move(b,lower,0,-2)
  edits.extend([{'remains_left_loose_bone_region':[0,16,14,39],'translation':[13,1]},{'remains_right_shin_region':[82,16,98,39],'translation':[-14,-2]},{'remains_raised_rib_tip_region':[47,0,56,5],'translation':[0,2]},{'remains_lower_loose_bones':[0,29,98,39],'translation':[0,-2]}])
 a,b,pal=palette_pair(a,b);entry={'standing_source':sn,'remains_source':rn,'native_selection_edits':edits,'shared_palette':pal.tolist()}
 for state,raw,canvas in [('standing',a,(96,96)),('remains',b,(96,48))]:
  im=Image.fromarray(raw);box=im.getbbox();crop=im.crop(box);dx=(canvas[0]-crop.width)//2;dy=canvas[1]-crop.height
  assert dx>=0 and dy>=0,(letter,state,crop.size)
  dst=Image.new('RGBA',canvas);dst.alpha_composite(crop,(dx,dy));name='skeleton_'+letter+('_remains' if state=='remains' else '');dst.save(S/(name+'.png'));entry[state]={'source_crop_bbox':list(box),'integer_registration':[dx-box[0],dy-box[1]],'origin':[48,canvas[1]],**stat(np.array(dst))};Image.fromarray(raw).save(W/(letter+'_'+state+'_cleaned_native.png'))
 records[letter]=entry
 print(letter,entry['standing']['visible_height'],entry['standing']['visible_width'],entry['standing']['colors'],entry['standing']['adjacent_change'],'pile',entry['remains']['visible_width'],entry['remains']['visible_height'],entry['remains']['colors'],entry['remains']['adjacent_change'])
(W/'finish_records.json').write_text(json.dumps(records,indent=2))
# One neutral scratch overview; formal comparisons will use requested ground plate.
out=Image.new('RGBA',(480,162),'#403D3F');d=ImageDraw.Draw(out)
for i,l in enumerate(records):
 p=Image.open(S/('skeleton_'+l+'.png'));b=Image.open(S/('skeleton_'+l+'_remains.png'));out.alpha_composite(p,(i*160,16));out.alpha_composite(b,(i*160+64,80));d.text((i*160+8,143),l,fill='#C1B9A9')
out.resize((1920,648),Image.Resampling.NEAREST).save(W/'gate_4x.png')
