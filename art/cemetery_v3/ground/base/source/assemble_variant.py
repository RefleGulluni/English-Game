from pathlib import Path
from PIL import Image
import numpy as np,json,sys
S=Path(__file__).resolve().parent;B=S.parent;sys.path.insert(0,str(S))
from assemble_base import registered_cells,quiet,cut_path,fill
pal=json.loads((S/'02_cleanup_metadata.json').read_text())['palette']
cells=registered_cells(S/'07_variant_generated.png','07')
e=quiet(cells,pal);old=np.array(Image.open(B/'ground_base_01.png').convert('RGB'))
err=((old.astype(float)-e.astype(float))**2).mean(2)
l=cut_path(err[:,8:33])+8;r=cut_path(err[:,191:216])+191
t=cut_path(err[8:25,:].T)+8;b=cut_path(err[103:120,:].T)+103
yy,xx=np.indices((128,224));mask=(xx>=l[:,None])&(xx<=r[:,None])&(yy>=t[None,:])&(yy<=b[None,:])
out=old.copy();out[mask]=e[mask]
assert np.array_equal(out[0],old[0]) and np.array_equal(out[-1],old[-1])
assert np.array_equal(out[:,0],old[:,0]) and np.array_equal(out[:,-1],old[:,-1])
Image.fromarray(out).convert('RGBA').save(B/'ground_base_02.png')
Image.fromarray((mask*255).astype('uint8')).save(S/'08_variant_selection_mask.png')
ids=fill([old,out],'base_fill_2x.png')
(S/'08_variant_assembly.json').write_text(json.dumps({'same_four_edges_exact':True,'same_outer8px_exact':bool(np.array_equal(out[:8],old[:8]) and np.array_equal(out[-8:],old[-8:]) and np.array_equal(out[:,:8],old[:,:8]) and np.array_equal(out[:,-8:],old[:,-8:])),'changed_pixel_count':int(np.any(old!=out,axis=2).sum()),'mask_pixels':int(mask.sum()),'random_seed':1048,'random_ids':ids,'method':'AI interior variation, paired40color palette and directed cleanup, irregular integer min-error perimeter cuts, original margins retained. No flips/rotations/resize.'},indent=2)+'\n')
print('Variant colors',len(np.unique(out.reshape(-1,3),axis=0)),'changed',np.any(old!=out,axis=2).sum())
