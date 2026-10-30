"""Section4: approved soil pixels, injective recolor, hand-authored local shade edits."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,itertools,hashlib,zipfile,datetime,subprocess,sys
S=Path(__file__).resolve().parent;B=S.parents[2];Q=B/'qc';R=B.parents[3]
LUMA=np.array([.2126,.7152,.0722])
# Each outline is manually specified. No random fields,noise,texture synthesis,
# smoothing of source art,or regeneration is used. Feather only chooses swatches.
FEATURES=[
 {'wet':[
  [(23,34),(31,23),(44,21),(57,27),(70,25),(77,36),(71,45),(62,49),(48,45),(38,49),(25,43)],
  [(142,69),(151,59),(168,61),(177,56),(190,67),(186,79),(172,87),(158,83),(147,86)],
  [(75,99),(82,91),(94,93),(105,101),(101,113),(90,115),(80,110)]],
 'sheen':[
  [(92,30),(103,23),(115,26),(124,22),(132,34),(125,43),(109,46),(97,40)],
  [(25,81),(34,73),(45,76),(55,72),(61,83),(54,91),(39,93),(28,88)]],
 'leaves':[[(39,64),(40,64),(40,65)],[(131,34),(132,34)],[(181,100),(181,101),(182,101),(183,101)],[(83,86),(84,86),(85,87)]]},
 {'wet':[
  [(94,55),(104,44),(119,47),(132,42),(147,49),(151,62),(141,74),(126,72),(113,77),(99,67)],
  [(31,91),(41,82),(54,85),(63,94),(57,108),(45,112),(34,104)],
  [(169,23),(179,14),(195,17),(204,14),(212,27),(206,37),(192,41),(178,35)]],
 'sheen':[
  [(35,34),(47,26),(63,29),(78,24),(89,36),(80,48),(65,51),(51,46),(39,47)],
  [(154,93),(162,84),(173,86),(184,82),(191,95),(185,109),(174,114),(162,105)]],
 'leaves':[[(64,29),(65,29),(65,30)],[(162,48),(163,49)],[(111,101),(112,101),(113,101),(113,102)],[(197,79),(198,79)]]}
]
def feather(poly):
 mask=Image.new('1',(224,128));ImageDraw.Draw(mask).polygon(poly,fill=1);inside=np.array(mask)
 yy,xx=np.indices((128,224));points=np.stack([xx,yy],2).astype(float);dist=np.full((128,224),1e6)
 for start,end in zip(poly,poly[1:]+poly[:1]):
  a=np.array(start,float);v=np.array(end,float)-a;t=np.clip(((points-a)*v).sum(2)/(v@v),0,1);d=np.linalg.norm(points-(a+t[:,:,None]*v),axis=2);dist=np.minimum(dist,d)
 return inside*np.minimum(dist/6.5,1)
def main():
 existing=[B/'veiled_base_01.png',B/'veiled_base_02.png']+list(Q.glob('veiled_base_*'))+list(S.glob('0[123]_*'))
 # First rejected material already has the requested recovery package;only
 # revision reruns need another pixel backup,while source records are retained.
 if (S/'03_revision_metrics.json').exists():
  with zipfile.ZipFile(Q/f'backups/veiled_native_before_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
   for p in existing:
    if p.is_file():z.write(p,str(p.relative_to(B)))
 originals=[np.array(Image.open(B/f'ground_base_{i:02}.png').convert('RGB')) for i in [1,2]]
 colors,counts=np.unique(np.concatenate([a.reshape(-1,3) for a in originals]),axis=0,return_counts=True);assert len(colors)==39
 lum=colors@LUMA;mean=np.average(lum,weights=counts);sd=np.sqrt(np.average((lum-mean)**2,weights=counts))
 chrom=colors.astype(float)-lum[:,None];chrom-=np.average(chrom,axis=0,weights=counts)
 desired=np.array([61.,64.,63.])+(8.9/sd)*(lum-mean)[:,None]+.12*chrom
 new=np.zeros_like(colors);used=set()
 for i in sorted(range(len(colors)),key=lambda i:-counts[i]):
  center=np.rint(desired[i]).astype(int);choices=[]
  for delta in itertools.product(range(-2,3),repeat=3):
   c=center+delta
   if tuple(c) in used or c[1]<c[0]+1 or abs(c[2]-c[1])>3 or c[2]<c[0]:continue
   error=np.sum((c-desired[i])**2)+2*((c-desired[i])@LUMA)**2;choices.append((error,tuple(c)))
  assert choices
  _,c=min(choices);new[i]=c;used.add(c)
 assert len(used)==39
 outputs=[];metrics=[]
 for index,original in enumerate(originals):
  ids=np.argmin(((original.astype(float)[:,:,None]-colors[None,None].astype(float))**2).sum(3),2)
  assert np.array_equal(colors[ids],original)
  recolored=new[ids];Image.fromarray(recolored).save(S/f'01_recolored_{index+1:02}_native.png')
  # All intended local differences are <=2.4 levels,with3-level leaf shreds.
  shift=np.zeros((128,224),float)
  for poly in FEATURES[index]['wet']:shift-=2.4*feather(poly)
  for poly in FEATURES[index]['sheen']:shift+=1.6*feather(poly)
  for cluster in FEATURES[index]['leaves']:
   assert 2<=len(cluster)<=4
   for x,y in cluster:shift[y,x]-=3.0
  shift=np.clip(shift,-3,2);shift[:8]=0;shift[-8:]=0;shift[:,:8]=0;shift[:,-8:]=0
  target=recolored.astype(float)+shift[:,:,None]
  rgb_error=((target[:,:,None]-new[None,None].astype(float))**2).sum(3)
  value_error=((target@LUMA)[:,:,None]-(new@LUMA)[None,None])**2
  ids2=np.argmin(rgb_error+value_error,2);out=new[ids2]
  # Zero-shift pixels retain their ORIGINAL palette IDs,not a near neighbor.
  out[shift==0]=recolored[shift==0]
  for edge in [lambda a:a[:8],lambda a:a[-8:],lambda a:a[:,:8],lambda a:a[:,-8:]]:assert np.array_equal(edge(out),edge(recolored))
  Image.fromarray(out).convert('RGBA').save(B/f'veiled_base_{index+1:02}.png');outputs.append(out)
  Image.fromarray(np.rint((shift+3)/5*255).astype('uint8')).save(S/f'02_authored_shade_mask_{index+1:02}.png')
  changed=np.any(out!=recolored,2);delta=(out.astype(float)-recolored)@LUMA
  metrics.append({'mean_rgb':out.mean((0,1)).tolist(),'luma_std':float((out@LUMA).std()),'colors':len(np.unique(out.reshape(-1,3),axis=0)),'recolor_injective':True,'recolored_unique_colors':len(np.unique(recolored.reshape(-1,3),axis=0)),'local_changed_pixels':int(changed.sum()),'local_changed_fraction':float(changed.mean()),'local_luma_delta_min_max':[float(delta.min()),float(delta.max())],'same_recolored_source_outer8px':True,'horizontal_change':float(np.any(out[:,1:]!=out[:,:-1],2).mean()*100),'sha256':hashlib.sha256((B/f'veiled_base_{index+1:02}.png').read_bytes()).hexdigest()})
  assert all(lo<=v<=hi for v,lo,hi in zip(metrics[-1]['mean_rgb'],[58,61,60],[63,66,65]))
  assert 8<=metrics[-1]['luma_std']<=10 and 30<=metrics[-1]['colors']<=40
 (S/'01_common_palette.json').write_text(json.dumps({'source':'Approved ground_base_01/02.png only','source_color_count':39,'target_color_count':39,'injective':True,'old_mean_rgb':np.average(colors,axis=0,weights=counts).tolist(),'new_mean_rgb_before_features':np.average(new,axis=0,weights=counts).tolist(),'old_luma_std':float(sd),'mapping':[{'from':c.tolist(),'to':n.tolist(),'count':int(k)} for c,n,k in zip(colors,new,counts)],'method':'Exact39-to39 common lookup,scaled luminance offsets and desaturated original chroma;nearest distinct RGB swatches;no blue overlay,source texture edit,blur or image generation.'},indent=2)+'\n')
 (S/'02_authored_features.json').write_text(json.dumps({'features':FEATURES,'wet_strength':-2.4,'sheen_strength':1.6,'leaf_strength':-3.0,'feather_width_px':6.5,'outer8px_locked':True,'method':'Manually specified irregular polygon regions and2–4pixel leaf clusters. Distance to authored edge selects nearby existing palette swatches,retaining source fine texture. No source pixel averaging,art blur,random texture or newly generated material.'},indent=2)+'\n')
 (S/'03_revision_metrics.json').write_text(json.dumps({'status':'SECTION4_NATIVE_SOIL_PENDING_VISUAL_REVIEW','images':metrics,'source_files':['ground_base_01.png','ground_base_02.png'],'image_generation_used':False},indent=2)+'\n')
 print(metrics)
if __name__=='__main__':main()
