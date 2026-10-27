"""Publish only section7's4 replacements and10 additions; accepted art is locked."""
from pathlib import Path
import json,zipfile,hashlib,datetime
S=Path(__file__).resolve().parent;D=S.parents[1];G=D.parent;R=G.parents[2];Q=D/'qc'
protected=json.loads((S/'protected_accepted_assets.json').read_text())
assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in protected.items())
m=json.loads((S/'round2_manifest.json').read_text());assert len(m['assets'])==14
previous=D/'source/delivery_manifest.json'
with zipfile.ZipFile(Q/f'backups/before_publish_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.write(previous,'delivery_manifest.json');z.write(S/'round2_manifest.json','round2_manifest.json')
 for row in m['assets']:
  p=D/row['file']
  if p.exists():z.write(p,p.name)
for row in m['assets']:
 assert str((D/row['file']).relative_to(R)) not in protected
 (D/row['file']).write_bytes((S/row['cleaned']).read_bytes())
replaced={'decal_puddle_01.png','decal_puddle_02.png','decal_moss_01.png','decal_moss_02.png'}
original=json.loads(previous.read_text());retained=[row for row in original['decals'] if row['file'] not in {r['file'] for r in m['assets']}]
assert len(retained)==6
entries=[]
for row in m['assets']:
 n=dict(row)
 for key in ['source','prompt','grid','restored','cleaned']:n[key]='round2/'+n[key]
 n['visible_bbox_size']=n.pop('visible');n['status']='SECTION7_PENDING_IN_GAME_REVIEW';entries.append(n)
for row in retained:row['status']='ACCEPTED_UNCHANGED_BY_SECTION7'
data={'status':'BASE_AND6_DECALS_ACCEPTED;14_ROUND2_DECALS_PENDING_USER_REVIEW','decals':entries+retained,'replaced_files':sorted(replaced),'added_files':sorted(r['file'] for r in m['assets'] if r['file'] not in replaced),'accepted_unchanged_files':[r['file'] for r in retained],'round2_details':'round2/round2_manifest.json','source_mode':'Built-in image_gen; exact prompts per entry, observed source grid, native center samples, material cleanup. No API fallback.'}
previous.write_text(json.dumps(data,indent=2)+'\n')
m['status']='PUBLISHED_FOR_USER_IN_GAME_REVIEW';m['published_sha256']={r['file']:hashlib.sha256((D/r['file']).read_bytes()).hexdigest() for r in m['assets']}
(S/'round2_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in protected.items())
print('Published14; all accepted originals byte-identical; delivery manifest now20.')
