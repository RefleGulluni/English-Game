"""Ground-base supplement: extract generated soil, transfer existing roots, QA."""
from pathlib import Path
import io,json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
BACKUP=REPO/'art_source/backups/cemetery_ground_bases_20261022_212052'
SOURCE=json.loads((ROOT/'source/ground_bases_generation.json').read_text())
NN=Image.Resampling.NEAREST
PAL=[]
for line in (ROOT/'cemetery_palette.gpl').read_text().splitlines():
    z=line.split()
    if len(z)>=3 and all(s.isdigit() for s in z[:3]):PAL.append(tuple(map(int,z[:3])))
PAL=np.array(PAL,dtype=np.uint8)
assert len(PAL)==64

def put_bytes(rel,data):
    p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists() and p.read_bytes()!=data:
        dest=BACKUP/'revisions'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():dest=dest.with_name(dest.stem+'_'+hashlib.sha256(p.read_bytes()).hexdigest()[:10]+dest.suffix)
        if not dest.exists():shutil.copy2(p,dest)
    p.write_bytes(data)

def save(im,rel):
    b=io.BytesIO();im.save(b,format='PNG');put_bytes(rel,b.getvalue())

def text_file(rel,s):put_bytes(rel,s.encode('utf8'))

def quant(im,soil=False):
    a=np.array(im.convert('RGBA'));rgb=a[:,:,:3]
    colors,inv=np.unique(rgb.reshape(-1,3),axis=0,return_inverse=True)
    if soil:
        # Material grading only; no invented texture, outlines or alpha feather.
        colors=np.clip(colors.astype(float)*np.array([.84,.88,.94]),0,255)
    dist=((colors[:,None,:].astype(np.int32)-PAL[None,:,:].astype(np.int32))**2).sum(axis=2)
    a[:,:,:3]=PAL[dist.argmin(axis=1)][inv].reshape(rgb.shape)
    a[:,:,3]=np.where(a[:,:,3]>=128,255,0);a[a[:,:,3]==0]=0
    return Image.fromarray(a)

def key(im):
    a=np.array(im.convert('RGBA'));r,g,b=[a[:,:,i].astype(np.int16) for i in range(3)]
    bg=((r-g>55)&(b-g>55)&(r+b>260))|(a[:,:,3]<128)
    a[:,:,3]=np.where(bg,0,255);a[bg]=0
    return Image.fromarray(a)

def extract(name,size):
    im=key(Image.open(SOURCE[name]['raw_path']))
    im=im.crop(im.getbbox()).resize(size,NN)
    return quant(im,soil=True)

CONFIG=[
    {'stem':'dead_tree_01','source':'tree_base','canvas':[288,224],'soil_size':[156,72],'soil_center_x':6},
    {'stem':'tombstone_upright_01','source':'upright_base','canvas':[96,77],'soil_size':[68,28],'soil_center_x':-7},
    {'stem':'tombstone_tilted_01','source':'tilted_base','canvas':[104,76],'soil_size':[76,32],'soil_center_x':-2},
    {'stem':'tombstone_fragment_01','source':'fragment_base','canvas':[96,48],'soil_size':[70,40],'soil_center_x':4},
    {'stem':'open_grave_01','source':'grave_base','canvas':[176,80],'soil_size':[124,66],'soil_center_x':12},
]

