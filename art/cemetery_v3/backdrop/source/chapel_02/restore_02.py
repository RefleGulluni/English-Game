from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
p=Path(__file__).resolve().parent
# Reuse the previously verified boundary search without running its authoring entrypoint.
ns={'__name__':'restore_library','__file__':str(p.parent/'restore_backdrop.py')};code=(p.parent/'restore_backdrop.py').read_text();exec(compile(code,str(p.parent/'restore_backdrop.py'),'exec'),ns,ns)
axis_grid=ns['axis_grid']
a=np.array(Image.open(p/'01b_generated_wings.png').convert('RGB'))
xs=axis_grid(a,1,11.0);ys=axis_grid(a,0,11.5)
# Manually checked source cross edges: global y trace sampled its bar fringe.
# Correct these local top-row boundaries from visible blocks, not a painted cross.
ys[:9]=[0,7,17,28,41,53,66,80,92]
xc=[(l+r-1)//2 for l,r in zip(xs,xs[1:])];yc=[(l+r-1)//2 for l,r in zip(ys,ys[1:])]
out=a[np.ix_(yc,xc)];Image.fromarray(out).save(p/'02_restored_cells.png')
meta={'source_file':'01b_generated_wings.png','source_size':[a.shape[1],a.shape[0]],'native_size':[out.shape[1],out.shape[0]],'cell_pitch_estimate':[11.0,11.5],'manual_top_y_boundaries':[0,7,17,28,41,53,66,80,92],'x_boundaries':xs,'y_boundaries':ys,'x_centers':xc,'y_centers':yc,'method':'Observed cell transition path, one integer center sample per cell; no resizing or averaged color. Some local source grid drift remains.'}
(p/'02_grid.json').write_text(json.dumps(meta,indent=2)+'\n')
im=Image.fromarray(a);dr=ImageDraw.Draw(im)
for x in xs[1:-1]:dr.line((x,0,x,im.height-1),fill=(40,215,190))
for y in ys[1:-1]:dr.line((0,y,im.width-1,y),fill=(40,215,190))
im.save(p/'02_grid_overlay.png')
mask=(out[:,:,0]<110)&(out[:,:,1]<115)&(out[:,:,2]<130)&(out.max(2).astype(int)-out.min(2)<60)
yy,xx=np.where(mask);top=yy.min()
print('Native',out.shape[1::-1],'overall bbox',[xx.min(),top,xx.max()+1,yy.max()+1])
for h in [90,92,94,96,98]:
 yy,xx=np.where(mask[:top+h]);print('top',h,'bbox width',xx.max()+1-xx.min(),'x',[xx.min(),xx.max()+1])
