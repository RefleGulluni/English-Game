from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-v3-20261027');O=W/'staged';F=O/'frames';F.mkdir(parents=True,exist_ok=True);Q=O/'qc';Q.mkdir(exist_ok=True)
P=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),int);L=np.array([.299,.587,.114]);stand={d:np.array(Image.open(S/('skeleton_B.png' if d=='front' else f'skeleton_B_{d}.png')).convert('RGBA')) for d in ['front','left','right']};ALL={};rec={};tim={}
def load(p):return np.array(Image.open(p).convert('RGBA'))
def put(a,b,dx=0,dy=0):
 ys,xs=np.where(b[:,:,3]>0);xx=xs+dx;yy=ys+dy;ok=(xx>=0)&(xx<96)&(yy>=0)&(yy<96);a[yy[ok],xx[ok]]=b[ys[ok],xs[ok]]
def codes(a):return ((a[:,:,:3,None].transpose(0,1,3,2)-P[None,None])**2).sum(3).argmin(2)
def dilate(m,n=1):
 a=m.copy()
 for i in range(n):
  b=np.pad(a,1);a=np.logical_or.reduce([b[dy:dy+96,dx:dx+96] for dy in range(3) for dx in range(3)])
 return a
def strip(a,mask):b=np.zeros_like(a);b[mask]=a[mask];return b
def save(n,fs,ds,loop,rs):
 ALL[n]=fs;rec[n]=rs;tim[n]={'frames':len(fs),'durations_ms':ds,'loop':loop,'sprite_sheet':n+'.png'};D=F/n;D.mkdir(exist_ok=True);sheet=Image.new('RGBA',(len(fs)*96,96))
 for k,a in enumerate(fs):im=Image.fromarray(a);im.save(D/f'{k+1:02}.png');sheet.alpha_composite(im,(k*96,0))
 sheet.save(O/(n+'.png'))
# Select the fabric pixels, preserving exposed bone kernels and their native one-pixel material rim.
boneids=[*range(37,48)];clothids=[20,21,23,25,*range(26,34),36]
def lower_material(a,y0=45):
 ids=codes(a);fg=a[:,:,3]>0;bonecore=fg&np.isin(ids,boneids);bone=dilate(bonecore,1)&fg;bone|=dilate(bonecore,2)&fg&np.isin(ids,[18,19,22,24,34,35]);bone[:y0]=False
 # Tiny isolated warm highlights in the old flag are cloth, not detached bones.
 seen=set();keep=np.zeros_like(bone)
 for yy,xx in zip(*np.where(bone)):
  if (yy,xx) in seen:continue
  stack=[(int(yy),int(xx))];seen.add((int(yy),int(xx)));comp=[]
  while stack:
   y,x=stack.pop();comp.append((y,x))
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     q=(y+dy,x+dx)
     if 0<=q[0]<96 and 0<=q[1]<96 and bone[q] and q not in seen:seen.add(q);stack.append(q)
  if len(comp)>=28 or max(y for y,x in comp)>=84:
   for y,x in comp:keep[y,x]=True
 bone=keep;cloth=fg&~bone;cloth[:y0]=False
 return bone,cloth
# Canonical cloth is explicitly selected by its drawn path, not a new geometric texture.
clothmasks={}
for d in ['left','right']:
 m=stand[d];ids=codes(m);fg=m[:,:,3]>0;bone,cloth=lower_material(m)
 if d=='right':
  # lower shroud lies at x46..64, with bare near leg on screen left, far shin visible through its tear.
  roi=np.zeros((96,96),bool)
  for y in range(45,84):roi[y,46 if y<58 else 47:65]=True
 else:
  roi=np.zeros((96,96),bool)
  for y in range(45,84):roi[y,40:54]=True
 cm=roi&fg&~bone;clothmasks[d]=cm;Image.fromarray(strip(m,cm)).save(W/(d+'_cloth_source.png'))
