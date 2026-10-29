from pathlib import Path
from PIL import Image,ImageDraw,GifImagePlugin
import numpy as np,json,hashlib,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');D=R/'art/character_design/lexicon';W=Path('/Users/mac/.codex/work/lexicon-paper-7_1');O=W/'staged';O.mkdir(exist_ok=True);Q=O/'qc';Q.mkdir(exist_ok=True)
read=lambda p:np.array(Image.open(p).convert('RGBA')); lum=lambda a:a[...,:3]@np.array([.299,.587,.114]); sha=lambda a:hashlib.sha256(a.tobytes()).hexdigest()
old=read(D/'lexicon_open_clean.png');base=old.copy();allowed=set(map(tuple,old[old[:,:,3]>0,:3]));pal=np.array(sorted(allowed),np.uint8)
# Local restoration only: retain original generated paper and leather pixels.
# Both page edges terminate on native row109. Right edge is lowered1 row.
base[103:110,136:236]=old[102:109,136:236]
# Correct the tapering left lower inner edge without erasing its stains.
for x in range(119,125):
 for y in range(106,110):
  if lum(base[y,x])<125:base[y,x]=old[108,118-(x-119)]
# Paper upper inner edges meet at the same level around the original dark binding.
for x in range(115,126):
 top=9+(x-115)//2
 for y in range(top,19):
  if lum(base[y,x])<125:base[y,x]=old[min(22,y+6),x-3]
for x in range(131,144):
 top=14-(x-131)//2
 for y in range(top,19):
  if lum(base[y,x])<125:base[y,x]=old[min(24,y+7),x+4]
# Preserve the folded-corner shapes, moving their existing paper-only pixels
# in front of the leather rim. No leather pixels are translated.
for x0,x1,y0,y1,dy in [(27,40,7,19,-3),(211,234,6,19,-3)]:
 patch=old[y0:y1,x0:x1].copy();m=(lum(patch)>125)&(patch[:,:,3]>0)
 # Keep the actual connected fold, excluding isolated leather highlights.
 seen=set();groups=[]
 for py,px in zip(*np.where(m)):
  if (py,px) in seen:continue
  todo=[(int(py),int(px))];seen.add((py,px));group=[]
  while todo:
   cy,cx=todo.pop();group.append((cy,cx))
   for ny,nx in [(cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)]:
    if 0<=ny<m.shape[0] and 0<=nx<m.shape[1] and m[ny,nx] and (ny,nx) not in seen:seen.add((ny,nx));todo.append((ny,nx))
  groups.append(group)
 m[:]=False
 for py,px in max(groups,key=len):m[py,px]=True
 for yy,xx in zip(*np.where(m)):
  base[y0+yy+dy,x0+xx]=patch[yy,xx]
# A tiny shadow under each existing folded lip, sampled from aged paper color.
for x,y in [(34,12),(35,13),(36,14),(37,15),(220,10),(221,11),(222,12),(223,13),(224,14)]:
 if lum(base[y,x])>150:base[y,x]=[168,134,102,255]
Image.fromarray(base).save(O/'lexicon_open_clean.png')
# Existing native poses are accepted. Reuse silhouettes, replace only their flat
# fills with the original book's paper texture; no new random marks or colors.
prev=D/'qc/page_turn_revision_20261029';layers=[read(prev/f'leaf_layer_{i:02}.png') for i in range(2,6)]
# Source rectangular paper samples retain stains and aged margins, not leather.
def papertex(side):
 x0,x1=(135,235) if side=='right' else (26,125)
 a=base[8:110,x0:x1].copy()
 for y,x in zip(*np.where(lum(a)<110)):
  # Replace leather occlusion with nearest existing same-page paper pixel.
  opts=[]
  for dy,dx in [(1,0),(2,0),(3,0),(4,0),(5,0),(0,1),(0,-1),(6,0),(-1,0),(-2,0),(-3,0)]:
   sy=min(a.shape[0]-1,max(0,y+dy));sx=min(a.shape[1]-1,max(0,x+dx))
   if lum(a[sy,sx])>=110:opts.append(a[sy,sx])
  a[y,x]=opts[0] if opts else [186,155,125,255]
 return a
right=papertex('right');left=papertex('left')
# One palette step darker for reverse side; preserve distinct stains.
paperpal=np.array([[145,106,70],[168,134,102],[186,155,125],[195,170,145],[205,189,172]],np.uint8)
def darker(c):
 v=lum(c);i=int(np.argmin(abs(lum(paperpal)-v)));return [*paperpal[max(0,i-1)],255]
