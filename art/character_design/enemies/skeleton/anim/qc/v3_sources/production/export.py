from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,subprocess,sys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-v3-20261027');O=W/'staged';Q=O/'qc';L=np.array([.299,.587,.114]);pal=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),np.uint8);pset={tuple(c) for c in pal};tim=json.loads((W/'new_timing.json').read_text());rec=json.loads((W/'records.json').read_text());protected=json.loads((W/'protected.json').read_text())
def load(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rh(a):return hashlib.sha256(a.tobytes()).hexdigest()
def metric(a):
 fg=a[:,:,3]>0;rgb=a[fg,:3];pairs=fg[:,:-1]&fg[:,1:];diff=(a[:,:-1,:3]!=a[:,1:,:3]).any(2);ys,xs=np.where(fg);bs=[]
 for y0,y1 in [(0,20),(20,45),(45,65),(65,96)]:
  b=a[y0:y1];c=b[b[:,:,3]>0,:3];bs.append({'band':[y0,y1-1],'mean_gray':float((c@L).mean()) if len(c) else None})
 return {'rgba_sha256':rh(a),'alpha_values':np.unique(a[:,:,3]).tolist(),'colors':len(np.unique(rgb,axis=0)),'new_colors':sorted({tuple(map(int,c)) for c in rgb}-pset),'horizontal_change_percent':float((pairs&diff).sum()/pairs.sum()*100),'lowest_y':int(ys.max()),'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'bands':bs}
flat=[0,0,0]+pal.flatten().tolist();flat += [0]*(768-len(flat));fsall={};met={};ver={};locks=json.loads((A/'qc/skeleton_B_walk_side_v2_lock.json').read_text())
for n,t in tim.items():
 fs=[load(O/'frames'/n/f'{i+1:02}.png') for i in range(t['frames'])];fsall[n]=fs;ms=[metric(a) for a in fs];met[n]=ms;assert Image.open(O/(n+'.png')).size==(len(fs)*96,96)
 for q in ms:assert set(q['alpha_values'])<={0,255} and not q['new_colors'] and q['lowest_y']==95
 pp=[]
 for a in fs:
  ix=np.zeros((96,96),np.uint8)
  for j,c in enumerate(pal):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=j+1
  im=Image.fromarray(ix).convert('P');im.putpalette(flat);pp.append(im.resize((768,768),Image.Resampling.NEAREST))
 opt={'loop':0} if t['loop'] else {};pp[0].save(Q/(n+'_8x.gif'),save_all=True,append_images=pp[1:],duration=t['durations_ms'],transparency=0,disposal=2,optimize=False,**opt);g=Image.open(Q/(n+'_8x.gif'));assert g.n_frames==len(fs)
 for k,a in enumerate(fs):
  g.seek(k);b=np.array(g.convert('RGBA'));expected=np.repeat(np.repeat(a,8,axis=0),8,axis=1);fg=expected[:,:,3]>0;assert np.array_equal(b[:,:,3],expected[:,:,3]) and np.array_equal(b[fg],expected[fg]);assert g.info['duration']==t['durations_ms'][k]
 ver[n]={'gif_decoded_rgba_and_durations_exact':True,'frames':len(fs),'total_ms':sum(t['durations_ms'])}
 shutil.copy2(W/(n+'_3x.png'),Q/(n+'_contact_3x.png'))
 if '_walk_' in n:
  d=n.split('_')[-2];m=load(S/f'skeleton_B_{d}.png');mm=metric(m);old=[load(A/'frames'/n.replace('_v3','_v2')/f'{k+1:02}.png') for k in range(8)]
  for k,(a,b) in enumerate(zip(fs,old)):
   assert np.array_equal(a[:45],b[:45]);assert np.array_equal(a[84:],b[84:]);mask=load(Q/'v3_sources/walk_layers'/d/f'{k+1:02}_bare_leg_protected.png')[:,:,3]>0;assert np.array_equal(a[mask],b[mask]);assert not (a[43:57,40:60,3]>0).sum(axis=1).min()==0
   for q,z in zip(ms[k]['bands'],mm['bands']):q['standing_mean_gray']=z['mean_gray'];q['difference']=q['mean_gray']-z['mean_gray'];assert abs(q['difference'])<=2,(n,k,q)
   for xx in locks[d][k]['entire_world_sole_x']:assert a[95,xx-locks[d][k]['world_translation'][0],3]==255
  ver[n].update({'upper_y0_44_exact_v2':True,'feet_y84_95_rgba_exact_v2':True,'bare_leg_protected_pixels_rgba_exact_v2':True,'support_ground_positions_exact_v2':True,'no_empty_horizontal_waist_row_y43_to56':True})
 else:
  pile=np.zeros((96,96,4),np.uint8);pile[48:]=load(S/'skeleton_B_remains.png');assert np.array_equal(fs[0],pile);assert np.array_equal(fs[-1],load(S/'skeleton_B.png'))
  assert all(np.array_equal(fs[k+22],load(A/'frames/skeleton_B_reassemble_front_v2'/f'{k+17:02}.png')) for k in range(4));ver[n].update({'first_exact_padded_remains':True,'last_exact_standard':True,'last_four_frames_exact_v2_17_to20':True})
  ver[n]['consecutive_rgba_changed_pixels']=[int((a!=b).any(2).sum()) for a,b in zip(fs,fs[1:])]
(Q/'skeleton_B_walk_side_v3_lock.json').write_text(json.dumps(locks,indent=2))
# Standard/V2/V3 whole silhouettes and waist/hem close-ups, with no resampling of sprite pixels.
b=Image.new('RGBA',(9*104,6*116),'#403D3F');dr=ImageDraw.Draw(b)
for j,d in enumerate(['left','right']):
 for r,vers in enumerate(['standard','v2','v3']):
  arr=[load(S/f'skeleton_B_{d}.png')]+([load(A/'frames'/f'skeleton_B_walk_{d}_v2'/f'{k+1:02}.png') for k in range(8)] if vers=='v2' else fsall[f'skeleton_B_walk_{d}_v3'] if vers=='v3' else [load(S/f'skeleton_B_{d}.png')]*8)
  for k,a in enumerate(arr):x=k*104;y=(j*3+r)*116;b.alpha_composite(Image.fromarray(a),(x+4,y+16));dr.text((x+4,y),f'{d} {vers}' if k==0 else str(k),fill='white')
b.resize((b.width*2,b.height*2),Image.Resampling.NEAREST).save(Q/'skeleton_B_walk_cloth_v2_v3_compare_2x.png')
for d in ['left','right']:
 b=Image.new('RGBA',(4*48,2*56),'#403D3F');dr=ImageDraw.Draw(b)
 for k,a in enumerate(fsall[f'skeleton_B_walk_{d}_v3']):x=k%4*48;y=k//4*56;b.alpha_composite(Image.fromarray(a).crop((24,38,72,88)),(x,y));dr.text((x,y+45),str(k+1),fill='white')
 b.resize((b.width*8,b.height*8),Image.Resampling.NEAREST).save(Q/f'skeleton_B_walk_{d}_v3_waist_8x.png')
# Expanded rise and four-frame skull path strips.
for label,ixs in [('rise',list(range(8,18))),('skull',list(range(17,23)))]:
 n='skeleton_B_reassemble_front_v3';b=Image.new('RGBA',(len(ixs)*104,116),'#403D3F');dr=ImageDraw.Draw(b)
 for j,k in enumerate(ixs):b.alpha_composite(Image.fromarray(fsall[n][k]),(j*104+4,0));dr.text((j*104+4,99),f'{k+1} {tim[n]["durations_ms"][k]}ms',fill='white')
 b.resize((b.width*4,b.height*4),Image.Resampling.NEAREST).save(Q/f'skeleton_B_reassemble_front_v3_{label}_4x.png')
# All recoverable anatomy sources retained, no generated broad torso used in this revision.
V=Q/'v3_sources';(V/'production').mkdir(exist_ok=True)
for f in ['build.py','export.py']:shutil.copy2(W/f,V/'production'/f)
for f in ['protected.json','records.json','new_timing.json']:shutil.copy2(W/f,V/f)
for d in ['left','right']:shutil.copy2(W/(d+'_cloth_source.png'),V/(d+'_canonical_cloth.png'))
ver['_old_files']={'count':len(protected),'all_unchanged_before_publication':all(Path(p).exists() and sha(p)==h for p,h in protected.items())};assert ver['_old_files']['all_unchanged_before_publication']
(Q/'skeleton_B_anim_v3_metrics.json').write_text(json.dumps(met,indent=2));(Q/'skeleton_B_anim_v3_verification.json').write_text(json.dumps(ver,indent=2));files=sorted((O/'frames').glob('*/*.png'));z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1.png'),*map(str,files)],text=True,capture_output=True);assert z.returncode==0;(Q/'skeleton_B_anim_v3_pixel_check.txt').write_text(z.stdout+z.stderr);print('PASS: 3 actions / 42 frames, GIF pixels/timing exact, walking luma differences <=2, old files intact')
