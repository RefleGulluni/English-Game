from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,subprocess,sys,colorsys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-entry-step2-20261028');O=W/'staged';Q=O/'qc';V=Q/'entry_step2_sources';P=R/'art/cemetery_v3/props';info=json.loads((V/'cleanup_index.json').read_text());load=lambda p:Image.open(p).convert('RGBA');hero=load(R/'art/character_design/hero_B1_front_straight.png');sk=load(R/'art/character_design/enemies/skeleton/skeleton_B.png');textures=[load(R/'art/cemetery_v3/ground/base/ground_base_01.png'),load(R/'art/cemetery_v3/ground/transitions/path_texture_01.png'),load(R/'art/cemetery_v3/ground/transitions/grass_texture_01.png')];font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',11);small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',10)
names=list(info);cn={'iron_gate_leaf_open_01':'半开铁门','iron_gate_leaf_fallen_01':'倒下铁门','fountain_dry_01':'干涸喷泉','dead_tree_02':'枯树 02','dead_tree_03':'枯树 03','fallen_lamp_post_01':'倒下路灯','signpost_01':'木路牌','wooden_cross_01':'直木十字','wooden_cross_02':'歪木十字'};names=['iron_gate_leaf_open_01','iron_gate_leaf_fallen_01','fountain_dry_01','dead_tree_02','dead_tree_03','fallen_lamp_post_01','signpost_01','wooden_cross_01','wooden_cross_02']
def floor(size,which=0):
 a=Image.new('RGBA',size);t=textures[which]
 for y in range(0,size[1],t.height):
  for x in range(0,size[0],t.width):a.alpha_composite(t,(x,y))
 return a

