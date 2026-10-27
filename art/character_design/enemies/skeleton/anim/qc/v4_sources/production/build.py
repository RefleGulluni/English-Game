from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-v4-20261027');O=W/'staged';F=O/'frames';F.mkdir(parents=True,exist_ok=True);Q=O/'qc';Q.mkdir(exist_ok=True);V=Q/'v4_sources';V.mkdir(exist_ok=True);P=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),int);L=np.array([.299,.587,.114]);stand={d:np.array(Image.open(S/('skeleton_B.png' if d=='front' else f'skeleton_B_{d}.png')).convert('RGBA')) for d in ['front','back','left','right']};ALL={};rec={};tim={}
def load(p):return np.array(Image.open(p).convert('RGBA'))
def put(a,b,dx=0,dy=0):
 ys,xs=np.where(b[:,:,3]>0);xx=xs+dx;yy=ys+dy;ok=(xx>=0)&(xx<96)&(yy>=0)&(yy<96);a[yy[ok],xx[ok]]=b[ys[ok],xs[ok]]
def codes(a):return ((a[:,:,:3,None].transpose(0,1,3,2).astype(int)-P[None,None])**2).sum(3).argmin(2)
def strip(a,mask):b=np.zeros_like(a);b[mask]=a[mask];return b
def save(n,fs,ds,loop,rs):
 ALL[n]=fs;rec[n]=rs;tim[n]={'frames':len(fs),'durations_ms':ds,'loop':loop,'sprite_sheet':n+'.png'};D=F/n;D.mkdir(exist_ok=True);b=Image.new('RGBA',(96*len(fs),96))
 for k,a in enumerate(fs):im=Image.fromarray(a);im.save(D/f'{k+1:02}.png');b.alpha_composite(im,(k*96,0))
 b.save(O/(n+'.png'))
def roi_rows(ranges):
 m=np.zeros((96,96),bool)
 for y0,y1,x0,x1 in ranges:m[y0:y1,x0:x1]=True
 return m
# Anatomical whole-arm selections, drawn from each own standing direction.
armregions={
 'right':[[(23,29,31,39),(29,35,29,37),(35,44,28,36),(44,47,28,37),(47,59,28,38)],[(37,44,40,44)]],
 'left':[[(20,29,51,57),(29,39,51,58),(39,46,51,57),(46,57,49,58)],[(39,54,39,43)]],
 'front':[[(24,30,29,37),(30,43,27,35),(43,59,27,37)],[(21,29,60,68),(29,44,62,70),(44,59,62,71)]],
 'back':[[(20,28,28,35),(28,43,25,33),(43,59,24,34)],[(21,29,57,65),(29,44,60,68),(44,60,61,71)]]}
arms={d:[strip(m,roi_rows(rr)) for rr in armregions[d]] for d,m in stand.items()}
arms['right'][1][:]=0
far=arms['left'][1];far[np.isin(codes(far),[20,21,23,25,*range(26,34),36])]=0
D=V/'arm_sources';D.mkdir(exist_ok=True)
for d,aa in arms.items():
 for j,a in enumerate(aa):Image.fromarray(a).save(D/f'{d}_{j+1}.png')
def union_arm_area(d,k,old):
 out=np.zeros((96,96),bool)
 for j,rr in enumerate(armregions[d]):
  m=roi_rows(rr)
  # Native bounding envelope covers old upper and lower arm offsets as well as the new single chain.
  ys,xs=np.where(m);x0=max(0,xs.min()-2);x1=min(96,xs.max()+3);y0=max(20,ys.min()-1);y1=min(96,ys.max()+4)
  if d in ['left','right'] and j==0:
   out[y0:min(y1,45),x0:x1]=True
   bm=load(A/'qc/v3_sources/walk_layers'/d/f'{k+1:02}_bare_leg_protected.png')[:,:,3]>0
   box=np.zeros_like(m);box[45:y1,x0:x1]=True;out|=bm&box
  elif d in ['left','right']:
   # Far-arm visible sliver, including its old generated hand position.
   ids=codes(old);farbox=roi_rows([(36,56,33,40)]) if d=='left' else m;out|=farbox&~np.isin(ids,[20,21,23,25,*range(26,34),36])&(old[:,:,3]>0)
  else:out[y0:y1,x0:x1]=True
 return out
