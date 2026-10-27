from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-skeleton-v2-20261027')
# Reuse only deterministic native-edit helpers, never old reassembly art.
s=(R/'art/character_design/enemies/skeleton/anim/qc/batch2_sources/production/build.py').read_text();exec(s[:s.index('# Small native changes')].replace('/tmp/english-game-skeleton-batch2-20261026','/tmp/english-game-skeleton-v2-20261027'))
A=S/'anim';oldwalk={d:[np.array(Image.open(A/'frames'/('skeleton_B_walk_'+d)/f'{k+1:02}.png').convert('RGBA')) for k in range(8)] for d in ['front','back','left','right']};events={}
def map_pixels(src,fn):
 a=np.zeros_like(src)
 for y,x in zip(*np.where(src[:,:,3]>0)):
  xx,yy=fn(int(x),int(y))
  if 0<=xx<96 and 0<=yy<96:a[yy,xx]=src[y,x]
 return a
def constrain_torso(a,m,dy=1,dx=0,lo=24,hi=45):
 # Exact canonical silhouette, generated walk's interior material pixels retained.
 a=a.copy();fills=0
 for y in range(lo,hi):
  sy=y-dy
  for x in range(20,77):
   sx=x-dx;opaque=0<=sx<96 and 0<=sy<96 and m[sy,sx,3]==255
   if not opaque:a[y,x]=0
   elif a[y,x,3]==0:a[y,x]=m[sy,sx];fills+=1
 return a,fills
for d in ['left','right','front','back']:
 m=stand[d];arrs=[];rr=[]
 for k,src in enumerate(oldwalk[d]):
  if d in ['left','right']:
   sign=-1 if d=='left' else 1
   def fn(x,y):
    dx=2*sign if y<19 else (sign if y<24 else 0);dy=1 if y<40 else (1 if y<46 and y%3 else 0);return x+dx,y+dy
   a=map_pixels(src,fn);a,fills=constrain_torso(a,m,1+[0,0,1,0,0,0,1,0][k],0,21,45)
  else:
   a=map_pixels(src,lambda x,y:(x,y+1 if y<38 else y));fills=0
  # No support foot or lower leg changes in this revision.
  a[50:]=src[50:];fix=bridge(a);a,tones=tone(a,m)
  arrs.append(a);rr.append({'frame':k+1,'source_existing_walk':str(A/'frames'/('skeleton_B_walk_'+d)/f'{k+1:02}.png'),'head_forward_px':2 if d in ['left','right'] else 0,'head_and_shoulder_drop_px':1,'canonical_torso_mask_rows':[21,45] if d in ['left','right'] else None,'canonical_mask_source_y_offset':1+[0,0,1,0,0,0,1,0][k] if d in ['left','right'] else None,'edge_fill_pixels':fills,'waist_bridge_rows':fix,'lower_geometry_y50_and_below_unchanged':True,'tone':tones})
 save('skeleton_B_walk_'+d+'_v2',arrs,[100]*8,True,rr)
# Irregular, direction-specific idle events. The body is at rest most of the loop.
idle_durations={'front':[1000,700,450,120,900,550,120,700],'back':[950,650,550,110,1100,500,130,650],'left':[1000,600,550,110,850,600,130,650],'right':[900,650,500,120,1050,550,100,700]}
def nod(a,dy=1):
 b=a.copy();b[:20]=0;put(b,a[:20],0,dy);return b
def pelvic_tug(m,p,u):
 a=map_pixels(m,lambda x,y:(x+(u if y<37 else p if y<50 else 0),y));a[50:]=m[50:];bridge(a);return a