def pp(a,n,x,y,base=False):
 path=(O if n in info else P)/(n+('_base' if base else '')+'.png');p=load(path);a.alpha_composite(p,(x-p.width//2,y-p.height))

def measure(p):
 a=np.array(load(p));fg=a[:,:,3]>0;alpha=sorted(map(int,np.unique(a[:,:,3])));rgb=a[fg,:3];nb=fg[:,:-1]&fg[:,1:];ch=(a[:,:-1,:3]!=a[:,1:,:3]).any(2);cy=0
 for c in np.unique(rgb,axis=0):
  h,s,v=colorsys.rgb_to_hsv(*(c/255))
  if 160<=h*360<=260 and s>=.35 and v>.3:cy+=int((rgb==c).all(1).sum())
 return {'canvas':[a.shape[1],a.shape[0]],'alpha_values':alpha,'colors':len(np.unique(rgb,axis=0)),'neighbor_change_pct':round(float((ch&nb).sum()/nb.sum()*100),4) if nb.any() else None,'cyan_pixels':cy,'lowest_opaque_y':int(np.where(fg)[0].max()) if fg.any() else -1,'bbox':Image.fromarray(a).getbbox(),'mean_rgb':np.round(rgb.mean(0),2).tolist() if len(rgb) else None,'opaque_pixels':int(fg.sum())}
metrics={}
# Each sprite alongside both approved actors, on the actual new base ground.
for n in names:
 cw,ch=info[n]['canvas'];wid=cw+216;hei=max(ch+28,144);b=floor((wid,hei));root=hei-24;pp(b,n,cw//2+4,root,True);pp(b,n,cw//2+4,root);b.alpha_composite(hero,(cw+12,root-96));b.alpha_composite(sk,(cw+112,root-96));d=ImageDraw.Draw(b);d.text((8,hei-18),cn[n],font=font,fill='#DED7C7');d.text((cw+26,hei-18),'主角 96px',font=font,fill='#DED7C7');d.text((cw+124,hei-18),'骷髅 B',font=font,fill='#DED7C7');b.save(Q/(n+'_vs_hero_skeleton_1x.png'));b.resize((wid*6,hei*6),Image.Resampling.NEAREST).save(Q/(n+'_vs_hero_skeleton_6x.png'))
 p=measure(O/(n+'.png'));base=measure(O/(n+'_base.png'));combined=measure(V/n/'04_final_native_with_base.png');assert set(p['alpha_values'])<={0,255} and set(base['alpha_values'])<={0,255};assert p['cyan_pixels']==base['cyan_pixels']==0;assert p['canvas']==base['canvas']==info[n]['canvas'];assert combined['colors']<=48;metrics[n]={'prop':p,'base':base,'combined':combined,'geometry':info[n]}
 #8x native preview per asset, without rescaling source art.
 im=load(V/n/'04_final_native_with_base.png');im.resize((im.width*8,im.height*8),Image.Resampling.NEAREST).save(Q/(n+'_8x.png'))
# Required one-row lineup on the accepted new native ground.
slots=[];x=24
for n in names:
 w=info[n]['canvas'][0];slot=max(w+16,108);slots.append((n,x+slot//2));x+=slot
herox=x+20;skx=x+116;width=x+224;hei=288;root=254;b=floor((width,hei));
for n,cx in slots:pp(b,n,cx,root,True)
for n,cx in slots:pp(b,n,cx,root)
b.alpha_composite(hero,(herox,root-96));b.alpha_composite(sk,(skx,root-96));d=ImageDraw.Draw(b)
for n,cx in slots:d.text((cx-32,hei-24),cn[n],font=font,fill='#E1D9C8')
d.text((herox+9,hei-24),'主角 96px',font=font,fill='#E1D9C8');d.text((skx+16,hei-24),'骷髅 B',font=font,fill='#E1D9C8');d.text((16,8),'墓园入口 · 第2步 / 新正式泥地',font=font,fill='#E1D9C8');b.save(Q/'entry_props_lineup_1x.png');b.resize((width*2,hei*2),Image.Resampling.NEAREST).save(Q/'entry_props_lineup_2x.png')
# Every base contact on each actual ground material; no new painted ground.
rows=[]
for n in names:
 p=load(O/(n+'_base.png'));bb=p.getbbox();crop=p.crop(bb) if bb else Image.new('RGBA',(1,1));rows.append((n,crop))
cellw=208;cellh=104;b=Image.new('RGBA',(cellw*3,cellh*len(rows)))
for i,(n,p) in enumerate(rows):
 for k in range(3):
  panel=floor((cellw,cellh),k);panel.alpha_composite(p,((cellw-p.width)//2,74-p.height));d=ImageDraw.Draw(panel);d.text((5,82),cn[n]+' / '+['泥地','碎石泥路','枯草苔藓'][k],font=font,fill='#E2DAC9');b.alpha_composite(panel,(cellw*k,cellh*i))
b.resize((b.width*2,b.height*2),Image.Resampling.NEAREST).save(Q/'entry_props_base_ground_match_2x.png')
# Required actual-pillar gate assembly. Existing accepted masonry/fences copied unchanged, never mirrored.
layout=[('iron_fence_01',185,270),('iron_fence_01',337,270),('iron_fence_01',633,270),('iron_fence_01',785,270),('wall_pillar_01',256,270),('wall_pillar_01',704,270),('gate_pillar_tall_01',408,270),('gate_pillar_tall_01',552,270)]
b=floor((960,400))
for n,cx,y in layout:pp(b,n,cx,y,True)
pp(b,'iron_gate_leaf_fallen_01',512,242,True);pp(b,'iron_gate_leaf_open_01',433,270,True);pp(b,'iron_gate_leaf_open_01',433,270)
for n,cx,y in layout:pp(b,n,cx,y)
b.alpha_composite(hero,(480-48,355-96));b.alpha_composite(sk,(616-48,355-96));d=ImageDraw.Draw(b);d.text((18,16),'墓园入口 / 柱心408、552，柱脚净空92 / 半开门＋倒门',font=font,fill='#DFD8C9');d.text((18,377),'新正式泥地；原门柱与铁栏未改，未镜像。',font=font,fill='#DFD8C9');b.save(Q/'entry_gate_assembly_1x.png');b.resize((1920,800),Image.Resampling.NEAREST).save(Q/'entry_gate_assembly_2x.png');b.crop((400,180,495,280)).resize((760,800),Image.Resampling.NEAREST).save(Q/'entry_gate_hinge_8x.png')
# Existing source connector coverage and minimum clear opening still numerically unchanged.
p=np.array(load(P/'gate_pillar_tall_01.png'));gaps=[]
for y in range(p.shape[0]):
 xs=np.where(p[y,:,3]>0)[0]
 if len(xs):gaps.append(144-int(xs[-1]-xs[0]+1))
assert min(gaps)==92
assembly={'pillar_roots':[[408,270],[552,270]],'center_spacing':144,'minimum_clear_opening':92,'open_gate_root':[433,270],'fallen_gate_root':[512,242],'unfolded_gate_design_width_range':[44,46],'projected_hinge_to_free_post_axis_span':31,'axis_span_unfolded_at45deg':round(31/(2**-.5),2),'notes':'Picket/diamond decorations and hinge mounting ears extend outside the nominal leaf-axis span. Game collision/door interaction left for Claude.'};(V/'assembly.json').write_text(json.dumps(assembly,ensure_ascii=False,indent=2));(Q/'entry_props_metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
files=[str(O/(n+s+'.png')) for n in names for s in ['', '_base']];z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),*files],capture_output=True,text=True);assert z.returncode==0;(Q/'entry_props_pixel_check.txt').write_text(z.stdout)
for n in names:
 z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),str(O/(n+'.png')),str(O/(n+'_base.png'))],capture_output=True,text=True);assert z.returncode==0;(V/n/'pixel_check.txt').write_text(z.stdout)
print('QC complete. combined colors/density:')
for n,m in metrics.items():print(n,m['combined']['colors'],m['combined']['neighbor_change_pct'],'prop',m['prop']['neighbor_change_pct'],'base',m['base']['neighbor_change_pct'])
