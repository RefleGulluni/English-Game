from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
W=Path('/tmp/english-game-ashlar02-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';S=W/'staged'
def get(n,suf=''):return Image.open((S if n=='low_wall_ashlar_02' else O)/(n+suf+'.png')).convert('RGBA')
def at(p,n,x,y,suf):
 im=get(n,suf);p.alpha_composite(im,(x-im.width//2,y-im.height))
objs=[('low_wall_ashlar_02',184,140),('low_wall_ashlar_02',424,140),('low_wall_broken_01',611,140),('wall_pillar_01',60,140),('low_wall_ashlar_02',184,320),('low_wall_ashlar_01',371,320),('low_wall_ashlar_02',552,320),('wall_pillar_01',60,320)]
p=Image.new('RGBA',(960,355),'#403D3F')
for suf in ['_base','']:
 for n,x,y in objs:at(p,n,x,y,suf)
h=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA')
for y in [140,320]:p.alpha_composite(h,(810,y-96))
d=ImageDraw.Draw(p);d.text((10,153),'Gate pillar + ashlar02 + ashlar02 + original broken ashlar',fill='#BEB7A9');d.text((10,333),'Gate pillar + ashlar02 + preserved ashlar01 + ashlar02',fill='#BEB7A9');p.save(W/'assembly_1x.png');p.resize((1920,710),Image.Resampling.NEAREST).save(W/'ashlar_02_assembly_2x.png')
joints=[(64,140,'gate /02'),(304,140,'02/02'),(544,140,'02/broken'),(64,320,'gate/02'),(304,320,'02/01'),(432,320,'01/02')]
j=Image.new('RGBA',(192,232),'#403D3F');jd=ImageDraw.Draw(j)
for k,(x,y,label) in enumerate(joints):
 x0=k%3*64;y0=k//3*116;j.alpha_composite(p.crop((x-29,y-98,x+29,y+4)),(x0+3,y0+10));jd.text((x0+3,y0),str(k+1)+' '+label,fill='#BEB7A9')
j.resize((1536,1856),Image.Resampling.NEAREST).save(W/'ashlar_02_joints_8x.png')
new=np.array(get('low_wall_ashlar_02'));broken=np.array(get('low_wall_broken_01'));old=np.array(get('low_wall_ashlar_01'))
checks={'left_equals_broken':bool(np.array_equal(new[:,24],broken[:,21])),'right_equals_broken':bool(np.array_equal(new[:,263],broken[:,21])),'self_repeat_exact':bool(np.array_equal(new[:,24],new[:,263])),'02_to01_exact':bool(np.array_equal(new[:,263],old[:,21])),'01_to02_exact':bool(np.array_equal(old[:,148],new[:,24]))};assert all(checks.values()),checks
(W/'interface_checks.json').write_text(json.dumps({'checks':checks,'assembly':objs,'joint_labels':[x[2] for x in joints]},indent=2));print(checks)
