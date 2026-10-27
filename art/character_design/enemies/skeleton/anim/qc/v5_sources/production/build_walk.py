from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-v5-20261027');O=W/'staged';F=O/'frames';Q=O/'qc';V=Q/'v5_sources';F.mkdir(parents=True,exist_ok=True);V.mkdir(parents=True,exist_ok=True)
M=np.array(Image.open(S/'skeleton_B_right.png').convert('RGBA'));plan=json.loads((W/'parts_plan_before_drawing.json').read_text());fg=M[:,:,3]>0;pal=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),int);ids=((M[:,:,:3,None].transpose(0,1,3,2).astype(int)-pal[None,None])**2).sum(3).argmin(2);parts={};used=np.zeros((96,96),bool)
def rect(x0,y0,x1,y1):a=np.zeros((96,96),bool);a[y0:y1,x0:x1]=True;return a
def take(n,mask):
 global used
 mask=mask&fg&~used;p=np.zeros_like(M);p[mask]=M[mask];parts[n]=p;used|=mask
# Exact semantic partition of the single approved portrait; no prior walk image is read.
take('head',rect(40,0,63,20));arm=np.zeros((96,96),bool)
for y0,y1,x0,x1 in [(23,29,31,39),(29,35,29,37),(35,44,28,36),(44,47,28,37),(47,59,28,38)]:arm[y0:y1,x0:x1]=True
take('near_right_arm',arm);take('thorax',rect(0,0,96,40));take('pelvis',rect(0,40,96,48));near=rect(0,48,48,96);near[48:78]&=~np.isin(ids[48:78],[26,27,28,29,30,31,32,33,36]);take('near_right_leg',near);take('far_left_leg_shroud',np.ones((96,96),bool));assert np.array_equal(sum((a.astype(np.uint16) for a in parts.values())).astype(np.uint8),M)
D=V/'standing_parts';D.mkdir(exist_ok=True)
for n,p in parts.items():Image.fromarray(p).save(D/(n+'.png'))
footref={}
for role,name,box in [('right','near_right_leg',(0,84,48,96)),('left','far_left_leg_shroud',(48,84,76,96))]:
 p=parts[name];x0,y0,x1,y1=box;ys,xs=np.where(p[y0:y1,x0:x1,3]>0);bottom=y0+ys.max();toe=x0+xs[ys==ys.max()].max();footref[role]={'bottom':int(bottom),'toe':int(toe),'source_foot_box':box}

def put(a,p,dx,dy,owner,which):
 for y,x in zip(*np.where(p[:,:,3]>0)):
  xx=x+dx;yy=y+dy
  if 0<=xx<96 and 0<=yy<96:a[yy,xx]=p[y,x];owner[yy,xx]=which

