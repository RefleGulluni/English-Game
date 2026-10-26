from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,re,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-entry-pillar-20261026');O=R/'art/cemetery_v3/props';D=O/'qc/entry_gate_sources';g=json.loads((D/'grid.json').read_text());r=json.loads((D/'cleanup.json').read_text());raw=np.array(Image.open(D/'01_generated_original.png').convert('RGB'));rest=np.array(Image.open(D/'02_restored_native_cells.png').convert('RGBA'));xs=g['x_boundaries'];ys=g['y_boundaries'];count=0
for y in range(rest.shape[0]):
 for x in range(rest.shape[1]):
  if rest[y,x,3]:assert np.array_equal(rest[y,x,:3],raw[(ys[y]+ys[y+1])//2,(xs[x]+xs[x+1])//2]);count+=1
ar=rest.copy();c=ar[:,:,:3].astype(int);ar[(c[:,:,0]-c[:,:,1]>30)&(c[:,:,2]-c[:,:,1]>30)]=0
ms=Image.new('1',(79,198));ImageDraw.Draw(ms).polygon([tuple(x) for x in r['layer_mask_polygon']],fill=1);ms=np.array(ms,dtype=bool);pal=np.array(r['inherited_palette_rgb']);verified=[]
for n,mask in [('gate_pillar_tall_01',ms),('gate_pillar_tall_01_base',~ms)]:
 p=ar.copy();p[~mask]=0;p=p[r['source_row_lookup']][:,r['source_column_lookup']].copy();fg=p[:,:,3]>0;rgb=p[fg,:3].astype(int)
 if n.endswith('_base'):rgb=np.rint(rgb*.68).astype(int)
 ix=((rgb[:,None]-pal[None])**2).sum(2).argmin(1);p[fg,:3]=pal[ix];out=np.zeros((192,96,4),dtype=np.uint8);out[25:25+p.shape[0],8:8+p.shape[1]]=p;actual=np.array(Image.open(O/(n+'.png')).convert('RGBA'));assert np.array_equal(actual,out);assert set(np.unique(actual[:,:,3]))<={0,255};verified.append(n)
# Link targets in delivered QA must resolve.
qa=O/'qc/entry_props_QA.md';links=re.findall(r'\]\(([^)]+)\)',qa.read_text());missing=[x for x in links if not (qa.parent/x).exists()];assert not missing,missing
protected=json.loads((W/'protected.json').read_text());unchanged=[p for p,h in protected.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()==h];assert len(unchanged)==len(protected)-1
proof={'source_cell_center_rgb_checks':count,'all_match':True,'final_layers_reconstructed_exactly':verified,'qa_links_checked':len(links),'all_qa_links_resolve':True,'preexisting_files_unchanged':len(unchanged),'manifest_backup_sha256':hashlib.sha256((O/'qc/backups/entry_gate_before_20261026/props_manifest.json').read_bytes()).hexdigest()};(D/'verification.json').write_text(json.dumps(proof,indent=2));print(proof)
for n in ['verify.py','write_qa.py']:shutil.copy2(W/n,D/'production'/n)
for n in ['family_reference_4x.png','hero_8x.png']:shutil.copy2(W/n,D/'production'/n)
