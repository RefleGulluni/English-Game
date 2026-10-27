from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,sys
REPO=Path(__file__).resolve().parents[5]
lib=REPO/'art/cemetery_v3/backdrop/source/restore_backdrop.py'
ns={'__name__':'restore_library','__file__':str(lib)};exec(compile(lib.read_text(),str(lib),'exec'),ns,ns)
p=Path(sys.argv[1]);sx=float(sys.argv[2]);sy=float(sys.argv[3]);im=Image.open(p).convert('RGB');a=np.array(im)
xs=ns['axis_grid'](a,1,sx);ys=ns['axis_grid'](a,0,sy)
xc=[(l+r-1)//2 for l,r in zip(xs,xs[1:])];yc=[(l+r-1)//2 for l,r in zip(ys,ys[1:])]
out=Image.fromarray(a[np.ix_(yc,xc)])
stem=p.stem.replace('_generated','');out.save(p.with_name(stem+'_restored_cells.png'))
p.with_name(stem+'_grid.json').write_text(json.dumps({'source_file':p.name,'source_size':list(im.size),'native_size':list(out.size),'estimated_pitch':[sx,sy],'x_boundaries':xs,'y_boundaries':ys,'x_centers':xc,'y_centers':yc,'method':'Observed source cell-transition path; one integer center sample per cell. No resizing/averaging. Empty background lattice inferred; local grid drift remains possible.'},indent=2)+'\n')
g=im.copy();dr=ImageDraw.Draw(g)
for x in xs[1:-1]:dr.line((x,0,x,im.height-1),fill=(225,70,160))
for y in ys[1:-1]:dr.line((0,y,im.width-1,y),fill=(225,70,160))
g.save(p.with_name(stem+'_grid_overlay.png'))
print(p.name,im.size,'->',out.size)
