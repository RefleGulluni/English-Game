from pathlib import Path
from PIL import Image
import numpy as np,json,zipfile
T=Path(__file__).resolve().parents[1];G=T.parent;R=T.parents[3];Q=T/'qc'
NEAR=Image.Resampling.NEAREST
# Restore archived previews as visible evidence without altering the archives.
for index in [1,2]:
 with zipfile.ZipFile(Q/'backups'/f'mud_attempt{index:02d}.zip') as z:
  im=Image.open(z.open('qc/tiles_random_fill_2x.png')).convert('RGBA')
  im.save(Q/f'tiles_random_fill_attempt{index:02d}_2x.png')
current=Image.open(Q/'tiles_random_fill_2x.png').convert('RGBA')
# Same seed, same tile identities for the three attempts. Overview is a native crop,
# then integer2x; no whole-screen downsampling hides defects.
comp=Image.new('RGBA',(1440,540))
for i,n in enumerate(['tiles_random_fill_attempt01_2x.png','tiles_random_fill_attempt02_2x.png','tiles_random_fill_2x.png']):
 im=Image.open(Q/n).convert('RGBA')
 comp.alpha_composite(im.crop((0,0,480,540)),(i*480,0))
comp.save(Q/'mud_attempts_detail_comparison_2x.png')
# Only a color/context proof, explicitly not the uncompleted test-area deliverable.
new=current.crop((0,0,480,270))
# Get native values by selecting one point from each known2x repeated cell.
# This is QC-layout extraction, not a runtime artwork conversion.
a=np.array(new);new=Image.fromarray(a[::2,::2])
old=Image.open(G/'trial/ground_trial_01.png').convert('RGBA')
placements=[('tombstone_upright_01',(46,122)),('rubble_pile_01',(198,127))]
def decorate(bg):
 out=bg.copy()
 for n,(x,y) in placements:
  im=Image.open(R/'art/cemetery_v3/props'/f'{n}_base.png').convert('RGBA');out.alpha_composite(im,(x-im.width//2,y-im.height))
 for n,(x,y) in placements:
  im=Image.open(R/'art/cemetery_v3/props'/f'{n}.png').convert('RGBA');out.alpha_composite(im,(x-im.width//2,y-im.height))
 im=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');out.alpha_composite(im,(128-im.width//2,128-im.height))
 return out
panel=Image.new('RGBA',(480,135));panel.alpha_composite(decorate(old));panel.alpha_composite(decorate(new),(240,0));panel.resize((960,270),NEAR).save(Q/'mud_only_vs_trial_2x.png')
decorate(new).resize((480,270),NEAR).save(Q/'mud_only_with_hero_2x.png')
# Ordered-pair contact sheets; edges are intentionally unmarked.
tiles=[Image.open(T/f'ground_mud_{i:02d}.png').convert('RGBA') for i in range(1,9)]
h=Image.new('RGBA',(512,256));v=Image.new('RGBA',(256,512))
for i,a in enumerate(tiles):
 for j,b in enumerate(tiles):
  h.alpha_composite(a,(j*64,i*32));h.alpha_composite(b,(j*64+32,i*32))
  v.alpha_composite(a,(j*32,i*64));v.alpha_composite(b,(j*32,i*64+32))
h.resize((1024,512),NEAR).save(Q/'mud_all_pairs_horizontal_2x.png');v.resize((512,1024),NEAR).save(Q/'mud_all_pairs_vertical_2x.png')
colors=set();checks=[]
for i,im in enumerate(tiles):
 a=np.array(im);cs=set(map(tuple,a[:,:,:3].reshape(-1,3)));colors|=cs
 checks.append({'file':f'ground_mud_{i+1:02d}.png','size':list(im.size),'alpha':np.unique(a[:,:,3]).tolist(),'colors':len(cs)})
meta={'status':'BLOCKED_VISUAL_SELF_QA_NOT_FULL_SET','runtime_unique_colors':len(colors),'tile_checks':checks,'missing':['16 corner transitions+JSON','3 full-path variations','6-8 decals','complete480x270 test area'],'context_preview':'mud_only_vs_trial_2x.png is old240x135 and new240x135 native side by side, same existing hero/props, no scale change. It is not the requested full test-area comparison.','edge_limit_note':'MaxRGB jump<=20 is just the color-ramp range, not proof of seamlessness. Original source crops have overlapping strips in attempt02/03, never identical tiles.'}
(Q/'blocked_verification.json').write_text(json.dumps(meta,indent=2)+'\n')
print('Current runtime palette:',len(colors),'colors',sorted(colors))
