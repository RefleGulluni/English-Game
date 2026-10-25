from pathlib import Path
from PIL import Image
import json,shutil,hashlib,subprocess,sys,numpy as np
W=Path('/tmp/english-game-props-batch2-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';Q=O/'qc';D=Q/'batch2_sources';SRC=O/'source/batch2';D.mkdir(exist_ok=True);SRC.mkdir(exist_ok=True)
rec=json.loads((W/'finish_records.json').read_text());manifest=json.loads((O/'props_manifest.json').read_text());backup=Path('/Users/mac/.codex/backups/English-Game/before-props-batch2-20261025/props_manifest.json');assert backup.exists()
for n,v in rec.items():
 assert n not in manifest['items'],n
 for suffix in ['', '_base']:
  dest=O/(n+suffix+'.png');assert not dest.exists(),dest;shutil.copy2(W/'staged'/dest.name,dest)
 im=Image.open(O/(n+'.png'));assert im.size==tuple(v['canvas']);assert Image.open(O/(n+'_base.png')).size==im.size
 nv={'prop':n+'.png','base':n+'_base.png','canvas':v['canvas'],'origin':v['origin'],'visible_height_px':v['prop']['height'],'join':None,'native_edit':v.get('native_edit'),'batch':'cemetery_props_batch2','qa':'qc/batch2_QA.md'}
 if n=='grave_slab_01':nv['side_thickness_px']=[8,9];nv['required_side_thickness_px']=[6,12];nv['projection_bbox_height_px']=v['prop']['height'];nv['visible_height_px']=9
 if n in ['rubble_pile_01','grave_vase_01','candles_01','grave_lantern_01']:nv['collision']=False
 if n.endswith('_broken'):nv['ground_fragment_in_base']=True;nv['parent']=v['parent']
 if n.endswith('_tilted'):nv['lean_degrees']=v['lean_left_angle_degrees'];nv['digital_rotation_or_shear']=False
 manifest['items'][n]=nv
 d=D/n;d.mkdir(exist_ok=True);rawdir=W/'recovered'/v['source'];grid=json.loads((rawdir/'grid.json').read_text());raw=Path(grid['source']);shutil.copy2(raw,d/'01_generated_original.png');shutil.copy2(rawdir/'restored_native.png',d/'02_restored_native_cells.png');shutil.copy2(rawdir/'grid_check_1x.png',d/'grid_check_1x.png');grid['original_tool_path']=grid['source'];grid['source']='01_generated_original.png';(d/'grid.json').write_text(json.dumps(grid,indent=2))
 p=Image.open(O/(n+'.png')).convert('RGBA');b=Image.open(O/(n+'_base.png')).convert('RGBA');b.alpha_composite(p);b.save(d/'03_final_native_with_base.png');(d/'native_edit.json').write_text(json.dumps(v,indent=2));
 if 'parent' in v:
  shutil.copy2(O/(v['parent']+'.png'),d/'parent_original_prop.png');shutil.copy2(O/(v['parent']+'_base.png'),d/'parent_original_base.png')
 z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),str(O/(n+'.png')),str(O/(n+'_base.png'))],capture_output=True,text=True);assert z.returncode==0,z.stdout+z.stderr;(d/'pixel_check.txt').write_text(z.stdout)
files=[str(O/(n+s+'.png')) for n in rec for s in ['', '_base']];z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),*files],capture_output=True,text=True);assert z.returncode==0; (Q/'batch2_pixel_check.txt').write_text(z.stdout)
# Preserve prior item dictionaries byte-for-byte in meaning; add only new batch entries.
old=json.loads(backup.read_text());assert all(manifest['items'][k]==v for k,v in old['items'].items())
manifest['cemetery_props_batch2']={'items':list(rec),'count':12,'qc':'qc/batch2_QA.md','status':'awaiting_in_game_acceptance','production':'single built-in image generation / detected cell center sampling / native selections and integer translations / inherited stone palettes','no_whole_image_resize':True}
(O/'props_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for f in ['finish.py','recover_one.py','tilt_gate.py','generation.json','tilt_generation.json','regen.json','fragments.json','fragments3.json','finish_records.json','tilt_gate.json','protected_hashes.json']:
 shutil.copy2(W/f,SRC/f)
# Retain final native fragments too, for layer audit.
for f in ['upper_fragment_final_native.png','cross_fragment_final_native.png']:shutil.copy2(W/f,SRC/f)
print('Published12pairs; prior manifest items unchanged; checker passed24PNGs.')