def build():
    records=[]
    for c in CONFIG:
        w,h=c['canvas'];obj=extract(c['source'],c['soil_size'])
        x=w//2+c['soil_center_x']-obj.width//2;y=h-obj.height
        base=Image.new('RGBA',(w,h));base.alpha_composite(obj,(x,y))
        if c['stem']=='dead_tree_01':
            original=Image.open(BACKUP/'props/dead_tree_01.png').convert('RGBA')
            a=np.array(original);root=a.copy();root[:160]=0
            # Last ten rows of root tips disappear INTO the generated soil.
            # No new pixels are drawn: reveal the generated wet soil underneath.
            root[214:]=0
            # Ground roots keep their exact native coordinates and pixel colors.
            base.alpha_composite(Image.fromarray(root))
            high=a.copy();high[178:]=0
            save(Image.fromarray(high),'props/dead_tree_01.png')
        rel=f"props/{c['stem']}_base.png";save(base,rel)
        p=Image.open(ROOT/f"props/{c['stem']}.png")
        records.append({'file':rel,'paired_prop':f"props/{c['stem']}.png",'canvas':[w,h],
             'origin':[w//2,h],'prop_origin':[p.width//2,p.height],
             'world_origin':[0,0],'soil_native_size':c['soil_size'],'soil_paste':[x,y],
             'render_layer':'ground_decal_above_plate_below_all_actors','y_sort':False,'collision':False})
    # Compact4-tuft sheet: four native sizes, without changing any old decals.
    sheet=key(Image.open(SOURCE['grass']['raw_path']));w,h=sheet.size
    for i,size in enumerate([(16,10),(24,14),(32,18),(44,24)]):
        row,col=divmod(i,2);im=sheet.crop((round(col*w/2),round(row*h/2),round((col+1)*w/2),round((row+1)*h/2)))
        im=quant(im.crop(im.getbbox()).resize(size,NN),soil=True)
        out=Image.new('RGBA',(size[0]+4,size[1]));out.alpha_composite(im,(2,0))
        rel=f'decals/dead_grass_{i+1:02}.png';save(out,rel)
        records.append({'file':rel,'canvas':list(out.size),'origin':[out.width//2,out.height],
                        'render_layer':'ground_decal_above_plate_below_all_actors','y_sort':False,'collision':False})
    text_file('props/ground_bases.json',json.dumps({'assets':records,'tree_root_transfer':{
        'source_backup':str(BACKUP/'props/dead_tree_01.png'),'base_root_rows':[160,224],
        'high_kept_rows':[0,178],'shared_overlap_rows':[160,178],'buried_root_tip_rows':[214,224],'canvas_unchanged':[288,224],
        'source_pixels_redrawn':0}},indent=2))
    return records

def anchored(bg,im,origin):
    bg.alpha_composite(im,(int(origin[0]-im.width//2),int(origin[1]-im.height)))

def preview():
    plate=Image.open(ROOT/'plates/ground_plate_960x540.png').convert('RGBA')
    bg=tuple(PAL[48])+(255,);fg=tuple(PAL[46])+(255,)
    out=Image.new('RGBA',(1440,970),bg);d=ImageDraw.Draw(out)
    font=ImageFont.load_default(size=12);small=ImageFont.load_default(size=11)
    def label(x,y,s):d.text((x,y),s,fill=fg,font=font)
    label(14,10,'ENGLISH GAME | GROUND CONTACT BASES | 2x nearest preview | 64 shared colors')
    label(14,30,'Same bottom-center world origin. Base layer stays below ALL character feet. No Godot files changed.')
    names=['Tree','Upright stone','Tilted stone','Fallen fragment','Open grave']
    # Identical ground crop per before/after column, different crop per prop.
    for i,(c,name) in enumerate(zip(CONFIG,names)):
        x=i*288;label(x+12,57,name)
        ox=360+i*16;patch=plate.crop((ox,190,ox+288,470))
        old=Image.open(BACKUP/'props/dead_tree_01.png').convert('RGBA') if i==0 else Image.open(ROOT/f"props/{c['stem']}.png").convert('RGBA')
        new=Image.open(ROOT/f"props/{c['stem']}.png").convert('RGBA')
        base=Image.open(ROOT/f"props/{c['stem']}_base.png").convert('RGBA')
        before=patch.copy();anchored(before,old,(144,258));out.alpha_composite(before,(x,82))
        label(x+12,86,'BEFORE / prop only')
        after=patch.copy();anchored(after,base,(144,258));anchored(after,new,(144,258));out.alpha_composite(after,(x,380))
        label(x+12,384,'AFTER / base + prop')
        # Ground-only layer, viewed at native scale before final2x export.
        base_only=patch.copy();anchored(base_only,base,(144,258))
        out.alpha_composite(base_only.crop((0,152,288,280)),(x,700))
        label(x+12,675,'BASE ONLY / roots belong here' if i==0 else 'BASE ONLY / disturbed wet soil')
    label(14,850,'EXTRA DEAD GRASS / four distinct native sizes / no collision / always under actors')
    for i in range(4):
        patch=plate.crop((400,220,580,290));grass=Image.open(ROOT/f'decals/dead_grass_{i+1:02}.png').convert('RGBA')
        anchored(patch,grass,(90,56));out.alpha_composite(patch,(14+i*210,875))
        label(18+i*210,948,f'{i+1:02} | {grass.width}x{grass.height}')
    # A static layer proof: actor deliberately drawn after a wide grass decal.
    patch=plate.crop((400,200,688,310));grass=Image.open(ROOT/'decals/dead_grass_04.png').convert('RGBA')
    hero=Image.open(REPO/'art/pixel_test/size_96/player_idle_01.png').convert('RGBA')
    anchored(patch,grass,(134,104));anchored(patch,hero,(134,104));out.alpha_composite(patch,(1080,846))
    label(1086,830,'LAYER CHECK / actor above decal')
    save(quant(out).resize((2880,1940),NN),'qc/prop_bases_preview.png')
    # Ground-contact detail for the full tree pair, including join pixels.
    patch=plate.crop((380,210,668,370));tree=Image.open(ROOT/'props/dead_tree_01.png').convert('RGBA');base=Image.open(ROOT/'props/dead_tree_01_base.png').convert('RGBA')
    anchored(patch,base,(144,145));anchored(patch,tree,(144,145))
    save(quant(patch).resize((1152,640),NN),'qc/tree_root_contact_4x.png')

def verify(records):
    failures=[];stats=[];union=set()
    for r in records+[{'file':'props/dead_tree_01.png'}]:
        im=Image.open(ROOT/r['file']).convert('RGBA');a=np.array(im);colors=np.unique(a[a[:,:,3]>0,:3],axis=0)
        alpha=np.unique(a[:,:,3]).tolist();bad=[v.tolist() for v in colors if not np.any(np.all(PAL==v,axis=1))]
        if set(alpha)-{0,255}:failures.append(r['file']+' nonbinary alpha')
        if bad:failures.append(r['file']+' off-palette')
        union.update(map(tuple,colors.tolist()));stats.append({'file':r['file'],'size':list(im.size),
            'visible_colors':len(colors),'alpha_values':alpha,'bbox':list(im.getbbox()),
            'origin':[im.width//2,im.height],'off_palette_colors':bad,
            'sha256':hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest()})
    old=np.array(Image.open(BACKUP/'props/dead_tree_01.png').convert('RGBA'))
    high=Image.open(ROOT/'props/dead_tree_01.png').convert('RGBA');base=Image.open(ROOT/'props/dead_tree_01_base.png').convert('RGBA')
    combo=base.copy();combo.alpha_composite(high);a=np.array(combo);visible=old[:,:,3]>0
    lost=int(np.count_nonzero(np.any(a[visible]!=old[visible],axis=1)))
    overlap=int(np.count_nonzero((np.array(base)[:,:,3]>0)&(np.array(high)[:,:,3]>0)))
    changed=np.any(a!=old,axis=2)&visible
    unintended=changed.copy();unintended[214:]=False
    if np.any(unintended):failures.append('tree pixels changed outside buried tips')
    if overlap==0:failures.append('tree/base joint has no overlap')
    # The canopy/trunk upper160rows are exactly unchanged and share the old origin.
    if not np.array_equal(np.array(high)[:160],old[:160]):failures.append('upper tree was changed')
    allold=json.loads((BACKUP/'all_files_before.json').read_text());changes=[]
    for rel,h in allold.items():
        p=ROOT/rel
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:changes.append(rel)
    allowed={'props/dead_tree_01.png','props/NOTES.md'}
    unexpected=[v for v in changes if v not in allowed]
    if unexpected:failures.append('unexpected existing files changed: '+str(unexpected))
    report={'passed':not failures,'failures':failures,'assets':stats,'new_base_count':5,'new_dead_grass_count':4,
        'shared_palette_size':len(PAL),'actual_visible_color_union':len(union),
        'tree_original_pixels_lost_or_recolored':lost,'tree_intentionally_buried_tip_pixels':lost,
        'tree_unintended_pixel_changes':int(np.count_nonzero(unintended)),'tree_base_overlap_pixels':overlap,
        'tree_canvas_and_origin_preserved':True,'existing_files_changed':changes,
        'backup':str(BACKUP),'engine_validation':'not performed; art-only delivery to Claude'}
    text_file('qc/prop_bases_QA.json',json.dumps(report,indent=2))
    print(json.dumps({k:report[k] for k in ['passed','failures','new_base_count','new_dead_grass_count',
          'actual_visible_color_union','tree_original_pixels_lost_or_recolored','tree_base_overlap_pixels','existing_files_changed']},indent=2))
    if failures:raise SystemExit(1)
    return report

if __name__=='__main__':
    data=build();preview();verify(data)
