from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,GifImagePlugin
import numpy as np,json,hashlib,subprocess,sys,shutil,colorsys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-combat-fx-20261028');O=W/'staged';Q=O/'qc';Q.mkdir(exist_ok=True);pal=np.array(json.loads((R/'art/character_design/enemies/skeleton/anim/qc/v2_sources/palette.json').read_text()),int);allowed=set(map(tuple,pal));L=np.array([.299,.587,.114]);spec={
'fx_bone_chip_a':{'frame_size':[16,16],'anchor':[8,8],'frames':4,'durations_ms':[80]*4,'loop':True,'role':'knobby fingerbone terminal / short broken shaft'},
'fx_bone_chip_b':{'frame_size':[16,16],'anchor':[8,8],'frames':4,'durations_ms':[80]*4,'loop':True,'role':'thin curved rib wall fragment'},
'fx_bone_chip_c':{'frame_size':[16,16],'anchor':[8,8],'frames':4,'durations_ms':[80]*4,'loop':True,'role':'compact angular cancellous bone grit'},
'fx_bone_dust':{'frame_size':[48,32],'anchor':[24,31],'frames':6,'durations_ms':[60,70,90,110,100,90],'loop':False,'emission_point':[24,31],'role':'granular dark bone ash, not smoke','key_frame':{'type':'burst_peak','frame':3,'frame_index':2,'time_ms':130}},
'fx_shroud_threads':{'frame_size':[32,32],'anchor':[16,8],'frames':6,'durations_ms':[70,80,100,120,130,100],'loop':False,'role':'four torn shroud fibers falling and disappearing','key_frame':{'type':'tear','frame':1,'frame_index':0,'time_ms':0}}}
def load(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rh(a):return hashlib.sha256(a.tobytes()).hexdigest()
def components(mask):
 todo=set(zip(*np.where(mask)));cs=[]
 while todo:
  q=[todo.pop()];c=q.copy()
  while q:
   y,x=q.pop()
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     pt=(y+dy,x+dx)
     if pt in todo:todo.remove(pt);q.append(pt);c.append(pt)
  cs.append(c)
 return cs
results={};ALL={}
for n,t in spec.items():
 fs=[load(p) for p in sorted((O/'frames'/n).glob('*.png'))];ALL[n]=fs;assert len(fs)==t['frames'];fw,fh=t['frame_size'];metrics=[];strip=load(O/(n+'.png'));assert strip.shape==(fh,fw*len(fs),4)
 for k,a in enumerate(fs):
  assert a.shape==(fh,fw,4) and set(np.unique(a[:,:,3]))<={0,255};fg=a[:,:,3]>0;colors=set(map(tuple,a[fg,:3]));assert colors<=allowed;assert not a[~fg].any();assert np.array_equal(strip[:,k*fw:(k+1)*fw],a)
  for c in colors:
   h,s,v=colorsys.rgb_to_hsv(*(np.array(c)/255));assert not(160<=h*360<=260 and s>=.35 and v>.3)
  bb=Image.fromarray(a).getbbox();size=[bb[2]-bb[0],bb[3]-bb[1]] if bb else [0,0];mean=float((a[fg,:3]@L).mean()) if fg.any() else None;maximum=float((a[fg,:3]@L).max()) if fg.any() else None;cc=components(fg)
  item={'frame':k+1,'bbox':bb,'visible_size':size,'opaque_pixels':int(fg.sum()),'colors':len(colors),'alpha_values':np.unique(a[:,:,3]).tolist(),'cyan_pixels':0,'new_colors':0,'mean_luma':mean,'max_luma':maximum,'component_pixel_counts':[len(c) for c in cc],'rgba_sha256':rh(a),'png_sha256':sha(O/'frames'/n/f'{k+1:02}.png')}
  if n.startswith('fx_bone_chip'):
   assert 4<=max(size)<=8 and len(cc)==1;yy,xx=np.where(fg);center=[float(xx.mean()),float(yy.mean())];assert max(abs(center[0]-8),abs(center[1]-8))<=.5;item['centroid_xy']=center
  elif n=='fx_bone_dust':
   assert size[0]<=40 and size[1]<=24
   if maximum is not None:assert maximum<=120
   if k==0:assert a[31,24,3]==255
   if k==len(fs)-1:assert not fg.any()
  else:
   assert not(fg[:-1,:-1]&fg[1:,:-1]&fg[:-1,1:]&fg[1:,1:]).any();item['no_2x2_filled_blocks']=True
   if k<5:assert len(cc)==[4,4,4,3,2][k] and all(4<=len(c)<=10 for c in cc)
   else:assert not fg.any()
  metrics.append(item)
 if t['loop']:assert len(set(rh(a) for a in fs))==4
 # Exact indexed-palette GIF, including the empty final frame of both one-shots.
 colors=np.array(sorted(set(tuple(c) for a in fs for c in a[a[:,:,3]>0,:3])),np.uint8);assert len(colors)<255;flat=[0,0,0]+colors.flatten().tolist();flat += [0]*(768-len(flat));pp=[]
 for a in fs:
  ix=np.zeros(a.shape[:2],np.uint8)
  for j,c in enumerate(colors):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=j+1
  im=Image.fromarray(ix).convert('P');im.putpalette(flat);pp.append(im.resize((fw*8,fh*8),Image.Resampling.NEAREST))
 # Write full frames explicitly: this also preserves a genuinely empty final frame without a delta-bbox exporter bug.
 header,_=GifImagePlugin.getheader(pp[0],info={'transparency':0,'background':0})
 with (Q/(n+'_8x.gif')).open('wb') as handle:
  for block in header:handle.write(block)
  if t['loop']:handle.write(b'!\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00')
  for k,im in enumerate(pp):
   for block in GifImagePlugin.getdata(im,duration=t['durations_ms'][k],disposal=2,transparency=0):handle.write(block)
  handle.write(b';')
 g=Image.open(Q/(n+'_8x.gif'));assert g.n_frames==len(fs),(n,g.n_frames)
 for k,a in enumerate(fs):
  g.seek(k);b=np.array(g.convert('RGBA'));e=np.repeat(np.repeat(a,8,0),8,1);f=e[:,:,3]>0;assert np.array_equal(b[:,:,3],e[:,:,3]) and np.array_equal(b[f],e[f]) and g.info['duration']==t['durations_ms'][k]
 t.update(sprite_sheet=n+'.png',duration_ms=sum(t['durations_ms']),qa='qc/combat_fx_QA.md',frame_numbering='frame is1-based; frame_index is0-based',pixel_only_rotation_frames=True)
 results[n]={'timing':t,'frames':metrics,'gif_decoded_exact':True,'palette_existing_only':True,'no_cyan':True,'last_frame_fully_transparent':not bool(fs[-1][:,:,3].any()),'strip_png_sha256':sha(O/(n+'.png'))}
 board=Image.new('RGBA',((fw+4)*len(fs),fh+13),'#403d43');dr=ImageDraw.Draw(board)
 for k,a in enumerate(fs):board.alpha_composite(Image.fromarray(a),(k*(fw+4),0));dr.text((k*(fw+4)+1,fh+3),str(k+1),fill='white')
 board.resize((board.width*8,board.height*8),Image.Resampling.NEAREST).save(Q/(n+'_contact_8x.png'))
 run=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(O/(n+'.png')),*map(str,sorted((O/'frames'/n).glob('*.png')))],capture_output=True,text=True,cwd=R,check=True);(Q/(n+'_pixel_check.txt')).write_text(run.stdout)
 (Q/(n+'_metrics.json')).write_text(json.dumps(results[n],indent=2)+'\n')
