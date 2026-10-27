"""Assemble AI center-cross repair from native source pixels, then inspect wraps."""
from pathlib import Path
from PIL import Image
from collections import Counter
import numpy as np,json,zipfile,datetime,sys,subprocess,hashlib
S=Path(__file__).resolve().parent;T=S.parents[1];G=T.parent;R=G.parents[2];Q=T/'qc'
existing=[T/'grass_texture_01.png',Q/'grass_texture_fill_2x.png',Q/'grass_texture_pixel_check.txt',Q/'grass_texture_verification.json']+list(S.glob('05_*'))
existing=[p for p in existing if p.exists()]
if existing:
 with zipfile.ZipFile(Q/f'backups/grass_texture_before_finish_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in existing:z.write(p,str(p.relative_to(T)))
cleanup_meta=json.loads((S/'02_cleanup_metadata.json').read_text())
pal=np.array(cleanup_meta['palette'],np.uint8);material_roles=np.array(cleanup_meta['palette_roles']);highlight_ids=set(cleanup_meta['highlight_palette_indices'])
old=np.array(Image.open(S/'03_half_offset_native.png').convert('RGB'));edit=np.array(Image.open(S/'04_cross_repair_restored_cells.png').convert('RGB'));assert old.shape==edit.shape==(128,224,3)
lab=np.argmin(((edit.astype(float)[:,:,None,:]-pal[None,None,:,:])**2).sum(3),axis=2)
def change(l):return float((l[:,1:]!=l[:,:-1]).mean()*100)
progress=[change(lab)]
for iteration in range(2):
 if change(lab)<=72:break
 counts=np.bincount(lab.ravel(),minlength=len(pal));seen=np.zeros(lab.shape,bool);out=lab.copy()
 for y in range(128):
  for x in range(224):
   if seen[y,x]:continue
   c=int(lab[y,x]);todo=[(x,y)];seen[y,x]=1;pts=[];adj=Counter()
   while todo:
    xx,yy=todo.pop();pts.append((xx,yy))
    for nx,ny in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
     if not(0<=nx<224 and 0<=ny<128):continue
     k=int(lab[ny,nx])
     if k==c and not seen[ny,nx]:seen[ny,nx]=1;todo.append((nx,ny))
     elif k!=c:adj[k]+=1
   if len(pts)>5:continue
   choices=[k for k in adj if material_roles[k]==material_roles[c] and counts[k]>counts[c] and np.linalg.norm(pal[k].astype(float)-pal[c])<=18]
   if not choices:continue
   k=max(choices,key=lambda k:(adj[k],-np.linalg.norm(pal[k].astype(float)-pal[c])))
   for xx,yy in pts:out[yy,xx]=k
 lab=out;progress.append(change(lab))
e=pal[lab];Image.fromarray(e).save(S/'05_repair_palette_native.png')
def cut(cost):
 h,w=cost.shape;dp=cost[0].copy();prev=np.zeros((h,w),int)
 for y in range(1,h):
  row=np.empty(w)
  for x in range(w):
   options=range(max(0,x-1),min(w,x+2));k=min(options,key=lambda k:dp[k]+.05*abs(k-x));row[x]=cost[y,x]+dp[k]+.05*abs(k-x);prev[y,x]=k
  dp=row
 x=int(dp.argmin());p=[x]
 for y in range(h-1,0,-1):x=int(prev[y,x]);p.append(x)
 return np.array(p[::-1])
cost=((old.astype(float)-e.astype(float))**2).mean(2)
left=cut(cost[:,92:106])+92;right=cut(cost[:,119:133])+119
top=cut(cost[46:59,:].T)+46;bottom=cut(cost[70:83,:].T)+70
yy,xx=np.indices((128,224));selection=((xx>=left[:,None])&(xx<=right[:,None]))|((yy>=top[None,:])&(yy<=bottom[None,:]));selection[[0,-1]]=False;selection[:,[0,-1]]=False
out=old.copy();out[selection]=e[selection]
# Pair textured native edge profiles. No flat-color border is introduced.
out[:,-1]=out[:,0];out[-1]=out[0]
final_labels=np.argmin(((out.astype(float)[:,:,None,:]-pal[None,None,:,:])**2).sum(3),axis=2);merges=[]
# A small number of almost identical shades may still alternate along intact
# strands. Merge nearest SAME-material swatches globally, never redraw plants.
for iteration in range(7):
 if change(final_labels)<=72:break
 active,weights=np.unique(final_labels,return_counts=True)
 if len(active)<=25:break
 count_map=dict(zip(active,weights));pairs=[]
 for j,i in enumerate(active):
  for k in active[j+1:]:
   if i in highlight_ids or k in highlight_ids or material_roles[i]!=material_roles[k]:continue
   distance=float(np.linalg.norm(pal[i].astype(float)-pal[k]))
   if distance<=8:pairs.append((distance,int(i),int(k)))
 if not pairs:break
 distance,i,k=min(pairs);keep,drop=(i,k) if count_map[i]>=count_map[k] else (k,i)
 final_labels[final_labels==drop]=keep
 merges.append({'from_id':drop,'to_id':keep,'material':str(material_roles[keep]),'rgb_distance':distance,'change_after':change(final_labels)})
active,weights=np.unique(final_labels,return_counts=True);newpal=pal[active].astype(float);is_high=np.array([int(i) in highlight_ids for i in active]);fraction=weights[~is_high].sum()/weights.sum()
newpal[~is_high]+=(np.array([67.,71.,55.])-np.average(newpal,axis=0,weights=weights))/fraction
newpal=np.rint(newpal).clip(0,255).astype('uint8');taken=set()
for i in range(len(newpal)):
 if tuple(newpal[i]) in taken:
  for delta in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
   c=newpal[i].astype(int)+np.array(delta)
   if tuple(c) not in taken:newpal[i]=c;break
 taken.add(tuple(newpal[i]))
final_lookup=pal.copy()
for i,c in zip(active,newpal):final_lookup[i]=c
out=final_lookup[final_labels]
(S/'05_final_palette.json').write_text(json.dumps({'same_material_near_shade_merges':merges,'final_palette':newpal.tolist(),'source_palette_ids':active.tolist(),'roles':material_roles[active].tolist(),'highlight_mask':is_high.tolist(),'mean_calibration':'67,71,55 by changing non-highlight swatches only; preserve explicitly requested straw highlights and all paired edges.'},indent=2)+'\n')
Image.fromarray(out).convert('RGBA').save(T/'grass_texture_01.png');Image.fromarray((selection*255).astype('uint8')).save(S/'05_cross_selection_mask.png')
(S/'05_assembly.json').write_text(json.dumps({'method':'Existing source/edit native pixels selected by irregular minimum-error center-cross cuts;1px opposite textured edge profiles paired. No blend, blur, synthesized grain or image resampling.','repair_horizontal_change_progress':progress,'repair_pixel_count':int(selection.sum()),'left_cut':left.tolist(),'right_cut':right.tolist(),'top_cut':top.tolist(),'bottom_cut':bottom.tolist(),'palette':pal.tolist()},indent=2)+'\n')
canvas=np.empty((640,1120,3),np.uint8)
for y in range(5):
 for x in range(5):canvas[y*128:y*128+128,x*224:x*224+224]=out
Image.fromarray(canvas[:540,:960]).resize((1920,1080),Image.Resampling.NEAREST).save(Q/'grass_texture_fill_2x.png')
Image.fromarray(out).resize((1344,768),Image.Resampling.NEAREST).save(Q/'grass_texture_native_6x.png')
wrap=np.tile(out,(2,2,1));Image.fromarray(wrap[104:152,200:248]).resize((384,384),Image.Resampling.NEAREST).save(Q/'grass_texture_wrap_junction_8x.png')
Image.fromarray(out[44:84,88:136]).resize((384,320),Image.Resampling.NEAREST).save(Q/'grass_texture_center_repair_8x.png')
checks={'size':[224,128],'mean_rgb':out.mean(axis=(0,1)).tolist(),'colors':len(np.unique(out.reshape(-1,3),axis=0)),'horizontal_change':float(np.any(out[:,1:]!=out[:,:-1],axis=2).mean()*100),'opposite_left_right_exact':bool(np.array_equal(out[:,0],out[:,-1])),'opposite_top_bottom_exact':bool(np.array_equal(out[0],out[-1])),'all_alpha_255':set(Image.open(T/'grass_texture_01.png').getchannel('A').getdata())=={255},'bare_fill_native_size':[960,540],'bare_fill_scale':2,'status':'SECTION7_GRASS_TEXTURE_READY_FOR_USER_REVIEW','straw_highlight_rgb':newpal[is_high].tolist(),'near_shade_merges':merges}
locked=json.loads((S/'protected_previous_assets.json').read_text());checks['protected_previous_files_unchanged']=all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in locked.items());assert checks['protected_previous_files_unchanged']
assert checks['opposite_left_right_exact'] and checks['opposite_top_bottom_exact'] and checks['all_alpha_255']
assert 25<=checks['colors']<=35 and 60<=checks['horizontal_change']<=72
assert all(lo<=v<=hi for v,lo,hi in zip(checks['mean_rgb'],[66,70,54],[74,78,62]))
res=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(T/'grass_texture_01.png')],cwd=R,text=True,capture_output=True,check=True);(Q/'grass_texture_pixel_check.txt').write_text(res.stdout);(Q/'grass_texture_verification.json').write_text(json.dumps(checks,indent=2)+'\n');print(checks);print(res.stdout)