# Frame2: retain gutter exactly, curl a larger outside corner using the actual
# original folded paper texture, with underlying shaded parchment showing.
layers[0][:]=0
# bent flap region grows inward from the existing upper outer corner;
# source pixels retain old paper grain, with a visible shadow beneath its lip.
for y in range(2,34):
 lo=220-(y-2) if y<11 else 212+max(0,y-15)//2;hi=min(234,221+(y-2)*2) if y<10 else 234-max(0,y-23)//3
 if lo>hi:continue
 for x in range(lo,hi+1):
  sy=min(109,10+(y-2));sx=min(234,max(135,x-3))
  c=base[sy,sx].copy()
  if lum(c)<110:c=np.array([186,155,125,255],np.uint8)
  layers[0][y,x]=c
 # crease on the inside edge, one pixel only, not a dark outline
 layers[0][y,lo]=[186,155,125,255]
 if y>=14 and hi<236:layers[0][y,hi+1]=[168,134,102,255]
# Hinge records are a conceptual attachment, not a bright overlay strip.
layers[0][14:110,128]=base[14:110,128]
# Native silhouettes for bent front and falling reverse; pixel projection of
# respective page grain. Map rows and per-row cross-section independently.
for i,tex,back in [(1,right,False),(3,left,True)]:
 mask=layers[i][:,:,3]>0;yy,xx=np.where(mask);top,bottom=int(yy.min()),int(yy.max())
 for y in range(top,bottom+1):
  xs=np.flatnonzero(mask[y]);lo,hi=int(xs[0]),int(xs[-1]);sy=round((y-top)/(bottom-top)*(tex.shape[0]-1))
  for x in xs:
   u=(x-lo)/max(1,hi-lo);sx=round(u*(tex.shape[1]-1));c=tex[sy,sx].copy()
   if back:c=np.array(darker(c),np.uint8)
   layers[i][y,x]=c
  # Thin aged top/bottom edges sampled from the actual paper's brown palette.
  if y in [top,bottom]:
   for x in xs:
    if lum(layers[i][y,x])>162:layers[i][y,x]=[186,155,125,255] if not back else [168,134,102,255]
  # Preserve irregular age marks within the border; onepx boundary is paper,
  # not black/leather. First/last native row keeps its source aged edge.
  for x in [lo,hi]:
   if lum(layers[i][y,x])>162:layers[i][y,x]=[186,155,125,255] if not back else [168,134,102,255]
# The accepted upright silhouette remains exactly1px atx128. Broken up paper
# tones read as an aged edge, without a new bright gutter in the flat pose.
for y in range(7,105):layers[2][y,128]=right[round((y-7)/97*101),0]
fs=[base.copy()]
for layer in layers:
 a=base.copy();m=layer[:,:,3]>0;a[m]=layer[m];fs.append(a)
fs.append(base.copy());Image.fromarray(np.concatenate(fs,axis=1)).save(O/'lexicon_page_turn.png')
# The approved closing/opening geometry is unchanged, except canonical last
# frame and matching paper-local repairs in near-flat penultimate frame.
fall=read(D/'lexicon_covers_fall.png');fall[:,-256:]=base
# Frame5 is narrower, not flat: preserve its geometry. Only restore the two
# exposed top corner lips over the rim by moving their own paperpixels up1px.
f5=fall[:,4*256:5*256].copy()
for x0,x1 in [(28,42),(214,229)]:
 for y in range(7,15):
  for x in range(x0,x1):
   if lum(f5[y,x])>125 and lum(f5[max(0,y-1),x])<110:fall[y-1,4*256+x]=f5[y,x]
Image.fromarray(fall).save(O/'lexicon_covers_fall.png')
# Exact indexed GIF, decoded and checked against delivered pixel frames.
def gif(frames,path):
 cs=sorted(set(tuple(c) for a in frames for c in a[a[:,:,3]>0,:3]));colors=[0,0,0]+[v for c in cs for v in c];colors += [0]*(768-len(colors));ims=[]
 for a in frames:
  ix=np.zeros(a.shape[:2],np.uint8)
  for i,c in enumerate(cs):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=i+1
  im=Image.fromarray(ix).convert('P');im.putpalette(colors);ims.append(im.resize((a.shape[1]*3,a.shape[0]*3),Image.Resampling.NEAREST))
 header,_=GifImagePlugin.getheader(ims[0],info={'transparency':0,'background':0})
 with path.open('wb') as f:
  for b in header:f.write(b)
  f.write(b'!\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00')
  for im in ims:
   for b in GifImagePlugin.getdata(im,duration=100,disposal=2,transparency=0):f.write(b)
  f.write(b';')
 g=Image.open(path);assert g.n_frames==len(frames)
 for k,a in enumerate(frames):
  g.seek(k);b=np.array(g.convert('RGBA'));e=np.repeat(np.repeat(a,3,0),3,1);m=e[:,:,3]>0;assert np.array_equal(b[:,:,3],e[:,:,3]) and np.array_equal(b[m],e[m]) and g.info['duration']==100

