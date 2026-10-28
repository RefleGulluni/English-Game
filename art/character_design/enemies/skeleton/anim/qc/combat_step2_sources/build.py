from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-combat-step2-20261028');O=W/'staged';O.mkdir(exist_ok=True);P=json.loads((W/'parts_plan_before_compositing.json').read_text());A=R/'art/character_design';S=A/'enemies/skeleton';L=np.array([.299,.587,.114]);ALL={};records={}
def load(p):return np.array(Image.open(p).convert('RGBA'))
def polygon(shape,pts):
 b=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(b).polygon(pts,fill=255);return np.array(b)>0

def part(a,mask):b=np.zeros_like(a);b[mask]=a[mask];return b

def put(a,b,dx=0,dy=0):
 ys,xs=np.where(b[:,:,3]>0);xx=xs+dx;yy=ys+dy;assert ((xx>=0)&(xx<a.shape[1])&(yy>=0)&(yy<a.shape[0])).all(),('clipped',dx,dy);a[yy,xx]=b[ys,xs]

def rowpose(m,upper,pelvis,armmask=None):
 # Whole portrait from its approved standing pixels, with flexible original coat/waist rows connecting rigid chest/pelvis.
 h,w=m.shape[:2];a=np.zeros_like(m);body=m.copy()
 if armmask is not None:body[armmask]=0
 for sy in range(h):
  if sy<40:dx,dy=upper
  elif sy<48:dx,dy=pelvis
  elif sy<78:t=(78-sy)/30;dx=round(pelvis[0]*t);dy=round(pelvis[1]*t)
  else:dx=dy=0
  sx=np.where(body[sy,:,3]>0)[0];a[sy+dy,sx+dx]=body[sy,sx]
 for y in range(40+upper[1],40+pelvis[1]):
  sx=np.where(body[40,:,3]>0)[0];a[y,sx+pelvis[0]]=body[40,sx]
 return a

