from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,subprocess,sys
S=Path(__file__).resolve().parent;B=S.parents[2];Q=B/'qc';R=B.parents[3];LUMA=np.array([.2126,.7152,.0722])
def mixed(tiles,ids):
 a=np.empty((384,672,3),np.uint8)
 for y in range(3):
  for x in range(3):a[y*128:y*128+128,x*224:x*224+224]=tiles[ids[y,x]]
 return a
def main():
 images=[np.array(Image.open(B/f'veiled_base_{i:02}.png').convert('RGB')) for i in [1,2]]
 sources=[np.array(Image.open(B/f'ground_base_{i:02}.png').convert('RGB')) for i in [1,2]]
 ids=np.random.default_rng(20261030).integers(0,2,(3,3));whole=mixed(images,ids);outer=mixed(sources,ids);bare=whole[:270,:480]
 Image.fromarray(whole).save(Q/'veiled_base_mix_3x3_1x.png');Image.fromarray(whole).resize((1344,768),Image.Resampling.NEAREST).save(Q/'veiled_base_mix_3x3_2x.png')
 Image.fromarray(bare).resize((960,540),Image.Resampling.NEAREST).save(Q/'veiled_base_fill_2x.png')
 half=np.concatenate([outer[:270,:240],whole[:270,:240]],axis=1);Image.fromarray(half).resize((960,540),Image.Resampling.NEAREST).save(Q/'veiled_base_vs_outer_2x.png')
 for i,a in enumerate(images,1):
  Image.fromarray(a).resize((1344,768),Image.Resampling.NEAREST).save(Q/f'veiled_base_{i:02}_6x.png')
  Image.fromarray(np.tile(a,(3,3,1))).save(Q/f'veiled_base_{i:02}_repeat_3x3_1x.png')
 # Exact copies of approved native assets,no engine grading or scene edits.
 scene=Image.fromarray(bare).convert('RGBA');outertile=Image.open(B/'ground_base_01.png').convert('RGBA');moss=Image.open(B.parent/'transitions/moss_texture_01.png').convert('RGBA')
 scene.alpha_composite(Image.fromarray(np.tile(np.array(outertile),(3,1,1))[:270,:96]),(384,0))
 scene.alpha_composite(moss.crop((25,22,131,84)),(239,187))
 puddle=Image.open(B.parent/'decals/decal_puddle_02.png').convert('RGBA');scene.alpha_composite(puddle,(330-puddle.width//2,218-puddle.height//2))
 for name,foot in [('tombstone_upright_01',(96,157)),('tombstone_upright_02',(286,161)),('tombstone_small_01',(264,245))]:
  for suffix in ['_base','']:
   im=Image.open(R/f'art/cemetery_v3/props/{name}{suffix}.png').convert('RGBA');scene.alpha_composite(im,(foot[0]-im.width//2,foot[1]-im.height))
 hero=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');scene.alpha_composite(hero,(190-hero.width//2,190-hero.height))
 scene.resize((960,540),Image.Resampling.NEAREST).save(Q/'veiled_base_with_props_2x.png')
 Image.fromarray(np.concatenate([np.array(outertile)[:,:,:3],images[0],np.array(moss)[:,:,:3]],axis=1)).resize((1344,256),Image.Resampling.NEAREST).save(Q/'veiled_base_material_compare_2x.png')
 for seed in range(4):
  corner=np.concatenate([np.concatenate([images[seed//2],images[seed%2]],1),np.concatenate([images[1-seed%2],images[1-seed//2]],1)],0)
  Image.fromarray(corner[104:152,200:248]).resize((384,384),Image.Resampling.NEAREST).save(Q/f'veiled_base_junction_{seed}_8x.png')
 rev=json.loads((S/'03_revision_metrics.json').read_text());recolors=[np.array(Image.open(S/f'01_recolored_{i:02}_native.png')) for i in [1,2]]
 pal=json.loads((S/'01_common_palette.json').read_text());lookup={tuple(p['from']):p['to'] for p in pal['mapping']}
 metrics={}
 for i,(a,src,recolor,m) in enumerate(zip(images,sources,recolors,rev['images']),1):
  expected=np.array([lookup[tuple(c)] for c in src.reshape(-1,3)],np.uint8).reshape(128,224,3);assert np.array_equal(expected,recolor)
  edgeproof=all(np.array_equal(edge(a),edge(recolor)) for edge in [lambda a:a[:8],lambda a:a[-8:],lambda a:a[:,:8],lambda a:a[:,-8:]])
  assert edgeproof and np.array_equal(a[0],a[-1]) and np.array_equal(a[:,0],a[:,-1])
  m.update({'size':[224,128],'all_alpha_255':set(Image.open(B/f'veiled_base_{i:02}.png').getchannel('A').getdata())=={255},'pure_recolor_matches_exact_39color_lookup':True,'outer8px_match_recolored_source':edgeproof,'opposite_edges_exact':True})
  metrics[f'veiled_base_{i:02}.png']=m
 lock=json.loads((S/'protected_approved_assets.json').read_text());assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in lock.items())
 pair=all(np.array_equal(a[:,0],b[:,-1]) and np.array_equal(a[0],b[-1]) for a in images for b in images);assert pair
 assert all(np.array_equal(edge(images[0]),edge(images[1])) for edge in [lambda a:a[:8],lambda a:a[-8:],lambda a:a[:,:8],lambda a:a[:,-8:]])
 report={'status':'SECTION4_NATIVE_SOIL_PENDING_VISUAL_REVIEW','source_method':'Approved39-color ground_base01/02 injective shared recolor plus manually authored low-contrast interior swatch edits,no image generation','images':metrics,'common_palette_color_count':39,'same_outer8px':True,'all_ordered_adjacencies_exact':pair,'random_seed':20261030,'mixed_ids':ids.tolist(),'bare_native_size':[480,270],'repeat_native_size':[672,384],'half_screen_comparison':'Left240px original,right240px new,same native positions and same01/02mix,no grading,2x nearest','approved_images_unchanged':True,'protected_image_count':len(lock),'runtime_integrated':False,'world_position_shading_used':False}
 result=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(B/'veiled_base_01.png'),str(B/'veiled_base_02.png')],cwd=R,text=True,capture_output=True,check=True)
 (Q/'veiled_base_pixel_check.txt').write_text(result.stdout);(Q/'veiled_base_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report);print(result.stdout)
if __name__=='__main__':main()
