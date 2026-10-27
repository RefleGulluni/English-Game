"""Generated-cell sampling and material cleanup for section7.
No drawing, noise synthesis, scaling, mirroring or rotation of game pixels.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,sys,datetime,zipfile,colorsys
S=Path(__file__).resolve().parent;D=S.parents[1];G=D.parent;R=G.parents[2];Q=D/'qc'
ns={'__name__':'grid_library','__file__':str(R/'art/cemetery_v3/backdrop/source/restore_backdrop.py')}
exec(compile(Path(ns['__file__']).read_text(),ns['__file__'],'exec'),ns,ns)
SPECS={
 'decal_puddle_01':('puddle_small_b',20.,21.3,'puddle','puddle_small_b.prompt.txt'),
 'decal_puddle_02':('puddle_medium_c',16.6,17.4,'puddle','puddle_medium_c.coarse.prompt.txt'),
 'decal_puddle_03':('decal_puddle_03',6.65,6.6,'puddle','decal_puddle_03.coarse.prompt.txt'),
 'decal_moss_01':('moss_small_b',21.3,22.7,'moss','moss_small_b.prompt.txt'),
 'decal_moss_02':('moss_medium_c',19.2,19.8,'moss','moss_medium_c.coarse.prompt.txt'),
 'decal_moss_03':('decal_moss_03',13.,13.1,'moss','decal_moss_03.coarse.prompt.txt'),
 'decal_pebbles_01':('decal_pebbles_01',6.4,6.8,'pebbles','decal_pebbles_01.coarse.prompt.txt'),
 'decal_pebbles_02':('decal_pebbles_02',10.35,10.6,'pebbles','decal_pebbles_02.coarse.prompt.txt'),
 'decal_bone_bits_01':('decal_bone_bits_01',8.,8.,'bone','decal_bone_bits_01.coarse.prompt.txt'),
 'decal_ruts_01':('decal_ruts_01',7.95,8.,'ruts','decal_ruts_01.coarse.prompt.txt'),
 # Last four pitches are confirmed from the generated source before final run.
 'decal_roots_01':('decal_roots_01',7.1,7.6,'roots','decal_roots_01.coarse.prompt.txt'),
 'decal_dead_flowers_01':('decal_dead_flowers_01',6.7,5.7,'flowers','decal_dead_flowers_01.coarse.prompt.txt'),
 'decal_cracked_slab_01':('decal_cracked_slab_01',12.3,10.9,'slab','decal_cracked_slab_01.edit.prompt.txt'),
 'decal_leaves_02':('decal_leaves_02',6.03,5.7,'leaves','decal_leaves_02.coarse.prompt.txt'),
}
def key(a):
 r,g,b=np.moveaxis(a.astype(float),2,0)
 return ~(((r>g+45)&(b>g+40))|((r>g+25)&(b>g+25)&(b>r*.65)))

def restore(src,sx,sy):
 raw=Image.open(S/f'{src}_generated.png').convert('RGB');a=np.array(raw)
 # Uniformize keyed background for detecting edges only. Sample original RGB.
 detect=a.copy();detect[~key(a)]=[255,0,255]
 xs=ns['axis_grid'](detect,1,sx);ys=ns['axis_grid'](detect,0,sy)
 xc=[(l+r-1)//2 for l,r in zip(xs,xs[1:])];yc=[(l+r-1)//2 for l,r in zip(ys,ys[1:])]
 cells=Image.fromarray(a[np.ix_(yc,xc)]);cells.save(S/f'{src}_round2_cells.png')
 meta={'source_size':list(raw.size),'native_size':list(cells.size),'pitch':[sx,sy],'x_boundaries':xs,'y_boundaries':ys,'x_centers':xc,'y_centers':yc,'method':'Source block-transition path. Keyed background uniformized for detection only; one untouched original RGB center sample per cell. No color averaging or image resampling. Background lattice inferred; local drift possible.'}
 (S/f'{src}_round2_grid.json').write_text(json.dumps(meta,indent=2)+'\n')
 overlay=raw.copy();dr=ImageDraw.Draw(overlay)
 for x in xs[1:-1]:dr.line((x,0,x,raw.height-1),fill=(213,100,170))
 for y in ys[1:-1]:dr.line((0,y,raw.width-1,y),fill=(213,100,170))
 overlay.save(S/f'{src}_round2_grid_overlay.png')
 return np.array(cells),meta

basepal=np.unique(np.array(Image.open(G/'base/ground_base_01.png').convert('RGB')).reshape(-1,3),axis=0)
stonepal=np.unique(np.array(Image.open(D/'decal_loose_slab_01.png').convert('RGBA')).reshape(-1,4),axis=0);stonepal=stonepal[stonepal[:,3]>0,:3]
def nearest(a,pal):
 return pal[np.argmin(((a.astype(float)[:,:,None,:]-pal[None,None,:,:].astype(float))**2).sum(3),axis=2)]
def cleanup(name,src,sx,sy,kind,prompt):
 rgb,grid=restore(src,sx,sy);mask=key(rgb);a=rgb.astype(float);r,g,b=np.moveaxis(a,2,0);L=a@np.array([.2126,.7152,.0722]);mid=float(np.median(L[mask]));target=a.copy();stats={}
 def ramp(c,k,center=mid):return np.asarray(c)+k*(L-center)[:,:,None]
 if kind=='puddle':
  water=(b>=r-2)&(b>=g-7)&mask
  vals=L[water];wm=float(np.median(vals));reflection=water&(L>max(wm+18,63))
  target=ramp([46,49,49],.40,wm);target[reflection]=np.array([67,70,68])+.10*(L[reflection]-np.median(L[reflection]))[:,None]
  mud=mask&~water;mm=float(np.median(L[mud]));soil=ramp([43,46,38],.50,mm);target[mud]=soil[mud]
  # Light source-earth fragments at the outside merge into receiving soil.
  interior=mask.copy();interior[1:]&=mask[:-1];interior[:-1]&=mask[1:];interior[:,1:]&=mask[:,:-1];interior[:,:-1]&=mask[:,1:]
  blend=mud&~interior&(L>mm+3);match=nearest(np.full(a.shape,[65,66,55])+.25*(L-mm)[:,:,None],basepal);target[blend]=match[blend]
  stats={'water_pixels':int(water.sum()),'reflection_pixels':int(reflection.sum()),'water_mean_before':a[water].mean(0).tolist(),'water_mean_after':target[water&~reflection].mean(0).tolist(),'wet_mud_pixels':int(mud.sum())}
 elif kind=='moss':
  earth=(r>=g-1)&(r>b+6)&mask;green=mask&~earth;gm=float(np.median(L[green]));target=ramp([53,61,44],.35,gm)
  soil=nearest(np.full(a.shape,[68,69,58])+.18*(L-mid)[:,:,None],basepal);target[earth]=soil[earth]
 elif kind=='pebbles':
  target=ramp([80,82,70],.65);target=np.clip(target,[46,49,42],[106,107,93])
 elif kind=='bone':
  target=ramp([83,81,66],.50);target=np.clip(target,[47,49,41],[110,107,88])
 elif kind=='ruts':
  target=ramp([54,57,46],.35)
 elif kind=='roots':
  target=ramp([66,63,48],.50);target=np.clip(target,[39,42,34],[94,87,65])
 elif kind=='flowers':
  petal=(r>g+5)&(b>=g-2)&mask
  target=ramp([71,69,52],.45);petals=ramp([67,54,59],.35);target[petal]=petals[petal]
 elif kind=='slab':
  target=ramp([98,100,90],.70);dark=L<np.percentile(L[mask],18)
  target=nearest(target,stonepal).astype(float);mud=nearest(ramp([52,55,46],.40),basepal);target[dark]=mud[dark]
 elif kind=='leaves':
  target=ramp([87,77,53],.45)
 target=np.rint(target).clip(0,255).astype('uint8')
 # Limit close colors without dithering; moss uses a quiet10color table.
 count=10 if kind=='moss' else 24
 strip=Image.fromarray(target[mask][None,:,:]);qp=strip.quantize(colors=count,dither=Image.Dither.NONE).convert('RGB');pal=np.unique(np.array(qp).reshape(-1,3),axis=0)
 out=nearest(target,pal);rgba=np.dstack([out,mask.astype('uint8')*255]);rgba[~mask]=0
 im=Image.fromarray(rgba);bbox=im.getbbox();im=im.crop(bbox);visible=list(im.size)
 padded=Image.new('RGBA',(im.width+4,im.height+4));padded.paste(im,(2,2));padded.save(S/f'{name}_cleaned_native.png')
 assert set(padded.getchannel('A').getdata())<={0,255}
 cyan=sum(160<=colorsys.rgb_to_hsv(*(v/255 for v in c))[0]*360<=260 and colorsys.rgb_to_hsv(*(v/255 for v in c))[1]>=.35 and max(c)>76.5 for c in np.array(padded)[:,:,:3][np.array(padded)[:,:,3]>0])
 assert not cyan,(name,cyan)
 return {'file':name+'.png','source':src+'_generated.png','prompt':prompt,'grid':src+'_round2_grid.json','restored':src+'_round2_cells.png','cleaned':name+'_cleaned_native.png','material':kind,'canvas':list(padded.size),'visible':visible,'source_cell_crop':list(bbox),'colors':len(np.unique(np.array(padded)[:,:,:3][np.array(padded)[:,:,3]>0],axis=0)),'material_stats':stats}

if __name__=='__main__':
 existing=list(S.glob('*_cleaned_native.png'))+list(S.glob('*_round2_cells.png'))+list(S.glob('*_round2_grid.json'))+list(S.glob('*_round2_grid_overlay.png'))
 if existing:
  with zipfile.ZipFile(Q/f'backups/round2_cleanup_before_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
   for p in existing:z.write(p,p.name)
 rows=[]
 for n,sp in SPECS.items():
  if (S/(sp[0]+'_generated.png')).exists():rows.append(cleanup(n,*sp))
 data={'pipeline':'Built-in image_gen, observed source cell center sampling, binary key and semantic palette cleanup, integer crop/pad. Intentional isolated moss/pebble flecks kept. No scaling, mirroring, rotation, generated noise or drawn pixels.','assets':rows,'unselected_sources':[p.name for p in S.glob('*_generated.png') if p.name not in {r['source'] for r in rows}],'status':'CANDIDATES_NOT_YET_COPIED_TO_DELIVERY'}
 if (S/'round2_manifest.json').exists():
  with zipfile.ZipFile(Q/f'backups/round2_manifest_before_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(S/'round2_manifest.json','round2_manifest.json')
 (S/'round2_manifest.json').write_text(json.dumps(data,indent=2)+'\n')
 print([(r['file'],r['visible'],r['colors']) for r in rows])
