from pathlib import Path
from PIL import Image
import json,shutil,hashlib,subprocess,sys,numpy as np
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-entry-pillar-20261026');O=R/'art/cemetery_v3/props';S=W/'staged';Q=O/'qc';D=Q/'entry_gate_sources';D.mkdir(parents=True,exist_ok=False);P=D/'production';P.mkdir()
protected=json.loads((W/'protected.json').read_text());assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in protected.items())
for p in S.rglob('*'):
 if not p.is_file():continue
 dest=O/p.relative_to(S);assert not dest.exists(),str(dest);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
g=json.loads((W/'generation.json').read_text());shutil.copy2(g['source'],D/'01_generated_original.png');shutil.copy2(W/'restored.png',D/'02_restored_native_cells.png');shutil.copy2(W/'combined.png',D/'03_final_native_with_base.png');shutil.copy2(W/'combined_6x.png',D/'04_final_6x.png');shutil.copy2(W/'grid_check_1x.png',D/'grid_check_1x.png')
for f in ['grid.json','cleanup.json','assembly.json','generation.json','prompts.json']:shutil.copy2(W/f,D/f)
for f in ['recover.py','finish.py','qc.py','publish.py','protected.json']:shutil.copy2(W/f,P/f)
(P/'README.md').write_text('Production provenance. Scripts retain historical work directory /tmp/english-game-entry-pillar-20261026; working archive is recoverable in ~/.Trash/english-game-entry-pillar-working-20261026. Adapt paths and use a new staging directory to rerun; do not overwrite approved outputs. Source cell center recovery and native row/column selection are recorded in grid.json / cleanup.json. No resize, rotation or mirroring used for delivered sprites.\n')
# Only existing file changed is manifest; back it up before adding one new item.
mf=O/'props_manifest.json';backup=Q/'backups/entry_gate_before_20261026';backup.mkdir(parents=True,exist_ok=False);shutil.copy2(mf,backup/'props_manifest.json');m=json.loads(mf.read_text());assert 'gate_pillar_tall_01' not in m['items'];m['items']['gate_pillar_tall_01']={'prop':'gate_pillar_tall_01.png','base':'gate_pillar_tall_01_base.png','canvas':[96,192],'origin':[48,192],'visible_height_px':161,'family':'B_ashlar','parent_material':'wall_pillar_01 / low_wall_ashlar_02','palette_parent':'wall_pillar_01','join':{'gate_center_spacing':144,'minimum_stone_clear_gap_px':92,'fence_endpoint_columns':[12,143],'assembly':'qc/entry_gate_assembly_2x.png'},'source_record':'qc/entry_gate_sources/generation.json','qa':'qc/entry_props_QA.md','status':'awaiting_in_game_acceptance'};mf.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
# Checker on actual final deliverables.
z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),str(O/'gate_pillar_tall_01.png'),str(O/'gate_pillar_tall_01_base.png')],capture_output=True,text=True);(Q/'entry_gate_pixel_check.txt').write_text(z.stdout);assert z.returncode==0
metrics={}
for n in ['gate_pillar_tall_01','gate_pillar_tall_01_base']:
 im=Image.open(O/(n+'.png')).convert('RGBA');a=np.array(im);fg=a[:,:,3]>0;v=fg[:,:-1]&fg[:,1:];metrics[n]={'canvas':list(im.size),'bbox_exclusive':list(im.getbbox()),'origin':[48,192],'colors':len(np.unique(a[fg,:3],axis=0)),'neighbor_pairs':int(v.sum()),'changed_pairs':int(((a[:,:-1,:3]!=a[:,1:,:3]).any(2)&v).sum()),'adjacent_change_pct':float(100*((a[:,:-1,:3]!=a[:,1:,:3]).any(2)&v).sum()/v.sum()),'alpha_values':[int(x) for x in np.unique(a[:,:,3])],'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest()}
changed=[p for p,v in protected.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=v];assert changed==[str(mf)],changed
old=json.loads((backup/'props_manifest.json').read_text());new=json.loads(mf.read_text());new['items'].pop('gate_pillar_tall_01');assert new==old
metrics['protection']={'checked_preexisting_files':len(protected),'unchanged':len(protected)-1,'sole_authorized_change':'props_manifest.json: append one new item; previous entries identical','backup':str(backup/'props_manifest.json')};metrics['assembly']=json.loads((W/'assembly.json').read_text());(Q/'entry_gate_metrics.json').write_text(json.dumps(metrics,indent=2));print(z.stdout);print('protected',len(protected),'unchanged',len(protected)-1)
