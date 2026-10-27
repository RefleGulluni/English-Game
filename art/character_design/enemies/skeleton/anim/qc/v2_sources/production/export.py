from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,subprocess,sys
W=Path('/tmp/english-game-skeleton-v2-20261027');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';O=W/'staged';Q=O/'qc';Q.mkdir(exist_ok=True)
L=np.array([.299,.587,.114]);pal=np.array(json.loads((W/'palette.json').read_text()),np.uint8);pset={tuple(c) for c in pal};tim=json.loads((W/'new_timing.json').read_text());rec=json.loads((W/'records.json').read_text());protected=json.loads((W/'protected.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(a):return hashlib.sha256(a.tobytes()).hexdigest()
def load(p):return np.array(Image.open(p).convert('RGBA'))
def metric(a):
 fg=a[:,:,3]>0;rgb=a[fg,:3];pairs=fg[:,:-1]&fg[:,1:];diff=(a[:,:-1,:3]!=a[:,1:,:3]).any(2);ys,xs=np.where(fg);bands=[]
 for y0,y1 in [(0,20),(20,45),(45,65),(65,96)]:
  b=a[y0:y1];c=b[b[:,:,3]>0,:3];bands.append({'rows':[y0,y1-1],'mean_gray':float((c@L).mean()) if len(c) else None,'highlight_over170_percent':float(((c@L)>170).mean()*100) if len(c) else None})
 return {'rgba_sha256':rgba(a),'colors':len(np.unique(rgb,axis=0)),'new_colors':sorted({tuple(map(int,c)) for c in rgb}-pset),'alpha_values':np.unique(a[:,:,3]).tolist(),'opaque_pixels':int(fg.sum()),'horizontal_change_percent':float((diff&pairs).sum()/pairs.sum()*100) if pairs.any() else 0,'lowest_y':int(ys.max()),'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'bands':bands}
stand={d:load(S/('skeleton_B.png' if d=='front' else f'skeleton_B_{d}.png')) for d in ['front','back','left','right']};pile=np.zeros((96,96,4),np.uint8);pile[48:]=load(S/'skeleton_B_remains.png');allframes={};metrics={};verify={}
# GIF keeps the exact approved palette; transparent index0. No adaptive dithering or optical filtering.
flat=[0,0,0]+pal.flatten().tolist();flat+= [0]*(768-len(flat))
for name,t in tim.items():
 fs=[load(O/'frames'/name/f'{k+1:02}.png') for k in range(t['frames'])];allframes[name]=fs;assert Image.open(O/(name+'.png')).size==(96*len(fs),96);ms=[metric(a) for a in fs];metrics[name]=ms
 for m in ms:assert not m['new_colors'] and set(m['alpha_values'])<={0,255}
 pframes=[]
 for a in fs:
  ix=np.zeros((96,96),np.uint8)
  for j,c in enumerate(pal):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=j+1
  im=Image.fromarray(ix,'P');im.putpalette(flat);pframes.append(im.resize((768,768),Image.Resampling.NEAREST))
 opt={'loop':0} if t['loop'] else {};pframes[0].save(Q/(name+'_8x.gif'),save_all=True,append_images=pframes[1:],duration=t['durations_ms'],transparency=0,disposal=2,optimize=False,**opt)
 gif=Image.open(Q/(name+'_8x.gif'));assert gif.n_frames==len(fs),(name,gif.n_frames,len(fs));gd=[]
 for k,a in enumerate(fs):
  gif.seek(k);b=np.array(gif.convert('RGBA'));expected=np.repeat(np.repeat(a,8,axis=0),8,axis=1);fg=expected[:,:,3]>0;assert np.array_equal(b[:,:,3],expected[:,:,3]);assert np.array_equal(b[fg],expected[fg]);gd.append(gif.info['duration'])
 assert gd==t['durations_ms'];verify[name]={'gif_frames':len(fs),'gif_decoded_rgba_exact':True,'gif_durations_exact':True}
 cols=4 if len(fs)<=8 else 5;rows=(len(fs)+cols-1)//cols;board=Image.new('RGBA',(cols*112,rows*116),'#403D3F');dr=ImageDraw.Draw(board)
 for k,a in enumerate(fs):x=k%cols*112;y=k//cols*116;board.alpha_composite(Image.fromarray(a),(x+8,y));dr.text((x+8,y+99),f'{k+1}: {gd[k]}ms',fill='white')
 board.resize((board.width*4,board.height*4),Image.Resampling.NEAREST).save(Q/(name+'_contact_4x.png'))
 d=name.split('_')[-2]
 if '_idle_' in name:
  assert np.array_equal(fs[0],stand[d]) and np.array_equal(fs[-1],stand[d]);assert all(np.array_equal(a[84:],stand[d][84:]) for a in fs);verify[name].update({'first_last_exact_standard':True,'first_rgba_sha256':rgba(fs[0]),'standard_rgba_sha256':rgba(stand[d]),'feet_y84_plus_exact':True})
 elif '_walk_' in name:
  old=[load(A/'frames'/name.replace('_v2','')/f'{k+1:02}.png') for k in range(8)];assert all(np.array_equal(a[50:,:,3],b[50:,:,3]) for a,b in zip(fs,old));assert all(m['lowest_y']==95 for m in ms);verify[name]['lower_geometry_y50_plus_identical_to_v1']=True
  sm=metric(stand[d]);
  for m in ms:
   for b,sb in zip(m['bands'],sm['bands']):b['standing_mean_gray']=sb['mean_gray'];b['difference']=b['mean_gray']-sb['mean_gray'];assert abs(b['difference'])<=2
  if d in ['left','right']:
   for k,a in enumerate(fs):dy=rec[name][k]['canonical_mask_source_y_offset'];assert np.array_equal(a[21:45,20:77,3],stand[d][21-dy:45-dy,20:77,3])
   verify[name]['chest_silhouette_rows21_to44_matches_registered_standard']=True
 elif '_hit_' in name:
  assert not np.array_equal(fs[0],stand[d]);assert all(np.array_equal(a[84:],stand[d][84:]) for a in fs);verify[name].update({'first_is_immediate_recoil':True,'feet_y84_plus_exact':True})
 else:
  assert np.array_equal(fs[0],pile) and np.array_equal(fs[-1],stand['front']);verify[name].update({'first_exact_padded_remains':True,'last_exact_front_standard':True,'first_rgba_sha256':rgba(fs[0]),'last_rgba_sha256':rgba(fs[-1])})
# Ground positions: read old proof and check actual new pixels, with full sole row retained.
locks={}
for d,proof in [('right','foot_lock.json'),('left','skeleton_B_walk_left_lock.json')]:
 data=json.loads((A/'qc'/proof).read_text());fs=allframes['skeleton_B_walk_'+d+'_v2'];rows=[]
 for k,r in enumerate(data):
  xy=r.get('support_local',r.get('canvas'));world=r.get('support_world',r.get('world'));tx=r['world_translation'][0];x,y=xy;assert fs[k][y,x,3]==255
  if d=='right':sole=(list(range(60,69)) if k<4 else list(range(78,89)))
  else:sole=r['entire_world_sole_x']
  assert all(0<=xx-tx<96 and fs[k][95,xx-tx,3]==255 for xx in sole)
  rows.append({'frame':k+1,'support':r.get('support',r.get('role')),'canvas':xy,'world_translation':r['world_translation'],'world':world,'entire_world_sole_x':sole,'all_sole_pixels_opaque':True})
 for rr in [rows[:4],rows[4:]]:assert len({tuple(r['world']) for r in rr})==1
 locks[d]=rows
(Q/'skeleton_B_walk_side_v2_lock.json').write_text(json.dumps(locks,indent=2))
# Side-by-side standard / original walk / v2: same registration and exact silhouette overlays.
board=Image.new('RGBA',(9*104,4*116),'#403D3F');dr=ImageDraw.Draw(board)
for di,d in enumerate(['left','right']):
 m=stand[d];old=[load(A/'frames'/('skeleton_B_walk_'+d)/f'{k+1:02}.png') for k in range(8)];fs=allframes['skeleton_B_walk_'+d+'_v2']
 for row,arrs,label in [(di*2,[m]+old,d+' STANDARD / V1'),(di*2+1,[m]+fs,d+' STANDARD / V2')]:
  for k,a in enumerate(arrs):board.alpha_composite(Image.fromarray(a),(k*104+4,row*116+16));dr.text((k*104+4,row*116),label if k==0 else str(k),fill='white')
board.resize((board.width*4,board.height*4),Image.Resampling.NEAREST).save(Q/'skeleton_B_walk_side_v2_compare_4x.png')
board=Image.new('RGBA',(8*104,2*116),'#29292D');dr=ImageDraw.Draw(board);widths={}
for di,d in enumerate(['left','right']):
 widths[d]=[];m=stand[d]
 for k,a in enumerate(allframes['skeleton_B_walk_'+d+'_v2']):
  dy=rec['skeleton_B_walk_'+d+'_v2'][k]['canonical_mask_source_y_offset'];fg=a[:,:,3]>0;im=np.zeros_like(a);im[fg]=[6,6,9,255]
  roi=fg[21:45,20:77];std=m[21-dy:45-dy,20:77,3]>0;im[21:45,20:77][std&roi]=[116,165,113,255];im[21:45,20:77][roi&~std]=[255,68,70,255];im[21:45,20:77][std&~roi]=[225,190,80,255];board.alpha_composite(Image.fromarray(im),(k*104+4,di*116+16));dr.text((k*104+4,di*116),f'{d} {k+1}',fill='white')
  ww=[int(np.ptp(np.where(row)[0])+1) if row.any() else 0 for row in roi];widths[d].append({'frame':k+1,'registered_dy':dy,'mask_mismatches':int((roi!=std).sum()),'row_widths_y21_44':ww,'max_width_including_arm':max(ww)})
board.resize((board.width*8,board.height*8),Image.Resampling.NEAREST).save(Q/'skeleton_B_walk_side_v2_silhouette_8x.png')
(Q/'skeleton_B_walk_side_v2_silhouette.json').write_text(json.dumps(widths,indent=2))
# Bone source and destination correspondence; original inventory is a complete partition.
groups={p.stem:load(p) for p in (W/'bone_groups').glob('*.png')};assert sum(int((a[:,:,3]>0).sum()) for a in groups.values())==int((pile[:,:,3]>0).sum())
colors=['#CF5354','#D9A34D','#7AAD70','#7BAABF','#A18CC5','#C682AA','#A5A568','#CE9573','#639C91','#8D97CB','#B0A094'];names=list(groups);dest={'skull':(49,9),'rib_tip':(53,24),'shoulder_nails':(37,18),'shroud':(48,40),'ribs':(51,30),'left_arm':(66,43),'left_leg':(59,77),'right_arm':(31,45),'right_leg':(36,77),'pelvis':(47,49),'small_bones':(47,60)}
board=Image.new('RGBA',(720,480),'#403D3F');dr=ImageDraw.Draw(board);scale=3
board.alpha_composite(Image.fromarray(pile).resize((288,288),Image.Resampling.NEAREST),(12,10));board.alpha_composite(Image.fromarray(stand['front']).resize((288,288),Image.Resampling.NEAREST),(408,10))
for j,n in enumerate(names):
 ys,xs=np.where(groups[n][:,:,3]>0);cx=int(np.mean(xs));cy=int(np.mean(ys));x,y=dest[n];c=colors[j%len(colors)];p1=(12+cx*3,10+cy*3);p2=(408+x*3,10+y*3);dr.line([p1,p2],fill=c,width=1);dr.ellipse((p1[0]-3,p1[1]-3,p1[0]+3,p1[1]+3),fill=c);dr.ellipse((p2[0]-3,p2[1]-3,p2[0]+3,p2[1]+3),fill=c);dr.text((12+(j%3)*235,320+(j//3)*30),str(j+1)+' '+n,fill=c)
dr.text((12,455),'Semantic correspondence, not a per-pixel anatomical reconstruction.',fill='white');board.save(Q/'skeleton_B_reassemble_map_v2.png')
# New source provenance: raw sheets + recovered grids; prove every opaque restored cell is a source center sample.
V=Q/'v2_sources';V.mkdir(exist_ok=True);sourceproof={}
for mode in ['ground','rise','settle']:
 D=V/mode;D.mkdir(exist_ok=True);g=json.loads((W/mode/'grid.json').read_text());src=Path(g[0]['source']);shutil.copy2(src,D/'generated_raw.png');shutil.copy2(W/mode/'grid.json',D/'grid.json');shutil.copy2(W/(mode+'_native_3x.png'),D/'restored_contact_3x.png');raw=np.array(Image.open(src).convert('RGB'));cnt=0
 for r in g:
  a=load(W/mode/f'frame_{r["frame"]:02}.png');xs=r['x_boundaries'];ys=r['y_boundaries'];ox,oy=r['crop_offset'];
  for y,x in zip(*np.where(a[:,:,3]>0)):
   sx=(xs[x]+xs[x+1])//2+ox;sy=(ys[y]+ys[y+1])//2+oy;assert np.array_equal(a[y,x,:3],raw[sy,sx]);cnt+=1
  shutil.copy2(W/mode/f'frame_{r["frame"]:02}.png',D/f'frame_{r["frame"]:02}.png')
 sourceproof[mode]={'restored_frames':len(g),'opaque_cell_centers_verified':cnt,'every_opaque_rgb_exact_source_center':True,'nominal_cell_px':g[0]['period'],'raw_sha256':sha(src),'note':'Generated grid is locally irregular; explicit cell boundaries retained. No full-image scaling.'}
for f in ['records.json','prompts.json','palette.json','bone_groups.json','protected.json']:shutil.copy2(W/f,V/f)
shutil.copytree(W/'bone_groups',V/'bone_groups',dirs_exist_ok=True);(V/'production').mkdir(exist_ok=True)
for f in ['build.py','recover.py','export.py']:shutil.copy2(W/f,V/'production'/f)
changed=[p for p,h in protected.items() if not Path(p).exists() or sha(p)!=h];assert not changed,changed
verify['_protected_existing_files']={'count':len(protected),'all_unchanged_before_publication':True};verify['_source_grid']=sourceproof
(Q/'skeleton_B_anim_v2_metrics.json').write_text(json.dumps(metrics,indent=2));(Q/'skeleton_B_anim_v2_verification.json').write_text(json.dumps(verify,indent=2));(Q/'skeleton_B_anim_v2_ground_inventory.json').write_text(json.dumps([{'frame':k+1,'duration_ms':tim['skeleton_B_reassemble_front_v2']['durations_ms'][k],**r} for k,r in enumerate(rec['skeleton_B_reassemble_front_v2'])],indent=2))
print('EXPORT PASS:',len(tim),'actions;',sum(len(fs) for fs in allframes.values()),'frames; all GIFs decode exactly; old files unchanged:',len(protected))
