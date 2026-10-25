from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,colorsys,runpy,subprocess,sys
W=Path('/tmp/english-game-ashlar02-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';S=W/'staged';S.mkdir(exist_ok=True)
a=np.array(Image.open(W/'restored.png').convert('RGBA'));B=np.array(Image.open(O/'low_wall_broken_01.png').convert('RGBA'));Bb=Image.open(O/'low_wall_broken_01_base.png').convert('RGBA')
# Original painted course bands map by integer row selection only. No scaling.
rowmap=[*range(0,10),*range(16,36),36,*range(38,67)];assert len(rowmap)==60
can=np.zeros((96,288,4),dtype=np.uint8);offsetx=16
for dy,sy in enumerate(rowmap):can[36+dy,offsetx:offsetx+a.shape[1]]=a[sy]
# Source silhouette has slightly unequal ends; repeat core crops terminal planes.
left,right=24,263;prop=can.copy();base=can.copy();prop[:,:left]=0;prop[:,right+1:]=0
# Select low stone face vs flat grass/mud. Lowerchips may remain in flatbase.
mask=np.zeros(prop.shape[:2],bool);mask[35:90,left:right+1]=True
# Natural foot: avoid moving the whole muddy band to the occluding prop.
for y in range(83,90):
 for x in range(left,right+1):
  rgb=can[y,x,:3].astype(int)
  if can[y,x,3] and rgb.max()-rgb.min()>45 and rgb[0]>rgb[1]+18:mask[y,x]=False
prop[~mask]=0;base[mask]=0
# Overlay three distinct inherited dark earth pieces to thicken sunken ground contact.
bi=Image.fromarray(base)
for box,xy in [((14,77,55,96),(13,77)),((55,82,98,96),(123,82)),((100,82,145,96),(236,82))]:bi.alpha_composite(Bb.crop(box),xy)
base=np.array(bi)
# Warm source grass/soil darkened, gray chips retain their relative light.
map_dark={}
for rgb in np.unique(base[base[:,:,3]>0,:3],axis=0):
 rr,gg,bb=[int(c) for c in rgb];hh,ss,vv=colorsys.rgb_to_hsv(rr/255,gg/255,bb/255)
 if 12<hh*360<82 and ss>.25 and .299*rr+.587*gg+.114*bb>70:
  c=tuple(round(v*.66) for v in [rr,gg,bb]);sel=np.all(base[:,:,:3]==rgb,axis=2)&(base[:,:,3]>0);base[sel,:3]=c;map_dark[str(tuple(int(v) for v in rgb))]=c
# Clean residual magenta from all native selections.
for ar in [prop,base]:
 c=ar[:,:,:3].astype(int);bad=(c[:,:,0]-c[:,:,1]>28)&(c[:,:,2]-c[:,:,1]>28);ar[bad]=0
# Fixed join colors must remain bit-for-bit; palette uses exact B native endpoints.
join=B[:,21];fixed=np.unique(join[join[:,3]>0,:3],axis=0)
def reduce(ar,limit,fixed=None):
 fg=ar[:,:,3]>0;rgb=ar[fg,:3];k=limit-(len(fixed) if fixed is not None else 0);q=Image.fromarray(rgb.reshape(1,-1,3)).quantize(max(8,k),method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);p=np.array(q.getpalette(),dtype=np.uint8).reshape(-1,3);p=p[np.unique(np.array(q))]
 if fixed is not None:p=np.unique(np.concatenate((fixed,p)),axis=0)
 out=ar.copy();p=p.astype(int)
 for y,x in zip(*np.where(fg)):
  c=ar[y,x,:3].astype(int);out[y,x,:3]=p[((p-c)**2).sum(1).argmin()]
 return out
prop=reduce(prop,50,fixed);base=reduce(base,48)
# Keep exact B interface columns; near-end context uses unique short strips from B.
prop[:,left]=join;prop[:,right]=join
# Two adjacent real native columns at each end reinforce corresponding course mortars.
prop[:,left+1]=B[:,22];prop[:,right-1]=B[:,22]
# These columns may add a few required colors; fold interior to their fixed palette budget if needed.
allfixed=np.unique(B[:,21:23][B[:,21:23,3]>0,:3],axis=0)
if len(np.unique(prop[prop[:,:,3]>0,:3],axis=0))>50:
 prop=reduce(prop,50,allfixed);prop[:,left]=join;prop[:,right]=join;prop[:,left+1]=B[:,22];prop[:,right-1]=B[:,22]
# Trim one exposed top scanline to match accepted B minY36 exactly; joins already transparent there.
prop[35]=0
Image.fromarray(prop).save(S/'low_wall_ashlar_02.png');Image.fromarray(base).save(S/'low_wall_ashlar_02_base.png')
com=Image.fromarray(base);com.alpha_composite(Image.fromarray(prop));com.save(W/'cleaned_combined.png')
notes={'canvas':[288,96],'origin':[144,96],'join_columns':[left,right],'stride':240,'source_x_offset':offsetx,'rowmap_source_rows':rowmap,'rowmap_target_start':36,'native_edit':'Integer source row selection: coping+upper bevel at36..45, upper face46..65, main mortar66, lower face67..89, ground90..95. Drop source cap rows10..15 and mortar transition row37; no interpolation, no stone duplication.','fixed_endpoint_colors':int(len(allfixed)),'darkening_palette_map':map_dark,'source_band_rows':{'coping':[0,10],'upper_course':[16,36],'main_mortar':[36,37],'lower_course':[38,61],'ground':[61,67]}}
(W/'cleanup.json').write_text(json.dumps(notes,indent=2))
# Verify grayscale-aware pixel specification through actual project checker.
z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),str(S/'low_wall_ashlar_02.png'),str(S/'low_wall_ashlar_02_base.png')],capture_output=True,text=True);(W/'pixel_check.txt').write_text(z.stdout);print(z.stdout);assert z.returncode==0
h=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');p=Image.new('RGBA',(410,145),'#403D3F');p.alpha_composite(h,(0,27));p.alpha_composite(com,(112,27));ImageDraw.Draw(p).text((4,130),'B1 / unique ashlar02',fill='#BEB7A9');p.resize((p.width*3,p.height*3),Image.Resampling.NEAREST).save(W/'review_3x.png')