def tone(a,m,frozen):
 a=a.copy();rs=[]
 for y0,y1 in [(0,20),(20,45),(45,65),(65,96)]:
  src=m[y0:y1];target=float((src[src[:,:,3]>0,:3]@L).mean());r=a[y0:y1];fg=r[:,:,3]>0;edit=fg&~frozen[y0:y1];rgb=r[edit,:3].astype(int);best=None
  for off in ([0] if y0==0 else np.arange(-125,125.1,.5)):
   q=np.clip(rgb+off,0,255);out=P[((q[:,None]-P[None])**2).sum(2).argmin(1)];z=r.copy();z[edit,:3]=out;mean=float((z[fg,:3]@L).mean());cost=float(((out-rgb)**2).mean()) if len(rgb) else 0;key=(max(0,abs(mean-target)-1.8),cost)
   if best is None or key<best[0]:best=(key,out,mean,float(off))
  r[edit,:3]=best[1];rs.append({'band':[y0,y1-1],'standing_mean':target,'mean':best[2],'difference':best[2]-target,'rgb_offset':best[3]})
 return a,rs

# Side walk: accepted cloth/legs/feet remain the base; only complete arm chains change.
for d in ['left','right']:
 fs=[];rr=[];old=[load(A/'frames'/f'skeleton_B_walk_{d}_v3'/f'{k+1:02}.png') for k in range(8)];m=stand[d]
 for k,b in enumerate(old):
  a=b.copy();remove=union_arm_area(d,k,b);ids=codes(b)
  # Shroud material pixels in the old arm envelope remain untouched unless hidden by the newly moved arm.
  cloth=remove&np.isin(ids,[20,21,23,25,*range(26,34),36]);remove &= ~cloth
  if d=='left':remove[20:44,42:51]=False
  else:remove[20:44,39:58]=False
  a[remove]=0
  # Where the old chain hid the torso, retain the approved adjacent shroud pixels; never fabricate a joint.
  poses=[];overlay=np.zeros_like(a);sg=1 if d=='left' else -1;dy=1+[0,0,1,0,0,0,1,0][k];dx=sg*[0,0,1,0,0,0,2,0][k]
  for j,arm in enumerate(arms[d]):
   ox=dx if j==0 else (0 if k not in [3,7] else -sg);oy=dy;put(overlay,arm,ox,oy);poses.append({'arm':j+1,'offset':[ox,oy],'source_shape_rigid_integer_translation':True})
  if d=='left':overlay[20:44,42:51]=0
  else:overlay[20:44,39:58]=0
  put(a,overlay);a[61:]=b[61:];a,tones=tone(a,m,~(overlay[:,:,3]>0));assert np.array_equal(a[61:],b[61:]);fs.append(a);rr.append({'frame':k+1,'whole_arm_poses':poses,'edit_envelope_pixels':int(remove.sum()),'no_y44_join':True,'below_y61_rgba_exact_v3':True,'arm_only_tone':tones})
  E=V/'side_arm_masks'/d;E.mkdir(parents=True,exist_ok=True);Image.fromarray(strip(b,remove)).save(E/f'{k+1:02}_removed.png');Image.fromarray(overlay).save(E/f'{k+1:02}_whole_arms.png');Image.fromarray(np.where((remove|(overlay[:,:,3]>0))[:,:,None],255,0).astype(np.uint8).repeat(4,axis=2)).save(E/f'{k+1:02}_edit_mask.png')
 save(f'skeleton_B_walk_{d}_v4',fs,[100]*8,True,rr)
