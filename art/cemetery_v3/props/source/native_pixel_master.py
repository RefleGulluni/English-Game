from PIL import Image, ImageDraw
from pathlib import Path
import json
import sys
W=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/'new_export'
W.mkdir(parents=True,exist_ok=True)
P=json.loads((Path(__file__).parent.parent/'qc/props_palette.json').read_text()); ramps=P['ramps']
S=ramps['stone']; M=ramps['moss']; E=ramps['earth']; I=ramps['iron']
assets={}
def new(w,h):return Image.new('RGBA',(w,h),(0,0,0,0))
def poly(im,pts,c):ImageDraw.Draw(im).polygon(pts,fill=c)
def line(im,pts,c,w=1):ImageDraw.Draw(im).line(pts,fill=c,width=w)
def rect(im,b,c):ImageDraw.Draw(im).rectangle(b,fill=c)
def chip(im,x,y,c):poly(im,[(x,y),(x+3,y),(x+4,y+1),(x+2,y+2),(x,y+1)],c)
def tuft(im,x,y,lean=0):
 line(im,[(x,y),(x-2+lean,y-4)],E[2]);line(im,[(x+1,y),(x+lean,y-6)],M[1]);line(im,[(x+2,y),(x+4+lean,y-3)],E[3]);rect(im,(x,y-1,x+2,y),M[0])
def ground(im,cx,cy,rx):
 # Individual deliberately placed short mud shelves; no ellipse, feathering or shadow.
 poly(im,[(cx-rx,cy-5),(cx-rx+7,cy-7),(cx-7,cy-8),(cx+4,cy-7),(cx+rx-4,cy-6),(cx+rx,cy-3),(cx+rx-3,cy-1),(cx+8,cy),(cx+4,cy-1),(cx-7,cy+1),(cx-rx+4,cy-1)],E[1])
 poly(im,[(cx-rx+5,cy-5),(cx-6,cy-6),(cx-2,cy-4),(cx-6,cy-3),(cx-rx+10,cy-2)],E[2])
 poly(im,[(cx+5,cy-5),(cx+rx-4,cy-4),(cx+rx-6,cy-2),(cx+9,cy-2)],E[0])
 chip(im,cx-rx+3,cy-2,E[2]);chip(im,cx+rx-7,cy,E[2]);chip(im,cx-5,cy+1,M[1]);chip(im,cx+7,cy-7,M[0]);tuft(im,cx-rx+2,cy-3,-1);tuft(im,cx+rx-2,cy-2,1)
def moss(im,x,y):
 poly(im,[(x,y),(x+5,y),(x+5,y+2),(x+3,y+2),(x+3,y+5),(x+1,y+5),(x+1,y+3),(x-1,y+3)],M[0]);rect(im,(x,y,x+3,y+1),M[1]);line(im,[(x,y),(x+2,y)],M[2])
def plinth(im,x,y,w):
 poly(im,[(x,y),(x+4,y-3),(x+w,y-3),(x+w+3,y),(x+w+3,y+4),(x+w-1,y+6),(x,y+5)],S[0])
 poly(im,[(x+1,y),(x+5,y-2),(x+w-1,y-2),(x+w+1,y),(x+w-3,y+2),(x+1,y+2)],S[3]);line(im,[(x+2,y),(x+w-4,y)],S[4]);poly(im,[(x+1,y+3),(x+w-3,y+3),(x+w-3,y+5),(x+1,y+4)],S[2]);poly(im,[(x+w-2,y+2),(x+w+2,y),(x+w+2,y+3),(x+w-2,y+5)],S[1])