for d,m in stand.items():
 states=[m.copy() for _ in range(8)];descs=['standard long hold']*8
 if d=='front':
  arm=(28,34,37,59);states[1]=patch(m,arm,1,0);states[2]=patch(m,arm,2,0);states[3]=patch(m,(29,48,36,59),1,0);states[5]=nod(m);states[6]=patch(m,(45,13,55,18),0,1);descs=['standard hold','one hanging arm drifts1px','same arm drifts2px','arm jerked back; wrist1px','standard hold','skull nods down1px','skull pulled up; jaw clicks1px','standard hold']
 elif d=='back':
  states[1]=pelvic_tug(m,1,0);states[2]=pelvic_tug(m,1,1);states[3]=patch(m,(26,39,33,53),1,0);states[5]=patch(m,(54,29,63,43),1,0,False);states[6]=patch(m,(62,47,69,60),-1,0);descs=['standard hold','pelvis slips1px, head holds','shoulders follow one frame late','structure snaps back; elbow1px','standard hold','right-shoulder fold creeps1px','fold released; wrist catches1px','standard hold']
 elif d=='left':
  states[1]=patch(m,(42,12,49,17),0,1);states[2]=patch(states[1],(50,39,59,57),0,1);states[3]=patch(m,(51,47,59,58),0,1);states[5]=patch(m,(36,65,42,80),-1,0);states[6]=patch(m,(50,48,59,59),1,0);descs=['standard hold','jaw opens1px','jaw held; near hand sags1px','jaw snaps shut; wrist catches','standard hold','near shroud torn edge creeps1px','cloth tugged back; hand1px','standard hold']
 else:
  states[1]=nod(m);states[2]=patch(states[1],(30,40,37,57),1,0);states[3]=patch(m,(30,48,37,58),1,0);states[5]=patch(m,(29,34,38,58),-2,0);states[6]=patch(m,(58,67,65,80),1,0);descs=['standard hold','skull hangs down1px','head holds; suspended wrist drifts1px','skull snaps back; wrist catches','standard hold','bare near forearm drifts2px','arm pulled back; shroud tip1px','standard hold']
 for a in states:bridge(a);a[84:]=m[84:]
 save('skeleton_B_idle_'+d+'_v2',states,idle_durations[d],True,[{'event':descs[k],'duration_ms':idle_durations[d][k]} for k in range(8)])
# Immediate visible recoil, peak dislocation, short pull-back; feet never move.
for d,m in stand.items():
 arrs=[];rr=[]
 for k in range(3):
  peak=k==1
  def fn(x,y):
   if y>=84:return x,y
   fade=min(1,max(0,(84-y)/20))
   if d in ['left','right']:
    sg=1 if d=='left' else -1;dd=(3 if y<37 else 2) if k<2 else 1;return x+sg*round(dd*fade),y
   if d=='front':return x+round((3 if y<37 else 2)*fade) if k<2 else x+round(fade),y+(1 if y<60 and k<2 else 0)
   return x,y+round(((3 if y<37 else 2) if k<2 else 1)*fade)
  a=map_pixels(m,fn)
  if peak:
   jaw={'front':(47,14,58,20),'back':(46,9,55,19),'left':(44,12,52,19),'right':(47,12,58,20)}[d];a=patch(a,jaw,0,1)
   shoulder={'front':(31,20,42,34),'back':(55,21,66,35),'left':(50,22,59,35),'right':(31,21,41,35)}[d];a=patch(a,shoulder,-1 if d in ['right','back'] else 1,1)
   cloth={'front':(41,28,52,36),'back':(53,31,62,43),'left':(40,35,48,43),'right':(44,28,54,39)}[d];a=patch(a,cloth,0,-1,False)
  fixes=bridge(a);a[84:]=m[84:];arrs.append(a);rr.append({'frame':k+1,'recoil_body_px':2 if k<2 else 1,'recoil_head_shoulders_px':3 if k<2 else 1,'peak_jaw_or_occiput_y':1 if peak else 0,'peak_shoulder_offset':[1,1] if peak else [0,0],'feet_y84_plus_exact':True,'waist_bridge_rows':fixes})
 save('skeleton_B_hit_'+d+'_v2',arrs,[80,120,160],False,rr)
def crooked_standard(headless=True,upper=2,hip=1,knee=2,headx=2,heady=1):
 m=stand['front'];src=m.copy();hm=np.zeros((96,96),bool)
 for yy in range(16):
  xmin=[45,43,42,42,41,42,41,41,42,42,42,43,44,44,44,45][yy];hm[yy,xmin:59]=True
 skull_piece=np.zeros_like(m);skull_piece[hm]=m[hm];src[hm]=0
 def fn(x,y):
  if y<42:return x+upper,y+1
  if y<55:return x+hip,y+1
  if y<84 and x<48:return x-round(knee*max(0,1-abs(y-68)/16)),y
  return x,y
 a=map_pixels(src,fn);bridge(a)
 if not headless:put(a,skull_piece,headx,heady)
 if headless or (headx==2 and heady==1):
  # Upper shroud corner hangs one native pixel below the pins until the settling catch.
  x0,x1=32+upper,43+upper;region=a[21:31,x0:x1].copy();mask=(region[:,:,3]>0)&((region[:,:,:3]@L)<175);piece=np.zeros_like(region);piece[mask]=region[mask];a[21:31,x0:x1][mask]=0;put(a,piece,x0,22)
 return a