# Exact gray limits from prior production, but keep whole arms and canonical head untouched.
liftA=[0,0,0,0,1,5,6,3];liftB=[1,5,6,3,0,0,0,0];px=[0,1,1,0,0,-1,-1,0];py=[0,1,2,1,0,1,2,1];uy=[0,0,1,1,0,0,1,1]
for d in ['front','back']:
 fs=[];rs=[];m=stand[d];old=[load(A/'frames'/f'skeleton_B_walk_{d}_v2'/f'{k+1:02}.png') for k in range(8)];src=m.copy();fullarm=(arms[d][0][:,:,3]>0)|(arms[d][1][:,:,3]>0);src[fullarm]=0
 # Existing shroud pixels are a separate hanging surface, lagging one frame behind the leg.
 clothroi=roi_rows([(55,84,40,68)]) if d=='front' else roi_rows([(47,58,43,58),(60,84,24,35)])
 ids=codes(src);clothmask=clothroi&(src[:,:,3]>0)&np.isin(ids,[*range(18),20,21,23,25,*range(26,34),36]);cloth=strip(src,clothmask);src[clothmask]=0
 for k in range(8):
  a=np.zeros_like(m);la,lb=liftA[k],liftB[k]
  for y,x in zip(*np.where(src[:,:,3]>0)):
   if y<38:xx=x;yy=y+uy[k]
   elif y<55:xx=x+px[k];yy=y+py[k]
   else:
    left=x<48;lift=la if left else lb;sg=-1 if left else 1;t=min(1,max(0,(y-55)/29));dy=round((1-t)*py[k]-t*lift);bend=round((2 if lift>=5 else 1 if lift else 0)*max(0,1-abs(y-66)/15));xx=x+sg*bend+round(px[k]*(1-t));yy=y+dy
   if 0<=xx<96 and 0<=yy<96:a[yy,xx]=src[y,x]
  for y,x in zip(*np.where(cloth[:,:,3]>0)):
   prev=(k-1)%8;t=min(1,max(0,(y-55)/28));dx=round(px[k]*(1-t)+px[prev]*t);lift=(liftA[prev] if x<48 else liftB[prev]);yy=y+round(py[k]*(1-t)-lift*.35*t);xx=x+dx
   if 0<=yy<96 and 0<=xx<96 and a[yy,xx,3]==0:a[yy,xx]=cloth[y,x]
  # Close only a whole-row torso gap introduced by a 1px pelvis/shoulder registration difference.
  for yy in range(37,61):
   if not (a[yy,39:60,3]>0).any():a[yy,39:60]=a[yy-1,39:60]
  # Reuse canonical feet as full translated pieces, giving measured 0 / 1 / 3 / 5 / 6px contact differences.
  for side,(x0,x1,lift) in enumerate([(24,48,la),(48,75,lb)]):
   # Clear lower foot envelope before inserting the same full foot pixels.
   a[84-lift:96,x0:x1]=0;put(a,m[84:96,x0:x1],x0,84-lift)
  # Whole shoulders-to-hands, with nonuniform suspended-arm catches.
  armoverlay=np.zeros_like(a);apos=[]
  for j,arm in enumerate(arms[d]):
   sg=-1 if j==0 else 1;dx=sg*(1 if k in [2,6] else 0);dy=1+uy[k];put(armoverlay,arm,dx,dy);apos.append([dx,dy])
  put(a,armoverlay);frozen=armoverlay[:,:,3]>0;frozen[:20]=True;a,tones=tone(a,m,frozen);fs.append(a);rs.append({'frame':k+1,'lift_screen_left':la,'lift_screen_right':lb,'pelvis_offset':[px[k],py[k]],'head_torso_y':uy[k],'arm_shoulder_y':1+uy[k],'knee_outward_px':[2 if la>=5 else 1 if la else 0,2 if lb>=5 else 1 if lb else 0],'whole_arm_offsets':apos,'cloth_lag_source_frame':(k-1)%8+1,'tone':tones})
 save(f'skeleton_B_walk_{d}_v4',fs,[100]*8,True,rs)
