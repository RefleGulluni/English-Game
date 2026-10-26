from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,subprocess,sys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-entry-pillar-20261026');O=R/'art/cemetery_v3/props';S=W/'staged';Q=S/'qc';Q.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12)
def load(n,base=False):
 name=n+('_base' if base else '')+'.png';return Image.open((S if n=='gate_pillar_tall_01' else O)/name).convert('RGBA')
def paste(im,n,x,y,base=False):
 p=load(n,base);im.alpha_composite(p,(x-p.width//2,y-p.height))
layout=[('iron_fence_01',185,270),('iron_fence_01',337,270),('iron_fence_01',633,270),('iron_fence_01',785,270),('wall_pillar_01',256,270),('wall_pillar_01',704,270),('gate_pillar_tall_01',408,270),('gate_pillar_tall_01',552,270)]
a=Image.open(R/'art/cemetery_pixel_v1/plates/ground_plate_960x540.png').convert('RGBA').crop((0,0,960,400))
for n,x,y in layout:paste(a,n,x,y,True)
for n,x,y in layout:paste(a,n,x,y)
h=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');a.alpha_composite(h,(480-48,355-96))
d=ImageDraw.Draw(a);d.text((18,16),'ENTRY GATE / B ashlar / native layout x2 nearest',font=font,fill='#DDD5C6');d.line((408,73,552,73),fill='#C6B79A');
for x in (408,552):d.line((x,69,x,78),fill='#C6B79A')
d.text((419,52),'centers: 144 px',font=font,fill='#DDD5C6');d.text((438,380),'B1: 96 px',font=font,fill='#DDD5C6');d.text((18,374),'Existing fence and intermediate piers unchanged. Entrance intentionally open.',font=font,fill='#DDD5C6')
a.save(Q/'entry_gate_assembly_1x.png');a.resize((1920,800),Image.Resampling.NEAREST).save(Q/'entry_gate_assembly_2x.png')
# Side-by-side requested native and nearest views.
c=Image.new('RGBA',(400,240),'#403D3F');c.alpha_composite(h,(0,210-96))
for n,x in [('wall_pillar_01',142),('gate_pillar_tall_01',260)]:paste(c,n,x,210,True);paste(c,n,x,210)
d=ImageDraw.Draw(c);d.text((9,220),'B1 / existing pier / tall gate pier',font=font,fill='#C6BDAE');c.save(Q/'gate_pillar_tall_01_vs_hero_1x.png');c.resize((2400,1440),Image.Resampling.NEAREST).save(Q/'gate_pillar_tall_01_vs_hero_6x.png')
# Interface overlay proof before and after stone occlusion. No sprite modifications.
j=Image.new('RGBA',(260,120),'#403D3F')
for k,(fencex,pierx) in enumerate([(337,408),(633,552)]):
 src=Image.new('RGBA',(960,400),(0,0,0,0));paste(src,'iron_fence_01',fencex,270);paste(src,'gate_pillar_tall_01',pierx,270)
 crop=src.crop((pierx-40,190,pierx+40,280));j.alpha_composite(crop,(k*130+20,15))
j.resize((2080,960),Image.Resampling.NEAREST).save(Q/'entry_gate_joints_8x.png')
# Exact endpoint coverage of opaque connector column against pillar, common origin.
checks=[]
for fencex,pierx,ex in [(337,408,143),(633,552,12),(185,256,143),(337,256,12),(633,704,143),(785,704,12)]:
 f=np.array(load('iron_fence_01'));n='gate_pillar_tall_01' if pierx in(408,552) else 'wall_pillar_01';p=np.array(load(n));worldx=fencex-80+ex;ys=np.where(f[:,ex,3]>0)[0];hidden=[]
 for sy in ys:
  wy=270-104+int(sy);px=worldx-(pierx-p.shape[1]//2);py=wy-(270-p.shape[0]);hidden.append(bool(0<=px<p.shape[1] and 0<=py<p.shape[0] and p[py,px,3]==255))
 checks.append({'fence_root':[fencex,270],'pier_root':[pierx,270],'fence_native_column':ex,'opaque_endpoint_pixels':len(ys),'hidden_by_stone':sum(hidden),'all_hidden':all(hidden)})
# Per-row opening gap for two identical pillars, centers144; true source outline included.
p=np.array(load('gate_pillar_tall_01'));gap=[]
for y in range(192):
 xs=np.where(p[y,:,3]>0)[0]
 if len(xs):gap.append({'native_row':y,'width':int(xs[-1]-xs[0]+1),'clear_gap_px':int(144-(xs[-1]-xs[0]+1))})
(W/'assembly.json').write_text(json.dumps({'gate_roots':[[408,270],[552,270]],'center_distance':144,'layout':layout,'endpoint_checks':checks,'gap_by_row':gap,'same_sprite_no_mirror':True},indent=2));print(checks)
z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),str(S/'gate_pillar_tall_01.png'),str(S/'gate_pillar_tall_01_base.png')],capture_output=True,text=True);(Q/'entry_gate_pixel_check.txt').write_text(z.stdout);print(z.stdout);assert z.returncode==0
