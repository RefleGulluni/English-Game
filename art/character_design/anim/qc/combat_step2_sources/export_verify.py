from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil,subprocess,sys,colorsys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-combat-step2-20261028');O=W/'staged';D=W/'delivery';P=json.loads((W/'parts_plan_before_compositing.json').read_text());pose=json.loads((W/'pose_records.json').read_text());L=np.array([.299,.587,.114]);timing={'hero':{},'skeleton':{}};results={}
def load(p):return np.array(Image.open(p).convert('RGBA'))
def rh(a):return hashlib.sha256(a.tobytes()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
exec((W/'check_draft.py').read_text().split('res={}')[0].split("defs=")[0] if False else 'pass')
def components(a):
 todo=set(zip(*np.where(a[:,:,3]>0)));sizes=[]
 while todo:
  q=[todo.pop()];count=0
  while q:
   y,x=q.pop();count+=1
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     p=(y+dy,x+dx)
     if p in todo:todo.remove(p);q.append(p)
  sizes.append(count)
 return sorted(sizes,reverse=True)
def gif(path,frames,ds,loop=False):
 colors=np.array(sorted(set(tuple(c) for a in frames for c in a[a[:,:,3]>0,:3])),np.uint8);assert len(colors)<255;flat=[0,0,0]+colors.flatten().tolist();flat += [0]*(768-len(flat));pp=[]
 for a in frames:
  ix=np.zeros(a.shape[:2],np.uint8)
  for j,c in enumerate(colors):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=j+1
  im=Image.fromarray(ix).convert('P');im.putpalette(flat);pp.append(im.resize((a.shape[1]*8,a.shape[0]*8),Image.Resampling.NEAREST))
 pp[0].save(path,save_all=True,append_images=pp[1:],duration=ds,transparency=0,disposal=2,optimize=False,**({'loop':0} if loop else {}))
 g=Image.open(path);assert g.n_frames==len(frames),(path,g.n_frames)
 for k,a in enumerate(frames):
  g.seek(k);b=np.array(g.convert('RGBA'));e=np.repeat(np.repeat(a,8,0),8,1);fg=e[:,:,3]>0;assert np.array_equal(b[:,:,3],e[:,:,3]) and np.array_equal(b[fg],e[fg]) and g.info['duration']==ds[k]

for d in sorted((O/'frames').iterdir()):
 n=d.name;kind='hero' if n.startswith('hero') else 'skeleton';direct='left' if 'left' in n else 'right';fw=160 if 'attack' in n else 96;dest=D/kind;Q=dest/'qc';Q.mkdir(parents=True,exist_ok=True);F=dest/'frames'/n;F.mkdir(parents=True,exist_ok=True)
 ref=R/('art/character_design/hero_B1_'+direct+'.png' if kind=='hero' else 'art/character_design/enemies/skeleton/skeleton_B_'+direct+'.png');m=load(ref);base=np.zeros((96,fw,4),np.uint8);off=(fw-96)//2;put=base.__setitem__;base[:,off:off+96]=m
 if kind=='hero':
  pals=[]
  for dr in ['front_straight','back','left','right']:
   a=load(R/'art/character_design'/f'hero_B1_{dr}.png');pals.extend(map(tuple,a[a[:,:,3]>0,:3]))
  allowed=set(pals)
 else:allowed=set(map(tuple,json.loads((R/'art/character_design/enemies/skeleton/anim/qc/v2_sources/palette.json').read_text())))
 frames=[load(p) for p in sorted(d.glob('*.png'))];assert len(frames)==P[n]['frames'];assert np.array_equal(frames[0],base) and np.array_equal(frames[-1],base);sheet=Image.new('RGBA',(len(frames)*fw,96));board=Image.new('RGBA',(4*(fw+8),((len(frames)+3)//4)*112),'#403d43');drw=ImageDraw.Draw(board);rs=[]
 for k,a in enumerate(frames):
  assert a.shape==(96,fw,4) and set(np.unique(a[:,:,3]))<={0,255};colors=set(map(tuple,a[a[:,:,3]>0,:3]));assert colors<=allowed,(n,k,colors-allowed)
  cyan=sum(1 for c in colors if 160<=colorsys.rgb_to_hsv(*(np.array(c)/255))[0]*360<=260 and colorsys.rgb_to_hsv(*(np.array(c)/255))[1]>=.35 and max(c)>.3*255);assert cyan==0
  yfoot=78 if kind=='hero' else 84;footmask=base[:,:,3]>0;footmask[:yfoot]=False;assert np.array_equal(a[footmask],base[footmask]),('foot overwritten',n,k)
  assert int(np.where(a[:,:,3]>0)[0].max())==95
  # Every standing neck pixel must remain filled after rigid movement; check complete upper-body shift.
  row=P[n];upper=(row.get('upper_dx',[0]*len(frames))[k],0) if kind=='hero' else (row['upper'][k] if 'upper' in row else ([0,1] if k==4 else [1,0] if k==5 else [0,0]))
  if n=='skeleton_B_attack_right_v2':
   # Only the two new frames use this check; inherited frames already have approved translations.
   checkneck=k in [4,5]
  else:checkneck=True
  if checkneck:
   yy,xx=np.where(m[15:22,39:52,3]>0);yy+=15;xx+=39;assert (a[yy+upper[1],xx+off+upper[0],3]==255).all(),('neck',n,k)
  cs=components(a)
  if 'dust' not in n:assert len(cs)==1,(n,k,cs)
  bands=[]
  for lo,hi in [(0,20),(20,45),(45,65),(65,96)]:
   b=a[lo:hi];v=base[lo:hi];rgb=b[b[:,:,3]>0,:3];vrgb=v[v[:,:,3]>0,:3];mean=float((rgb@L).mean());vm=float((vrgb@L).mean());delta=mean-vm;assert abs(delta)<=2,(n,k,lo,delta)
   bands.append({'y':[lo,hi-1],'mean_luma':mean,'standing_mean_luma':vm,'delta':delta,'highlight_gt170_pct':float(((rgb@L)>170).mean()*100),'standing_highlight_gt170_pct':float(((vrgb@L)>170).mean()*100)})
  out=F/f'{k+1:02}.png'
  if n=='skeleton_B_attack_right_v2' and k not in [4,5]:
   old=R/'art/character_design/enemies/skeleton/anim/frames/skeleton_B_attack_right'/f'{k+1:02}.png';assert np.array_equal(a,load(old));shutil.copy2(old,out)
  else:Image.fromarray(a).save(out)
  sheet.paste(Image.fromarray(a),(fw*k,0));x=k%4*(fw+8);y=k//4*112;board.alpha_composite(Image.fromarray(a),(x,y));drw.text((x+2,y+98),str(k+1),fill='white')
  rs.append({'frame':k+1,'rgba_sha256':rh(a),'file_sha256':sha(out),'colors':len(colors),'alpha_values':np.unique(a[:,:,3]).tolist(),'cyan_pixels':0,'lowest_y':95,'foot_source_rgba_exact':True,'components_sizes':cs,'neck_source_pixels_missing':0,'bands':bands,'changed_pixels_previous':int((a!=frames[k-1]).any(2).sum()) if k else 0})
 sheet.save(dest/(n+'.png'));assert np.array_equal(load(dest/(n+'.png'))[:,:fw],base);board.resize((board.width*4,board.height*4),Image.Resampling.NEAREST).save(Q/(n+'_contact_4x.png'));ds=P[n]['durations_ms'];gif(Q/(n+'_8x.gif'),frames,ds)
 event='release' if 'cast' in n else 'hit' if 'hit' in n or 'attack' in n else 'shed';eventf=P[n].get(event+'_frame',2 if event=='shed' else 1);t={'frames':len(frames),'frame_size':[fw,96],'anchor':[fw//2,96],'durations_ms':ds,'duration_ms':sum(ds),'loop':False,'sprite_sheet':n+'.png',event+'_frame':eventf,event+'_frame_index':eventf-1,'key_frame':{'type':event,'frame':eventf,'frame_index':eventf-1,'time_ms':sum(ds[:eventf-1])},'frame_numbering':'frame is1-based; frame_index is0-based','qa':'qc/combat_step2_QA.md'}
 if 'attack' in n:
  rr=pose[n][0] if n.endswith('v2') else pose[n][eventf-1];tip=rr['tip'];t['hit_tip']=tip;t['hit_tip_offset_from_anchor']=[tip[0]-80,tip[1]-96]
  if n.endswith('v2'):t.update(expected_program_advance_px_range=[60,80],comparison_of='skeleton_B_attack_right',modified_frames=[5,6])
  else:t['expected_program_advance_px']=40
 timing[kind][n]=t
 result={'name':n,'standard_file':str(ref.relative_to(R)),'standard_png_sha256_before':sha(ref),'standard_rgba_sha256':rh(m),'padded_standard_rgba_sha256':rh(base),'first_frame_rgba_sha256':rh(frames[0]),'last_frame_rgba_sha256':rh(frames[-1]),'first_last_exact_standard':True,'frames':rs,'timing':t,'gifs_decoded_rgba_and_timing_exact':True}
 if n.endswith('v2'):
  eq=[]
  for k,a in enumerate(frames):eq.append(np.array_equal(a,load(R/f'art/character_design/enemies/skeleton/anim/frames/skeleton_B_attack_right/{k+1:02}.png')))
  assert [k+1 for k,v in enumerate(eq) if not v]==[5,6];result['exact_original_frames']=[k+1 for k,v in enumerate(eq) if v];result['forearm_measurements']=pose[n]
 (Q/(n+'_metrics.json')).write_text(json.dumps(result,indent=2)+'\n');results[n]=result
 run=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(dest/(n+'.png')),*map(str,sorted(F.glob('*.png')))],capture_output=True,text=True,cwd=R,check=True);(Q/(n+'_pixel_check.txt')).write_text(run.stdout)
# Matched side-by-side preview; only the new side is reauthored.
orig=[load(R/f'art/character_design/enemies/skeleton/anim/frames/skeleton_B_attack_right/{k:02}.png') for k in range(1,10)];new=[load(D/f'skeleton/frames/skeleton_B_attack_right_v2/{k:02}.png') for k in range(1,10)];combo=[]
for a,b in zip(orig,new):
 im=Image.new('RGBA',(336,112),'#403d43');im.alpha_composite(Image.fromarray(a),(0,12));im.alpha_composite(Image.fromarray(b),(176,12));dr=ImageDraw.Draw(im);dr.text((4,1),'V1 accepted / long',fill='white');dr.text((180,1),'V2 short / diagonal',fill='white');combo.append(np.array(im))
gif(D/'skeleton/qc/skeleton_B_attack_right_v1_v2_compare_8x.gif',combo,P['skeleton_B_attack_right_v2']['durations_ms'])
(W/'results.json').write_text(json.dumps(results,indent=2));(W/'timing_entries.json').write_text(json.dumps(timing,indent=2))
print(json.dumps({n:{'frames':len(v['frames']),'ms':v['timing']['duration_ms'],'max_band_delta':max(abs(b['delta']) for r in v['frames'] for b in r['bands']),'max_frame_delta':max(r['changed_pixels_previous'] for r in v['frames']),'key_frame':v['timing']['key_frame'],'tip_offset':v['timing'].get('hit_tip_offset_from_anchor')} for n,v in results.items()},indent=2))
