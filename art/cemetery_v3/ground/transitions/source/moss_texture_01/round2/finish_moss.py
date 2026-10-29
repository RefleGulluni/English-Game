"""Select AI-repaired native pixels; export480x270 bare/propped checks."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,zipfile,datetime,subprocess,sys
S=Path(__file__).resolve().parent;T=S.parents[2];Q=T/'qc';R=T.parents[3]
exec(compile((S/'material_ops.py').read_text(),str(S/'material_ops.py'),'exec'))
existing=[T/'moss_texture_01.png']+list(Q.glob('moss_texture_*'))+list(S.glob('06_*'))
existing=[p for p in existing if p.is_file()]
if existing:
 with zipfile.ZipFile(Q/f'backups/moss_before_finish_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in existing:z.write(p,str(p.relative_to(T)))
meta=json.loads((S/'03_cleanup_metadata.json').read_text());pal=np.array(meta['palette'],np.uint8)
old=np.array(Image.open(S/'04_half_offset_native.png').convert('RGB'));edit=np.array(Image.open(S/'05_cross_repair_restored_cells.png').convert('RGB'));assert old.shape==edit.shape==(128,224,3)
lab=np.argmin(((edit.astype(float)[:,:,None]-pal[None,None].astype(float))**2).sum(3),2)
lichen=lab>=30;keep=small_lichen(lichen)
for y,x in zip(*np.where(lichen&~keep)):
 adjacent=[(xx,yy) for yy in range(max(0,y-2),min(128,y+3)) for xx in range(max(0,x-2),min(224,x+3)) if lab[yy,xx]<30]
 if adjacent:
  xx,yy=min(adjacent,key=lambda p:(p[0]-x)**2+(p[1]-y)**2);lab[y,x]=lab[yy,xx]
lab,progress=quiet(lab,pal);e=pal[lab];Image.fromarray(e).save(S/'06_repair_palette_native.png')
def cut(cost):
 h,w=cost.shape;dp=cost[0].copy();prev=np.zeros((h,w),int)
 for y in range(1,h):
  row=np.empty(w)
  for x in range(w):
   k=min(range(max(0,x-1),min(w,x+2)),key=lambda k:dp[k]+.05*abs(k-x));row[x]=cost[y,x]+dp[k]+.05*abs(k-x);prev[y,x]=k
  dp=row
 x=int(dp.argmin());p=[x]
 for y in range(h-1,0,-1):x=int(prev[y,x]);p.append(x)
 return np.array(p[::-1])
cost=((old.astype(float)-e.astype(float))**2).mean(2)
left=cut(cost[:,90:104])+90;right=cut(cost[:,120:135])+120;top=cut(cost[43:57].T)+43;bottom=cut(cost[73:87].T)+73
yy,xx=np.indices((128,224));selection=((xx>=left[:,None])&(xx<=right[:,None]))|((yy>=top[None,:])&(yy<=bottom[None,:]));selection[[0,-1]]=False;selection[:,[0,-1]]=False
out=old.copy();out[selection]=e[selection]
# Keep native lichen at1–2pixels through composition;merge border lichen
# into neighboring original moss before pairing,avoiding the round1 wrap3px issue.
labels=np.argmin(((out.astype(float)[:,:,None]-pal[None,None].astype(float))**2).sum(3),2)
lichen=labels>=30;keep=small_lichen(lichen);edge=np.zeros((128,224),bool);edge[[0,-1]]=True;edge[:,[0,-1]]=True
removed=[]
for y,x in zip(*np.where((lichen&~keep)|(lichen&edge))):
 choices=[(xx,yy) for yy in range(max(0,y-4),min(128,y+5)) for xx in range(max(0,x-4),min(224,x+5)) if labels[yy,xx]<30]
 assert choices
 xx,yy=min(choices,key=lambda p:(p[0]-x)**2+(p[1]-y)**2);labels[y,x]=labels[yy,xx];removed.append([int(x),int(y),int(xx),int(yy)])
out=pal[labels];out[:,-1]=out[:,0];out[-1]=out[0]
(S/'06_lichen_edge_cleanup.json').write_text(json.dumps({'removed_into_adjacent_moss_xy_source_xy':removed,'method':'Remove only oversized or boundary gray lichen pixels by copying adjacent native moss labels before opposite-profile pairing;no new dots or uniform border.'},indent=2)+'\n')
labels=np.argmin(((out.astype(float)[:,:,None]-pal[None,None].astype(float))**2).sum(3),2)
newpal=calibrated(pal,labels);out=newpal[labels]
Image.fromarray(out).convert('RGBA').save(T/'moss_texture_01.png')
Image.fromarray((selection*255).astype('uint8')).save(S/'06_cross_selection_mask.png')
(S/'06_final_palette.json').write_text(json.dumps({'from':pal.tolist(),'to':newpal.tolist(),'method':'Palette-only correction to mean59,69,55/std11.5 while fixing the two neutral lichen colors.'},indent=2)+'\n')
(S/'06_assembly.json').write_text(json.dumps({'method':'Native old/edit pixel selection across irregular minimum-error cross. Opposite1px textured edge profiles paired, no flat border. No texture synthesis, blend, blur or art resizing.','edit_cleanup_rate_progress':progress,'edit_selected_pixels':int(selection.sum()),'left_cut':left.tolist(),'right_cut':right.tolist(),'top_cut':top.tolist(),'bottom_cut':bottom.tolist()},indent=2)+'\n')
whole3=np.tile(out,(3,3,1));Image.fromarray(whole3).save(Q/'moss_texture_repeat_3x3_1x.png');Image.fromarray(whole3).resize((1344,768),Image.Resampling.NEAREST).save(Q/'moss_texture_repeat_3x3_2x.png')
bare=whole3[:270,:480];Image.fromarray(bare).resize((960,540),Image.Resampling.NEAREST).save(Q/'moss_texture_fill_2x.png')
Image.fromarray(out).resize((1344,768),Image.Resampling.NEAREST).save(Q/'moss_texture_native_6x.png')
wrap=np.tile(out,(2,2,1));Image.fromarray(wrap[104:152,200:248]).resize((384,384),Image.Resampling.NEAREST).save(Q/'moss_texture_wrap_junction_8x.png')
# Full native-scale object comparison; the right108px strip is approved grass.
scene=Image.fromarray(bare).convert('RGBA');grass=np.array(Image.open(T/'grass_texture_01.png').convert('RGBA'));strip=Image.fromarray(np.tile(grass,(3,1,1))[:270,:108]);scene.alpha_composite(strip,(372,0))
placements=[('tombstone_upright_01',(104,156)),('tombstone_upright_02',(289,164)),('tombstone_small_01',(273,242))]
for name,foot in placements:
 for suffix in ['_base','']:
  im=Image.open(R/f'art/cemetery_v3/props/{name}{suffix}.png').convert('RGBA');scene.alpha_composite(im,(foot[0]-im.width//2,foot[1]-im.height))
hero=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');scene.alpha_composite(hero,(193-hero.width//2,188-hero.height))
scene.resize((960,540),Image.Resampling.NEAREST).save(Q/'moss_texture_with_props_2x.png')
Image.fromarray(np.concatenate([out,np.array(Image.open(T/'grass_texture_01.png').convert('RGB'))],axis=1)).resize((1344,384),Image.Resampling.NEAREST).save(Q/'moss_texture_vs_grass_3x.png')
checks={'status':'ROUND2_STOPPED_3X3_PATCH_REPETITION','size':[224,128],'alpha_values':[255],'colors':len(np.unique(out.reshape(-1,3),axis=0)),'mean_rgb':out.mean((0,1)).tolist(),'luma_standard_deviation':float((out@LUMA).std()),'luma_formula':'Rec709:0.2126R+0.7152G+0.0722B','horizontal_change':float(np.any(out[:,1:]!=out[:,:-1],2).mean()*100),'opposite_left_right_exact':bool(np.array_equal(out[:,0],out[:,-1])),'opposite_top_bottom_exact':bool(np.array_equal(out[0],out[-1])),'lichen_palette':newpal[30:].tolist(),'lichen_pixel_count':int((labels>=30).sum()),'lichen_max_component_8connected':max(map(len,groups(labels>=30))),'lichen_max_component_wrapped_8connected':max(map(len,groups(np.tile(labels>=30,(2,2))))),'native_bare_fill_size':[480,270],'qc_scale':2,'props_preview':'Static480x270 native-scale3tombstones+their original bases+hero;right108px strip is approved grass,hard comparison boundary not runtime terrain edge.','sha256':hashlib.sha256((T/'moss_texture_01.png').read_bytes()).hexdigest()}
lock=json.loads((S/'protected_approved_assets.json').read_text());checks['approved_asset_hashes_unchanged']=all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in lock.items());assert checks['approved_asset_hashes_unchanged']
assert checks['opposite_left_right_exact'] and checks['opposite_top_bottom_exact']
assert checks['lichen_max_component_wrapped_8connected']<=2
assert 25<=checks['colors']<=35 and 10<=checks['luma_standard_deviation']<=13
assert all(lo<=v<=hi for v,lo,hi in zip(checks['mean_rgb'],[56,66,52],[62,72,58]))
result=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(T/'moss_texture_01.png')],cwd=R,text=True,capture_output=True,check=True)
(Q/'moss_texture_pixel_check.txt').write_text(result.stdout);(Q/'moss_texture_verification.json').write_text(json.dumps(checks,indent=2)+'\n');print(checks);print(result.stdout)
