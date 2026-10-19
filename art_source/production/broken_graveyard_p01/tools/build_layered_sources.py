"""Build editable OpenRaster sources and review GIF from actual assets/captures."""
from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET
import json,zipfile,io,math
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'art_source/production/broken_graveyard_p01'

def png_bytes(image):
    out=io.BytesIO(); image.save(out,format='PNG'); return out.getvalue()

def ora(path,size,groups):
    root=ET.Element('image',{'version':'0.0.3','w':str(size[0]),'h':str(size[1]),'name':path.stem})
    stack=ET.SubElement(root,'stack')
    composite=Image.new('RGBA',size)
    entries=[]
    # groups authored back-to-front; XML layer stack uses front-to-back.
    for groupname,layers in groups:
        group=ET.Element('stack',{'name':groupname})
        for name,image,x,y in layers:
            src='data/layer_%03d.png'%len(entries)
            entries.append((src,png_bytes(image)))
            node=ET.Element('layer',{'name':name,'src':src,'x':str(x),'y':str(y),'opacity':'1.0','visibility':'visible','composite-op':'svg:src-over'})
            group.insert(0,node)
            composite.alpha_composite(image,(x,y))
        stack.insert(0,group)
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
        z.writestr('stack.xml',ET.tostring(root))
        z.writestr('mergedimage.png',png_bytes(composite),compress_type=zipfile.ZIP_DEFLATED)
        thumb=composite.copy(); thumb.thumbnail((256,256))
        z.writestr('Thumbnails/thumbnail.png',png_bytes(thumb))
        for name,data in entries: z.writestr(name,data,compress_type=zipfile.ZIP_DEFLATED)
    return composite

def main():
    folder=SOURCE/'editable'; folder.mkdir(exist_ok=True)
    poses=json.loads((SOURCE/'skeleton_pose_manifest.json').read_text())
    for mode,parts in poses.items():
        layers=[]
        for name,spec in parts.items():
            image=Image.open(ROOT/spec['texture']).convert('RGBA')
            sx,sy=spec['scale']
            image=image.resize((max(1,round(image.width*sx*3)),max(1,round(image.height*sy*3))),Image.Resampling.LANCZOS)
            image=image.rotate(-math.degrees(spec['rotation']),resample=Image.Resampling.BICUBIC,expand=True)
            x=round(256+spec['position'][0]*3-image.width/2)
            y=round(420+spec['position'][1]*3-image.height/2)
            layers.append((name,image,x,y))
        composite=ora(folder/('skeleton_'+mode+'.ora'),(512,512),[('Cutout parts',layers)])
        composite.save(SOURCE/'reviews'/('skeleton_'+mode+'_transparent.png'))
    layout=json.loads((SOURCE/'environment_layout.json').read_text())
    groups=[]
    for group in ['BackgroundGround','Backdrop','Midground','Foreground']:
        layers=[]
        for p in layout['placements']:
            if p['parent']!=group: continue
            image=Image.open(ROOT/'art/environments/textures'/(p['texture']+'.png')).convert('RGBA')
            w,h=map(round,p['display'])
            image=image.resize((w,h),Image.Resampling.LANCZOS)
            x,y=p['position']
            if p['texture']!='ground': x-=w*.5; y-=h*.5
            layers.append((p['name'],image,round(x),round(y)))
        groups.append((group,layers))
    ora(folder/'broken_graveyard_layers.ora',(1900,1100),groups)
    frames=[]
    for p in sorted((SOURCE/'reviews/animation_frames').glob('frame_*.png')):
        frames.append(Image.open(p).convert('RGB'))
    if frames:
        frames[0].save(SOURCE/'reviews/skeleton_collapse_reassembly.gif',save_all=True,append_images=frames[1:],duration=80,loop=0)
    vfx=[Image.open(p).convert('RGB') for p in sorted((SOURCE/'reviews/vfx_frames').glob('frame_*.png'))]
    if vfx:
        vfx[0].save(SOURCE/'reviews/echo_loot_vfx.gif',save_all=True,append_images=vfx[1:],duration=80,loop=0)
    print('Three layered .ora sources and actual Godot capture GIF written.')
if __name__=='__main__': main()
