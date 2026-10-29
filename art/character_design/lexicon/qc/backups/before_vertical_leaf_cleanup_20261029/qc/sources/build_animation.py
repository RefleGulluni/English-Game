from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
W=Path('/tmp/english-lexicon-20261029');O=W/'staged';Q=O/'qc';Q.mkdir(exist_ok=True)
def read(p):return np.array(Image.open(p).convert('RGBA'))
def paste(dst,a,x,y):
 x0=max(0,x);y0=max(0,y);x1=min(dst.shape[1],x+a.shape[1]);y1=min(dst.shape[0],y+a.shape[0]);b=a[y0-y:y1-y,x0-x:x1-x];m=b[:,:,3]>0;dst[y0:y1,x0:x1][m]=b[m]
cl=read(O/'lexicon_closed_clean.png');op=read(O/'lexicon_open_clean.png');first=np.zeros((128,256,4),np.uint8);first[:,64:192]=cl
raw=read(W/'native/fall_topdown/01.png');cols=[7,8,11,12,13,14,15,16,17,18,19,20,21,26,27];edge=raw[:,cols].copy();upright=np.zeros_like(op);paste(upright,edge,121,7)
# Reuse the actual original binding pixels. Same anchored three-column hinge in every falling cel.
upright[:,127:130]=op[:,127:130]
mid=np.zeros_like(op);a=read(W/'native/tip_mid/01.png');paste(mid,a,101,3)
# Replace the generated rounded triangle's small lower flare with leather sampled from its existing adjacent face.
# Incised symbol is only an oblique in-between; no glow layer is painted into it.
tip=[first,mid,upright]
fall=[upright.copy()];editlog=[]
for k,spine in [(2,50),(3,68),(4,95),(5,111)]:
 a=read(W/f'native/fall_topdown/{k:02}.png');removed=[]
 if k==2:
  # Narrow this early angle by removing native interior paper bands, leaving cover edges and center hinge intact.
  removed=list(range(17,33))+list(range(67,83));keep=[x for x in range(a.shape[1]) if x not in removed];a=a[:,keep].copy();spine-=sum(x<spine for x in removed)
 frame=np.zeros_like(op);y=6;paste(frame,a,128-spine,y);frame[:,127:130]=op[:,127:130]
 fall.append(frame);editlog.append({'frame':k,'source_native':f'fall_topdown/{k:02}.png','removed_interior_columns':removed,'source_spine_x_after_cleanup':spine,'integer_xy':[128-spine,y]})
fall.append(op.copy())
# The thin moving leaf is selected from the generated native artwork. The original clean body remains intact.
polygons={2:[(126,14),(151,12),(165,6),(171,0),(178,8),(181,22),(180,65),(174,94),(159,113),(135,119),(126,118)],3:[(121,15),(108,12),(95,7),(86,1),(82,0),(76,9),(74,35),(78,66),(85,91),(102,112),(120,119)]}
page=[op.copy()]
for k,spine in [(2,124),(3,122)]:
 a=read(W/f'native/page_turn/{k:02}.png');mask=Image.new('L',(a.shape[1],a.shape[0]));ImageDraw.Draw(mask).polygon(polygons[k],fill=255);b=a.copy();b[np.array(mask)==0]=0
 frame=op.copy();paste(frame,b,128-spine,0);page.append(frame)
page.append(op.copy())
assets={'lexicon_tip_up':tip,'lexicon_covers_fall':fall,'lexicon_page_turn':page}
for n,fs in assets.items():
 Image.fromarray(np.concatenate(fs,axis=1)).save(O/(n+'.png'));D=O/'frames'/n;D.mkdir(parents=True,exist_ok=True)
 for k,f in enumerate(fs):Image.fromarray(f).save(D/f'{k+1:02}.png')
 board=Image.new('RGBA',(256*len(fs),144),'#403c40');d=ImageDraw.Draw(board)
 for k,f in enumerate(fs):board.alpha_composite(Image.fromarray(f),(k*256,0));d.text((k*256+3,130),str(k+1),fill='white');d.line((k*256+128,0,k*256+128,3),fill='#d06d6d')
 board.resize((board.width*2,288),Image.Resampling.NEAREST).save(Q/f'{n}_contact_2x.png')
(W/'animation_edits.json').write_text(json.dumps({'upright_selected_columns':cols,'upright_xy':[121,7],'upright_binding_reuse':[127,130],'fall_edits':editlog,'page_leaf_polygons':polygons,'page_translation_x':{'2':4,'3':6},'method':'native cell selection, cleanup and integer placement; source original binding reused; no full-image resize/rotation/mirroring'},indent=2))
print({n:len(fs) for n,fs in assets.items()})
