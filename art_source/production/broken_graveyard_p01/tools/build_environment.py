"""Serialize image-based reusable modules and the agreed collision-aligned layout."""
from pathlib import Path
from PIL import Image
import json
ROOT=Path(__file__).resolve().parents[4]
TEX=ROOT/'art/environments/textures'

def main():
    # Extract complete post and one metal rail from generated fence, not procedural art.
    raw=Image.open(ROOT/'art_source/production/broken_graveyard_p01/raw/fence.png').convert('RGB')
    import numpy as np
    a=np.array(raw); mask=(a[:,:,0]>150)&(a[:,:,2]>130)&(a[:,:,1]<100)
    rgba=np.dstack((a, np.where(mask,0,255).astype('uint8')))
    im=Image.fromarray(rgba)
    for name,box in [('fence_post',(340,130,500,715)),('fence_rail',(505,361,574,387))]:
        part=im.crop(box); part=part.crop(part.getbbox()); part.save(TEX/(name+'.png'))
    modules=ROOT/'art/environments/modules'; modules.mkdir(exist_ok=True)
    for name in ['grave_a','grave_b','bracken','rubble','fence','wall','fence_post','fence_rail']:
        text=f'[gd_scene load_steps=2 format=3]\n[ext_resource type="Texture2D" path="res://art/environments/textures/{name}.png" id="1"]\n[node name="{name.title()}" type="Sprite2D"]\ntexture = ExtResource("1")\n'
        (modules/(name+'.tscn')).write_text(text)
    names=['ground','grave_a','grave_b','bracken','rubble','wall','fence_post','fence_rail']
    lines=['[gd_scene load_steps=13 format=3]']
    for i,name in enumerate(names):
        lines.append(f'[ext_resource type="Texture2D" path="res://art/environments/textures/{name}.png" id="{i+1}"]')
    lines += ['[ext_resource type="Script" path="res://art/environments/occlusion.gd" id="9"]','[ext_resource type="Shader" path="res://art/environments/fog.gdshader" id="10"]','[sub_resource type="ShaderMaterial" id="fog"]','shader = ExtResource("10")','shader_parameter/strength = 0.07','[node name="BrokenGraveyardVisual" type="Node2D"]','script = ExtResource("9")']
    for name,z in [('BackgroundGround',-20),('Backdrop',-10),('Midground',-4),('Foreground',4),('Atmosphere',5)]:
        lines += [f'[node name="{name}" type="Node2D" parent="."]',f'z_index = {z}']
    placements=[]
    def sprite(name,texture,pos,display,parent,rotation=0,centered=True):
        image=Image.open(TEX/(texture+'.png'))
        scale=(display[0]/image.width,display[1]/image.height)
        lines.extend([f'[node name="{name}" type="Sprite2D" parent="{parent}"]',f'position = Vector2({pos[0]}, {pos[1]})',f'scale = Vector2({scale[0]}, {scale[1]})',f'rotation = {rotation}',f'texture = ExtResource("{names.index(texture)+1}")'])
        if not centered: lines.append('centered = false')
        placements.append(dict(name=name,texture=texture,position=pos,display=display,parent=parent,occlusionClass='foreground_fade' if parent=='Foreground' else 'ground_or_backdrop',actorSafeArea='avoid central walk strip y440..560',occupantPolicy='fade when player behind' if parent=='Foreground' else 'unchanged'))
    sprite('Foundation','ground',(0,0),(1900,1100),'BackgroundGround',centered=False)
    for i in range(7):
        sprite('NorthWall'+str(i),'wall',(i*285+140,34),(300,92),'Backdrop')
        sprite('SouthWall'+str(i),'wall',(i*285+140,1088),(300,92),'Foreground')
    for col in range(7):
        x=631+col*170
        for row,base_y in enumerate([400,710]):
            tex='grave_a' if (row+col)%2==0 else 'grave_b'
            h=86 if tex=='grave_a' else 67
            original=Image.open(TEX/(tex+'.png'))
            width=round(h*original.width/original.height)
            sprite('Headstone_%d_%d'%(col,row),tex,(x,base_y-h*.5),(width,h),'Midground' if row==0 else 'Foreground')
    for i,y in enumerate([80,220,370,615,755,900,1040]):
        sprite('FencePost'+str(i),'fence_post',(480,y-32),(18,64),'Midground')
    for i,(a,b) in enumerate([(80,220),(220,370),(615,755),(755,900),(900,1040)]):
        sprite('FenceRail'+str(i),'fence_rail',(480,(a+b)*.5-20),(6,b-a),'Midground')
    for i,(x,y) in enumerate([(140,100),(1750,130),(180,980),(1770,1000)]):
        sprite('DeadBracken'+str(i),'bracken',(x,y),(95,69),'Foreground' if y>800 else 'Backdrop')
    lines += ['[node name="Fog" type="Polygon2D" parent="Atmosphere"]','material = SubResource("fog")','polygon = PackedVector2Array(0, 0, 1900, 0, 1900, 1100, 0, 1100)','uv = PackedVector2Array(0, 0, 1, 0, 1, 1, 0, 1)']
    # Ten external resources + one subresource + scene itself = 12.
    lines[0]='[gd_scene load_steps=12 format=3]'
    index=lines.index('[node name="BrokenGraveyardVisual" type="Node2D"]')
    lines.insert(index+1,'texture_filter = 4')
    (ROOT/'art/environments/env_broken_graveyard_visual.tscn').write_text('\n'.join(lines)+'\n')
    p=ROOT/'art_source/production/broken_graveyard_p01/environment_layout.json'
    p.write_text(json.dumps(dict(world=[1900,1100],collision_owner='scenes/world/world_broken_graveyard.tscn',collision_changed=False,placements=placements),indent=2)+'\n')
    print('Environment scene, eight reusable modules and explicit placement data written.')
if __name__=='__main__': main()
