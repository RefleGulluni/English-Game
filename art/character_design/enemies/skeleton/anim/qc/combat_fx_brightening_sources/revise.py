from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,GifImagePlugin
import numpy as np,json,hashlib,subprocess,sys,copy
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');D=R/'art/character_design/enemies/skeleton/anim';W=Path('/tmp/english-fx-brighter-20261029');O=W/'staged';Q=O/'qc';Q.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file()};(W/'protected.json').write_text(json.dumps(protected,indent=2))
L=np.array([.299,.587,.114]);pal=set(map(tuple,json.loads((D/'qc/v2_sources/palette.json').read_text())))
ash=np.array([[138,102,58],[146,114,64],[166,124,66],[169,134,81],[181,150,101],[190,158,109]],np.uint8)
cloth=np.array([[181,150,101],[185,157,111],[186,158,113],[187,159,114],[188,159,115],[189,161,116],[190,162,116]],np.uint8)
def comps(m):
 todo=set(map(tuple,np.argwhere(m).tolist()));out=[]
 while todo:
  q=[todo.pop()];c=q.copy()
  while q:
   y,x=q.pop()
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     p=(y+dy,x+dx)
     if p in todo:todo.remove(p);q.append(p);c.append(p)
  out.append(sorted(c))
 return sorted(out,key=lambda c:min(x for y,x in c))
def map_colors(a,ramp,target):
 out=a.copy();fg=a[:,:,3]>0
 for c in np.unique(a[fg,:3],axis=0):
  wanted=target(float(c@L));idx=np.argmin(abs(ramp@L-wanted));out[(a[:,:,:3]==c).all(2)&fg,:3]=ramp[idx]
 return out
allframes={};records={};reports={}
for n,size in [('fx_bone_dust',(48,32)),('fx_shroud_threads',(32,32))]:
 old=np.array(Image.open(D/(n+'.png')).convert('RGBA'));fw,fh=size;oldfs=[old[:,k*fw:(k+1)*fw].copy() for k in range(6)];newfs=[];edits=[]
 for k,a in enumerate(oldfs):
  if n=='fx_bone_dust':
   b=map_colors(a,ash,lambda l:138.42+.60*(l-76))
   for c in comps(a[:,:,3]>0):
    if len(c)>=4:
     # One darker existing bone pixel at the lower edge of a substantial cluster.
     y,x=max(c,key=lambda p:(p[0],-p[1]));b[y,x,:3]=ash[0]
   assert np.array_equal(b[:,:,3],a[:,:,3])
  else:
   b=map_colors(a,cloth,lambda l:161.24+.055*(l-110))
   for c in comps(a[:,:,3]>0):
    # Preserve the complete old strand; lengthen its upper endpoint by two pixels.
    sc=set(c);ends=[p for p in c if sum(max(abs(p[0]-q[0]),abs(p[1]-q[1]))==1 for q in c)==1];assert len(ends)==2
    endpoint=min(ends);oldend=endpoint;added=[]
    for step in range(2):
     near=[q for q in sc if max(abs(q[0]-endpoint[0]),abs(q[1]-endpoint[1]))==1];assert len(near)==1
     dy=endpoint[0]-near[0][0];dx=endpoint[1]-near[0][1];candidates=[]
     for sy in [-1,0,1]:
      for sx in [-1,0,1]:
       if not(sy or sx):continue
       y=endpoint[0]+sy;x=endpoint[1]+sx
       if not(0<=y<fh and 0<=x<fw) or b[y,x,3]:continue
       nearby=[(yy,xx) for yy in range(max(0,y-1),min(fh,y+2)) for xx in range(max(0,x-1),min(fw,x+2)) if b[yy,xx,3]]
       if nearby!=[endpoint]:continue
       candidates.append(((sy-dy)**2+(sx-dx)**2+.1*sy,(y,x)))
     assert candidates,(k,c)
     pt=min(candidates)[1];b[pt]=b[endpoint];sc.add(pt);added.append(pt);endpoint=pt
    edits.append({'frame':k+1,'old_points_yx':c,'added_yx':added,'length_before':len(c),'length_after':len(sc)})
   assert (a[:,:,3]<=b[:,:,3]).all()
  newfs.append(b)
 strip=np.concatenate(newfs,axis=1);Image.fromarray(strip).save(O/(n+'.png'));fdir=O/'frames'/n;fdir.mkdir(parents=True,exist_ok=True)
 for k,b in enumerate(newfs):Image.fromarray(b).save(fdir/f'{k+1:02}.png')
 metadata=json.loads((D/'qc'/f'{n}_metrics.json').read_text());t=metadata['timing'];rows=[]
 for k,b in enumerate(newfs):
  fg=b[:,:,3]>0;v=b[fg,:3]@L;colors=set(map(tuple,b[fg,:3]));assert colors<=pal and set(np.unique(b[:,:,3]))<={0,255};assert not b[~fg].any()
  bb=Image.fromarray(b).getbbox();cs=comps(fg);r=copy.deepcopy(metadata['frames'][k]);r.update(bbox=bb,visible_size=[bb[2]-bb[0],bb[3]-bb[1]] if bb else [0,0],opaque_pixels=int(fg.sum()),colors=len(colors),mean_luma=float(v.mean()) if len(v) else None,min_luma=float(v.min()) if len(v) else None,median_luma=float(np.median(v)) if len(v) else None,max_luma=float(v.max()) if len(v) else None,component_pixel_counts=[len(c) for c in cs],rgba_sha256=hashlib.sha256(b.tobytes()).hexdigest(),png_sha256=sha(fdir/f'{k+1:02}.png'))
  if len(v):
   if n=='fx_bone_dust':assert v.min()>=100 and v.max()<=170 and 130<=np.median(v)<=150
   else:assert np.median(v)>=140 and all(6<=len(c)<=12 for c in cs)
  if n=='fx_shroud_threads':
   assert not(fg[:-1,:-1]&fg[1:,:-1]&fg[:-1,1:]&fg[1:,1:]).any()
   assert len(cs)==[4,4,4,3,2,0][k]
  rows.append(r)
 assert not newfs[-1].any()
 # Exact GIF frames and unmodified timing; retain genuinely empty last frame.
 cs=sorted(set(tuple(c) for b in newfs for c in b[b[:,:,3]>0,:3]));flat=[0,0,0]+[v for c in cs for v in c];flat+=[0]*(768-len(flat));pp=[]
 for b in newfs:
  ix=np.zeros(b.shape[:2],np.uint8)
  for i,c in enumerate(cs):ix[(b[:,:,:3]==c).all(2)&(b[:,:,3]>0)]=i+1
  im=Image.fromarray(ix).convert('P');im.putpalette(flat);pp.append(im.resize((fw*8,fh*8),Image.Resampling.NEAREST))
 header,_=GifImagePlugin.getheader(pp[0],info={'transparency':0,'background':0})
 with (Q/f'{n}_8x.gif').open('wb') as f:
  for block in header:f.write(block)
  for k,im in enumerate(pp):
   for block in GifImagePlugin.getdata(im,duration=t['durations_ms'][k],disposal=2,transparency=0):f.write(block)
  f.write(b';')
 g=Image.open(Q/f'{n}_8x.gif');assert g.n_frames==6
 for k,b in enumerate(newfs):
  g.seek(k);actual=np.array(g.convert('RGBA'));expected=np.repeat(np.repeat(b,8,0),8,1);fg=expected[:,:,3]>0;assert np.array_equal(actual[:,:,3],expected[:,:,3]) and np.array_equal(actual[fg],expected[fg]);assert g.info['duration']==t['durations_ms'][k]
 board=Image.new('RGBA',((fw+4)*6,fh+13),'#403d43');draw=ImageDraw.Draw(board)
 for k,b in enumerate(newfs):board.alpha_composite(Image.fromarray(b),(k*(fw+4),0));draw.text((k*(fw+4)+1,fh+3),str(k+1),fill='white')
 board.resize((board.width*8,board.height*8),Image.Resampling.NEAREST).save(Q/f'{n}_contact_8x.png')
 metadata.update(frames=rows,strip_png_sha256=sha(O/(n+'.png')),revision='2026-10-29 brightening: colors only; threads extended by two endpoint pixels',brightness_formula='0.299R+0.587G+0.114B',shape_preserved_except_thread_endpoint_extension=True)
 (Q/f'{n}_metrics.json').write_text(json.dumps(metadata,indent=2)+'\n')
 run=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(O/(n+'.png')),*map(str,sorted(fdir.glob('*.png')))],capture_output=True,text=True,cwd=R,check=True);(Q/f'{n}_pixel_check.txt').write_text(run.stdout)
 vv=strip[strip[:,:,3]>0,:3]@L;reports[n]={'min':float(vv.min()),'median':float(np.median(vv)),'max':float(vv.max()),'mean':float(vv.mean()),'frames':rows,'whole_strip_colors':len(cs)};allframes[n]={'old':oldfs,'new':newfs};records[n]=edits