# Hand-traced anatomical envelopes exclude the old cloth's warm flecks; they do not move a bone.
legpaths={
 'right':[
  [[47,53,56,57,60],[43,40,39,37,35]],[[47,50,50,53,55],[43,43,44,41,39]],[[49,50,50,50,51],[43,44,47,47,44]],[[46,46,43,43,46],[43,44,47,49,51]],
  [[46,46,42,40,42],[43,44,49,51,54]],[[49,51,47,43,47],[43,43,49,49,50]],[[49,50,51,50,45],[43,43,48,51,54]],[[47,53,56,55,56],[43,42,42,40,40]]],
 'left':[
  [[53,53,51,57,58],[42,39,39,34,34]],[[54,53,51,54,54],[42,39,39,38,37]],[[54,53,52,53,50],[42,39,39,39,39]],[[54,54,52,53,52],[42,40,37,40,42]],
  [[54,54,52,55,56],[42,40,37,38,38]],[[54,54,54,53,55],[42,41,40,41,43]],[[57,57,55,53,51],[43,42,41,46,48]],[[53,53,51,55,55],[42,39,40,37,37]]]
}
def anatomy_envelope(d,k):
 roi=np.zeros((96,96),bool)
 for centers in legpaths[d][k]:
  for y in range(45,84):
   x=round(np.interp(y,[45,55,64,73,83],centers));roi[y,max(0,x-5):min(96,x+6)]=True
 if d=='right':roi[45:59,27:45]=True
 else:roi[45:61,49:63]=True
 roi[84:]=True
 return roi
for d in ['left','right']:
 fs=[];rs=[];m=stand[d];source=strip(m,clothmasks[d]);old=[load(A/'frames'/('skeleton_B_walk_'+d+'_v2')/f'{k+1:02}.png') for k in range(8)];sg=-1 if d=='right' else 1
 # Delayed hem response; upper edge stays at the waist, only lower rows trail behind the gait.
 lag=[0,0,1,2,1,0,-1,0]
 for k,a0 in enumerate(old):
  a=a0.copy();bones,oldcloth=lower_material(a,45);bones &= anatomy_envelope(d,k);oldcloth=(a[:,:,3]>0)&~bones;oldcloth[:45]=False;a[oldcloth]=0;fabric=np.zeros_like(a);coords=[]
  for y,x in zip(*np.where(source[:,:,3]>0)):
   ankles=([35.5,40.5,45.5,50.5,55.5,50.5,45.5,40.5] if d=='right' else [38,43,48,53,58,53,48,43]);target=.75*ankles[k]+.25*ankles[(k-1)%8];bend=round((target-(57 if d=='right' else 53))*max(0,min(1,(y-48)/32)));dy=0 if y<58 else ([0,0,0,-1,0,0,1,0][k] if y<81 else 0);xx=x+bend;yy=y+dy
   if 0<=xx<96 and 45<=yy<84:fabric[yy,xx]=source[y,x];coords.append([int(x),int(y),int(xx),int(yy)])
  # Fabric is behind the original visible bones; no leg/foot pixel is moved or recolored.
  # The shroud covers its wrapped leg, while the bare leg and hand remain in front.
  bare=np.zeros((96,96),bool)
  for yy in range(45,84):
   xx=round(np.interp(yy,[45,55,64,73,83],legpaths[d][k][0]));bare[yy,max(0,xx-5):min(96,xx+6)]=True
  if d=='right':bare[45:59,27:45]=True
  else:bare[45:61,49:63]=True
  frontbone=bones&bare
  mask=(fabric[:,:,3]>0)&~frontbone; a[mask]=fabric[mask];a[:45]=a0[:45];a[84:]=a0[84:]
  # Continue the same drawn fold at waist y44/45. Fill a missing fabric edge using its own adjacent native pixel only.
  joins=[]
  for y in range(45,53):
   for x in range(40,60):
    if a[y,x,3]==0 and a[y-1,x,3]>0 and codes(a[y-1:y].repeat(96,axis=0))[0,x] in clothids and fabric[min(83,y+1),x,3]>0:
     a[y,x]=fabric[y+1,x];mask[y,x]=True;joins.append([x,y])
  # Brightness correction is restricted to the replaced fabric. The accepted head/torso/bones stay byte-identical.
  tones=[]
  for y0,y1 in [(45,65),(65,96)]:
   rr=(m[y0:y1]);target=float((rr[rr[:,:,3]>0,:3]@L).mean());region=a[y0:y1];edit=mask[y0:y1]&(region[:,:,3]>0);orig=region[edit,:3].copy();fg=region[:,:,3]>0;best=None;cp=P[np.array(clothids+[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17])]
   for off in np.arange(-125,60.1,.5):
    rgb=np.clip(orig.astype(float)+off,0,255);out=cp[((rgb[:,None]-cp[None])**2).sum(2).argmin(1)];probe=region.copy();probe[edit,:3]=out;mean=float((probe[fg,:3]@L).mean());cost=float(((out-orig.astype(float))**2).mean()) if len(orig) else 0;key=(max(0,abs(mean-target)-1.8),cost)
    if best is None or key<best[0]:best=(key,out,mean,float(off))
   region[edit,:3]=best[1];tones.append({'band':[y0,y1-1],'standing_mean':target,'mean':best[2],'difference':best[2]-target,'cloth_only_rgb_offset':best[3]})
  assert np.array_equal(a[:45],a0[:45]);assert np.array_equal(a[frontbone],a0[frontbone]);assert np.array_equal(a[84:],a0[84:]);fs.append(a);rs.append({'frame':k+1,'upper_y0_44_exact_v2':True,'protected_leg_bone_pixels':int(frontbone.sum()),'wrapped_leg_occluded_by_cloth_pixels':int((bones&mask).sum()),'hem_target_x':target,'removed_old_fabric_pixels':int(oldcloth.sum()),'new_fabric_pixels':int(mask.sum()),'hem_lag_px':lag[k]*sg,'waist_joins':joins,'tones':tones,'source_pixel_positions':coords})
  Image.fromarray(strip(a0,bones)).save(W/f'{d}_boneprotect_{k+1:02}.png')
  D=Q/'v3_sources'/'walk_layers'/d;D.mkdir(parents=True,exist_ok=True)
  Image.fromarray(strip(a0,bones)).save(D/f'{k+1:02}_leg_before_cloth.png');Image.fromarray(strip(a0,frontbone)).save(D/f'{k+1:02}_bare_leg_protected.png');Image.fromarray(fabric).save(D/f'{k+1:02}_cloth_underlay.png')
 save('skeleton_B_walk_'+d+'_v3',fs,[100]*8,True,rs)
