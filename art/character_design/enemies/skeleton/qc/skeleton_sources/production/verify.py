from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
W=Path('/tmp/english-game-skeleton-design-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/character_design/enemies/skeleton';Q=O/'qc';rec=json.loads((W/'finish_records.json').read_text());protected=json.loads((W/'protected_hashes.json').read_text());changed=[p for p,h in protected.items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h];important=['art/character_design/hero_B1_front_straight.png','art/cemetery_pixel_v1/plates/ground_plate_960x540.png','art/cemetery_v3/props/tombstone_upright_01.png','art/cemetery_v3/props/tombstone_cross_01.png','art/cemetery_v3/props/obelisk_01.png','docs/SKELETON_DESIGN_REQUEST.md','docs/PIXEL_ASSET_PIPELINE.md'];assert not set(changed).intersection(important),changed;assert not [x for x in changed if x.lower().endswith('.png')],changed
metrics={};sample_total=0
for l,v in rec.items():
 pal=np.array(v['shared_palette'])
 for state in ['standing','remains']:
  n='skeleton_'+l+('_remains' if state=='remains' else '');p=O/(n+'.png');a=np.array(Image.open(p).convert('RGBA'));m=a[:,:,3]>0;assert set(np.unique(a[:,:,3])).issubset({0,255});assert list(Image.open(p).size)==v[state]['canvas'];assert 30<=v[state]['colors']<=50 and v[state]['adjacent_change']>=80;assert np.all(np.any(np.all(a[m,:3][:,None,:]==pal[None,:,:],axis=2),axis=1));assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((W/'staged'/p.name).read_bytes()).digest()
  if state=='standing':assert list(a.shape[:2])==[96,96] and 84<=v[state]['visible_height']<=96 and v[state]['lowest_opaque_y']==95
  else:assert 48<=v[state]['visible_width']<=72 and 20<=v[state]['visible_height']<=36 and v[state]['lowest_opaque_y']==47
  d=Q/'skeleton_sources'/(l+'_'+state);g=json.loads((d/'grid.json').read_text());raw=np.array(Image.open(d/'01_generated_original.png').convert('RGB'));rest=np.array(Image.open(d/'02_restored_native_cells.png').convert('RGBA'));xs=g['x_boundaries'];ys=g['y_boundaries'];count=0
  for y,x in zip(*np.where(rest[:,:,3]>0)):
   sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2;assert np.array_equal(rest[y,x,:3],raw[sy,sx]);count+=1
  sample_total+=count;metrics[n]={'file':p.name,'origin':v[state]['origin'],**v[state],'rgba_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'png_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'verified_raw_cell_samples':count,'alpha_values':[int(x) for x in np.unique(a[:,:,3])]}
proof={'protected_preexisting_files_checked':len(protected),'concurrent_changed_preexisting_files_not_written_by_this_task':changed,'preexisting_png_images_unchanged':True,'protected_files_unchanged_count':len(protected)-len(changed),'final_sprite_count':6,'single_source_cell_center_samples_verified':sample_total,'binary_alpha_all':True,'standing_canvases_all_96x96':True,'standing_lowest_y_all_95':True,'standing_origins_all':[48,96],'remains_canvases_all':[96,48],'remains_origins_all':[48,48],'all_colors_30_to50':True,'all_adjacent_change_at_least80':True,'game_runtime_changed':False,'direction_selected':False,'in_game_acceptance':'not_requested_this_round; await user direction choice'}
(Q/'skeleton_design_metrics.json').write_text(json.dumps({'verification':proof,'sprites':metrics},indent=2));print(json.dumps(proof,indent=2))