def render(r,stand=False,armblend=1):
 if stand:return M.copy(),np.zeros((96,96),np.uint8),{}
 a=np.zeros_like(M);own=np.zeros((96,96),np.uint8);lay={};pd=r['pelvis_offset'];cd=r['chest_offset'];hd=r['head_offset']
 for name,role,which in [('far_left_leg_shroud','left',1),('near_right_leg','right',2)]:
  p=parts[name];ref=footref[role];toe=r['far_toe_x'] if role=='left' else r['near_toe_x'];lift=r['far_lift'] if role=='left' else r['near_lift'];ankdx=toe-ref['toe'];ankdy=95-lift-ref['bottom'];out=np.zeros_like(M)
  # Native source rows register onto a bent hip/knee/ankle chain; foot pixels translate as one unchanged shape.
  destrows=[]
  for sy in range(48,84):
   t=(sy-48)/36;dy=round(np.interp(sy,[48,65,84],[0,-lift*.4,ankdy]));destrows.append(sy+dy)
  for yy in range(min(destrows),max(destrows)+1):
   sy=48+int(np.argmin(np.abs(np.array(destrows)-yy)));t=(sy-48)/36;knee=round((1 if role=='right' else -1)*max(0,1-abs(sy-65)/17)*(.5 if lift<2 else 1))
   for sx in np.where(p[sy,:,3]>0)[0]:
    dx=round(np.interp(sy,[48,65,84],[pd[0],pd[0]+max(-1,min(1,ankdx*.12)),ankdx]))+knee
    if role=='left' and 51<=sy<76 and ids[sy,sx] in [*range(18),20,21,23,25,*range(26,34),36]:
     # Only the free middle fold lags. The wrapped shin/ankle anchor uses the current LEFT leg.
     dx=round(np.interp(sy,[48,64,84],[pd[0],pd[0],ankdx]))
     prev=plan['frames'][(r.get('cycle_index',r['frame']-1)-1)%8];lag=prev['far_toe_x']-r['far_toe_x'];dx+=round(max(-2,min(0,lag*.3))*np.sin((sy-66)/14*np.pi)) if 67<=sy<81 and (sx<=50 or sx>=58) and not r.get('disable_hem_lag',False) else 0
    xx=sx+dx
    if 0<=xx<96 and 0<=yy<96:out[yy,xx]=p[sy,sx]
  for sy,sx in zip(*np.where(p[84:,:,3]>0)):
   sy+=84;xx=sx+ankdx;yy=sy+ankdy
   if 0<=xx<96 and 0<=yy<96:out[yy,xx]=p[sy,sx]
  lay[name]=out.copy();put(a,out,0,0,own,which)
 # Pelvis and chest are exact rigid source pixel sets. Flexible waist ties bridge their 0-2px separation.
 pp=parts['pelvis'];put(a,pp,*pd,own,3)
 for yy in range(39+cd[1]+1,40+pd[1]):
  for sx in range(36,61):
   if M[40,sx,3]:xx=sx+pd[0];a[yy,xx]=M[40,sx];own[yy,xx]=4
 put(a,parts['thorax'],*cd,own,5)
 # Whole near-arm chain starts at the fixed shoulder; it hangs forward toward the pelvis, with a small swing.
 ar=np.zeros_like(M);swing=r.get('near_arm_swing',0);p=parts['near_right_arm']
 for sy,sx in zip(*np.where(p[:,:,3]>0)):
  if sy<35:w=(sy-23)/12;forward=round((4+swing*.3)*max(0,w)*armblend)
  elif sy<47:w=(sy-35)/12;forward=round((4+w*(3+swing*.7))*armblend)
  else:forward=round((7+swing)*armblend)
  xx=sx+cd[0]+forward;yy=sy+round(cd[1]*min(1,max(0,(47-sy)/12)))
  if 0<=xx<96 and 0<=yy<96:ar[yy,xx]=p[sy,sx]
 put(a,ar,0,0,own,6);lay['near_right_arm']=ar
 put(a,parts['head'],*hd,own,7)
 # Missing elbow pixels from integer changes are filled from the same original bone row, never from an old walk frame.
 for yy in range(25+cd[1],58+cd[1]):
  if not (ar[yy,:,3]>0).any() and (ar[yy-1,:,3]>0).any() and (ar[yy+1,:,3]>0).any():
   row=ar[yy-1].copy();aa=row[:,3]>0;a[yy,aa]=row[aa];own[yy,aa]=6
 return a,own,lay

ALL={};tim={};records={}
def save(n,fs,ds,rs):
 ALL[n]=fs;tim[n]={'frames':len(fs),'durations_ms':ds,'loop':n=='skeleton_B_walk_right_v5','sprite_sheet':n+'.png'};records[n]=rs;D=F/n;D.mkdir(exist_ok=True);b=Image.new('RGBA',(96*len(fs),96))
 for k,p in enumerate(fs):Image.fromarray(p).save(D/f'{k+1:02}.png');b.alpha_composite(Image.fromarray(p),(k*96,0))
 b.save(O/(n+'.png'))
