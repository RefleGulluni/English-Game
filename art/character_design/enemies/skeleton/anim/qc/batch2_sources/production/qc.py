from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,subprocess,sys,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';W=Path('/tmp/english-game-skeleton-batch2-20261026');O=W/'staged';Q=O/'qc';Q.mkdir(exist_ok=True);P=Q/'batch2_sources';P.mkdir(exist_ok=True);L=np.array([.299,.587,.114]);pal=np.array(json.loads((W/'palette.json').read_text()));palset=set(map(tuple,pal.tolist()));newtim=json.loads((W/'new_timing.json').read_text());records=json.loads((W/'records.json').read_text());stand={d:Image.open(S/('skeleton_B.png' if d=='front' else f'skeleton_B_{d}.png')).convert('RGBA') for d in ['front','back','left','right']};pile=Image.new('RGBA',(96,96));pile.alpha_composite(Image.open(S/'skeleton_B_remains.png').convert('RGBA'),(0,48));metrics={'animations':{},'standards':{},'endpoint_checks':{},'left_foot_lock':[],'source_checks':{}};font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
for d,f in {**stand,'remains_padded':pile}.items():metrics['standards'][d]={'rgba_sha256':hashlib.sha256(f.tobytes()).hexdigest(),'size':list(f.size)}
for name,t in newtim.items():
 frames=[Image.open(p).convert('RGBA') for p in sorted((O/'frames'/name).glob('*.png'))];rows=[];gif=[];side=name.rsplit('_',1)[-1];master=np.array(stand.get(side,stand['front']));hsh=[]
 for k,f in enumerate(frames):
  a=np.array(f);fg=a[:,:,3]>0;colors=set(map(tuple,a[fg,:3].tolist()));assert not colors-palset;assert set(np.unique(a[:,:,3]))<={0,255};ys,xs=np.where(fg);bands=[]
  for y0,y1 in [(0,20),(20,45),(45,65),(65,96)]:
   b=a[y0:y1];rgb=b[b[:,:,3]>0,:3];ref=master[y0:y1];ref=ref[ref[:,:,3]>0,:3];mean=float((rgb@L).mean()) if len(rgb) else None;baseline=float((ref@L).mean());bands.append({'range':[y0,y1],'mean':mean,'standing_mean':baseline,'difference':mean-baseline if mean is not None else None,'highlights_gt170_percent':float(100*((rgb@L)>170).mean()) if len(rgb) else None})
  v=fg[:,:-1]&fg[:,1:];rows.append({'frame':k+1,'rgba_sha256':hashlib.sha256(f.tobytes()).hexdigest(),'bbox':list(f.getbbox()),'lowest_opaque_y':int(ys.max()),'alpha_values':[int(x) for x in np.unique(a[:,:,3])],'colors':len(colors),'new_colors':0,'adjacent_change_pct':float(100*((a[:,:-1,:3]!=a[:,1:,:3]).any(2)&v).sum()/v.sum()),'bands':bands});assert int(ys.max())==95,(name,k,'floating whole pose')
  if '_walk_' in name:
   for b in bands:assert abs(b['difference'])<=2,(name,k,b)
   for yy in range(36,65):assert (a[yy,40:59,3]>0).any(),(name,k,yy,'waist gap')
  if '_idle_' in name:
   assert np.array_equal(a[84:],master[84:]),(name,k,'idle feet move')
  if '_hit_' in name:assert np.array_equal(a[84:],master[84:]),(name,k,'hit feet move')
  # Shared exact inherited palette: index0 is the transparent background, no quantization/dither.
  ix=np.zeros(a.shape[:2],np.uint8)
  for pi,c in enumerate(pal):ix[fg&np.all(a[:,:,:3]==c,axis=2)]=pi+1
  ii=Image.fromarray(ix);ii.putpalette(([0,0,0]+pal.flatten().tolist()+[0]*768)[:768]);ii.info['transparency']=0;gif.append(ii.resize((768,768),Image.Resampling.NEAREST))
 opt={'save_all':True,'append_images':gif[1:],'duration':t['durations_ms'],'transparency':0,'disposal':2,'optimize':False}
 if t['loop']:opt['loop']=0
 path=Q/(name+'_8x.gif');gif[0].save(path,**opt);im=Image.open(path);assert im.n_frames==len(frames),(name,im.n_frames,len(frames));decoded=[]
 for k,f in enumerate(frames):
  im.seek(k);decoded.append(im.info['duration']);a=np.array(im.convert('RGBA'));b=np.array(f.resize((768,768),Image.Resampling.NEAREST));assert np.array_equal(a[:,:,3],b[:,:,3]);fg=b[:,:,3]>0;assert np.array_equal(a[fg,:3],b[fg,:3])
 assert decoded==t['durations_ms'];metrics['animations'][name]={'frames':rows,'gif_decoded_durations_ms':decoded,'gif_opaque_rgba_and_alpha_exact':True,'loop':t['loop']}
 if '_idle_' in name or '_hit_' in name:
  assert np.array_equal(np.array(frames[0]),master);metrics['endpoint_checks'][name]={'first_exact_standard':True,'first_rgba_sha256':rows[0]['rgba_sha256']}
 if name=='skeleton_B_remains_idle':assert np.array_equal(np.array(frames[0]),np.array(pile));metrics['endpoint_checks'][name]={'first_exact_padded_remains':True,'first_rgba_sha256':rows[0]['rgba_sha256']}
 if name=='skeleton_B_reassemble_front':
  assert np.array_equal(np.array(frames[0]),np.array(pile));assert np.array_equal(np.array(frames[-1]),np.array(stand['front']));metrics['endpoint_checks'][name]={'first_exact_padded_remains':True,'last_exact_front_standard':True,'first_rgba_sha256':rows[0]['rgba_sha256'],'last_rgba_sha256':rows[-1]['rgba_sha256']}
  for k in range(3,9):assert not (np.array(frames[k])[:20,:,3]>0).any(),('head attached too early',k+1)
 # Existing full contact sheet, nearest4x.
 shutil.copy2(W/(name+'_4x.png'),Q/(name+'_contact_4x.png'))
