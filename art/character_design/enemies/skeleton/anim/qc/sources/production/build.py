from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-skeleton-animation-20261026');S=R/'art/character_design/enemies/skeleton';O=W/'staged';F=O/'frames';F.mkdir(parents=True,exist_ok=True);pal=np.array(json.loads((W/'palette.json').read_text()),dtype=int);luma=pal@np.array([.299,.587,.114]);master=np.array(Image.open(S/'skeleton_B_right.png').convert('RGBA'))
def put(can,a,dx,dy):
 for y,x in zip(*np.where(a[:,:,3]>0)):
  yy=y+dy;xx=x+dx
  if 0<=yy<96 and 0<=xx<96:can[yy,xx]=a[y,x]
def clean(a):
 a=a.copy();c=a[:,:,:3].astype(int);a[(c[:,:,0]-c[:,:,1]>26)&(c[:,:,2]-c[:,:,1]>26)]=0;fg=a[:,:,3]>0;rgb=a[fg,:3].astype(int);a[fg,:3]=pal[((rgb[:,None]-pal[None])**2).sum(2).argmin(1)];return a
# Native pose sources; anticipation frames reuse a full generated contact pose with different limb/cloth edits.
source=[1,2,3,5,5,6,7,1];nearx=[68,63,58,53,48,53,58,63];farx=[48,53,58,63,68,63,58,53];ny=[95,95,95,95,95,94,93,94];fy=[95,94,93,94,95,95,95,95];hips=[0,1,0,0,0,1,0,0];upper=[0,0,1,0,0,0,1,0];hipx=[0,1,1,0,0,1,1,0];upx=[0,0,1,1,0,0,1,1]
# Stable planted feet from existing standard, not new texture or rotated parts.
feet={}
for n,box in [('near',(30,85,48,96)),('far',(48,78,68,94))]:
 f=master[box[1]:box[3],box[0]:box[2]].copy();bb=Image.fromarray(f).getbbox();f=f[bb[1]:bb[3],bb[0]:bb[2]];feet[n]=f
walk=[];rec=[]
for k,si in enumerate(source):
 a=np.array(Image.open(W/'prepared'/f'walk_{si:02}.png').convert('RGBA'));can=np.zeros((96,96,4),dtype=np.uint8)
 # Continuous whole-frame native row registration for 1px pelvis lead and delayed shoulder, fades to fixed knees.
 for y in range(65):
  if y<38:dy=upper[k];dx=upx[k]
  elif y<46:dy=hips[k] if y>=42 else upper[k];dx=hipx[k] if y>=42 else upx[k]
  elif y<58:dy=hips[k];dx=hipx[k]
  else:dy=round(hips[k]*(65-y)/7) if y<65 else 0;dx=round(hipx[k]*(65-y)/7) if y<65 else 0
  for x in np.where(a[y,:,3]>0)[0]:
   if y+dy<96 and x+dx<96:can[y+dy,x+dx]=a[y,x]
 # Skin-free skull stays the original standard pixels, only integer movement; original shoulder pins remain pose art.
 can[:20+upper[k]]=0;head=master[:20].copy();put(can,head,upx[k],upper[k])
 # Full generated lower-leg selections get small integer scanline adjustments to meet stable original feet.
 # Split at the inter-leg negative space; all directions retain their original lighting.
 split={1:50,2:43,3:53,5:50,6:44,7:53}[si];near_right=si in (1,2)
 for role,targetx,targety in [('far',farx[k],fy[k]),('near',nearx[k],ny[k])]:
  ft=feet[role];anchor=int(np.where(ft[-1,:,3]>0)[0].max());ox=targetx-anchor;oy=targety-ft.shape[0]+1
  # Existing generated shins remain intact at knee and meet the original ankle shape below.
  if split is not None:
   side=(lambda x: x>=split) if (near_right==(role=='near')) else (lambda x: x<split)
   refxs=np.array([x for x in np.where(a[85,:,3]>0)[0] if side(x)])
   if True:
    target_ankle=ox+int(np.median(np.where(ft[0,:,3]>0)[0]));refankle=int(np.median(refxs)) if len(refxs) else target_ankle;delta=target_ankle-refankle
    # Re-register existing lower-leg rows to meet exact unrotated source ankle.
    for y in range(65,oy):
     sy=min(y,86);dd=round(delta*(y-65)/max(1,oy-66))
     for x in np.where(a[sy,:,3]>0)[0]:
      if side(x) and 0<=x+dd<96:can[y,x+dd]=a[sy,x]
  # Toe/ankle integer translation; far foot is composited before near foot.
  put(can,ft,ox,oy)
 # Arm hanging offset at one beat: hand cluster shifts1px, gets pulled back next frame.
 if k in (2,6):
  region=can[40:54,28:39].copy();can[40:54,28:39]=0;put(can,region,27,40)
 # Repair the one native row exposed where pelvis drops before torso: inherit adjacent cloth/rope row.
 bridges=[]
 for yy in range(38,65):
  if not (can[yy,39:61,3]>0).any():
   can[yy,39:61]=can[yy-1,39:61];bridges.append(yy)
 # Palette calibration: constant mapping per color per anatomical band; no added dots/dither.
 tone=[]
 for b,(y0,y1) in enumerate([(0,20),(20,45),(45,65),(65,96)]):
  m=master[y0:y1];target=float((m[m[:,:,3]>0,:3]@np.array([.299,.587,.114])).mean());chunk=can[y0:y1];fg=chunk[:,:,3]>0;rgb=chunk[fg,:3].astype(int);before=float((rgb@np.array([.299,.587,.114])).mean());best=None
  # Preserve exact skull when its band already meets tolerance.
  for shift in ([0] if b==0 and abs(before-target)<=2 else np.arange(-65,65.1,.25)):
   probe=np.clip(rgb+shift,0,255);ix=((probe[:,None]-pal[None])**2).sum(2).argmin(1);out=pal[ix];mean=float((out@np.array([.299,.587,.114])).mean());err=abs(mean-target);cost=float(((out-rgb)**2).mean())
   key=(max(0,err-1.8),cost)
   if best is None or key<best[0]:best=(key,out,mean,float(shift))
  chunk[fg,:3]=best[1];tone.append({'band':b,'baseline':target,'before':before,'mean':best[2],'delta':best[2]-target,'constant_rgb_offset_before_nearest_palette':best[3]})
 walk.append(Image.fromarray(can));rec.append({'frame':k+1,'whole_pose_source':si,'pelvis_shift':[hipx[k],hips[k]],'shoulder_head_shift':[upx[k],upper[k]],'near_foot_toe':[nearx[k],ny[k]],'far_foot_toe':[farx[k],fy[k]],'support':'near_right' if k<4 else 'far_left','support_local':[nearx[k] if k<4 else farx[k],95],'world_translation':[5*k,0],'support_world':[nearx[k]+5*k if k<4 else farx[k]+5*k,95],'native_transition_bridge_rows':bridges,'tone':tone})
 for b in tone:assert abs(b['delta'])<=2,(k,b)
