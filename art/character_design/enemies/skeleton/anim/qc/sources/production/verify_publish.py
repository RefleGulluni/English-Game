from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,re,shutil,subprocess,sys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-skeleton-animation-20261026');S=R/'art/character_design/enemies/skeleton';O=W/'staged';Q=O/'qc';metrics=json.loads((Q/'skeleton_B_anim_metrics.json').read_text());checks={};total=0
for mode in ['walk','collapse','mid']:
 d=Q/'sources'/mode;rs=json.loads((d/'grid.json').read_text());raw=np.array(Image.open(d/'01_generated_original.png').convert('RGB'));ct=0
 for rec in rs:
  a=np.array(Image.open(d/f"frame_{rec['frame']:02}.png").convert('RGBA'));xs=rec['x_boundaries'];ys=rec['y_boundaries'];ox,oy=rec['crop_offset']
  for y,x in zip(*np.where(a[:,:,3]>0)):
   sx=ox+(xs[x]+xs[x+1])//2;sy=oy+(ys[y]+ys[y+1])//2;assert np.array_equal(a[y,x,:3],raw[sy,sx]);ct+=1
 checks[mode]={'center_samples_checked':ct,'exact':True};total+=ct
 # One actual source-pixel crop showing fitted painted cell edges.
 rec=rs[0];ov=Image.fromarray(raw);dr=ImageDraw.Draw(ov);xs=rec['x_boundaries'];ys=rec['y_boundaries'];ox,oy=rec['crop_offset']
 for x in xs:dr.line((x+ox,ys[0]+oy,x+ox,ys[-1]+oy),fill='#FF8080')
 for y in ys:dr.line((xs[0]+ox,y+oy,xs[-1]+ox,y+oy),fill='#FF8080')
 cx=ox+(xs[0]+xs[-1])//2;cy=oy+(ys[0]+ys[-1])//2;ov.crop((max(0,cx-100),max(0,cy-100),cx+100,cy+100)).save(d/'grid_check_1x.png')
# Track entire bottom planted sole, not just an arbitrary toe sample.
sole=[]
for k in range(8):
 a=np.array(Image.open(O/'frames/skeleton_B_walk_right'/f'{k+1:02}.png').convert('RGBA'));toe=[68,63,58,53][k%4];width=9 if k<4 else 11;loc=list(range(toe-width+1,toe+1));assert np.all(a[95,loc,3]==255);world=[x+k*5 for x in loc];sole.append({'frame':k+1,'support_world_sole_x':world,'all_opaque':True})
assert all(x['support_world_sole_x']==sole[0]['support_world_sole_x'] for x in sole[:4]);assert all(x['support_world_sole_x']==sole[4]['support_world_sole_x'] for x in sole[4:])
protected=json.loads((W/'protected.json').read_text());assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protected.items())
checks.update({'total_source_samples':total,'preexisting_files_unchanged':len(protected),'planted_sole_world_pixels':sole});(Q/'verification.json').write_text(json.dumps(checks,indent=2))
# Supplemental same-ground scale comparison, no game files touched.
bg=Image.open(R/'art/cemetery_pixel_v1/plates/ground_plate_960x540.png').convert('RGBA').crop((0,0,960,300));d=ImageDraw.Draw(bg);ft=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12)
items=[('B right standard',Image.open(S/'skeleton_B_right.png').convert('RGBA'))]+[(f'walk {k}',Image.open(O/'frames/skeleton_B_walk_right'/f'{k:02}.png').convert('RGBA')) for k in [1,3,5,7]]+[(f'collapse {k}',Image.open(O/'frames/skeleton_B_collapse_front'/f'{k:02}.png').convert('RGBA')) for k in [1,4,7,9]]
for i,(label,im) in enumerate(items):x=20+i*103;bg.alpha_composite(im,(x,170-im.height));d.text((x,185),label,font=ft,fill='#D0C5B1')
bg.resize((1920,600),Image.Resampling.NEAREST).save(Q/'skeleton_B_trials_on_ground_2x.png')
# Make all record/build code and exact repeated master scale references reviewable.
pd=Q/'sources/production';pd.mkdir(exist_ok=True)
for name in ['recover.py','prep.py','build.py','qc.py','write_qa.py','verify_publish.py','walk_anchor.png','collapse_anchor.png','skeleton_B_right_8x.png']:
 shutil.copy2(W/name,pd/name)
(pd/'README.md').write_text('Built-in image_gen is the image source. Processors only recover painted-cell centers, inherited-palette mappings and documented native selections/registration. Source poses and grids are in sibling folders. Scripts retain historical work path /tmp/english-game-skeleton-animation-20261026; recoverable working archive: ~/.Trash/english-game-skeleton-animation-working-20261026. Adapt paths and use a NEW staging directory if reproducing. Do not rerun publishing over approved outputs.\n')
qa=Q/'skeleton_B_anim_QA.md';text=qa.read_text();text=text.replace('此处是完整帧的接合整理，不是用透明缝表示关节。','此处是完整帧的接合整理，不是用透明缝表示关节。散架第2帧另用连续原生行表使骨盆先降3px、上胸和脚保持原位；中间布/骨段做少量原生省行/重复行接合，完整表在edit_records.json，未用平滑缩放。');text=text.replace('标记已在实际PNG检查为完全不透明。','标记已在实际PNG检查为完全不透明。进一步核对了整段最低脚底像素：右脚地面x=60～68的9px、左脚x=78～88的11px分别在各自着地的4帧中完全固定（见verification.json）。');qa.write_text(text,encoding='utf8')
# Check relative links in new QA.
links=re.findall(r'\]\(([^)]+)\)',text);assert all((Q/p).exists() for p in links)
# Nothing existed at destination: only add this trial package.
dest=S/'anim';assert not dest.exists();shutil.copytree(O,dest)
# Pixel checker again on actual final artifact paths (staging log retained in sources).
log=dest/'qc/pixel_check.txt';shutil.copy2(log,dest/'qc/sources/pixel_check_staging.txt');z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(S/'skeleton_B_right.png'),str(dest/'skeleton_B_walk_right.png'),str(dest/'skeleton_B_collapse_front.png')],capture_output=True,text=True);log.write_text(z.stdout);assert z.returncode==0
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protected.items());print('Verified source cells:',total,'; old files unchanged:',len(protected));print(z.stdout)
