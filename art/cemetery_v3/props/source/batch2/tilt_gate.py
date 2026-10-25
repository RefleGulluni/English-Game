from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math,runpy,subprocess,sys
W=Path('/tmp/english-game-props-batch2-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';S=W/'staged';S.mkdir(exist_ok=True)
a=np.array(Image.open(W/'recovered/tombstone_upright_01_tilted/restored_native.png').convert('RGBA'));parent=np.array(Image.open(O/'tombstone_upright_01.png').convert('RGBA'));pal=np.unique(parent[parent[:,:,3]>0,:3],axis=0).astype(int)
fg=a[:,:,3]>0;out=a.copy();bad=(a[:,:,0].astype(int)-a[:,:,1].astype(int)>28)&(a[:,:,2].astype(int)-a[:,:,1].astype(int)>28);out[bad]=0
for y,x in zip(*np.where(out[:,:,3]>0)):
 c=out[y,x,:3].astype(int);out[y,x,:3]=pal[((pal-c)**2).sum(1).argmin()]
# Redrawn stone selection, not a transformed parent image.
m=Image.new('L',(a.shape[1],a.shape[0]),0);ImageDraw.Draw(m).polygon([(0,0),(84,0),(84,66),(74,66),(74,75),(68,78),(39,78),(27,75),(22,69),(0,68)],fill=255);mask=np.array(m)>0;prop=out.copy();base=out.copy();prop[~mask]=0;base[mask]=0
# Dark ground palette inherited from original soil; never a bright grass rim.
oldbase=np.array(Image.open(O/'tombstone_upright_01_base.png').convert('RGBA'));bp=np.unique(oldbase[oldbase[:,:,3]>0,:3],axis=0).astype(int)
for y,x in zip(*np.where(base[:,:,3]>0)):
 c=base[y,x,:3].astype(int);base[y,x,:3]=bp[((bp-c)**2).sum(1).argmin()]
# Drop detached source mud chips to ground. No floatingclods left in silhouette.
# They are excluded from stone mask; source crops translate within base only.
# Native scene registration settles redraw4px deeper into original footline.
pi=Image.new('RGBA',(112,112));bi=Image.new('RGBA',(112,112));pi.alpha_composite(Image.fromarray(prop),(6,21));bi.alpha_composite(Image.fromarray(base),(6,17));n='tombstone_upright_01_tilted';pi.save(S/(n+'.png'));bi.save(S/(n+'_base.png'))
# Straight-shaft centerline over rows25..65; excludes crown and disturbed dirt.
ys=[];centers=[]
for y in range(25,66):
 xs=np.where(prop[y,:,3]>0)[0]
 if len(xs)>20:ys.append(y);centers.append((int(xs.min())+int(xs.max()))/2)
slope,intercept=np.polyfit(ys,centers,1);angle=float(np.degrees(np.arctan(slope)));record={'redrawn_source':json.loads((W/'tilt_generation.json').read_text())['source'],'digital_rotation_or_shear':False,'centerline_fit_rows':[25,65],'lean_left_angle_degrees':angle,'registration':{'prop_offset':[6,21],'base_offset':[6,17],'canvas':[112,112]},'identity':['rounded crown','left crown olive moss','crown rain streak','three unreadable incisions','lowerleft pale lichen','right thickness and lower fracture']};(W/'tilt_gate.json').write_text(json.dumps(record,indent=2))
old=Image.open(W/'tombstone_upright_01_native.png').convert('RGBA');com=bi.copy();com.alpha_composite(pi);h=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');p=Image.new('RGBA',(360,145),'#403D3F');p.alpha_composite(h,(0,27));p.alpha_composite(old,(115,11));p.alpha_composite(com,(235,11));ImageDraw.Draw(p).text((7,130),'B1 / original01 / redrawn tilt',fill='#BEB7A9');p.resize((2160,870),Image.Resampling.NEAREST).save(W/'tilt_gate_vs_parent_6x.png')
z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),str(S/(n+'.png')),str(S/(n+'_base.png'))],capture_output=True,text=True);print(z.stdout);assert z.returncode==0;print('redrawn lean angle',angle)
