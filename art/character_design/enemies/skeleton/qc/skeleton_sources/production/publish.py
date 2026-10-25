from pathlib import Path
from PIL import Image,ImageDraw
import json,shutil,subprocess,sys,numpy as np
W=Path('/tmp/english-game-skeleton-design-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/character_design/enemies/skeleton';assert not O.exists();O.mkdir(parents=True);Q=O/'qc';Q.mkdir();REF=O/'reference';REF.mkdir();SRC=Q/'skeleton_sources';SRC.mkdir();rec=json.loads((W/'finish_records.json').read_text());hi=json.loads((W/'all_prompts.json').read_text())['hires_paths'];H=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA')
for l,v in rec.items():
 for state in ['standing','remains']:
  name='skeleton_'+l+('_remains' if state=='remains' else '');dest=O/(name+'.png');shutil.copy2(W/'staged'/dest.name,dest);n=v[state+'_source'];d=SRC/(l+'_'+state);d.mkdir();gd=W/'recovered'/n;g=json.loads((gd/'grid.json').read_text());shutil.copy2(g['source'],d/'01_generated_original.png');shutil.copy2(gd/'restored_native.png',d/'02_restored_native_cells.png');shutil.copy2(gd/'grid_check_1x.png',d/'grid_check_1x.png');g['original_tool_path']=g['source'];g['source']='01_generated_original.png';(d/'grid.json').write_text(json.dumps(g,indent=2));shutil.copy2(W/(l+'_'+state+'_cleaned_native.png'),d/'03_cleaned_native_selection.png');shutil.copy2(dest,d/'04_final_native.png');(d/'native_edit.json').write_text(json.dumps({'edits':v['native_selection_edits'],'shared_palette':v['shared_palette'],'registration_and_metrics':v[state]},indent=2));z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),str(dest)],capture_output=True,text=True);assert z.returncode==0,z.stdout+z.stderr;(d/'pixel_check.txt').write_text(z.stdout)
 shutil.copy2(hi[l],REF/('skeleton_'+l+'_concept_hires.png'))
 shutil.copy2(W/(l+'_identity_reference_8x.png'),REF/('skeleton_'+l+'_pixel_identity_8x.png'))
 pal=Q/'palettes';pal.mkdir(exist_ok=True);(pal/('skeleton_'+l+'.gpl')).write_text('GIMP Palette\nName: Skeleton '+l+' paired forms\nColumns: 8\n# sampled material colors, no dithering\n'+'\n'.join(f'{int(c[0]):3d} {int(c[1]):3d} {int(c[2]):3d} material_{k:02d}' for k,c in enumerate(v['shared_palette']))+'\n')