# Reassembly v2: new phase art and canonical bone inventory; NO old reassembly frame is read.
P=pile.copy();used=np.zeros((96,96),bool);groups={}
def take(name,mask):
 global used
 keep=mask&(P[:,:,3]>0)&~used;ar=np.zeros_like(P);ar[keep]=P[keep];groups[name]=ar;used|=keep
def rect(box):
 x0,y0,x1,y1=box;m=np.zeros((96,96),bool);m[y0:y1,x0:x1]=True;return m
take('skull',rect((68,67,87,90)));take('rib_tip',rect((52,60,60,68)));take('shoulder_nails',rect((13,60,32,81)))
cm=Image.new('1',(96,96));ImageDraw.Draw(cm).polygon([(22,68),(36,68),(65,79),(61,88),(38,85),(22,79)],fill=1);take('shroud',np.array(cm,dtype=bool));take('ribs',rect((40,60,68,79)));take('left_arm',rect((10,80,32,96)));take('left_leg',rect((27,84,54,96)));take('right_arm',rect((54,79,68,96)));take('right_leg',rect((53,87,86,96)));take('pelvis',rect((31,75,55,87)));take('small_bones',np.ones((96,96),bool))
# Newly drawn skull turning slightly toward the viewer, kept at original scale by cell selection.
g=clean(np.array(Image.open(W/'ground/frame_03.png').convert('RGBA')));turn=g[8:30,56:74].copy();skullturn=np.zeros_like(P);put(skullturn,turn,68,67)
# Fixed order gives the shroud/foreground bones their established occlusion.
order=['small_bones','pelvis','right_leg','left_leg','ribs','left_arm','right_arm','rib_tip','shoulder_nails','shroud','skull'];offsets={n:[0,0] for n in groups};inventory=[];arrs=[P.copy()];rr=[{'phase':1,'exact_padded_remains':True,'ground_groups':order.copy()}]
def floor_pose(active,turned=True):
 a=np.zeros_like(P)
 for name in order:
  if name not in active:continue
  if name=='skull' and turned:put(a,skullturn,*offsets[name])
  else:put(a,groups[name],*offsets[name])
 return a
active=set(order)
for k in range(1,8):
 moves=[]
 if k==1:offsets['shroud']=[-1,0];offsets['rib_tip']=[1,0];moves=['shroud','rib_tip']
 if k==2:offsets['rib_tip']=[0,0];moves=['rib_tip','skull turn']
 if k==3:offsets['left_arm']=[2,0];moves=['left_arm']
 if k==4:offsets['left_leg']=[2,-1];offsets['shroud']=[-1,-1];moves=['left_leg','shroud']
 if k==5:offsets['right_arm']=[-2,0];offsets['ribs']=[0,-1];moves=['right_arm','ribs']
 if k==6:offsets['shoulder_nails']=[2,1];offsets['right_leg']=[-2,-1];moves=['shoulder_nails','right_leg']
 if k==7:offsets['pelvis']=[0,-2];offsets['shroud']=[-1,-2];moves=['pelvis','shroud']
 a=floor_pose(active,k>=2);arrs.append(a);rr.append({'phase':1 if k<3 else 2,'changed_groups':moves,'ground_groups':sorted(active),'offsets':json.loads(json.dumps(offsets))})
