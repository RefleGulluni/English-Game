"""Deterministic crops/chroma cleanup of image_gen assets; no creative painting."""
from pathlib import Path
from PIL import Image
import json, shutil, subprocess, concurrent.futures

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'art_source/production/broken_graveyard_p01'
PROCESSOR = Path('/Users/mac/.codex/skills/generate2dsprite/scripts/generate2dsprite.py')
PARTS = ['skull','ribcage','pelvis','weapon','upper_arm_l','upper_arm_r','forearm_l','forearm_r','thigh_l','thigh_r','shin_l','shin_r','hand_l','hand_r','foot_l','foot_r','shoulder_cloth','hip_cloth','burial_cord','nails']

def run():
    raw = SOURCE / 'raw'
    atlas = Image.open(raw / 'skeleton_parts.png')
    # Generated rows have nonuniform whitespace, so complete-object gutters take precedence.
    xs, ys = [0,280,560,840,1122], [0,285,540,823,1075,1402]
    crops = []
    for i,name in enumerate(PARTS):
        row,col=divmod(i,4)
        box=(xs[col],ys[row],xs[col+1],ys[row+1])
        atlas.crop(box).save(raw / (name+'.crop.png'))
        crops.append({'name':name,'source':'skeleton_parts.png','box':box})
    (SOURCE/'qc/complete_object_crops.json').write_text(json.dumps(crops,indent=2)+'\n')
    tasks=[(name,raw/(name+'.crop.png'),'art/enemies/skeleton_parts/'+name+'.png') for name in PARTS]
    tasks += [(name,raw/(name+'.png'),'art/environments/textures/'+name+'.png') for name in ['grave_a','grave_b','bracken','rubble','fence','wall']]
    tasks += [(name,raw/(name+'.png'),dest) for name,dest in [('chisel','art/loot/textures/weathered_chisel.png'),('clasp','art/characters/textures/lexicon_clasp_quiet.png'),('player','art/characters/textures/wordbearer_base.png')]]
    def one(task):
        name,src,dest=task
        out=SOURCE/'processed'/name
        args=['python3',str(PROCESSOR),'process','--input',str(src),'--target','asset','--mode','single','--rows','1','--cols','1','--cell-size','512','--output-dir',str(out),'--fit-scale','0.88','--align','center','--trim-border','0','--component-mode','all','--min-component-area','6','--strict-qc']
        result=subprocess.run(args,capture_output=True,text=True)
        if result.returncode: return name,False,result.stderr[-600:]
        im=Image.open(out/'single-1.png').convert('RGBA')
        bbox=im.getbbox()
        target=ROOT/dest
        target.parent.mkdir(parents=True,exist_ok=True)
        im.crop(bbox).save(target)
        meta=json.loads((out/'pipeline-meta.json').read_text())
        shutil.copy2(out/'pipeline-meta.json',SOURCE/'qc'/(name+'.json'))
        return name,True,im.crop(bbox).size
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(one,tasks))
    (SOURCE/'qc/processing_results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
    assert all(x[1] for x in results), 'Some crops failed strict QC'
    out=ROOT/'art/environments/textures/ground.png'
    out.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(raw/'ground.png',out)

if __name__=='__main__': run()