# Formal requested comparison uses EXACT sample ground; only the final preview is enlarged2x.
P=R/'art/cemetery_v3/props';ground=Image.open(R/'art/cemetery_pixel_v1/plates/ground_plate_960x540.png').convert('RGBA');assert ground.size==(960,540);out=ground.copy();props=[('tombstone_upright_01',145,199),('tombstone_cross_01',478,192),('obelisk_01',786,202)]
for n,x,y in props:
 im=Image.open(P/(n+'_base.png')).convert('RGBA');out.alpha_composite(im,(x-im.width//2,y-im.height))
for n,x,y in props:
 im=Image.open(P/(n+'.png')).convert('RGBA');out.alpha_composite(im,(x-im.width//2,y-im.height))
out.alpha_composite(H,(100-48,340-96));layout={'B1':[100,340]}
for l,x in zip('ABC',[275,500,725]):
 im=Image.open(O/('skeleton_'+l+'.png')).convert('RGBA');b=Image.open(O/('skeleton_'+l+'_remains.png')).convert('RGBA');out.alpha_composite(im,(x-48,340-96));out.alpha_composite(b,(x+65-48,382-48));layout[l]={'standing_origin':[x,340],'remains_origin':[x+65,382]}
d=ImageDraw.Draw(out)
def label(x,y,text):
 box=d.textbbox((0,0),text);d.rectangle((x-4,y-2,x+box[2]+4,y+box[3]+3),fill='#292726');d.text((x,y),text,fill='#D7CFB9')
label(22,20,'GRAVE SKELETON / A-B-C design exploration / native scene shown2x');label(83,410,'B1 96px')
for l,x,n in zip('ABC',[242,467,692],['CORD-BOUND','SHROUD-KEPT','NAIL-LACED']):label(x,410,l+' / '+n)
label(22,508,'Standing + matching Bone Remains. Sample ground and approved props are unchanged references.');out.save(Q/'skeleton_compare_1x.png');out.resize((1920,1080),Image.Resampling.NEAREST).save(Q/'skeleton_compare.png');(Q/'comparison_layout.json').write_text(json.dumps({'sample_ground':'art/cemetery_pixel_v1/plates/ground_plate_960x540.png','scale':2,'origins':layout,'props':props},indent=2))
# Detail sheet at exact6x: B1 and all three forms, with their heaps below.
bg='#403D3F';txt='#C7BEAB';detail=Image.new('RGBA',(480,196),bg);d=ImageDraw.Draw(detail)
for n,x,im in [('B1',12,H)]+[(l,132+i*120,Image.open(O/('skeleton_'+l+'.png')).convert('RGBA')) for i,l in enumerate('ABC')]:
 detail.alpha_composite(im,(x,16));d.text((x+35,4),n,fill=txt)
 if n!='B1':detail.alpha_composite(Image.open(O/('skeleton_'+n+'_remains.png')).convert('RGBA'),(x,126))
d.text((12,180),'Native96px B1 / A93 / B96 / C95 | shared palette per pair',fill=txt);detail.resize((2880,1176),Image.Resampling.NEAREST).save(Q/'skeleton_vs_hero_6x.png')
for l in 'ABC':
 im=Image.open(O/('skeleton_'+l+'.png')).convert('RGBA');b=Image.open(O/('skeleton_'+l+'_remains.png')).convert('RGBA');panel=Image.new('RGBA',(288,150),bg);d=ImageDraw.Draw(panel);panel.alpha_composite(H,(0,15));panel.alpha_composite(im,(96,15));panel.alpha_composite(b,(192,63));d.text((8,134),'B1 / '+l+' / Bone Remains',fill=txt);panel.resize((1728,900),Image.Resampling.NEAREST).save(SRC/(l+'_standing')/'05_vs_hero_6x.png')
# Pure black silhouettes, keep original transparent holes.
sil=Image.new('RGBA',(480,196),'#D0CDC3');d=ImageDraw.Draw(sil)
for n,x,im in [('B1',12,H)]+[(l,132+i*120,Image.open(O/('skeleton_'+l+'.png')).convert('RGBA')) for i,l in enumerate('ABC')]:
 a=np.array(im);a[a[:,:,3]>0,:3]=0;sil.alpha_composite(Image.fromarray(a),(x,16));d.text((x+35,4),n,fill='#292725')
 if n!='B1':
  a=np.array(Image.open(O/('skeleton_'+n+'_remains.png')).convert('RGBA'));a[a[:,:,3]>0,:3]=0;sil.alpha_composite(Image.fromarray(a),(x,126))
sil.resize((1920,784),Image.Resampling.NEAREST).save(Q/'skeleton_silhouette.png')
# Store inspectable recipes and prompt provenance inside requested new folder only.
prod=SRC/'production';prod.mkdir()
for f in ['finish.py','recover.py','protected_hashes.json','finish_records.json','selected_sources.json']:shutil.copy2(W/f,prod/f)
shutil.copy2(W/'all_prompts.json',Q/'skeleton_design_prompts.json');files=[str(O/('skeleton_'+l+s+'.png')) for l in 'ABC' for s in ['', '_remains']];z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1_front_straight.png'),*files],capture_output=True,text=True);assert z.returncode==0;(Q/'skeleton_pixel_check.txt').write_text(z.stdout)
print(z.stdout)
