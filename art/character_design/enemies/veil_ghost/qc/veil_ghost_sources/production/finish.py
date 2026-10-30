from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, json, shutil, sys, importlib.util, hashlib, subprocess, colorsys
W=Path('/Users/mac/.codex/work/veil-ghost-20261030'); R=Path('/Users/mac/Documents/GitHub.nosync/English-Game'); O=W/'staged'; S=O/'qc/veil_ghost_sources'; Q=O/'qc'; F=O/'reference'; F.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('pixel_check',R/'scripts/tools/pixel_check.py'); pc=importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
sel={'A':sys.argv[1] if len(sys.argv)>1 else 'A_match','B':'B_regen','C':'C_regen'}
bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])
metrics={}; images={}; masks={}
for key,n in sel.items():
 d=S/n; im=Image.open(d/'02_restored_cells.png').convert('RGBA'); a=np.array(im); m=a[:,:,3]>0
 # Chroma spill is source background, not a material. No fractional alpha.
 c=a[:,:,:3].astype(float); spill=(c[:,:,0]>1.3*(c[:,:,1]+1))&(c[:,:,2]>1.3*(c[:,:,1]+1))&(c[:,:,0]>130)&(c[:,:,2]>130); m&=~spill
 # Low-saturation cold world palette; preserve the source's material-value ordering.
 rgb=c[m]; lum=rgb@np.array([.299,.587,.114]); shift={'A':[-4,0,3],'B':[-3,3,-2],'C':[-5,1,6]}[key]
 col=np.clip(.4*rgb+.6*lum[:,None]+shift,0,255).astype(np.uint8)
 # Build palette only from opaque colors: no resampling or synthetic texture.
 strip=Image.fromarray(col.reshape(1,-1,3)); qstrip=strip.quantize(colors=48,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
 a[:]=0; a[m,:3]=np.array(qstrip).reshape(-1,3); a[m,3]=255
 # A's generated robe has overlong trailing strips. Shorten only its cloth silhouette
 # on the recovered native grid; no rows are removed and no part is scaled.
 trimmed=0
 if key=='A' and n=='A_match':
  # Authored staggered hem: three uneven taper ends, all below the hands.
  ends=[110,111,112,114,116,118,119,117,115,113,111,110,111,113,115,117,118,116,114,112,110,111,113,115,117,119,118,116,114,112,111,110,111,113,115,117,118,116,114,112,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110]
  before_a=a[:,:,3]>0
  for cx in range(a.shape[1]):a[ends[cx]+1:,cx]=0
  trimmed=int(before_a.sum()-(a[:,:,3]>0).sum())
 clean=Image.fromarray(a); bb=clean.getbbox(); clean=clean.crop(bb); nw,nh=clean.size
 assert 100<=nh<=120,(key,nh)
 assert nw<=76
 ox=48-nw//2; oy=127-nh
 out=Image.new('RGBA',(96,128));out.paste(clean,(ox,oy)); p=O/f'veil_ghost_{key}.png';out.save(p); images[key]=out
 clean.save(d/'03_native_cleaned.png');out.save(d/'04_canvas_aligned.png')
 # Local authored retention fields, sampled by a fixed ordered mask. Only deletes.
 yy,xx=np.indices((128,96)); x=(xx-ox)/max(1,nw-1); y=(yy-oy)/max(1,nh-1)
 def ellipse(cx,cy,rx,ry):
  u=np.clip(1-((x-cx)/rx)**2-((y-cy)/ry)**2,0,1)
  return u*u*(3-2*u)
 if key=='A':
  density=.43-.20*np.clip((y-.55)/.45,0,1)
  density+=.50*np.maximum(ellipse(.20,.36,.23,.60),ellipse(.80,.36,.23,.60))
  density+=.30*ellipse(.50,.28,.38,.16)
  density-=.27*ellipse(.50,.12,.24,.16)
  density-=.16*ellipse(.50,.52,.25,.24)
 elif key=='B':
  density=.44-.13*np.clip((y-.75)/.30,0,1)
  density+=.52*ellipse(.50,.035,.70,.12)
  density+=.43*ellipse(.50,.19,.64,.20)
  density-=.31*ellipse(.50,.54,.27,.44)
  density+=.28*np.maximum(ellipse(.30,.72,.16,.42),ellipse(.73,.72,.16,.42))
  density+=.54*ellipse(.52,.30,.11,.14)
 else:
  density=.33-.17*np.clip((y-.58)/.42,0,1)
  density+=.66*ellipse(.50,.34,.41,.21)
  density+=.49*ellipse(.23,.40,.24,.20)
  density+=.41*ellipse(.68,.43,.23,.15)
  density+=.16*ellipse(.38,.10,.34,.19)
  density-=.21*ellipse(.46,.13,.22,.14)
  density-=.13*ellipse(.72,.69,.34,.27)
 density=np.clip(density,.08,.98)
 opaque=np.array(out)[:,:,3]>0
 keep=opaque&((bayer[yy%4,xx%4]+.5)/16<density)
 faded=np.array(out);faded[~keep]=0;fi=Image.fromarray(faded);fi.save(O/f'veil_ghost_{key}_faded.png');images[key+'_faded']=fi
 assert np.all(faded[keep]==np.array(out)[keep])
 assert not np.any(keep&~opaque)
 mask=np.zeros((128,96,4),np.uint8);mask[keep]=[255,255,255,255];Image.fromarray(mask).save(S/f'{key}_retained_pixels.png')
 Image.fromarray((np.clip(density,0,1)*255).astype('uint8')).save(S/f'{key}_retention_density.png')
 # Large reference is the selected generated design with only chroma background removed.
 raw=Image.open(d/'01_generated_original.png').convert('RGBA'); ra=np.array(raw); rc=ra[:,:,:3].astype(int); rm=~((rc[:,:,0]>170)&(rc[:,:,2]>150)&(rc[:,:,1]<110)&(rc[:,:,0]-rc[:,:,1]>70)&(rc[:,:,2]-rc[:,:,1]>65));ra[~rm]=0;ra[rm,3]=255
 Image.fromarray(ra).save(F/f'veil_ghost_{key}_concept_hires.png')
 met=pc.measure(p);met.update({'source_selected':n,'visible_bbox':list(out.getbbox()),'visible_height':nh,'placement':[ox,oy],'anchor':[48,127],'opaque_pixels':int(opaque.sum()),'faded':pc.measure(O/f'veil_ghost_{key}_faded.png'),'faded_retained_pixels':int(keep.sum()),'faded_retained_percent':round(float(keep.sum()/opaque.sum()*100),2),'faded_added_pixels':int((keep&~opaque).sum()),'faded_rgb_mismatches':int(np.any(faded[:,:,:3]!=np.array(out)[:,:,:3],axis=2)[keep].sum()),'opacity_values':list(map(int,np.unique(np.array(out)[:,:,3]))),'source_spill_pixels_removed':int(spill.sum()),'native_hem_pixels_trimmed':trimmed})
 pairs=opaque[:,1:]&opaque[:,:-1]; aout=np.array(out); met['horizontal_change_percent_exact']=round(float(np.any(aout[:,1:,:3]!=aout[:,:-1,:3],axis=2)[pairs].mean()*100),3)
 met['mean_rgb']=np.round(aout[opaque,:3].mean(axis=0),2).tolist(); metrics[key]=met
 assert met['alpha_ok'] and met['cyan']==0 and 30<=met['colors']<=50
 assert met['horizontal_change_percent_exact']>=80,(key,met)
 print(key,met)
(Q/'veil_ghost_metrics.json').write_text(json.dumps(metrics,indent=2))
# Actual ground tiles, not a generated backdrop.
hero=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA'); skel=Image.open(R/'art/character_design/enemies/skeleton/skeleton_B.png').convert('RGBA')
props=[Image.open(R/f'art/cemetery_v3/props/{n}.png').convert('RGBA') for n in ['tombstone_upright_01','tombstone_upright_02','tombstone_cross_01']]
try: font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',10)
except OSError: font=ImageFont.load_default()
def ground(path,w,h):
 tile=Image.open(path).convert('RGBA');bg=Image.new('RGBA',(w,h))
 for y in range(0,h,tile.height):
  for x in range(0,w,tile.width):bg.paste(tile,(x,y))
 return bg
def label(bg,xy,txt):
 dr=ImageDraw.Draw(bg); x,y=xy;box=dr.textbbox((x,y),txt,font=font);dr.rectangle((box[0]-3,box[1]-2,box[2]+3,box[3]+2),fill=(28,31,31,235));dr.text((x,y),txt,font=font,fill=(222,225,220))
def place(bg,im,x,y,anchor=None):
 if anchor is None:anchor=(im.width//2,im.height)
 bg.alpha_composite(im,(x-anchor[0],y-anchor[1]))
for kind,path in [('compare',R/'art/cemetery_v3/ground/base/veiled_base_01.png'),('moss_compare',R/'art/cemetery_v3/ground/transitions/moss_texture_01.png')]:
 bg=ground(path,1056,204)
 place(bg,hero,48,161);label(bg,(28,176),'HERO')
 place(bg,skel,126,161);label(bg,(108,176),'BONE')
 for j,key in enumerate(['A','B','C']):
  for state in range(2):
   x=225+(j*2+state)*100; k=key+('_faded' if state else '');place(bg,images[k],x,161,(48,127));label(bg,(x-33,176),key+(' FADED' if state else ' REVEAL'))
 for j,pr in enumerate(props):place(bg,pr,842+j*82,161);label(bg,(820+j*82,176),'STONE '+str(j+1))
 bg.resize((bg.width*2,bg.height*2),Image.Resampling.NEAREST).save(Q/f'veil_ghost_{kind}.png')
# Hero/detail panels, each exact 6x, laid vertically to keep a usable width.
bg=Image.new('RGBA',(368,3*156),(53,57,56,255))
for j,key in enumerate(['A','B','C']):
 y=j*156; place(bg,hero,64,y+134);place(bg,images[key],176,y+134,(48,127));place(bg,images[key+'_faded'],284,y+134,(48,127));label(bg,(12,y+7),key+' / HERO - REVEALED - FADED')
bg.resize((bg.width*6,bg.height*6),Image.Resampling.NEAREST).save(Q/'veil_ghost_vs_hero_6x.png')
bg=Image.new('RGBA',(832,164),(227,229,224,255))
for j,(key,im) in enumerate([('HERO',hero),('BONE',skel)]+[(k,images[k]) for k in ['A','A_faded','B','B_faded','C','C_faded']]):
 ar=np.array(im);ar[ar[:,:,3]>0]=[0,0,0,255];place(bg,Image.fromarray(ar),52+j*104,136,(48,127) if im.height==128 else None);label(bg,(22+j*104,143),key)
bg.resize((1664,328),Image.Resampling.NEAREST).save(Q/'veil_ghost_silhouette.png')
for k,im in images.items():im.resize((im.width*8,im.height*8),Image.Resampling.NEAREST).save(Q/f'veil_ghost_{k}_8x.png')
# Prompt provenance: all attempts, with selection noted.
records=[]
for f in sorted(W.glob('generation_*.json')):records+=json.loads(f.read_text())
for r in records:r['selected_for']=next((k for k,n in sel.items() if n==r['name']),None)
(Q/'veil_ghost_design_prompts.json').write_text(json.dumps({'tool':'built-in image_gen','records':records},ensure_ascii=False,indent=2))
run=subprocess.run(['python3','scripts/tools/pixel_check.py']+[str(O/f'veil_ghost_{k}{s}.png') for k in ['A','B','C'] for s in ['','_faded']],cwd=R,capture_output=True,text=True)
(S/'pixel_check.txt').write_text(run.stdout+run.stderr);assert run.returncode==0
print(run.stdout)