# Actual left-facing toe position plus the whole bottom planted sole in world coordinates.
for k,r in enumerate(records['skeleton_B_walk_left']):
 a=np.array(Image.open(O/'frames/skeleton_B_walk_left'/f'{k+1:02}.png').convert('RGBA'));support=r['support'];x,y=support['canvas'];assert a[y,x,3]==255;rowxs=np.where(a[95,:,3]>0)[0];expectedworld=[x-5*k,95];assert support['world']==expectedworld
 # Sole pixels translated with their master shape; isolate planted foot's own last-row source mask.
 leg=r['legs'][0 if k<4 else 1];box=leg['foot_crop'];m=np.array(stand['left']);ft=m[box[1]:box[3],box[0]:box[2]];bb=Image.fromarray(ft).getbbox();ft=ft[bb[1]:bb[3],bb[0]:bb[2]];solexs=np.where(ft[-1,:,3]>0)[0]+leg['offset'][0];assert np.all(a[95,solexs,3]==255);worldsole=(solexs-5*k).tolist();metrics['left_foot_lock'].append({'frame':k+1,**support,'entire_world_sole_x':worldsole,'all_opaque':True})
assert all(x['entire_world_sole_x']==metrics['left_foot_lock'][0]['entire_world_sole_x'] for x in metrics['left_foot_lock'][:4]);assert all(x['entire_world_sole_x']==metrics['left_foot_lock'][4]['entire_world_sole_x'] for x in metrics['left_foot_lock'][4:])
# Every restored raw cell's RGB must equal the original center sample, not resize/average.
for mode in ['left','front','back','reassemble']:
 rs=json.loads((W/mode/'grid.json').read_text());count=0;srcpath=Path(rs[0]['source']);raw=np.array(Image.open(srcpath).convert('RGB'));dd=P/mode;dd.mkdir(exist_ok=True);shutil.copy2(srcpath,dd/'01_generated_original.png')
 for r in rs:
  a=np.array(Image.open(W/mode/f"frame_{r['frame']:02}.png").convert('RGBA'));ox,oy=r['source_crop_offset'];xb=r['x_boundaries'];yb=r['y_boundaries']
  for y,x in zip(*np.where(a[:,:,3]>0)):
   sx=ox+(xb[x]+xb[x+1])//2;sy=oy+(yb[y]+yb[y+1])//2;assert np.array_equal(a[y,x,:3],raw[sy,sx]);count+=1
  shutil.copy2(W/mode/f"frame_{r['frame']:02}.png",dd/f"frame_{r['frame']:02}.png")
 shutil.copy2(W/mode/'grid.json',dd/'grid.json');metrics['source_checks'][mode]={'sample_count':count,'all_exact':True}
 r=rs[0];ov=Image.fromarray(raw);d=ImageDraw.Draw(ov);ox,oy=r['source_crop_offset'];xb=r['x_boundaries'];yb=r['y_boundaries']
 for x in xb:d.line((ox+x,oy+yb[0],ox+x,oy+yb[-1]),fill='#FF8080')
 for y in yb:d.line((ox+xb[0],oy+y,ox+xb[-1],oy+y),fill='#FF8080')
 cx=ox+(xb[0]+xb[-1])//2;cy=oy+(yb[0]+yb[-1])//2;ov.crop((max(0,cx-100),max(0,cy-100),cx+100,cy+100)).save(dd/'grid_check_1x.png')
