"""Convert fresh Godot premultiplied viewport captures to straight-alpha PNG.
Run exactly once immediately AFTER capture_sigil_assets.gd, before importing PNGs.
"""
from pathlib import Path
from PIL import Image
import numpy as np,json
ROOT=Path(__file__).resolve().parents[4];SRC=ROOT/'art_source/production/cemetery_kit_v1'
records=[]
for p in sorted((ROOT/'art/cemetery_kit_v1/ui').glob('*.png')):
    a=np.array(Image.open(p).convert('RGBA'),dtype=float);alpha=a[:,:,3]/255
    a[:,:,:3]=np.divide(a[:,:,:3],alpha[:,:,None],out=np.zeros_like(a[:,:,:3]),where=alpha[:,:,None]>0)
    Image.fromarray(np.clip(a,0,255).astype('uint8')).save(p)
    records.append({'file':str(p.relative_to(ROOT)),'pixels':[a.shape[1],a.shape[0]],'source':'Godot transparent SubViewport actual Control; unpremultiplied once','focus_cost':'not baked; native control owns geometry chambers'})
(SRC/'qc/ui_alpha.json').write_text(json.dumps(records,indent=2)+'\n')
print(len(records),'UI textures normalized to straight alpha')
