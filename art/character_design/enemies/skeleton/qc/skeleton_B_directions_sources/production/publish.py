from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,shutil,subprocess,sys,numpy as np
W=Path('/tmp/english-game-skeleton-directions-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/character_design/enemies/skeleton';Q=O/'qc';D=Q/'skeleton_B_directions_sources';assert not D.exists();D.mkdir();rec=json.loads((W/'finish_records.json').read_text());S=W/'staged'
for n,v in rec.items():
 f='skeleton_B_'+n+'.png';dest=O/f;assert not dest.exists();shutil.copy2(S/f,dest);sd=D/n;sd.mkdir();g=json.loads((W/'recovered'/v['source']/'grid.json').read_text());shutil.copy2(g['source'],sd/'01_generated_original.png');shutil.copy2(W/'recovered'/v['source']/'restored_native.png',sd/'02_restored_native_cells.png');shutil.copy2(W/(n+'_cleaned_native.png'),sd/'03_cleaned_native_geometry.png');shutil.copy2(dest,sd/'04_final_96x96.png');shutil.copy2(W/'recovered'/v['source']/'grid_check_1x.png',sd/'grid_check_1x.png');g['original_tool_path']=g['source'];g['source']='01_generated_original.png';(sd/'grid.json').write_text(json.dumps(g,indent=2));(sd/'native_edit.json').write_text(json.dumps(v,indent=2));z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),str(dest)],capture_output=True,text=True);assert z.returncode==0;(sd/'pixel_check.txt').write_text(z.stdout)
# Single native row, skeleton four directions followed by corresponding B1 directions.
directions=['front','back','left','right'];out=Image.new('RGBA',(896,128),'#403D3F');d=ImageDraw.Draw(out)
for i,n in enumerate(directions):
 sk=Image.open(O/('skeleton_B.png' if n=='front' else 'skeleton_B_'+n+'.png')).convert('RGBA');h=Image.open(R/'art/character_design'/('hero_B1_front_straight.png' if n=='front' else 'hero_B1_'+n+'.png')).convert('RGBA');x=8+i*108;out.alpha_composite(sk,(x,8));d.text((x+21,112),'S '+n,fill='#C7BEAB');x=456+i*108;out.alpha_composite(h,(x,8));d.text((x+17,112),'B1 '+n,fill='#C7BEAB')
d.line((442,8,442,120),fill='#847867');out.resize((1792,256),Image.Resampling.NEAREST).save(Q/'skeleton_B_turnaround_2x.png');out.resize((5376,768),Image.Resampling.NEAREST).save(Q/'skeleton_B_turnaround_6x.png')
# Marking artwork is generated at6x; final sprites are never painted on.
MARKS={
'front':{'cloth':[(33,18,64,85)],'pins':[(31,10,44,20)],'X':[(42,23,58,34)],'wrap':[(42,2,56,9)],'waist':[(36,34,63,40)]},
'back':{'cloth':[(51,17,68,37),(35,66,44,81)],'pins':[(53,13,65,20)],'X':[(51,23,63,32)],'wrap':[(40,2,57,10)],'waist':[(35,34,64,40)]},
'left':{'cloth':[(39,36,54,85),(40,22,47,34)],'pins':[(52,12,59,20)],'X':[(39,24,47,33)],'wrap':[(40,2,56,10)],'waist':[(39,33,59,39)]},
'right':{'cloth':[(30,17,54,37),(47,40,62,84)],'pins':[(31,9,43,20)],'X':[(46,23,56,34)],'wrap':[(40,2,58,10)],'waist':[(39,34,59,41)]}}
COLORS={'cloth':'#D7B46F','pins':'#D8896D','X':'#C0A2C7','wrap':'#AFBF8D','waist':'#DDD3BD'}
notes={
'front':['1 cloth: R shoulder -> L shin','2 two pins: anatomical R shoulder','3 black X seam on front sheet','4 diagonal forehead wrap','5 waist cord'],
'back':['1 rear R-shoulder fold; L-calf edge','2 tips only; heads hidden in front','3 HIDDEN: X seam on front face','4 cloth wrap around back of skull','5 waist cord across back'],
'left':['1 front edge + NEAR left calf panel','2 FAR R-shoulder tip; other occluded','3 partial seam at front chest edge','4 forehead/side wrap','5 waist cord at side'],
'right':['1 NEAR R-shoulder fold; FAR L-calf','2 two obvious NEAR R-shoulder pins','3 partial X on front-facing fold','4 forehead/side wrap','5 waist cord at side']}
try:
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17);titlefont=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',23)
except OSError:font=titlefont=ImageFont.load_default()
marks=Image.new('RGBA',(2400,840),'#403D3F');d=ImageDraw.Draw(marks)
for k,n in enumerate(directions):
 x=k*600+12;y=44;im=Image.open(O/('skeleton_B.png' if n=='front' else 'skeleton_B_'+n+'.png')).convert('RGBA');marks.alpha_composite(im.resize((576,576),Image.Resampling.NEAREST),(x,y));d.text((x+210,8),n.upper(),font=titlefont,fill='#D7CEBA')
 for number,(key,boxes) in enumerate(MARKS[n].items(),1):
  for j,box in enumerate(boxes):
   b=tuple((x+box[i]*6) if i%2==0 else (y+box[i]*6) for i in range(4));color=COLORS[key]
   if n=='back' and key=='X':
    for a0 in range(0,360,30):d.arc(b,a0,a0+17,fill=color,width=2)
   else:d.ellipse(b,outline=color,width=2)
   label=str(number)+('b' if j else '')+('H' if n=='back' and key=='X' else '')
   d.rectangle((b[2]+2,b[1]-2,b[2]+36,b[1]+20),fill='#403D3F');d.text((b[2]+3,b[1]-2),label,font=font,fill=color)
 for i,t in enumerate(notes[n]):d.text((x+8,644+i*26),t,font=font,fill=list(COLORS.values())[i])
d.text((22,800),'6x native pixels | right/left are anatomical | dashed3H locates an OCCLUDED front seam, not an extra back mark.',font=font,fill='#D7CEBA');marks.save(Q/'skeleton_B_marks.png');(D/'mark_regions.json').write_text(json.dumps({'native_boxes':MARKS,'legend':notes,'colors':COLORS},indent=2))
# An extra compact2x sample-ground check, no runtime edits.
g=Image.open(R/'art/cemetery_pixel_v1/plates/ground_plate_960x540.png').convert('RGBA');dd=ImageDraw.Draw(g)
for i,n in enumerate(directions):
 im=Image.open(O/('skeleton_B.png' if n=='front' else 'skeleton_B_'+n+'.png')).convert('RGBA');x=168+i*208;g.alpha_composite(im,(x-48,290-96));dd.rectangle((x-35,313,x+45,331),fill='#292726');dd.text((x-28,316),n,fill='#D7CEBA')
g.resize((1920,1080),Image.Resampling.NEAREST).save(Q/'skeleton_B_directions_on_ground_2x.png')
prod=D/'production';prod.mkdir()
for f in ['finish.py','recover.py','finish_records.json','allowed_palette.json','protected_hashes.json','prompt_drafts.json','paths.json','paths_v2.json','paths_v3.json']:shutil.copy2(W/f,prod/f)
files=[str(O/'skeleton_B.png')]+[str(O/('skeleton_B_'+n+'.png')) for n in ['back','left','right']];z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),*files],capture_output=True,text=True);assert z.returncode==0;(D/'pixel_check_all.txt').write_text(z.stdout);print(z.stdout)