# Real-size montage on the actual approved ground. No assets are fitted or enlarged inside the native scene.
ground=load(R/'art/cemetery_v3/ground/base/ground_base_01.png');scene=Image.fromarray(np.tile(ground,(2,2,1))[:160,:256]);sk=Image.open(R/'art/character_design/enemies/skeleton/skeleton_B.png').convert('RGBA');scene.alpha_composite(sk,(80,40))
placements=[('fx_bone_chip_a',1,(83,57)),('fx_bone_chip_b',3,(153,72)),('fx_bone_chip_c',0,(87,91)),('fx_bone_dust',2,(55,110)),('fx_shroud_threads',2,(147,74))]
for n,k,xy in placements:scene.alpha_composite(Image.fromarray(ALL[n][k]),xy)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',10);dr=ImageDraw.Draw(scene);dr.text((7,4),'骨片 / 骨灰 / 布丝：原生大小',font=font,fill='#d2cbbc');dr.text((6,146),'B 余裹者 96 px · 正式地面',font=font,fill='#d2cbbc');scene.save(Q/'combat_fx_with_skeleton_1x.png');scene.resize((768,480),Image.Resampling.NEAREST).save(Q/'combat_fx_with_skeleton_3x.png')
(Q/'combat_fx_montage_placements.json').write_text(json.dumps({'native_scene':[256,160],'scale':3,'ground':'art/cemetery_v3/ground/base/ground_base_01.png','skeleton':'art/character_design/enemies/skeleton/skeleton_B.png','skeleton_xy':[80,40],'placements':[{'asset':n,'frame':k+1,'xy':list(xy)} for n,k,xy in placements]},indent=2))
# A compact native comparison table for all four bone poses, useful beside the 3x context image.
b=Image.new('RGBA',(160,64),'#403d43');dr=ImageDraw.Draw(b)
for row,n in enumerate(['fx_bone_chip_a','fx_bone_chip_b','fx_bone_chip_c']):
 dr.text((2,row*20+4),n[-1].upper(),fill='white')
 for k,a in enumerate(ALL[n]):b.alpha_composite(Image.fromarray(a),(20+k*34,row*20))
b.resize((960,384),Image.Resampling.NEAREST).save(Q/'bone_chips_shapes_compare_6x.png')
(W/'timing_entries.json').write_text(json.dumps(spec,indent=2));(W/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps({n:{'frames':t['frames'],'canvas':t['frame_size'],'anchor':t['anchor'],'ms':t['duration_ms'],'opaque_counts':[r['opaque_pixels'] for r in results[n]['frames']],'max_luma':max(r['max_luma'] or 0 for r in results[n]['frames']),'last_clear':results[n]['last_frame_fully_transparent']} for n,t in spec.items()},indent=2))
