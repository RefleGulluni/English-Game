"""Geometry-only debug images; these are NOT game artwork."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
S=Path(__file__).resolve().parent;Q=S.parent/'qc';rows=json.loads((S/'layout_contract.json').read_text())['tiles'];a=np.array(Image.open(S/'01_best_native_crop_palette_preview.png').convert('RGBA'));m=a[:,:,3]>0
tiles={r['code']:m[r['y']*32:r['y']*32+32,r['x']*32:r['x']*32+32] for r in rows}
def debug(mask):
 rgb=np.empty(mask.shape+(3,),np.uint8);rgb[:]=[41,42,38];rgb[mask]=[185,176,151];return Image.fromarray(rgb)
debug(m).resize((768,768),Image.Resampling.NEAREST).save(Q/'path_alpha_failed_candidate_6x.png')
layout=json.loads((S/'failed_candidate_brush_layout.json').read_text());canvas=np.zeros((288,480),bool)
for y,row in enumerate(layout['tile_codes']):
 for x,code in enumerate(row):canvas[y*32:y*32+32,x*32:x*32+32]=tiles[code]
im=debug(canvas[:270]);im.resize((960,540),Image.Resampling.NEAREST).save(Q/'path_brush_alpha_failed_candidate_2x.png')
pairs=[]
for ar in rows:
 for br in rows:
  if ar['tr']==br['tl'] and ar['br']==br['bl'] and ar['tr']!=ar['br']:
   aa=tiles[ar['code']];bb=tiles[br['code']];n=int((aa[:,-1]!=bb[:,0]).sum());pairs.append((n,ar['code'],br['code']))
pairs.sort(reverse=True);out=Image.new('RGB',(768,960),(28,30,27));dr=ImageDraw.Draw(out)
for i,(n,ac,bc) in enumerate(pairs[:8]):
 x=i%2*384;y=i//2*240;patch=np.concatenate([tiles[ac],tiles[bc]],axis=1);pic=debug(patch).resize((384,192),Image.Resampling.NEAREST);out.paste(pic,(x,y+32));dr.text((x+4,y+5),f'{ac} | {bc}: {n}/32 alpha mismatch',fill=(225,217,199));dr.line((x+192,y+32,x+192,y+223),fill=(190,66,66))
out.save(Q/'path_worst_legal_joins_debug_6x.png')
print('Worst legal mixed-edge pair:',pairs[0])
