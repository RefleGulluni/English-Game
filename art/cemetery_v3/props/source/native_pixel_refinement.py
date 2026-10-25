exec(__import__('pathlib').Path(__file__).with_name('native_pixel_master.py').read_text())
def patch(im,pts,c):poly(im,pts,c)
# Wide irregular weather patches are intentionally authored in native coordinates.
im=assets['tombstone_upright_01'][0]
poly(im,[(16,14),(19,11),(22,11),(22,13),(20,13),(20,16),(18,17),(18,23),(16,24)],S[3]);poly(im,[(19,36),(22,35),(24,37),(24,40),(22,42),(22,47),(19,47)],S[3]);poly(im,[(25,17),(28,18),(29,23),(27,24),(26,22)],S[1]);poly(im,[(29,43),(31,42),(32,44),(32,49),(28,50),(27,48)],S[1]);line(im,[(18,26),(20,26)],S[3]);line(im,[(23,28),(25,28)],S[1]);poly(im,[(13,39),(15,40),(15,45),(17,45),(17,49),(14,50)],S[1]);moss(im,13,39);moss(im,15,48);moss(im,29,51);moss(im,24,7);rect(im,(25,8,26,10),M[1]);poly(im,[(12,17),(14,18),(14,21),(12,22)],S[0]);line(im,[(15,24),(15,31)],S[3]);line(im,[(15,33),(15,37)],S[4]);chip(im,20,56,S[2]);rect(im,(25,57,27,57),S[1]);moss(im,10,55)
im=assets['tombstone_upright_02'][0]
poly(im,[(19,17),(24,17),(25,19),(23,20),(23,24),(19,25)],S[3]);poly(im,[(29,36),(34,34),(35,36),(34,38),(34,43),(31,45),(28,44),(28,40)],S[3]);poly(im,[(19,40),(21,39),(23,42),(23,46),(20,46),(19,44)],S[1]);poly(im,[(32,14),(36,14),(36,16),(34,18),(31,17)],S[1]);line(im,[(22,29),(28,29)],S[1]);line(im,[(22,32),(26,32)],S[1]);moss(im,15,48);moss(im,35,45);moss(im,16,10);rect(im,(16,13,17,17),M[0]);line(im,[(38,19),(38,24)],S[3]);poly(im,[(13,32),(15,32),(15,35),(14,36),(13,36)],S[0]);moss(im,25,54);chip(im,31,55,S[3]);rect(im,(15,56,18,56),S[1])
im=assets['tombstone_cross_01'][0]
poly(im,[(24,12),(27,10),(28,13),(27,17),(28,19),(26,21),(24,20)],S[3]);poly(im,[(25,31),(29,31),(30,34),(28,36),(28,40),(25,41)],S[1]);poly(im,[(25,51),(27,50),(29,54),(29,59),(26,61),(24,59)],S[3]);poly(im,[(12,25),(15,25),(16,28),(13,28)],S[1]);line(im,[(26,10),(28,10)],S[4]);moss(im,22,53);moss(im,23,62);moss(im,34,21);moss(im,17,68);poly(im,[(23,44),(25,45),(25,48),(23,49)],S[0]);line(im,[(31,33),(31,38)],S[3]);chip(im,29,69,S[2])
# Slab erosion preserves the diagonal silhouette; rim breaks remain part of stone, no scattered noise.
im=assets['grave_lid_01'][0]
poly(im,[(21,30),(24,29),(26,33),(24,36),(22,35)],S[3]);poly(im,[(33,48),(36,47),(40,53),(38,56),(35,55)],S[3]);poly(im,[(31,27),(33,29),(33,32),(35,35),(34,37),(32,34)],S[1]);poly(im,[(17,38),(20,39),(23,44),(22,47),(20,46)],S[1]);moss(im,14,30);moss(im,28,61);moss(im,41,59);chip(im,35,65,S[2]);line(im,[(14,34),(17,39)],S[4])
im=assets['open_grave_01'][0]
poly(im,[(23,20),(27,19),(29,20),(27,22),(23,23)],S[2]);poly(im,[(35,18),(37,17),(41,17),(40,19),(36,20)],S[2]);poly(im,[(35,37),(38,38),(40,41),(38,42),(36,40)],S[2]);poly(im,[(47,51),(48,49),(51,52),(51,55),(49,55)],S[1]);poly(im,[(71,61),(75,60),(77,61),(74,63),(71,63)],S[2]);moss(im,22,21);moss(im,43,17);moss(im,61,63);moss(im,80,58)
# Give wall courses stone faces, weathered chips and irregular bright shelves instead of pristine rectangles.
for n in ['low_wall_01','low_wall_broken_01']:
 im=assets[n][0]; a0=im.getchannel('A'); under=im.copy()
 patches=[([(3,26),(10,26),(12,28),(10,29),(9,32),(4,32)],S[2]), ([(26,27),(31,26),(35,27),(35,30),(32,32),(26,31)],S[3]), ([(53,25),(61,25),(64,27),(62,29),(58,28),(55,30),(53,29)],S[3]), ([(79,28),(84,27),(88,29),(89,32),(83,32)],S[1]), ([(13,39),(18,38),(23,39),(23,42),(19,43),(14,42)],S[3]), ([(42,40),(46,38),(50,39),(50,41),(47,43),(42,43)],S[1]), ([(67,39),(71,38),(76,40),(76,43),(71,44),(68,42)],S[3]), ([(27,50),(32,49),(36,51),(34,53),(29,54),(27,53)],S[1]), ([(56,50),(60,49),(65,50),(66,53),(62,55),(58,54)],S[3]), ([(82,52),(87,51),(90,52),(89,55),(83,55)],S[2])]
 for pts,c in patches:
  region=new(96,64);poly(region,pts,c)
  # Limit weather patches to existing front surface and don't fill broken silhouette.
  im.alpha_composite(Image.composite(region,new(96,64),a0))
 for x,y in [(17,24),(34,36),(77,48)]:poly(im,[(x,y),(x+2,y),(x+2,y+2),(x,y+1)],S[0])
 # Restore alpha envelope exactly, including exposed staircase.
 im.putalpha(a0)
 moss(im,3,49);moss(im,19,52);moss(im,52,52);moss(im,82,51 if n=='low_wall_01' else 54)
 if n=='low_wall_01':moss(im,25,17);moss(im,69,17)
 else:moss(im,25,24);moss(im,55,34)
 # Small angular edge bites, authored not randomized.
 for x in [17,44,81]:rect(im,(x,57,x+1,58),(0,0,0,0))
