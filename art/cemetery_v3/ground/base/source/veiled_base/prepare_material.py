from pathlib import Path
from PIL import Image
import numpy as np,json
S=Path(__file__).resolve().parent
exec(compile((S/'material_ops.py').read_text(),str(S/'material_ops.py'),'exec'))
im=Image.open(S/'01_material_restored_cells.png').convert('RGB');w,h=im.size;assert w>=224 and h>=128
x=(w-224)//2;y=(h-128)//2;crop=(x,y,x+224,y+128);im=im.crop(crop);im.save(S/'02_crop_native.png')
a=np.array(im.quantize(colors=36,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB'));pal,inv=np.unique(a.reshape(-1,3),axis=0,return_inverse=True);lab=inv.reshape(128,224)
r,g,b=pal.astype(int).T;roles=np.where((r-g>4)&(g-b>3),'leaf','mud');lab,progress=quiet(lab,pal,roles);newpal=calibrate(pal,lab,roles);out=newpal[lab]
Image.fromarray(out).save(S/'02_cleaned_native.png');Image.fromarray(out).resize((1344,768),Image.Resampling.NEAREST).save(S/'02_cleaned_6x.png')
shift=np.roll(out,(64,112),axis=(0,1));Image.fromarray(shift).save(S/'03_half_offset_native.png');Image.fromarray(shift).resize((1344,768),Image.Resampling.NEAREST).save(S/'03_half_offset_6x.png')
meta={'restored_size':[w,h],'crop_xyxy':crop,'palette':newpal.tolist(),'roles':roles.tolist(),'mapping':[{'from':p.tolist(),'to':q.tolist(),'material':str(k)} for p,q,k in zip(pal,newpal,roles)],'mean_rgb':out.mean((0,1)).tolist(),'luma_std':float((out@LUMA).std()),'horizontal_change_progress':progress,'method':'36-color no-dither quantization;two <=3px same-material adjacent near-color merges,distance<=14;palette-only neutral cool mud61,64,63/std9,subdued decomposed leaf shades;native half-offset112,64. No drawn texture/noise,art resize,blend or blur.'}
(S/'02_cleanup_metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print({k:v for k,v in meta.items() if k not in ['palette','mapping','roles']})