def save(n,im,b,desc):assets[n]=(im,b,desc)
# TOMBSTONE 01: softened arch, narrow shoulder, restrained inset blank epitaph.
im=new(48,68);b=new(48,68);ground(b,24,65,22)
poly(im,[(13,54),(12,16),(14,10),(18,6),(25,4),(31,6),(35,11),(37,18),(37,51),(33,56)],S[0])
poly(im,[(15,16),(17,11),(21,8),(27,7),(32,10),(34,16),(34,51),(30,54),(15,52)],S[1])
poly(im,[(15,15),(18,10),(23,7),(28,8),(31,11),(32,16),(32,51),(15,51)],S[3])
poly(im,[(17,17),(19,13),(23,11),(27,12),(29,15),(30,49),(17,49)],S[2])
line(im,[(15,17),(15,14),(18,10),(23,8),(27,8)],S[4]);line(im,[(33,17),(34,50)],S[0]);line(im,[(18,19),(27,19),(28,21),(28,44),(18,45),(18,19)],S[1]);line(im,[(19,21),(26,21)],S[3]);line(im,[(20,28),(25,28)],S[1]);line(im,[(21,31),(26,31)],S[1]);rect(im,(20,34,23,34),S[1]);line(im,[(29,36),(27,38),(28,41),(26,43)],S[0]);plinth(im,10,55,25);moss(im,13,46);moss(im,30,52);chip(im,21,54,S[4]);save('tombstone_upright_01',im,b,'完整圆拱墓碑；浅凹碑面、右侧厚度与抬高的石质座。')
# TOMBSTONE 02: broken corner, broad low shoulder, a different silhouette.
im=new(56,64);b=new(56,64);ground(b,28,61,26)
poly(im,[(13,52),(13,13),(15,8),(25,8),(28,4),(35,4),(35,10),(40,10),(42,14),(42,52),(37,56)],S[0])
poly(im,[(15,14),(17,10),(26,10),(29,7),(33,7),(33,13),(38,13),(39,16),(39,52),(15,52)],S[3]);poly(im,[(17,16),(36,16),(36,50),(17,50)],S[2]);poly(im,[(39,15),(41,14),(41,51),(37,54),(37,17)],S[1]);line(im,[(16,13),(18,10),(25,10)],S[4]);line(im,[(29,8),(31,8),(31,12),(34,14)],S[1]);line(im,[(26,12),(25,17),(28,21),(27,25)],S[0]);line(im,[(18,21),(34,21),(34,45),(19,46),(18,21)],S[1]);line(im,[(20,23),(32,23)],S[3]);line(im,[(22,30),(29,30)],S[1]);line(im,[(22,33),(27,33)],S[1]);poly(im,[(16,43),(20,45),(21,50),(18,51),(16,49)],S[1]);plinth(im,10,54,31);moss(im,16,47);moss(im,34,53);save('tombstone_upright_02',im,b,'缺角的宽肩墓碑；断面与大裂口取代细碎写实纹理。')
# CROSS: squat old stone cross, structural silhouette, no shiny gold.
im=new(56,80);b=new(56,80);ground(b,28,77,25)
poly(im,[(22,66),(21,31),(9,31),(9,19),(21,19),(21,9),(25,5),(34,5),(35,9),(35,17),(46,17),(47,29),(35,33),(35,65)],S[0])
poly(im,[(23,65),(23,29),(11,29),(11,22),(23,22),(23,10),(26,8),(32,8),(32,22),(44,20),(44,27),(32,30),(32,65)],S[3]);poly(im,[(26,13),(30,12),(30,25),(40,23),(40,26),(30,28),(30,63),(26,63),(26,27),(14,27),(14,24),(26,24)],S[2]);poly(im,[(33,10),(34,9),(34,23),(46,20),(46,27),(34,31),(34,65),(32,66),(32,30),(44,27),(44,22),(32,24)],S[1]);line(im,[(23,20),(23,10),(26,7),(31,7)],S[4]);line(im,[(12,22),(20,22)],S[4]);line(im,[(25,42),(28,45),(27,49),(29,52)],S[0]);plinth(im,16,67,23);moss(im,23,57);moss(im,34,69);save('tombstone_cross_01',im,b,'厚重石十字；窄高竖干与横臂形成独立剪影，右侧石厚清楚。')
# GRAVE: parallelogram hole, dark excavation interior belongs ground layer.
im=new(112,80);b=new(112,80)
# flat turned soil around footprint, intentionally irregular non-shadow patches
poly(b,[(9,22),(20,14),(51,11),(62,16),(72,29),(98,54),(102,63),(90,72),(57,77),(37,65),(16,39)],E[1]);poly(b,[(11,24),(20,18),(25,19),(26,26),(17,30)],E[2]);poly(b,[(50,69),(69,72),(88,65),(93,67),(80,74),(60,77)],E[2]);poly(b,[(26,27),(54,21),(88,58),(61,65)],I[0]);poly(b,[(26,27),(32,28),(60,57),(60,65)],E[0]);poly(b,[(32,28),(54,21),(56,26),(37,32)],E[0]);poly(b,[(56,27),(86,58),(79,59),(53,32)],E[1]);poly(b,[(41,43),(47,45),(59,56),(57,59),(50,52)],E[1]);line(b,[(35,32),(47,44)],E[2]);tuft(b,10,35,-1);tuft(b,93,64,1);tuft(b,42,72);chip(b,78,70,S[1])
# raised stone rim built in explicit four segments, top light / front dark
poly(im,[(20,19),(54,13),(60,18),(27,25),(59,60),(94,53),(99,59),(62,69),(56,67),(17,28)],S[0]);poly(im,[(21,20),(53,15),(57,18),(26,24),(59,62),(94,55),(96,58),(60,66),(20,27)],S[3]);poly(im,[(22,23),(26,25),(60,63),(60,68),(56,66),(20,28)],S[1]);poly(im,[(60,64),(96,57),(96,61),(61,70)],S[1]);line(im,[(21,21),(52,15)],S[4]);line(im,[(28,25),(57,59)],S[4]);line(im,[(62,64),(92,57)],S[4]);poly(im,[(57,18),(61,18),(96,53),(94,56),(89,55),(54,21)],S[2]);line(im,[(60,18),(95,53)],S[3]);
for pts in [[(29,19),(31,22)],[(41,17),(43,20)],[(26,31),(30,30)],[(35,41),(39,40)],[(45,53),(49,52)],[(68,62),(70,66)],[(80,60),(82,63)],[(69,28),(66,30)],[(81,40),(78,42)]]:line(im,pts,S[0])
moss(im,18,24);moss(im,57,63);moss(im,88,54);save('open_grave_01',im,b,'墓穴石沿独立遮挡；坑内深色、土壁与坑底在地面 base 层，避免坑底遮住角色。约96×64占地。')
# SLAB: tilted against rim/ground, no baked shadow.
im=new(64,76);b=new(64,76);ground(b,32,73,29)
poly(im,[(10,28),(33,16),(55,60),(52,65),(29,71),(8,33)],S[0]);poly(im,[(12,28),(32,19),(52,59),(30,66)],S[3]);poly(im,[(30,66),(52,59),(53,63),(30,69),(10,33),(10,30)],S[1]);poly(im,[(16,30),(30,23),(47,57),(32,61)],S[2]);line(im,[(13,29),(31,20),(33,23)],S[4]);line(im,[(19,32),(29,27),(42,54),(33,57),(19,32)],S[1]);line(im,[(29,35),(31,39),(29,42),(33,46)],S[0]);moss(im,28,62);chip(im,47,60,S[4]);save('grave_lid_01',im,b,'单独斜倚的盖板，轮廓为厚石板；可摆在墓穴旁，非固定盖死的成组画。')
# WALL: common horizontally repeatable end profile, masonry staggered by hand.
def wall(broken=False):
 im=new(96,64);b=new(96,64);ground(b,48,61,46)
 outline=[(0,17),(95,17),(95,58),(0,58)] if not broken else [(0,17),(26,17),(26,25),(41,25),(41,33),(58,33),(58,42),(75,42),(75,50),(95,50),(95,58),(0,58)]
 poly(im,outline,S[0]);mask=im.getchannel('A')
 paint=new(96,64)
 # courses: dark mortar gutters with varied blocks, no noisy per-pixel texture
 for y,spans in [(24,[(0,18),(21,46),(49,73),(76,95)]),(36,[(0,8),(11,34),(37,61),(64,86),(89,95)]),(48,[(0,22),(25,49),(52,77),(80,95)])]:
  for k,(x,x1) in enumerate(spans):
   rect(paint,(x,y,x1,y+8),S[2] if k%3 else S[1]);line(paint,[(x,y),(x1-1,y)],S[3]);line(paint,[(x,y+1),(x,y+6)],S[3]);line(paint,[(x+2,y+7),(x1,y+7)],S[1]);
 # top stepped caps, each top bevel is 4px deep
 caps=[(0,17,25),(26,25,15),(42,33,16),(59,42,16),(76,50,19)] if broken else [(0,17,23),(24,17,23),(48,17,23),(72,17,23)]
 for x,y,span in caps:
  poly(paint,[(x,y),(x+3,y-3),(x+span,y-3),(x+span,y+2),(x,y+2)],S[0]);poly(paint,[(x,y),(x+3,y-2),(x+span-1,y-2),(x+span-1,y),(x,y+1)],S[3]);line(paint,[(x+2,y-1),(x+span-2,y-1)],S[4]);rect(paint,(x,y+2,x+span-1,y+4),S[2])
 # combine caps (including their upper bevel) then body clipped to stepped silhouette
 im.alpha_composite(Image.composite(paint,new(96,64),mask))
 for x,y,span in caps:
  poly(im,[(x,y),(x+3,y-3),(x+span,y-3),(x+span,y+1),(x,y+1)],S[0]);poly(im,[(x,y),(x+3,y-2),(x+span-1,y-2),(x+span-1,y),(x,y)],S[3]);line(im,[(x+3,y-2),(x+span-2,y-2)],S[4])
 moss(im,7,51);moss(im,38,54);moss(im,72,51 if not broken else 53);line(im,[(31,30),(30,34),(32,38)],S[0]);
 if broken:chip(b,85,60,S[2]);chip(b,70,63,S[1]);chip(b,88,55,S[3]);tuft(b,75,58)
 return im,b
