from pathlib import Path
from PIL import Image
import numpy as np,json
S=Path(__file__).resolve().parent
exec(compile((S/'material_ops.py').read_text(),str(S/'material_ops.py'),'exec'))
im=Image.open(S/'01_material_restored_cells.png').convert('RGB');w,h=im.size;x=(w-224)//2;y=(h-128)//2;crop=(x,y,x+224,y+128)
a=np.array(im.crop(crop));Image.fromarray(a).save(S/'03_crop_native.png');r,g,b=a.astype(int).transpose(2,0,1)
lichen=(g-b<18)&(a@LUMA>75)&(a.max(2).astype(int)-a.min(2).astype(int)<30);keep=small_lichen(lichen)
filled=a.copy()
for yy,xx in zip(*np.where(lichen)):
 for radius in range(1,7):
  choices=[(nx,ny) for ny in range(max(0,yy-radius),min(128,yy+radius+1)) for nx in range(max(0,xx-radius),min(224,xx+radius+1)) if not lichen[ny,nx]]
  if choices:
   nx,ny=min(choices,key=lambda p:(p[0]-xx)**2+(p[1]-yy)**2);filled[yy,xx]=a[ny,nx];break
q=np.array(Image.fromarray(filled).quantize(colors=30,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB'))
pal,inv=np.unique(q.reshape(-1,3),axis=0,return_inverse=True);assert len(pal)==30
pal=np.vstack([pal,[[96,101,96],[103,106,100]]]).astype('uint8');lab=inv.reshape(128,224)
lab[keep]=np.where((a@LUMA)[keep]>=100,31,30)
lab,progress=quiet(lab,pal);newpal=calibrated(pal,lab);out=newpal[lab]
Image.fromarray(out).save(S/'03_cleaned_native.png');Image.fromarray(out).resize((1344,768),Image.Resampling.NEAREST).save(S/'03_cleaned_6x.png')
Image.fromarray((keep*255).astype('uint8')).save(S/'03_lichen_selection.png')
shift=np.roll(out,(64,112),axis=(0,1));Image.fromarray(shift).save(S/'04_half_offset_native.png');Image.fromarray(shift).resize((1344,768),Image.Resampling.NEAREST).save(S/'04_half_offset_6x.png')
meta={'restored_size':[w,h],'crop_xyxy':crop,'palette':newpal.tolist(),'palette_mapping':[{'from':p.tolist(),'to':n.tolist()} for p,n in zip(pal,newpal)],'mean_rgb':out.mean((0,1)).tolist(),'luma_std':float((out@LUMA).std()),'horizontal_change_progress':progress,'lichen_source_pixels':int(lichen.sum()),'lichen_retained_pixels':int(keep.sum()),'lichen_max_component':max(map(len,groups(keep))),'method':'Native center samples, integer crop;30-color moss without dithering plus2 retained lichen shades. Reduce gray lichen clusters to at most2 existing pixels and merge their other edge pixels into adjacent native moss. <=3px adjacent moss near-shade merge distance14,2passes. Palette-only mean59,69,55/std11.5. No new moss forms, noise, blur or art resizing. Half offset112,64.'}
(S/'03_cleanup_metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print({k:v for k,v in meta.items() if k not in ['palette','palette_mapping','method']})