def raw_body(mode,i,box,target,top=None):
 ar=clean(np.array(Image.open(W/mode/f'frame_{i:02}.png').convert('RGBA')));x0,y0,x1,y1=box;ar=ar[y0:min(y1,ar.shape[0]),x0:min(x1,ar.shape[1])];seen=set();drop=[]
 for yy,xx in zip(*np.where(ar[:,:,3]>0)):
  seed=(int(yy),int(xx))
  if seed in seen:continue
  stack=[seed];seen.add(seed);comp=[]
  while stack:
   y,x=stack.pop();comp.append((y,x))
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     q=(y+dy,x+dx)
     if 0<=q[0]<ar.shape[0] and 0<=q[1]<ar.shape[1] and q not in seen and ar[q[0],q[1],3]>0:seen.add(q);stack.append(q)
  if min(x for y,x in comp)>=55 and min(y for y,x in comp)>=ar.shape[0]-17 and len(comp)<65:drop.extend(comp)
 for y,x in drop:ar[y,x]=0
 bb=Image.fromarray(ar).getbbox();ar=ar[bb[1]:bb[3],bb[0]:bb[2]];ar,rows=native_length(ar,target,[12,18,24,30,36,42,48,54,60,66,72,78,84]);ys,xs=np.where(ar[:max(8,target//3),:,3]>0);cx=int(np.median(xs));ox=48-cx;oy=(96-target if top is None else top);can=np.zeros_like(P);put(can,ar,ox,oy);return can,{'new_generated_phase':mode,'source_frame':i,'crop':box,'tight_crop':bb,'source_rows':rows,'offset':[ox,oy]}
removed_by_frame=[['pelvis','left_leg'],['right_leg'],['ribs','left_arm'],['shoulder_nails','rib_tip'],['right_arm'],['small_bones','shroud']]
boxes=[(0,0,31,55),(0,0,48,100),(0,0,53,100),(0,0,75,100),(0,0,72,100),(0,0,72,100)]
for j,(box,target) in enumerate(zip(boxes,[43,49,60,68,74,76])):
 for name in removed_by_frame[j]:active.discard(name)
 bg=floor_pose(active);body,r=raw_body('rise',j+1,box,target,40 if j==0 else None)
 if j>=4:body=crooked_standard(True,2,1,2);r['final_pose_source']='canonical pixels newly registered to crooked, soft-knee pose; generated art used as pose study only at this late stage'
 put(bg,body);arrs.append(bg);r.update({'phase':3 if j<2 else 4,'ground_groups':sorted(active),'removed_from_ground':removed_by_frame[j]});rr.append(r)
# F15 retains the same last skull on the ground; the new headless body is crooked/soft-kneed.
body,r=raw_body('settle',1,(0,0,70,100),76);body=crooked_standard(True,2,1,2);body=patch(body,(31,43,39,60),1,0);r['final_pose_source']='canonical headless crooked pose with suspended wrist1px; new settle source used as pose study';a=floor_pose({'skull'});put(a,body);arrs.append(a);r.update({'phase':5,'ground_groups':['skull'],'event':'headless pause before snap'});rr.append(r)
# F16-19 new settling pose art, explicit two-step straightening, original skull retained for identity.
for j,(pose,upperx,headx,heady) in enumerate([(2,2,2,1),(3,2,2,2),(4,1,2,2),(5,0,1,1)]):
 a,r=prep('settle',pose,96)
 # Retain the approved actor's material pixels for crooked settling rather than morphing into a broad new torso.
 a=crooked_standard(False,upperx,1 if j<2 else 0,2 if j<2 else 1,headx,heady);fills=0
 arrs.append(a);r.update({'final_pose_source':'canonical pixels newly posed using the new crooked-settling study, no old reassembly frame reused','phase':5 if j==0 else 6,'upper_lean_x':upperx,'head_offset':[headx,heady],'canonical_edge_fills':fills,'event':['skull snap, still crooked','shroud catches shoulder pins, crooked hold','first interrupted pull','second pull, head lags'][j]});rr.append(r)
arrs.append(stand['front'].copy());rr.append({'phase':6,'exact_front_standard':True,'event':'final small tug to rest'})
assert len(arrs)==20
durations=[340,160,100,170,130,150,130,120,110,140,120,100,90,90,130,50,150,110,110,100];assert sum(durations)==2600
save('skeleton_B_reassemble_front_v2',arrs,durations,False,rr)
(W/'records.json').write_text(json.dumps(rec,indent=2));(W/'new_timing.json').write_text(json.dumps(tim,indent=2));(W/'palette.json').write_text(json.dumps(pal.tolist()));(W/'bone_groups.json').write_text(json.dumps({n:{'opaque_pixels':int((a[:,:,3]>0).sum())} for n,a in groups.items()},indent=2));G=W/'bone_groups';G.mkdir(exist_ok=True)
for n,a in groups.items():Image.fromarray(a).save(G/(n+'.png'))
for name,arrs in ALL.items():
 cols=4 if len(arrs)<=8 else 5;rows=(len(arrs)+cols-1)//cols;board=Image.new('RGBA',(cols*112,rows*116),'#403D3F');dr=ImageDraw.Draw(board)
 for i,a in enumerate(arrs):x=i%cols*112;y=i//cols*116;board.alpha_composite(Image.fromarray(a),(x+8,y));dr.text((x+8,y+100),str(i+1),fill='white')
 board.resize((board.width*3,board.height*3),Image.Resampling.NEAREST).save(W/(name+'_3x.png'))
print('built',len(ALL),'v2 actions',sum(len(x) for x in ALL.values()),'frames')