im=assets['wall_pillar_01'][0]
poly(im,[(14,18),(18,18),(20,20),(18,21),(14,21)],S[3]);poly(im,[(23,28),(28,26),(30,28),(30,31),(26,32),(23,31)],S[3]);poly(im,[(14,38),(18,37),(21,39),(20,42),(16,43)],S[1]);poly(im,[(23,50),(27,49),(30,51),(29,54),(24,54)],S[3]);moss(im,13,46);moss(im,15,53);moss(im,32,57);moss(im,11,13);line(im,[(31,37),(30,40),(31,44)],S[0]);chip(im,24,9,S[2]);line(im,[(14,15),(18,15)],S[4])
# Native seam correction: common edge profile, no resampling.
im=assets['low_wall_01'][0]
for y in range(im.height):
 c=im.getpixel((1,y)); im.putpixel((0,y),c); im.putpixel((95,y),c)
# Shorten pillar by moving its complete cap two native rows down, keeping footing fixed.
im=assets['wall_pillar_01'][0];cap=im.crop((0,7,48,19));rect(im,(0,7,47,18),(0,0,0,0));im.alpha_composite(cap,(0,9))
# Base chips use spatially sparse little groups, no opaque disk contact shadows.
for n,(im,b,desc) in assets.items():
 im.save(W/(n+'.png'));b.save(W/(n+'_base.png'))
sheet=Image.new('RGBA',(720,300),'#403D3F');hero=Image.open('/Users/mac/Documents/GitHub.nosync/English-Game/art/character_design/hero_B1.png').convert('RGBA')
for row in range(2):sheet.alpha_composite(hero,(3,row*150+10))
for k,(n,(im,b,d)) in enumerate(assets.items()):
 row=0 if k<5 else 1;col=k if k<5 else k-5;x=110+col*120;y=row*150
 sheet.alpha_composite(b,(x+(120-b.width)//2,y+108-b.height));sheet.alpha_composite(im,(x+(120-im.width)//2,y+108-im.height));ImageDraw.Draw(sheet).text((x,y+118),n.replace('tombstone','tomb').replace('_01',''),fill='white')
sheet.resize((1440,600),Image.Resampling.NEAREST).save(W/'draft_refined.png')
