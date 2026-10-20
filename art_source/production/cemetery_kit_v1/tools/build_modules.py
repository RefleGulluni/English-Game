"""Assemble reusable Godot props from extracted generated art, never paint new props."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, json, math, shutil
ROOT=Path(__file__).resolve().parents[4];SRC=ROOT/'art_source/production/cemetery_kit_v1';OUT=ROOT/'art/cemetery_kit_v1'
def sheet(name,items,cols=4,cell=(320,320)):
    rows=math.ceil(len(items)/cols);im=Image.new('RGBA',(cols*cell[0],rows*cell[1]),(24,29,30,255));d=ImageDraw.Draw(im)
    for i,item in enumerate(items):
        p=ROOT/item['file'];a=Image.open(p).convert('RGBA');a.thumbnail((cell[0]-36,cell[1]-65),Image.Resampling.LANCZOS)
        x=(i%cols)*cell[0];y=(i//cols)*cell[1];im.alpha_composite(a,(x+(cell[0]-a.width)//2,y+32+(cell[1]-65-a.height)//2))
        d.text((x+12,y+8),item['name'],fill=(209,208,193));d.text((x+12,y+cell[1]-22),f"RGBA  {Image.open(p).width}x{Image.open(p).height} px",fill=(136,147,145))
    im.convert('RGB').save(SRC/'reviews'/name)
def emit(item):
    name=item['name'];folder=item['folder'];im=Image.open(ROOT/item['file']);w,h=im.size
    scale=(item['world_height']/h) if item['world_height'] else item['world_width']/w
    ww,wh=w*scale,h*scale;role=item['role'];p=OUT/folder/(name+'.tscn')
    lines=['[gd_scene load_steps=2 format=3]',f'[ext_resource type="Texture2D" path="res://{item["file"]}" id="1"]',f'[node name="{name}" type="Node2D"]',f'metadata/kit_id = "{name}"',f'metadata/role = "{role}"',f'metadata/display_size = Vector2({ww:.4f}, {wh:.4f})','metadata/contact_origin = "bottom_center"','metadata/collision_owner = "program"',f'[node name="Artwork" type="Sprite2D" parent="."]',f'position = Vector2(0, {-wh/2:.4f})',f'scale = Vector2({scale:.8f}, {scale:.8f})','texture_filter = 4','texture = ExtResource("1")']
    if role=='Foreground': lines+=['modulate = Color(0.38, 0.42, 0.43, 0.96)']
    if role=='Structure':
        # Socket coordinates are authored from actual visible grounding endpoints.
        sockets={'wall_straight':[[-ww*.49,0],[ww*.49,-wh*.37]],'wall_low':[[-ww*.49,0],[ww*.49,-wh*.44]],'wall_collapsed':[[-ww*.48,-2],[ww*.48,-wh*.3]],'wall_corner':[[-ww*.47,-wh*.09],[ww*.47,0]],'gate_base':[[-ww*.34,0],[ww*.34,0]],'fence_straight':[[-ww*.45,0],[ww*.45,0]],'fence_broken':[[-ww*.45,0],[ww*.45,0]],'cemetery_gate':[[-ww*.44,0],[ww*.44,0]],'fence_y':[[-ww*.37,0],[ww*.38,-wh*.55]],'fence_y_broken':[[-ww*.37,0],[ww*.38,-wh*.55]],'gate_y':[[-ww*.37,0],[ww*.38,-wh*.55]]}.get(name,[[-ww*.4,0],[ww*.4,0]])
        for label,point in zip(['SocketA','SocketB'],sockets):lines += [f'[node name="{label}" type="Marker2D" parent="."]',f'position = Vector2({point[0]:.4f}, {point[1]:.4f})']
        item['socket_a'],item['socket_b']=sockets
        item['connection_note']='Art-grounding sockets, projected/oblique; align sockets then inspect joints. Not a promise of orthogonal world collision. Never rotate sprite 90deg to create Y fence.'
    p.write_text('\n'.join(lines)+'\n');item['scene']=str(p.relative_to(ROOT));item['display_size']=[ww,wh];item['uniform_scale']=scale
def main():
    data=json.loads((SRC/'asset_manifest.json').read_text());assert all(x['ok'] for x in data)
    for x in data:
        if x['role'] in ['Prop','Structure','Foreground']: emit(x)
    # Third thin modular iron variant, derived from accepted generated complete straight fence.
    # Isolate the already-generated post, enabling program to assemble tight Y-axis posts/rails.
    raw=Image.open(OUT/'structures/fence_straight.png');box=(0,0,43,raw.height)
    post=raw.crop(box);post.save(OUT/'structures/fence_post.png')
    x=dict(name='fence_post',file='art/cemetery_kit_v1/structures/fence_post.png',folder='structures',world_height=74,world_width=None,role='Structure',ok=True,pixels=list(post.size),derived_from='fence_straight.png left intact post crop')
    emit(x);data.append(x)
    # Generated fog luminance is an editable matte, no atmosphere in terrain/props.
    fog=Image.open(SRC/'raw/fog.png').convert('RGB');a=np.array(fog,dtype=float);lum=a.mean(2)
    alpha=np.clip((lum-3)*1.8,0,140);rgba=np.empty((*lum.shape,4),dtype='uint8');rgba[:,:,:3]=[158,168,169];rgba[:,:,3]=alpha.astype('uint8')
    Image.fromarray(rgba).save(OUT/'foreground/fog_edge.png')
    data.append(dict(name='fog_edge',file='art/cemetery_kit_v1/foreground/fog_edge.png',role='VFX',folder='foreground',ok=True,pixels=list(fog.size),world_height=160,transparent=True))
    # Manifest is stable engine handoff; no collision baked into visual modules.
    (OUT/'module_manifest.json').write_text(json.dumps([x for x in data if x['role']!='Character Rig'],indent=2)+'\n')
    (SRC/'asset_manifest.json').write_text(json.dumps(data,indent=2)+'\n')
    sheet('02_wall_module_sheet.png',[x for x in data if x['role']=='Structure'],3,(400,280))
    sheet('03_graveyard_prop_sheet.png',[x for x in data if x['role']=='Prop'],4,(320,300))
    sheet('04_foreground_asset_sheet.png',[x for x in data if x['folder']=='foreground'],3,(400,300))
    sheet('05_player_rig_sheet.png',[x for x in data if x['role']=='Character Rig'],6,(240,260))
    sheet('09_vfx_source_sheet.png',[x for x in data if x['role']=='VFX'],3,(360,280))
    # Reuse real accepted skeleton art as independent cutout sources, not flattened bone pile.
    skeleton=[dict(name=p.stem,file=str(p.relative_to(ROOT))) for p in (ROOT/'art/enemies/skeleton_parts').glob('*.png')]
    sheet('06_grave_skeleton_rig_sheet.png',skeleton,5,(256,280))
    sheet('07_bone_remains_sheet.png',skeleton,5,(256,280))
    chisel=dict(name='weathered_chisel',file='art/loot/textures/weathered_chisel.png')
    sheet('08_weathered_chisel_asset.png',[chisel],1,(480,360))
    print(len(data),'assets; Godot modules, source sheets, independent fog matte emitted')
if __name__=='__main__':main()
