from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,copy
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-other3-20261027');O=W/'staged';Q=O/'qc';V=Q/'other3_sources';plans=json.loads((V/'parts_plan_before_drawing.json').read_text());refs=json.loads((V/'foot_references.json').read_text());palette=np.array(json.loads((A/'qc/v2_sources/palette.json').read_text()),np.uint8)
ALL={};records={};timings={};layers={}
def load(p):return np.array(Image.open(p).convert('RGBA'))
def put(dst,src,dx=0,dy=0):
 ys,xs=np.where(src[:,:,3]>0);xx=xs+dx;yy=ys+dy;keep=(xx>=0)&(xx<96)&(yy>=0)&(yy<96);dst[yy[keep],xx[keep]]=src[ys[keep],xs[keep]]
def render(direction,r):
 m=load(Path(plans[direction]['source']));parts={p.stem:load(p) for p in (V/'standing_parts'/direction).glob('*.png')}
 if r.get('exact_standard'):return m.copy(),parts.copy()
 pd=r['pelvis_offset'];ud=r['upper_offset'];out=np.zeros_like(m);ls={}
 for role in ['left','right']:
  p=parts['leg_'+role];leg=r['legs'][role];lift=leg['lift'];ax=leg['foot_dx'];ay=95-lift-refs[direction][role]['bottom'];dst=np.zeros_like(m)
  isleftscreen=(role=='right') if direction=='front' else (role=='left');ksign=-1 if isleftscreen else 1
  srcrows=list(range(48,84));destrows=[sy+round(np.interp(sy,[48,65,84],[0,-lift*.45,ay])) for sy in srcrows]
  for yy in range(min(destrows),max(destrows)+1):
   sy=srcrows[int(np.argmin(np.abs(np.array(destrows)-yy)))];knee=round(ksign*leg['knee_outward']*max(0,1-abs(sy-65)/17))
   dx=round(np.interp(sy,[48,65,84],[pd[0],pd[0]+knee,ax]))
   for sx in np.where(p[sy,:,3]>0)[0]:
    dd=dx
    # Free shroud edge has a delayed hem; ankle-wrapped cloth follows this same anatomical leg.
    color=p[sy,sx,:3].astype(int);pi=int(np.argmin(((palette.astype(int)-color)**2).sum(1)))
    cloth=pi in [*range(26,34),36]
    if cloth and 57<=sy<80:
     prev=plans[direction]['frames'][r.get('cloth_phase_index',0)]['legs'][role]
     lag=prev['foot_dx']-leg['foot_dx'] if direction=='left' else prev['lift']-lift
     # Keep all fabric roots and wrapped shin fixed; only extreme loose edges trail one beat.
     rowxs=np.where(p[sy,:,3]>0)[0];edge=sx in (rowxs.min(),rowxs.max())
     if edge:dd+=round(np.clip(lag*.25,-1,1)*np.sin((sy-57)/23*np.pi)*r.get('motion_blend',1))
    xx=sx+dd
    if 0<=xx<96:dst[yy,xx]=p[sy,sx]
  for sy,sx in zip(*np.where(p[84:,:,3]>0)):
   sy+=84;xx=sx+ax;yy=sy+ay
   if 0<=xx<96 and 0<=yy<96:dst[yy,xx]=p[sy,sx]
  ls['leg_'+role]=dst
 order=['right','left'] if direction=='left' else (['right','left'] if r['foreground_leg']=='left' else ['left','right'])
 for role in order:put(out,ls['leg_'+role])
 pp=np.zeros_like(m);put(pp,parts['pelvis'],*pd);ls['pelvis_rigid']=pp;put(out,pp)
 # One native waist-tying row bridges vertical roots of upper and pelvis. No lower/upper cut line.
 bridge=np.zeros_like(m)
 for y in range(40+ud[1],40+pd[1]):
  for x in np.where(parts['pelvis'][40,:,3]>0)[0]:
   xx=x+pd[0]
   if 0<=xx<96:bridge[y,xx]=parts['pelvis'][40,x]
 put(out,bridge);ls['waist_bridge']=bridge
 upper=np.zeros_like(m);put(upper,parts['upper'],*ud);ls['upper_rigid']=upper;put(out,upper)
 # Complete native bone chains, no independent pasted hand or lower-arm fragments.
 for role in ['right','left']:
  p=parts['arm_'+role];ar=np.zeros_like(m);ys,xs=np.where(p[:,:,3]>0)
  if len(ys)==0:continue
  top=int(ys.min());bottom=int(ys.max());swing=r['arm_swing']*(1 if role=='left' else -1)
  for sy,sx in zip(ys,xs):
   t=np.clip((sy-top)/max(1,bottom-top),0,1);dx=round(swing*t);dy=round(ud[1]*(1-t*.45));xx=sx+ud[0]+dx;yy=sy+dy
   if 0<=xx<96 and 0<=yy<96:ar[yy,xx]=p[sy,sx]
  # Native nearest bone row closes integer-projection hinge discontinuities only.
  for yy in range(top+ud[1]+1,bottom):
   if not ar[yy,:,3].any() and ar[yy-1,:,3].any() and ar[yy+1,:,3].any():ar[yy]=ar[yy-1]
  ls['arm_'+role]=ar;put(out,ar)
 return out,ls

