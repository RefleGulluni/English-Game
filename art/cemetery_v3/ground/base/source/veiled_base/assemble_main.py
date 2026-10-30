from pathlib import Path
from PIL import Image
import numpy as np,json,zipfile,datetime
S=Path(__file__).resolve().parent;B=S.parents[1];Q=B/'qc'
exec(compile((S/'material_ops.py').read_text(),str(S/'material_ops.py'),'exec'))
existing=[B/'veiled_base_01.png']+list(S.glob('05_*'))
existing=[p for p in existing if p.is_file()]
if existing:
 with zipfile.ZipFile(Q/f'backups/veiled_main_before_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in existing:z.write(p,str(p.relative_to(B)))
meta=json.loads((S/'02_cleanup_metadata.json').read_text());pal=np.array(meta['palette'],np.uint8);roles=np.array(meta['roles'])
old=np.array(Image.open(S/'03_half_offset_native.png').convert('RGB'));raw=np.array(Image.open(S/'04_cross_repair_restored_cells.png').convert('RGB'));assert old.shape==raw.shape==(128,224,3)
lab,progress=quiet(match(raw,pal),pal,roles);edit=pal[lab];Image.fromarray(edit).save(S/'05_repair_palette_native.png')
cost=((old.astype(float)-edit.astype(float))**2).mean(2)
l=cut(cost[:,90:104])+90;r=cut(cost[:,120:135])+120;t=cut(cost[43:57].T)+43;b=cut(cost[73:87].T)+73
yy,xx=np.indices((128,224));mask=((xx>=l[:,None])&(xx<=r[:,None]))|((yy>=t[None,:])&(yy<=b[None,:]));mask[[0,-1]]=False;mask[:,[0,-1]]=False
out=old.copy();out[mask]=edit[mask];out[:,-1]=out[:,0];out[-1]=out[0]
labels=match(out,pal);newpal=calibrate(pal,labels,roles);out=newpal[labels]
Image.fromarray(out).convert('RGBA').save(B/'veiled_base_01.png');Image.fromarray(out).resize((1344,768),Image.Resampling.NEAREST).save(S/'05_main_6x.png')
Image.fromarray((mask*255).astype('uint8')).save(S/'05_seam_selection_mask.png')
(S/'05_final_palette.json').write_text(json.dumps({'palette':newpal.tolist(),'roles':roles.tolist(),'method':'Common36color material palette;main mean61,64,63/std9. Variant must use this palette and preserve original boundary pixels.'},indent=2)+'\n')
(S/'05_main_assembly.json').write_text(json.dumps({'repair_selected_pixels':int(mask.sum()),'quiet_progress':progress,'left_cut':l.tolist(),'right_cut':r.tolist(),'top_cut':t.tolist(),'bottom_cut':b.tolist(),'method':'Select native AI repair through irregular minimum-error central-cross cuts;retain source outside;pair1px opposing textured profiles;palette-only recalibration,no blur,blend or new grain.'},indent=2)+'\n')
print('Main mean',out.mean((0,1)),'std',(out@LUMA).std(),'colors',len(np.unique(out.reshape(-1,3),axis=0)))
