from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-combat-trial-20261028');O=W/'staged';O.mkdir(exist_ok=True);plan=json.loads((W/'plan.json').read_text());A=R/'art/character_design';S=A/'enemies/skeleton'
def load(p):return np.array(Image.open(p).convert('RGBA'))
def polygon(shape,points):
 b=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(b).polygon(points,fill=255);return np.array(b)>0

def put(dst,src,dx=0,dy=0):
 yy,xx=np.where(src[:,:,3]>0);ty=yy+dy;tx=xx+dx;assert ((tx>=0)&(tx<dst.shape[1])&(ty>=0)&(ty<dst.shape[0])).all();dst[ty,tx]=src[yy,xx]

def part(a,m):b=np.zeros_like(a);b[m]=a[m];return b

def export(n,frames,fw):
 D=O/'frames'/n;D.mkdir(parents=True,exist_ok=True);strip=Image.new('RGBA',(len(frames)*fw,96));board=Image.new('RGBA',(4*(fw+8),((len(frames)+3)//4)*112),'#403d43');dr=ImageDraw.Draw(board)
 for k,a in enumerate(frames):
  im=Image.fromarray(a);im.save(D/f'{k+1:02}.png');strip.alpha_composite(im,(fw*k,0));x=k%4*(fw+8);y=k//4*112;board.alpha_composite(im,(x,y));dr.text((x+2,y+98),str(k+1),fill='white')
 strip.save(O/(n+'.png'));board.resize((board.width*3,board.height*3),Image.Resampling.NEAREST).save(W/(n+'_contact3x.png'))

# HERO: complete approved body with a one-pixel restrained lean; exact feet and lower coat retained.
M=load(A/'hero_B1_right.png');yy,xx=np.indices((96,96));lampmask=(yy>=45)&(yy<=60)&(xx>=58)&(xx<=66)&(M[:,:,3]>0);lamp=part(M,lampmask);body=M.copy();body[lampmask]=0
coats=part(M,(yy>=20)&(yy<40)&(xx>=35)&(xx<53));coatpal=np.unique(coats[coats[:,:,3]>0,:3],axis=0).astype(int);handcolors=M[40:45,55:65];skinpal=np.unique(handcolors[handcolors[:,:,3]>0,:3],axis=0).astype(int)
hero=[];herorows=[]
for r in plan['hero']:
 if r['f'] in [1,8]:a=M.copy();castmask=np.zeros((96,96),bool)
 else:
  a=np.zeros_like(M);dx=r['body_dx']
  for sy in range(96):
   sx=np.where(body[sy,:,3]>0)[0];d=dx if sy<60 else 0; a[sy,sx+d]=body[sy,sx]
  if r['arm_pose'] in [2,3,4,5,6]:
   g=load(W/f'hero_{r["arm_pose"]:02}.png');mask=(xx>=48)&(yy>=11)&(yy<=33)
   if r['arm_pose'] in [2,3,6]:mask &= polygon(g.shape,[(48,19),(59,17),(67,20),(66,28),(58,34),(48,33)])
   else:mask &= polygon(g.shape,[(48,21),(60,19),(65,14),(73,11),(80,18),(78,25),(65,28),(56,32),(48,31)])
   p=part(g,mask);ys,xs=np.where(p[:,:,3]>0)
   # Same-material color subset: coat sleeve and standard pale hand.
   for sy,sx in zip(ys,xs):
    skin=(sx>=64 if r['arm_pose'] in [4,5] else sx>=53 and sy<=26)
    pal=skinpal if skin else coatpal;c=p[sy,sx,:3].astype(int);p[sy,sx,:3]=pal[((pal-c)**2).sum(1).argmin()]
   castmask=np.zeros((96,96),bool);ady=8 if r['arm_pose'] in [4,5] else 4;put(a,p,dx,ady);castmask[ady:,dx:]|=p[:96-ady,:96-dx,3]>0
  else:castmask=np.zeros((96,96),bool)
  # Anchor the handle to the unchanged holding hand; only lower lamp rows swing.
  for sy,sx in zip(*np.where(lamp[:,:,3]>0)):
   swing=round(r['lamp_bottom_dx']*max(0,(sy-47)/13));a[sy,sx+dx+swing]=lamp[sy,sx]
 assert np.array_equal(a[78:],M[78:]);hero.append(a);dd=O/'qc/combat_sources/hero_layers';dd.mkdir(parents=True,exist_ok=True);Image.fromarray(part(a,castmask)).save(dd/f'{r["f"]:02}_casting_arm.png')
 herorows.append({'frame':r['f'],'lantern_grip':[61+r['body_dx'],44],'handle_top':[61+r['body_dx'],45],'lamp_bottom_extra_dx':r['lamp_bottom_dx'],'foot_pixels_y78_95_exact':True,'cast_added_pixels':int(castmask.sum())})
export('hero_B1_cast_right',hero,96);(W/'hero_pose_records.json').write_text(json.dumps(herorows,indent=2))

# SKELETON: original complete body; exact rigid head/neck/thorax; own arm pose imagery.
master=load(S/'skeleton_B_right.png');parts={p.stem:load(p) for p in (S/'anim/qc/v5_sources/standing_parts').glob('*.png')};arm0=parts['near_right_arm'];body=master.copy();body[arm0[:,:,3]>0]=0;fw=160;off=32;full=np.zeros((96,fw,4),np.uint8);put(full,master,off,0);syy,sxx=np.indices((96,fw))
polys={
 '3':[(73,18),(76,21),(72,25),(67,28),(65,34),(69,39),(67,44),(63,42),(57,36),(55,29),(58,25),(65,21)],
 '4':[(72,18),(76,21),(73,25),(66,26),(62,27),(61,31),(65,35),(70,40),(69,44),(64,42),(59,37),(55,31),(55,26),(58,22),(65,19)],
 '7':[(73,20),(76,23),(72,30),(68,34),(70,36),(78,38),(87,39),(93,44),(87,46),(78,43),(68,41),(63,39),(62,33),(66,26)],
 '8':[(73,20),(76,24),(73,30),(71,34),(74,39),(78,44),(77,50),(72,52),(67,49),(67,42),(66,36),(68,29)]}
hit=load(W/'hit_restored.png');hitmask=polygon(hit.shape,[(74,18),(80,18),(83,19),(99,19),(105,20),(149,20),(153,24),(149,28),(115,28),(103,26),(98,25),(82,24),(76,26)])
armhit=part(hit,hitmask);skel=[];skelrows=[];layers=O/'qc'/'combat_sources'/'skeleton_layers';layers.mkdir(parents=True,exist_ok=True)
for r in plan['skeleton']:
 k=r['f'];pd=r['pelvis'];ud=r['upper'];a=np.zeros((96,160,4),np.uint8)
 if k in [1,9]:a=full.copy();near=np.zeros_like(a);put(near,arm0,32,0)
 else:
  # Soft pelvis ties and cloth are positioned together from the same whole portrait.
  for sy in range(40,96):
   if sy<48:dx,dy=pd
   elif sy<62:t=(62-sy)/14;dx=round(pd[0]*t);dy=round(pd[1]*t)
   else:dx=dy=0
   sx=np.where(body[sy,:,3]>0)[0];a[sy+dy,sx+32+dx]=body[sy,sx]
  upper=part(body,yy<40);put(a,upper,32+ud[0],ud[1])
  # Fill only the flexible waist-tie row if pelvis led the chest by one pixel.
  for y in range(40+ud[1],40+pd[1]):
   sx=np.where(body[40,:,3]>0)[0];a[y,sx+32+pd[0]]=body[40,sx]
  near=np.zeros_like(a);pose=r['arm_pose']
  if pose=='standard':put(near,arm0,32+ud[0],ud[1])
  elif pose=='8':
   for y,x in zip(*np.where(arm0[:,:,3]>0)):
    swing=round(max(0,min(2,(y-25)/16)));near[y+ud[1],x+32+ud[0]+swing]=arm0[y,x]
  elif pose in ['hit','hit_follow']:
   p=armhit.copy();dx=-5+ud[0];dy=3+ud[1]
   if pose=='hit_follow':
    # Native column offsets make a slight downward settling sweep, no bitmap rotation.
    for y,x in zip(*np.where(p[:,:,3]>0)):
     ey=y+dy+round(max(0,x-82)*.055);near[ey,x+dx]=p[y,x]
   else:put(near,p,dx,dy)
  else:
   g=load(W/f'skeleton_{int(pose):02}.png');p=part(g,polygon(g.shape,polys[pose]));put(near,p,-7+ud[0],3+ud[1])
  put(a,near)
  # Shoulder cap remains the same bone pixels, follows the rigid shoulder, bridges to the generated arm root.
  cap=part(arm0,(yy>=23)&(yy<=25));put(a,cap,32+ud[0],ud[1])
  # The shroud stays on the far left leg; only its free outside edge settles a beat late.
  lag={2:0,3:0,4:-1,5:-1,6:1,7:1,8:1}.get(k,0)
  if lag:
   free=(yy>=65)&(yy<81)&(xx>=56)&(master[:,:,3]>0);p=part(master,free);a[yy[free],xx[free]+32]=0;put(a,p,32+lag,0)
 assert np.array_equal(a[84:,32:128],master[84:]);skel.append(a);Image.fromarray(near).save(layers/f'{k:02}_attacking_arm.png')
 ar=np.where(near[:,:,3]>0);tip=[int(ar[1].max()),int(np.median(ar[0][ar[1]==ar[1].max()]))] if len(ar[0]) else None
 skelrows.append(dict(r,arm_tip=tip,tip_offset_from_root=tip[0]-80,feet_exact_standard=True,head_neck_thorax_translation=ud))
export('skeleton_B_attack_right',skel,160);(W/'skeleton_pose_records.json').write_text(json.dumps(skelrows,indent=2))