def save(name,direction,kind,rs):
 fs=[];rec=[];d=O/'frames'/name;d.mkdir(parents=True,exist_ok=True);ld=V/'layers'/name;ld.mkdir(parents=True,exist_ok=True)
 for k,r in enumerate(rs):
  im,ls=render(direction,r);fs.append(im);rec.append(r);Image.fromarray(im).save(d/f'{k+1:02}.png');dd=ld/f'{k+1:02}';dd.mkdir(exist_ok=True)
  for ln,p in ls.items():Image.fromarray(p).save(dd/(ln+'.png'))
 ALL[name]=fs;records[name]=rec
 sheet=Image.new('RGBA',(96*len(fs),96))
 for k,im in enumerate(fs):sheet.paste(Image.fromarray(im),(96*k,0))
 sheet.save(O/(name+'.png'));timings[name]={'frames':len(fs),'durations_ms':[100]*len(fs),'loop':kind=='walk','sprite_sheet':name+'.png'}
 if kind!='walk':timings[name]['hold_last_frame']=True
 elif direction=='left':timings[name].update({'movement_px_per_second':50,'support_foot_canvas_step_px':5,'world_direction':[-1,0]})
 else:timings[name].update({'walk_mode':'in_place','vertical_support_lock':False,'foot_lift_max_px':6,'knee_outward_max_px':2})

def blend(direction,target,t,starting):
 r=copy.deepcopy(target);r['motion_blend']=t
 r['pelvis_offset']=[round(v*t) for v in target['pelvis_offset']]
 # Pelvis initiates, upper follows without independently moving head or neck.
 r['upper_offset']=[round(v*t) for v in target['upper_offset']];r['head_offset']=r['upper_offset'].copy();r['neck_offset']=r['upper_offset'].copy();r['arm_swing']=round(target['arm_swing']*t)
 for role,l in r['legs'].items():
  ref=refs[direction][role];standinglift=95-ref['bottom'];l['lift']=round(standinglift*(1-t)+l['lift']*t);l['foot_dx']=round(l['foot_dx']*t);l['knee_outward']=round(l['knee_outward']*t);l['support']=l['lift']==0
 if all(l['lift']>0 for l in r['legs'].values()):
  planted=min(r['legs'],key=lambda role:(r['legs'][role]['lift'],role!='right'));r['legs'][planted]['lift']=0;r['legs'][planted]['support']=True
 return r
for direction,pl in plans.items():
 rs=pl['frames'];save(f'skeleton_B_walk_{direction}_v5',direction,'walk',rs)
 start=[{'exact_standard':True},blend(direction,rs[0],.35,True),blend(direction,rs[0],.7,True)];start[1]['pelvis_offset'][1]=1
 stop=[blend(direction,rs[-1],.7,False),blend(direction,rs[-1],.35,False),{'exact_standard':True}]
 save(f'skeleton_B_walk_start_{direction}',direction,'start',start);save(f'skeleton_B_walk_stop_{direction}',direction,'stop',stop)
# Export exact palette nearest previews. Transparency uses its own index; no alpha blending.
flat=[0,0,0]+palette.flatten().tolist();flat+= [0]*(768-len(flat))
def gif(p,fs,loop=True):
 ims=[]
 for a in fs:
  ix=np.zeros((96,96),np.uint8)
  for k,c in enumerate(palette):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=k+1
  assert np.array_equal(ix>0,a[:,:,3]>0)
  im=Image.fromarray(ix).convert('P');im.putpalette(flat);ims.append(im.resize((768,768),Image.Resampling.NEAREST))
 kw={'save_all':True,'append_images':ims[1:],'duration':[100]*len(ims),'transparency':0,'disposal':2,'optimize':False}
 if loop:kw['loop']=0
 ims[0].save(p,**kw)
for name,fs in ALL.items():
 gif(Q/(name+'_8x.gif'),fs,timings[name]['loop']);cols=4;rows=(len(fs)+3)//4;b=Image.new('RGBA',(cols*104,rows*112),'#403D43');d=ImageDraw.Draw(b)
 for k,a in enumerate(fs):x=k%4*104+4;y=k//4*112;b.alpha_composite(Image.fromarray(a),(x,y));d.text((x,y+98),str(k+1),fill='white')
 b.resize((b.width*4,b.height*4),Image.Resampling.NEAREST).save(Q/(name+'_frames_4x.png'))
for direction in plans:
 sn=f'skeleton_B_walk_start_{direction}';wn=f'skeleton_B_walk_{direction}_v5';en=f'skeleton_B_walk_stop_{direction}';gif(Q/(f'skeleton_B_{direction}_start_walk_stop_8x.gif'),ALL[sn]+ALL[wn]*2+ALL[en],False)
(V/'frame_records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));(V/'timing_entries.json').write_text(json.dumps(timings,indent=2));print('Built',len(ALL),'actions;',sum(map(len,ALL.values())),'frames')
