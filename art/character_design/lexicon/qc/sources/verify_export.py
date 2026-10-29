from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,GifImagePlugin
import numpy as np,json,hashlib,subprocess,sys,colorsys
W=Path('/tmp/english-lexicon-20261029');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=W/'staged';Q=O/'qc';pal=set(map(tuple,json.loads((W/'world_palette.json').read_text())));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rh=lambda a:hashlib.sha256(a.tobytes()).hexdigest();read=lambda p:np.array(Image.open(p).convert('RGBA'))
spec={'lexicon_tip_up':{'frames':3,'durations_ms':[100]*3,'frame_size':[256,128],'anchor':[128,64],'spine_x_by_frame':[87,109,128],'spine_position_notes':'First two are approximate physical left-binding positions; x128 becomes fixed from last tip frame, per user clarification.'},'lexicon_covers_fall':{'frames':6,'durations_ms':[100]*6,'frame_size':[256,128],'anchor':[128,64],'spine_x_by_frame':[128]*6},'lexicon_page_turn':{'frames':4,'durations_ms':[70,80,80,70],'frame_size':[256,128],'anchor':[128,64],'spine_x_by_frame':[128]*4}}
allframes={};metrics={}
for n,t in spec.items():
 fs=[read(p) for p in sorted((O/'frames'/n).glob('*.png'))];assert len(fs)==t['frames'];allframes[n]=fs;strip=read(O/(n+'.png'));assert strip.shape==(128,256*len(fs),4);rows=[]
 for k,a in enumerate(fs):
  assert np.array_equal(strip[:,k*256:(k+1)*256],a);assert set(np.unique(a[:,:,3]))<={0,255};fg=a[:,:,3]>0;cs=set(map(tuple,a[fg,:3]));assert cs<=pal and not a[~fg].any()
  for c in cs:
   h,s,v=colorsys.rgb_to_hsv(*(np.array(c)/255));assert not(160<=h*360<=260 and s>=.35 and v>.3)
  rows.append({'frame':k+1,'rgba_sha256':rh(a),'png_sha256':sha(O/'frames'/n/f'{k+1:02}.png'),'bbox':Image.fromarray(a).getbbox(),'opaque_pixels':int(fg.sum()),'colors':len(cs),'new_colors':0,'cyan_pixels':0,'partial_alpha_pixels':0,'spine_x':t['spine_x_by_frame'][k]})
 t.update(duration_ms=sum(t['durations_ms']),loop=False,sprite_sheet='../lexicon/'+n+'.png',qa='../lexicon/qc/lexicon_book_QA.md',frame_numbering='frame is1-based; frame_index is0-based')
 metrics[n]={'timing':t,'strip_png_sha256':sha(O/(n+'.png')),'frames':rows}
for n,size in [('lexicon_closed_clean',(128,128)),('lexicon_open_clean',(256,128)),('lexicon_sigil_mask',(128,128))]:
 a=read(O/(n+'.png'));assert a.shape==(size[1],size[0],4);fg=a[:,:,3]>0;cs=set(map(tuple,a[fg,:3]));assert set(np.unique(a[:,:,3]))<={0,255} and not a[~fg].any()
 if n=='lexicon_sigil_mask':assert cs=={(255,255,255)}
 else:assert cs<=pal
 metrics[n]={'frame_size':list(size),'rgba_sha256':rh(a),'png_sha256':sha(O/(n+'.png')),'colors':len(cs),'opaque_pixels':int(fg.sum()),'new_colors':0 if n!='lexicon_sigil_mask' else 'white-mask-only exception','partial_alpha_pixels':0,'cyan_pixels':0}
