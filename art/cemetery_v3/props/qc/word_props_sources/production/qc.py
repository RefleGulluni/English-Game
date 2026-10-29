from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,shutil,hashlib,importlib.util
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/Users/mac/.codex/work/cemetery-word-props-20261029');O=W/'staged';Q=O/'qc';S=Q/'word_props_sources';P=R/'art/cemetery_v3/props'
ns=['raven_ground_01','tombstone_raven_01','tombstone_mossy_01','grave_bell_01','bell_frame_01','crypt_sealed_01','old_well_01','fresh_grave_mound_01'];rec=json.loads((S/'cleanup_index.json').read_text())
# Make selected raw sources obvious; archive superseded initial drafts, do not
# label an abandoned high-resolution draft as the selected native source.
for n in ns:
 d=S/n;d.mkdir(exist_ok=True);src=rec[n].get('source')
 if src and d!=S/src:
  initial=d/'unused_initial';initial.mkdir(exist_ok=True)
  for fn in ['01_generated_original.png','02_restored_cells.png','grid.json','grid_check_1x.png','generation.json']:
   if (d/fn).exists() and not(initial/fn).exists():shutil.copy2(d/fn,initial/fn)
   shutil.copy2(S/src/fn,d/fn)
 if n=='tombstone_raven_01':
  shutil.copy2(P/'tombstone_upright_01.png',d/'01_parent_stone.png');shutil.copy2(P/'tombstone_upright_01_base.png',d/'01_parent_base.png');shutil.copy2(S/'raven_final/01_generated_original.png',d/'01_generated_original_raven.png');shutil.copy2(S/'raven_final/02_restored_cells.png',d/'02_restored_raven.png');shutil.copy2(S/'raven_final/grid.json',d/'grid_raven.json')
 if n=='fresh_grave_mound_01':
  for fn in ['01_generated_original.png','02_restored_cells.png','grid.json','grid_check_1x.png']:
   shutil.copy2(S/'mound_final'/fn,d/('mound_'+fn))
# Retain source scripts/prompts and the actual style references as audit data.
production=S/'production';production.mkdir(exist_ok=True)
for f in ['recover.py','finish.py','qc.py','before.json']:shutil.copy2(W/f,production/f)
shutil.copytree(W/'refs',S/'references',dirs_exist_ok=True)
for f in W.glob('generation_*.json'):shutil.copy2(f,production/f.name)
# Final pixel metrics of the DELIVERY PNGs.
spec=importlib.util.spec_from_file_location('pixel_check',R/'scripts/tools/pixel_check.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);stats={}
for n in ns:
 stats[n]={}
 for suffix in ['', '_base']:
  p=O/(n+suffix+'.png');a=np.array(Image.open(p).convert('RGBA'));m=mod.measure(p);assert m['alpha_ok'] and not m['cyan'];assert not a[a[:,:,3]==0].any();stats[n]['prop' if not suffix else 'base']={**m,'png_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bbox':Image.open(p).getbbox()}
 # Same shared anchor and canvas, do not trim runtime assets.
 assert Image.open(O/(n+'.png')).size==Image.open(O/(n+'_base.png')).size
 stats[n]['canvas']=rec[n]['canvas'];stats[n]['origin']=rec[n]['origin'];stats[n]['visible_height_px']=rec[n]['visible_height'];stats[n]['source']=rec[n].get('source',rec[n].get('parent'));stats[n]['no_scale_rotation_mirror']=True
(Q/'word_props_metrics.json').write_text(json.dumps(stats,indent=2))
ground=Image.open(R/'art/cemetery_v3/ground/base/ground_base_01.png').convert('RGBA');hero=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');skel=Image.open(R/'art/character_design/enemies/skeleton/skeleton_B.png').convert('RGBA')
def background(size):
 b=Image.new('RGBA',size)
 for y in range(0,size[1],ground.height):
  for x in range(0,size[0],ground.width):b.paste(ground,(x,y))
 return b

def at(b,im,root):b.alpha_composite(im,(root[0]-im.width//2,root[1]-im.height))
def prop(b,n,root,src=O,layer='both'):
 if layer in ['base','both']:at(b,Image.open(src/(n+'_base.png')).convert('RGBA'),root)
 if layer in ['body','both']:at(b,Image.open(src/(n+'.png')).convert('RGBA'),root)
# One native-pixel row with actual anchors and familiar96px actors.
width=sum(rec[n]['canvas'][0]+24 for n in ns)+240;line=background((width,240));roots=[];x=20
for n in ns:
 cw,ch=rec[n]['canvas'];root=(x+cw//2,202);roots.append((n,root));prop(line,n,root);x+=cw+24
at(line,hero,(x+35,202));at(line,skel,(x+120,202));d=ImageDraw.Draw(line)
for n,root in roots:d.text((root[0]-len(n)*3,218),n,fill='#d6cbb7')
d.text((x+15,218),'HERO',fill='#d6cbb7');d.text((x+100,218),'SKELETON',fill='#d6cbb7');line.save(Q/'word_props_lineup_1x.png');line.resize((width*2,480),Image.Resampling.NEAREST).save(Q/'word_props_lineup_2x.png')
# Per-item compare at1x/6x, no global fitting of individual assets.
for n in ns:
 cw,ch=rec[n]['canvas'];width=cw+170;h=max(ch,96)+42;b=background((width,h));root=(cw//2+8,h-26);prop(b,n,root);at(b,hero,(cw+60,h-26));d=ImageDraw.Draw(b);d.text((6,h-17),n,fill='#d6cbb7');d.text((cw+40,h-17),'HERO B1',fill='#d6cbb7');b.save(Q/(n+'_vs_hero_1x.png'));b.resize((width*6,h*6),Image.Resampling.NEAREST).save(Q/(n+'_vs_hero_6x.png'))
# A world-feeling QC arrangement, not a new game room or scene modification.
b=background((960,540));placements=[('dead_tree_02',(130,290),P),('fountain_dry_01',(380,320),P),('tombstone_upright_02',(780,290),P),('tombstone_mossy_01',(225,366),O),('grave_bell_01',(520,380),O),('old_well_01',(680,403),O),('raven_ground_01',(370,410),O)]
for n,root,src in placements:prop(b,n,root,src,'base')
for n,root,src in sorted(placements,key=lambda t:t[1][1]):prop(b,n,root,src,'body')
at(b,hero,(445,445));at(b,skel,(540,450));b.save(Q/'word_props_with_entry_1x.png');b.resize((1920,1080),Image.Resampling.NEAREST).save(Q/'word_props_with_entry_2x.png')
(Q/'word_props_qc_layout.json').write_text(json.dumps({'lineup_roots':roots,'entry_scene_roots':[[n,list(root),'new' if src==O else 'accepted'] for n,root,src in placements],'ground':'art/cemetery_v3/ground/base/ground_base_01.png','integer_translation_only':True,'no_runtime_scene_modified':True},indent=2))
print(json.dumps({n:{'height':stats[n]['visible_height_px'],'colors':stats[n]['prop']['colors'],'change':stats[n]['prop']['change'],'base_colors':stats[n]['base']['colors'],'base_change':stats[n]['base']['change']} for n in ns},indent=2))