# Capture is a 6x native-pixel presentation: halve its first 800x760 panel to match the requested 3x sprite view.
screen=Image.open(R/'docs/reference/reality_fx_ingame_v1.png').convert('RGBA');base=screen.crop((0,0,800,760)).resize((400,380),Image.Resampling.NEAREST)
placements=[('fx_bone_dust',2,(172,174)),('fx_shroud_threads',2,(188,115))]
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',15);compare=Image.new('RGBA',(800,410),'#141519')
for j,version in enumerate(['old','new']):
 panel=base.copy()
 for n,k,xy in placements:panel.alpha_composite(Image.fromarray(allframes[n][version][k]).resize((allframes[n][version][k].shape[1]*3,allframes[n][version][k].shape[0]*3),Image.Resampling.NEAREST),xy)
 compare.alpha_composite(panel,(j*400,30));ImageDraw.Draw(compare).text((j*400+8,7),'原版骨灰 / 布丝' if j==0 else '改亮 + 布丝加长 · 3 倍',font=font,fill='#e3dbc9')
compare.save(Q/'combat_fx_visibility_ingame_3x.png')
(Q/'combat_fx_brightening_placements.json').write_text(json.dumps({'screenshot':'docs/reference/reality_fx_ingame_v1.png','capture_crop':[0,0,800,760],'capture_presentation_size':[400,380],'sprite_scale':3,'nearest_only':True,'placements':[{'asset':n,'frame':k+1,'xy':xy} for n,k,xy in placements],'notes':'Capture shows ~6 capture pixels/native pixel. Its first panel is presented at half size so effects and skeleton both use 3x native size. Positions are in the 400x380 panel, before header.'},indent=2))
(W/'results.json').write_text(json.dumps(reports,indent=2));(Q/'combat_fx_brightening_edits.json').write_text(json.dumps(records,indent=2));print(json.dumps({n:{key:r[key] for key in ['min','median','max','whole_strip_colors']} for n,r in reports.items()},indent=2))
