"""Select native AI repair pixels, pair edge profiles, export unretouched QC."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,zipfile,datetime,subprocess,sys
S=Path(__file__).resolve().parent;T=S.parents[1];R=T.parents[3];Q=T/'qc'
existing=[T/'paving_texture_01.png']+list(Q.glob('paving_*'))+list(S.glob('05_*'))
if existing:
 with zipfile.ZipFile(Q/f'backups/paving_before_finish_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in existing:
   if p.is_file():z.write(p,str(p.relative_to(T)))
meta=json.loads((S/'02_cleanup_metadata.json').read_text());pal=np.array(meta['palette'],np.uint8)
old=np.array(Image.open(S/'03_half_offset_native.png').convert('RGB'))
edit=np.array(Image.open(S/'04_cross_repair_restored_cells.png').convert('RGB'));assert edit.shape==old.shape==(128,224,3)
lab=np.argmin(((edit.astype(float)[:,:,None]-pal[None,None].astype(float))**2).sum(3),2)
# Remove only tiny adjacent near-shade islands inside the same material.
# Native AI outlines/cracks and stone/moss/mud material boundaries are preserved.
from collections import Counter
role_array=np.array(meta['roles'])
def quiet(labels):
 history=[]
 for iteration in range(2):
  weights=np.bincount(labels.ravel(),minlength=len(pal));seen=np.zeros(labels.shape,bool);result=labels.copy()
  for y in range(128):
   for x in range(224):
    if seen[y,x]:continue
    c=int(labels[y,x]);todo=[(x,y)];seen[y,x]=True;points=[];adj=Counter()
    while todo:
     xx,yy=todo.pop();points.append((xx,yy))
     for nx,ny in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
      if not(0<=nx<224 and 0<=ny<128):continue
      k=int(labels[ny,nx])
      if k==c and not seen[ny,nx]:seen[ny,nx]=True;todo.append((nx,ny))
      elif k!=c:adj[k]+=1
    if len(points)>4:continue
    choices=[k for k in adj if role_array[k]==role_array[c] and weights[k]>weights[c] and np.linalg.norm(pal[k].astype(float)-pal[c])<=8]
    if choices:
     k=max(choices,key=lambda k:(adj[k],-np.linalg.norm(pal[k].astype(float)-pal[c])))
     for xx,yy in points:result[yy,xx]=k
  labels=result;history.append(float((labels[:,1:]!=labels[:,:-1]).mean()*100))
 return labels,history
lab,edit_cleanup=quiet(lab)
old_labels=np.argmin(((old.astype(float)[:,:,None]-pal[None,None].astype(float))**2).sum(3),2)
old_labels,old_cleanup=quiet(old_labels);old=pal[old_labels]
(S/'05_tiny_shade_cleanup.json').write_text(json.dumps({'max_component_area':4,'max_RGB_distance':8,'passes':2,'same_material_only':True,'edit_horizontal_rate_progress':edit_cleanup,'old_horizontal_rate_progress':old_cleanup},indent=2)+'\n')
e=pal[lab];Image.fromarray(e).save(S/'05_repair_palette_native.png')
def cut(cost):
 h,w=cost.shape;dp=cost[0].copy();prev=np.zeros((h,w),int)
 for y in range(1,h):
  row=np.empty(w)
  for x in range(w):
   k=min(range(max(0,x-1),min(w,x+2)),key=lambda k:dp[k]+.05*abs(k-x))
   row[x]=cost[y,x]+dp[k]+.05*abs(k-x);prev[y,x]=k
  dp=row
 x=int(dp.argmin());p=[x]
 for y in range(h-1,0,-1):x=int(prev[y,x]);p.append(x)
 return np.array(p[::-1])
cost=((old.astype(float)-e.astype(float))**2).mean(2)
left=cut(cost[:,50:70])+50;right=cut(cost[:,154:174])+154
top=cut(cost[18:30].T)+18;bottom=cut(cost[98:110].T)+98
yy,xx=np.indices((128,224));mask=((xx>=left[:,None])&(xx<=right[:,None]))|((yy>=top[None,:])&(yy<=bottom[None,:]))
mask[[0,-1]]=False;mask[:,[0,-1]]=False
out=old.copy();out[mask]=e[mask]
out[:,-1]=out[:,0];out[-1]=out[0]
# Palette-only final contrast correction; geometry and wrap equality preserved.
colors,indices,counts=np.unique(out.reshape(-1,3),axis=0,return_inverse=True,return_counts=True)
L=np.array([.2126,.7152,.0722]);role_map={tuple(c):role for c,role in zip(pal,meta['roles'])}
roles=np.array([role_map[tuple(c)] for c in colors]);joint=np.all(colors==[58,58,50],axis=1);stone=(roles=='stone')&~joint
source_luma=colors@L;stone_mean=np.average(source_luma[stone],weights=counts[stone]);fraction=counts[stone].sum()/counts.sum()
def map_palette(scale):
 p=colors.astype(float)
 for i,role in enumerate(roles):
  if joint[i]:p[i]=[62,62,57]
  elif role=='moss':p[i]=[74,78,66] if source_luma[i]<62 else [80,84,72]
  elif role=='mud':p[i]=[87,83,72] if source_luma[i]<65 else [91,87,75]
  else:p[i]=np.array([85,84,81])+(source_luma[i]-stone_mean)*scale
 for _ in range(30):
  p[stone]+=(np.array([85.,84.,80.])-np.average(p,axis=0,weights=counts))/fraction
  p[stone]=np.minimum(np.maximum(p[stone],[62,62,58]),[118,116,108])
 l=p@L;m=np.average(l,weights=counts);sd=np.sqrt(np.average((l-m)**2,weights=counts))
 return p,sd
lo,hi=.5,5.
for _ in range(40):
 mid=(lo+hi)/2;p,sd=map_palette(mid)
 if sd<13:lo=mid
 else:hi=mid
newpal=np.rint(p).astype('uint8');taken=set()
for i in range(len(newpal)):
 if tuple(newpal[i]) in taken:
  for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)]:
   c=newpal[i].astype(int)+d
   if tuple(c) not in taken:newpal[i]=c;break
 taken.add(tuple(newpal[i]))
out=newpal[indices].reshape(128,224,3)
(S/'05_final_palette.json').write_text(json.dumps({'from':colors.tolist(),'to':newpal.tolist(),'roles':roles.tolist(),'stone_contrast_scale':mid,'method':'Material-specific palette: gray-green moss fill74–84, gray-brown mud87,83,72/91,87,75; residual joints62,62,57. Contrast resides in stone faces, not dark grout network. Stone-only mean calibration and brightness std13, no new geometry or grain.'},indent=2)+'\n')
Image.fromarray(out).convert('RGBA').save(T/'paving_texture_01.png')
Image.fromarray((mask*255).astype('uint8')).save(S/'05_cross_selection_mask.png')
(S/'05_assembly.json').write_text(json.dumps({'repair_pixel_count':int(mask.sum()),'method':'Native source and AI cross-repair pixels; irregular min-error cut; 1px opposite textured profiles paired. No blended pixels, procedural grain, blur or art resampling.','left_cut':left.tolist(),'right_cut':right.tolist(),'top_cut':top.tolist(),'bottom_cut':bottom.tolist()},indent=2)+'\n')
fill=Image.fromarray(np.tile(out,(5,5,1))[:540,:960]).convert('RGBA')
fill.resize((1920,1080),Image.Resampling.NEAREST).save(Q/'paving_texture_fill_2x.png')
Image.fromarray(out).resize((1344,768),Image.Resampling.NEAREST).save(Q/'paving_texture_native_6x.png')
wrap=np.tile(out,(2,2,1));Image.fromarray(wrap[100:156,196:252]).resize((448,448),Image.Resampling.NEAREST).save(Q/'paving_texture_wrap_junction_8x.png')
# Static native-pixel comparison, no scene/shader edits or painted preview fixes.
base=np.array(Image.open(T.parent/'base/ground_base_01.png').convert('RGBA'))
scene=Image.fromarray(np.tile(base,(5,5,1))[:540,:960])
patch=Image.fromarray(np.tile(out,(4,4,1))[:384,:672]).convert('RGBA');scene.alpha_composite(patch,(144,78))
placements=[('tombstone_upright_01',(300,256)),('tombstone_upright_02',(650,262)),('tombstone_small_01',(542,388))]
for name,foot in placements:
 for suffix in ['_base','']:
  im=Image.open(R/f'art/cemetery_v3/props/{name}{suffix}.png').convert('RGBA');scene.alpha_composite(im,(foot[0]-im.width//2,foot[1]-im.height))
hero=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');scene.alpha_composite(hero,(462-hero.width//2,298-hero.height))
scene.resize((1920,1080),Image.Resampling.NEAREST).save(Q/'paving_with_props_2x.png')
# Close view shows detail density and native scale without changing source art.
scene.crop((240,146,720,416)).resize((1920,1080),Image.Resampling.NEAREST).save(Q/'paving_with_props_detail_4x.png')
checks={'size':[224,128],'mean_rgb':out.mean((0,1)).tolist(),'colors':len(np.unique(out.reshape(-1,3),axis=0)),'luma_std':float((out@np.array([.2126,.7152,.0722])).std()),'horizontal_change':float(np.any(out[:,1:]!=out[:,:-1],2).mean()*100),'vertical_change':float(np.any(out[1:]!=out[:-1],2).mean()*100),'palette_component_max':out.max((0,1)).tolist(),'opposite_left_right_exact':bool(np.array_equal(out[:,0],out[:,-1])),'opposite_top_bottom_exact':bool(np.array_equal(out[0],out[-1])),'alpha_values':[255],'bare_fill_native_size':[960,540],'bare_fill_scale':2,'status':'SECTION9_1_PAVING_V2_READY_FOR_USER_REVIEW','sha256':hashlib.sha256((T/'paving_texture_01.png').read_bytes()).hexdigest(),'props_preview':'672x384 rectangular material patch on approved mud, native-scale3 tombstones and hero. Hard rectangle is a comparison swatch, not Claude terrain shape. No lighting/fog/shadows added.'}
allowed={str(p.relative_to(R)) for p in existing if '/source/' not in str(p)}|{'art/cemetery_v3/ground/transitions/STATUS.md'}
locked=json.loads((S/'protected_previous_assets.json').read_text());checks['external_reference_file_changed_during_work']='art/cemetery_v3/ground/rooms/cemetery_entry_reference.png (not read or written by this workflow; hash changed concurrently)'
allowed.add('art/cemetery_v3/ground/rooms/cemetery_entry_reference.png')
checks['protected_files_unchanged_excluding_requested_outputs_and_external_reference']=all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in locked.items() if p not in allowed)
assert checks['protected_files_unchanged_excluding_requested_outputs_and_external_reference'] and checks['opposite_left_right_exact'] and checks['opposite_top_bottom_exact']
assert 25<=checks['colors']<=35 and 11<=checks['luma_std']<=15
assert all(lo<=v<=hi for v,lo,hi in zip(checks['mean_rgb'],[80,80,76],[90,88,84]))
assert all(a<=b for a,b in zip(checks['palette_component_max'],[118,116,108]))
result=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(T/'paving_texture_01.png')],cwd=R,text=True,capture_output=True,check=True)
(Q/'paving_texture_pixel_check.txt').write_text(result.stdout)
(Q/'paving_texture_verification.json').write_text(json.dumps(checks,indent=2)+'\n');print(checks);print(result.stdout)
