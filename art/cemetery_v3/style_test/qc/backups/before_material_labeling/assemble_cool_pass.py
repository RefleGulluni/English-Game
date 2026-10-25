"""Integer-grid extraction, ramp mapping, and comparison assembly only.
The scene artwork is redrawn by image_gen, not generated procedurally here.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
import json,hashlib,colorsys

ROOT=Path(__file__).resolve().parents[1]
QC=ROOT/'qc'
REPO=ROOT.parents[2]
GEN=Path('/Users/mac/.codex/generated_images/01a1707a-4cde-7eb1-a5bc-f1c69c246e40')
FILES={'V1':'exec-0dc7ecf9-f301-4649-a4d8-57fc686e73f0.png','V2':'exec-e94fcf01-5bf9-4495-a655-79b2220ae5e5.png'}
RAMPS={
 'V1':{
  'stone':['#272d33','#596266','#8a918e','#adb0a3','#c5c5b4'],
  'iron':['#192026','#3b464e','#616e75','#919d9f'],
  'mud':['#373f43','#4c575b','#657074','#7a8587'],
  'water':['#43535e','#5b6e79','#7c9099','#9caaad'],
  'grass':['#424837','#62674b','#868964','#aaa983'],
  'grave':['#191e22','#272f34','#394246','#4c5757']},
 'V2':{
  'stone':['#293139','#58666e','#899594','#bbc1b4'],
  'iron':['#1a2026','#3e4c55','#687980','#9ba8aa'],
  'mud':['#333f45','#4b5c63','#697b81','#849499'],
  'water':['#43525e','#5e7480','#8299a3','#a6b7bc'],
  'grass':['#424d39','#66724f','#8b966b','#b0b790'],
  'grave':['#1a2026','#2c3840','#43535a','#5c6a69']}}

def rgb(s): return tuple(bytes.fromhex(s[1:]))
fontpath='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
font=ImageFont.truetype(fontpath,28)
small=ImageFont.truetype(fontpath,19)
hero=Image.open(REPO/'art/character_design/hero_B1_front_straight.png').convert('RGBA')
original=Image.open(REPO/'art/cemetery_v3/design/bg_skeleton_room_A.png').convert('RGB').crop((600,180,960,440))
assert original.size==(360,260) and hero.size==(96,96)
original.save(QC/'original_crop.png')
metadata={'crop':[600,180,960,440],'native_size':[360,260],'hero_position':[4,80],'hero_source_sha256':hashlib.sha256((REPO/'art/character_design/hero_B1_front_straight.png').read_bytes()).hexdigest(),'extraction':'1536x1024 generated canvas; upper-left 1080x780 artwork; select source[0:780:3,0:1080:3], exactly integer factor 3; never arbitrary resize','materials':RAMPS,'variants':{}}
images=[original]
for name in ('V1','V2'):
    src=Image.open(GEN/FILES[name]).convert('RGB')
    assert src.size==(1536,1024)
    a=np.asarray(src)[:780,:1080]
    native=Image.fromarray(a[::3,::3].copy())
    assert native.size==(360,260)
    colors=[rgb(c) for ramp in RAMPS[name].values() for c in ramp]
    # Assign material families before ramp mapping. A global nearest-color map
    # incorrectly assigns brown soil to olive grass; this is not a valid palette.
    n=np.asarray(native); nf=n.astype(float)/255
    maxc=nf.max(axis=2); minc=nf.min(axis=2)
    sat=np.divide(maxc-minc,maxc,out=np.zeros_like(maxc),where=maxc>0)
    hue=np.zeros(maxc.shape)
    unique,inv=np.unique(n.reshape(-1,3),axis=0,return_inverse=True)
    hu=np.array([colorsys.rgb_to_hsv(*(int(v)/255 for v in c))[0]*360 for c in unique])
    hue=hu[inv].reshape(maxc.shape)
    yy,xx=np.mgrid[:260,:360]
    family=np.full((260,360),'mud',dtype='<U6')
    family[(hue>=160)&(hue<=260)&(sat>.10)]='water'
    family[(hue>=38)&(hue<=85)&(sat>=.19)]='grass'
    objects=((xx>=90)&(xx<=260)&(yy>=23)&(yy<=145))|((xx>=250)&(yy<=100))|((xx>=305)&(yy>=100)&(yy<=172))|((xx>=243)&(xx<=284)&(yy>=156)&(yy<=215))|((yy>=208)&(xx>=195))|((yy>=221)&(xx>=138)&(xx<=185))
    family[objects&(sat<.18)]='stone'
    ironzone=((yy>=188)&(yy<=231)&(xx>=229))|((yy>=228)&(xx<=108))
    family[ironzone&(maxc<.28)]='iron'
    pitmask=Image.new('1',(360,260));pd=ImageDraw.Draw(pitmask)
    pd.polygon([(121,45),(152,32),(190,91),(150,105)],fill=1)
    family[np.asarray(pitmask)&(maxc<.28)]='grave'
    result=np.empty(n.shape,dtype=np.uint8)
    lum=(n.astype(float)*np.array([.2126,.7152,.0722])).sum(axis=2)
    for mat,ramp in RAMPS[name].items():
        palette=np.array([rgb(c) for c in ramp],dtype=np.uint8)
        levels=(palette.astype(float)*np.array([.2126,.7152,.0722])).sum(axis=1)
        indices=np.abs(lum[:,:,None]-levels).argmin(axis=2)
        chosen=palette[indices];mask=family==mat;result[mask]=chosen[mask]
    out=Image.fromarray(result)
    out.save(ROOT/f'style_test_{name}.png')
    used=set(out.getdata()); palette_used=[c for c in colors if c in used]
    blue=[c for c in used if 160<=colorsys.rgb_to_hsv(*(v/255 for v in c))[0]*360<=260 and colorsys.rgb_to_hsv(*(v/255 for v in c))[1]>=.35]
    assert not blue
    arr=np.asarray(out)
    same=np.zeros((258,358),dtype=np.uint8)
    center=arr[1:-1,1:-1]
    for dy,dx in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]: same+=np.all(center==arr[1+dy:259+dy,1+dx:359+dx],axis=2)
    block=a.reshape(260,3,360,3,3).transpose(0,2,1,3,4).reshape(260,360,9,3)
    variation=np.max(block,axis=2).astype(int)-np.min(block,axis=2).astype(int)
    metadata['variants'][name]={'source':str(GEN/FILES[name]),'source_size':list(src.size),'sample_origin':[0,0],'sample_step':3,'native_size':list(out.size),'mode':out.mode,'colors':len(used),'palette_limit':len(colors),'saturated_cyan_blue_colors':len(blue),'isolated_8_neighbor_pixels':int((same==0).sum()),'generated_3x3_cells_with_channel_range_over_12':int(np.any(variation>12,axis=2).sum()),'palette_used_by_family':{key:[c for c in ramp if rgb(c) in used] for key,ramp in RAMPS[name].items()},'material_label_counts':{mat:int((family==mat).sum()) for mat in RAMPS[name]}}
    images.append(out)
    with (QC/f'style_palette_{name}.gpl').open('w') as f:
        f.write(f'GIMP Palette\nName: Cemetery Style Test {name}\nColumns: 5\n# Material ramps\n')
        for mat,ramp in RAMPS[name].items():
            for i,c in enumerate(ramp):
                r,g,b=rgb(c);f.write(f'{r:3d} {g:3d} {b:3d}  {mat}_{i}\n')

# No variant contains a character; composite source hero only in comparison panels.
comparison=Image.new('RGB',(3240,840),(28,32,35))
draw=ImageDraw.Draw(comparison)
composites=[]
for i,(name,im) in enumerate(zip(('原图截块','V1 收敛版','V2 风格化版'),images)):
    composite=im.copy();composite.paste(hero,(4,80),hero.getchannel('A'))
    h=np.asarray(hero);mask=h[:,:,3]==255
    assert np.array_equal(np.asarray(composite)[80:176,4:100][mask],h[:,:,:3][mask])
    composites.append(composite)
    comparison.paste(composite.resize((1080,780),Image.Resampling.NEAREST),(i*1080,60))
    draw.text((i*1080+20,12),name+' · 同位置原色主角 · nearest 3×',font=font,fill=(224,228,220))
comparison.save(QC/'style_compare_3x.png')

# 96x96 native panels; stone region remains at its native scale.
edge=Image.new('RGB',(3072,828),(28,32,35));d=ImageDraw.Draw(edge)
hero_panel=Image.new('RGB',(96,96),(76,87,92));hero_panel.paste(hero,(0,0),hero.getchannel('A'))
edge_panels=[hero_panel]
for im in images:
    panel=Image.new('RGB',(96,96),(76,87,92));panel.paste(im.crop((280,88,360,184)),(8,0));edge_panels.append(panel)
for i,(name,panel) in enumerate(zip(('原色主角','原图墓碑','V1 墓碑','V2 墓碑'),edge_panels)):
    edge.paste(panel.resize((768,768),Image.Resampling.NEAREST),(i*768,60));d.text((i*768+22,13),name+' · nearest 8×',font=font,fill=(224,228,220))
edge.save(QC/'style_edges_8x.png')

# Compact overview is a separate 1x comparison, never used as 3x proof.
overview=Image.new('RGB',(1080,300),(28,32,35));d=ImageDraw.Draw(overview)
for i,(name,panel) in enumerate(zip(('原图','V1 收敛','V2 风格化'),composites)):
    overview.paste(panel,(i*360,40));d.text((i*360+12,7),name,font=small,fill=(224,228,220))
overview.save(QC/'style_overview_1x.png')

swatch=Image.new('RGB',(1000,520),(28,32,35));d=ImageDraw.Draw(swatch)
for vi,name in enumerate(('V1','V2')):
    xx=vi*500;d.text((xx+15,8),name+' 材质色阶',font=font,fill=(224,228,220))
    for mi,(mat,ramp) in enumerate(RAMPS[name].items()):
        yy=55+mi*76;d.text((xx+12,yy),mat,font=small,fill=(224,228,220))
        for j,c in enumerate(ramp):
            x=xx+105+j*76;d.rectangle((x,yy,x+65,yy+32),fill=rgb(c));d.text((x,yy+36),c,font=ImageFont.truetype(fontpath,13),fill=(224,228,220))
swatch.save(QC/'style_material_ramps.png')
metadata['hero_visible_pixels_exact_in_all_comparisons']=True
(QC/'style_test_metrics.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
print(json.dumps(metadata,ensure_ascii=False,indent=2))
