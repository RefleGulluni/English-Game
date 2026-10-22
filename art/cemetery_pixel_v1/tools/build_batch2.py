"""Deterministic extraction / palette cleanup / seam repair. No creative drawing."""
from pathlib import Path
import json, hashlib, shutil, datetime, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
MAN = json.loads((ROOT/'source/generation_manifest.json').read_text())
BACKUP = REPO/'art_source/backups/cemetery_pixel_v1_batch2'
NN = Image.Resampling.NEAREST

def store_bytes(rel, data):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists() and p.read_bytes()!=data:
        old=BACKUP/rel; old.parent.mkdir(parents=True,exist_ok=True)
        if old.exists(): old=old.with_name(old.stem+'_'+hashlib.sha256(p.read_bytes()).hexdigest()[:10]+old.suffix)
        if not old.exists(): shutil.copy2(p,old)
    p.write_bytes(data)

def save(im,rel):
    b=io.BytesIO(); im.save(b,format='PNG'); store_bytes(rel,b.getvalue())

def write(rel,s): store_bytes(rel,s.encode('utf-8'))

def raw(k): return Image.open(MAN[k]['raw_path']).convert('RGBA')

base=[]
for line in (REPO/'art/pixel_test/shared_palette.gpl').read_text().splitlines():
    z=line.split()
    if len(z)>=3 and all(v.isdigit() for v in z[:3]): base.append(tuple(map(int,z[:3])))
extra=[(29,34,39),(37,42,47),(44,48,51),(50,53,55),(55,58,61),
       (61,65,70),(68,74,82),(77,85,95),(87,96,106),(99,108,116),
       (47,49,32),(60,62,39),(74,75,45),(88,87,51),(101,98,59),
       (42,51,62),(54,64,77)]
PAL=np.asarray(base+extra,dtype=np.uint8)
assert len(PAL)==64

