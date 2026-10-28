from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,subprocess,sys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-collapse-rb-213-20261028');O=W/'staged';Q=O/'qc';V=Q/'collapse_rb_sources';load=lambda p:np.array(Image.open(p).convert('RGBA'));rh=lambda a:hashlib.sha256(a.tobytes()).hexdigest();records=json.loads((V/'frame_records.json').read_text());timings=json.loads((V/'timing_entries.json').read_text());pal={tuple(c) for c in json.loads((A/'qc/v2_sources/palette.json').read_text())};front=load(A/'skeleton_B_collapse_front.png');canonical=front[:,-96:];rem=np.zeros_like(canonical);rem[48:]=load(S/'skeleton_B_remains.png');assert np.array_equal(canonical,rem);left=load(A/'skeleton_B_collapse_left.png');assert np.array_equal(canonical,left[:,-96:]);results={}
for direct in ['right','back']:
 name='skeleton_B_collapse_'+direct;fs=[load(p) for p in sorted((O/'frames'/name).glob('*.png'))];master=load(S/f'skeleton_B_{direct}.png');assert len(fs)==12;assert Image.open(O/(name+'.png')).size==(1152,96);assert np.array_equal(fs[0],master);assert np.array_equal(fs[-1],canonical);rr=[]
 board=Image.new('RGBA',(4*112,3*116),'#403D43');draw=ImageDraw.Draw(board)
 for k,a in enumerate(fs):
  assert a.shape==(96,96,4);assert set(np.unique(a[:,:,3]))<={0,255};fg=a[:,:,3]>0;colors={tuple(c) for c in a[fg,:3]};assert colors<=pal;bottom=int(np.where(fg)[0].max());assert bottom==95,(direct,k,bottom)
  body=load(V/direct/'layers'/f'{k+1:02}'/'body_no_skull.png');head=load(V/direct/'layers'/f'{k+1:02}'/'single_skull.png');mask=head[:,:,3]>0;assert mask.any();rebuilt=body.copy();rebuilt[mask]=head[mask];assert np.array_equal(rebuilt,a);assert np.array_equal(a[mask],head[mask])
  ys,xs=np.where(mask);bbox=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1];center=[round((bbox[0]+bbox[2]-1)/2,1),round((bbox[1]+bbox[3]-1)/2,1)];neighbor=fg[:,:-1]&fg[:,1:];change=(a[:,:-1,:3]!=a[:,1:,:3]).any(2);own=records[direct][k].get('active_bone_groups',{n:'standing' for n in ['skull','shoulder_chest','pelvis','arms_hands','legs_feet','shroud']});assert len(own)==6
  r={'frame':k+1,'duration_ms':timings[name]['durations_ms'][k],'rgba_sha256':rh(a),'colors':len(colors),'neighbor_change_pct':round(float((neighbor&change).sum()/neighbor.sum()*100),4),'alpha_values':[int(c) for c in np.unique(a[:,:,3])],'new_colors':0,'bottom_y':bottom,'one_explicit_skull_layer':True,'head_plus_headless_body_equals_final':True,'head_bbox':bbox,'head_center':center,'bone_group_ownership':own,'pixel_changes_from_previous':None if k==0 else int((a!=fs[k-1]).any(2).sum())};rr.append(r)
  x=k%4*112+8;y=k//4*116;board.alpha_composite(Image.fromarray(a),(x,y));x0,y0,x1,y1=bbox;draw.rectangle((x+x0-1,y+y0-1,x+x1,y+y1),outline='#EAB788');draw.text((x,y+98),f'{k+1} ONE SKULL',fill='#FFE1BE')
 board.resize((1792,1392),Image.Resampling.NEAREST).save(Q/(name+'_skull_track_4x.png'))
 g=Image.open(Q/(name+'_8x.gif'));assert g.n_frames==12
 for k,a in enumerate(fs):
  g.seek(k);decoded=np.array(g.convert('RGBA'));expected=np.repeat(np.repeat(a,8,0),8,1);assert np.array_equal(decoded[:,:,3],expected[:,:,3]);assert np.array_equal(decoded[decoded[:,:,3]>0],expected[expected[:,:,3]>0]);assert g.info['duration']==timings[name]['durations_ms'][k]
 # Pose/destination map, numbers refer to anatomy groups, not independent claims for every occluded tiny bone.
 b=Image.new('RGBA',(440,140),'#403D43');d=ImageDraw.Draw(b)
 for x,a in [(8,fs[0]),(162,fs[4]),(326,fs[-1])]:b.alpha_composite(Image.fromarray(a),(x,0))
 sp=[(50,8),(37,13),(49,29),(49,45),(56,66),(42,77),(32,51)] if direct=='right' else [(48,7),(59,20),(47,28),(48,45),(56,45),(40,78),(28,51)]
 ep=[(73,76),(22,71),(49,70),(44,85),(43,80),(50,92),(22,87)];cols=['#EFBB83','#D29B79','#D5C9AB','#BF9A85','#B7B28C','#BAA78F','#D6BD9A']
 for i,(p,e,c) in enumerate(zip(sp,ep,cols)):
  for ox,point in [(8,p),(326,e)]:
   x,y=ox+point[0],point[1];d.ellipse((x-3,y-3,x+3,y+3),fill='#302C31',outline=c);d.text((x-1,y-2),str(i+1),fill=c)
  d.line((8+p[0]+4,p[1],135,p[1]),fill=c);d.line((290,e[1],326+e[0]-4,e[1]),fill=c)
 d.text((8,101),'STANDING '+direct.upper(),fill='white');d.text((162,101),'FALLING POSE 5',fill='white');d.text((326,101),'SAME HEAP',fill='white');d.text((8,116),'1 skull / 2 pinned shoulder / 3 ribs+spine / 4 pelvis (hidden)',fill='#E9D7C5');d.text((8,127),'5 shroud / 6 long bones+feet / 7 forearms+hands',fill='#E9D7C5');b.resize((1760,560),Image.Resampling.NEAREST).save(Q/(name+'_map.png'))
 result={'name':name,'spec':'21.3','frame_size':[96,96],'anchor':[48,96],'frames':rr,'total_ms':sum(timings[name]['durations_ms']),'first_equals_direction_standard':True,'last_equals_front_final':True,'last_equals_left_final':True,'last_equals_remains_pasted_0_48':True,'first_rgba_sha256':rh(master),'last_rgba_sha256':rh(canonical),'gif_exact_nearest8x_decoded':True,'independent_generation':str(V/direct/'generated_early_fall.png'),'mirror_or_raster_rotation_used':False,'anatomical_count_validation':'Explicit single skull/headless-body layers + per-frame visual review and bone-group handoff ledger; not an automatic tiny-bone anatomical detector.'};results[direct]=result;(Q/(name+'_metrics.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2))
 # Major-bone ownership appears once in each column. Standing form is removed before ground form appears.
 lines=['# '+direct+'：逐帧骨组归属','','每列只允许一个在场形态。第8帧是上身/手臂落地换面：空中组先撤掉，再绘制骨堆组。裹尸布上段与下摆是同一块布的不同部分。','','|帧|头骨|肩/胸/脊柱|骨盆|手臂/手|腿/脚|布|','|---|---|---|---|---|---|---|']
 for f in rr:
  own=f['bone_group_ownership'];lines.append('|'+str(f['frame'])+'|'+'|'.join(own[n] for n in ['skull','shoulder_chest','pelvis','arms_hands','legs_feet','shroud'])+'|')
 (V/direct/'bone_group_handoff.md').write_text('\n'.join(lines),encoding='utf8')
 # Repository pixel checker on all twelve actual native files.
 p=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(R/'art/character_design/hero_B1.png'),*[str(p) for p in sorted((O/'frames'/name).glob('*.png'))]],capture_output=True,text=True);assert p.returncode==0;(V/direct/'pixel_check.txt').write_text(p.stdout)
(V/'verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('PASS: 24 frames, two exact standing starts and canonical endpoints, palette/alpha/anchor, layered reconstruction, both 12-frame GIFs decoded at native RGBA nearest8x.')
for d,v in results.items():print(d,'head centers',[f['head_center'] for f in v['frames']],'colors',min(f['colors'] for f in v['frames']),max(f['colors'] for f in v['frames']))
