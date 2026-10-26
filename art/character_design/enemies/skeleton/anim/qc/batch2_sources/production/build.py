from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';W=Path('/tmp/english-game-skeleton-batch2-20261026');O=W/'staged';F=O/'frames';F.mkdir(parents=True,exist_ok=True);L=np.array([.299,.587,.114]);stand={d:np.array(Image.open(S/('skeleton_B.png' if d=='front' else f'skeleton_B_{d}.png')).convert('RGBA')) for d in ['front','back','left','right']};pile=np.zeros((96,96,4),np.uint8);pile[48:]=np.array(Image.open(S/'skeleton_B_remains.png').convert('RGBA'));pal=np.unique(np.concatenate([a[a[:,:,3]>0,:3] for a in [*stand.values(),pile]]),axis=0).astype(int);ALL={};rec={};tim={}
def put(can,a,dx=0,dy=0):
 for y,x in zip(*np.where(a[:,:,3]>0)):
  yy=y+int(dy);xx=x+int(dx)
  if 0<=yy<96 and 0<=xx<96:can[yy,xx]=a[y,x]
def clean(a):
 a=a.copy();c=a[:,:,:3].astype(int);a[(c[:,:,0]-c[:,:,1]>26)&(c[:,:,2]-c[:,:,1]>26)]=0;fg=a[:,:,3]>0;rgb=a[fg,:3].astype(int);a[fg,:3]=pal[((rgb[:,None]-pal[None])**2).sum(2).argmin(1)];return a
def patch(a,box,dx=0,dy=0,erase=True):
 b=a.copy();x0,y0,x1,y1=box;region=a[y0:y1,x0:x1].copy()
 if erase:b[y0:y1,x0:x1]=0
 put(b,region,x0+dx,y0+dy);return b