# Reassembly: source anatomy is the approved B, no wide generated rising body is reused.
m=stand['front'];pile=np.zeros_like(m);pile[48:]=load(S/'skeleton_B_remains.png');G={p.stem:load(p) for p in (A/'qc/v2_sources/bone_groups').glob('*.png')};order=['small_bones','pelvis','right_leg','left_leg','ribs','left_arm','right_arm','rib_tip','shoulder_nails','shroud','skull'];offsets={n:[0,0] for n in G}
hm=np.zeros((96,96),bool)
for y,xmin in enumerate([45,43,42,42,41,42,41,41,42,42,42,43,44,44,44,45]):hm[y,xmin:59]=True
head=strip(m,hm);bodybase=m.copy();bodybase[hm]=0
# Keep the turned original-size skull from the accepted V2 wake study, on exactly the same ground spot.
turned=np.zeros_like(m);v=load(A/'frames/skeleton_B_reassemble_front_v2/03.png');turned[67:90,68:88]=v[67:90,68:88]
def floor_pose(active,turn=True):
 a=np.zeros_like(m)
 for n in order:
  if n in active:put(a,turned if n=='skull' and turn else G[n],*offsets[n])
 return a
# Canonical shroud/skin partitions, stored in QC to make the native posing reviewable.
frontids=codes(m);clothroi=np.zeros((96,96),bool)
for y in range(45,84):clothroi[y,40 if y<57 else 43:68]=True
bone,cl=lower_material(m);frontcloth=clothroi&(m[:,:,3]>0)&~bone
# Piecewise row registration uses only existing canonical pixels, preserves art marks, and foreshortens shafts with explicit row selections.
def choose_rows(start,end,target,protected_rows=()):
 rows=list(range(start,end));target=max(1,target)
 while len(rows)>target:
  pool=[j for j in range(1,len(rows)-1) if rows[j] not in protected_rows]
  if not pool:pool=list(range(1,len(rows)-1))
  if not pool:break
  j=pool[(len(rows)*7)%len(pool)];rows.pop(j)
 return rows

