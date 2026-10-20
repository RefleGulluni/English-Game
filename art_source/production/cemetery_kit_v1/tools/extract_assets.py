"""Complete-object crops + installed sprite processor; no painted sprite creation."""
from pathlib import Path
from PIL import Image, ImageDraw
import subprocess, concurrent.futures, json, numpy as np, shutil
ROOT=Path(__file__).resolve().parents[4]
SRC=ROOT/'art_source/production/cemetery_kit_v1'
OUT=ROOT/'art/cemetery_kit_v1'
PROC=Path('/Users/mac/.codex/skills/generate2dsprite/scripts/generate2dsprite.py')
JOBS=[]
def add(name,raw,box,folder,world_height,role='Prop',width=None):
    JOBS.append(dict(name=name,raw=raw,box=box,folder=folder,world_height=world_height,role=role,world_width=width))
def grid(raw,names,cols,rows,folder,heights,role='Prop'):
    im=Image.open(SRC/'raw'/f'{raw}.png');w,h=im.size
    for i,n in enumerate(names):
        x,y=i%cols,i//cols
        add(n,raw,[round(x*w/cols),round(y*h/rows),round((x+1)*w/cols),round((y+1)*h/rows)],folder,heights[i] if isinstance(heights,list) else heights,role)
def plan():
    grid('graves',[f'grave_{i:02}' for i in range(1,9)],4,2,'props', [102,75,113,91,85,93,94,61])
    for n,b,h,w in [
        ('wall_straight',[0,0,870,386],None,256),('wall_corner',[870,0,1536,386],None,200),
        ('wall_collapsed',[0,386,865,687],None,256),('wall_low',[865,386,1536,687],None,256),
        ('gate_base',[0,687,880,1024],None,256),('wall_end_pier',[880,687,1536,1024],96,None)]:
        add(n,'walls',b,'structures',h,'Structure',w)
    for n,b,h,w in [('fence_straight',[0,0,1671,300],None,192),('fence_broken',[0,300,1671,570],None,192),('cemetery_gate',[0,570,1671,941],None,228)]:
        add(n,'fences',b,'structures',h,'Structure',w)
    for n,h in [('tree_a',270),('tree_b',235)]: add(n,n,None,'props',h)
    parts=['head','torso','upper_arm_l','upper_arm_r','forearm_l','forearm_r','hand_l','hand_r','thigh_l','thigh_r','shin_l','shin_r','boot_l','boot_r','weapon','coat_front','coat_back','cloak','belt_pouch','clasp']
    xs=[0,280,560,840,1122];ys=[0,300,535,795,1065,1402]
    for i,n in enumerate(parts):
        r,c=divmod(i,4);b=[xs[c],ys[r],xs[c+1],ys[r+1]]
        if n=='weapon': b=[560,790,840,1158]
        if n=='coat_front': b=[840,790,1122,1112]
        if n=='clasp': b=[840,1115,1122,1402]
        if n=='cloak': b=[280,1100,600,1402]
        if n=='belt_pouch': b=[600,1160,875,1360]
        if n=='clasp': b=[910,1145,1110,1320]
        add(n,'player_parts',b,'player/parts',None,'Character Rig')
    if (SRC/'raw/player_back.png').exists():
        for n,b in [('head_back',[0,0,640,560]),('torso_back',[640,0,1287,565]),('cloak_back',[0,565,663,1222]),('coat_back_view',[663,565,1287,1222])]:
            add(n,'player_back',b,'player/parts',None,'Character Rig')
    if (SRC/'raw/fences_y.png').exists():
        grid('fences_y',['fence_y','fence_y_broken','gate_y'],3,1,'structures',[110,110,130],'Structure')
    if (SRC/'raw/dressing.png').exists():
        grid('dressing',['stone_pieces','long_bones','funeral_cloth','dead_weeds','bone_cluster','stone_chips','urn_fragments','grass_tuft'],4,2,'props',[24,13,17,38,22,12,22,22])
    if (SRC/'raw/foreground.png').exists():
        add('close_grave_edge','foreground',[887,0,1774,443],'foreground',63,'Foreground')
        add('fence_foreground','foreground',[0,460,887,887],'foreground',125,'Foreground')
    if (SRC/'raw/branches.png').exists():
        grid('branches',['branch_left','branch_right'],2,1,'foreground',150,'Foreground')
    if (SRC/'raw/vfx.png').exists():
        grid('vfx',['echo_fragment','loot_reflection','dust','bone_splinters','cord_tension','sigil_fragments'],3,2,'vfx',[5,4,30,5,30,22],'VFX')
def process(job):
    name=job['name']; original=Image.open(SRC/'raw'/(job['raw']+'.png'))
    crop=original.crop(job['box']) if job['box'] else original
    path=SRC/'raw/crops'/f'{name}.png';path.parent.mkdir(parents=True,exist_ok=True);crop.save(path)
    tmp=SRC/'processing'/name
    result=subprocess.run(['python3',str(PROC),'process','--input',str(path),'--target','asset','--mode','single','--rows','1','--cols','1','--cell-size','512','--fit-scale','0.88','--align','center','--trim-border','0','--component-mode','all','--min-component-area','3','--strict-qc','--output-dir',str(tmp)],capture_output=True,text=True)
    if result.returncode: return dict(job,ok=False,error=result.stdout[-800:]+result.stderr[-800:])
    im=Image.open(tmp/'single-1.png').convert('RGBA');a=np.array(im,dtype=float)
    spill=np.minimum(a[:,:,0],a[:,:,2])-a[:,:,1];affected=(spill>22)&(a[:,:,3]>0)
    a[:,:,3][affected]*=np.clip(1-(spill[affected]-18)/55,0,1)
    a[:,:,2][affected]=np.minimum(a[:,:,2][affected],a[:,:,1][affected]+9)
    a[:,:,0][affected]=np.minimum(a[:,:,0][affected],a[:,:,1][affected]*1.3+10)
    if job['folder']=='vfx' and name in ['echo_fragment','loot_reflection','dust','sigil_fragments']:
        # Recover neutral pale foreground from magenta-composited semi-transparent paint.
        # This is chroma-matte decontamination, not replacement illustration.
        opacity=np.clip(1-(np.minimum(a[:,:,0],a[:,:,2])-a[:,:,1])/255,0.02,1)
        luminance=np.clip(a[:,:,1]/opacity,0,255)
        a[:,:,3]*=opacity
        a[:,:,0]=luminance; a[:,:,1]=luminance*.99; a[:,:,2]=luminance*.95
    im=Image.fromarray(np.clip(a,0,255).astype('uint8'));im=im.crop(im.getbbox())
    padded=Image.new('RGBA',(im.width+4,im.height+4));padded.alpha_composite(im,(2,2))
    target=OUT/job['folder']/f'{name}.png';target.parent.mkdir(parents=True,exist_ok=True);padded.save(target)
    shutil.copy2(tmp/'pipeline-meta.json',SRC/'qc'/(name+'.json'))
    return dict(job,ok=True,pixels=list(padded.size),file=str(target.relative_to(ROOT)),alpha_extrema=list(padded.getchannel('A').getextrema()))
def main():
    import sys
    plan()
    if '--player-only' in sys.argv: JOBS[:]=[j for j in JOBS if j['folder']=='player/parts']
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(process,JOBS))
    (SRC/'asset_manifest.json').write_text(json.dumps(results,indent=2)+'\n')
    for r in results: print(r['name'],r['ok'],r.get('pixels',r.get('error')))
    assert all(r['ok'] for r in results)
if __name__=='__main__':main()
