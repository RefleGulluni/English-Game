from pathlib import Path
from PIL import Image
import numpy as np,json,subprocess,sys
W=Path('/tmp/english-game-props-complete-20261025');S=W/'staged';R=Path('/Users/mac/Documents/GitHub.nosync/English-Game')
meta={}
# Full stone wall source-column crop and 2-column end cleanup, generated pixels only.
# Share an optimized material ramp between both generated walls; no new texture.
pa=np.array(Image.open(S/'low_wall_01.png'));pb=np.array(Image.open(S/'low_wall_broken_01.png'))
fg=np.concatenate([pa[pa[:,:,3]>0,:3],pb[pb[:,:,3]>0,:3]],axis=0)
q=Image.fromarray(fg.reshape(1,-1,3)).quantize(50,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
qp=np.array(q.getpalette(),dtype=np.uint8).reshape(-1,3);qp=qp[np.unique(np.array(q))].astype(int)
for nm,ar in [('low_wall_01',pa),('low_wall_broken_01',pb)]:
 for yy,xx in zip(*np.where(ar[:,:,3]>0)):
  rgb=ar[yy,xx,:3].astype(int);ar[yy,xx,:3]=qp[((qp-rgb)**2).sum(1).argmin()]
 Image.fromarray(ar).save(S/(nm+'.png'))
n='low_wall_01';a=np.array(Image.open(S/(n+'.png')));off=13;left=off+8;right=off+155;a[:,:left]=0;a[:,right+1:]=0;a[:,right]=a[:,left];a[:,right-1]=a[:,left+1];Image.fromarray(a).save(S/(n+'.png'));meta[n]={'stride':148,'canvas_core_x':[left,right],'endpoint_rgba_equal':bool(np.array_equal(a[:,left],a[:,right])),'method':'Trim generated terminal side faces, copy two native contour columns across end. No texture synthesis.'}
# Broken end joins the same complete-wall contour; map its stone ramp to that of wall.
n='low_wall_broken_01';b=np.array(Image.open(S/(n+'.png')));leftb=(176-149)//2+8;b[:,:leftb]=0;b[:,leftb]=a[:,left];b[:,leftb+1]=a[:,left+1];Image.fromarray(b).save(S/(n+'.png'));meta[n]={'left_join_x':leftb,'left_profile_rgba_equal_to_wall':bool(np.array_equal(b[:,leftb],a[:,left])),'method':'Use shared50-color wall-family ramp, copy two generated contour columns to match full-wall end; remainder unique broken source art.'}
# Iron rails need an unclipped repeated connector, equal alpha/RGB at both ends.
n='iron_fence_01';c=np.array(Image.open(S/(n+'.png')));off=(160-143)//2;lf=off+4;rt=off+135;c[:,:lf]=0;c[:,rt+1:]=0;c[:,rt]=c[:,lf];Image.fromarray(c).save(S/(n+'.png'));meta[n]={'stride':132,'canvas_core_x':[lf,rt],'endpoint_rgba_equal':bool(np.array_equal(c[:,lf],c[:,rt])),'method':'Trim terminal knobs, copy one generated native connector column. Six bars keep their world left/right lighting.'}
(W/'join_metadata.json').write_text(json.dumps(meta,indent=2))
# Invoke user's exact checker for each prop and each base, with accepted hero ref.
files=sorted(S.glob('*.png'));files=[p for p in files if not p.name.endswith('_combined_cells.png')]
cmd=[sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),*[str(p) for p in files]]
z=subprocess.run(cmd,capture_output=True,text=True);(W/'pixel_check_output.txt').write_text(z.stdout+z.stderr);print(z.stdout);assert z.returncode==0,z.stderr