def rise_pose(delta,stage,upper=2):
 a=np.zeros_like(m);ledger=[]
 # Feet stay planted. The pelvis rises first; two knees remain staggered and spread, not a vertical scale change.
 a[84:]=m[84:]
 thightop=55+round(delta*.68);kneey=67+round(delta*.42);shiny=84
 for side,(x0,x1,sg) in enumerate([(26,48,-1),(48,73,1)]):
  if stage==0 and side==1:continue
  knee=round(6*delta/27);throws=choose_rows(55,68,max(5,kneey-thightop),[55,56,64,65,66,67]);shrows=choose_rows(68,84,max(4,84-kneey),[68,69,81,82,83])
  for part,rows,ty in [('thigh',throws,thightop),('shin',shrows,kneey)]:
   for j,sy in enumerate(rows):
    yy=ty+j
    if yy>=84:continue
    taper=(j/max(1,len(rows)-1)) if part=='thigh' else (1-j/max(1,len(rows)-1));dx=round(sg*knee*taper)
    for x in range(x0,x1):
     if m[sy,x,3] and not frontcloth[sy,x]:
      xx=x+dx
      if 0<=xx<96:a[yy,xx]=m[sy,x]
   ledger.append({'side':side,'part':part,'source_rows':rows,'target_start_y':ty,'knee_out_px':sg*knee})
 # Pelvis and waist: native pixels, lowered as one set until the structure hauls them up.
 for y in range(45,55):
  for x in range(35,61):
   if m[y,x,3] and not frontcloth[y,x]:a[y+delta,x+1]=m[y,x]
 # Fabric hangs diagonally from the same waist; folded rows remain near the ground until lifted.
 rows=choose_rows(45,84,max(13,39-delta),[45,46,47,62,63,73,74,80,81,82,83])
 for j,y in enumerate(rows):
  yy=45+delta+j
  if yy>=84:continue
  dx=1+round(2*delta/27*j/max(1,len(rows)-1))
  for x in range(38,69):
   if frontcloth[y,x] and not (a[yy,min(95,x+dx),3]>0):a[yy,x+dx]=m[y,x]
 ledger.append({'part':'shroud_waist_to_shin','source_rows':rows,'target_start_y':45+delta})
 # Add spine, rib cage, then shoulder/shroud and asynchronous arms. All from B, never the rejected broad body.
 if stage>=1:
  top=45 if stage<=2 else 16
  for y in range(top,45):
   for x in range(25,73):
    if not bodybase[y,x,3]:continue
    if stage<3 and (x<39 or x>59):continue
    if stage==3 and x>=61:continue
    yy=y+delta;xx=x+upper
    if 0<=yy<96 and 0<=xx<96:a[yy,xx]=bodybase[y,x]
 # Stack the actual bare spine and ribs from the same B's back view while its diagonal shroud is still being hauled up.
 if stage in [1,2]:
  back=load(S/'skeleton_B_back.png');bc=codes(back);y0=27 if stage==1 else 18
  for y in range(y0,36):
   for x in range(42,51 if stage==1 else 54):
    if back[y,x,3] and (bc[y,x]>=18):
     yy=y+delta+8
     if yy<96:a[yy,x+upper]=back[y,x]
 # The late-arriving arm remains suspended 2px below shoulder level, caught next frame.
 if stage>=4:
  for y in range(28,59):
   for x in range(60,70):
    if m[y,x,3]:
     yy=y+delta+(2 if stage==4 else 0)
     if yy<96:a[yy,x+upper]=m[y,x]
 return a,ledger
# Reuse the accepted late native pose helper, not any V2 generated rising frames.
s=(A/'qc/v2_sources/production/build.py').read_text();helper=s[s.index('def crooked_standard('):s.index('# Reassembly v2:')]
# Helpers used by the canonical late-pose routine.
def map_pixels(src,fn):
 a=np.zeros_like(src)
 for y,x in zip(*np.where(src[:,:,3]>0)):
  xx,yy=fn(int(x),int(y))
  if 0<=xx<96 and 0<=yy<96:a[yy,xx]=src[y,x]
 return a
def bridge(a):
 for y in range(36,65):
  if not (a[y,40:59,3]>0).any():a[y,40:59]=a[y-1,40:59]
def patch(a,box,dx=0,dy=0,erase=True):
 b=a.copy();x0,y0,x1,y1=box;p=a[y0:y1,x0:x1].copy()
 if erase:b[y0:y1,x0:x1]=0
 put(b,p,x0+dx,y0+dy);return b
exec(helper)
fs=[pile.copy()];rs=[{'phase':'wake','ground_groups':order.copy(),'exact_padded_remains':True}];active=set(order)
# Larger native 2-4px pulls, one or two groups at a time, with no whole-pile disappearance.
events=[{'shroud':[-2,0],'rib_tip':[2,0]},{'rib_tip':[0,0]}, {'left_arm':[4,-1]}, {'left_leg':[4,-2],'shroud':[-3,-1]}, {'right_arm':[-4,0],'ribs':[0,-3]}, {'shoulder_nails':[3,2],'right_leg':[-4,-2]}, {'pelvis':[0,-4],'shroud':[-3,-3]}]
for j,e in enumerate(events):
 offsets.update(e);a=floor_pose(active,turn=j>=1);fs.append(a);rs.append({'phase':'wake' if j<2 else 'gather','ground_groups':order.copy(),'changed_group_offsets':e,'ground_offsets':{n:offsets[n].copy() for n in order}})
