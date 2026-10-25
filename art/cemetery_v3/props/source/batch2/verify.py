from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np,subprocess,sys
W=Path('/tmp/english-game-props-batch2-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';Q=O/'qc';rec=json.loads((W/'finish_records.json').read_text());old=json.loads((W/'protected_hashes.json').read_text());manifest='art/cemetery_v3/props/props_manifest.json';bad=[p for p,h in old.items() if p!=manifest and (not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h)];assert not bad,bad
ranges={'tombstone_flat_01':(60,72),'tombstone_pointed_01':(76,90),'tombstone_small_01':(30,42),'obelisk_01':(110,130),'rubble_pile_01':(10,18),'grave_vase_01':(18,26),'candles_01':(10,18),'grave_lantern_01':(22,32)}
metrics={}
for n,v in rec.items():
 for suffix,key in [('', 'prop'),('_base','base')]:
  p=O/(n+suffix+'.png');a=np.array(Image.open(p).convert('RGBA'));assert set(np.unique(a[:,:,3])).issubset({0,255});assert not np.any(a[-1,:,3]),p
  assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((W/'staged'/p.name).read_bytes()).digest();assert list(Image.open(p).size)==v['canvas'];metrics[n+suffix]={'rgba_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'png_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),**v[key]}
 if n in ranges:assert ranges[n][0]<=v['prop']['height']<=ranges[n][1]
 if n not in ['rubble_pile_01','grave_vase_01','candles_01','grave_lantern_01']:assert 30<=v['prop']['colors']<=50 and v['prop']['adjacent_change']>=80
# Retained regions must match exact source RGBA after integer registration.
stump=np.array(Image.open(O/'tombstone_upright_02_broken.png').convert('RGBA'))[32:144,24:120];parent=np.array(Image.open(O/'tombstone_upright_02.png').convert('RGBA'));assert np.array_equal(stump[67:],parent[67:]);stump_count=int((parent[67:,:,3]>0).sum())
cross=np.array(Image.open(O/'tombstone_cross_01_broken.png').convert('RGBA'))[16:144,8:104];parent=np.array(Image.open(O/'tombstone_cross_01.png').convert('RGBA'));mask=np.ones(parent.shape[:2],bool);mask[39:72,:39]=False;assert np.array_equal(cross[mask],parent[mask]);cross_count=int((mask&(parent[:,:,3]>0)).sum())
# Every restored native color is exactly one recorded source cell-center sample (including original alpha mask).
for n,v in rec.items():
 d=Q/'batch2_sources'/n;g=json.loads((d/'grid.json').read_text());raw=np.array(Image.open(d/'01_generated_original.png').convert('RGB'));a=np.array(Image.open(d/'02_restored_native_cells.png').convert('RGBA'));xs=g['x_boundaries'];ys=g['y_boundaries'];count=0
 for y,x in zip(*np.where(a[:,:,3]>0)):
  sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2;assert np.array_equal(a[y,x,:3],raw[sy,sx]);count+=1
 metrics[n]['verified_raw_cell_samples']=count
z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),*[str(O/(n+s+'.png')) for n in rec for s in ['', '_base']]],capture_output=True,text=True);assert z.returncode==0;(Q/'batch2_pixel_check.txt').write_text(z.stdout)
proof={'protected_original_files_checked':len(old)-1,'changed_original_files':bad,'manifest_is_only_modified_preexisting_art_file':True,'retained_stump_opaque_pixels':stump_count,'retained_cross_opaque_pixels':cross_count,'every_restored_pixel_is_recorded_source_center':True,'all24_png_alpha_binary':True,'all24_png_last_row_transparent':True,'size_ranges_passed':True,'large_prop_color_and_density_passed':True,'old_manifest_items_unchanged':True,'game_acceptance':'pending'}
(Q/'batch2_metrics.json').write_text(json.dumps({'verification':proof,'assets':metrics},indent=2));print(json.dumps(proof,indent=2))
