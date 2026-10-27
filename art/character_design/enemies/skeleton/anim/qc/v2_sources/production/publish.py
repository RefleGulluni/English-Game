from pathlib import Path
import json,hashlib,shutil,subprocess,sys
W=Path('/tmp/english-game-skeleton-v2-20261027');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');A=R/'art/character_design/enemies/skeleton/anim';O=W/'staged';Q=O/'qc';protected=json.loads((W/'protected.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert all(Path(p).exists() and sha(p)==h for p,h in protected.items())
p=Q/'skeleton_B_anim_v2_QA.md';p.write_text(p.read_text().replace('镁红去底','品红去底'))
# Refuse overwriting any earlier V2 asset; this publication adds new paths only.
files=[p for p in O.rglob('*') if p.is_file()]
assert all(not (A/p.relative_to(O)).exists() for p in files)
old=json.loads((A/'timing.json').read_text());new=json.loads((W/'new_timing.json').read_text());assert len(old['animations'])==15 and not set(old['animations'])&set(new)
backup=A/'qc/backups/before_v2_20261027/timing.json';assert not backup.exists();backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(A/'timing.json',backup)
merged=json.loads(json.dumps(old))
for n,t in new.items():
 base=old['animations'][n.removesuffix('_v2')].copy();base.update(t)
 if 'reassemble' in n:base['hold_last_frame']=True
 merged['animations'][n]=base
for src in files:
 dest=A/src.relative_to(O);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
(A/'timing.json').write_text(json.dumps(merged,ensure_ascii=False,indent=2)+'\n')
assert len(json.loads((A/'timing.json').read_text())['animations'])==28
assert all(merged['animations'][k]==v for k,v in old['animations'].items())
assert sha(backup)==protected[str(A/'timing.json')]
changed=[p for p,h in protected.items() if sha(p)!=h];assert changed==[str(A/'timing.json')],changed
checks=A/'qc/skeleton_B_anim_v2_verification.json';v=json.loads(checks.read_text());v['_publication']={'new_actions':13,'new_frames':96,'all_old_animation_entries_unchanged':True,'old_files_count':len(protected),'only_existing_file_modified':'anim/timing.json','timing_backup':'qc/backups/before_v2_20261027/timing.json','backup_matches_original_sha256':True,'all_other_649_preexisting_files_unchanged':True};checks.write_text(json.dumps(v,indent=2))
paths=sorted(p for n in new for p in (A/'frames'/n).glob('*.png'));z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1.png'),*map(str,paths)],text=True,capture_output=True);assert z.returncode==0;(A/'qc/skeleton_B_anim_v2_pixel_check.txt').write_text(z.stdout+z.stderr)
# Human-review entry points and manifest live with the final assets.
manifest={str(p.relative_to(A)):sha(p) for p in A.rglob('*') if p.is_file() and ('_v2' in str(p.relative_to(A)) or 'v2_sources' in str(p.relative_to(A)))};(A/'qc/skeleton_B_anim_v2_manifest.json').write_text(json.dumps(manifest,indent=2))
print('PUBLISHED',len(files),'new files;',len(manifest),'manifest entries; 13 new animations / 96 frames; 649 prior files unchanged, timing backed up and appended only.')