def native_length(a,target,locations):
 h=a.shape[0];rows=list(range(h));delta=target-h
 if delta<0:
  rm=[x for x in locations if x<h][: -delta]
  if len(rm)<-delta:rm += [x for x in range(20,h-7) if x not in rm][: -delta-len(rm)]
  rows=[x for x in rows if x not in rm]
 elif delta>0:
  candidates=[x for x in locations if x<h]
  if not candidates:candidates=[max(0,h//2)]
  add=[candidates[i%len(candidates)] for i in range(delta)];rows=sorted(rows+add)
 assert len(rows)==target;return a[rows].copy(),rows
def prep(mode,i,target=96):
 a=clean(np.array(Image.open(W/mode/f'frame_{i:02}.png').convert('RGBA')));bb=Image.fromarray(a).getbbox();a=a[bb[1]:bb[3],bb[0]:bb[2]];a,rows=native_length(a,target,[23,28,35,43,54,63,71,78,83,87,90,93]);h,w=a.shape[:2]
 if mode!='reassemble':
  ys,xs=np.where(a[25:48,:,3]>0);cx=int(np.median(xs))
 else:cx=w//2
 ox=48-cx;oy=96-h;can=np.zeros((96,96,4),np.uint8);put(can,a,ox,oy);return can,{'source':mode,'frame':i,'crop':bb,'source_row_lookup':rows,'offset':[ox,oy]}
def bridge(a):
 fixes=[]
 for y in range(36,65):
  if not (a[y,40:59,3]>0).any():a[y,40:59]=a[y-1,40:59];fixes.append(y)
 return fixes
def tone(a,master):
 a=a.copy();rows=[]
 for j,(y0,y1) in enumerate([(0,20),(20,45),(45,65),(65,96)]):
  b=master[y0:y1];target=float((b[b[:,:,3]>0,:3]@L).mean());c=a[y0:y1];fg=c[:,:,3]>0;rgb=c[fg,:3].astype(int);before=float((rgb@L).mean());best=None
  for off in ([0] if j==0 and abs(before-target)<=2 else np.arange(-80,80.1,.25)):
   probe=np.clip(rgb+off,0,255);ix=((probe[:,None]-pal[None])**2).sum(2).argmin(1);res=pal[ix];mean=float((res@L).mean());err=abs(mean-target);cost=float(((res-rgb)**2).mean());key=(max(0,err-1.8),cost)
   if best is None or key<best[0]:best=(key,res,mean,float(off))
  c[fg,:3]=best[1];rows.append({'band':[y0,y1],'standing_mean':target,'before_mean':before,'mean':best[2],'difference':best[2]-target,'palette_rgb_offset':best[3]});assert abs(best[2]-target)<=2
 return a,rows
def save(name,arrs,durations,loop,records):
 ALL[name]=arrs;rec[name]=records;tim[name]={'frames':len(arrs),'durations_ms':durations,'loop':loop,'sprite_sheet':name+'.png'};dd=F/name;dd.mkdir(exist_ok=True);sheet=Image.new('RGBA',(96*len(arrs),96))
 for i,a in enumerate(arrs):im=Image.fromarray(a);im.save(dd/f'{i+1:02}.png');sheet.alpha_composite(im,(96*i,0))
 sheet.save(O/(name+'.png'))
# Small native changes to original generated masters: structure sway, never breathing.
hem={'front':(60,68,67,81),'back':(24,74,29,83),'left':(37,66,42,81),'right':(59,69,65,83)}
for d,m in stand.items():
 arrs=[m.copy()];rr=[{'exact_standard':True}]
 for k in [1,2,3]:
  p=[0,1,0,0][k];u=[0,0,1,0][k];a=np.zeros_like(m)
  for y in range(96):
   dx=u if y<37 else (p if y<57 else (round(p*(67-y)/10) if y<67 else 0))
   for x in np.where(m[y,:,3]>0)[0]:
    if 0<=x+dx<96:a[y,x+dx]=m[y,x]
  a[50:]=m[50:]
  if k==2:a=patch(a,hem[d],1,0)
  bridge(a);arrs.append(a);rr.append({'pelvis_x':p,'shoulder_head_x':u,'hem_tip_x':1 if k==2 else 0,'legs_below_y':84})
 save('skeleton_B_idle_'+d,arrs,[500]*4,True,rr)
 # Hit: preserve first master; one peak pose then near-return. Floor row and feet stay unchanged.
 arrs=[m.copy()];rr=[{'exact_standard':True,'document_conflict':'Section2 exact-first takes precedence over section5 first-frame recoil'}]
 for k in [1,2]:
  a=np.zeros_like(m);peak=(k==1)
  for y in range(96):
   if y>=84:dx=dy=0
   elif d in ['left','right']:
    direction=1 if d=='left' else -1;val=(3 if y<36 else 2) if peak else 1;dx=direction*round(val*min(1,(84-y)/20));dy=0
   elif d=='front':dx=(2 if y<20 else 1) if peak else 1;dy=-1 if 22<=y<60 and peak else 0;dx=round(dx*min(1,(84-y)/20))
   else:dx=0;dy=(2 if y<36 else 1) if peak else 1;dy=round(dy*min(1,(84-y)/20))
   for x in np.where(m[y,:,3]>0)[0]:
    yy=y+dy;xx=x+dx
    if 0<=yy<96 and 0<=xx<96:a[yy,xx]=m[y,x]
  fixes=bridge(a)
  if peak:
   # Small separated elbow/forearm group is caught by the wrist binding next frame.
   hand={'front':(29,38,35,52),'back':(25,39,32,53),'left':(49,38,57,54),'right':(29,39,36,53)}[d];a=patch(a,hand,1 if d in ['left','front'] else -1,0)
  arrs.append(a);rr.append({'stage':'peak_dislocation' if peak else 'return_1px','feet_y84_and_below_exact':True,'waist_bridge_rows':fixes,'front_head_note':'Head kept within y>=0; recoil uses 2px lateral skull offset instead of clipping at top' if d=='front' else None})
 save('skeleton_B_hit_'+d,arrs,[80,120,160],False,rr)
# Bone pile barely alive: one upright bone and waist/cloth cord twitch, not whole-pile motion.
arrs=[pile.copy(),patch(pile,(52,60,61,70),1,0),patch(pile,(39,78,54,81),1,0),pile.copy()]
save('skeleton_B_remains_idle',arrs,[500]*4,True,[{'exact_padded_remains':True},{'bone_patch':[52,60,61,70],'dx':1},{'cord_patch':[39,78,54,81],'dx':1},{'exact_padded_remains':True}])
# Whole generated walking poses; native retarget to original planted feet, as in accepted right-walk.
hips=[0,1,0,0,0,1,0,0];upp=[0,0,1,0,0,0,1,0]
for d in ['left','front','back']:
 m=stand[d];arrs=[];rr=[]
 if d=='left':boxes={'near':(31,83,49,96),'far':(48,83,64,96)}
 else:boxes={'screen_left':(24,83,48,96),'screen_right':(49,83,74,96)}
 feet={}
 for role,box in boxes.items():
  ft=m[box[1]:box[3],box[0]:box[2]].copy();bb=Image.fromarray(ft).getbbox();feet[role]=(ft[bb[1]:bb[3],bb[0]:bb[2]],box[0]+bb[0])
 for k in range(8):
  pose_index=([1,2,3,5,5,6,7,1][k] if d=='left' else k+1);src,record=prep(d,pose_index);a=np.zeros_like(m)
  for y in range(65):
   if y<38:dy=upp[k];dx=0
   elif y<57:dy=hips[k];dx=(1 if d=='left' else 0)*(-1 if k in[1,2] else 0)
   else:dy=0;dx=0
   for x in np.where(src[y,:,3]>0)[0]:
    if y+dy<96 and 0<=x+dx<96:a[y+dy,x+dx]=src[y,x]
  neck_cut=24 if d=='left' else 20;a[:neck_cut+upp[k]]=0;put(a,m[:neck_cut],0,upp[k]);legs=[]
  roles=list(feet)
  for role in roles:
   ft,originalx=feet[role]
   if d=='left':
    near=(role=='near');tox=([28,33,38,43,48,43,38,33] if near else [48,43,38,33,28,33,38,43])[k];lift=([0,0,0,0,0,1,3,1] if near else [0,1,3,1,0,0,0,0])[k];anchor=int(np.where(ft[-1,:,3]>0)[0].min());ox=tox-anchor;near_left=(pose_index<5);is_left=(near==near_left)
   else:
    is_left=(role=='screen_left');lift=([0,0,0,0,0,1,3,1] if is_left else [0,1,3,1,0,0,0,0])[k];ox=originalx;tox=None
   oy=96-lift-ft.shape[0];side=(lambda x:x<48) if is_left else (lambda x:x>=48);refrow=min(84,oy-1);refxs=np.array([x for x in np.where(src[refrow,:,3]>0)[0] if side(x)]);anklex=ox+int(np.median(np.where(ft[0,:,3]>0)[0]));ref=int(np.median(refxs)) if len(refxs) else anklex;delta=anklex-ref
   for y in range(65,oy):
    dd=round(delta*(y-65)/max(1,oy-66));sy=min(y,86)
    for x in np.where(src[sy,:,3]>0)[0]:
     if side(x) and 0<=x+dd<96:a[y,x+dd]=src[sy,x]
   put(a,ft,ox,oy);legs.append({'role':role,'foot_crop':boxes[role],'offset':[ox,oy],'lowest_y':95-lift,'toe_x':tox,'shin_dx':delta})
  # Suspended arm is nudged out for one beat, then caught by binding.
  if k in [2,6]:
   box=(51,40,58,53) if d=='left' else ((28,39,35,52) if d=='back' else (28,39,35,52));a=patch(a,box,1,0)
  # Back's existing shoulder fold tip visibly lags, no new cloak. Mask only original generated cloth edge.
  if d=='back':
   clothbox=(53,29,61,43);lag=[0,0,2,1,0,-1,-2,-1][k];a=patch(a,clothbox,lag,0,False)
  fixes=bridge(a);a,tones=tone(a,m);record.update({'pelvis_y':hips[k],'shoulder_head_y':upp[k],'legs':legs,'waist_bridge_rows':fixes,'tone':tones,'back_shoulder_fold_tip_dx':[0,0,2,1,0,-1,-2,-1][k] if d=='back' else None})
  if d=='left':
   support=legs[0 if k<4 else 1];tx=support['toe_x'];record['support']={'role':support['role'],'canvas':[tx,95],'world_translation':[-5*k,0],'world':[tx-5*k,95]};assert a[95,tx,3]==255
  arrs.append(a);rr.append(record)
 save('skeleton_B_walk_'+d,arrs,[100]*8,True,rr)
# Reassemble is new construction: intact skull stays on floor while pelvis/spine stand.
arrs=[pile.copy()];rr=[{'exact_padded_remains':True}]
a=patch(pile,(27,70,56,84),-1,-1,False);arrs.append(a);rr.append({'first_tension':'original shroud/waist fold offset(-1,-1), underlying bones held'})
a=patch(pile,(13,76,31,93),2,0);a=patch(a,(53,82,65,94),-2,0);a=patch(a,(28,70,55,84),0,-1,False);arrs.append(a);rr.append({'gathering':'two long-bone groups pulled toward center; floor skull held'})
# A small skull-only source preserves scale while generator's early poses had a larger pile.
skull=pile[67:89,68:86].copy()
def floor_skull(a):
 a=a.copy();put(a,skull,68,67);return a
bodies_without_skull={}
for i,target in [(4,49),(5,49),(6,60),(7,76)]:
 src=clean(np.array(Image.open(W/'reassemble'/f'frame_{i:02}.png').convert('RGBA')));bb=Image.fromarray(src).getbbox();src=src[bb[1]:bb[3],bb[0]:bb[2]]
 # Register central pelvis/body independently of the loose skull at the right edge.
 ww=src.shape[1];body=src[:,:min(55,ww)].copy();body[max(0,body.shape[0]-25):,50:]=0;bb2=Image.fromarray(body).getbbox();body=body[bb2[1]:bb2[3],bb2[0]:bb2[2]];body,rows=native_length(body,target,[12,18,24,30,36,42,48,54,60]);a=np.zeros_like(pile);ox=48-body.shape[1]//2;oy=96-target;put(a,body,ox,oy);bodies_without_skull[i]=a.copy();a=floor_skull(a);arrs.append(a);rr.append({'source_frame':i,'source_crop':bb,'body_crop':bb2,'removed_loose_skull_edge':'source body last25 rows x>=50 before body bbox; removes remaining edge of separately rendered floor skull','body_source_row_lookup':rows,'body_offset':[ox,oy],'floor_skull':'original remains crop [68,67,86,89] held in place'})
# Frame8 headless torso pulls arm in, skull still floor; frame9 skull yanked upward late.
headless_eight=patch(bodies_without_skull[7],(30,42,38,64),1,0);a=floor_skull(headless_eight);arrs.append(a);rr.append({'source':'headless frame7 body','arm_dx':1,'skull':'held at floor'})
a=headless_eight.copy();put(a,skull,62,37);arrs.append(a);rr.append({'source':'headless frame8 body','skull_crop':[68,67,86,89],'skull_new_offset':[62,37],'event':'head yanked up AFTER pelvis and chest stand'})
# Snap the original standing skull onto new headless body; 1px horizontal overshoot fits native canvas.
a=headless_eight.copy();head=stand['front'][:20,40:59].copy();put(a,head,41,0);arrs.append(a);rr.append({'source':'headless frame8 body','head_source':'front standard [40,0,59,20]','head_offset':[41,0],'event':'skull snap, 1px horizontal overshoot'})
a=stand['front'].copy();a=patch(a,(59,65,67,81),-1,-1,False);arrs.append(a);rr.append({'source':'front standard','event':'shroud caught on right shoulder, final torn-tip settling1px'})
arrs.append(stand['front'].copy());rr.append({'exact_standard_front':True});assert len(arrs)==12
save('skeleton_B_reassemble_front',arrs,[180,180,160,90,80,70,70,100,60,40,90,160],False,rr)
(W/'records.json').write_text(json.dumps(rec,indent=2));(W/'new_timing.json').write_text(json.dumps(tim,indent=2));(W/'palette.json').write_text(json.dumps(pal.tolist(),indent=2))
for name,arrs in ALL.items():
 cols=4;rows=(len(arrs)+cols-1)//cols;board=Image.new('RGBA',(cols*112,rows*116),'#403D3F');dr=ImageDraw.Draw(board)
 for i,a in enumerate(arrs):x=i%cols*112;y=i//cols*116;board.alpha_composite(Image.fromarray(a),(x+8,y));dr.text((x+8,y+100),str(i+1),fill='white')
 board.resize((board.width*4,board.height*4),Image.Resampling.NEAREST).save(W/(name+'_4x.png'))
print('Built',len(ALL),'new actions,',sum(len(x) for x in ALL.values()),'frames')