# Final timing refinement after the pre-draw table: low pelvis landing, held pass, smaller delayed chest/head excursion.
for k,r in enumerate(plan['frames']):
 signal=[2,2,0,0,2,2,0,0]
 r['pelvis_offset']=[0,signal[k]];r['chest_offset']=[0,signal[(k-1)%8]//2];r['head_offset']=[0,signal[(k-2)%8]//2]
 r['near_arm_swing']=[-2,-1,1,2,2,1,-1,-2][k]
 r['near_hand_target']=[40+r['chest_offset'][0]+r['near_arm_swing'],53+r['chest_offset'][1]]
 r['far_hand_target']=[48-r['near_arm_swing'],51+r['chest_offset'][1]]
walk=[];wr=[]
for k,r0 in enumerate(plan['frames']):
 r=dict(r0);r['cycle_index']=k;im,owner,layers=render(r);walk.append(im);wr.append(r);dd=V/'walk_layers'/f'{k+1:02}';dd.mkdir(parents=True,exist_ok=True)
 for n,p in layers.items():Image.fromarray(p).save(dd/(n+'.png'))
 Image.fromarray(owner).save(dd/'ownership.png')
 for n,key in [('head','head_offset'),('thorax','chest_offset'),('pelvis','pelvis_offset')]:
  p=np.zeros_like(M);dummy=np.zeros((96,96),np.uint8);put(p,parts[n],*r[key],dummy,1);Image.fromarray(p).save(dd/(n+'_rigid.png'))
save('skeleton_B_walk_right_v5',walk,[100]*8,wr)
# Explicit coherent whole-portrait intermediate, not a pasted strip from an old cycle.
# Search only coherent complete-pose intermediates, never selecting arbitrary pixels from two endpoint frames.
def transition_pose(first,last,target,kind):
 best=None
 for nr in [0,.25,.5,.75,1]:
  for fr in [0,.25,.5,.75,1]:
   for hip in [0,1,2]:
    for hh in [0,1]:
     for blend in [0,.5,1]:
      r=dict(target);n0=footref['right']['toe'];f0=footref['left']['toe'];r.update({'near_toe_x':round(n0*(1-nr)+target['near_toe_x']*nr),'far_toe_x':round(f0*(1-fr)+target['far_toe_x']*fr),'near_lift':0,'far_lift':1,'pelvis_offset':[0,hip],'chest_offset':[0,0],'head_offset':[0,hh],'near_arm_swing':0})
      im,_,_=render(r,armblend=blend);d1=int((first!=im).any(2).sum());d2=int((im!=last).any(2).sum());key=(max(d1,d2),d1+d2,abs(nr-.5)+abs(fr-.5))
      if best is None or key<best[0]:best=(key,im,r,blend,d1,d2)
 return best
st=transition_pose(M,walk[0],wr[0],'start');sp=transition_pose(walk[-1],M,wr[-1],'stop')
for data in [st,sp]:data[2]['arm_pose_blend']=data[3];data[2]['endpoint_pixel_changes']=[data[4],data[5]]
# Start actually leads with the pelvis, then advances the right leg; no duplicated walk frame is baked into the bridge.
lead=dict(wr[0]);lead.update({'near_toe_x':footref['right']['toe'],'far_toe_x':footref['left']['toe'],'near_lift':0,'far_lift':2,'pelvis_offset':[0,1],'chest_offset':[0,0],'head_offset':[0,0],'near_arm_swing':0,'disable_hem_lag':True,'arm_pose_blend':.5})
pre=dict(wr[0]);pre.update({'far_toe_x':footref['left']['toe'],'far_lift':2,'disable_hem_lag':True,'arm_pose_blend':1})
li,_,_=render(lead,armblend=.5);pi,_,_=render(pre)
save('skeleton_B_walk_start_right',[M.copy(),li,pi],[100]*3,[{'exact_standard':True},lead,pre])
settle=dict(wr[-1]);settle.update({'near_toe_x':wr[-1]['near_toe_x']-1,'near_lift':1,'arm_pose_blend':1});si,_,_=render(settle)
save('skeleton_B_walk_stop_right',[si,sp[1],M.copy()],[100]*3,[settle,sp[2],{'exact_standard':True}])
for n,fs in ALL.items():
 cols=4;rows=(len(fs)+3)//4;b=Image.new('RGBA',(cols*112,rows*116),'#403D3F');d=ImageDraw.Draw(b)
 for k,im in enumerate(fs):x=k%cols*112;y=k//cols*116;b.alpha_composite(Image.fromarray(im),(x+8,y));d.text((x+8,y+99),str(k+1),fill='white')
 b.resize((b.width*4,b.height*4),Image.Resampling.NEAREST).save(W/(n+'_4x.png'))
(W/'walk_records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));(W/'walk_timing.json').write_text(json.dumps(tim,indent=2));(W/'foot_reference.json').write_text(json.dumps(footref,indent=2));print('new-from-standing walk built; source part sizes', {n:int((p[:,:,3]>0).sum()) for n,p in parts.items()},'foot refs',footref)
