from pathlib import Path
from PIL import Image
import numpy as np,json,zipfile,sys
S=Path(__file__).resolve().parent;B=S.parent;sys.path.insert(0,str(S))
from assemble_base import fill
pal=np.array(json.loads((S/'02_cleanup_metadata.json').read_text())['palette'],dtype=int)
newpal=np.rint(np.array([46,51,49])+.45*(pal-np.array([55,58,52]))).clip(0,255).astype('uint8')
outs=[]
with zipfile.ZipFile(B/'qc/backups/base_before_contrast_adjust.zip') as z:
 for i in [1,2]:
  im=Image.open(z.open(f'ground_base_{i:02d}.png')).convert('RGB');a=np.array(im)
  lab=np.argmin(((a[:,:,None,:].astype(int)-pal[None,None,:,:])**2).sum(3),axis=2)
  out=newpal[lab];outs.append(out);Image.fromarray(out).convert('RGBA').save(B/f'ground_base_{i:02d}.png')
fill(outs,'base_fill_2x.png');fill(outs[:1],'base_01_only_fill_2x.png')
(S/'09_final_palette.json').write_text(json.dumps({'original_palette':pal.tolist(),'final_palette':newpal.tolist(),'mapping':'One-to-one material color replacement: center(46,51,49)+0.45*(source-(55,58,52)), integer rounding. No geometry/texture generation, filtering, blur or resampling. Darkens and reduces foreground-like highlight contrast while retaining nuanced40-color hue ramps.','actual_palette_count':len(np.unique(newpal,axis=0))},indent=2)+'\n')
print('Palette',len(np.unique(newpal,axis=0)))
