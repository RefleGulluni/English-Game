"""Remove residual chroma spill on generated cutout edges; no painted replacement."""
from pathlib import Path
from PIL import Image
import numpy as np, json, shutil
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'art_source/production/broken_graveyard_p01'
records=[]
for folder in ['enemies/skeleton_parts','environments/textures','loot/textures','characters/textures']:
    for p in (ROOT/'art'/folder).glob('*.png'):
        if p.name=='ground.png': continue
        image=Image.open(p).convert('RGBA')
        a=np.array(image,dtype=np.float32)
        spill=np.minimum(a[:,:,0],a[:,:,2])-a[:,:,1]
        affected=(spill>22)&(a[:,:,3]>0)
        a[:,:,3][affected]*=np.clip(1-(spill[affected]-18)/55,0,1)
        a[:,:,2][affected]=np.minimum(a[:,:,2][affected],a[:,:,1][affected]+9)
        a[:,:,0][affected]=np.minimum(a[:,:,0][affected],a[:,:,1][affected]*1.3+10)
        cleaned=Image.fromarray(np.clip(a,0,255).astype('uint8'))
        cleaned=cleaned.crop(cleaned.getbbox())
        padded=Image.new('RGBA',(cleaned.width+4,cleaned.height+4))
        padded.alpha_composite(cleaned,(2,2))
        padded.save(p)
        # Transparent border is an actual alpha channel, not a checkerboard.
        records.append(dict(file=str(p.relative_to(ROOT)),spill_pixels=int(affected.sum()),transparent_pixels=int((np.array(padded)[:,:,3]==0).sum()),source_width=image.width,source_height=image.height,export_width=padded.width,export_height=padded.height))
        config=p.with_suffix('.png.import')
        if config.exists():
            backup=SOURCE/'qc/import_defaults'/config.name
            backup.parent.mkdir(parents=True,exist_ok=True)
            if not backup.exists(): shutil.copy2(config,backup)
            config.write_text(config.read_text().replace('mipmaps/generate=false','mipmaps/generate=true'))
(SOURCE/'qc/alpha_refinement.json').write_text(json.dumps(records,indent=2)+'\n')
print(len(records),'cutouts alpha-refined; linear mipmap import enabled.')