# A time-labelled construction map makes the separate reassembly order reviewable.
mapim=Image.new('RGBA',(1740,520),'#353335');d=ImageDraw.Draw(mapim);steps=[1,4,6,7,8,9,10,12];dur=newtim['skeleton_B_reassemble_front']['durations_ms'];labels=['Pile / cord taut','PELVIS first','Spine stacks','Ribs / no head','Head waits','Skull yanked','SNAP skull','Shroud / whole']
for ci,(k,label) in enumerate(zip(steps,labels)):
 f=Image.open(O/'frames/skeleton_B_reassemble_front'/f'{k:02}.png').convert('RGBA');x=12+ci*216;mapim.alpha_composite(f.resize((192,192),Image.Resampling.NEAREST),(x,65));d.text((x,280),f'F{k} / {sum(dur[:k-1])} ms',font=font,fill='#D8CCB6');d.text((x,310),label,font=font,fill='#C6B99E')
d.text((16,18),'REASSEMBLE / a new construction sequence, not reversed collapse',font=font,fill='#E0D6C6');d.text((16,375),'Pelvis and legs support the structure before the ribs. The skull remains on the floor through F8.',font=font,fill='#C6B99E');d.text((16,410),'F9: skull hauled upward. F10: 40 ms snap. F11: shroud catches the right-shoulder pins. F12: exact master.',font=font,fill='#C6B99E');mapim.save(Q/'skeleton_B_reassemble_map.png')
# Bone remains tiny twitch review.
shutil.copy2(W/'skeleton_B_remains_idle_4x.png',Q/'skeleton_B_remains_idle_contact_4x.png')
(Q/'skeleton_B_anim_batch2_metrics.json').write_text(json.dumps(metrics,indent=2));(Q/'skeleton_B_walk_left_lock.json').write_text(json.dumps(metrics['left_foot_lock'],indent=2));(P/'records.json').write_text(json.dumps(records,indent=2));shutil.copy2(W/'prompts.json',P/'prompts.json');shutil.copy2(W/'palette.json',P/'palette.json')
print('Verified13actions/68frames, endpoints, palette/alpha, walking luma, full planted sole and GIF decode/timing.')
