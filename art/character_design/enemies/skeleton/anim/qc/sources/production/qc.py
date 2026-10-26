from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,colorsys,subprocess,sys,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-skeleton-animation-20261026');S=R/'art/character_design/enemies/skeleton';O=W/'staged';Q=O/'qc';Q.mkdir(exist_ok=True);P=Q/'sources';P.mkdir(exist_ok=True);palette=np.array(json.loads((W/'palette.json').read_text()));L=np.array([.299,.587,.114]);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16);small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
names=['skeleton_B_walk_right','skeleton_B_collapse_front'];timing={'version':1,'frame_size':[96,96],'anchor':[48,96],'animations':{'skeleton_B_walk_right':{'frames':8,'durations_ms':[100]*8,'loop':True,'sprite_sheet':'skeleton_B_walk_right.png','movement_px_per_second':50,'support_foot_canvas_step_px':-5},'skeleton_B_collapse_front':{'frames':9,'durations_ms':[80,70,70,80,90,100,120,200,200],'loop':False,'sprite_sheet':'skeleton_B_collapse_front.png','hold_last_frame':True}}};(O/'timing.json').write_text(json.dumps(timing,indent=2))
metrics={'animations':{},'standards':{}};palset=set(map(tuple,palette.tolist()));base=np.array(Image.open(S/'skeleton_B_right.png').convert('RGBA'));stand_luma=[float((b[b[:,:,3]>0,:3]@L).mean()) for b in [base[0:20],base[20:45],base[45:65],base[65:96]]]
for p in [S/n for n in ['skeleton_B.png','skeleton_B_back.png','skeleton_B_left.png','skeleton_B_right.png','skeleton_B_remains.png']]:
 im=Image.open(p).convert('RGBA');metrics['standards'][p.name]={'png_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'size':list(im.size)}
for name in names:
 frames=[Image.open(p).convert('RGBA') for p in sorted((O/'frames'/name).glob('*.png'))];rows=[];indexed=[]
 for i,f in enumerate(frames):
  a=np.array(f);fg=a[:,:,3]>0;colors=set(map(tuple,a[fg,:3].tolist()));bands=[]
  for j,(y0,y1) in enumerate([(0,20),(20,45),(45,65),(65,96)]):
   b=a[y0:y1];rgb=b[b[:,:,3]>0,:3];mean=float((rgb@L).mean()) if len(rgb) else None;bands.append({'mean':mean,'difference_from_right_standing':mean-stand_luma[j] if mean is not None else None,'highlights_gt170_pct':float(100*((rgb@L)>170).mean()) if len(rgb) else None})
  v=fg[:,:-1]&fg[:,1:];rows.append({'frame':i+1,'rgba_sha256':hashlib.sha256(f.tobytes()).hexdigest(),'alpha_values':[int(x) for x in np.unique(a[:,:,3])],'new_colors':len(colors-palset),'colors':len(colors),'lowest_opaque_y':int(np.where(fg)[0].max()),'bbox_exclusive':list(f.getbbox()),'adjacent_change_pct':float(100*((a[:,:-1,:3]!=a[:,1:,:3]).any(2)&v).sum()/v.sum()),'bands':bands});assert set(np.unique(a[:,:,3]))<={0,255};assert not colors-palset
  # Exact shared palette, transparent index0, no quantization or dithering for GIF.
  idx=np.zeros(a.shape[:2],dtype=np.uint8)
  for pi,c in enumerate(palette):idx[fg&np.all(a[:,:,:3]==c,axis=2)]=pi+1
  pal=[0,0,0]+palette.flatten().tolist();pal+= [0]*(768-len(pal));ii=Image.fromarray(idx,'P');ii.putpalette(pal);ii.info['transparency']=0;indexed.append(ii.resize((768,768),Image.Resampling.NEAREST))
 opts={'save_all':True,'append_images':indexed[1:],'duration':timing['animations'][name]['durations_ms'],'transparency':0,'disposal':2,'optimize':False}
 if timing['animations'][name]['loop']:opts['loop']=0
 indexed[0].save(Q/(name+'_8x.gif'),**opts)
 # Verify GIF decoded opaque pixels, durations and frame count against actual PNG frames.
 gif=Image.open(Q/(name+'_8x.gif'));assert gif.n_frames==len(frames);dur=[]
 for i,f in enumerate(frames):
  gif.seek(i);dur.append(gif.info['duration']);g=np.array(gif.convert('RGBA'));n=np.array(f.resize((768,768),Image.Resampling.NEAREST));assert np.array_equal(g[:,:,3],n[:,:,3]);mask=n[:,:,3]>0;assert np.array_equal(g[mask,:3],n[mask,:3])
 assert dur==timing['animations'][name]['durations_ms'];metrics['animations'][name]={'frames':rows,'decoded_gif_durations_ms':dur,'decoded_gif_matches_png_rgba_on_opaque':True,'loop':timing['animations'][name]['loop']}
 # Smaller runtime-scale preview and transparent contact sheet.
 board=Image.new('RGBA',(4*112,((len(frames)+3)//4)*116),'#403D3F');d=ImageDraw.Draw(board)
 for i,f in enumerate(frames):x=i%4*112;y=i//4*116;board.alpha_composite(f,(x+8,y));d.text((x+8,y+100),str(i+1),fill='white')
 board.resize((board.width*4,board.height*4),Image.Resampling.NEAREST).save(Q/(name+'_contact_4x.png'))
# Bone destination comparison: actual delivered intermediate frames, semantic group markers.
mapim=Image.new('RGBA',(1550,800),'#353335');d=ImageDraw.Draw(mapim);d.text((24,16),'B / COLLAPSE: anatomical groups, not a per-pixel correspondence claim',font=font,fill='#DED6C4');stages=[1,4,7,9];groups=[('Skull + headwrap','#E3C17B',[(48,9),(51,31),(77,77),(77,77)]),('Right shoulder / two nails','#C68E71',[(35,19),(37,39),(28,61),(25,69)]),('Ribs / spine','#ADB8A7',[(54,28),(54,49),(58,75),(58,72)]),('Pelvis (covered in pile)','#BFA8C6',[(47,49),(48,69),(47,82),(47,82)]),('Shroud / stitched fold','#A5B59B',[(53,55),(55,70),(43,76),(43,79)]),('Long bones / feet','#BCABA0',[(40,78),(39,88),(30,90),(30,90)])]
for ci,stage in enumerate(stages):
 f=Image.open(O/'frames/skeleton_B_collapse_front'/f'{stage:02}.png').convert('RGBA').resize((288,288),Image.Resampling.NEAREST);x=24+ci*380;y=66;mapim.alpha_composite(f,(x,y));d.text((x,y+300),f'Frame {stage}',font=font,fill='#DED6C4')
 for gi,(name,color,points) in enumerate(groups):
  px,py=points[ci];cx=x+px*3;cy=y+py*3;d.ellipse((cx-5,cy-5,cx+5,cy+5),outline=color,width=2);d.text((cx+6,cy-8),str(gi+1),font=small,fill=color)
for gi,(name,color,pts) in enumerate(groups):
 yy=410+gi*55;d.ellipse((28,yy,40,yy+12),fill=color);d.text((50,yy-4),str(gi+1)+'. '+name,font=font,fill=color);d.text((470,yy-4),f'{pts[0]} -> {pts[1]} -> {pts[2]} -> {pts[3]}',font=font,fill='#CCC4B5')
d.text((24,760),'Positions are native (x,y). Pelvis/rib parts obscured by cloth are semantic locations, not visibly isolated pieces.',font=small,fill='#CCC4B5');mapim.save(Q/'skeleton_B_collapse_map.png')
# Ground-lock coordinates, measured actual opaque toe pixels.
r=json.loads((W/'edit_records.json').read_text());lock=[]
for f in r['walk']:
 im=np.array(Image.open(O/'frames/skeleton_B_walk_right'/f"{f['frame']:02}.png").convert('RGBA'));x,y=f['support_local'];assert im[y,x,3]==255;f['actual_support_pixel_opaque']=True;lock.append({k:f[k] for k in ['frame','support','support_local','world_translation','support_world','actual_support_pixel_opaque']})
metrics['foot_lock']=lock;metrics['walking_baseline_luma']=stand_luma
front=Image.open(S/'skeleton_B.png').convert('RGBA');end=Image.new('RGBA',(96,96));end.alpha_composite(Image.open(S/'skeleton_B_remains.png').convert('RGBA'),(0,48));start=Image.open(O/'frames/skeleton_B_collapse_front/01.png').convert('RGBA');last=Image.open(O/'frames/skeleton_B_collapse_front/09.png').convert('RGBA');assert np.array_equal(front,start);assert np.array_equal(end,last);metrics['collapse_endpoints']={'first_rgba_sha256':hashlib.sha256(start.tobytes()).hexdigest(),'last_rgba_sha256':hashlib.sha256(last.tobytes()).hexdigest(),'padded_remains_rgba_sha256':hashlib.sha256(end.tobytes()).hexdigest(),'first_exact':True,'last_exact':True}
for f in metrics['animations']['skeleton_B_walk_right']['frames']:
 assert f['lowest_opaque_y']==95
 for b in f['bands']:assert abs(b['difference_from_right_standing'])<=2
z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(S/'skeleton_B_right.png'),str(O/'skeleton_B_walk_right.png'),str(O/'skeleton_B_collapse_front.png')],capture_output=True,text=True);(Q/'pixel_check.txt').write_text(z.stdout);assert z.returncode==0
(Q/'skeleton_B_anim_metrics.json').write_text(json.dumps(metrics,indent=2));(Q/'foot_lock.json').write_text(json.dumps(lock,indent=2))
# Preserve selected original generation and every recovered frame/grid, not only final strips.
raws={'walk':'exec-04d54907-32ff-4b49-855e-e9509528b060.png','collapse':'exec-3979d2a7-4f23-47c9-b03e-bae83e214b57.png','mid':'exec-27e880e3-60a0-470d-adac-2ca342da494a.png'}
for mode,raw in raws.items():
 dd=P/mode;dd.mkdir(exist_ok=True);shutil.copy2(Path('/Users/mac/.codex/generated_images/01a16768-6cb4-7a02-aee2-ae3ac8b12896')/raw,dd/'01_generated_original.png')
 for p in (W/mode).glob('*'):shutil.copy2(p,dd/p.name)
for n in ['prep.json']:shutil.copy2(W/'prepared'/n,P/n)
for n in ['edit_records.json','palette.json','prompts.json','protected.json']:shutil.copy2(W/n,P/n)
print('GIFs RGBA/timing verified, lock toes and luma checked; exact endpoints verified')