# Native B reconstruction helpers from the V3 production source; no generated wide body is used.
s=(A/'qc/v3_sources/production/build.py').read_text();boneids=list(range(37,48));exec(s[s.index('def dilate('):s.index('def strip(')]);exec(s[s.index('def lower_material('):s.index('# Canonical cloth')]);block=s[s.index('# Reassembly: source anatomy'):s.index('# Reuse the accepted late')];exec(block)
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
h=(A/'qc/v2_sources/production/build.py').read_text();exec(h[h.index('def crooked_standard('):h.index('# Reassembly v2:')])
# Separate the native lower skeleton/shroud and thorax so the pelvis can lead without translating the whole actor.
source=(A/'qc/v3_sources/production/build.py').read_text();fsource=source[source.index('def rise_pose('):source.index('# Reuse the accepted late')]
fsource=fsource.replace('def rise_pose(', 'def rise_layers(').replace(' # Add spine, rib cage, then shoulder/shroud and asynchronous arms.', ' lower=a.copy();a[:]=0\n # Add spine, rib cage, then shoulder/shroud and asynchronous arms.').replace(' return a,ledger',' return lower,a,ledger')
exec(fsource)
# Remove complete arm sources from the torso/pelvis builders; they return as whole chains below.
m=stand['front'].copy();am=(arms['front'][0][:,:,3]>0)|(arms['front'][1][:,:,3]>0);m[am]=0;bodybase=m.copy();bodybase[hm]=0

# A direct 1px stitched line, in B's existing darkest seam color. Explicit user-requested pixel path.
thread=tuple(P[0].tolist()+[255])
def line(a,points):
 path=[]
 for (x0,y0),(x1,y1) in zip(points,points[1:]):
  dx=abs(x1-x0);sx=1 if x0<x1 else -1;dy=-abs(y1-y0);sy=1 if y0<y1 else -1;err=dx+dy
  while True:
   if 0<=x0<96 and 0<=y0<96:a[y0,x0]=thread;path.append([x0,y0])
   if x0==x1 and y0==y1:break
   e=2*err
   if e>=dy:err+=dy;x0+=sx
   if e<=dx:err+=dx;y0+=sy
 return path
# Smaller individual pulls, separated across six ground poses.
fs=[pile.copy()];rs=[{'phase':'wake','exact_padded_remains':True}];active=set(order)
events=[{'shroud':[-1,0],'rib_tip':[1,0]}, {'rib_tip':[0,0],'left_arm':[2,-1]}, {'left_leg':[3,-2],'shroud':[-2,-1]}, {'right_arm':[-3,0],'ribs':[0,-2]}, {'shoulder_nails':[2,1],'right_leg':[-2,-1],'pelvis':[0,-2]}]
for j,e in enumerate(events):
 offsets.update(e);a=floor_pose(active,turn=j>=1);fs.append(a);rs.append({'phase':'wake' if j<3 else 'gather','group_offsets':{n:offsets[n].copy() for n in order},'changed_groups':e,'ground_groups':sorted(active)})
# Twenty-one canonical rising poses. New shoulders/ribs arrive in smaller pieces instead of appearing as one full block.
deltas=[27,26,24,23,21,20,18,17,15,14,12,11,9,8,6,5,4,3,2,1,1];remove_at={0:['pelvis'],1:['left_leg'],2:['right_leg'],4:['ribs'],5:['left_arm'],6:['shoulder_nails'],7:['rib_tip'],8:['right_arm'],10:['small_bones'],16:['shroud']}
last_lower_delta=27;last_upper_delta=27;armdy=[27,27]
for j,delta in enumerate(deltas):
 for n in remove_at.get(j,[]):active.discard(n)
 stage=(0 if j==0 else 1 if j<=2 else 2 if j<=6 else 3 if j<=8 else 4 if j<=11 else 5)
 if j%2==0:last_lower_delta=delta
 if j%2==1:last_upper_delta=deltas[j-1]
 lower,_,ledger=rise_layers(last_lower_delta,0 if j==0 else 1)
 _,upper,_=rise_layers(last_upper_delta,stage)
 body=lower.copy();put(body,upper)
 # Whole arms arrive at different beats and lag behind the thorax by up to two pixels.
 for ai,first in [(0,8),(1,10)]:
  if j<first:continue
  if j==first:armdy[ai]=last_upper_delta+(2 if ai==1 else 0)
  elif j%2==ai:armdy[ai]=max(last_upper_delta,armdy[ai]-3)
  put(body,arms['front'][ai],2,armdy[ai])
 if j==18:
  target=crooked_standard(True,2,1,2);zone=np.zeros((96,96),bool);zone[50:]=True;zone[20:62,25:39]=False;zone[20:62,60:73]=False;body[zone]=target[zone]
 if j==19:
  target=crooked_standard(True,2,1,2);zone=np.zeros((96,96),bool);zone[40:]=True;zone[20:62,25:39]=False;zone[20:62,60:73]=False;body[zone]=target[zone]
 if j==20:body=crooked_standard(True,2,1,2)
 a=floor_pose(active);put(a,body);r={'phase':'rise','pelvis_delta_y':last_lower_delta,'thorax_delta_y':last_upper_delta,'arm_delta_y':armdy.copy(),'canonical_ledger':ledger,'ground_groups':sorted(active),'removed_from_ground':remove_at.get(j,[])}
 if j==20:r['phase']='headless_pause';r['thread_path']=line(a,[(53,19),(63,45),(76,68)])
 fs.append(a);rs.append(r)
