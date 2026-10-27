"""Assemble AI center-cross repair from native source pixels, then inspect wraps."""
from pathlib import Path
from PIL import Image
from collections import Counter
import numpy as np,json,zipfile,datetime,sys,subprocess,hashlib
S=Path(__file__).resolve().parent;T=S.parents[1];G=T.parent;R=G.parents[2];Q=T/'qc'
existing=[T/'path_texture_01.png',Q/'path_texture_fill_2x.png',Q/'path_texture_pixel_check.txt',Q/'path_texture_verification.json']+list(S.glob('06_*'))
existing=[p for p in existing if p.exists()]
if existing:
 with zipfile.ZipFile(Q/f'backups/path_texture_before_finish_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in existing:z.write(p,str(p.relative_to(T)))
pal=np.array(json.loads((S/'03_cleanup_metadata.json').read_text())['palette'],np.uint8)
old=np.array(Image.open(S/'04_half_offset_native.png').convert('RGB'));edit=np.array(Image.open(S/'05_cross_repair_restored_cells.png').convert('RGB'));assert old.shape==edit.shape==(128,224,3)
lab=np.argmin(((edit.astype(float)[:,:,None,:]-pal[None,None,:,:])**2).sum(3),axis=2)
def change(l):return float((l[:,1:]!=l[:,:-1]).mean()*100)
progress=[change(lab)]
for iteration in range(2):
 if change(lab)<=70:break
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
   if len(pts)>3:continue
   choices=[k for k in adj if counts[k]>counts[c] and np.linalg.norm(pal[k].astype(float)-pal[c])<=18]
   if not choices:continue
   k=max(choices,key=lambda k:(adj[k],-np.linalg.norm(pal[k].astype(float)-pal[c])))
   for xx,yy in pts:out[yy,xx]=k
 lab=out;progress.append(change(lab))
e=pal[lab];Image.fromarray(e).save(S/'06_repair_palette_native.png')
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
Image.fromarray(out).convert('RGBA').save(T/'path_texture_01.png');Image.fromarray((selection*255).astype('uint8')).save(S/'06_cross_selection_mask.png')
(S/'06_assembly.json').write_text(json.dumps({'method':'Existing source/edit native pixels selected by irregular minimum-error center-cross cuts;1px opposite textured edge profiles paired. No blend, blur, synthesized grain or image resampling.','repair_horizontal_change_progress':progress,'repair_pixel_count':int(selection.sum()),'left_cut':left.tolist(),'right_cut':right.tolist(),'top_cut':top.tolist(),'bottom_cut':bottom.tolist(),'palette':pal.tolist()},indent=2)+'\n')
canvas=np.empty((640,1120,3),np.uint8)
for y in range(5):
 for x in range(5):canvas[y*128:y*128+128,x*224:x*224+224]=out
Image.fromarray(canvas[:540,:960]).resize((1920,1080),Image.Resampling.NEAREST).save(Q/'path_texture_fill_2x.png')
Image.fromarray(out).resize((1344,768),Image.Resampling.NEAREST).save(Q/'path_texture_native_6x.png')
wrap=np.tile(out,(2,2,1));Image.fromarray(wrap[104:152,200:248]).resize((384,384),Image.Resampling.NEAREST).save(Q/'path_texture_wrap_junction_8x.png')
Image.fromarray(out[44:84,88:136]).resize((384,320),Image.Resampling.NEAREST).save(Q/'path_texture_center_repair_8x.png')
checks={'size':[224,128],'mean_rgb':out.mean(axis=(0,1)).tolist(),'colors':len(np.unique(out.reshape(-1,3),axis=0)),'horizontal_change':float(np.any(out[:,1:]!=out[:,:-1],axis=2).mean()*100),'opposite_left_right_exact':bool(np.array_equal(out[:,0],out[:,-1])),'opposite_top_bottom_exact':bool(np.array_equal(out[0],out[-1])),'all_alpha_255':set(Image.open(T/'path_texture_01.png').getchannel('A').getdata())=={255},'bare_fill_native_size':[960,540],'bare_fill_scale':2,'status':'SECTION5_TEXTURE_READY_FOR_USER_REVIEW'}
locked=json.loads((S/'protected_previous_assets.json').read_text());checks['protected_previous_files_unchanged']=all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in locked.items());assert checks['protected_previous_files_unchanged']
assert checks['opposite_left_right_exact'] and checks['opposite_top_bottom_exact'] and checks['all_alpha_255']
assert 25<=checks['colors']<=35 and 55<=checks['horizontal_change']<=70
assert all(lo<=v<=hi for v,lo,hi in zip(checks['mean_rgb'],[88,84,70],[95,90,76]))
res=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(T/'path_texture_01.png')],cwd=R,text=True,capture_output=True,check=True);(Q/'path_texture_pixel_check.txt').write_text(res.stdout);(Q/'path_texture_verification.json').write_text(json.dumps(checks,indent=2)+'\n');print(checks);print(res.stdout)
