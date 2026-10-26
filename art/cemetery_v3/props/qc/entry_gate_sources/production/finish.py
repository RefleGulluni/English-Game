from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,colorsys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-entry-pillar-20261026');O=R/'art/cemetery_v3/props';S=W/'staged';S.mkdir(exist_ok=True)
a=np.array(Image.open(W/'restored.png').convert('RGBA'));c=a[:,:,:3].astype(int);bad=(c[:,:,0]-c[:,:,1]>30)&(c[:,:,2]-c[:,:,1]>30);a[bad]=0
parent=np.array(Image.open(O/'wall_pillar_01.png').convert('RGBA'));pal=np.unique(parent[parent[:,:,3]>0,:3],axis=0)
# Polygon is only a layer-selection mask on the existing painted native pixels.
sel=Image.new('1',(79,198));ImageDraw.Draw(sel).polygon([(0,0),(78,0),(78,155),(63,155),(66,160),(66,176),(54,184),(15,175),(14,160),(18,156),(0,155)],fill=1);mask=np.array(sel,dtype=bool)
prop=a.copy();base=a.copy();prop[~mask]=0;base[mask]=0
# Native length editing: shorten long urn and blank course interiors, never resize.
removed=[2,6,9,20,23,26,29,32,72,75,78,81,94,97,100,103,113,116,119,122,134,137,140,143]
rows=[y for y in range(190) if y not in removed]
rec={'source_column_lookup':[x for x in range(79) if x!=14],'removed_outer_bevel_column':14,'source_row_lookup':rows,'removed_native_rows':removed,'flat_apron_trimmed_rows':[190,198],'source_to_canvas_offset':[8,25],'canvas':[96,192],'origin':[48,192],'layer_mask_polygon':[(0,0),(78,0),(78,155),(63,155),(66,160),(66,176),(54,184),(15,175),(14,160),(18,156),(0,155)],'method':'Native selected row removal in urn/course interiors and trim flat-soil tail, followed by integer registration. No whole image scaling/rotation/mirroring. Palette nearest inherited B-family colors, no noise/dithering.'}
for n,ar in [('gate_pillar_tall_01',prop),('gate_pillar_tall_01_base',base)]:
 ar=ar[rows][:,[x for x in range(79) if x!=14]].copy();fg=ar[:,:,3]>0;rgb=ar[fg,:3].astype(int)
 if n.endswith('_base'):
  # One-to-one darkening of ground palette before nearest inherited material ramp.
  rgb=np.rint(rgb*.68).astype(int)
 ix=((rgb[:,None]-pal.astype(int)[None])**2).sum(2).argmin(1);ar[fg,:3]=pal[ix]
 can=np.zeros((192,96,4),dtype=np.uint8);can[25:25+len(rows),8:86]=ar;Image.fromarray(can).save(S/(n+'.png'))
 v=(can[:,:-1,3]>0)&(can[:,1:,3]>0);change=100*((can[:,:-1,:3]!=can[:,1:,:3]).any(2)&v).sum()/v.sum();print(n,'bbox',Image.fromarray(can).getbbox(),'colors',len(np.unique(can[can[:,:,3]>0,:3],axis=0)),'change',change)
rec['inherited_palette_rgb']=pal.tolist();(W/'cleanup.json').write_text(json.dumps(rec,indent=2))
p=Image.open(S/'gate_pillar_tall_01_base.png').convert('RGBA');p.alpha_composite(Image.open(S/'gate_pillar_tall_01.png').convert('RGBA'));p.save(W/'combined.png');p.resize((576,1152),Image.Resampling.NEAREST).save(W/'combined_6x.png')
