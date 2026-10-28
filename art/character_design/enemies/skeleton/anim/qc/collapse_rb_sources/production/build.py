from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-collapse-rb-213-20261028');O=W/'staged';Q=O/'qc';V=Q/'collapse_rb_sources';load=lambda p:np.array(Image.open(p).convert('RGBA'));pal=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),np.uint8);end=load(V/'canonical_final.png');H=load(V/'canonical_single_skull.png');B=load(V/'canonical_headless_heap.png');groups={n:load(V/('heap_group_'+n+'.png')) for n in ['hands','shoulder_pins','rib_spine','shroud','long_bones_pelvis']};durations=[100,110,90,80,70,70,70,80,100,130,180,200];timings={};allrecords={}
def crop(a):
 ys,xs=np.where(a[:,:,3]>0);return a[ys.min():ys.max()+1,xs.min():xs.max()+1].copy()
def poly(shape,points):
 im=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def masked(a,m):
 b=np.zeros_like(a);b[m]=a[m];return b
def put(a,p,dx=0,dy=0):
 ys,xs=np.where(p[:,:,3]>0);xx=xs+dx;yy=ys+dy;k=(xx>=0)&(xx<96)&(yy>=0)&(yy<96);a[yy[k],xx[k]]=p[ys[k],xs[k]]
def fitrows(a,target):
 h=a.shape[0];need=h-target
 if need<=0:return a.copy(),list(range(h)),[]
 candidates=list(range(23,max(24,h-10)));removed=[]
 for f in np.linspace(0,len(candidates)-1,need):
  r=candidates[round(f)]
  while r in removed:r+=1
  removed.append(r)
 keep=[i for i in range(h) if i not in removed];assert len(keep)==target;return a[keep].copy(),keep,sorted(removed)
def rect(shape,box):
 x0,y0,x1,y1=box;a=np.zeros(shape[:2],bool);a[y0:y1,x0:x1]=True;return a

def head_mask(d,k,a):
 if d=='right':
  boxes={2:(17,0,37,21),3:(22,0,41,21),4:(25,0,46,21),5:(60,0,77,22),6:(78,9,95,30)};return rect(a.shape,boxes[k])
 if k==5:return rect(a.shape,(38,0,59,20))
 if k==6:return rect(a.shape,(46,0,68,20))
 # Back skull has no coffin pins above it; locate its crown, then cover only the cranium/short neck.
 ys,xs=np.where(a[:8,:,3]>0);x0=max(0,int(xs.min())-3);x1=min(a.shape[1],int(xs.max())+5);return rect(a.shape,(x0,0,x1,20))

def prune_crumbs(a):
 todo=set(zip(*np.where(a[:,:,3]>0)))
 while todo:
  q=[todo.pop()];cc=q.copy()
  while q:
   y,x=q.pop()
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     p=(y+dy,x+dx)
     if p in todo:todo.remove(p);q.append(p);cc.append(p)
  if len(cc)<=5:
   for y,x in cc:a[y,x]=0
 return a

def emit(d,fs,rs,heads,bodies):
 name='skeleton_B_collapse_'+d;F=O/'frames'/name;F.mkdir(parents=True,exist_ok=True);L=V/d/'layers';L.mkdir(exist_ok=True);sheet=Image.new('RGBA',(96*len(fs),96));board=Image.new('RGBA',(4*112,3*116),'#403D43');dr=ImageDraw.Draw(board)
 for k,a in enumerate(fs):
  Image.fromarray(a).save(F/f'{k+1:02}.png');sheet.paste(Image.fromarray(a),(k*96,0));dd=L/f'{k+1:02}';dd.mkdir(exist_ok=True);Image.fromarray(heads[k]).save(dd/'single_skull.png');Image.fromarray(bodies[k]).save(dd/'body_no_skull.png');x=k%4*112+8;y=k//4*116;board.alpha_composite(Image.fromarray(a),(x,y));dr.text((x,y+99),str(k+1),fill='white');rs[k]['duration_ms']=durations[k]
 sheet.save(O/(name+'.png'));board.resize((1792,1392),Image.Resampling.NEAREST).save(Q/(name+'_contact_4x.png'));flat=[0,0,0]+pal.flatten().tolist();flat+=[0]*(768-len(flat));ims=[]
 for a in fs:
  ix=np.zeros((96,96),np.uint8)
  for k,c in enumerate(pal):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=k+1
  assert np.array_equal(ix>0,a[:,:,3]>0);im=Image.fromarray(ix).convert('P');im.putpalette(flat);ims.append(im.resize((768,768),Image.Resampling.NEAREST))
 ims[0].save(Q/(name+'_8x.gif'),save_all=True,append_images=ims[1:],duration=durations,transparency=0,disposal=2,optimize=False);timings[name]={'frames':len(fs),'durations_ms':durations,'loop':False,'sprite_sheet':name+'.png','hold_last_frame':True};allrecords[d]=rs

