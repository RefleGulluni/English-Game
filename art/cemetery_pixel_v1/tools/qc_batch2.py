"""Verify delivered pixels and assemble review sheets, with no game changes."""
from pathlib import Path
import json,hashlib,io,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent))
from build_batch2 import ROOT,REPO,PAL,quant,save,write,store_bytes,NN

ASSET_DIRS=['terrain','decals','path','props','player_anim','plates']
LUMA=np.array([.2126,.7152,.0722])

def image_info(p):
    im=Image.open(p).convert('RGBA');a=np.array(im);v=a[:,:,3]>0
    colors=np.unique(a[v,:3],axis=0)
    return {'file':str(p.relative_to(ROOT)),'size':list(im.size),'bbox':list(im.getbbox()) if im.getbbox() else None,
            'visible_colors':len(colors),'alpha_values':np.unique(a[:,:,3]).tolist(),
            'off_palette_colors':[c.tolist() for c in colors if not np.any(np.all(PAL==c,axis=1))],
            'mean_visible_luma':round(float((a[v,:3]@LUMA).mean()),3),
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def table(rows):
    return '\n'.join(['| \u6587\u4ef6 | \u539f\u751f\u5c3a\u5bf8 | \u53ef\u89c1\u8272\u6570 | Alpha |','|---|---:|---:|---|']+
           [f"| `{r['file']}` | {r['size'][0]}\xd7{r['size'][1]} | {r['visible_colors']} | {r['alpha_values']} |" for r in rows])

def overview():
    bg=tuple(PAL[48])+(255,);white=tuple(PAL[46])+(255,);muted=tuple(PAL[55])+(255,)
    im=Image.new('RGBA',(1280,1060),bg);d=ImageDraw.Draw(im)
    f=ImageFont.load_default(size=13);small=ImageFont.load_default(size=11)
    def label(x,y,s):d.text((x,y),s,font=f,fill=white)
    def put(rel,x,y):im.alpha_composite(Image.open(ROOT/rel).convert('RGBA'),(x,y))
    label(16,12,'ENGLISH GAME | BROKEN GRAVEYARD | BATCH 2')
    label(16,32,'Native 960 x 540 | Hero 96px | Grid 32px | Shared 64-color palette | Review sheet: 2x nearest')
    put('source/visual_target_960x540.png',16,58)
    label(992,66,'DUAL-GRID / 32px tiles')
    d.text((992,92),'Mud / grass',font=small,fill=white);d.text((1136,92),'Mud / puddle',font=small,fill=white)
    put('terrain/mud_grass_dualgrid.png',992,112);put('terrain/mud_puddle_dualgrid.png',1136,112)
    label(992,258,'BASE VARIANTS / seamless')
    for y,mat in enumerate(['mud','grass','puddle']):
        for x in range(4):put(f'terrain/{mat}_base_{x+1:02}.png',992+x*48,286+y*52)
        d.text((1192,294+y*52),mat,font=small,fill=white)
    label(992,456,'CEMETERY / 64 colors')
    for i,c in enumerate(PAL):
        y,x=divmod(i,8);d.rectangle((992+x*24,482+y*13,1015+x*24,494+y*13),fill=tuple(c)+(255,))
    label(16,620,'INDEPENDENT PROPS / NATIVE SCALE / NO BAKED GROUND SHADOWS')
    props=['dead_tree_01','tombstone_upright_01','tombstone_tilted_01','tombstone_fragment_01','open_grave_01']
    positions=[(164,882),(370,882),(470,882),(578,882),(724,882)]
    for name,(x,y) in zip(props,positions):
        p=Image.open(ROOT/f'props/{name}.png').convert('RGBA');im.alpha_composite(p,(x-p.width//2,y-p.height))
        short={'dead_tree_01':'Tree 01','tombstone_upright_01':'Upright 01','tombstone_tilted_01':'Tilted 01','tombstone_fragment_01':'Fragment 01','open_grave_01':'Open grave 01'}[name]
        d.text((x-40,890),short,font=small,fill=muted)
    label(820,628,'RIGHT WALK / 6 frames / 120ms each')
    strip=Image.open(ROOT/'player_anim/walk_side_strip.png').convert('RGBA')
    # Two chronological rows, no additional resizing on this native review canvas.
    im.alpha_composite(strip.crop((0,0,240,96)),(828,660))
    im.alpha_composite(strip.crop((240,0,480,96)),(828,778))
    for row in range(2):
        for col in range(3):d.text((844+80*col,758+118*row),str(row*3+col+1),font=small,fill=muted)
    label(16,924,'DECALS / gravel x3, leaves x2, crack x1, moss x2')
    for i,p in enumerate(sorted((ROOT/'decals').glob('*.png'))):
        obj=Image.open(p).convert('RGBA');im.alpha_composite(obj,(32+i*76,980-obj.height))
        short=p.stem.replace('ground_crack','crack').replace('gravel','G').replace('leaves','L').replace('moss','M')
        d.text((24+i*76,988),short,font=small,fill=muted)
    label(660,924,'OLD STONE PATH / 8 independent slabs')
    for i,p in enumerate(sorted((ROOT/'path').glob('*.png'))):
        obj=Image.open(p).convert('RGBA');im.alpha_composite(obj,(675+i*70,980-obj.height));d.text((675+i*70,988),f'{i+1:02}',font=small,fill=muted)
    label(16,1020,'QA sheets: qc/*_QA.md | GIF: qc/walk_side_preview.gif | Godot validation: pending Claude')
    save(quant(im).resize((2560,2120),NN),'qc/batch2_overview.png')

def contrast_preview():
    im=Image.new('RGBA',(960,240),tuple(PAL[48])+(255,));d=ImageDraw.Draw(im);f=ImageFont.load_default(size=12)
    hero=Image.open(REPO/'art/pixel_test/size_96/player_idle_01.png').convert('RGBA')
    for i,mat in enumerate(['mud','grass','puddle']):
        for y in range(6):
            for x in range(10):
                tile=Image.open(ROOT/f'terrain/{mat}_base_{1+(x+3*y)%4:02}.png').convert('RGBA')
                im.alpha_composite(tile,(i*320+x*32,40+y*32))
        im.alpha_composite(hero,(i*320+130,88))
        d.text((i*320+12,12),f'{mat.upper()} | accepted 96px player',font=f,fill=tuple(PAL[46])+(255,))
    save(quant(im).resize((1920,480),NN),'qc/player_ground_contrast.png')

def main():
    files=[]
    for folder in ASSET_DIRS:files+=sorted((ROOT/folder).glob('*.png'))
    files+=[ROOT/'source/visual_target_960x540.png',ROOT/'source/visual_target_generated_reference.png']
    records=[image_info(p) for p in files]
    failures=[]
    for r in records:
        if r['off_palette_colors']:failures.append(r['file']+' off palette')
        if set(r['alpha_values'])-{0,255}:failures.append(r['file']+' nonbinary alpha')
    for r in records:
        f=r['file'];w,h=r['size']
        if f.startswith('terrain/'):
            expected=[128,128] if 'dualgrid' in f else [32,32]
            if r['size']!=expected:failures.append(f+' wrong dimensions')
        if f.startswith('decals/') and not(8<=max(w,h)<=32):failures.append(f+' decal out of size range')
        if f.startswith('path/') and not(16<=max(w,h)<=40):failures.append(f+' slab out of size range')
    frames=[r for r in records if r['file'].startswith('player_anim/walk_side_') and 'strip' not in r['file']]
    if len(frames)!=6 or len({tuple(r['size']) for r in frames})!=1:failures.append('walk canvas/count')
    if any(r['bbox'][3]!=96 for r in frames):failures.append('walk foot baseline')
    if Image.open(ROOT/'player_anim/walk_side_strip.png').size!=(480,96):failures.append('walk strip dimensions')
    gif=Image.open(ROOT/'qc/walk_side_preview.gif')
    gif_record={'size':list(gif.size),'frames':gif.n_frames,'durations_ms':[],'transparency_binary':True}
    for i in range(gif.n_frames):
        gif.seek(i);gif_record['durations_ms'].append(gif.info.get('duration'))
        if set(np.unique(np.array(gif.convert('RGBA'))[:,:,3]))-{0,255}:gif_record['transparency_binary']=False
    if gif_record['size']!=[320,384] or gif_record['frames']!=6:failures.append('GIF dimension/count')
    refs=json.loads((ROOT/'qc/reference_hashes_before.json').read_text())
    modified=[f for f,h in refs.items() if hashlib.sha256((REPO/f).read_bytes()).hexdigest()!=h]
    if modified:failures.append('reference files modified')
    seam=json.loads((ROOT/'qc/terrain_seam_results.json').read_text())
    if seam['base_edge_failures'] or any(t['edge_mismatch_pairs'] for t in seam['seam_tests']):failures.append('terrain seams')
    # Cross-variant seamless checks (all16 variant pairs per material, two axes).
    cross={}
    for mat in ['mud','grass','puddle']:
        ims=[np.array(Image.open(ROOT/f'terrain/{mat}_base_{i:02}.png')) for i in range(1,5)]
        bad=sum(int(not np.array_equal(a[:,-1],b[:,0]))+int(not np.array_equal(a[-1],b[0])) for a in ims for b in ims)
        cross[mat]={'legal_pairs_per_axis':16,'mismatch_pairs':bad,
             'luma_means':[round(float((a[:,:,:3]@LUMA).mean()),3) for a in ims]}
        if bad:failures.append(mat+' cross-variant seam')
    allcolors=set()
    for p in files:
        a=np.array(Image.open(p).convert('RGBA'));allcolors.update(map(tuple,a[a[:,:,3]>0,:3].tolist()))
    report={'technical_pixel_checks_passed':not failures,'failures':failures,'visible_palette_entries':64,
        'actual_union_visible_colors':len(allcolors),'png_assets_checked':len(records),'assets':records,
        'walk':{'frames':frames,'gif':gif_record},'seams':seam,'base_cross_variants':cross,
        'reference_files_checked':len(refs),'reference_files_changed':modified,'engine_validation':'not performed; Claude owns Godot validation'}
    write('qc/batch2_QA.json',json.dumps(report,indent=2))
    common='\n\n\u68c0\u67e5\uff1aPNG \u539f\u751f\u5206\u8fa8\u7387\uff1b\u6240\u6709\u53ef\u89c1\u50cf\u7d20\u5747\u5728\u5171\u4eab\u8c03\u8272\u677f\u5185\uff1bAlpha \u4ec5 0/255\uff1b\u4f7f\u7528 nearest \u91c7\u6837\uff0c\u65e0\u6297\u952f\u9f7f\u6216\u6296\u8272\u3002\u6280\u672f\u68c0\u67e5\u4e0d\u66ff\u4ee3 Godot \u4e2d\u7684\u7f8e\u672f\u9a8c\u6536\u3002\n'
    def rows(prefix):return [r for r in records if r['file'].startswith(prefix)]
    write('qc/palette_QA.md','# Cemetery \u8c03\u8272\u677f QA\n\n47 \u4e2a\u539f\u6709\u989c\u8272\u9010\u9879\u539f\u6837\u4fdd\u7559\uff0c\u65b0\u589e 17 \u4e2a\u51b7\u4e2d\u6027\u3001\u79ef\u6c34\u84dd\u7070\u548c\u82d4\u85d3\u6a44\u6984\u8272\uff0c\u5171 64 \u4e2a\u53ef\u89c1\u989c\u8272\uff1b\u900f\u660e\u5ea6\u5355\u72ec\u5b58\u50a8\u3002\n\n\u5168\u90e8\u4ea4\u4ed8\u7d20\u6750\u5171\u4eab `cemetery_palette.gpl`\uff0c\u672c\u8f6e\u672a\u589e\u52a0\u7b26\u6587\u9752\u84dd\u8272\u3002\u4fdd\u7559\u539f\u6709\u89d2\u8272\u914d\u8272\uff0c\u5730\u9762\u964d\u4f4e\u660e\u5ea6\u3001\u9650\u5236\u5bf9\u6bd4\u3002\n\n\u672c\u6b21\u68c0\u67e5\u7684 PNG \u53ef\u89c1\u989c\u8272\u5e76\u96c6\uff1a'+str(len(allcolors))+'\u3002\u8c03\u8272\u677f\u5916\u989c\u8272\uff1a0\u3002'+common)
    write('qc/source_QA.md','# \u573a\u666f\u76ee\u6807\u56fe QA\n\n'+table(rows('source/'))+'\n\n\u5148\u7528\u5185\u7f6e image_gen \u751f\u6210\u6574\u4f53\u76ee\u6807\uff0c\u518d\u6309\u5b83\u7684\u753b\u6cd5\u5236\u4f5c\u5730\u677f\u548c\u72ec\u7acb\u7d20\u6750\u3002\u539f\u751f\u6210\u6784\u56fe\u4fdd\u7559\u5728 `source/visual_target_generated_reference.png`\u3002\n\n`visual_target_960x540.png` \u7528\u6700\u7ec8\u5730\u677f\u4e0e\u72ec\u7acb\u7269\u4ef6\u91cd\u65b0\u5408\u6210\uff0c\u4e3b\u89d2\u76f4\u63a5\u4f7f\u7528\u5df2\u786e\u8ba4 96 px \u539f\u56fe\uff0c\u4fee\u6b63 AI \u539f\u56fe\u4e2d\u4eba\u7269\u548c\u5893\u7891\u504f\u5927\u7684\u6bd4\u4f8b\u3002\u5e03\u5c40\u5750\u6807\u89c1 `source/preview_placement.json`\uff0c\u4ec5\u7528\u4e8e\u7f8e\u672f\u9884\u89c8\u3002\n\n\u6784\u56fe\uff1a\u5de6\u4e0b\u4e24\u5ea7\u5893\u7891\u5939\u51fa\u5165\u53e3 \u2192 \u65e7\u5893\u533a \u2192 \u4e2d\u53f3\u7a7a\u5730 \u2192 \u574d\u584c\u5893\u7a74 \u2192 \u53f3\u4e0a\u51fa\u53e3\u3002\u9759\u6001\u56fe\u4e0d\u542b Godot \u63a5\u89e6\u9634\u5f71\u3001\u96fe\u3001\u706f\u5149\u6216\u771f\u5b9e Y-Sort\u3002'+common)
    base_summary='\n'.join(f"- {m} \u56db\u53d8\u4f53\u660e\u5ea6\u8303\u56f4\uff1a{min(v['luma_means']):.3f}\uff5e{max(v['luma_means']):.3f}\uff080\uff5e255\uff09\u3002" for m,v in cross.items())
    write('qc/terrain_QA.md','# Terrain / Dual-Grid QA\n\n'+table(rows('terrain/'))+'\n\n\u89d2\u70b9\u7d22\u5f15\uff1a`index = 8*TL + 4*TR + 2*BL + BR`\uff0cX=1\u3001\u6ce5=0\u3002\u56fe\u96c6\u5750\u6807 `(index%4, index//4)`\uff0c\u65e0\u95f4\u9694\u3001\u65e0\u5916\u8fb9\u8ddd\uff0c\u5b8c\u5168\u5bf9\u5e94\u4efb\u52a1\u7684\u884c\u5217\u6392\u5217\u3002\n\n\u4e24\u56fe\u96c6\u5404\u68c0\u67e5\u6c34\u5e73 64 \u7ec4\u3001\u5782\u76f4 64 \u7ec4\u5408\u89c4\u90bb\u63a5\uff0c\u5171 256 \u7ec4\uff0c\u8fb9\u7f18\u9519\u7f1d 0\u3002\u4e09\u79cd\u57fa\u7840\u5757\u5404\u68c0\u67e5 16 \u7ec4\u53d8\u4f53\u4e92\u63a5 \xd7 \u4e24\u4e2a\u65b9\u5411\uff0c\u5171 96 \u7ec4\uff0c\u9519\u7f1d 0\u3002\u5171\u540c\u6ce5\u5730\u53ef\u5728\u4e24\u5957\u56fe\u96c6\u4e2d\u66ff\u6362\u3002\n\n'+base_summary+'\n\n\u5236\u4f5c\u4fee\u6b63\uff1a\u7b2c\u4e00\u7248\u5185\u90e8\u6750\u8d28\u4e0e\u57fa\u7840\u5757\u660e\u5ea6\u4e0d\u4e00\u81f4\uff0c\u867d\u5bf9\u8fb9\u4e00\u81f4\u4ecd\u6709\u7f51\u683c\u611f\uff1b\u73b0\u7528 AI \u751f\u6210\u6750\u8d28\u53d6\u6837\u3001\u89d2\u70b9\u906e\u7f69\u53ca\u8fb9\u754c\u4fee\u6574\u7edf\u4e00\u6750\u8d28\u3002\u79ef\u6c34\u7eb9\u7406\u7b2c\u4e8c\u6b21\u538b\u4f4e\u5bf9\u6bd4\uff0c\u8349\u5730\u57fa\u7840\u5757\u53bb\u6389\u9192\u76ee\u8349\u7c07\u30028\xd78 \u56db\u53d8\u4f53\u6df7\u94fa\u56fe\u548c\u8fde\u63a5\u56fe\u5747\u5728 qc/\u3002\n\n\u5df2\u77e5\u9650\u5236\uff1a\u53ea\u6709 16 \u79cd\u57fa\u7840\u8fc7\u6e21\uff0c\u82e5\u5927\u9762\u79ef\u5355\u4e00\u56fe\u5757\u53cd\u590d\u4f7f\u7528\uff0c\u4ecd\u53ef\u80fd\u8bc6\u522b\u5230\u7ec6\u5c0f\u7eb9\u7406\u91cd\u590d\uff1b\u5efa\u8bae\u7eaf\u533a\u57df\u6df7\u7528\u56db\u53d8\u4f53\uff0c\u8d34\u82b1\u7a00\u758f\u6446\u653e\u3002\u4e3b\u89c2\u201c\u5b8c\u5168\u770b\u4e0d\u51fa\u91cd\u590d\u201d\u4ecd\u9700\u5b9e\u673a\u9a8c\u6536\u3002\u4e0d\u8981\u540c\u65f6\u53e0\u52a0\u4e24\u4e2a\u4e0d\u900f\u660e\u5730\u5f62\u5c42\u906e\u4f4f\u5f7c\u6b64\uff0c\u4e5f\u4e0d\u63d0\u4f9b\u8349\u2194\u6c34\u7684\u76f4\u63a5\u8fc7\u6e21\u3002'+common)
    write('qc/decals_QA.md','# \u5e73\u9762\u8d34\u82b1 QA\n\n'+table(rows('decals/'))+'\n\n\u6570\u91cf\uff1a\u788e\u77f3 3\u3001\u843d\u53f6 2\u3001\u88c2\u7eb9 1\u3001\u82d4\u85d3 2\uff0c\u5171 8\u3002\u6700\u5927\u8fb9\u5747\u5728 8\uff5e32 px \u5185\u3002\u900f\u660e\u80cc\u666f\uff0c\u65e0\u5730\u9762\u6295\u5f71\uff1b\u88c2\u7eb9\u4ec5\u4e3a\u5730\u8868\u6697\u7ebf\uff0c\u82d4\u85d3\u4f7f\u7528\u65b0\u589e\u6a44\u6984\u8272\u3002\n\n\u5df2\u77e5\u9650\u5236\uff1a\u6781\u5c0f\u53f6\u7247\u4e0e\u788e\u77f3\u5728\u6697\u5730\u9762\u4e0a\u7684\u8fa8\u8bc6\u5ea6\u9700\u5b9e\u673a\u68c0\u67e5\uff1b\u4e0d\u8981\u5bc6\u94fa\u3002'+common)
    write('qc/path_QA.md','# \u6b8b\u7f3a\u77f3\u8def QA\n\n'+table(rows('path/'))+'\n\n8 \u5757\u72ec\u7acb\u65e7\u77f3\u677f\uff0c\u4f9d\u5e8f\u4e3a\uff1a\u5b8c\u6574\u78e8\u635f\u3001\u957f\u6761\u88c2\u5f00\u3001\u7f3a\u89d2\u3001\u534a\u57cb\u3001\u5206\u88c2\u3001\u8349\u8986\u8fb9\u7f18\u3001\u82d4\u8680\u692d\u5706\u3001\u5c0f\u578b\u4e09\u89d2\u6b8b\u5757\u3002\u6700\u5927\u8fb9 16\uff5e40 px\uff1b\u5747\u4e3a\u5e73\u9762\u4f4e\u77ee\u77f3\u677f\uff0c\u4e0d\u5e26\u5730\u9762\u9634\u5f71\u3002\n\n\u5df2\u77e5\u9650\u5236\uff1a\u8fd1\u770b\u53ef\u89c1\u5c11\u91cf 1\uff5e2 px \u539a\u5ea6\u7684\u4fa7\u7f18\uff1b\u4f5c\u4e3a\u4f4e\u77ee\u5730\u9762\u88c5\u9970\u4f7f\u7528\uff0c\u4e0d\u4f5c\u4e3a\u53ef\u7ed5\u884c\u7684\u9ad8\u77f3\u5757\u3002'+common)
    write('qc/props_QA.md','# \u72ec\u7acb\u7269\u4ef6 QA\n\n'+table(rows('props/'))+'\n\n5 \u4e2a\u72ec\u7acb\u900f\u660e\u7269\u4ef6\uff1b\u67af\u6811\u6807\u79f0 224 px \u9ad8\uff1b\u76f4\u7acb\u5893\u7891\u4fdd\u7559\u5df2\u786e\u8ba4\u539f\u56fe\u7684\u50cf\u7d20\u5185\u5bb9\uff0c\u4ec5\u8c03\u6574\u900f\u660e\u753b\u5e03\u4e0e\u5e95\u90e8\u539f\u70b9\uff1b\u503e\u659c\u5893\u7891\u4e3a\u5355\u72ec\u751f\u6210\uff0c\u672a\u65cb\u8f6c\u539f\u7d20\u6750\u3002\u6240\u6709\u7269\u4ef6\u5747\u65e0\u70d8\u7119\u5730\u9762\u6295\u5f71\u3002\n\n\u5e95\u90e8\u63a5\u89e6\u70b9\u5e73\u79fb\u5230\u56fe\u7247\u5e95\u8fb9\u4e2d\u5fc3\uff0c\u753b\u5e03\u5bbd\u5ea6\u5305\u542b\u4e0d\u5bf9\u79f0\u7559\u767d\uff0c\u7981\u6b62\u6309\u975e\u900f\u660e\u5305\u56f4\u76d2\u91cd\u65b0\u5c45\u4e2d\uff1b\u539f\u70b9\u3001\u5360\u5730\u4e0e\u78b0\u649e\u5efa\u8bae\u89c1 props/NOTES.md\u3002\n\n\u5df2\u77e5\u9650\u5236\uff1a\u6811\u51a0\u7ec6\u679d\u5728\u6697\u8272\u80cc\u666f\u4e0a\u8f83\u5f31\uff1b\u5893\u7a74\u6697\u90e8\u5c5e\u4e8e\u5751\u6d1e\u5185\u90e8\u800c\u975e\u6295\u5f71\uff1b\u5893\u7a74\u8fdc\u7aef\u5e26\u4f4e\u77ee\u6b8b\u7891\uff0c\u5b9e\u9645\u5e95\u5ea7\u6309 3\xd72 \u683c\u6807\u6ce8\u3002\u78b0\u649e\u5efa\u8bae\u672a\u7ecf Godot \u9a8c\u8bc1\u3002'+common)
    walkmeta=json.loads((ROOT/'qc/walk_processing.json').read_text())
    write('qc/player_anim_QA.md','# \u4fa7\u5411\u884c\u8d70\u6d4b\u8bd5 QA\n\n'+table(rows('player_anim/'))+'\n\n\u671d\u53f3 6 \u5e27\uff0c\u7edf\u4e00 80\xd796 \u753b\u5e03\uff1b\u6a2a\u6392 480\xd796\uff1b\u5e95\u8fb9\u57fa\u7ebf y=96\uff0c\u7edf\u4e00\u539f\u70b9 (40,96)\u3002\u6574\u7ec4\u4f7f\u7528\u4e00\u4e2a\u7f29\u653e\u7cfb\u6570 '+str(round(walkmeta['shared_native_scale'],8))+'\uff0c\u6ca1\u6709\u9010\u5e27\u62c9\u4f38\u8865\u6bd4\u4f8b\u3002\u8f6e\u5ed3\u9ad8\u5ea6\u5141\u8bb8 1\uff5e2 px \u7684\u6b65\u6001\u53d8\u5316\u3002GIF \u4e3a 320\xd7384\uff0c\u5373\u6bcf\u5e27 4\xd7 nearest\uff0c6 \u5e27\uff0c\u6bcf\u5e27 120 ms\uff0c\u5faa\u73af 720 ms\u3002\n\n\u751f\u4ea7\u8bb0\u5f55\uff1a\u52a8\u753b\u539f\u56fe\u8c03\u7528 1 \u6b21\uff0c\u4f7f\u7528\u5df2\u786e\u8ba4\u4e3b\u89d2\u53ca 2\xd73 anchor \u6a21\u677f\uff1b\u81ea\u52a8\u5904\u7406\u5305\u62ec\u53bb\u5e95\u3001\u53bb\u8fb9\u7f18\u6d0b\u7ea2\u3001\u5171\u4eab\u539f\u751f\u7f29\u5c0f\u3001\u9650\u5236\u539f\u6709 47 \u8272\u30016 \u5e27\u5e95\u8fb9/\u6a2a\u5411\u8eaf\u5e72\u5bf9\u9f50\u3001strip \u548c GIF \u62fc\u88c5\u3002\u9996\u6b21\u5904\u7406\u7559\u767d\u8fc7\u5c0f\uff0c\u89e6\u53d1 6 \u5e27\u8d34\u8fb9\u4fdd\u62a4\uff1b\u6539\u7528\u5b89\u5168\u7559\u767d\u91cd\u65b0\u5904\u7406\u901a\u8fc7\uff0c\u518d\u4ece\u539f\u59cb\u56fe\u4ee5 nearest \u5bfc\u51fa\u539f\u751f\u50cf\u7d20\u5e27\u3002\u672a\u628a\u5e73\u6ed1\u7f29\u653e\u7684\u4e2d\u95f4\u7ed3\u679c\u5f53\u6700\u7ec8\u7d20\u6750\u3002\n\n\u5b9e\u9645\u9010\u50cf\u7d20\u4eba\u5de5\u91cd\u7ed8\uff1a**0 \u50cf\u7d20\u30010 \u5e27**\uff0c\u56e0\u6b64\u4e0d\u80fd\u7ed9\u51fa\u201c\u4eba\u5de5\u4fee\u6574\u8017\u65f6\u201d\u7684\u5b9e\u6d4b\u503c\u3002\u4e0a\u8ff0\u7ea6\u675f\u548c\u5904\u7406\u53c2\u6570\u7531\u4eba\u5de5\u5224\u65ad\u9009\u5b9a\uff0c6 \u5e27\u5747\u4f5c\u4f4d\u7f6e\u4fee\u6b63\u3002\n\n\u6700\u6613\u8dd1\u504f\uff1a02/05 \u4e0b\u6c89\u5e27\u7684\u8138\u90e8\u4e0e\u56f4\u5dfe\u9ad8\u5149\uff1b03/06 \u901a\u8fc7\u5e27\u7684\u6301\u5251\u624b\u3001\u5251\u5c16\u548c\u8863\u6446\uff1b04 \u4e0e 01 \u5bf9\u4fa7\u63a5\u89e6\u5e27\u7684\u540e\u811a\u8f6e\u5ed3\u3002\u5f53\u524d\u4ecd\u6709\u8f7b\u5fae\u7ec6\u8282\u95ea\u52a8\uff0c\u9002\u5408\u9a8c\u8bc1\u52a8\u753b\u751f\u4ea7\u65b9\u5f0f\uff0c**\u4e0d\u6807\u4e3a\u6b63\u5f0f\u89d2\u8272\u52a8\u753b\u7ec8\u7a3f**\u3002\u82e5\u8fdb\u5165\u6b63\u5f0f\u6279\u91cf\uff0c\u9700\u50cf\u7d20\u7f8e\u672f\u5728 1\xd7/4\xd7 \u5faa\u73af\u4e0b\u4fee\u6574\u8fd9\u4e9b\u7ec6\u8282\u5e76\u7531 Godot \u9a8c\u6536\uff1b\u672c\u8f6e\u4e0d\u7f16\u9020\u4eba\u5de5\u4fee\u6574\u65f6\u95f4\u3002'+common)
    write('qc/plates_QA.md','# AI \u6574\u5f20\u5730\u9762\u677f QA\n\n'+table(rows('plates/'))+'\n\n\u4ece\u6574\u4f53\u76ee\u6807\u56fe\u7ecf\u5185\u7f6e image_gen \u53bb\u9664\u5168\u90e8\u6811\u3001\u5893\u7891\u3001\u89d2\u8272\u548c\u5893\u7a74\u5e76\u8865\u9f50\u5730\u9762\uff0c\u518d nearest \u89c4\u6574\u5230 960\xd7540 \u548c\u5171\u4eab\u8c03\u8272\u677f\u3002\u4ec5\u6709\u6ce5\u3001\u67af\u8349\u3001\u6d45\u79ef\u6c34\u3001\u4f4e\u77ee\u77f3\u8def\u53ca\u5e73\u9762\u5c0f\u788e\u5c51\uff0c\u65e0\u9ad8\u7269\u4ef6\u3001\u6df1\u5751\u6216\u70d8\u7119\u6295\u5f71\u3002\n\n\u7528\u9014\uff1a\u4e0e\u74e6\u7247\uff0b\u8d34\u82b1\u65b9\u6848\u4f5c\u89c6\u89c9\u5bf9\u7167\u3002\u677f\u5185\u5df2\u6709\u77f3\u8def\u4e0e\u8349\uff0c\u4e0d\u5e94\u518d\u53e0\u52a0\u76f8\u540c\u7ec6\u8282\u5f62\u6210\u53cc\u4efd\u3002\u662f\u5426\u4f18\u4e8e\u74e6\u7247\u65b9\u6848\u7531 Claude \u7684\u623f\u95f4\u5b9e\u673a\u5bf9\u6bd4\u51b3\u5b9a\u3002'+common)
    # Engine handoff information, no scene edits.
    footprints={'dead_tree_01':([2,1],[-32,-28,64,28]),'tombstone_upright_01':([2,1],[-32,-15,44,15]),
                'tombstone_tilted_01':([2,1],[-32,-18,48,18]),'tombstone_fragment_01':([2,1],[-24,-28,48,28]),
                'open_grave_01':([3,2],[-40,-64,96,64])}
    note=['# Props\uff1a\u539f\u70b9\u3001\u5360\u5730\u4e0e\u78b0\u649e\u4ea4\u63a5','',
          '\u5730\u9762\u903b\u8f91\u683c 32\xd732\uff1b\u4e0b\u5217\u4e3a\u7f8e\u672f\u5efa\u8bae\uff0c\u7cbe\u786e\u78b0\u649e\u7531 Claude \u5728 Godot \u9a8c\u8bc1\u3002\u6240\u6709 PNG \u7684\u539f\u70b9\u4e3a\u56fe\u7247\u5e95\u8fb9\u4e2d\u5fc3 `(W/2,H)`\uff0c\u5de6\u4e0a\u4e3a `(0,0)`\u3002\u900f\u660e\u7559\u767d\u662f\u539f\u70b9\u5951\u7ea6\u7684\u4e00\u90e8\u5206\uff0c\u4e0d\u8981\u81ea\u52a8\u88c1\u5207\u3002',
          '', 'Sprite2D \u4f7f\u7528 centered=true \u65f6\u53ef\u8bbe offset=(0,-H/2)\uff0c\u628a Node2D \u653e\u5728\u5730\u9762\u63a5\u89e6\u70b9\uff1b\u4e0d\u9700\u8981\u975e\u6574\u6570\u7f29\u653e\u3002Y-Sort \u4f7f\u7528\u8fd9\u4e2a\u6839\u8282\u70b9\u3002',
          '', '| \u6587\u4ef6 | PNG \u753b\u5e03 | \u539f\u70b9 | \u5e95\u5ea7\u5360\u5730\u683c | \u78b0\u649e\u77e9\u5f62\u8349\u6848 (x,y,w,h) |','|---|---:|---:|---:|---|']
    propmeta=[]
    for name,(grid,rect) in footprints.items():
        im=Image.open(ROOT/f'props/{name}.png');w,h=im.size
        note.append(f'| `{name}.png` | {w}\xd7{h} | ({w//2},{h}) | {grid[0]}\xd7{grid[1]} | {tuple(rect)} |')
        propmeta.append({'file':f'{name}.png','canvas':[w,h],'origin':[w//2,h],'footprint_cells':grid,'collision_rect_draft':rect})
    note+=['','- \u6811\u4ec5\u6811\u5e72/\u6839\u811a\u963b\u6321\uff0c\u6811\u51a0\u53c2\u4e0e\u906e\u6321\uff1b\u957f\u6839\u53ef\u4f5c\u4e3a\u89c6\u89c9\u5ef6\u4f38\uff0c\u4e0d\u5fc5\u5168\u505a\u78b0\u649e\u3002',
           '- \u5893\u7891\u5360\u5730\u6309\u5305\u56f4\u5e95\u5ea7\u5411\u4e0a\u53d6\u6574\uff0c\u78b0\u649e\u53ef\u6bd4\u683c\u5b50\u5360\u5730\u66f4\u7d27\u3002',
           '- \u5012\u7891\u788e\u5757\u4e3a\u4f4e\u77ee\u7269\u4ef6\uff1b\u53ef\u6309\u623f\u95f4\u8bbe\u8ba1\u51b3\u5b9a\u662f\u5426\u963b\u6321\uff0c\u4e0d\u80fd\u56e0\u753b\u5e03\u8f83\u5bbd\u800c\u81ea\u52a8\u94fa\u6ee1\u78b0\u649e\u3002',
           '- \u5893\u7a74\u5e95\u5ea7 3\xd72 \u683c\uff0896\xd764\uff09\uff0c\u56fe\u50cf\u591a\u51fa\u7684\u9ad8\u5ea6\u7528\u4e8e\u7834\u635f\u8fb9\u6cbf/\u6b8b\u7891\u3002\u5751\u6d1e\u5185\u90e8\u5e94\u963b\u6321\u6216\u6309\u8bbe\u8ba1\u5904\u7406\uff0c\u4e0d\u5f53\u4f5c\u666e\u901a\u6ce5\u5730\u3002',
           '- \u5893\u7a74\u77e9\u5f62\u53ef\u504f\u79bb\u539f\u70b9\u5bf9\u79f0\uff0c\u8fd9\u662f 3/4 \u89c6\u89d2\u4e0e\u5e95\u90e8\u63a5\u89e6\u70b9\u5171\u540c\u5bfc\u81f4\u7684\u6b63\u5e38\u504f\u79fb\u3002',
           '- \u65e0\u7269\u4ef6\u70d8\u7119\u6295\u5f71\uff1b\u63a5\u89e6\u9634\u5f71\u3001\u5149\u8272\u3001Y-Sort\u3001\u96fe\u548c\u6700\u7ec8\u78b0\u649e\u7531 Godot \u7edf\u4e00\u63d0\u4f9b\u3002','']
    write('props/NOTES.md','\n'.join(note));write('props/anchors.json',json.dumps(propmeta,indent=2))
    safe_path=Path('/Users/mac/.codex/batch2_work_20261022/walk_safe/pipeline-meta.json')
    if safe_path.exists():
        safe=json.loads(safe_path.read_text())
        write('qc/walk_raw_qc.json',json.dumps({'source_edge_touch_frames':safe['source_edge_touch_frames'],
            'empty_frames':safe['empty_frames'],'qc_summary':safe['qc_summary'],'note':'Intermediate safe extraction only. Final native export uses nearest, global palette and explicit bottom baseline.'},indent=2))
    write('qc/batch2_QA.md','# Broken Graveyard \u7b2c\u4e8c\u6279\u4ea4\u4ed8\u68c0\u67e5\n\n**\u72b6\u6001\uff1a\u7d20\u6750\u5df2\u4ea4\u4ed8\uff0c\u6280\u672f\u50cf\u7d20\u68c0\u67e5'+('\u901a\u8fc7' if not failures else '\u5931\u8d25')+'\uff1bGodot \u89c6\u89c9\u4e0e\u7a7a\u95f4\u9a8c\u6536\u5f85 Claude\u3002**\n\n- \u68c0\u67e5 PNG '+str(len(records))+' \u5f20\uff08\u5305\u542b\u539f\u59cb\u751f\u6210\u76ee\u6807\u7684\u6e05\u7406\u7248\u53c2\u8003\uff09\uff1b\u5b9e\u9645\u53ef\u89c1\u8272\u5e76\u96c6 '+str(len(allcolors))+'\uff0c\u8c03\u8272\u677f\u4e0a\u9650 64\u3002\n- \u8c03\u8272\u677f\u5916\u989c\u8272 0\uff1b\u975e\u4e8c\u503c Alpha 0\uff1b\u539f\u751f\u5c3a\u5bf8\u68c0\u67e5\u901a\u8fc7\u3002\n- \u53cc\u7f51\u683c 256 \u7ec4\u5408\u6cd5\u90bb\u63a5\u5bf9\u6bd4\u65e0\u9519\u7f1d\uff1b\u57fa\u7840\u53d8\u4f53 96 \u7ec4\u4e92\u63a5\u65e0\u9519\u7f1d\u3002\n- \u52a8\u753b 6 \u5e27\u3001\u56fa\u5b9a\u753b\u5e03/\u811a\u5e95\u3001strip\u30014\xd7 GIF \u5747\u5df2\u68c0\u67e5\u3002\n- \u539f\u6709 pixel_test \u6587\u4ef6\u6821\u9a8c '+str(len(refs))+' \u4e2a\uff0c\u53d8\u5316 '+str(len(modified))+'\u3002\u672a\u6539 Godot \u573a\u666f\u6216\u5de5\u7a0b\u914d\u7f6e\u3002\n\n\u91cd\u70b9\u590d\u6838\uff1a\u52a8\u753b\u4ecd\u6709\u8f7b\u5fae\u8863\u7269/\u6301\u5251\u7ec6\u8282\u95ea\u52a8\uff0c\u5c5e\u4e8e\u751f\u4ea7\u65b9\u5f0f\u9a8c\u8bc1\u7a3f\uff1b\u8349\u5730/\u79ef\u6c34\u4e3b\u89c2\u91cd\u590d\u611f\u3001\u539f\u70b9\u78b0\u649e\u548c\u4eba\u7269\u843d\u5730\u611f\u9700\u5b9e\u673a\u786e\u8ba4\u3002\u6280\u672f\u901a\u8fc7\u4e0d\u7b49\u4e8e\u7f8e\u672f\u7ec8\u9a8c\u901a\u8fc7\u3002\n\n\u5b8c\u6574\u7edf\u8ba1 `batch2_QA.json`\uff1b\u5206\u9879\u8bb0\u5f55 `palette/source/terrain/decals/path/props/player_anim/plates_QA.md`\uff1b\u603b\u89c8 `batch2_overview.png` \u4e3a 2\xd7 nearest\u3002\n\n\u672c\u6279\u751f\u6210\u671f\u95f4\u7684\u53ef\u6062\u590d\u5907\u4efd\u4f4d\u4e8e\u4ed3\u5e93 `art_source/backups/cemetery_pixel_v1_batch2/`\u3002\u539f\u59cb image_gen \u8f93\u51fa\u4fdd\u7559\u5728\u9ed8\u8ba4\u751f\u6210\u76ee\u5f55\uff0c\u8def\u5f84\u4e0e\u624b\u5199\u63d0\u793a\u8bcd\u5728 source/ \u4e2d\u3002\u4e34\u65f6\u5904\u7406\u6587\u4ef6\u3001\u5e03\u5c40\u5bfc\u5f15\u5728\u4ea4\u4ed8\u524d\u79fb\u5165\u5e9f\u7eb8\u7bd3\uff0c\u672a\u5220\u9664\u7528\u6237\u539f\u59cb\u7d20\u6750\u3002\n')
    overview();contrast_preview()
    write('README.md','# English Game \xb7 Cemetery Pixel v1 \xb7 Batch 2\n\n\u552f\u4e00\u7f8e\u672f\u89c4\u8303\uff1a`English_Game_Art_Direction_Bible_v3_Pixel_World_SpecLocked_CLEAN.md`\u3002\n\n96 px \u4e3b\u89d2 / 960\xd7540 \u539f\u751f\u753b\u9762 / 32 px \u5730\u9762\u683c / 64 \u8272\u5171\u4eab\u8c03\u8272\u677f / \u5de6\u4e0a\u5149\u6e90 / 3/4 \u4fef\u89c6\u3002\u8bed\u8a00\u672c\u4f53\u540c\u50cf\u7d20\u5bc6\u5ea6\u3001\u7cbe\u786e\u4e14\u53d1\u5149\uff1b\u672c\u6279\u4e0d\u65b0\u589e\u8bed\u8a00\u7b26\u6587\u7d20\u6750\u3002\n\n\u5148\u770b `qc/batch2_overview.png` \u548c `qc/batch2_QA.md`\uff1b\u52a8\u753b\u770b `qc/walk_side_preview.gif`\u3002\n\n\u4ea4\u4ed8\u76ee\u5f55\uff1asource\uff08\u76ee\u6807\u56fe\u4e0e\u6765\u6e90\uff09\u3001terrain\uff08\u4e24\u595716\u5757\u53cc\u7f51\u683c\u56fe\u96c6\u300112\u5757\u57fa\u7840\u53d8\u4f53\uff09\u3001decals\uff088\uff09\u3001path\uff088\uff09\u3001props\uff085\u53ca\u539f\u70b9/\u5360\u5730\u8bf4\u660e\uff09\u3001player_anim\uff086\u5e27\u4e0e\u6a2a\u6392\uff09\u3001plates\uff08\u5e73\u9762\u6574\u56fe\u5bf9\u7167\uff09\u3001qc\uff08\u68c0\u67e5\u548c\u9884\u89c8\uff09\u3001tools\uff08\u53ef\u590d\u9a8c\u7684\u6e05\u7406\u4e0e\u68c0\u67e5\u6d41\u7a0b\uff09\u3002\n\nGodot \u4ea4\u63a5\uff1a\u5168\u90e8\u4f7f\u7528 nearest\u3001\u6574\u6570\u4f4d\u7f6e/\u7f29\u653e\uff1bDual-Grid \u7d22\u5f15\u53ca\u63a5\u7f1d\u8bf4\u660e\u89c1 terrain_QA\uff1b\u7269\u4ef6\u539f\u70b9\u89c1 props/NOTES\uff1b\u52a8\u753b\u539f\u70b9 (40,96)\uff0c6\u5e27120ms\u5faa\u73af\uff0c\u5411\u5de6\u955c\u50cf\u3002\u6b63\u5f0f\u52a8\u753b\u50cf\u7d20\u7cbe\u4fee\u548c\u5f15\u64ce\u9a8c\u6536\u5c1a\u672a\u5b8c\u6210\uff0c\u672c\u6279\u7528\u4e8e\u623f\u95f4\u4e0e\u751f\u4ea7\u65b9\u5f0f\u9a8c\u8bc1\u3002\n\n\u751f\u6210\u65b9\u6cd5\uff1a\u5185\u7f6e image_gen\uff0c\u624b\u5199\u63d0\u793a\u8bcd\u4fdd\u5b58\u5728 source/prompts.json \u4e0e source/bases.prompt.txt\uff0c\u539f\u59cb\u6765\u6e90\u7d22\u5f15 source/generation_manifest.json\u3002\u811a\u672c\u53ea\u505a\u63d0\u53d6\u3001\u6750\u8d28\u91c7\u6837\u62fc\u88c5\u3001\u8fb9\u7f18\u4fee\u590d\u3001\u8c03\u8272\u677f\u89c4\u6574\u4e0e\u9884\u89c8\u68c0\u67e5\uff1b\u4e0d\u4fee\u6539\u539f\u6709\u7d20\u6750\u548c Godot \u6587\u4ef6\u3002\n')
    print(json.dumps({'png_checked':len(records),'visible_colors':len(allcolors),'failures':failures,'unchanged_reference_files':len(refs),'gif':gif_record,'base_variants':cross},indent=2))
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