# Thread-driven skull sequence: 0.9s. Neck source is fixed; lateral sway occurs while the skull hangs from the line.
skullposes=[(0,0),(-3,0),(-6,-1),(-8,-11),(-14,-25),(-12,-38),(-19,-54)]
for j,(dx,dy) in enumerate(skullposes):
 a=crooked_standard(True,2,1,2);put(a,turned,dx,dy);attach=[76+dx,68+dy];path=line(a,[(53,19),attach]);fs.append(a);rs.append({'phase':['thread_taut','ground_drag','ground_drag','lift','hanging_sway_left','hanging_sway_right','thread_reel_in'][j],'skull_offset_from_ground':[dx,dy],'thread_rgb':list(thread[:3]),'thread_path':path,'neck_anchor':[53,19],'skull_attachment':attach})
for hx,hy,phase in [(3,1,'snap_60ms'),(2,2,'thread_retract')]:
 a=crooked_standard(False,2,1,2,hx,hy);path=line(a,[(53,19),(52+hx,17+hy)]) if phase=='snap_60ms' else line(a,[(53,19),(53,20)]);fs.append(a);rs.append({'phase':phase,'head_offset':[hx,hy],'thread_path':path,'thread_rgb':list(thread[:3])})
# Six interrupted corrections, ending exactly in the original standard.
settles=[(2,1,2,2,2),(1,1,2,2,2),(0,1,2,1,2),(0,0,1,0,1)]
for upper,hip,knee,hx,hy in settles:
 a=crooked_standard(False,upper,hip,knee,hx,hy);fs.append(a);rs.append({'phase':'settling','upper_x':upper,'hip_x':hip,'knee_out':knee,'head_offset':[hx,hy],'thread_gone':True})
a=stand['front'].copy();a[:45]=0;put(a,stand['front'][:45],0,1);fs.append(a);rs.append({'phase':'settling','upper_only_y_offset':1,'thread_gone':True})
fs.append(stand['front'].copy());rs.append({'phase':'settled','exact_standard_front':True,'thread_gone':True})
ds=[340,160,150,150,150,150]+[100]*21+[120,110,110,100,100,100,90,60,110]+[150,140,140,130,120,100]
assert len(fs)==len(ds)==42;save('skeleton_B_reassemble_front_v4',fs,ds,False,rs)
for n,arr in ALL.items():
 cols=4 if len(arr)<=8 else 7;rows=(len(arr)+cols-1)//cols;b=Image.new('RGBA',(cols*112,rows*116),'#403D3F');dr=ImageDraw.Draw(b)
 for k,a in enumerate(arr):x=k%cols*112;y=k//cols*116;b.alpha_composite(Image.fromarray(a),(x+8,y));dr.text((x+8,y+99),str(k+1)+' '+str(tim[n]['durations_ms'][k])+'ms',fill='white')
 b.resize((b.width*3,b.height*3),Image.Resampling.NEAREST).save(W/(n+'_3x.png'))
(W/'records.json').write_text(json.dumps(rec,indent=2));(W/'new_timing.json').write_text(json.dumps(tim,indent=2));print('built',len(ALL),'actions;',sum(map(len,ALL.values())),'frames; reassembly',sum(ds),'ms')