for d in ['right','back']:
 master=load(S/f'skeleton_B_{d}.png');src=V/d;raws={k:load(src/f'palette_crop_{k:02}.png') for k in range(1,7)};fs=[master.copy()];hh=masked(master,rect(master.shape,(38,0,64,20) if d=='right' else (39,0,58,15)));bb=master.copy();bb[hh[:,:,3]>0]=0;heads=[hh];bodies=[bb];rs=[{'frame':1,'exact_standard':True,'source':f'skeleton_B_{d}.png','one_active_skull':True}];maps={};earlyheads={}
 for k,target in [(2,94),(3,88),(4,80),(5,76)]:
  a=raws[k];b,keep,removed=fitrows(a,target);ox=48-b.shape[1]//2;oy=96-b.shape[0];can=np.zeros_like(master);put(can,b,ox,oy);hp=masked(a,head_mask(d,k,a))[keep];hl=np.zeros_like(master);head_dx=0
  if d=='right' and k==5:
   # A forward-splayed leg widens the source crop. Register skull+short neck left by 10 native pixels, without flipping or scaling.
   cm=head_mask(d,k,a)|rect(a.shape,(48,6,60,14));chunk=masked(a,cm)[keep];cc=np.zeros_like(master);put(cc,chunk,ox,oy);can[cc[:,:,3]>0]=0;put(can,cc,-10,0);head_dx=-10
  put(hl,hp,ox+head_dx,oy);bl=can.copy();bl[hl[:,:,3]>0]=0;fs.append(can);heads.append(hl);bodies.append(bl);maps[k]={'offset':[ox,oy],'skull_neck_native_dx':head_dx,'row_lookup':keep,'removed_internal_rows':removed};earlyheads[k]=hl;rs.append({'frame':k,'direction_pose_source':k,'source':str(src/f'palette_crop_{k:02}.png'),'one_active_skull':True,'pose':'loose_joints_fall','active_bone_groups':{'skull':'new_direction_pose','shoulder_chest':'new_direction_pose','pelvis':'new_direction_pose','arms_hands':'new_direction_pose','legs_feet':'new_direction_pose','shroud':'new_direction_pose'},**maps[k]})
 # Native frame5 has one set of falling chest/shoulder/pelvis/arms, excluding both head and legs.
 r5=raws[5];hm5=head_mask(d,5,r5);keep=maps[5]['row_lookup'];ox,oy=maps[5]['offset']
 if d=='right':
  arms=rect(r5.shape,(19,15,39,47));torso=poly(r5.shape,[(38,0),(48,0),(51,6),(60,8),(60,15),(54,17),(57,34),(40,36),(31,29),(30,15)]);pelvis=rect(r5.shape,(34,37,57,53))
 else:
  arms=rect(r5.shape,(0,26,15,64))|rect(r5.shape,(53,31,75,79));torso=poly(r5.shape,[(18,8),(34,10),(41,17),(55,22),(61,36),(53,46),(33,43),(18,33),(14,20)]);pelvis=rect(r5.shape,(20,49,55,71))
 fall=masked(r5,(arms|torso|pelvis)&~hm5)[keep];fallcan=np.zeros_like(master);put(fallcan,fall,ox,oy)
 if d=='right':
  neck=masked(r5,rect(r5.shape,(48,6,60,14)))[keep];nc=np.zeros_like(master);put(nc,neck,ox,oy);fallcan[nc[:,:,3]>0]=0;put(fallcan,nc,-10,0)
 Image.fromarray(fallcan).save(src/'airborne_headless_torso_arms_pelvis.png');hp5=crop(earlyheads[5]);roll=crop(masked(raws[6],head_mask(d,6,raws[6])));Image.fromarray(hp5).save(src/'skull_droop.png');Image.fromarray(roll).save(src/'skull_ground_turn.png');canon=crop(H)
 if d=='right':centers=[(69,44),(71,58),(73,72),(74,79),(73,75),(73,76)];fall_offsets=[(0,8),(0,15)]
 else:centers=[(62,43),(66,57),(70,71),(73,79),(73,75),(73,76)];fall_offsets=[(0,10),(2,18)]
 for i in range(6):
  k=i+6;bl=np.zeros_like(master);body_offsets={'long_bones_pelvis':(0,0)}
  if i<2:
   body_offsets['shroud']=((-1,-8-i*-3) if d=='right' else (0,-10+i*3))
   for n,(dx,dy) in body_offsets.items():put(bl,groups[n],dx,dy)
   put(bl,fallcan,*fall_offsets[i]);bl=prune_crumbs(bl)
   active={'skull':'direction_droop','shoulder_chest':'airborne_direction','pelvis':'airborne_direction','arms_hands':'airborne_direction','legs_feet':'canonical_ground','shroud':'upper_direction_plus_lower_hem'}
  else:
   body_offsets.update({'shoulder_pins':(0,-1 if i==2 else 0),'rib_spine':(0,-2 if i==2 else 0),'hands':(0,0),'shroud':(0,[-4,-2,-1,0][i-2])})
   for n,(dx,dy) in body_offsets.items():put(bl,groups[n],dx,dy)
   active={n:'canonical_ground' for n in ['shoulder_chest','pelvis','arms_hands','legs_feet','shroud']};active['skull']='ground_turn' if i==2 else 'canonical_skull'
  hp=hp5 if i<2 else roll if i==2 else canon;cx,cy=centers[i];hl=np.zeros_like(master);put(hl,hp,cx-hp.shape[1]//2,cy-hp.shape[0]//2);a=bl.copy();put(a,hl);fs.append(a);heads.append(hl);bodies.append(bl);rs.append({'frame':k,'one_active_skull':True,'skull_pose':'posterior' if d=='back' and i<2 else 'ground_turn' if i==2 else 'droop' if i<2 else 'canonical','head_target_center':[cx,cy],'body_group_offsets':{n:list(off) for n,off in body_offsets.items()},'airborne_to_ground_handoff':i==2,'active_bone_groups':active})
 fs.append(end.copy());heads.append(H.copy());bodies.append(B.copy());rs.append({'frame':12,'exact_canonical_heap':True,'one_active_skull':True,'active_bone_groups':{n:'canonical_ground' for n in ['skull','shoulder_chest','pelvis','arms_hands','legs_feet','shroud']}});emit(d,fs,rs,heads,bodies)
(V/'frame_records.json').write_text(json.dumps(allrecords,ensure_ascii=False,indent=2));(V/'timing_entries.json').write_text(json.dumps(timings,indent=2));print('Built two independent directional strips:',len(timings),'actions,24 frames; shared canonical endpoint.')
