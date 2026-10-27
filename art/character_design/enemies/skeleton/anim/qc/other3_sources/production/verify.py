from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,subprocess,sys
exec(open('/tmp/english-game-skeleton-other3-20261027/check_components.py').read().split("if __name__")[0])
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-other3-20261027');O=W/'staged';Q=O/'qc';V=Q/'other3_sources';plans=json.loads((V/'parts_plan_before_drawing.json').read_text());refs=json.loads((V/'foot_references.json').read_text());records=json.loads((V/'frame_records.json').read_text());timings=json.loads((V/'timing_entries.json').read_text());pal={tuple(c) for c in json.loads((A/'qc/v2_sources/palette.json').read_text())}
load=lambda p:np.array(Image.open(p).convert('RGBA'))
rh=lambda a:hashlib.sha256(a.tobytes()).hexdigest()
def grey(a):
 fg=a[:,:,3]>0;lum=a[:,:,:3]@np.array([.299,.587,.114]);b=[]
 for lo,hi in [(0,20),(20,45),(45,65),(65,96)]:z=lum[lo:hi][fg[lo:hi]];b.append({'mean':float(z.mean()),'highlight_gt170_fraction':float((z>170).mean())})
 return {'bands':b,'whole_mean':float(lum[fg].mean())}
def density(a):
 fg=a[:,:,3]>0;nb=fg[:,:-1]&fg[:,1:];change=(a[:,:-1,:3]!=a[:,1:,:3]).any(2);return float((nb&change).sum()/nb.sum()*100)
results={};standards={};world=[]
for direction,pl in plans.items():
 master=load(Path(pl['source']));base=grey(master);standards[direction]={'rgba_sha256':rh(master),'brightness':base}
 upper=load(V/'standing_parts'/direction/'upper.png');pelvis=load(V/'standing_parts'/direction/'pelvis.png')
 for kind,name in [('walk',f'skeleton_B_walk_{direction}_v5'),('start',f'skeleton_B_walk_start_{direction}'),('stop',f'skeleton_B_walk_stop_{direction}')]:
  rs=records[name];fs=[load(O/'frames'/name/f'{k+1:02}.png') for k in range(len(rs))];rr=[]
  assert Image.open(O/(name+'.png')).size==(96*len(fs),96)
  if kind=='start':assert np.array_equal(fs[0],master)
  if kind=='stop':assert np.array_equal(fs[-1],master)
  for k,(a,r) in enumerate(zip(fs,rs)):
   assert a.shape==(96,96,4) and set(np.unique(a[:,:,3]))<={0,255};colors={tuple(c) for c in a[a[:,:,3]>0,:3]};assert colors<=pal
   comps=components(a);assert len(comps)==1,(name,k,'detached',list(map(len,comps)))
   dy=0 if r.get('exact_standard') else r['upper_offset'][1]
   # Actual visible source registration, not merely an abstract component hash.
   x0,x1=40,56;y1=20 if direction=='left' else 23
   assert np.array_equal(a[dy:y1+dy,x0:x1],master[:y1,x0:x1]),(name,k,'visible head/neck changed')
   srcproof={}
   if not r.get('exact_standard'):
    for key,p,offset in [('upper_rigid',upper,r['upper_offset']),('pelvis_rigid',pelvis,r['pelvis_offset'])]:
     layer=load(V/'layers'/name/f'{k+1:02}'/(key+'.png'));ys,xs=np.where(layer[:,:,3]>0);undo=np.zeros_like(layer);undo[ys-offset[1],xs-offset[0]]=layer[ys,xs];assert np.array_equal(undo,p);srcproof[key]=rh(undo)
   fg=a[:,:,3]>0;bottom=int(np.where(fg)[0].max());assert bottom==95,(name,k,bottom)
   g=grey(a);footdata={}
   if not r.get('exact_standard'):
    for role in ['left','right']:
     leg=load(V/'layers'/name/f'{k+1:02}'/('leg_'+role+'.png'));b=int(np.where(leg[:,:,3]>0)[0].max());lift=r['legs'][role]['lift'];assert b==95-lift
     footdata[role]={'bottom_y':b,'lift_px':lift,'support':r['legs'][role]['support']}
     if kind=='walk' and direction=='left' and lift==0:
      target=refs[direction][role]['toe_min']+r['legs'][role]['foot_dx'];worldx=target-5*k
      source=load(V/'standing_parts'/direction/('leg_'+role+'.png'));sy=refs[direction][role]['bottom'];sourcex=refs[direction][role]['toe_min'];assert np.array_equal(a[95,target],source[sy,sourcex]),(name,k,role,'support witness occluded')
      footdata[role].update({'toe_canvas_x':target,'world_origin_x':-5*k,'toe_world_x':worldx});world.append({'frame':k+1,'role':role,'canvas_x':target,'origin_x':-5*k,'world_x':worldx,'sole_visible':True})
   rr.append({'frame':k+1,'rgba_sha256':rh(a),'colors':len(colors),'neighbor_color_change_pct':density(a),'bottom_y':bottom,'upper_offset':[0,dy],'head_neck_visible_crop_equal':True,'connected_components':len(comps),'source_rigid_sha256':srcproof,'feet':footdata,'brightness':g,'band_mean_delta':[round(g['bands'][j]['mean']-base['bands'][j]['mean'],4) for j in range(4)],'whole_mean_delta':round(g['whole_mean']-base['whole_mean'],4),'pixel_delta_from_previous':None if k==0 else int((a!=fs[k-1]).any(2).sum())})
  gif=Image.open(Q/(name+'_8x.gif'));assert gif.n_frames==len(fs),(name,gif.n_frames)
  for k,a in enumerate(fs):
   gif.seek(k);ga=np.array(gif.convert('RGBA'));expected=np.repeat(np.repeat(a,8,axis=0),8,axis=1);assert np.array_equal(ga[:,:,3],expected[:,:,3]);assert np.array_equal(ga[ga[:,:,3]>0],expected[expected[:,:,3]>0]);assert gif.info['duration']==100
  results[name]={'direction':direction,'kind':kind,'frames':rr,'loop_boundary_pixel_changes':int((fs[0]!=fs[-1]).any(2).sum()) if kind=='walk' else None,'gif_exact_rgba_nearest8x':True,'endpoint_exact_standing':True if kind!='walk' else None}
  (Q/(name+'_metrics.json')).write_text(json.dumps(results[name],ensure_ascii=False,indent=2))