def quant(im, indices=None):
    a=np.array(im.convert('RGBA')); rgb=a[:,:,:3]
    unique,inv=np.unique(rgb.reshape(-1,3),axis=0,return_inverse=True)
    allowed=PAL if indices is None else PAL[np.asarray(indices)]
    chunks=[]
    for u in np.array_split(unique,max(1,len(unique)//5000)):
        dist=((u[:,None,:].astype(np.int32)-allowed[None,:,:].astype(np.int32))**2).sum(axis=2)
        chunks.append(allowed[dist.argmin(axis=1)])
    a[:,:,:3]=np.concatenate(chunks)[inv].reshape(rgb.shape)
    a[:,:,3]=np.where(a[:,:,3]>=128,255,0)
    a[a[:,:,3]==0]=0
    return Image.fromarray(a)

def key(im):
    a=np.array(im.convert('RGBA')); r,g,b=[a[:,:,i].astype(np.int16) for i in range(3)]
    # Chroma only: preserve dark outlines; remove magenta interiors and fringes.
    bg=((r-g>55)&(b-g>55)&(r+b>260)) | (a[:,:,3]<128)
    a[:,:,3]=np.where(bg,0,255);a[bg]=0
    return Image.fromarray(a)

def extract(k,target_height=None,target_size=None,canvas=None,anchor=None):
    im=key(raw(k));im=im.crop(im.getbbox())
    if target_size: im=im.resize(target_size,NN)
    elif target_height: im=im.resize((round(im.width*target_height/im.height),target_height),NN)
    im=quant(im)
    if canvas:
        out=Image.new('RGBA',canvas);x=(canvas[0]-im.width)//2
        if anchor is not None: x=canvas[0]//2-round(anchor*im.width)
        out.alpha_composite(im,(x,canvas[1]-im.height));im=out
    return im

def bottom_origin(im, width=None, height=None):
    # Align a real ground-contact extremity to the bottom-center pivot. Padding
    # is transparent; silhouette pixels are never stretched or painted.
    im=im.crop(im.getbbox());a=np.array(im);ys,xs=np.where(a[:,:,3]>0)
    contact=round(float(np.median(xs[ys>=ys.max()-1])))
    width=max(width or 0,2*(max(contact,im.width-contact)+2));width+=width%2
    height=max(height or 0,im.height)
    out=Image.new('RGBA',(width,height));out.alpha_composite(im,(width//2-contact,height-im.height))
    return out

def palette():
    lines=['GIMP Palette','Name: English Game Cemetery v1 - 64 visible colors','Columns: 8',
           '# Entries 1-47 preserved exactly from art/pixel_test/shared_palette.gpl.',
           '# Entries 48-64: Cemetery cool neutrals, blue-gray water, olive moss.',
           '# Alpha is separate and strictly binary. No cyan sigil extension in this batch.']
    for i,c in enumerate(PAL):
        label=f'Global_{i+1:02}' if i<47 else ['Cold_Deep','Cold_Dark','Cold_Charcoal','Cold_Mud','Cold_Neutral','Slate_Shadow','Slate_Mid','Puddle_Main','Puddle_Light','Puddle_Glint','Moss_Deep','Moss_Shadow','Moss_Mid','Moss_Light','Moss_Dry','Puddle_Deep','Puddle_Shadow'][i-47]
        lines.append(f'{int(c[0]):3} {int(c[1]):3} {int(c[2]):3}  {label}')
    write('cemetery_palette.gpl','\n'.join(lines)+'\n')

def environment():
    plate=quant(raw('plate').resize((960,540),NN));save(plate,'plates/ground_plate_960x540.png')
    tree=bottom_origin(extract('tree',target_height=224),width=288,height=224)
    save(tree,'props/dead_tree_01.png')
    # Keep accepted upright reference at its original native size and drawing.
    upright=bottom_origin(quant(Image.open(REPO/'art/pixel_test/size_96/tombstone_01.png')),width=72)
    save(upright,'props/tombstone_upright_01.png')
    save(bottom_origin(extract('tilted',target_height=76),width=72),'props/tombstone_tilted_01.png')
    save(bottom_origin(extract('fragment',target_size=(48,35)),width=64),'props/tombstone_fragment_01.png')
    save(bottom_origin(extract('grave',target_size=(96,72)),width=128),'props/open_grave_01.png')
    # Preserve original generated target separately as a palette-clean source
    # reference; the requested target is reassembled with final native assets
    # so scale/hand/anchor can be judged without AI's oversized scale witness.
    save(quant(raw('target').resize((960,540),NN)),'source/visual_target_generated_reference.png')
    target=plate.copy()
    placements=[('props/dead_tree_01.png',180,236),('props/tombstone_upright_01.png',95,451),
                ('props/tombstone_upright_01.png',218,499),('props/tombstone_upright_01.png',335,178),
                ('props/tombstone_upright_01.png',590,98),('props/tombstone_tilted_01.png',899,278),
                ('props/tombstone_fragment_01.png',642,128),('props/open_grave_01.png',803,330)]
    hero=quant(Image.open(REPO/'art/pixel_test/size_96/player_idle_01.png'))
    items=[(Image.open(ROOT/f).convert('RGBA'),x,y,f) for f,x,y in placements]
    items.append((hero,338,408,'accepted_player_reference'))
    for im,x,y,name in sorted(items,key=lambda v:v[2]):target.alpha_composite(im,(x-im.width//2,y-im.height))
    save(target,'source/visual_target_960x540.png')
    write('source/preview_placement.json',json.dumps({'purpose':'QA only; no Godot assembly','canvas':[960,540],
          'props':[{'file':f,'bottom_center':[x,y]} for f,x,y in placements],
          'player_reference':{'file':'../pixel_test/size_96/player_idle_01.png','bottom_center':[338,408]}},indent=2))

def compact():
    sheet=key(raw('compact')); w,h=sheet.size
    names=['decals/gravel_01','decals/gravel_02','decals/gravel_03','decals/leaves_01',
           'decals/leaves_02','decals/ground_crack_01','decals/moss_01','decals/moss_02']
    sizes=[16,22,14,20,20,28,24,28,30,36,30,28,32,30,36,20]
    records=[]
    for k in range(16):
        y,x=divmod(k,4)
        cell=sheet.crop((round(x*w/4),round(y*h/4),round((x+1)*w/4),round((y+1)*h/4)))
        bbox=cell.getbbox();obj=cell.crop(bbox)
        scale=sizes[k]/max(obj.size);dims=(max(1,round(obj.width*scale)),max(1,round(obj.height*scale)))
        obj=quant(obj.resize(dims,NN))
        # Ground crack kept darker than stone. Moss uses Cemetery olive ramp.
        if k==5:
            a=np.array(obj);vis=a[:,:,3]>0
            q=quant(Image.fromarray(a),[3,6,11,14,49,50]);obj=q
        if k in [6,7]:obj=quant(obj,list(range(57,62)))
        cw=obj.width+4;cw+=cw%2;out=Image.new('RGBA',(cw,obj.height))
        out.alpha_composite(obj,((cw-obj.width)//2,0))
        rel=(names[k] if k<8 else f'path/old_slab_{k-7:02}')+'.png';save(out,rel)
        records.append({'file':rel,'source_cell':k,'native_size':out.size})
    write('source/compact_extraction.json',json.dumps(records,indent=2))

def periodic(a):
    a=a.copy();a[-1]=a[0];a[:,-1]=a[:,0]
    a[0,-1]=a[-1,0]=a[-1,-1]=a[0,0]
    return a

def terrain():
    source=raw('terrain')
    # Deterministic extraction: AI atlas is exactly4x8, no gutters.
    atlas=np.array(quant(source.resize((128,256),NN)))
    # Keep only quiet source-art pixel clusters for base tiles. No invented texture.
    base_source=raw('bases') if 'bases' in MAN else source
    origins={'mud':(0,0),'grass':(1,0),'puddle':(2,0)} if 'bases' in MAN else {'mud':(0,0),'grass':(3,3),'puddle':(7,3)}
    bases={};means={}
    for mat,(r,c) in origins.items():
        # Full-material cell sampled at64 first; four32x32 crops are real art variants.
        sw,sh=base_source.size
        # Each distinct AI-authored cell becomes one base variant.
        nrows=3 if 'bases' in MAN else 8
        crop=base_source.crop((round(c*sw/4),round(r*sh/nrows),round((c+1)*sw/4),round((r+1)*sh/nrows))).resize((64,64),NN)
        ca=np.array(crop)
        # Terrain contrast compression keeps it behind the hero and avoids bright grass noise.
        center=np.median(ca[:,:,:3].reshape(-1,3),axis=0)
        if mat=='mud': center=np.array([49,49,49])
        elif mat=='grass': center=np.array([61,59,43])
        else:center=np.array([66,76,89])
        delta=ca[:,:,:3].astype(float)-np.median(ca[:,:,:3].reshape(-1,3),axis=0)
        ca[:,:,:3]=np.clip(np.maximum(delta,0)*.25+PAL[53] if mat=='puddle' else delta*.48+center,0,255)
        ca=np.array(quant(Image.fromarray(ca)))
        canonical=periodic(ca[:32,:32])
        variants=[]
        for n,(oy,ox) in enumerate([(0,0),(0,32),(32,0),(32,32)]):
            if 'bases' in MAN:
                cell=np.array(base_source.crop((round(n*sw/4),round(r*sh/3),round((n+1)*sw/4),round((r+1)*sh/3))).resize((32,32),NN))
                delta=cell[:,:,:3].astype(float)-np.median(cell[:,:,:3].reshape(-1,3),axis=0)
                cell[:,:,:3]=np.clip(np.maximum(delta,0)*.25+PAL[53] if mat=='puddle' else delta*.48+center,0,255)
                a=np.array(quant(Image.fromarray(cell)))
            else:a=ca[oy:oy+32,ox:ox+32].copy()
            # Match means using a very small color correction, then snap back to shared palette.
            rgb=a[:,:,:3].astype(float)
            rgb+=canonical[:,:,:3].mean(axis=(0,1))-rgb.mean(axis=(0,1))
            a[:,:,:3]=np.clip(rgb,0,255);a=np.array(quant(Image.fromarray(a)))
            # Shared source-art boundary pixels make ANY variant neighbor legal.
            a[0]=canonical[0];a[-1]=canonical[-1];a[:,0]=canonical[:,0];a[:,-1]=canonical[:,-1]
            variants.append(a);save(Image.fromarray(a),f'terrain/{mat}_base_{n+1:02}.png')
        bases[mat]=variants
    seams=[]
    tile_sets={}
    for group,other in enumerate(['grass','puddle']):
        tiles=[]
        for k in range(16):
            r,c=divmod(k,4);a=atlas[group*128+r*32:group*128+(r+1)*32,c*32:(c+1)*32].copy()
            bits=[(k>>b)&1 for b in [3,2,1,0]];tl,tr,bl,br=bits
            # Extract AI-authored material masks; use the geometry guide only to
            # repair topology/crossings. Visible texture pixels are sampled from
            # the AI-authored material cells, never generated by drawing code.
            rgb=a[:,:,:3].astype(float)
            if other=='grass':raw_mask=(rgb[:,:,0]+rgb[:,:,1]-2*rgb[:,:,2]>16)
            else:raw_mask=(rgb[:,:,2]-rgb[:,:,0]>9)
            yy,xx=np.mgrid[0:32,0:32]/31
            guide=tl*(1-xx)*(1-yy)+tr*xx*(1-yy)+bl*(1-xx)*yy+br*xx*yy
            mask=guide>=.5
            band=(abs(guide-.5)<.055)
            mask[band]=raw_mask[band]
            mask[0]=np.r_[np.full(16,tl),np.full(16,tr)]
            mask[-1]=np.r_[np.full(16,bl),np.full(16,br)]
            mask[:,0]=np.r_[np.full(16,tl),np.full(16,bl)]
            mask[:,-1]=np.r_[np.full(16,tr),np.full(16,br)]
            a=np.where(mask[:,:,None],bases[other][0],bases['mud'][0])
            # Canonical endpoint profiles. An edge depends ONLY on its two shared corners.
            # These are copied generated material pixels, not procedural texture drawing.
            def hedge(l,rr):
                m1=bases[other if l else 'mud'][0];m2=bases[other if rr else 'mud'][0]
                return np.concatenate([m1[0,:16],m2[0,16:]],axis=0)
            def vedge(t,b):
                m1=bases[other if t else 'mud'][0];m2=bases[other if b else 'mud'][0]
                return np.concatenate([m1[:16,0],m2[16:,0]],axis=0)
            a[0]=hedge(tl,tr);a[-1]=hedge(bl,br);a[:,0]=vedge(tl,bl);a[:,-1]=vedge(tr,br)
            tiles.append(a)
        out=np.zeros((128,128,4),dtype=np.uint8)
        for k,a in enumerate(tiles):r,c=divmod(k,4);out[r*32:(r+1)*32,c*32:(c+1)*32]=a
        save(Image.fromarray(out),f'terrain/mud_{other}_dualgrid.png');tile_sets[other]=tiles
        hp=vp=fail=0
        for i,a in enumerate(tiles):
            ib=[(i>>b)&1 for b in [3,2,1,0]]
            for j,b in enumerate(tiles):
                jb=[(j>>bb)&1 for bb in [3,2,1,0]]
                if [ib[1],ib[3]]==[jb[0],jb[2]]:
                    hp+=1;fail+=int(not np.array_equal(a[:,-1],b[:,0]))
                if [ib[2],ib[3]]==[jb[0],jb[1]]:
                    vp+=1;fail+=int(not np.array_equal(a[-1],b[0]))
        seams.append({'atlas':f'mud_{other}_dualgrid.png','horizontal_legal_pairs':hp,'vertical_legal_pairs':vp,'edge_mismatch_pairs':fail})
    # 8x8 mixed-variant tiling and representative connected dual-grid maps.
    rng=np.random.default_rng(127)
    for mat,variants in bases.items():
        out=Image.new('RGBA',(256,256))
        for y in range(8):
            for x in range(8):out.paste(Image.fromarray(variants[int(rng.integers(4))]),(32*x,32*y))
        save(out.resize((512,512),NN),f'qc/{mat}_base_8x8.png')
    for other,tiles in tile_sets.items():
        yy,xx=np.mgrid[0:10,0:16]
        # QA placement geometry only. All visible pixels come from generated tiles.
        field=((xx-7)**2/40+(yy-4)**2/13<1).astype(int)
        field[2:5,11:14]=1;field[4,7]=0;field[5,8]=0
        out=Image.new('RGBA',(15*32,9*32))
        for y in range(9):
            for x in range(15):
                k=8*field[y,x]+4*field[y,x+1]+2*field[y+1,x]+field[y+1,x+1]
                out.paste(Image.fromarray(tiles[int(k)]),(x*32,y*32))
        save(out.resize((960,576),NN),f'qc/mud_{other}_seam_preview.png')
    result={'corner_bit_order':['top_left_8','top_right_4','bottom_left_2','bottom_right_1'],
            'index_formula':'8*TL+4*TR+2*BL+BR; cell=(index%4,index//4)',
            'atlas_size':[128,128],'tile_size':[32,32],'seam_tests':seams,
            'base_edge_failures':sum(int(not(np.array_equal(a[0],a[-1]) and np.array_equal(a[:,0],a[:,-1]))) for v in bases.values() for a in v)}
    write('qc/terrain_seam_results.json',json.dumps(result,indent=2))
    return result

def walk():
    sheet=key(raw('walk'));w,h=sheet.size;cells=[];rects=[]
    for y in range(2):
        for x in range(3):
            cell=sheet.crop((round(x*w/3),round(y*h/2),round((x+1)*w/3),round((y+1)*h/2)))
            bbox=cell.getbbox();rects.append(bbox);cells.append(cell)
    scale=96/max(b[3]-b[1] for b in rects)
    frames=[];records=[]
    for k,(cell,b) in enumerate(zip(cells,rects)):
        obj=cell.crop(b);obj=obj.resize((round(obj.width*scale),round(obj.height*scale)),NN);obj=quant(obj,range(47))
        out=Image.new('RGBA',(80,96))
        # Torso root comes from fixed source-cell center, never median swinging feet.
        dx=40-round((cell.width/2-b[0])*scale);dy=96-obj.height
        out.alpha_composite(obj,(dx,dy));frames.append(out)
        records.append({'frame':k+1,'source_bbox':b,'source_to_native_scale':scale,'paste':[dx,dy],'bbox':out.getbbox(),'hand_redrawn_pixels':0})
    strip=Image.new('RGBA',(480,96))
    for k,im in enumerate(frames):save(im,f'player_anim/walk_side_{k+1:02}.png');strip.paste(im,(80*k,0))
    save(strip,'player_anim/walk_side_strip.png')
    # Fixed global GIF palette; transparent index0, no per-frame palette optimization.
    palette_flat=[0,0,0]+PAL.flatten().tolist()+[0,0,0]*(256-65)
    gif=[]
    for im in frames:
        a=np.array(im.resize((320,384),NN));ind=np.zeros(a.shape[:2],dtype=np.uint8)
        for i,c in enumerate(PAL):ind[(a[:,:,:3]==c).all(axis=2)&(a[:,:,3]>0)]=i+1
        p=Image.fromarray(ind);p.putpalette(palette_flat);p.info['transparency']=0;gif.append(p)
    buf=io.BytesIO();gif[0].save(buf,format='GIF',save_all=True,append_images=gif[1:],loop=0,duration=120,transparency=0,disposal=2,optimize=False)
    store_bytes('qc/walk_side_preview.gif',buf.getvalue())
    write('qc/walk_processing.json',json.dumps({'shared_native_scale':scale,'canvas':[80,96],'origin':[40,96],'fps':8.333333,'frames':records,'pixel_redraw_performed':False},indent=2))

if __name__=='__main__':
    palette();environment();compact();result=terrain();walk()
    print(json.dumps(result,indent=2))
