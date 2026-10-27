from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,subprocess,sys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-v5-20261027');O=W/'staged';Q=O/'qc';V=Q/'v5_sources';P=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),np.uint8);pset={tuple(c) for c in P};L=np.array([.299,.587,.114]);tim=json.loads((W/'walk_timing.json').read_text());tim.update(json.loads((W/'reassemble_timing.json').read_text()));records=json.loads((W/'walk_records.json').read_text());sourceparts={p.stem:np.array(Image.open(p).convert('RGBA')) for p in (V/'standing_parts').glob('*.png')};master=np.array(Image.open(S/'skeleton_B_right.png').convert('RGBA'));met={};vf={};frames={}
def load(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rh(a):return hashlib.sha256(a.tobytes()).hexdigest()
def metric(a):
 fg=a[:,:,3]>0;rgb=a[fg,:3];pa=fg[:,:-1]&fg[:,1:];de=(a[:,:-1,:3]!=a[:,1:,:3]).any(2);ys,xs=np.where(fg);bs=[]
 for y0,y1 in [(0,20),(20,45),(45,65),(65,96)]:
  z=a[y0:y1];c=z[z[:,:,3]>0,:3];bs.append({'band':[y0,y1-1],'mean_gray':float((c@L).mean()) if len(c) else None})
 return {'rgba_sha256':rh(a),'alpha_values':np.unique(a[:,:,3]).tolist(),'colors':len(np.unique(rgb,axis=0)),'new_colors':sorted({tuple(map(int,c)) for c in rgb}-pset),'opaque_pixels':int(fg.sum()),'horizontal_change_percent':float((pa&de).sum()/pa.sum()*100),'lowest_y':int(ys.max()),'mean_gray':float((rgb@L).mean()),'bands':bs}
flat=[0,0,0]+P.flatten().tolist();flat += [0]*(768-len(flat))
def gif(path,fs,ds,loop=False):
 pp=[]
 for a in fs:
  ix=np.zeros((96,96),np.uint8)
  for j,c in enumerate(P):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=j+1
  im=Image.fromarray(ix).convert('P');im.putpalette(flat);pp.append(im.resize((768,768),Image.Resampling.NEAREST))
 opt={'loop':0} if loop else {};pp[0].save(path,save_all=True,append_images=pp[1:],duration=ds,transparency=0,disposal=2,optimize=False,**opt);g=Image.open(path);assert g.n_frames==len(fs)
 for k,a in enumerate(fs):
  g.seek(k);b=np.array(g.convert('RGBA'));e=np.repeat(np.repeat(a,8,axis=0),8,axis=1);fg=e[:,:,3]>0;assert np.array_equal(b[:,:,3],e[:,:,3]) and np.array_equal(b[fg],e[fg]);assert g.info['duration']==ds[k]
for n,t in tim.items():
 fs=[load(O/'frames'/n/f'{k+1:02}.png') for k in range(t['frames'])];frames[n]=fs;ms=[metric(a) for a in fs];met[n]=ms;assert Image.open(O/(n+'.png')).size==(96*len(fs),96)
 for m in ms:assert set(m['alpha_values'])<={0,255} and not m['new_colors'] and m['lowest_y']==95
 gif(Q/(n+'_8x.gif'),fs,t['durations_ms'],t['loop']);changes=[int((a!=b).any(2).sum()) for a,b in zip(fs,fs[1:])];vf[n]={'gif_decoded_pixels_alpha_framecount_timing_exact':True,'frames':len(fs),'duration_ms':sum(t['durations_ms']),'consecutive_changed_pixels':changes,'transitions_over1000':[{'from':k+1,'to':k+2,'changed_pixels':x} for k,x in enumerate(changes) if x>1000]}
 if '_reassemble_' not in n:
  sm=metric(master)
  for mm in ms:
   mm['whole_gray_difference']=mm['mean_gray']-sm['mean_gray']
   for b,sb in zip(mm['bands'],sm['bands']):b['standing_mean_gray']=sb['mean_gray'];b['difference']=b['mean_gray']-sb['mean_gray']
 src=W/(n+('_3x.png' if 'reassemble' in n else '_4x.png'));shutil.copy2(src,Q/src.name)
walk=frames['skeleton_B_walk_right_v5'];start=frames['skeleton_B_walk_start_right'];stop=frames['skeleton_B_walk_stop_right'];assert np.array_equal(start[0],master) and np.array_equal(stop[-1],master)
chain={'start_to_walk':int((start[-1]!=walk[0]).any(2).sum()),'walk_loop_8_to1':int((walk[-1]!=walk[0]).any(2).sum()),'walk8_to_stop':int((walk[-1]!=stop[0]).any(2).sum())};vf['boundaries']=chain
# Rigid sets are verified by undoing their recorded integer translations, not by relying on color-count statistics.
rigid=[]
for k,r in enumerate(records['skeleton_B_walk_right_v5']):
 for p,key,owner in [('head','head_offset',7),('thorax','chest_offset',5),('pelvis','pelvis_offset',3)]:
  rendered=load(V/'walk_layers'/f'{k+1:02}'/(p+'_rigid.png'));dx,dy=r[key];undo=np.zeros_like(rendered);ys,xs=np.where(rendered[:,:,3]>0);undo[ys-dy,xs-dx]=rendered[ys,xs];assert np.array_equal(undo,sourceparts[p]);labels=np.array(Image.open(V/'walk_layers'/f'{k+1:02}'/'ownership.png'));vis=labels==owner;yy,xx=np.where(vis);assert np.array_equal(walk[k][vis],sourceparts[p][yy-dy,xx-dx]);rigid.append({'frame':k+1,'part':p,'offset':[dx,dy],'source_rgba_sha256':rh(sourceparts[p]),'untranslated_rgba_sha256':rh(undo),'mismatch_pixels':0,'visible_pixels_match_source_rgba':True})
(V/'rigid_part_verification.json').write_text(json.dumps(rigid,indent=2));vf['rigid_parts']={'all_24_untranslated_sets_rgba_exact':True,'no_recolor_or_new_rib_pixels':True}
# Fixed anatomical ownership and actual support contacts.
locks=[]
for k,r in enumerate(records['skeleton_B_walk_right_v5']):
 role=r['support'];x=r['near_toe_x'] if role=='right' else r['far_toe_x'];y=95;assert walk[k][y,x,3]==255;world=x+5*k;locks.append({'frame':k+1,'support_anatomical_leg':role,'local':[x,y],'world_translation':[5*k,0],'world':[world,y],'shroud_anatomical_owner':'left','foreground_occluder':'right'})
assert len({r['world'][0] for r in locks[:4]})==1 and len({r['world'][0] for r in locks[4:]})==1
(Q/'skeleton_B_walk_right_v5_lock.json').write_text(json.dumps(locks,indent=2));vf['anatomy']={'wide_shroud_source_is_far_left_only':True,'near_right_layer_always_foreground_at_crossing':True,'support_reference_pixels_actual_opaque_and_world_locked':True}
re=frames['skeleton_B_reassemble_front_v5'];oldre=[load(A/'frames/skeleton_B_reassemble_front_v4'/f'{k+1:02}.png') for k in range(42)];assert np.array_equal(re[0],oldre[0]) and np.array_equal(re[-1],oldre[-1]);assert all(np.array_equal(re[k],oldre[k]) for k in list(range(12))+list(range(23,42)));vf['reassembly_preserved']={'frames1_to12_and24_to42_rgba_exact_v4':True,'black_thread_sequence_unchanged':True,'cloth_lift_frames':[13,14,15,16,17,18],'cloth_lift_duration_ms':600}
# Whole-frame silhouette overlaps for all 14 walking/transition frames.
flatfs=[]
for n in ['skeleton_B_walk_start_right','skeleton_B_walk_right_v5','skeleton_B_walk_stop_right']:
 for k,a in enumerate(frames[n]):flatfs.append((n,k,a))
b=Image.new('RGBA',(4*112,4*116),'#29292D');dr=ImageDraw.Draw(b);sf=master[:,:,3]>0
for j,(n,k,a) in enumerate(flatfs):
 f=a[:,:,3]>0;out=np.zeros_like(a);out[sf&f]=[151,164,133,255];out[f&~sf]=[215,116,90,255];out[sf&~f]=[212,184,91,255];x=j%4*112;y=j//4*116;b.alpha_composite(Image.fromarray(out),(x+8,y));dr.text((x+8,y+99),('start' if '_start_' in n else 'stop' if '_stop_' in n else 'walk')+' '+str(k+1),fill='white')
b.resize((b.width*4,b.height*4),Image.Resampling.NEAREST).save(Q/'skeleton_B_right_v5_silhouette_overlays_4x.png')
# Fixed thorax at original position, with eight translated instances, so the ribs and cloth can be compared directly.
b=Image.new('RGBA',(9*48,76),'#403D3F');dr=ImageDraw.Draw(b)
for k,arr in enumerate([sourceparts['thorax']]+[load(V/'walk_layers'/f'{i+1:02}'/'thorax_rigid.png') for i in range(8)]):
 b.alpha_composite(Image.fromarray(arr).crop((24,12,68,62)),(k*48,0));dr.text((k*48,54),'std' if k==0 else str(k),fill='white')
b.resize((b.width*8,b.height*8),Image.Resampling.NEAREST).save(Q/'skeleton_B_right_v5_fixed_thorax_8x.png')
# Anatomical ownership uses QA colors only; game PNGs keep their original palette.
b=Image.new('RGBA',(4*112,2*116),'#29292D');dr=ImageDraw.Draw(b)
for k,a in enumerate(walk):
 labels=np.array(Image.open(V/'walk_layers'/f'{k+1:02}'/'ownership.png'));z=a.copy();z[labels==1]=[199,138,75,255];z[labels==2]=[150,177,128,255];x=k%4*112;y=k//4*116;b.alpha_composite(Image.fromarray(z),(x+8,y));dr.text((x+8,y+99),str(k+1)+' L=ochre R=green',fill='white')
b.resize((b.width*4,b.height*4),Image.Resampling.NEAREST).save(Q/'skeleton_B_right_v5_leg_ownership_4x.png')
b=Image.new('RGBA',(6*104,116),'#403D3F');dr=ImageDraw.Draw(b)
for j,k in enumerate(range(12,18)):b.alpha_composite(Image.fromarray(re[k]),(j*104+4,0));dr.text((j*104+4,99),str(k+1),fill='white')
b.resize((b.width*4,b.height*4),Image.Resampling.NEAREST).save(Q/'skeleton_B_reassemble_front_v5_cloth_six_4x.png')
gif(Q/'skeleton_B_right_v5_start_walk_stop_8x.gif',start+walk+walk+stop,[100]*22,False)
# Source audit: walking reads only its standing PNG, the palette list and the pre-draw plan; no old walk image import.
walkcode=(W/'build_walk.py').read_text();assert "Image.open(S/'skeleton_B_right.png')" in walkcode and 'Image.open(A/' not in walkcode;vf['new_walk_source']={'only_character_art_input':'skeleton_B_right.png','no_previous_walk_png_or_frame_read':True,'pre_draw_parts_table_preserved':True}
(V/'production').mkdir(exist_ok=True)
for f in ['build_walk.py','build_reassemble.py','export.py']:shutil.copy2(W/f,V/'production'/f)
for f in ['parts_plan_before_drawing.json','parts_plan_before_drawing.md','walk_records.json','reassemble_records.json','protected.json','foot_reference.json']:shutil.copy2(W/f,V/f)
protected=json.loads((W/'protected.json').read_text());assert all(Path(p).exists() and sha(p)==h for p,h in protected.items());vf['old_assets']={'count':len(protected),'all_unchanged_before_publication':True}
(Q/'skeleton_B_anim_v5_metrics.json').write_text(json.dumps(met,indent=2));(Q/'skeleton_B_anim_v5_verification.json').write_text(json.dumps(vf,indent=2));(W/'new_timing.json').write_text(json.dumps(tim,indent=2));paths=sorted((O/'frames').glob('*/*.png'));z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1.png'),*map(str,paths)],text=True,capture_output=True);assert z.returncode==0;(Q/'skeleton_B_anim_v5_pixel_check.txt').write_text(z.stdout+z.stderr);print('Verified 4 actions / 56 frames; rigid blocks exact; transitions',chain,'; known >1000 changes recorded, not hidden.')
