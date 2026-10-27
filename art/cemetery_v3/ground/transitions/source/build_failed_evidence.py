"""Inspect native crop only; no rescaling or alternate terrain method.
The candidate is explicitly NOT a usable or approved corner tileset.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,subprocess,sys
S=Path(__file__).resolve().parent;T=S.parent;G=T.parent;R=G.parents[2];Q=T/'qc'
raw=Image.open(S/'01_best_native_crop_raw.png').convert('RGBA');a=np.array(raw);mask=a[:,:,3]>0
# Palette-only material preview; geometry is the literal native crop. Do not
# generate a new silhouette or synthesize detail from the layout guide.
strip=Image.fromarray(a[:,:,:3][mask][None,:,:]);reduced=strip.quantize(colors=24,dither=Image.Dither.NONE).convert('RGB');pal,counts=np.unique(np.array(reduced).reshape(-1,3),axis=0,return_counts=True)
L=pal@np.array([.2126,.7152,.0722]);center=float(np.average(L,weights=counts));new=np.array([84.,81.,69.])+.85*(L-center)[:,None]+.25*(pal-L[:,None]);new+=np.array([84.,81.,69.])-np.average(new,axis=0,weights=counts);new=np.rint(new).clip(0,255).astype('uint8')
ids=np.argmin(((a[:,:,:3].astype(float)[:,:,None,:]-pal[None,None,:,:])**2).sum(3),axis=2);a[:,:,:3]=new[ids];a[~mask]=0;candidate=Image.fromarray(a);candidate.save(S/'01_best_native_crop_palette_preview.png')
(S/'01_preview_palette.json').write_text(json.dumps({'purpose':'Color-only FAILED CANDIDATE preview. Alpha and native geometry unchanged. No final tile is being published.','mapping':[{'from':c.tolist(),'to':n.tolist()} for c,n in zip(pal,new)]},indent=2)+'\n')
contract=json.loads((S/'layout_contract.json').read_text());tiles={row['code']:candidate.crop((row['x']*32,row['y']*32,row['x']*32+32,row['y']*32+32)) for row in contract['tiles']}
bases=[Image.open(G/f'base/ground_base_{i:02d}.png').convert('RGBA') for i in [1,2]]
def ground(w,h):
 out=Image.new('RGBA',(w,h));rng=np.random.default_rng(1048)
 for y in range(0,h,128):
  for x in range(0,w,224):out.alpha_composite(bases[int(rng.integers(2))],(x,y))
 return out
def big(im,k,name):im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST).save(Q/name)
tiled=ground(384,384)
for y in range(3):
 for x in range(3):tiled.alpha_composite(candidate,(x*128,y*128))
big(tiled,2,'path_tiled_failed_candidate_2x.png')
preview=ground(128,128);preview.alpha_composite(candidate);big(preview,6,'path_crop_failed_candidate_6x.png')
grid=preview.resize((768,768),Image.Resampling.NEAREST);dr=ImageDraw.Draw(grid)
for n in range(1,4):dr.line((n*192,0,n*192,767),fill=(185,72,72));dr.line((0,n*192,767,n*192),fill=(185,72,72))
for row in contract['tiles']:dr.text((row['x']*192+5,row['y']*192+5),row['code'],fill=(242,226,205))
grid.save(Q/'path_crop_grid_failed_candidate_6x.png')

def distance_segment(xx,yy,p,q):
 p=np.array(p);v=np.array(q)-p;t=np.clip(((xx-p[0])*v[0]+(yy-p[1])*v[1])/float(v@v),0,1)
 return np.sqrt((xx-p[0]-t*v[0])**2+(yy-p[1]-t*v[1])**2)
yy,xx=np.indices((10,16));xx=xx*32;yy=yy*32
main=[(0,208),(144,208),(208,144),(224,80),(320,80),(480,128)]
branch=[(208,144),(288,208),(416,288)]
d1=np.minimum.reduce([distance_segment(xx,yy,p,q) for p,q in zip(main,main[1:])]);d2=np.minimum.reduce([distance_segment(xx,yy,p,q) for p,q in zip(branch,branch[1:])]);nodes=(d1<=31)|(d2<=23);nodes[2,2]=True
floor=ground(480,288);tile_ids=[]
for y in range(9):
 row=[]
 for x in range(15):
  code=''.join('P' if nodes[y+dy,x+dx] else 'm' for dx,dy in [(0,0),(1,0),(0,1),(1,1)]);row.append(code);floor.alpha_composite(tiles[code],(x*32,y*32))
 tile_ids.append(row)
floor=floor.crop((0,0,480,270));big(floor,2,'path_brush_failed_candidate_only_2x.png')
# Approved decals/actors are read-only visual context, never baked into source.
decals=[('decal_loose_slab_01',(292,218)),('decal_pebbles_01',(360,130)),('decal_puddle_03',(160,234)),('decal_dead_grass_01',(415,260)),('decal_leaves_01',(128,48))]
for n,(x,y) in decals:
 im=Image.open(G/f'decals/{n}.png').convert('RGBA');floor.alpha_composite(im,(x-im.width//2,y-im.height//2))
layout=[('tombstone_upright_01',(113,140)),('tombstone_pointed_01',(411,218)),('tombstone_cross_01',(340,175))];P=R/'art/cemetery_v3/props';draw=[]
for n,(x,y) in layout:
 im=Image.open(P/f'{n}_base.png').convert('RGBA');floor.alpha_composite(im,(x-im.width//2,y-im.height));draw.append(((x,y),Image.open(P/f'{n}.png').convert('RGBA')))
draw.append(((230,170),Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA')))
for (x,y),im in sorted(draw,key=lambda item:item[0][1]):floor.alpha_composite(im,(x-im.width//2,y-im.height))
big(floor,2,'path_test_area_failed_candidate_2x.png')
(S/'failed_candidate_brush_layout.json').write_text(json.dumps({'status':'FAILED_CANDIDATE_ONLY_NOT_FOR_RUNTIME','cell_size':32,'vertex_nodes':nodes.astype(int).tolist(),'tile_codes':tile_ids,'native_preview':[480,270],'main_centerline':main,'branch_centerline':branch},indent=2)+'\n')

# Exhaustively compare every legal same-corner endpoint pair, rather than only
# the guide's original neighbors. These are measurements, not seam repairs.
records=[]
for ar in contract['tiles']:
 aa=np.array(tiles[ar['code']])
 for br in contract['tiles']:
  bb=np.array(tiles[br['code']])
  for axis,compatible,e1,e2 in [('horizontal',ar['tr']==br['tl'] and ar['br']==br['bl'],aa[:,-1],bb[:,0]),('vertical',ar['bl']==br['tl'] and ar['br']==br['tr'],aa[-1],bb[0])]:
   if compatible:records.append({'a':ar['code'],'b':br['code'],'axis':axis,'rgba_exact':bool(np.array_equal(e1,e2)),'alpha_exact':bool(np.array_equal(e1[:,3],e2[:,3]))})
locked=json.loads((S/'protected_previous_assets.json').read_text());unchanged=all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in locked.items());assert unchanged
checks={'status':'STOPPED_NATIVE_ATLAS_CONTRACT_FAILED','native_restores':{'01':[156,156],'02':[97,86],'03':[104,102]},'crop_feasibility':json.loads((S/'01_crop_feasibility.json').read_text()),'legal_adjacency_combinations':len(records),'rgba_exact_pairs':sum(r['rgba_exact'] for r in records),'alpha_exact_pairs':sum(r['alpha_exact'] for r in records),'all_pairs':records,'mmmm_opaque_pixels':int((np.array(tiles['mmmm'])[:,:,3]>0).sum()),'PPPP_transparent_pixels':int((np.array(tiles['PPPP'])[:,:,3]==0).sum()),'protected274_pngs_unchanged':unchanged,'variants_not_made':'No valid master atlas; stopped before manufacturing compatible full variants.'}
(Q/'verification_failed_candidate.json').write_text(json.dumps(checks,indent=2)+'\n')
res=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(S/'01_best_native_crop_palette_preview.png')],cwd=R,text=True,capture_output=True,check=True);(Q/'pixel_check_failed_candidate.txt').write_text(res.stdout)
print({k:v for k,v in checks.items() if k not in ['all_pairs','crop_feasibility']});print(res.stdout)
