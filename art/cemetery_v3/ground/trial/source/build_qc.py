from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[3]
QC=ROOT/'qc'
ONE=Image.open(ROOT/'ground_trial_01.png').convert('RGBA')
TWO=Image.open(ROOT/'ground_trial_02.png').convert('RGBA')
NEAR=Image.Resampling.NEAREST
seam=Image.new('RGBA',(480,135));seam.alpha_composite(ONE);seam.alpha_composite(TWO,(240,0))
seam.save(QC/'ground_seam_test_1x.png')
seam.resize((960,270),NEAR).save(QC/'ground_seam_test_2x.png')
# Full-height 48-pixel strip: the join is exactly in its center. No seam retouch.
seam.crop((216,0,264,135)).resize((384,1080),NEAR).save(QC/'ground_seam_detail_8x.png')
# An optional marked diagnostic with separate margin, leaving terrain pixels untouched.
marked=Image.new('RGB',(960,294),(24,24,24));marked.paste(seam.resize((960,270),NEAR),(0,24))
dr=ImageDraw.Draw(marked);dr.text((8,7),'01',fill='white');dr.text((490,7),'02',fill='white');dr.line((480,15,480,23),fill=(255,60,140));marked.save(QC/'ground_seam_position_2x.png')
# Exactly the same actors, at integer positions and natural size, on both backgrounds.
placements=[('tombstone_upright_01',(46,122)),('rubble_pile_01',(198,127))]
hero=(128,128)
def composite(ground):
 canvas=ground.copy().convert('RGBA')
 for name,(x,y) in placements:
  base=Image.open(REPO/'art/cemetery_v3/props'/f'{name}_base.png').convert('RGBA')
  canvas.alpha_composite(base,(x-base.width//2,y-base.height))
 objects=[]
 for name,foot in placements:
  obj=Image.open(REPO/'art/cemetery_v3/props'/f'{name}.png').convert('RGBA');objects.append((foot[1],foot,obj))
 obj=Image.open(REPO/'art/character_design/hero_B1_front_straight.png').convert('RGBA');objects.append((hero[1],hero,obj))
 for _,(x,y),obj in sorted(objects,key=lambda o:o[0]):canvas.alpha_composite(obj,(x-obj.width//2,y-obj.height))
 return canvas
original=composite(ONE)
original.resize((480,270),NEAR).save(QC/'ground_trial_with_props_2x.png')
a=np.array(original);a[:,:,:3]=np.rint(a[:,:,:3]*np.array([.80,.84,.92])).astype('uint8')
Image.fromarray(a).resize((480,270),NEAR).save(QC/'ground_trial_with_props_tinted_2x.png')
old=Image.open(REPO/'art/cemetery_pixel_v1/plates/ground_plate_960x540.png').convert('RGBA').crop((80,340,320,475))
comparison=Image.new('RGBA',(480,135));comparison.alpha_composite(composite(old));comparison.alpha_composite(original,(240,0))
comparison.resize((960,270),NEAR).save(QC/'ground_compare_2x.png')
# Detail crop and hero on plain dark background, at equal 6x native pixels.
panel=Image.new('RGBA',(200,108),(28,26,23,255))
panel.alpha_composite(ONE.crop((103,29,199,125)),(0,6))
h=Image.open(REPO/'art/character_design/hero_B1_front_straight.png').convert('RGBA');panel.alpha_composite(h,(104,6))
panel.resize((1200,648),NEAR).save(QC/'ground_trial_vs_hero_6x.png')
# Before/after color consolidation, identical source crop and placement.
before=Image.open(ROOT/'source/04_native_crop_240x135.png').convert('RGBA')
pair=Image.new('RGBA',(480,135));pair.alpha_composite(before);pair.alpha_composite(ONE,(240,0));pair.resize((960,270),NEAR).save(QC/'mud_cleanup_before_after_2x.png')
a=np.array(seam).astype(int)[:,:,:3]
jump=np.abs(a[:,240]-a[:,239]).mean(axis=1)
near=np.concatenate([np.abs(a[:,x+1]-a[:,x]).mean(axis=1) for x in list(range(220,238))+list(range(241,259))])
stats={'seam_x':240,'seam_mean_absolute_rgb_jump':round(float(jump.mean()),2),'nearby_internal_boundaries_mean_absolute_rgb_jump':round(float(near.mean()),2),'note':'RGB jump is diagnostic only, not a seam acceptance criterion. No boundary pixels copied, blended, shifted or retouched.','placements_bottom_center':placements,'hero_bottom_center':hero,'old_crop_xyxy':[80,340,320,475],'tint':[.80,.84,.92]}
(QC/'assembly_metadata.json').write_text(json.dumps(stats,indent=2)+'\n')
print(stats)
