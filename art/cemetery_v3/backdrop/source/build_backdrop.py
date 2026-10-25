"""Assemble center-sampled generated silhouettes at native pixel scale.
Sky bands/cloud marks and same-color seam repair are explicitly authorized by brief.
All preview enlargement is integer nearest-neighbor; no asset resizing/mirroring.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
from collections import deque
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
S=ROOT/'source';Q=ROOT/'qc'
NEAR=Image.Resampling.NEAREST
META={}

def keyed(name,palette):
 im=Image.open(S/f'{name}_restored_cells.png').convert('RGB');a=np.array(im).astype(int)
 # Reject all magenta-contaminated edge colors instead of painting a fringe.
 keep=(a[:,:,0]<110)&(a[:,:,1]<125)&(a[:,:,2]<145)&(a.max(2)-a.min(2)<55)
 bright=a.mean(2)
 out=np.zeros((im.height,im.width,4),np.uint8)
 # Flat material levels, no dithering and no new texture.
 levels=np.digitize(bright,[58,74]) if name.startswith('skyline') else np.digitize(bright,[24,40])
 if name=='chapel':levels=np.digitize(bright,[57,72])
 for i,c in enumerate(palette):out[(levels==i)&keep]=list(c)+[255]
 # Remove only 1-2 pixel disconnected specks using 8-connectivity.
 seen=np.zeros(keep.shape,bool);removed=0
 for y in range(im.height):
  for x in range(im.width):
   if seen[y,x] or not keep[y,x]:continue
   stack=[(x,y)];seen[y,x]=1;comp=[]
   while stack:
    xx,yy=stack.pop();comp.append((xx,yy))
    for nx in range(max(0,xx-1),min(im.width,xx+2)):
     for ny in range(max(0,yy-1),min(im.height,yy+2)):
      if keep[ny,nx] and not seen[ny,nx]:seen[ny,nx]=1;stack.append((nx,ny))
   if len(comp)<=2:
    for xx,yy in comp:out[yy,xx]=0;removed+=1
 META[name]={'removed_isolated_pixels':removed,'native_size':[im.width,im.height]}
 return Image.fromarray(out)

# Sky: hand-placed horizontal solid-color bands; the brief explicitly allows this.
sky=Image.new('RGBA',(960,100),(139,145,152,255));dr=ImageDraw.Draw(sky)
for y,c in [(12,(137,143,151,255)),(25,(135,141,148,255)),(38,(132,138,146,255)),(52,(130,136,144,255))]:dr.rectangle((0,y,959,99),fill=c)
# Few fixed subdued stepped cloud streaks. No random noise, no gradual blur.
clouds=[([(19,8),(113,8),(113,9),(168,9),(168,10),(53,10),(53,9),(19,9)],(136,142,150,255)),
 ([(225,20),(380,20),(380,21),(423,21),(423,22),(268,22),(268,21),(225,21)],(132,138,146,255)),
 ([(548,10),(677,10),(677,11),(742,11),(742,12),(588,12),(588,11),(548,11)],(136,142,150,255)),
 ([(736,30),(915,30),(915,31),(947,31),(947,32),(799,32),(799,31),(736,31)],(130,136,144,255)),
 ([(48,34),(166,34),(166,35),(202,35),(202,36),(84,36),(84,35),(48,35)],(132,138,146,255)),
 ([(364,4),(473,4),(473,5),(532,5),(532,6),(408,6),(408,5),(364,5)],(137,143,151,255))]
for shape,c in clouds:dr.polygon(shape,fill=c)
sky.save(S/'sky_native.png')

# Collapse distant artwork to a quiet single-color contour; source inner gradients
# are deliberately removed, rather than interpreting them as surface texture.
HILL=(76,82,90,255)
segments=[]
for name in ['skyline_a','skyline_b','skyline_c','skyline_d']:
 full=keyed(name,[(64,70,78),(72,78,86),(82,88,96)])
 cropx=7 if name=='skyline_a' else 0;cropy=full.height-100
 patch=full.crop((cropx,cropy,cropx+240,cropy+100));a=np.array(patch)
 alpha=a[:,:,3]>0
 first=np.array([np.where(alpha[:,x])[0][0] if alpha[:,x].any() else 99 for x in range(240)])
 # Median ignores sparse thin trunks while preserving the source contour shape.
 shift=54-int(np.median(first))
 if name=='skyline_c':shift=4 # keep the tall distant treetops clear of the upper sky edge
 flat=Image.new('RGBA',(240,100));flatdata=np.zeros((100,240,4),np.uint8);flatdata[alpha]=HILL
 flat.alpha_composite(Image.fromarray(flatdata),(0,shift))
 flat.save(S/f'{name}_native_segment.png');segments.append(flat)
 META[name].update({'crop_xyxy':[cropx,cropy,cropx+240,cropy+100],'integer_vertical_offset':shift,'shared_silhouette_color':HILL})

assembled=Image.new('RGBA',(960,100))
for i,im in enumerate(segments):assembled.alpha_composite(im,(240*i,0))
assembled.save(S/'skyline_before_seam_repair.png')
a=np.array(assembled);before=a.copy();repairs=[]
for join in [240,480,720]:
 # Bridge only the opaque land silhouette, 12px each side, by adding the SAME
 # existing silhouette color. No filtered blending, alpha ramp, or image cloning.
 def height(x):
  # Broad row occupancy separates the hill crest from thin branch tips.
  opaque=(a[:,max(0,x-20):min(960,x+21),3]>0).mean(1)
  yy=np.where(opaque>.85)[0]
  return int(yy[0]) if len(yy) else 99
 l=join-24;r=join+23;yl=height(l);yr=height(r)
 oldband=a[:,l:r+1,:].copy()
 # Recut the narrow join as a quiet stepped hillside, using the same existing
 # opaque silhouette color. This removes clipped boundary twigs, not copy-paste.
 a[:,l:r+1,:]=0
 for x in range(l,r+1):
  y=round(yl+(yr-yl)*(x-l)/(r-l))
  a[max(0,y):,x,:]=HILL
 newband=a[:,l:r+1,:]
 edits=int(np.any(oldband!=newband,axis=2).sum())
 added=int(((oldband[:,:,3]==0)&(newband[:,:,3]>0)).sum())
 removed=int(((oldband[:,:,3]>0)&(newband[:,:,3]==0)).sum())
 repairs.append({'join_x':join,'band_x_inclusive':[l,r],'end_heights':[yl,yr],'changed_pixels':edits,'added_pixels':added,'removed_pixels':removed})
# Simple distant land reserved for runtime fog, deliberately featureless.
a[70:,:,:]=HILL
skyline=Image.fromarray(a);skyline.save(S/'skyline_repaired_native.png')
Image.fromarray(np.where(np.any(a!=before,axis=2)[:,:,None],np.array([255,80,160,255],np.uint8),np.array([0,0,0,0],np.uint8))).save(S/'skyline_repair_mask.png')
META['skyline_seams']=repairs

# Chapel: native cutout. Two dark tower windows survive; lower entry/window detail
# is consolidated into the body so it stays a distant, barely detailed silhouette.
chapel=keyed('chapel',[(58,63,70),(65,70,78),(72,77,85)])
bbox=chapel.getbbox();chapel=chapel.crop(bbox);ca=np.array(chapel)
for y in range(34,chapel.height):
 for x in range(chapel.width):
  if ca[y,x,3] and tuple(ca[y,x,:3])==(58,63,70):ca[y,x,:3]=(65,70,78)
chapel=Image.fromarray(ca);chapel.save(S/'chapel_cleaned_native.png')
# Top row's narrow tower apex supplies the alignment point, rather than canvas center.
ytip=np.where(ca[:,:,3].any(1))[0][0];xtip=int(round(np.where(ca[ytip,:,3]>0)[0].mean()))
chapelpos=(480-xtip,71-chapel.height)
META['chapel'].update({'crop_bbox':list(bbox),'visible_size':list(chapel.size),'placement_top_left':chapelpos,'steeple_tip_x':480})
back=sky.copy();back.alpha_composite(chapel,chapelpos);back.alpha_composite(skyline)
back.convert('RGBA').save(ROOT/'entry_backdrop_01.png')
back.resize((1920,200),NEAR).save(Q/'entry_backdrop_2x.png')
back.resize((3840,400),NEAR).save(Q/'entry_backdrop_4x.png')
# Seam strips after repair, and matching before/after comparison.
seamview=Image.new('RGBA',(288,800),(24,25,29,255))
for i,j in enumerate([240,480,720]):
 seamview.alpha_composite(back.crop((j-6,0,j+6,100)).resize((96,800),NEAR),(96*i,0))
seamview.save(Q/'skyline_seams_8x.png')

# Foreground branches: independent original sources, no mirror. Keep native scale.
BRANCHPAL=[(14,15,18),(19,21,24),(29,32,36)]
for side,height in [('left',175),('right',150)]:
 name='branches_'+side;im=keyed(name,BRANCHPAL);bbox=im.getbbox();cut=im.crop(bbox)
 # Left source is taller than approximate brief height. Preserve all twig tips.
 canvas=Image.new('RGBA',(220,height));x=0 if side=='left' else 220-cut.width;y=height-cut.height
 assert x>=0 and y>=0,(side,cut.size)
 canvas.alpha_composite(cut,(x,y));canvas.save(ROOT/f'fg_branches_{side}_01.png')
 META[name].update({'crop_bbox':list(bbox),'visible_size':list(cut.size),'final_canvas':[220,height],'integer_offset':[x,y],'edge_anchor':'bottom_'+side})
 # Checker is QA only; actual sprite remains transparent.
 checker=Image.new('RGBA',canvas.size,(93,96,102,255));cd=ImageDraw.Draw(checker)
 for yy in range(0,height,8):
  for xx in range(0,220,8):
   if (xx//8+yy//8)%2:cd.rectangle((xx,yy,xx+7,yy+7),fill=(107,110,116,255))
 checker.alpha_composite(canvas);checker.resize((880,height*4),NEAR).save(Q/f'fg_branches_{side}_4x.png')

# Greybox reference is 960x1090: upper 540px + 10px divider + lower 540px.
grey=Image.open(REPO/'docs/reference/cemetery_entry_greybox.png').convert('RGBA')
assert grey.size==(960,1090)
upper=grey.crop((0,0,960,540));lower=grey.crop((0,550,960,1090))
# Required flat-top paste preview. The image cannot recreate hidden engine layers;
# keep a separate note in QA that y0..99 replaces baked screenshot pixels.
upper.alpha_composite(back,(0,0));upper.resize((1920,1080),NEAR).save(Q/'backdrop_on_greybox_2x.png')
for side in ['left','right']:
 im=Image.open(ROOT/f'fg_branches_{side}_01.png').convert('RGBA')
 lower.alpha_composite(im,(0 if side=='left' else 960-im.width,540-im.height))
lower.resize((1920,1080),NEAR).save(Q/'branches_on_greybox_2x.png')
META['preview']={'greybox_size':[960,1090],'upper_crop':[0,0,960,540],'lower_crop':[0,550,960,1090],'central_clear_x_inclusive':[380,580],'note':'Offline paste preview; scene untouched, no fog/tint added. Backdrop replaces screenshot top100px as requested, not a live engine layer.'}
(S/'assembly_metadata.json').write_text(json.dumps(META,indent=2)+'\n')
print(json.dumps(META,indent=2))