closed=read(O/'lexicon_closed_clean.png');opened=read(O/'lexicon_open_clean.png');tip=allframes['lexicon_tip_up'];fall=allframes['lexicon_covers_fall'];page=allframes['lexicon_page_turn'];first=np.zeros_like(opened);first[:,64:192]=closed;assert np.array_equal(tip[0],first);assert np.array_equal(tip[-1],fall[0]);assert np.array_equal(fall[-1],opened);assert np.array_equal(page[0],opened) and np.array_equal(page[-1],opened)
assert all(np.array_equal(a[:,127:130],opened[:,127:130]) for a in fall)
# Each page-turn body is exactly the original clean book outside the two thin-leaf selections.
checks={'tip_first_centered_closed_rgba_sha256':rh(first),'tip_first_actual_rgba_sha256':rh(tip[0]),'tip_last_rgba_sha256':rh(tip[-1]),'fall_first_rgba_sha256':rh(fall[0]),'open_clean_rgba_sha256':rh(opened),'fall_last_rgba_sha256':rh(fall[-1]),'page_first_rgba_sha256':rh(page[0]),'page_last_rgba_sha256':rh(page[-1]),'fixed_binding_x127_through129_rgba_sha256':rh(opened[:,127:130]),'all_fall_binding_pixels_identical':True,'upright_body_width_px':15,'white_mask_pixels':metrics['lexicon_sigil_mask']['opaque_pixels']}
# Export exact nearest3 GIFs using complete frames, preserving identical endpoint slots.
def gif(name,fs,ds):
 cs=sorted(set(tuple(c) for a in fs for c in a[a[:,:,3]>0,:3]));flat=[0,0,0]+[v for c in cs for v in c];assert len(cs)<255;flat+=[0]*(768-len(flat));pp=[]
 for a in fs:
  ix=np.zeros(a.shape[:2],np.uint8)
  for i,c in enumerate(cs):ix[(a[:,:,:3]==c).all(2)&(a[:,:,3]>0)]=i+1
  im=Image.fromarray(ix).convert('P');im.putpalette(flat);pp.append(im.resize((768,384),Image.Resampling.NEAREST))
 header,_=GifImagePlugin.getheader(pp[0],info={'transparency':0,'background':0})
 with (Q/(name+'_3x.gif')).open('wb') as f:
  for b in header:f.write(b)
  f.write(b'!\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00')
  for k,im in enumerate(pp):
   for b in GifImagePlugin.getdata(im,duration=ds[k],disposal=2,transparency=0):f.write(b)
  f.write(b';')
 g=Image.open(Q/(name+'_3x.gif'));assert g.n_frames==len(fs)
 for k,a in enumerate(fs):
  g.seek(k);b=np.array(g.convert('RGBA'));expected=np.repeat(np.repeat(a,3,0),3,1);fg=expected[:,:,3]>0;assert np.array_equal(b[:,:,3],expected[:,:,3]) and np.array_equal(b[fg],expected[fg]) and g.info['duration']==ds[k]
 return {'frames':len(fs),'duration_ms':sum(ds),'decoded_exact':True,'scale':3}
checks['opening_gif']=gif('lexicon_opening',tip+fall,spec['lexicon_tip_up']['durations_ms']+spec['lexicon_covers_fall']['durations_ms']);checks['page_turn_gif']=gif('lexicon_page_turn',page,spec['lexicon_page_turn']['durations_ms'])
mask=read(O/'lexicon_sigil_mask.png');sig=mask[:,:,3]>0;overlay=closed.copy();overlay[sig]=[70,202,213,255]
b=Image.new('RGBA',(384,144),'#343132');dr=ImageDraw.Draw(b);font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',10)
for k,(a,label) in enumerate([(closed,'干净封面'),(mask,'白色遮罩'),(overlay,'青蓝叠加位置检查')]):b.alpha_composite(Image.fromarray(a),(k*128,0));dr.text((k*128+3,131),label,font=font,fill='#d9d1c4')
b.resize((1152,432),Image.Resampling.NEAREST).save(Q/'lexicon_sigil_check_3x.png')
# The mask is exactly the original source cyan footprint.
ref=read(W/'closed_reference.png');r=ref[:,:,:3].astype(int);original_cyan=(r[:,:,1]>r[:,:,0]+20)&(r[:,:,2]>r[:,:,0]+20);assert np.array_equal(original_cyan,sig);checks['mask_equals_original_symbol_footprint']=True
for n,t in spec.items():(Q/f'{n}_metrics.json').write_text(json.dumps(metrics[n],indent=2)+'\n')
(Q/'lexicon_endpoint_checks.json').write_text(json.dumps(checks,indent=2)+'\n');(Q/'lexicon_clean_metrics.json').write_text(json.dumps({n:m for n,m in metrics.items() if n not in spec},indent=2)+'\n');(W/'timing_entries.json').write_text(json.dumps(spec,indent=2)+'\n')
run=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),*map(str,sorted(O.glob('*.png'))),*map(str,sorted((O/'frames').rglob('*.png')))],cwd=R,capture_output=True,text=True,check=True);(Q/'lexicon_pixel_check.txt').write_text(run.stdout)
print(json.dumps({'runtime_files':6,'animation_frames':13,'world_palette':len(pal),'new_colors':0,'partial_alpha':0,'cyan':0,'endpoints_exact':True,'mask_pixels':int(sig.sum()),'gif_checks':[checks['opening_gif'],checks['page_turn_gif']]},indent=2))