# Collapse uses full generated frames and exact immutable endpoints.
front=Image.open(S/'skeleton_B.png').convert('RGBA');pile=Image.new('RGBA',(96,96));pile.alpha_composite(Image.open(S/'skeleton_B_remains.png').convert('RGBA'),(0,48));collapse=[front];cr=[]
for mode,i in [('collapse',2),('collapse',3),('collapse',4),('collapse',5),('mid',2),('mid',3),('collapse',8)]:
 a=clean(np.array(Image.open(W/mode/f'frame_{i:02}.png').convert('RGBA')));bb=Image.fromarray(a).getbbox();a=a[bb[1]:bb[3],bb[0]:bb[2]];hh,ww=a.shape[:2]
 # Register whole falling pose at unchanged floor; skull travels right only after contact.
 ox=(96-ww)//2;oy=96-hh;can=np.zeros((96,96,4),dtype=np.uint8);put(can,a,ox,oy)
 if len(collapse)==1:
  # Delay only the intact skull by one beat; shoulder/torsobody is the newly generated collapse frame.
  can[:20]=0;put(can,np.array(front)[:20],0,0)
  # Pelvis gives way before shoulders: one contiguous inverse native-row lookup, feet/head unchanged.
  cr_rows=[*range(36),36,37,38,39,39,40,41,42,42,43,44,45,46,46,*range(47,59),*[y for y in range(59,80) if y not in [65,70,75]],*range(80,96)]
  assert len(cr_rows)==96
  can=can[cr_rows].copy()
 collapse.append(Image.fromarray(can));cr.append({'source_action':mode,'source_frame':i,'source_crop':bb,'integer_registration':[ox,oy],'native_bbox':[ww,hh],'pelvis_lead_native_row_lookup':cr_rows if len(collapse)==2 else None})
# Skull reaches its actual final group at first ground contact; tiny final bounce.
pile_a=np.array(pile)
f7=np.array(collapse[6]);f7[65:92,65:90]=0;put(f7,pile_a[65:92,65:90],65,65);collapse[6]=Image.fromarray(f7);cr[5]['final_skull_source']={'image':'padded_original_remains','crop':[65,65,90,92],'offset':[65,65]}
# The penultimate pose is settled bones, only the shroud and skull settling 1px.
f8=pile_a.copy();mask=Image.new('1',(96,96));ImageDraw.Draw(mask).polygon([(23,68),(39,68),(66,79),(64,87),(39,86),(24,79)],fill=1);cm=np.array(mask,dtype=bool)&(pile_a[:,:,3]>0);cloth=np.zeros_like(pile_a);cloth[cm]=pile_a[cm];put(f8,cloth,0,-1)
f8[65:92,65:90]=0;put(f8,pile_a[65:92,65:90],65,64);collapse[7]=Image.fromarray(f8);cr[6]={'final_source':'padded_original_remains','changes':'Cloth fold overlay up1px, original bones held; skull crop [65,65,90,92] shifted up1px. Former generated collapse08 pose not used in final.'}
collapse.append(pile)
for name,frames in [('skeleton_B_walk_right',walk),('skeleton_B_collapse_front',collapse)]:
 (F/name).mkdir(exist_ok=True);sheet=Image.new('RGBA',(96*len(frames),96))
 for i,f in enumerate(frames):f.save(F/name/f'{i+1:02}.png');sheet.alpha_composite(f,(96*i,0))
 sheet.save(O/(name+'.png'))
(W/'edit_records.json').write_text(json.dumps({'walk':rec,'collapse':cr,'foot_sources':{'near':[30,85,48,96],'far':[48,78,68,94]}},indent=2))
# Native contact sheet, no annotations over art.
for mode,frames,cols in [('walk',walk,4),('collapse',collapse,3)]:
 board=Image.new('RGBA',(cols*112,((len(frames)+cols-1)//cols)*116),'#403D3F');d=ImageDraw.Draw(board)
 for i,f in enumerate(frames):x=i%cols*112;y=i//cols*116;board.alpha_composite(f,(x+8,y));d.text((x+8,y+100),str(i+1),fill='white')
 board.resize((board.width*4,board.height*4),Image.Resampling.NEAREST).save(W/(mode+'_contact_4x.png'))
print('built walk8 / collapse9')
