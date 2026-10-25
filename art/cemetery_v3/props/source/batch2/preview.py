from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np
W=Path('/tmp/english-game-props-batch2-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';Q=O/'qc';rec=json.loads((W/'finish_records.json').read_text());H=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');BG='#403D3F';TXT='#C1B9A9'
def composite(n):
 b=Image.open(O/(n+'_base.png')).convert('RGBA');p=Image.open(O/(n+'.png')).convert('RGBA');b.alpha_composite(p);return b

def scaled(im,z,path):im.resize((im.width*z,im.height*z),Image.Resampling.NEAREST).save(path)
for n,v in rec.items():
 d=Q/'batch2_sources'/n;p=Image.open(O/(n+'.png')).convert('RGBA');b=Image.open(O/(n+'_base.png')).convert('RGBA');w=96+32+max(160,p.width)+24;h=max(96,v['prop']['height'])+52;baseline=h-34;out=Image.new('RGBA',(w,h),BG);dr=ImageDraw.Draw(out);out.alpha_composite(H,(8,baseline-96));out.alpha_composite(composite(n),(136+(max(160,p.width)-p.width)//2,baseline-v['prop']['bbox'][3]));dr.text((8,4),n,fill=TXT);dr.text((8,h-11),'B1 96px / native asset / nearest6x',fill=TXT);scaled(out,6,d/'05_vs_hero_6x.png');out.save(d/'05_vs_hero_1x.png')
 l=Image.new('RGBA',(p.width*2+16,p.height+18),BG);l.alpha_composite(p,(0,0));l.alpha_composite(b,(p.width+16,0));ld=ImageDraw.Draw(l);ld.text((3,p.height+4),'PROP',fill=TXT);ld.text((p.width+19,p.height+4),'BASE',fill=TXT);scaled(l,8,d/'04_layers_8x.png')
# One row, all old and new tombstone shapes and states.
names=['tombstone_upright_01','tombstone_upright_02','tombstone_cross_01','tombstone_flat_01','tombstone_pointed_01','tombstone_small_01','obelisk_01','grave_slab_01','tombstone_upright_01_tilted','tombstone_upright_02_broken','tombstone_cross_01_broken'];labels=['01 arch','02 broken corner','03 cross','04 flat','05 pointed','06 small','07 obelisk','08 ground slab','09 tilted01','10 broken02','11 broken cross']
slots=[max(116,composite(n).width+12) for n in names];out=Image.new('RGBA',(128+sum(slots)+16,218),BG);d=ImageDraw.Draw(out);baseline=174;out.alpha_composite(H,(16,baseline-96));d.text((16,196),'B1 /96px',fill=TXT);x=128
for n,label,sw in zip(names,labels,slots):
 im=composite(n);bbox=Image.open(O/(n+'.png')).getbbox();out.alpha_composite(im,(x+(sw-im.width)//2,baseline-bbox[3]));d.text((x+3,196),label,fill=TXT);x+=sw
d.text((16,8),'CEMETERY BATCH2 | old + new shapes / native scale | 2x nearest',fill=TXT);scaled(out,2,Q/'batch2_lineup_2x.png')
# State pairs align unchanged parent and derivative by logical origin, not cropped bbox.
pairs=[('tombstone_upright_01','tombstone_upright_01_tilted'),('tombstone_upright_02','tombstone_upright_02_broken'),('tombstone_cross_01','tombstone_cross_01_broken')];out=Image.new('RGBA',(400,624),BG);d=ImageDraw.Draw(out)
for i,(a,b) in enumerate(pairs):
 top=i*208;origin_y=top+178
 for n,ox in [(a,100),(b,285)]:
  im=composite(n);out.alpha_composite(im,(ox-im.width//2,origin_y-im.height))
 d.text((12,top+7),a+' / '+b,fill=TXT);d.text((42,top+190),'ORIGINAL',fill=TXT);d.text((240,top+190),'STATE',fill=TXT)
 out.crop((0,top,400,top+208)).resize((2400,1248),Image.Resampling.NEAREST).save(Q/'batch2_sources'/b/'state_pair_6x.png')
scaled(out,6,Q/'batch2_states_6x.png')
# Fifteen unique props on neutral dark QC ground. These are placements only, not new scene art.
layout=[('tombstone_upright_01',98,180),('tombstone_pointed_01',235,168),('tombstone_cross_01',390,170),('obelisk_01',535,180),('tombstone_flat_01',90,305),('tombstone_upright_01_tilted',240,300),('tombstone_upright_02',385,290),('tombstone_small_01',520,295),('tombstone_upright_02_broken',130,426),('tombstone_cross_01_broken',350,425),('grave_slab_01',520,410),('grave_vase_01',155,205),('grave_lantern_01',434,209),('candles_01',297,329),('rubble_pile_01',441,341)]
out=Image.new('RGBA',(640,464),'#343332');d=ImageDraw.Draw(out)
for n,x,y in layout:
 im=Image.open(O/(n+'_base.png')).convert('RGBA');out.alpha_composite(im,(x-im.width//2,y-im.height))
actors=[(y,n,x) for n,x,y in layout]+[(235,'B1',285)]
for y,n,x in sorted(actors):
 im=H if n=='B1' else Image.open(O/(n+'.png')).convert('RGBA');out.alpha_composite(im,(x-im.width//2,y-im.height))
d.text((15,14),'BATCH2 |15 unique props + B1 | neutral QC ground',fill=TXT);d.text((15,447),'Layer order: all bases / props + B1 by origin Y. No added shadows.',fill=TXT);scaled(out,2,Q/'batch2_cluster_2x.png');(Q/'batch2_cluster_layout.json').write_text(json.dumps({'background':'#343332 neutral QC ground, not production terrain','hero':[285,235],'objects':layout},indent=2))
# Pixel layer crop proof: the slab is broad due to perspective, thickness is only the side face.
n='grave_slab_01';out=Image.new('RGBA',(192,130),BG);out.alpha_composite(composite(n),(0,0));d=ImageDraw.Draw(out);dx,dy=rec[n]['offset'];samples=[(50,51,59),(80,42,50),(115,33,42)]
for x,y0,y1 in samples:
 x+=dx;y0+=dy;y1+=dy;d.line((x,y0,x,y1),fill='#DA8574');d.text((x+2,y1+2),str(y1-y0)+'px',fill=TXT)
d.text((6,114),'Side face 8 /8 /9px; full top-face depth is not thickness.',fill=TXT);scaled(out,6,Q/'batch2_slab_thickness_6x.png')
print('Preview files complete; all enlargements integer NEAREST.')