im,b=wall();save('low_wall_01',im,b,'96px完整直墙段，错缝石砌；左右端为同一断面，可原生水平重复。')
im,b=wall(True);save('low_wall_broken_01',im,b,'同墙系阶梯状残断段，向右破落；不作为无限重复中段。')
# PILLAR: equal depth, same masonry ramp.
im=new(48,68);b=new(48,68);ground(b,24,65,22)
poly(im,[(11,57),(11,14),(16,9),(34,9),(38,14),(38,59),(32,63),(11,62)],S[0]);rect(im,(13,16,31,59),S[2]);poly(im,[(32,16),(36,13),(36,58),(32,61)],S[1]);
for y in [22,34,46]:
 line(im,[(13,y),(31,y)],S[0]);line(im,[(13,y+1),(31,y+1)],S[3]);line(im,[(32,y),(36,y-2)],S[0])
for x,y in [(23,16),(19,24),(25,36),(20,48)]:line(im,[(x,y),(x,y+8)],S[0])
plinth(im,8,58,28);poly(im,[(8,13),(13,7),(35,7),(41,12),(36,17),(8,17)],S[0]);poly(im,[(10,12),(14,8),(34,8),(38,12),(34,14),(10,14)],S[3]);line(im,[(12,11),(16,9),(32,9)],S[4]);poly(im,[(10,15),(34,15),(34,18),(10,18)],S[2]);poly(im,[(35,14),(39,12),(39,15),(35,18)],S[1]);moss(im,13,49);moss(im,32,58);save('wall_pillar_01',im,b,'墙柱与墙同材质，柱帽有顶面；可覆盖墙与栏的连接端。')
# IRON FENCE: tall spade tips, visible negative space; warm rust only in small groups.
im=new(96,76);b=new(96,76)
for x in [8,40,72,88]:ground(b,x,73,6)
for y in [28,52]:
 rect(im,(0,y,95,y+3),I[0]);line(im,[(0,y),(95,y)],I[2]);line(im,[(0,y+1),(95,y+1)],I[1]);
