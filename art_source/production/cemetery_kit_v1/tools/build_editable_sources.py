"""Editable OpenRaster layers composed from delivered PNGs, not simulated PSD layers."""
from pathlib import Path
from PIL import Image,ImageDraw
import xml.etree.ElementTree as ET,zipfile,io,json,math
ROOT=Path(__file__).resolve().parents[4];SRC=ROOT/'art_source/production/cemetery_kit_v1';OUT=ROOT/'art/cemetery_kit_v1'
def png(im):
    b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()
def ora(name,items,cols=4,cell=(384,384)):
    rows=math.ceil(len(items)/cols);w,h=cols*cell[0],rows*cell[1]
    doc=ET.Element('image',w=str(w),h=str(h),name=name,version='0.0.3');stack=ET.SubElement(doc,'stack',name=name)
    merged=Image.new('RGBA',(w,h));records=[]
    target=SRC/'editable'/(name+'.ora')
    with zipfile.ZipFile(target,'w') as z:
        z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
        for i,item in enumerate(items):
            im=Image.open(ROOT/item['file']).convert('RGBA');im.thumbnail((cell[0]-24,cell[1]-24),Image.Resampling.LANCZOS)
            x=(i%cols)*cell[0]+(cell[0]-im.width)//2;y=(i//cols)*cell[1]+(cell[1]-im.height)//2
            path=f'data/layer{i:03}.png';z.writestr(path,png(im));ET.SubElement(stack,'layer',{'name':item['name'],'src':path,'x':str(x),'y':str(y),'opacity':'1.0','visibility':'visible','composite-op':'svg:src-over'})
            merged.alpha_composite(im,(x,y));records.append({'layer':item['name'],'source_png':item['file'],'x':x,'y':y})
        z.writestr('stack.xml',ET.tostring(doc,encoding='utf-8'));z.writestr('mergedimage.png',png(merged));thumb=merged.copy();thumb.thumbnail((256,256));z.writestr('Thumbnails/thumbnail.png',png(thumb))
    return {'file':str(target.relative_to(ROOT)),'layers':len(items),'meaning':'one separate whole editable asset per layer; original full-resolution PNG and generated raw atlas preserved separately','layer_sources':records}
def main():
    data=json.loads((SRC/'asset_manifest.json').read_text());report=[]
    report.append(ora('player_rig_parts',[x for x in data if x['role']=='Character Rig'],6))
    report.append(ora('cemetery_props',[x for x in data if x['role']=='Prop'],4))
    report.append(ora('wall_structures',[x for x in data if x['role']=='Structure'],3))
    report.append(ora('foreground_layers',[x for x in data if x['folder']=='foreground'],3,(512,384)))
    report.append(ora('vfx_sources',[x for x in data if x['folder']=='vfx'],3))
    terrain=[{'name':n,'file':f'art/cemetery_kit_v1/terrain/{n}.png'} for n in ['wet_stone_path','broken_stone_path','muddy_ground','mossy_stone','cracked_graveyard_floor','puddle_damp_edge']]
    report.append(ora('terrain_materials',terrain,3,(256,256)))
    skeleton=[dict(name=p.stem,file=str(p.relative_to(ROOT))) for p in sorted((ROOT/'art/enemies/skeleton_parts').glob('*.png'))]
    report.append(ora('skeleton_rig_parts',skeleton,5))
    (SRC/'editable/layer_sources.json').write_text(json.dumps(report,indent=2)+'\n')
    # Individual UI files are actual runtime transparent captures, not poster art.
    states=['idle','hovered','selected','invoking','used','retained','echo_copy','exhausted','disabled']
    sheet=Image.new('RGBA',(1320,248*9),(23,28,29,255));d=ImageDraw.Draw(sheet)
    for r,state in enumerate(states):
        for c,word in enumerate(['observe','shatter','erode']):
            im=Image.open(OUT/'ui'/f'{word}_{state}.png').convert('RGBA');sheet.alpha_composite(im,(c*440,r*248));d.text((c*440+10,r*248+10),word.upper()+' / '+state.upper(),fill=(159,171,167))
    sheet.convert('RGB').save(SRC/'reviews/10_word_sigil_ui_assets.png')
    print(json.dumps([{'file':x['file'],'layers':x['layers']} for x in report],indent=2))
if __name__=='__main__':main()