# 4 canonical crouch frames + 3 newly inserted half-rise frames; no style/anatomy switch at the former F12->13 join.
deltas=[27,23,19,15,11,7,3];removed=[['pelvis','left_leg'],['right_leg'],['ribs','left_arm'],['shoulder_nails','rib_tip'],['right_arm'],['small_bones'],['shroud']]
for j,delta in enumerate(deltas):
 for n in removed[j]:active.discard(n)
 a=floor_pose(active);body,ledger=rise_pose(delta,j);put(a,body);fs.append(a);rs.append({'phase':'pelvis_rise' if j<2 else 'stack_and_half_rise','canonical_source':str(S/'skeleton_B.png'),'pelvis_delta_y':delta,'native_piece_registration':ledger,'ground_groups':sorted(active),'removed_from_ground':removed[j]})
for j in range(2):
 a=floor_pose({'skull'});body=crooked_standard(True,2,1,2)
 if j==1:body=patch(body,(31,43,39,60),1,0)
 put(a,body);fs.append(a);rs.append({'phase':'headless_settle','ground_groups':['skull'],'canonical_crooked_pose':True})
a=floor_pose({'skull'});body=crooked_standard(True,2,1,2);put(a,body);fs.append(a);rs.append({'phase':'headless_pause','ground_groups':['skull']})
# Four readable head flight poses: ground origin -> airborne -> fastest snap/overshoot -> return to neck.
for j,(dx,dy) in enumerate([(-5,-19),(-14,-43)]):
 a=crooked_standard(True,2,1,2);put(a,turned,dx,dy);fs.append(a);rs.append({'phase':'skull_flight','skull_source_ground_bbox':[68,67,88,90],'skull_offset_from_ground':[dx,dy],'ground_groups':[]})
for headx,heady,event in [(3,1,'60ms snap with lateral overshoot'),(2,2,'90ms return to crooked neck')]:
 a=crooked_standard(False,2,1,2,headx,heady)
 # Shroud still one pixel below nails until the following crooked hold catches it.
 x0,x1=34,45;region=a[21:31,x0:x1].copy();mask=(region[:,:,3]>0)&((region[:,:,:3]@L)<175);piece=np.zeros_like(region);piece[mask]=region[mask];a[21:31,x0:x1][mask]=0;put(a,piece,x0,22)
 fs.append(a);rs.append({'phase':'skull_snap_and_return','head_offset':[headx,heady],'event':event,'ground_groups':[]})
# Keep the accepted crooked catch and interrupted straightening poses unchanged.
for k in range(17,21):
 fs.append(load(A/'frames/skeleton_B_reassemble_front_v2'/f'{k:02}.png'));rs.append({'phase':'crooked_catch_and_tugs','exact_v2_source_frame':k,'ground_groups':[]})
ds=[340,160,100,170,130,150,130,120]+[110,140,120,100,90,90,100]+[90,90,130]+[100,100,60,90]+[150,110,110,100]
assert len(fs)==len(ds)==26 and sum(ds)==3180
save('skeleton_B_reassemble_front_v3',fs,ds,False,rs)
for n,arr in ALL.items():
 cols=4 if len(arr)<=8 else 7;rows=(len(arr)+cols-1)//cols;b=Image.new('RGBA',(cols*112,rows*116),'#403D3F');dr=ImageDraw.Draw(b)
 for k,a in enumerate(arr):x=k%cols*112;y=k//cols*116;b.alpha_composite(Image.fromarray(a),(x+8,y));dr.text((x+8,y+99),str(k+1)+' '+str(tim[n]['durations_ms'][k])+'ms',fill='white')
 b.resize((b.width*3,b.height*3),Image.Resampling.NEAREST).save(W/(n+'_3x.png'))
(W/'records.json').write_text(json.dumps(rec,indent=2));(W/'new_timing.json').write_text(json.dumps(tim,indent=2));print('built 3 actions;',sum(map(len,ALL.values())),'frames')
