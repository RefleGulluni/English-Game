from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-other3-20261027');O=W/'staged';V=O/'qc/other3_sources';V.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(W/'protected.json').write_text(json.dumps({str(p):sha(p) for p in S.rglob('*') if p.is_file()},indent=2))
pal=json.loads((A/'qc/v2_sources/palette.json').read_text());plans={};refs={}
armboxes={'left':{'left':[(20,29,51,57),(29,39,51,58),(39,46,51,57),(46,57,49,58)],'right':[(44,55,36,40)]},'front':{'right':[(30,43,27,36),(43,57,27,35)],'left':[(23,29,58,62),(29,43,60,68),(43,57,62,70)]},'back':{'left':[(21,29,28,36),(29,43,25,34),(43,58,23,31)],'right':[(25,29,62,66),(29,43,61,71),(43,58,64,73)]}}
for direction in ['left','front','back']:
 m=np.array(Image.open(S/('skeleton_B.png' if direction=='front' else f'skeleton_B_{direction}.png')).convert('RGBA'));fg=m[:,:,3]>0;used=np.zeros((96,96),bool);parts={}
 def take(n,mask):
  global used
  mask=mask&fg&~used;p=np.zeros_like(m);p[mask]=m[mask];parts[n]=p;used|=mask
 for role,boxes in armboxes[direction].items():
  mask=np.zeros((96,96),bool)
  for y0,y1,x0,x1 in boxes:mask[y0:y1,x0:x1]=True
  take('arm_'+role,mask)
 mask=np.zeros((96,96),bool);mask[:40]=True;take('upper',mask)
 mask=np.zeros((96,96),bool);mask[40:48]=True;take('pelvis',mask)
 # Left near leg is anatomical LEFT with broad shroud. Front/back keep their own source silhouette.
 boundary=52 if direction=='left' else 48
 screenleftrole='right' if direction=='front' else 'left'
 mask=np.zeros((96,96),bool);mask[48:,:boundary]=True;take('leg_'+screenleftrole,mask);take('leg_'+('left' if screenleftrole=='right' else 'right'),np.ones((96,96),bool))
 assert np.array_equal(sum((p.astype(np.uint16) for p in parts.values())).astype(np.uint8),m)
 d=V/'standing_parts'/direction;d.mkdir(parents=True,exist_ok=True)
 for n,p in parts.items():Image.fromarray(p).save(d/(n+'.png'))
 refs[direction]={}
 for role in ['left','right']:
  p=parts['leg_'+role];yy,xx=np.where(p[84:,:,3]>0);bottom=int(yy.max()+84);refs[direction][role]={'bottom':bottom,'toe_min':int(xx[yy==yy.max()].min()),'foot_bbox':[int(xx.min()),84,int(xx.max())+1,96]}
 rows=[]
 for k in range(8):
  signal=[2,2,0,0,2,2,0,0];pd=[0,signal[k]];cd=[0,signal[(k-1)%8]//2]
  if direction!='left':pd[0]=[0,1,0,-1,0,-1,0,1][k]
  legs={}
  for role in ['left','right']:
   if direction=='left':
    lift=([0,0,0,0,1,3,4,2] if role=='left' else [1,3,4,2,0,0,0,0])[k]
    dx=([-5,0,5,10,10,5,0,-5] if role=='left' else [5,0,-5,-10,-10,-5,0,5])[k]
   else:
    lift=([0,0,0,0,2,5,6,3] if role=='left' else [2,5,6,3,0,0,0,0])[k];dx=0
   legs[role]={'lift':lift,'foot_dx':dx,'support':lift==0,'cloth_owner':role=='left','knee_outward':(0 if lift<2 else 1 if lift<5 else 2)}
  rows.append({'frame':k+1,'cycle_index':k,'pelvis_offset':pd,'upper_offset':cd,'head_offset':cd.copy(),'neck_offset':cd.copy(),'legs':legs,'arm_swing':[-2,-1,1,2,2,1,-1,-2][k],'foreground_leg':('left' if direction=='left' else ('left' if k<4 else 'right')),'shroud_leg':'left','cloth_phase_index':(k-1)%8,'head_neck_chest_one_group':True})
 plans[direction]={'source':str(S/('skeleton_B.png' if direction=='front' else f'skeleton_B_{direction}.png')),'frames':rows,'start':[{'exact_standard':True},{'blend_to_walk1':.35,'pelvis_leads':True},{'blend_to_walk1':.7}],'stop':[{'blend_from_walk8_to_standard':.3},{'blend_from_walk8_to_standard':.65},{'exact_standard':True}],'notes':'anatomical IDs; foreground order is depth, not leading foot; upper is one immutable source group; source parts partition entire standing exactly.'}
(V/'parts_plan_before_drawing.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2));(V/'foot_references.json').write_text(json.dumps(refs,indent=2))
lines=['# 逐帧零件表（绘制前）','','每个方向独立取站姿；没有读取任何旧行走图片。L/R 均为角色自身左右。头、颈、胸共用 upper 位移；裹尸布及踝带固定归左腿。背面的肩后垂布保留站姿右侧位置，左胫的小片破布固定在左腿。','']
for d,p in plans.items():
 lines+=['## '+d,'','|帧|骨盆 dx,dy|头颈胸 dx,dy|左腿 lift / dx|右腿 lift / dx|支撑|手臂摆幅|布相位|','|---|---|---|---|---|---|---|---|']
 for r in p['frames']:
  l=r['legs']['left'];rr=r['legs']['right'];lines.append(f"|{r['frame']}|{r['pelvis_offset']}|{r['upper_offset']}|{l['lift']} / {l['foot_dx']}|{rr['lift']} / {rr['foot_dx']}|{','.join(k for k,v in r['legs'].items() if v['support'])}|{r['arm_swing']}|{r['cloth_phase_index']+1}|")
 lines+=['','起步：站姿 → 骨盆先引动的约35%步态 → 约70%步态 → 循环1。停步：循环8 → 回收约30% → 回收约65% → 站姿。中间帧上身整体移动，颈长不变。','']
(V/'parts_plan_before_drawing.md').write_text('\n'.join(lines));print(json.dumps(refs,indent=2))
