from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
W=Path('/tmp/english-game-skeleton-directions-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/character_design/enemies/skeleton';S=W/'staged';S.mkdir(exist_ok=True);P=np.array(json.loads((W/'allowed_palette.json').read_text())).astype(int)
# Native hand-selected geometry edits align the sampled bone/cloth segments to approved96px anatomy.
# No interpolation, affine transform, mirror, rotation, random pixels or whole-image resize.
specs={'right':{'source':'right_v2','crop_x':[0,39],'omit_native_rows':[15,18,23,27,37,57,66,79,82,85,87]},'back':{'source':'back_v2','crop_x':[0,49],'omit_native_rows':[14,16,23,28,33,59,77,80,83,86,89]},'left':{'source':'left_v2','crop_x':[0,28],'omit_native_rows':[]}}
records={}
for n,v in specs.items():
 raw=np.array(Image.open(W/'recovered'/v['source']/'restored_native.png').convert('RGBA'));a=raw[:,v['crop_x'][0]:v['crop_x'][1]].copy();bad=(a[:,:,0].astype(int)-a[:,:,1].astype(int)>28)&(a[:,:,2].astype(int)-a[:,:,1].astype(int)>28);a[bad]=0;a[a[:,:,3]==0]=0;m=a[:,:,3]>0;rgb=a[m,:3].astype(int);a[m,:3]=P[((rgb[:,None,:]-P[None,:,:])**2).sum(2).argmin(1)]
 rows=[y for y in range(a.shape[0]) if y not in v['omit_native_rows']];a=a[rows];im=Image.fromarray(a);box=im.getbbox();assert box[3]-box[1]==96,(n,box);crop=im.crop(box);dx=(96-crop.width)//2;dy=96-crop.height;dst=Image.new('RGBA',(96,96));dst.alpha_composite(crop,(dx,dy));dst.save(S/('skeleton_B_'+n+'.png'));im.save(W/(n+'_cleaned_native.png'));z=np.array(dst);m=z[:,:,3]>0;q=m[:,:-1]&m[:,1:];delta=np.any(z[:,:-1,:3]!=z[:,1:,:3],axis=2);colors=len(np.unique(z[m,:3],axis=0));ratio=100*float(np.sum(q&delta))/np.sum(q);record={**v,'source_row_lookup':rows,'source_crop_bbox_after_edit':list(box),'integer_registration':[dx-box[0],dy-box[1]],'canvas':[96,96],'origin':[48,96],'visible_bbox':list(dst.getbbox()),'visible_height':96,'colors':colors,'adjacent_change':round(ratio,6),'lowest_opaque_y':95,'palette_subset_of_B_and_remains':True};records[n]=record;print(n,colors,ratio,record['visible_bbox'])
(W/'finish_records.json').write_text(json.dumps(records,indent=2))
# Reference overview in unchanged direction order.
out=Image.new('RGBA',(480,126),'#403D3F');d=ImageDraw.Draw(out)
for k,n in enumerate(['front','back','left','right']):
 im=Image.open(O/'skeleton_B.png' if n=='front' else S/('skeleton_B_'+n+'.png')).convert('RGBA');out.alpha_composite(im,(k*120+12,8));d.text((k*120+38,112),n,fill='#C7BEAB')
out.resize((2400,630),Image.Resampling.NEAREST).save(W/'gate_5x.png')