for role in ['left','right']:
 xs=[r['world_x'] for r in world if r['role']==role];assert len(set(xs))==1
# Re-decode combined previews as well; animation frame count and duration must match.
transitions={}
for d in plans:
 names=[f'skeleton_B_walk_start_{d}',f'skeleton_B_walk_{d}_v5',f'skeleton_B_walk_stop_{d}'];ss=[[load(p) for p in sorted((O/'frames'/n).glob('*.png'))] for n in names];seq=ss[0]+ss[1]*2+ss[2];g=Image.open(Q/f'skeleton_B_{d}_start_walk_stop_8x.gif');assert g.n_frames==len(seq)
 for k,a in enumerate(seq):
  g.seek(k);b=np.array(g.convert('RGBA'));a=np.repeat(np.repeat(a,8,0),8,1);assert np.array_equal(b[:,:,3],a[:,:,3]);assert np.array_equal(b[b[:,:,3]>0],a[a[:,:,3]>0])
 transitions[d]={'start_to_loop1':int((ss[0][-1]!=ss[1][0]).any(2).sum()),'loop8_to_stop1':int((ss[1][-1]!=ss[2][0]).any(2).sum()),'all_sequence_deltas':[int((seq[k]!=seq[k-1]).any(2).sum()) for k in range(1,len(seq))]}
report={'standards':standards,'actions':results,'left_world_support':world,'transitions':transitions,'all_frames':42,'actual_visible_head_neck_invariant':True,'old_walk_frames_read':False}
(Q/'skeleton_B_other3_v5_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
# Joint details: actual pixels, nearest only. Head-neck and waist/arm junction shown for every loop frame.
for d in plans:
 b=Image.new('RGBA',(8*56,2*56),'#46424A');dr=ImageDraw.Draw(b)
 for k in range(8):
  a=Image.open(O/'frames'/f'skeleton_B_walk_{d}_v5'/f'{k+1:02}.png')
  for row,box in enumerate([(32,0,72,28),(22,30,76,64)]):b.alpha_composite(a.crop(box),(k*56+1,row*56));dr.text((k*56+2,row*56+39),str(k+1),fill='white')
 b.resize((b.width*8,b.height*8),Image.Resampling.NEAREST).save(Q/f'skeleton_B_{d}_v5_joints_8x.png')
# Authoritative repository pixel checker, invoked for every delivered native frame.
files=[str(p) for p in sorted((O/'frames').glob('*/*.png'))];p=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1.png'),*files],capture_output=True,text=True);assert p.returncode==0;(V/'pixel_check.txt').write_text(p.stdout)
print('PASS: 42 native frames; 9 GIFs and 3 combined GIFs decoded; one connected body each; visible head/neck preserved; rigid upper/pelvis exact; endpoints exact; foot contacts and left world lock verified.')
print('World:',world)
print('Transitions:',{d:{'entry':v['start_to_loop1'],'exit':v['loop8_to_stop1'],'max':max(v['all_sequence_deltas'])} for d,v in transitions.items()})
