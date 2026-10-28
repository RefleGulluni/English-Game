"""Select native AI repair pixels, pair edge profiles, export unretouched QC."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,zipfile,datetime,subprocess,sys
S=Path(__file__).resolve().parent;T=S.parents[1];R=T.parents[3];Q=T/'qc'
existing=[T/'paving_texture_01.png']+list(Q.glob('paving_*'))+list(S.glob('07_*'))
if existing:
 with zipfile.ZipFile(Q/f'backups/paving_before_finish_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in existing:
   if p.is_file():z.write(p,str(p.relative_to(T)))
meta=json.loads((S/'04_cleanup_metadata.json').read_text());pal=np.array(meta['palette'],np.uint8)
old=np.array(Image.open(S/'05_half_offset_native.png').convert('RGB'))
edit=np.array(Image.open(S/'06_cross_repair_restored_cells.png').convert('RGB'));assert edit.shape==old.shape==(128,224,3)
lab=np.argmin(((edit.astype(float)[:,:,None]-pal[None,None].astype(float))**2).sum(3),2)
e=pal[lab];Image.fromarray(e).save(S/'07_repair_palette_native.png')
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
left=cut(cost[:,78:96])+78;right=cut(cost[:,130:148])+130
top=cut(cost[39:52].T)+39;bottom=cut(cost[76:89].T)+76
yy,xx=np.indices((128,224));mask=((xx>=left[:,None])&(xx<=right[:,None]))|((yy>=top[None,:])&(yy<=bottom[None,:]))
mask[[0,-1]]=False;mask[:,[0,-1]]=False
out=old.copy();out[mask]=e[mask]
out[:,-1]=out[:,0];out[-1]=out[0]
Image.fromarray(out).convert('RGBA').save(T/'paving_texture_01.png')
Image.fromarray((mask*255).astype('uint8')).save(S/'07_cross_selection_mask.png')
(S/'07_assembly.json').write_text(json.dumps({'repair_pixel_count':int(mask.sum()),'method':'Native source and AI cross-repair pixels; irregular min-error cut; 1px opposite textured profiles paired. No blended pixels, procedural grain, blur or art resampling.','left_cut':left.tolist(),'right_cut':right.tolist(),'top_cut':top.tolist(),'bottom_cut':bottom.tolist()},indent=2)+'\n')
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
checks={'size':[224,128],'mean_rgb':out.mean((0,1)).tolist(),'colors':len(np.unique(out.reshape(-1,3),axis=0)),'horizontal_change':float(np.any(out[:,1:]!=out[:,:-1],2).mean()*100),'vertical_change':float(np.any(out[1:]!=out[:-1],2).mean()*100),'palette_component_max':out.max((0,1)).tolist(),'opposite_left_right_exact':bool(np.array_equal(out[:,0],out[:,-1])),'opposite_top_bottom_exact':bool(np.array_equal(out[0],out[-1])),'alpha_values':[255],'bare_fill_native_size':[960,540],'bare_fill_scale':2,'status':'SECTION9_PAVING_READY_FOR_USER_REVIEW','sha256':hashlib.sha256((T/'paving_texture_01.png').read_bytes()).hexdigest(),'props_preview':'672x384 rectangular material patch on approved mud, native-scale3 tombstones and hero. Hard rectangle is a comparison swatch, not Claude terrain shape. No lighting/fog/shadows added.'}
locked=json.loads((S/'protected_previous_assets.json').read_text());checks['previous_files_unchanged_except_status']=all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in locked.items() if p!='art/cemetery_v3/ground/transitions/STATUS.md')
assert checks['previous_files_unchanged_except_status'] and checks['opposite_left_right_exact'] and checks['opposite_top_bottom_exact']
assert 25<=checks['colors']<=35 and 55<=checks['horizontal_change']<=70
assert all(lo<=v<=hi for v,lo,hi in zip(checks['mean_rgb'],[80,80,76],[90,88,84]))
assert all(a<=b for a,b in zip(checks['palette_component_max'],[118,116,108]))
result=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(T/'paving_texture_01.png')],cwd=R,text=True,capture_output=True,check=True)
(Q/'paving_texture_pixel_check.txt').write_text(result.stdout)
(Q/'paving_texture_verification.json').write_text(json.dumps(checks,indent=2)+'\n');print(checks);print(result.stdout)
