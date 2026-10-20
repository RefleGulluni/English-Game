"""Extract generated material art, remove opposite-edge discontinuities, emit TileSet.
No procedural replacement painting; masks only control generated-material alpha.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, json
ROOT=Path(__file__).resolve().parents[4]
SRC=ROOT/'art_source/production/cemetery_kit_v1'
OUT=ROOT/'art/cemetery_kit_v1/terrain'
NAMES=['wet_stone_path','broken_stone_path','muddy_ground','mossy_stone','cracked_graveyard_floor','puddle_damp_edge']
def periodic(a):
    a=np.array(a.convert('RGB'),dtype=float)
    # Local smooth correction. End pixels match exactly; all interior paint survives.
    for axis in [1,0]:
        v=np.swapaxes(a,axis,0); delta=(v[-1]-v[0])/2
        band=24
        for j in range(band):
            w=(1-j/(band-1))**2
            v[j]+=delta*w; v[-1-j]-=delta*w
        a=np.swapaxes(v,0,axis)
    return Image.fromarray(np.clip(a,0,255).astype('uint8'))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    raw=Image.open(SRC/'raw/terrain.png'); w,h=raw.size
    atlas=Image.new('RGB',(256*6,256*4)); tiles=[]; qc=[]
    for i,name in enumerate(NAMES):
        x,y=i%3,i//3
        # Stay inside each generated sample, avoiding blended borders between materials.
        cx,cy=(x+.5)*w/3,(y+.5)*h/2
        im=periodic(raw.crop((int(cx-210),int(cy-210),int(cx+210),int(cy+210))).resize((256,256),Image.Resampling.LANCZOS))
        im.save(OUT/(name+'.png')); tiles.append(im)
        for variant in range(4):
            a=np.roll(np.roll(np.array(im),variant*61,axis=0),variant*97,axis=1)
            atlas.paste(Image.fromarray(a),(i*256,variant*256))
        a=np.array(im).astype(float)
        qc.append({'material':name,'opposite_edge_mean_delta':float(max(np.abs(a[0]-a[-1]).mean(),np.abs(a[:,0]-a[:,-1]).mean()))})
    atlas.save(OUT/'terrain_atlas.png')
    # Transparent edge/corner overlays on top of the muddy base. Bit order N/E/S/W.
    edge_atlas=Image.new('RGBA',(256*16,256*5)); yy,xx=np.mgrid[:256,:256]
    for row,i in enumerate([0,1,3,4,5]):
        for mask in range(16):
            alpha=np.ones((256,256),float)
            for bit,distance in enumerate([yy,255-xx,255-yy,xx]):
                if mask&(1<<bit): alpha*=np.clip(distance/42,0,1)**.8
            a=np.array(tiles[i].convert('RGBA')); a[:,:,3]=(alpha*255).astype('uint8')
            edge_atlas.paste(Image.fromarray(a),(mask*256,row*256))
    edge_atlas.save(OUT/'terrain_edges.png')
    lines=['[gd_resource type="TileSet" load_steps=5 format=3]','[ext_resource type="Texture2D" path="res://art/cemetery_kit_v1/terrain/terrain_atlas.png" id="1"]','[ext_resource type="Texture2D" path="res://art/cemetery_kit_v1/terrain/terrain_edges.png" id="2"]','[sub_resource type="TileSetAtlasSource" id="Base"]','texture = ExtResource("1")','texture_region_size = Vector2i(256, 256)']
    for x in range(6):
        for y in range(4): lines += [f'{x}:{y}/0 = 0']
    lines+=['[sub_resource type="TileSetAtlasSource" id="Edges"]','texture = ExtResource("2")','texture_region_size = Vector2i(256, 256)']
    for x in range(16):
        for y in range(5): lines += [f'{x}:{y}/0 = 0']
    lines+=['[resource]','tile_size = Vector2i(256, 256)','sources/0 = SubResource("Base")','sources/1 = SubResource("Edges")']
    (OUT/'cemetery_tileset.tres').write_text('\n'.join(lines)+'\n')
    mapping={'world_tile_size':128,'tile_size':256,'tilemap_scale':.5,'base_source_id':0,'base_materials':{n:{'atlas_x':i,'variant_y':[0,1,2,3]} for i,n in enumerate(NAMES)},'edges_source_id':1,'edge_rows':[NAMES[i] for i in [0,1,3,4,5]],'edge_atlas_x':'mask bits N=1 E=2 S=4 W=8; set bit if adjoining cell is muddy/outside this material','edge_usage':'Underlay muddy source0 (2,variant); overlay source1 (mask,material_row). Same origin and scale. No built-in terrain/autotile metadata; explicit mapping drives placement.','variant_policy':'Offset variants preserve light direction. Seamless SAME variant; different phase variants need blended overlays, never butt-join arbitrary phase variants.','collision':'none; program owns collision','source':'image_gen terrain.png; deterministic crop/periodic boundary correction only'}
    (OUT/'terrain_mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
    (SRC/'qc/terrain_seams.json').write_text(json.dumps(qc,indent=2)+'\n')
    # Sheet is assembled from delivered tiles, not generated illustration.
    sheet=Image.new('RGB',(1536,1152),(24,28,29)); d=ImageDraw.Draw(sheet)
    for i,tile in enumerate(tiles):
        x=(i%3)*512;y=(i//3)*576
        for row in range(2):
            for col in range(2): sheet.paste(tile,(x+col*256,y+row*256+32))
        d.text((x+12,y+8),NAMES[i],fill=(210,210,195))
    sheet.save(SRC/'reviews/01_cemetery_tile_sheet.png')
    print(json.dumps(qc)); assert max(q['opposite_edge_mean_delta'] for q in qc)<1
if __name__=='__main__':main()
