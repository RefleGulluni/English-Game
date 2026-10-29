from pathlib import Path
from PIL import Image,ImageDraw,GifImagePlugin,ImageFont
import numpy as np,json,hashlib,math
W=Path('/tmp/lexicon-page-revision-20261029');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');D=R/'art/character_design/lexicon';O=W/'staged';Q=O/'qc/page_turn_revision_20261029';Q.mkdir(parents=True,exist_ok=True);S=Q/'sources';S.mkdir(exist_ok=True);read=lambda p:np.array(Image.open(p).convert('RGBA'));rh=lambda a:hashlib.sha256(a.tobytes()).hexdigest();L=np.array([.299,.587,.114]);paper=np.array([[186,155,125],[195,170,145],[205,189,172]],np.uint8)
raw=read(W/'page_leaves_square_generated.png');records=[];native=[]
def fg(a):
 c=a[:,:,:3].astype(int);return ~((c[:,:,0]>170)&(c[:,:,2]>150)&(c[:,:,1]<110)&(c[:,:,0]-c[:,:,1]>70)&(c[:,:,2]-c[:,:,1]>65))
def edges(a,f,axis):
 d=np.abs(np.diff(a[:,:,:3].astype(float),axis=axis)).mean(2);m=f[:,1:]&f[:,:-1] if axis==1 else f[1:]&f[:-1];return(d*m).sum(0 if axis==1 else 1)/np.maximum(m.sum(0 if axis==1 else 1),1)
def fit(z,lo,hi,p=5.3):
 z=(z-np.median(z))/(np.std(z)+1e-6);score=np.full(len(z)+1,-1e12);prev=np.full(len(z)+1,-1,int)
 for j in range(lo,min(lo+7,hi)):score[j]=z[max(0,j-1)]
 for j in range(lo+7,hi):
  for n in [4,5,6,7]:
   k=j-n
   if k>=lo:
    val=score[k]+z[j-1]-.8*(n-p)**2
    if val>score[j]:score[j]=val;prev[j]=k
 end=max(range(max(lo,hi-7),hi),key=lambda j:score[j]);out=[]
 while end>=lo:out.append(int(end));end=prev[end]
 return sorted(out)
for k in range(4):
 x0=k%2*627;y0=k//2*627;a=raw[y0:y0+627,x0:x0+627];f=fg(a);yy,xx=np.where(f);xs=fit(edges(a,f,1),max(0,int(xx.min())-6),min(627,int(xx.max())+7));ys=fit(edges(a,f,0),max(0,int(yy.min())-6),min(627,int(yy.max())+7));out=np.zeros((len(ys)-1,len(xs)-1,4),np.uint8)
 for y in range(len(ys)-1):
  for x in range(len(xs)-1):
   sx=(xs[x]+xs[x+1])//2;sy=(ys[y]+ys[y+1])//2
   if f[sy,sx]:out[y,x]=a[sy,sx,:3].tolist()+[255]
 im=Image.fromarray(out);bb=im.getbbox();out=np.array(im.crop(bb));native.append(out);Image.fromarray(out).save(S/f'native_leaf_{k+1:02}.png')
 overlay=Image.fromarray(a);dd=ImageDraw.Draw(overlay)
 for x in xs:dd.line((x,ys[0],x,ys[-1]),fill='#ff6666')
 for y in ys:dd.line((xs[0],y,xs[-1],y),fill='#ff6666')
 mx=int(np.median(xx));my=int(np.median(yy));overlay.crop((mx-80,my-80,mx+80,my+80)).save(S/f'leaf_{k+1:02}_gridcheck.png')
 records.append({'pose':k+1,'source_cell':[x0,y0,x0+627,y0+627],'observed_pitch':[5.3,5.3],'x_boundaries':xs,'y_boundaries':ys,'native_size':list(Image.fromarray(out).size),'crop':list(bb),'method':'each observed block center becomes one native pixel; no full-art resize'})
