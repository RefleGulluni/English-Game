"""Normalize generated concept art, composite the original-size hero, and make QA sheets.
No scene art is drawn by this script. Run from this directory.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import colorsys, json, hashlib

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
QC = ROOT / 'qc'
GEN = Path('/Users/mac/.codex/generated_images/01a1707a-4cde-7eb1-a5bc-f1c69c246e40')
SOURCES = dict(A='exec-a07a32aa-e235-4041-b636-0bcb0241b346.png', B='exec-ddecc85f-dcf3-4343-89fd-1e48000cdffd.png', C='exec-081f878d-def9-4fdd-87cd-69a83ed1d0cb.png')
HERO = REPO / 'art/character_design/hero_B1_front_straight.png'
hero = Image.open(HERO).convert('RGBA')
assert hero.size == (96,96) and set(hero.getchannel('A').getdata()) == {0,255}
hero_original = hero.copy()
hero_array = np.array(hero)
hero_remap = {(36,139,155):(107,120,122), (70,202,213):(152,165,166), (164,237,239):(190,196,190)}
remapped_pixels = 0
for old,new in hero_remap.items():
    mask = np.all(hero_array[:,:,:3] == old,axis=2) & (hero_array[:,:,3]==255)
    remapped_pixels += int(mask.sum()); hero_array[mask,:3] = new
hero = Image.fromarray(hero_array)
font_path = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
font = ImageFont.truetype(font_path,16)
small = ImageFont.truetype(font_path,13)
titlefont = ImageFont.truetype(font_path,22)
native = {k:Image.open(GEN/v).convert('RGB').resize((960,540),Image.Resampling.NEAREST) for k,v in SOURCES.items()}
atlas = Image.new('RGB',(960,1620))
for i,k in enumerate('ABC'): atlas.paste(native[k],(0,i*540))
basepal = atlas.quantize(colors=64,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
rgb = basepal.getpalette()[:192]
envpal=[]
for i in range(64):
    r,g,b=rgb[i*3:i*3+3]
    h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
    # Cemetery is subdued; blue-grey never becomes language-layer cyan.
    s=min(s,0.22 if 160<=h*360<=260 else 0.30)
    envpal.append(tuple(round(c*255) for c in colorsys.hsv_to_rgb(h,s,v)))
palimage=Image.new('P',(1,1)); palimage.putpalette([v for c in envpal for v in c]+list(envpal[-1])*192)
metadata={'native_canvas':[960,540],'environment_palette_limit':64,'hero_sha256':hashlib.sha256(HERO.read_bytes()).hexdigest(),'hero_original_size':True,'hero_palette_exception':{'reason':'remove pre-existing saturated cyan ornament from world-only visual target','remap':{str(k):v for k,v in hero_remap.items()},'affected_pixels':remapped_pixels,'original_source_untouched':True},'method':'nearest native grid -> shared 64-color median-cut palette, saturation cap, no dithering -> isolated-pixel majority cleanup -> 1x hero composite with three cyan ornament palette entries muted','directions':{}}
panels=[]
layouts={
 'A':{'name':'残墙院落','arena':(280,100,680,320),'entry':(0,290,170,385),'exits':[(440,0,555,90),(865,102,960,180)],'grave':(705,210,865,306),'hero':(350,210),'props':[(0,0,200,185),(0,220,145,320),(145,300,365,432),(585,33,860,120),(720,345,960,540),(0,400,395,540)],'fracture':(0,320,185,390)},
 'B':{'name':'雾坡墓群','arena':(280,104,680,324),'entry':(0,225,155,300),'exits':[(505,0,595,100),(865,125,960,210)],'grave':(715,198,858,290),'hero':(350,210),'props':[(0,0,210,205),(210,45,450,130),(590,0,835,145),(0,300,430,540),(590,365,960,540),(710,278,795,345)],'fracture':(660,277,765,345)},
 'C':{'name':'下沉墓区','arena':(270,125,670,345),'entry':(0,215,170,295),'exits':[(462,0,610,126),(870,65,960,173)],'grave':(755,208,888,286),'hero':(350,210),'props':[(0,0,210,200),(190,0,460,125),(610,0,865,165),(0,290,300,540),(590,345,960,540)],'fracture':(125,42,225,110)}
}
def label(draw,xy,text,color):
    x,y=xy; box=draw.textbbox((x,y),text,font=small); draw.rectangle((box[0]-3,box[1]-2,box[2]+3,box[3]+2),fill=(23,24,25)); draw.text((x,y),text,font=small,fill=color)
for k in 'ABC':
    q=native[k].quantize(palette=palimage,dither=Image.Dither.NONE)
    a=np.asarray(q).copy(); before=a.copy(); neighbors=[np.roll(np.roll(before,dy,0),dx,1) for dy in (-1,0,1) for dx in (-1,0,1) if (dx,dy)!=(0,0)]
    changes=np.zeros(a.shape,bool)
    # Remove an isolated pixel only when at least six surrounding pixels agree.
    for candidate in neighbors:
        count=sum((n==candidate).astype(np.uint8) for n in neighbors)
        same=sum((n==before).astype(np.uint8) for n in neighbors)
        mask=(same==0)&(count>=6); mask[[0,-1],:]=False; mask[:,[0,-1]]=False
        a[mask]=candidate[mask]; changes|=mask
    q=Image.fromarray(a,'P'); q.putpalette(palimage.getpalette()); env=q.convert('RGB')
    l=layouts[k]; out=env.copy(); out.paste(hero,l['hero'],hero.getchannel('A'))
    out.save(ROOT/f'bg_skeleton_room_{k}.png')
    x,y=l['hero']; finalarr=np.asarray(out); h=np.asarray(hero); mask=h[:,:,3]==255
    assert np.array_equal(finalarr[y:y+96,x:x+96][mask],h[:,:,:3][mask])
    used=set(out.getdata()); envused=set(env.getdata())
    cyan=[c for c in used if 160<=colorsys.rgb_to_hsv(*(v/255 for v in c))[0]*360<=260 and colorsys.rgb_to_hsv(*(v/255 for v in c))[1]>=0.35]
    metadata['directions'][k]={'source_path':str(GEN/SOURCES[k]),'source_size':Image.open(GEN/SOURCES[k]).size,'output_size':out.size,'mode':out.mode,'colors_total':len(used),'environment_colors':len(envused),'saturated_cyan_blue_colors':len(cyan),'isolated_pixels_cleaned':int(changes.sum()),'hero_visible_pixel_match_after_declared_color_remap':True,'hero_xy':l['hero'],'hero_size':[96,96],'layout':l}
    panels.append(out)
    annotated=Image.new('RGB',(960,690),(23,24,25)); annotated.paste(out,(0,0)); d=ImageDraw.Draw(annotated)
    for i,box in enumerate(l['props']):
        d.rectangle(box,outline=(211,173,132),width=1); label(d,(box[0]+5,box[1]+5),f'P{i+1}',(211,173,132))
    d.rectangle(l['arena'],outline=(206,216,153),width=2); label(d,(l['arena'][0]+5,l['arena'][1]+4),'战斗空地 400 × 220',(206,216,153))
    d.rectangle(l['entry'],outline=(225,183,114),width=2); label(d,(8,l['entry'][1]+5),'入口',(225,183,114))
    for i,box in enumerate(l['exits']):
        d.rectangle(box,outline=(196,219,184),width=2); label(d,(box[0]+4,box[1]+4),f'出口 {i+1}',(196,219,184))
    d.rectangle(l['grave'],outline=(212,158,160),width=2); label(d,(l['grave'][0]+4,l['grave'][1]+3),'打开的墓穴',(212,158,160))
    d.rectangle(l['fracture'],outline=(189,160,201),width=2); label(d,(l['fracture'][0]+3,l['fracture'][1]+3),'F：关系错误待复核',(189,160,201))
    for xx in range(0,960,16): d.line((xx,324,min(xx+8,959),324),fill=(244,216,181),width=2)
    label(d,(395,505),'y ≥ 324：未来战斗界面覆盖区',(244,216,181))
    d.text((20,554),f'{k}  {l["name"]}  |  960×540 原生布局',font=titlefont,fill=(225,224,211))
    d.text((20,590),'黄：入口   浅绿：出口   灰绿：战斗空地   粉：墓穴   紫：Fracture 候选位置',font=font,fill=(210,210,200))
    d.text((20,620),'P 框：未来独立的树、碑、墙栏、台阶／土坡；重复墓碑按实例继续拆。墓穴同样独立。',font=font,fill=(210,210,200))
    d.text((20,650),'本图为方向标注，不是碰撞图。C 的战斗框低端越过界面线 21px，详见 QA。',font=font,fill=(210,210,200))
    annotated.save(QC/f'bg_layout_{k}.png')
compare=Image.new('RGB',(5760,1080))
for i,p in enumerate(panels): compare.paste(p.resize((1920,1080),Image.Resampling.NEAREST),(i*1920,0))
compare.save(QC/'bg_directions_compare_2x.png')
overview=Image.new('RGB',(1440,310),(23,24,25)); d=ImageDraw.Draw(overview)
for i,(k,p) in enumerate(zip('ABC',panels)):
    overview.paste(p.resize((480,270),Image.Resampling.NEAREST),(i*480,40)); d.text((i*480+14,7),f'{k}  {layouts[k]["name"]}',font=titlefont,fill=(225,224,211))
overview.save(QC/'bg_directions_overview.png')
hero_colors=sorted({tuple(c[:3]) for c in hero.getdata() if c[3]==255})
colors=list(dict.fromkeys(envpal+hero_colors))
with (QC/'bg_palette.gpl').open('w') as f:
    f.write('GIMP Palette\nName: Cemetery v3 proposal + Hero B1 world-only remap\nColumns: 8\n# First 64 are environment; remaining entries are hero colors with three cyan ornament entries muted.\n')
    for i,c in enumerate(colors): f.write(f'{c[0]:3d} {c[1]:3d} {c[2]:3d}  {"ENV" if i<64 else "HERO"}_{i:03d}\n')
swatch=Image.new('RGB',(800,90+((len(colors)+7)//8)*52),(23,24,25)); d=ImageDraw.Draw(swatch)
d.text((18,12),'Cemetery v3 子调色板提案',font=titlefont,fill=(225,224,211)); d.text((18,47),'ENV：64 色共享环境   HERO：主角色（三档饰物青蓝改为灰色）',font=font,fill=(210,210,200))
for i,c in enumerate(colors):
    xx=(i%8)*100; yy=90+(i//8)*52; d.rectangle((xx+6,yy,xx+93,yy+27),fill=c); d.text((xx+6,yy+29),f'{i:02d} #{c[0]:02x}{c[1]:02x}{c[2]:02x}',font=small,fill=(210,210,200))
swatch.save(QC/'bg_palette.png')
metadata['palette_entries']=len(colors)
(QC/'bg_design_metrics.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
print(json.dumps(metadata,ensure_ascii=False,indent=2))
