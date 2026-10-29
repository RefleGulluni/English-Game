from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np,colorsys,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');D=R/'art/character_design/enemies/skeleton/anim';W=Path('/tmp/english-fx-brighter-20261029');O=W/'staged';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();protected=json.loads((W/'protected.json').read_text());results=json.loads((W/'results.json').read_text());files={str(p.relative_to(O)):p for p in O.rglob('*') if p.is_file()};overwritten=[rel for rel in files if rel in protected];backup=D/'qc/backups/before_combat_fx_brightening_20261029'
# Last frames remain the same all-zero PNG, so are correctly byte-identical despite being copied.
changed=[rel for rel,h in protected.items() if not (D/rel).exists() or sha(D/rel)!=h]
assert set(changed)==set(overwritten)-{'frames/fx_bone_dust/06.png','frames/fx_shroud_threads/06.png'}
for rel,p in files.items():assert sha(D/rel)==sha(p)
for rel in overwritten+['timing.json']:assert sha(backup/rel)==protected[rel]
code=(W/'publish.py').read_text();tail=code[code.index("assert sha(D/'timing.json')"):];exec(tail)
shutil.copy2(W/'finish_verify.py',D/'qc/combat_fx_brightening_sources/finish_verify.py')
print('All published GIF/frame/strip pixels, unchanged timing, protected files, and recoverable backups verified.')