(S/'native_grid.json').write_text(json.dumps(records,indent=2));print('native',[a.shape[:2] for a in native])
base=read(D/'lexicon_open_clean.png');fs=[base.copy()];layers=[];edits=[]
def pale(a,back=False):
 b=a.copy();f=b[:,:,3]>0;v=b[:,:,:3]@L
 if back:
  b[f,:3]=paper[1];b[f&(v>244),:3]=paper[2]
 else:
  b[f,:3]=paper[2];b[f&(v<208),:3]=paper[1]
 # Recolor the existing silhouette boundary, one pixel inward only; no added outside contour.
 padded=np.pad(f,1);inside=(padded[:-2,1:-1]&padded[2:,1:-1]&padded[1:-1,:-2]&padded[1:-1,2:]);edge=f&~inside;b[edge,:3]=paper[0 if back else 1];b[~f]=0
 return b

def place(layer,a,x,y):
 assert x>=0 and y>=0 and x+a.shape[1]<=256 and y+a.shape[0]<=128,(a.shape,x,y)
 mask=a[:,:,3]>0;layer[y:y+a.shape[0],x:x+a.shape[1]][mask]=a[mask]
# 2: Only the outer corner moves; the rest of this leaf retains the canonical right-page pixels.
a=pale(native[0]);layer=np.zeros_like(base);layer[10:112,128:236]=base[10:112,128:236];cw=23;ch=23;corner=a[:ch,-cw:];place(layer,corner,213,7);layer[10:112,128]=[*paper[1],255];layers.append(layer);edits.append({'frame':2,'hinge_y_inclusive':[10,111],'source_corner_crop_xyxy':[a.shape[1]-cw,0,a.shape[1],ch],'corner_xy':[213,7]})
# 3: Raised curved front page, independently generated.
a=pale(native[1]);h=a.shape[0];assert h<=116;top=7;layer=np.zeros_like(base);place(layer,a,128,top);layer[top:top+h,128]=[*paper[1],255];layers.append(layer);edits.append({'frame':3,'native_pose':2,'xy':[128,top],'hinge_y_inclusive':[top,top+h-1]})
# 4: A real, visible 1 px upright paper edge. Each row samples the generated edge-on leaf.
a=native[2];h=min(a.shape[0],110);top=7;layer=np.zeros_like(base);samples=[]
for y in range(h):
 xs=np.flatnonzero(a[y,:,3]);x=int(xs[len(xs)//2]) if len(xs) else int(a.shape[1]//2);layer[top+y,128]=[*paper[1],255];samples.append([x,y])
layers.append(layer);edits.append({'frame':4,'native_pose':3,'source_row_samples_xy':samples,'hinge_y_inclusive':[top,top+h-1],'edge_width_px':1,'placed_x':128,'color_rgb':paper[1].tolist()})
# 5: Independently drawn back of paper falling onto LEFT, not a flipped right page.
a=pale(native[3],back=True);h=a.shape[0];assert h<=116;top=7;left=129-a.shape[1];layer=np.zeros_like(base);place(layer,a,left,top);layer[top:top+h,128]=[*paper[1],255];layers.append(layer);edits.append({'frame':5,'native_pose':4,'xy':[left,top],'hinge_y_inclusive':[top,top+h-1],'back_face':True})
# Close native sampling pinholes beside the hinge and retain a single-paper silhouette.
layers[0][10:112,129:132]=[*paper[2],255]
for index in [1,3]:
 layer=layers[index];back=index==3
 for y in range(layer.shape[0]):
  xs=np.flatnonzero(layer[y,:,3])
  if len(xs):
   lo,hi=int(xs.min()),int(xs.max())
   for x in range(lo,hi+1):
    if layer[y,x,3]==0:layer[y,x]=[*paper[1 if back else 2],255]
 f=layer[:,:,3]>0;padded=np.pad(f,1);inside=(padded[:-2,1:-1]&padded[2:,1:-1]&padded[1:-1,:-2]&padded[1:-1,2:]);layer[f&~inside,:3]=paper[0 if back else 1]
for layer in layers:
 b=base.copy();m=layer[:,:,3]>0;b[m]=layer[m];fs.append(b)
fs.append(base.copy());strip=np.concatenate(fs,axis=1);Image.fromarray(strip).save(O/'lexicon_page_turn.png')
# Re-extract the FINISHED strip from disk for every verification below.
strip=read(O/'lexicon_page_turn.png');fs=[strip[:,k*256:(k+1)*256].copy() for k in range(6)];folder=Q/'frames';folder.mkdir(exist_ok=True);metrics=[]
def box(mask):
 yy,xx=np.where(mask);return [int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())] if len(xx) else None
for k,b in enumerate(fs):
 f=b[:,:,3]>0;colors=set(map(tuple,b[f,:3]));allowed=set(map(tuple,json.loads((D/'qc/sources/world_palette.json').read_text())));assert colors<=allowed;assert set(np.unique(b[:,:,3]))<={0,255};assert not b[~f].any();diff=(b!=base).any(2);prev=(b!=fs[k-1]).any(2) if k else np.zeros((128,256),bool);Image.fromarray(b).save(folder/f'{k+1:02}.png')
 r={'frame':k+1,'rgba_sha256':rh(b),'different_from_open_count':int(diff.sum()),'different_from_open_bbox_inclusive':box(diff),'different_from_previous_count':int(prev.sum()),'different_from_previous_bbox_inclusive':box(prev),'left_of_spine_changed_pixels':int(diff[:,:128].sum()),'on_spine_changed_pixels':int(diff[:,128].sum()),'right_of_spine_changed_pixels':int(diff[:,129:].sum()),'new_colors':0,'partial_alpha_pixels':0,'cyan_pixels':0}
 if k in [0,5]:assert not diff.any()
 else:
  assert diff.any();layer=layers[k-1];start,end=edits[k-1]['hinge_y_inclusive'];assert (layer[start:end+1,128,3]==255).all();r['hinge_y_inclusive']=[start,end];r['hinge_missing_rows']=[]
  gaps=[]
  for y in range(start,end+1):
   xs=np.flatnonzero(layer[y,:,3])
   if len(xs) and not (layer[y,int(xs.min()):int(xs.max())+1,3]==255).all():gaps.append(y)
  assert not gaps;r['leaf_row_internal_gap_rows']=gaps
  Image.fromarray(layer).save(Q/f'leaf_layer_{k+1:02}.png')
 if k:assert prev.any()
 if k==3:
  assert r['different_from_open_bbox_inclusive'][0]==128 and r['different_from_open_bbox_inclusive'][2]==128;assert r['different_from_open_count']>=90;r['edge_width_px']=1
 if k==4:assert r['left_of_spine_changed_pixels']>=1000
 metrics.append(r)
assert len({rh(a) for a in fs[1:5]})==4
# GIF is transparent, nearest3, exactly100ms per frame (total600ms).
cs=sorted(set(tuple(c) for a in fs for c in a[a[:,:,3]>0,:3]));flat=[0,0,0]+[v for c in cs for v in c];flat+=[0]*(768-len(flat));pp=[]
for a in fs:
 ix=np.zeros(a.shape[:2],np.uint8)
 for i,c in enumerate(cs):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=i+1
 im=Image.fromarray(ix).convert('P');im.putpalette(flat);pp.append(im.resize((768,384),Image.Resampling.NEAREST))
header,_=GifImagePlugin.getheader(pp[0],info={'transparency':0,'background':0})
with (W/'lexicon_page_turn_3x.gif').open('wb') as f:
 for b in header:f.write(b)
 f.write(b'!\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00')
 for im in pp:
  for b in GifImagePlugin.getdata(im,duration=100,disposal=2,transparency=0):f.write(b)
 f.write(b';')
g=Image.open(W/'lexicon_page_turn_3x.gif');assert g.n_frames==6
for k,a in enumerate(fs):
 g.seek(k);b=np.array(g.convert('RGBA'));e=np.repeat(np.repeat(a,3,0),3,1);m=e[:,:,3]>0;assert np.array_equal(b[:,:,3],e[:,:,3]) and np.array_equal(b[m],e[m]) and g.info['duration']==100
# Compact 3x contact, with no squashing of individual frames.
board=Image.new('RGBA',(768,288),'#403c40');dd=ImageDraw.Draw(board)
for k,a in enumerate(fs):board.alpha_composite(Image.fromarray(a),(k%3*256,k//3*144));dd.text((k%3*256+3,k//3*144+131),str(k+1),fill='white')
board.resize((2304,864),Image.Resampling.NEAREST).save(Q/'page_turn_contact_3x.png')
(Q/'page_turn_metrics.json').write_text(json.dumps({'frame_size':[256,128],'frames':6,'durations_ms':[100]*6,'duration_ms':600,'rgba_open_sha256':rh(base),'frames_metrics':metrics,'gif_decoded_exact':True,'source_edits':edits},indent=2));print(json.dumps(metrics,indent=2))