def export(n,fs):
 ALL[n]=fs;D=O/'frames'/n;D.mkdir(parents=True,exist_ok=True);fw=fs[0].shape[1];sheet=Image.new('RGBA',(fw*len(fs),96));board=Image.new('RGBA',(4*(fw+8),((len(fs)+3)//4)*112),'#403d43');d=ImageDraw.Draw(board)
 for k,a in enumerate(fs):
  im=Image.fromarray(a);im.save(D/f'{k+1:02}.png');sheet.paste(im,(k*fw,0));x=k%4*(fw+8);y=k//4*112;board.alpha_composite(im,(x,y));d.text((x+2,y+98),str(k+1),fill='white')
 sheet.save(O/(n+'.png'));board.resize((board.width*3,board.height*3),Image.Resampling.NEAREST).save(W/(n+'_contact3x.png'))

def save_layer(n,k,role,a):
 d=O/'qc/combat_step2_sources'/n;d.mkdir(parents=True,exist_ok=True);Image.fromarray(a).save(d/f'{k:02}_{role}.png')

# Hero left caster: near left hand lifts; far right lantern and near hip bag retained from the left master.
m=load(A/'hero_B1_left.png');yy,xx=np.indices((96,96));lm=(yy>=43)&(yy<=60)&(xx>=36)&(xx<=40)&(m[:,:,3]>0);lamp=part(m,lm);body=m.copy();body[lm]=0
# Resting near hand at the bag rim, replaced by adjacent native cloth when that hand leaves.
rest=(yy>=36)&(yy<=40)&(xx>=45)&(xx<=49)&((m[:,:,:3]@L)>105)&(m[:,:,3]>0)
cleared=body.copy()
for y,x in zip(*np.where(rest)):
 donor=(y,max(41,x-4));cleared[y,x]=m[donor] if m[donor][3] else m[y,min(55,x+5)]
name='hero_B1_cast_left';pp=P[name];fs=[];rr=[]
for k in range(8):
 dx=pp['upper_dx'][k];pose=pp['arm_poses'][k]
 if k in [0,7]:a=m.copy();arm=np.zeros_like(a)
 else:
  src=cleared if pose else body;a=rowpose(src,[dx,0],[dx,0]);arm=np.zeros_like(a)
  if pose:
   g=load(W/f'cast_left_{pose:02}.png');mask=(xx<=50)&(yy>=17)&(yy<=37)
   if pose in [2,3,6]:mask&=polygon(g.shape,[(36,18),(46,20),(50,26),(49,34),(39,37),(28,33),(27,23)])
   else:mask&=polygon(g.shape,[(45,20),(50,26),(49,31),(41,34),(28,37),(18,36),(11,33),(11,27),(17,23),(25,25),(36,24)])
   arm=part(g,mask);put(a,arm,dx,0)
  for y,x in zip(*np.where(lamp[:,:,3]>0)):
   swing=round(pp['lamp_bottom_dx'][k]*max(0,(y-46)/14));a[y,x+dx+swing]=lamp[y,x]
  shifted=np.zeros_like(a);put(shifted,arm,dx,0);arm=shifted
 assert np.array_equal(a[78:],m[78:]);save_layer(name,k+1,'moving_arm',arm);fs.append(a);rr.append({'frame':k+1,'upper':[dx,0],'pelvis':[dx,0],'casting_hand':'left near','lantern_hand':'right far','grip':[38+dx,42],'handle_top':[38+dx,43],'lamp_bottom_dx':pp['lamp_bottom_dx'][k]})
export(name,fs);records[name]=rr

# Physical hit: all native standing shapes are reused, pelvis reacts before the rigid head/neck/shoulder group.
for direction in ['left','right']:
 name='hero_B1_hit_'+direction;pp=P[name];m=load(A/f'hero_B1_{direction}.png');yy,xx=np.indices((96,96));lm=((yy>=43)&(yy<=60)&(xx>=36)&(xx<=40)) if direction=='left' else ((yy>=45)&(yy<=60)&(xx>=58)&(xx<=66));lm&=m[:,:,3]>0;lamp=part(m,lm);body=m.copy();body[lm]=0
 holdmask=polygon(m.shape,[(40,25),(45,25),(48,32),(56,36),(61,40),(65,42),(65,44),(60,45),(54,43),(49,41),(43,38),(39,33)]) if direction=='right' else ((xx>=36)&(xx<=41)&(yy>=32)&(yy<=43))
 holdmask&=m[:,:,3]>0;holding_arm=part(m,holdmask);body[holdmask]=0;fs=[];rr=[]
 for k in range(4):
  ud=pp['upper_dx'][k];pd=pp['pelvis_dx'][k]
  if k in [0,3]:a=m.copy()
  else:
   a=rowpose(body,[ud,0],[pd,0]);put(a,holding_arm,ud,0)
   for y,x in zip(*np.where(lamp[:,:,3]>0)):
    pivot=46 if direction=='left' else 47;bottom=round(pp['lamp_bottom_dx'][k]*max(0,(y-pivot)/14));a[y,x+ud+bottom]=lamp[y,x]
  assert np.array_equal(a[78:],m[78:]);fs.append(a);rr.append({'frame':k+1,'upper':[ud,0],'pelvis':[pd,0],'lamp_bottom_dx':pp['lamp_bottom_dx'][k],'feet_fixed':True})
 export(name,fs);records[name]=rr

# Left attack: far right arm separately drawn, near left arm and cloth remain that of the LEFT portrait.
name='skeleton_B_attack_left';pp=P[name];m=load(S/'skeleton_B_left.png');yy,xx=np.indices((96,96));farhand=(xx>=38)&(xx<=40)&(yy>=45)&(yy<=53)&(m[:,:,3]>0)
# The covered far arm moves out from behind the shroud, its small old hand is hidden by the same shroud material.
base=m.copy()
for y,x in zip(*np.where(farhand)):
 if (m[y,x,:3]@L)>150:base[y,x]=m[y,min(x+4,50)]
base[49,40]=m[48,40];base[50,40]=m[48,40];base[49,40,:3]=[229,193,121]
polys={
3:[(83,15),(88,15),(95,18),(100,22),(101,27),(98,33),(93,35),(92,31),(95,26),(91,24),(84,23)],
4:[(83,14),(89,14),(95,18),(103,22),(104,27),(99,30),(92,29),(89,26),(94,24),(90,22),(84,21)],
5:[(12,19),(23,18),(38,18),(48,19),(55,19),(74,19),(76,23),(73,26),(54,25),(48,27),(34,26),(25,27),(19,25),(12,24)],
6:[(11,23),(23,22),(35,23),(48,21),(55,20),(75,20),(77,25),(71,28),(55,27),(47,29),(34,29),(22,30),(11,29)],
7:[(38,25),(51,24),(58,26),(65,28),(72,23),(76,26),(74,30),(68,34),(61,35),(54,32),(46,32),(38,30)]}
fs=[];rr=[]
for k in range(9):
 ud=pp['upper'][k];pd=pp['pelvis'][k];pose=pp['arm_poses'][k];a=np.zeros((96,160,4),np.uint8);arm=np.zeros_like(a)
 if k in [0,8]:put(a,m,32,0)
 else:
  body=rowpose(base,ud,pd)
  if pose in [3,4,5,6,7]:
   g=load(W/f'attack_left_{pose:02}.png');p=part(g,polygon(g.shape,polys[pose]));shift={3:(-5,3),4:(-6,4),5:(0,2),6:(0,2),7:(0,1)}[pose];put(arm,p,shift[0]+ud[0],shift[1]+ud[1])
   put(a,arm) # Far arm is behind the entire original chest and near arm.
  put(a,body,32,0)
  # Free left-shin shroud edge lags by1px while the wrapped part stays on the same leg.
  if k in [3,4,5,6,7]:
   free=(yy>=63)&(yy<81)&(xx<=40)&(m[:,:,3]>0);p=part(m,free);a[yy[free],xx[free]+32]=0;put(a,p,32+(1 if k in [3,4] else -1),0)
 save_layer(name,k+1,'moving_arm',arm);assert np.array_equal(a[84:,32:128],m[84:]);fs.append(a);ys,xs=np.where(arm[:,:,3]>0);tip=[int(xs.min()),int(np.median(ys[xs==xs.min()]))] if len(xs) else None;rr.append({'frame':k+1,'upper':ud,'pelvis':pd,'attack_arm':'right far','near_left_arm':'original standing pixels','tip':tip,'shroud_leg':'left','feet_fixed':True})
export(name,fs);records[name]=rr

# Right short-arm comparison: only frames5/6 differ from accepted current attack.
name='skeleton_B_attack_right_v2';m=load(S/'skeleton_B_right.png');oldname='skeleton_B_attack_right';fs=[load(S/'anim/frames'/oldname/f'{i:02}.png') for i in range(1,10)];yy,xx=np.indices((96,96));arm0=load(S/'anim/qc/v5_sources/standing_parts/near_right_arm.png');mask0=arm0[:,:,3]>0;without=m.copy();without[mask0]=0;rr=[]
polysv={2:[(67,18),(73,18),(79,22),(84,25),(88,25),(90,28),(90,31),(94,35),(98,39),(96,41),(92,38),(86,33),(84,31),(81,30),(75,28),(69,25),(67,23)],3:[(67,18),(72,18),(76,22),(80,26),(84,30),(88,33),(88,36),(92,38),(97,42),(95,44),(91,41),(85,38),(81,35),(77,32),(72,29),(68,25)]}
for k,newpose,ud,pd in [(4,2,[0,1],[1,0]),(5,3,[1,0],[1,0])]:
 original=fs[k].copy();oldarm=load(S/f'anim/qc/combat_sources/skeleton_layers/{k+1:02}_attacking_arm.png');erase=oldarm[:,:,3]>0;body=np.zeros_like(original);put(body,rowpose(without,ud,pd),32,0)
 a=original.copy();a[erase]=body[erase]
 # Remove the remaining old shoulder cap only where it belongs to the formerly hanging upper arm.
 cap=np.zeros((96,160),bool)
 for y,x in zip(*np.where(mask0&(yy>=23)&(yy<=25))):cap[y+ud[1],x+32+ud[0]]=True
 a[cap]=body[cap]
 g=load(W/'short_mid_restored.png') if newpose==2 else load(W/f'attack_right_v2_{newpose:02}.png')
 poly=[(68,18),(78,17),(85,17),(88,20),(90,23),(94,26),(94,29),(90,29),(86,25),(83,23),(78,24),(71,24),(68,23)] if newpose==2 else polysv[newpose]
 arm=part(g,polygon(g.shape,poly));dx=(-2 if newpose==2 else -1)+ud[0];dy=3+ud[1];layer=np.zeros_like(a);put(layer,arm,dx,dy);put(a,layer);save_layer(name,k+1,'moving_arm',layer)
 fs[k]=a;ys,xs=np.where(layer[:,:,3]>0);tip=[int(xs.max()),int(np.median(ys[xs==xs.max()]))];elbow=[84+dx,19+dy] if newpose==2 else [84+dx,34+dy];rr.append({'frame':k+1,'tip':tip,'tip_relative_anchor':[tip[0]-80,tip[1]-96],'elbow_marker':elbow,'forearm_projected_length':float(np.hypot(tip[0]-elbow[0],tip[1]-elbow[1])),'upper':ud,'pelvis':pd,'changed_from_accepted':int((a!=original).any(2).sum())})
for k in [0,1,2,3,6,7,8]:assert np.array_equal(fs[k],load(S/'anim/frames'/oldname/f'{k+1:02}.png'))
export(name,fs);records[name]=rr

# Falling ash: sample small disconnected dark clusters actually drawn in the raw dust pose sheets.
def small_components(a):
 todo=set(zip(*np.where(a[:,:,3]>0)));cs=[]
 while todo:
  first=todo.pop();q=[first];c=[first]
  while q:
   y,x=q.pop()
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     pt=(y+dy,x+dx)
     if pt in todo:todo.remove(pt);q.append(pt);c.append(pt)
  if 1<=len(c)<=12:
   ys=[t[0] for t in c];xs=[t[1] for t in c]
   if max(xs)-min(xs)<=4 and max(ys)-min(ys)<=5:cs.append((c,(min(xs),min(ys),max(xs)+1,max(ys)+1)))
 return cs
for direction in ['left','right']:
 name='skeleton_B_dust_'+direction;pp=P[name];m=load(S/f'skeleton_B_{direction}.png');yy,xx=np.indices((96,96));g=load(W/f'dust_{direction}_03.png');candidates=small_components(g);chosen=[]
 for pts,bb in candidates:
  if bb[0]<54:continue
  rgb=np.array([g[y,x,:3] for y,x in pts]);mean=(rgb@L).mean()
  if mean>130 or bb[2]-bb[0]>4 or bb[3]-bb[1]>5:continue
  p=np.zeros((bb[3]-bb[1],bb[2]-bb[0],4),np.uint8)
  for y,x in pts:p[y-bb[1],x-bb[0]]=g[y,x]
  chosen.append((p,bb))
 if len(chosen)<3:
  for pts,bb in small_components(load(W/f'dust_{direction}_04.png')):
   if bb[0]<54 or bb[2]-bb[0]>4 or bb[3]-bb[1]>5:continue
   p=np.zeros((bb[3]-bb[1],bb[2]-bb[0],4),np.uint8)
   for y,x in pts:p[y-bb[1],x-bb[0]]=load(W/f'dust_{direction}_04.png')[y,x]
   chosen.append((p,bb))
 assert len(chosen)>=3,(direction,len(chosen));chosen=chosen[:3]
 # Keep a native 3x3 piece of each independently drawn ash cluster, not a resized clump.
 small=[]
 for c,bb in chosen:
  best=None
  for y in range(max(1,c.shape[0]-2)):
   for x in range(max(1,c.shape[1]-2)):
    patch=c[y:y+3,x:x+3].copy();count=int((patch[:,:,3]>0).sum())
    if best is None or count>best[0]:best=(count,patch,[bb[0]+x,bb[1]+y,bb[0]+x+patch.shape[1],bb[1]+y+patch.shape[0]])
  small.append((best[1],best[2]))
 chosen=small;d=O/'qc/combat_step2_sources'/name;d.mkdir(parents=True,exist_ok=True)
 for j,(c,bb) in enumerate(chosen):Image.fromarray(c).save(d/f'ash_cluster_{j+1}.png')
 starts=[(57,22),(59,39),(61,59)] if direction=='left' else [(39,24),(58,40),(63,59)];fs=[];rr=[]
 for k in range(6):
  ud=pp['upper'][k];pd=pp['pelvis'][k];a=m.copy() if k in [0,5] else rowpose(m,ud,pd);dust=np.zeros_like(a);trail=[]
  if k in [1,2,3,4]:
   drops=([0,0,0] if k==1 else [10,10,9] if k==2 else [31,30,23] if k==3 else [64,48,33])
   for j,((c,bb),(sx,sy),drop) in enumerate(zip(chosen,starts,drops)):
    # Distinct actual generation-derived ash clusters, integer falling trajectories, no synthetic noise.
    dx=[0,1,2,3][k-1] if direction=='left' else [0,-1,-2,-1][k-1];px=sx+dx;py=min(sy+drop,96-c.shape[0]);
    if k==4:px=(66 if direction=='right' else 64)+j*4
    put(dust,c,px,py);trail.append({'id':j+1,'source_bbox':[int(v) for v in bb],'xy':[px,py]})
   put(a,dust)
  save_layer(name,k+1,'ash',dust);fs.append(a);rr.append({'frame':k+1,'upper':ud,'pelvis':pd,'ash_clusters':trail,'feet_fixed':True})
 export(name,fs);records[name]=rr
(W/'pose_records.json').write_text(json.dumps(records,indent=2));print({n:len(fs) for n,fs in ALL.items()})