for n,x in enumerate([8,24,40,56,72,88]):
 poly(im,[(x,11),(x-3,17),(x-2,20),(x-1,20),(x-1,68),(x+2,68),(x+2,20),(x+4,18)],I[0]);line(im,[(x,19),(x,66)],I[2]);line(im,[(x+1,21),(x+1,67)],I[1]);line(im,[(x,14),(x-1,18),(x,19)],I[3]);rect(im,(x-1,29,x+2,31),I[0]);rect(im,(x-1,53,x+2,55),I[0]);rect(im,(x,29,x,30),I[3]);
 if n in [1,4]:rect(im,(x,39,x,42),E[2]);rect(im,(x,43,x,44),I[1])
# little forged diamonds between bars, only structural purposeful accents
for x in [16,48,80]:line(im,[(x-4,45),(x,38),(x+4,45),(x,50),(x-4,45)],I[1]);line(im,[(x-3,44),(x,39)],I[2])
save('iron_fence_01',im,b,'六根矛尖铁栏、上下横梁与少量锻铁菱花；镂空清楚，可独立立地。')
# native exports only: no resize in asset creation
for n,(im,b,d) in assets.items():im.save(W/(n+'.png'));b.save(W/(n+'_base.png'))
(W/'descriptions.json').write_text(json.dumps({n:d for n,(_,_,d) in assets.items()},ensure_ascii=False,indent=2))
# first review contact at 4x only, assets remain native
sheet=Image.new('RGBA',(600,310),'#403D3F')
for k,(n,(im,b,d)) in enumerate(assets.items()):
 x=(k%5)*120;y=(k//5)*150;sheet.alpha_composite(b,(x+(120-b.width)//2,y+100-b.height));sheet.alpha_composite(im,(x+(120-im.width)//2,y+100-im.height));ImageDraw.Draw(sheet).text((x+3,y+108),n.replace('tombstone','tomb').replace('_01',''),fill='white')
sheet.resize((1200,620),Image.Resampling.NEAREST).save(W/'draft.png')
print('native assets',len(assets))
