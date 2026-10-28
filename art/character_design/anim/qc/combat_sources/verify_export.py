from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,subprocess,sys,colorsys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-combat-trial-20261028');O=W/'staged';D=W/'delivery';H=D/'hero';S=D/'skeleton';L=np.array([.299,.587,.114]);plan=json.loads((W/'plan.json').read_text());results={};timing={}
def load(p):return np.array(Image.open(p).convert('RGBA'))
def rh(a):return hashlib.sha256(a.tobytes()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def components(a):
 todo=set(zip(*np.where(a[:,:,3]>0)));sizes=[]
 while todo:
  q=[todo.pop()];k=0
  while q:
   y,x=q.pop();k+=1
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     pt=(y+dy,x+dx)
     if pt in todo:todo.remove(pt);q.append(pt)
  sizes.append(k)
 return sorted(sizes,reverse=True)
for kind,name,ref,fw,ds,event,eventf in [
 ('hero','hero_B1_cast_right','art/character_design/hero_B1_right.png',96,[90,100,100,120,100,90,80,80],'release',4),
 ('skeleton','skeleton_B_attack_right','art/character_design/enemies/skeleton/skeleton_B_right.png',160,[100,130,150,140,60,70,140,120,100],'hit',5)]:
 dest=H if kind=='hero' else S;Q=dest/'qc';Q.mkdir(parents=True,exist_ok=True);F=dest/'frames'/name;F.mkdir(parents=True,exist_ok=True);src=Q/'combat_sources';src.mkdir(exist_ok=True)
 m=load(R/ref);base=np.zeros((96,fw,4),np.uint8);base[:,(fw-96)//2:(fw+96)//2]=m
 if kind=='hero':
  pals=[]
  for direction in ['front_straight','back','left','right']:
   a=load(R/'art/character_design'/f'hero_B1_{direction}.png');pals.extend(map(tuple,a[a[:,:,3]>0,:3]))
 else:pals=map(tuple,np.array(json.loads((R/'art/character_design/enemies/skeleton/anim/qc/v2_sources/palette.json').read_text())))
 allowed=set(pals);frames=[load(p) for p in sorted((O/'frames'/name).glob('*.png'))];assert np.array_equal(frames[0],base) and np.array_equal(frames[-1],base);checks=[]
 strip=Image.new('RGBA',(fw*len(frames),96));board=Image.new('RGBA',(4*(fw+8),((len(frames)+3)//4)*112),'#403d43');dr=ImageDraw.Draw(board)
 for k,a in enumerate(frames):
  assert set(np.unique(a[:,:,3]))<={0,255};used=set(map(tuple,a[a[:,:,3]>0,:3]));assert used<=allowed
  cyan=sum(1 for c in a[a[:,:,3]>0,:3] if 160<=colorsys.rgb_to_hsv(*(c/255))[0]*360<=260 and colorsys.rgb_to_hsv(*(c/255))[1]>=.35 and max(c)>.3*255);assert cyan==0
  y0=78 if kind=='hero' else 84;assert np.array_equal(a[y0:],base[y0:]);assert np.where(a[:,:,3]>0)[0].max()==95
  cs=components(a);assert len(cs)==1,(kind,k,cs)
  bands=[]
  for lo,hi in [(0,20),(20,45),(45,65),(65,96)]:
   b=a[lo:hi];b=b[b[:,:,3]>0,:3];v=base[lo:hi];v=v[v[:,:,3]>0,:3];mean=float((b@L).mean());refmean=float((v@L).mean());diff=mean-refmean;assert abs(diff)<=2,(kind,k,lo,diff)
   bands.append({'y':[lo,hi-1],'mean_luma':mean,'standing_mean_luma':refmean,'delta':diff,'highlight_over170_pct':float(((b@L)>170).mean()*100),'standing_highlight_over170_pct':float(((v@L)>170).mean()*100)})
  rs={'frame':k+1,'rgba_sha256':rh(a),'alpha_values':np.unique(a[:,:,3]).tolist(),'colors':len(used),'cyan_pixels':cyan,'connected_components_sizes':cs,'foot_pixels_exact':True,'lowest_y':95,'changed_pixels_from_previous':int((a!=frames[k-1]).any(2).sum()) if k else 0,'bands':bands};checks.append(rs)
  Image.fromarray(a).save(F/f'{k+1:02}.png');strip.paste(Image.fromarray(a),(fw*k,0));x=k%4*(fw+8);y=k//4*112;board.alpha_composite(Image.fromarray(a),(x,y));dr.text((x+2,y+98),str(k+1),fill='white')
 strip.save(dest/(name+'.png'));assert np.array_equal(load(dest/(name+'.png'))[:,:fw],base);board.resize((board.width*4,board.height*4),Image.Resampling.NEAREST).save(Q/(name+'_contact_4x.png'))
 # Exact indexed GIF, no adaptive palette or transparency bleeding. One-shot matches runtime.
 pal=np.array(sorted(set(tuple(c) for a in frames for c in a[a[:,:,3]>0,:3])),np.uint8);assert len(pal)<255;flat=[0,0,0]+pal.flatten().tolist();flat+=[0]*(768-len(flat));pp=[]
 for a in frames:
  ix=np.zeros(a.shape[:2],np.uint8)
  for j,c in enumerate(pal):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=j+1
  im=Image.fromarray(ix).convert('P');im.putpalette(flat);pp.append(im.resize((fw*8,768),Image.Resampling.NEAREST))
 pp[0].save(Q/(name+'_8x.gif'),save_all=True,append_images=pp[1:],duration=ds,transparency=0,disposal=2,optimize=False)
 g=Image.open(Q/(name+'_8x.gif'));assert g.n_frames==len(frames),(kind,g.n_frames)
 for k,a in enumerate(frames):
  g.seek(k);b=np.array(g.convert('RGBA'));e=np.repeat(np.repeat(a,8,0),8,1);fg=e[:,:,3]>0;assert np.array_equal(b[:,:,3],e[:,:,3]) and np.array_equal(b[fg],e[fg]) and g.info['duration']==ds[k]
 t={'frames':len(frames),'frame_size':[fw,96],'anchor':[fw//2,96],'durations_ms':ds,'duration_ms':sum(ds),'loop':False,'sprite_sheet':name+'.png',event+'_frame':eventf,event+'_frame_index':eventf-1,'key_frame':{'type':event,'frame':eventf,'frame_index':eventf-1,'time_ms':sum(ds[:eventf-1])},'frame_numbering':'frame fields are1-based; *_index fields are0-based'}
 if kind=='skeleton':
  rr=json.loads((W/'skeleton_pose_records.json').read_text());tip=rr[eventf-1]['arm_tip'];t.update(hit_tip=tip,hit_tip_offset_from_anchor=[tip[0]-80,tip[1]-96],expected_program_advance_px=40)
  results[kind]={'name':name,'reference':ref,'standard_file_sha256':sha(R/ref),'standard_rgba_sha256':rh(m),'padded_standard_rgba_sha256':rh(base),'first_frame_rgba_sha256':rh(frames[0]),'last_frame_rgba_sha256':rh(frames[-1]),'first_last_exact':True,'frames':checks,'hit_tip':tip,'hit_reach_px':tip[0]-80,'timing':t}
 else:results[kind]={'name':name,'reference':ref,'standard_file_sha256':sha(R/ref),'standard_rgba_sha256':rh(m),'first_frame_rgba_sha256':rh(frames[0]),'last_frame_rgba_sha256':rh(frames[-1]),'first_last_exact':True,'frames':checks,'timing':t}
 timing[kind]={name:t};(Q/(name+'_metrics.json')).write_text(json.dumps(results[kind],ensure_ascii=False,indent=2)+'\n')
 for fn in [kind+'_generated.png',kind+'_prompt.txt',kind+'_grid.json',kind+'_gridcheck.png',kind+'_restored.png',kind+'_anchor4x.png',kind+'_ref6x.png',kind+'_pose_records.json','plan.json','recover.py','build.py','tone.py','tone_records.json','cloth_tone_records.json','verify_export.py']:
  if (W/fn).exists():shutil.copy2(W/fn,src/fn)
 if kind=='skeleton':
  for fn in ['hit_generated.png','hit_restored.png','hit_grid.json','skeleton_hit_prompt.txt','recover_hit.py']:shutil.copy2(W/fn,src/fn)
  shutil.copytree(O/'qc/combat_sources/skeleton_layers',src/'skeleton_layers',dirs_exist_ok=True)
 else:shutil.copytree(O/'qc/combat_sources/hero_layers',src/'hero_layers',dirs_exist_ok=True)
 paths=sorted(F.glob('*.png'));result=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),*map(str,paths)],capture_output=True,text=True,cwd=R,check=True);(Q/(name+'_pixel_check.txt')).write_text(result.stdout)
(W/'final_results.json').write_text(json.dumps(results,indent=2));(W/'timing_entries.json').write_text(json.dumps(timing,indent=2));print({k:{'frames':len(v['frames']),'duration':v['timing']['duration_ms'],'event':v['timing']['key_frame'],'max_band_delta':max(abs(b['delta']) for f in v['frames'] for b in f['bands']),'max_frame_delta':max(f['changed_pixels_from_previous'] for f in v['frames']),'tip':v.get('hit_tip')} for k,v in results.items()})
