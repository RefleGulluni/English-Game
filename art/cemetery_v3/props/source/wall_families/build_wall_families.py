from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,runpy,subprocess,sys
W=Path('/tmp/english-game-wall-families-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';S=W/'staged';S.mkdir(exist_ok=True)
A=Image.open(O/'low_wall_01.png').convert('RGBA');Ab=Image.open(O/'low_wall_01_base.png').convert('RGBA');B=Image.open(O/'low_wall_broken_01.png').convert('RGBA');Bb=Image.open(O/'low_wall_broken_01_base.png').convert('RGBA');recipes={}
def mask(im,pts):
 m=Image.new('L',im.size,0);ImageDraw.Draw(m).polygon(pts,fill=255);a=np.array(im);a[np.array(m)==0]=0;return Image.fromarray(a)
def paste(dst,src,box,xy):
 # Every pixel is a literal source copy at integer coordinates; no resampling.
 dst.alpha_composite(src.crop(box),xy)
def exact_paste(dst,src,box,xy):dst.paste(src.crop(box),xy)
# A1: destroy the right half along masonry joints; retain the entire left half.
n='low_wall_rubble_broken_01';p=mask(A,[(0,0),(88,0),(88,44),(95,46),(95,58),(109,58),(113,62),(113,73),(134,73),(139,78),(148,78),(148,84),(191,84),(191,95),(0,95)]);b=Ab.copy()
# Retained source stone fragments moved to ground; their original upperleft light retained.
frag1=mask(A,[(87,79),(94,78),(98,81),(98,85),(94,88),(88,87),(85,84)])
frag2=mask(A,[(121,62),(128,62),(132,65),(130,70),(123,71),(119,67)])
paste(b,frag1,(84,77,100,89),(139,84));paste(b,frag2,(118,61,134,73),(162,84))
# Keep a50-color subset of the inherited stone+earth palettes. No synthesized colors.
ba=np.array(b);fg=ba[:,:,3]>0;cs,cts=np.unique(ba[fg,:3],axis=0,return_counts=True);keep=cs[np.argsort(cts)[-50:]].astype(int)
for yy,xx in zip(*np.where(fg)):
 rgb=ba[yy,xx,:3].astype(int);ba[yy,xx,:3]=keep[((keep-rgb)**2).sum(1).argmin()]
b=Image.fromarray(ba)
p.save(S/(n+'.png'));b.save(S/(n+'_base.png'));recipes[n]={'parent':'low_wall_01','canvas':[192,96],'origin':[96,96],'joins':{'left':21,'parent_right':168,'root_dx_after_parent':148},'left_unchanged_region':[0,0,89,96],'native_edit':'Remove source upper-right stone courses along native contour; 2 actual rounded-stone fragments moved onto original base.','fragments':[{'source_box':[84,77,100,89],'target_xy':[139,84]},{'source_box':[118,61,134,73],'target_xy':[162,84]}]}
# A2: SAME whole wall with an embedded higher center; all lowercourses remain unchanged.
n='low_wall_rubble_pillar_01';p=Image.new('RGBA',(192,128));b=Image.new('RGBA',(192,128));p.alpha_composite(A,(0,32));b.alpha_composite(Ab,(0,32))
# Upper two-stone stack and its mortar bond taken from the same rubble wall.
cap=A.crop((68,34,112,59));cap=mask(cap,[(0,10),(4,4),(12,1),(20,3),(25,0),(34,2),(43,7),(43,24),(0,24)])
p.alpha_composite(cap,(74,43))
# Small tie-course overlaps the existing central coping only, no plinth or forward foot.
bond=A.crop((67,58,111,74));p.alpha_composite(bond,(74,65))
p.save(S/(n+'.png'));b.save(S/(n+'_base.png'));recipes[n]={'parent':'low_wall_01','canvas':[192,128],'origin':[96,128],'joins':{'left':21,'right':168,'stride':148},'native_edit':'Same complete parent wall shifted down32 solely for taller canvas; centered upper stones and mortar copied from parent to raise a bonded stack. No projecting pedestal.','source_patches':[{'source_box':[68,34,112,59],'target_xy':[74,43]},{'source_box':[67,58,111,74],'target_xy':[74,65]}],'lower_wall_unchanged_from_y':81}
# B1: extend complete ashlar left end using source face/coping courses at unchanged y.
n='low_wall_ashlar_01';p=Image.new('RGBA',(176,96));b=Image.new('RGBA',(176,96));left,right=21,148
# Keep source's intact prefix and full-course levels, then extend source ashlar faces.
exact_paste(p,B,(21,32,43,90),(21,32))
for x in [43,75,107,139]:
 # Material-rich ashlar front face, horizontal mortar at its original height.
 paste(p,B,(29,49,61,70),(x,49))
 paste(p,B,(31,70,63,90),(x,70))
# The original intact coping is20px wide; continue it at the same elevation.
for x in [43,63,83,103,123,143]:paste(p,B,(23,35,43,50),(x,35))
# Constrain to intended128px wall span, retaining native y and protecting both joins.
a=np.array(p);a[:,:left]=0;a[:,right+1:]=0;p=Image.fromarray(a)
# Context near right join is the real intact B prefix, including native mortar courses.
exact_paste(p,B,(21,32,43,90),(127,32))
a=np.array(p);a[:,:left]=0;a[:,right+1:]=0;a[:,right]=np.array(B)[:,21];a[:,left]=np.array(B)[:,21];p=Image.fromarray(a)
# Ground is inherited and repeated from B's existing dark base, not newly generated.
for x in [12,44,76,108,140]:paste(b,Bb,(15,76,47,96),(x,76))
bb=np.array(b);bb[:,:11]=0;bb[:,159:]=0;b=Image.fromarray(bb)
p.save(S/(n+'.png'));b.save(S/(n+'_base.png'));recipes[n]={'parent':'low_wall_broken_01','canvas':[176,96],'origin':[88,96],'joins':{'left':21,'right':148,'stride':128,'parent_broken_left':21,'root_dx_to_parent_broken':128},'native_edit':'Preserve complete parent prefix; extend existing ashlar faces and coping at native original y35/49/70; repeat original dark ground; right context copies parent intact prefix.','source_regions':{'prefix':[21,32,43,90],'upper_face':[29,49,61,70],'lower_face':[31,70,63,90],'coping':[23,35,43,50],'base':[15,76,47,96]}}
(W/'recipes.json').write_text(json.dumps(recipes,indent=2))
# Preview all new components with the accepted B1 at native size and nearest2x.
h=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');c=Image.new('RGBA',(780,170),'#403D3F');d=ImageDraw.Draw(c)
for k,n in enumerate(recipes):
 x=k*260;c.alpha_composite(h,(x-10,40))
 for suf in ['_base','']:
  im=Image.open(S/(n+suf+'.png'));c.alpha_composite(im,(x+160-im.width//2,136-im.height))
 d.text((x+2,148),n,fill='#BEB7A9')
c.resize((1560,340),Image.Resampling.NEAREST).save(W/'components_2x.png')
