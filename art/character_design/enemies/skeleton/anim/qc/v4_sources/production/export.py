from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,subprocess,sys
W=Path('/tmp/english-game-skeleton-v4-20261027');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';O=W/'staged';Q=O/'qc';V=Q/'v4_sources';L=np.array([.299,.587,.114]);P=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),np.uint8);pset={tuple(c) for c in P};tim=json.loads((W/'new_timing.json').read_text());rec=json.loads((W/'records.json').read_text());protected=json.loads((W/'protected.json').read_text());met={};vf={};fsall={}
def load(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rh(a):return hashlib.sha256(a.tobytes()).hexdigest()
def metric(a):
 fg=a[:,:,3]>0;rgb=a[fg,:3];pa=fg[:,:-1]&fg[:,1:];de=(a[:,:-1,:3]!=a[:,1:,:3]).any(2);ys,xs=np.where(fg);bands=[]
 for y0,y1 in [(0,20),(20,45),(45,65),(65,96)]:
  z=a[y0:y1];c=z[z[:,:,3]>0,:3];bands.append({'band':[y0,y1-1],'mean_gray':float((c@L).mean()) if len(c) else None})
 return {'rgba_sha256':rh(a),'alpha_values':np.unique(a[:,:,3]).tolist(),'colors':len(np.unique(rgb,axis=0)),'new_colors':sorted({tuple(map(int,c)) for c in rgb}-pset),'horizontal_change_percent':float((pa&de).sum()/pa.sum()*100),'lowest_y':int(ys.max()),'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'bands':bands}
flat=[0,0,0]+P.flatten().tolist();flat += [0]*(768-len(flat));locks=json.loads((A/'qc/skeleton_B_walk_side_v3_lock.json').read_text());footproof={};armproof={}
for n,t in tim.items():
 fs=[load(O/'frames'/n/f'{k+1:02}.png') for k in range(t['frames'])];fsall[n]=fs;ms=[metric(a) for a in fs];met[n]=ms;assert Image.open(O/(n+'.png')).size==(96*len(fs),96)
 for m in ms:assert set(m['alpha_values'])<={0,255} and not m['new_colors'] and m['lowest_y']==95
 pp=[]
 for a in fs:
  ix=np.zeros((96,96),np.uint8)
  for j,c in enumerate(P):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=j+1
  im=Image.fromarray(ix).convert('P');im.putpalette(flat);pp.append(im.resize((768,768),Image.Resampling.NEAREST))
 opt={'loop':0} if t['loop'] else {};pp[0].save(Q/(n+'_8x.gif'),save_all=True,append_images=pp[1:],duration=t['durations_ms'],transparency=0,disposal=2,optimize=False,**opt);g=Image.open(Q/(n+'_8x.gif'));assert g.n_frames==len(fs),(n,g.n_frames,len(fs))
 for k,a in enumerate(fs):
  g.seek(k);b=np.array(g.convert('RGBA'));e=np.repeat(np.repeat(a,8,axis=0),8,axis=1);fg=e[:,:,3]>0;assert np.array_equal(b[:,:,3],e[:,:,3]) and np.array_equal(b[fg],e[fg]);assert g.info['duration']==t['durations_ms'][k]
 vf[n]={'frames':len(fs),'duration_ms':sum(t['durations_ms']),'gif_decoded_pixels_alpha_framecount_timing_exact':True};shutil.copy2(W/(n+'_3x.png'),Q/(n+'_contact_3x.png'))
 if '_walk_' in n:
  d=n.split('_')[-2];m=load(S/('skeleton_B.png' if d=='front' else f'skeleton_B_{d}.png'));sm=metric(m)
  for z in ms:
   for b,sb in zip(z['bands'],sm['bands']):b['standing_mean_gray']=sb['mean_gray'];b['difference']=b['mean_gray']-sb['mean_gray'];assert abs(b['difference'])<=2,(n,b)
  if d in ['left','right']:
   armproof[d]=[]
   for k,a in enumerate(fs):
    old=load(A/'frames'/n.replace('_v4','_v3')/f'{k+1:02}.png');mask=load(V/'side_arm_masks'/d/f'{k+1:02}_edit_mask.png')[:,:,3]>0;overlay=load(V/'side_arm_masks'/d/f'{k+1:02}_whole_arms.png');fg=overlay[:,:,3]>0
    assert np.array_equal(a[~mask],old[~mask]);assert np.array_equal(a[61:],old[61:]);assert (a[fg,3]==255).all();x0,x1=(42,51) if d=='left' else (39,58);assert np.array_equal(a[20:44,x0:x1],old[20:44,x0:x1])
    for j,r in enumerate(rec[n][k]['whole_arm_poses']):
     source=load(V/'arm_sources'/f'{d}_{j+1}.png');ss=np.zeros_like(source);dy=r['offset'][1];dx=r['offset'][0];ys,xs=np.where(source[:,:,3]>0);ss[ys+dy,xs+dx]=source[ys,xs];sfg=ss[:,:,3]>0;assert (a[sfg,3]==255).all()
    for xx in locks[d][k]['entire_world_sole_x']:assert a[95,xx-locks[d][k]['world_translation'][0],3]==255
    armproof[d].append({'frame':k+1,'whole_arm_alpha_masks_present_at_exact_integer_offsets':True,'all_pixels_outside_arm_edit_envelope_rgba_exact_v3':True,'all_pixels_y61_95_rgba_exact_v3':True,'thorax_core_rgba_exact_v3':True,'arm_color_calibrated_only_inside_new_arm_mask':True})
   vf[n].update({'arm_shape_sources_constant_rigid_translation':True,'lower_y61_to95_rgba_exact_v3':True,'support_feet_ground_positions_exact_v3':True,'cloth_outside_arm_occlusion_unchanged':True,'chest_core_rgba_exact_v3':True})
  else:
   rows=[]
   for k,a in enumerate(fs):
    r=rec[n][k];p=[]
    for side,(x0,x1,key) in enumerate([(24,48,'lift_screen_left'),(48,75,'lift_screen_right')]):
     lift=r[key];ft=m[84:96,x0:x1];ys,xs=np.where(ft[:,:,3]>0);ey=int(ys.max()+84-lift);bottom=xs[ys==ys.max()]+x0;assert all(a[ey,x,3]==255 for x in bottom);p.append({'side':'screen_left' if side==0 else 'screen_right','lift_px':lift,'actual_foot_lowest_y':ey,'bottom_sole_x':bottom.tolist(),'all_actual_sole_pixels_present':True})
    assert min(v['lift_px'] for v in p)==0;rows.append({'frame':k+1,'pelvis_offset':r['pelvis_offset'],'feet':p,'knee_outward_px':r['knee_outward_px'],'cloth_lag_source_frame':r['cloth_lag_source_frame']})
   footproof[d]=rows;assert max(v['lift_px'] for r in rows for v in r['feet'])==6;vf[n].update({'actual_raised_foot_peak_6px':True,'at_least_one_actual_support_sole_at_y95_every_frame':True,'in_place_no_vertical_foot_lock':True})
 else:
  pile=np.zeros((96,96,4),np.uint8);pile[48:]=load(S/'skeleton_B_remains.png');assert np.array_equal(fs[0],pile) and np.array_equal(fs[-1],load(S/'skeleton_B.png'));deltas=[int((a!=b).any(2).sum()) for a,b in zip(fs,fs[1:])];assert max(deltas)<=1000,max(deltas)
  pathproof=[]
  for k,r in enumerate(rec[n]):
   if 'thread_path' not in r:continue
   path=r['thread_path'];assert all(tuple(fs[k][y,x,:3])==(19,10,2) and fs[k][y,x,3]==255 for x,y in path);assert all(max(abs(a[0]-b[0]),abs(a[1]-b[1]))<=1 for a,b in zip(path,path[1:]));pathproof.append({'frame':k+1,'phase':r['phase'],'color':'#130A02','path_pixels':len(set(map(tuple,path))),'all_pixels_opaque_and_exact_seam_color':True,'path_8_connected':True})
  assert all(v>=80 or (rec[n][k]['phase']=='snap_60ms' and v==60) for k,v in enumerate(t['durations_ms']));vf[n].update({'first_exact_padded_remains':True,'last_exact_front_standard':True,'every_adjacent_rgba_change_at_most_1000':True,'adjacent_rgba_changed_pixels':deltas,'thread_checks':pathproof,'all_non_snap_frames_at_least80ms':True})
(Q/'skeleton_B_walk_side_v4_lock.json').write_text(json.dumps(locks,indent=2));(Q/'skeleton_B_walk_front_back_v4_feet.json').write_text(json.dumps(footproof,indent=2));(Q/'skeleton_B_walk_side_v4_arm_checks.json').write_text(json.dumps(armproof,indent=2))
# Clear anatomical close-ups, same native camera and pixel magnification.
b=Image.new('RGBA',(9*48,2*58),'#403D3F');dr=ImageDraw.Draw(b)
for j,d in enumerate(['right','left']):
 arr=[load(S/f'skeleton_B_{d}.png')]+fsall[f'skeleton_B_walk_{d}_v4']
 for k,a in enumerate(arr):b.alpha_composite(Image.fromarray(a).crop((24,16,68,63)),(k*48,j*58));dr.text((k*48,j*58+47),d+' std' if k==0 else str(k),fill='white')
b.resize((b.width*8,b.height*8),Image.Resampling.NEAREST).save(Q/'skeleton_B_walk_side_v4_arms_8x.png')
b=Image.new('RGBA',(4*56,4*52),'#403D3F');dr=ImageDraw.Draw(b)
for j,d in enumerate(['front','back']):
 for k,a in enumerate(fsall[f'skeleton_B_walk_{d}_v4']):x=k%4*56;y=(j*2+k//4)*52;b.alpha_composite(Image.fromarray(a).crop((24,55,76,96)),(x,y));dr.text((x,y+41),f'{d} {k+1}',fill='white')
b.resize((b.width*8,b.height*8),Image.Resampling.NEAREST).save(Q/'skeleton_B_walk_front_back_v4_feet_8x.png')
n='skeleton_B_reassemble_front_v4';ixs=[k for k,r in enumerate(rec[n]) if 'thread_path' in r];b=Image.new('RGBA',(5*52,2*92),'#403D3F');dr=ImageDraw.Draw(b)
for j,k in enumerate(ixs):x=j%5*52;y=j//5*92;b.alpha_composite(Image.fromarray(fsall[n][k]).crop((43,8,91,91)),(x,y));dr.text((x,y+83),f'{k+1} {tim[n]["durations_ms"][k]}ms',fill='white')
b.resize((b.width*8,b.height*8),Image.Resampling.NEAREST).save(Q/'skeleton_B_reassemble_front_v4_thread_8x.png')
# Old/new side arms at gameplay size for easy handoff.
b=Image.new('RGBA',(9*104,4*116),'#403D3F');dr=ImageDraw.Draw(b)
for di,d in enumerate(['right','left']):
 for vi,ver in enumerate(['v3','v4']):
  arr=[load(S/f'skeleton_B_{d}.png')]+([load(A/'frames'/f'skeleton_B_walk_{d}_v3'/f'{k+1:02}.png') for k in range(8)] if ver=='v3' else fsall[f'skeleton_B_walk_{d}_v4'])
  for k,a in enumerate(arr):x=k*104;y=(di*2+vi)*116;b.alpha_composite(Image.fromarray(a),(x+4,y+16));dr.text((x+4,y),d+' '+ver if k==0 else str(k),fill='white')
b.resize((b.width*2,b.height*2),Image.Resampling.NEAREST).save(Q/'skeleton_B_walk_side_v3_v4_compare_2x.png')
# Provenance and reproducible native edits.
(V/'production').mkdir(exist_ok=True);(V/'canonical').mkdir(exist_ok=True)
for f in ['build.py','export.py']:shutil.copy2(W/f,V/'production'/f)
for f in ['records.json','new_timing.json','protected.json']:shutil.copy2(W/f,V/f)
for f in ['skeleton_B.png','skeleton_B_back.png','skeleton_B_left.png','skeleton_B_right.png','skeleton_B_remains.png']:shutil.copy2(S/f,V/'canonical'/f)
assert all(Path(p).exists() and sha(p)==h for p,h in protected.items());vf['_old_files']={'protected_count':len(protected),'all_existing_files_unchanged_before_publication':True}
(Q/'skeleton_B_anim_v4_metrics.json').write_text(json.dumps(met,indent=2));(Q/'skeleton_B_anim_v4_verification.json').write_text(json.dumps(vf,indent=2));paths=sorted((O/'frames').glob('*/*.png'));z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1.png'),*map(str,paths)],text=True,capture_output=True);assert z.returncode==0;(Q/'skeleton_B_anim_v4_pixel_check.txt').write_text(z.stdout+z.stderr);print('PASS: 5 actions / 74 frames; exact GIF playback; all walk luma <=2; 41 reassembly transitions <=1000; thread exact 1px path; original files intact.')
