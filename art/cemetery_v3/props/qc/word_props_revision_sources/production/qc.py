from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,importlib.util
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');P=R/'art/cemetery_v3/props';W=Path('/Users/mac/.codex/work/word-props-revision-20261029');O=W/'staged';Q=O/'qc';S=Q/'word_props_revision_sources';rec=json.loads((S/'cleanup_index.json').read_text());B=P/'qc/backups/before_word_props_revision_20261029';read=lambda p:np.array(Image.open(p).convert('RGBA'))
sp=importlib.util.spec_from_file_location('pc',R/'scripts/tools/pixel_check.py');pc=importlib.util.module_from_spec(sp);sp.loader.exec_module(pc)
def source(n,suffix=''):
 p=O/(n+suffix+'.png');return p if p.exists() else P/p.name

def body(n):
 im=Image.open(source(n,'_base')).convert('RGBA');im.alpha_composite(Image.open(source(n)));return im

ground=Image.open(R/'art/cemetery_v3/ground/base/ground_base_01.png').convert('RGBA');hero=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');skel=Image.open(R/'art/character_design/enemies/skeleton/skeleton_B.png').convert('RGBA')
def bg(size):
 b=Image.new('RGBA',size)
 for y in range(0,size[1],ground.height):
  for x in range(0,size[0],ground.width):b.paste(ground,(x,y))
 return b

def at(b,im,root):b.alpha_composite(im,(root[0]-im.width//2,root[1]-im.height))
metrics={}
for n in ['crypt_sealed_01','fresh_grave_mound_01']:
 metrics[n]={}
 for suffix,key in [('', 'prop'),('_base','base')]:
  path=source(n,suffix);a=read(path);stats=pc.measure(path);assert stats['alpha_ok'] and stats['cyan']==0;assert not a[a[:,:,3]==0].any();metrics[n][key]={**stats,'png_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rgba_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'bbox':Image.open(path).getbbox()}
 metrics[n]['details']=rec[n]
 im=body(n);w=im.width+140;h=max(im.height,96)+42;b=bg((w,h));at(b,im,(im.width//2+8,h-26));at(b,hero,(im.width+70,h-26));d=ImageDraw.Draw(b);d.text((6,h-17),n,fill='#d6cbb7');d.text((im.width+45,h-17),'HERO B1',fill='#d6cbb7');b.save(Q/(n+'_vs_hero_1x.png'));b.resize((w*6,h*6),Image.Resampling.NEAREST).save(Q/(n+'_vs_hero_6x.png'))
# Door check: left is intact facade and hero; right places unchanged96px hero
# on the threshold inside the measured door aperture to check vertical fit.
b=bg((620,300));im=body('crypt_sealed_01');at(b,im,(148,272));at(b,hero,(278,272));at(b,im,(465,272));ox=465-128;oy=272-256;x0,y0,x1,y1=rec['crypt_sealed_01']['door_canvas_bbox_exclusive'];at(b,hero,(ox+(x0+x1)//2,oy+y1));d=ImageDraw.Draw(b);d.rectangle((ox+x0,oy+y0,ox+x1-1,oy+y1-1),outline='#d5bf8d',width=1);d.text((22,8),'NEW CRYPT / HERO 96PX',fill='#d6cbb7');d.text((365,8),f'DOOR {x1-x0} x {y1-y0} / HERO96',fill='#d6cbb7');b.save(Q/'crypt_sealed_01_door_scale_1x.png');b.resize((1240,600),Image.Resampling.NEAREST).save(Q/'crypt_sealed_01_door_scale_2x.png')
# Actual mud/gravel screenshot crop. It is a3x pixel screenshot: selecting
# each3x3 block's middle yields the original native viewport without smoothing.
shot=read(R/'docs/reference/ground_paint_room_grass_01.png');assert shot.shape[:2]==(1620,2880);native=shot[1::3,1::3];crop=Image.fromarray(native).crop((330,230,610,390));crop.save(S/'path_crop_native.png');scene=Image.new('RGBA',(560,180));scene.paste(crop,(0,0));scene.paste(crop,(280,0));old=Image.open(B/'fresh_grave_mound_01_base.png').convert('RGBA');old.alpha_composite(Image.open(P/'fresh_grave_mound_01.png'));at(scene,old,(220,140));at(scene,body('fresh_grave_mound_01'),(500,140));d=ImageDraw.Draw(scene);d.text((8,164),'BEFORE / MUD AND GRAVEL',fill='#d6cbb7');d.text((288,164),'NEW WET EARTH / SAME SHOVEL',fill='#d6cbb7');scene.save(Q/'fresh_grave_mound_01_revision_compare_1x.png');scene.resize((1120,360),Image.Resampling.NEAREST).save(Q/'fresh_grave_mound_01_revision_compare_2x.png')
# Updated all8 lineup; all6 accepted sprite files are loaded directly unchanged.
names=['raven_ground_01','tombstone_raven_01','tombstone_mossy_01','grave_bell_01','bell_frame_01','crypt_sealed_01','old_well_01','fresh_grave_mound_01'];width=sum(body(n).width+24 for n in names)+240;line=bg((width,310));x=20;d=ImageDraw.Draw(line)
for n in names:
 im=body(n);at(line,im,(x+im.width//2,272));d.text((x,289),n,fill='#d6cbb7');x+=im.width+24
at(line,hero,(x+35,272));at(line,skel,(x+120,272));d.text((x+15,289),'HERO',fill='#d6cbb7');d.text((x+100,289),'SKELETON',fill='#d6cbb7');line.save(Q/'word_props_lineup_1x.png');line.resize((width*2,620),Image.Resampling.NEAREST).save(Q/'word_props_lineup_2x.png')
# Old/new crypt on same ground, no scaling of runtime sprites for comparison.
b=bg((680,300));old=Image.open(B/'crypt_sealed_01_base.png').convert('RGBA');old.alpha_composite(Image.open(B/'crypt_sealed_01.png'));at(b,old,(145,272));at(b,hero,(290,272));at(b,body('crypt_sealed_01'),(475,272));at(b,hero,(620,272));d=ImageDraw.Draw(b);d.text((35,10),'BEFORE',fill='#d6cbb7');d.text((375,10),'NEW / REGENERATED NATIVE PIXELS',fill='#d6cbb7');b.resize((1360,600),Image.Resampling.NEAREST).save(Q/'crypt_sealed_01_revision_compare_2x.png')
metrics['path_sample']={'source':'docs/reference/ground_paint_room_grass_01.png','native_reconstruction':'select source[1::3,1::3] because screenshot is exactly3x native; QC only','native_crop_xyxy':[330,230,610,390]};(Q/'word_props_revision_metrics.json').write_text(json.dumps(metrics,indent=2))
prod=S/'production';prod.mkdir(exist_ok=True)
for f in ['recover.py','finish.py','qc.py','before.json']:shutil.copy2(W/f,prod/f)
for p in W.glob('generation*.json'):shutil.copy2(p,prod/p.name)
print('QC and final metrics written. Runtime shovel bytes remain unchanged.')