gif(fs,Q/'lexicon_page_turn_3x.gif');tip=read(D/'lexicon_tip_up.png');gif([tip[:,i*256:(i+1)*256] for i in range(3)]+[fall[:,i*256:(i+1)*256] for i in range(6)],Q/'lexicon_opening_3x.gif')
# Metrics from saved final files, not merely working layers.
def bbox(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None
def stats(a):
 c=np.array(a)[...,:3].reshape(-1,3);v=lum(c);return {'pixels':len(c),'mean_rgb':np.round(c.mean(0),3).tolist(),'mean_luma':round(float(v.mean()),3),'luma_std':round(float(v.std()),3),'colors':len(np.unique(c,axis=0))}
strip=read(O/'lexicon_page_turn.png');records=[];frames=Q/'frames';frames.mkdir(exist_ok=True)
for k in range(6):
 a=strip[:,256*k:256*(k+1)];Image.fromarray(a).save(frames/f'{k+1:02}.png');d=(a!=base).any(2)
 assert set(map(tuple,a[a[:,:,3]>0,:3]))<=allowed;assert set(np.unique(a[:,:,3]))<={0,255}
 r={'frame':k+1,'diff_pixels':int(d.sum()),'bbox_inclusive':bbox(d),'rgba_sha256':sha(a)}
 if k in [0,5]:assert np.array_equal(a,base)
 else:
  layer=layers[k-1];m=layer[:,:,3]>0;r['leaf_material']=stats(layer[m]);Image.fromarray(layer).save(Q/f'leaf_{k+1:02}.png')
  yy=np.flatnonzero(layer[:,128,3]);r['hinge_y_range']=[int(yy.min()),int(yy.max())];r['hinge_missing_rows']=[int(y) for y in range(yy.min(),yy.max()+1) if layer[y,128,3]!=255];assert not r['hinge_missing_rows']
 if k==3:assert bbox(d)[0]==bbox(d)[2]==128
 records.append(r)
assert np.array_equal(fall[:,-256:],base)
ref_right=base[8:110,135:235];ref_left=base[8:110,26:125]
metrics={'actual_right_page_reference':stats(ref_right[lum(ref_right)>=110]),'actual_left_page_reference':stats(ref_left[lum(ref_left)>=110]),'reference_region_method':'right x135..234 / left x26..124, y8..109 inclusive; exclude leather pixels with luma<110; include stains and aged paper margins','frames':records,'right_page_paper_reference':stats(right),'left_page_paper_reference':stats(left),'open_rgba_sha256':sha(base),'bottom_paper_row':109,'spine_x':128,'durations_ms':[100]*6,'new_colors':0,'partial_alpha':0,'fall_frame5_changed_pixels':int((fall[:,1024:1280]!=f5).any(2).sum()),'fall_first4_unchanged':True,'gif_decoded_exact':True}
(Q/'metrics.json').write_text(json.dumps(metrics,indent=2))
board=Image.new('RGBA',(768,288),'#403c40');dd=ImageDraw.Draw(board)
for k,a in enumerate(fs):board.alpha_composite(Image.fromarray(a),(k%3*256,k//3*144));dd.text((k%3*256+3,k//3*144+131),str(k+1),fill='white')
board.resize((2304,864),Image.Resampling.NEAREST).save(Q/'page_turn_contact_3x.png')
comp=Image.new('RGBA',(512,144),'#403c40');comp.alpha_composite(Image.fromarray(old),(0,0));comp.alpha_composite(Image.fromarray(base),(256,0));dd=ImageDraw.Draw(comp);dd.text((2,131),'BEFORE',fill='white');dd.text((258,131),'AFTER',fill='white');comp.resize((1536,432),Image.Resampling.NEAREST).save(Q/'open_before_after_3x.png')
print(json.dumps(metrics,indent=2))
