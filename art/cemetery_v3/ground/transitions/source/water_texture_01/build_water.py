"""Approved surface colors+flattened approved submerged mud;native palette authoring."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,zipfile,datetime,subprocess,sys
S=Path(__file__).resolve().parent;T=S.parents[1];Q=T/'qc';R=T.parents[3];LUMA=np.array([.2126,.7152,.0722])
# Hand-authored soft fog-reflection regions,not random fields or a copied decal.
FOG=[
 {'strength':5.0,'feather':24,'polygon':[[-24,20],[-5,-15],[40,-24],[75,-10],[103,-17],[142,8],[125,45],[99,58],[69,49],[43,64],[13,56],[-11,64]]},
 {'strength':3.6,'feather':24,'polygon':[[88,88],[101,49],[132,38],[160,48],[183,34],[222,57],[241,89],[221,118],[185,122],[159,145],[121,133],[99,116]]},
 {'strength':1.1,'feather':12,'polygon':[[51,98],[65,83],[83,87],[96,79],[116,93],[105,108],[86,114],[72,106]]}
]
LEAVES=[[(43,87),(46,85),(50,86),(52,89),(48,91),(44,90)],[(143,36),(148,35),(151,38),(148,40),(144,39)],[(189,93),(193,92),(197,94),(195,98),(191,97)]]
TWIGS=[[(77,58),(83,58),(89,60),(94,60)],[(169,103),(169,99),(171,95)]]
def region(poly,feather):
 # Repeat hand-painted contours across borders so features cross wraps naturally.
 yy,xx=np.indices((128,224));points=np.stack([xx,yy],2).astype(float);weight=np.zeros((128,224))
 for dy in [-128,0,128]:
  for dx in [-224,0,224]:
   p=[(x+dx,y+dy) for x,y in poly];im=Image.new('1',(224,128));ImageDraw.Draw(im).polygon(p,fill=1);inside=np.array(im);distance=np.full((128,224),1e6)
   for a,b in zip(p,p[1:]+p[:1]):
    a=np.array(a,float);v=np.array(b,float)-a;t=np.clip(((points-a)*v).sum(2)/(v@v),0,1);distance=np.minimum(distance,np.linalg.norm(points-(a+t[:,:,None]*v),axis=2))
   w=inside*np.minimum(distance/feather,1);weight=np.maximum(weight,w)
 return weight
def main():
 existing=[T/'water_texture_01.png']+list(Q.glob('water_texture_*'))+list(S.glob('0[234]_*'));existing=[p for p in existing if p.is_file()]
 if existing:
  with zipfile.ZipFile(Q/f'backups/water_before_build_{datetime.datetime.now():%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
   for p in existing:z.write(p,str(p.relative_to(T)))
 src=np.array(Image.open(S/'veiled_base_01_source.png').convert('RGB'));colors,ids=np.unique(src.reshape(-1,3),axis=0,return_inverse=True)
 lum=colors@LUMA;median=float(np.median(src@LUMA));steps=np.select([lum<median-9,lum<median-3,lum>median+9,lum>median+3],[-.6,-.3,.6,.3],0.)
 submerged=steps[ids].reshape(128,224)
 color_source=json.loads((S/'01_surface_color_sources.json').read_text());center=np.rint(np.array(color_source['combined_surface_mean_rgb'])-11).astype(int)
 Image.fromarray(np.rint(center+submerged[:,:,None]).clip(0,255).astype('uint8')).save(S/'02_flattened_substrate_native.png')
 field=submerged.copy()
 for f in FOG:field+=f['strength']*region(f['polygon'],f['feather'])
 before_debris=field.copy()
 for poly in LEAVES:field-=1.2*region(poly,1.4)
 # Submerged branches have a low-contrast center and weaker neighboring shade;
 # final palette quantization keeps them indistinct,not crisp surface strokes.
 twigmask=Image.new('1',(224,128));d=ImageDraw.Draw(twigmask)
 for p in TWIGS:d.line(p,fill=1,width=1)
 m=np.array(twigmask);field[m]-=1.2
 neighbors=np.zeros_like(m)
 for shift,axis in [(1,0),(-1,0),(1,1),(-1,1)]:neighbors|=np.roll(m,shift,axis=axis)
 field[neighbors&~m]-=.3
 # Darken the approved ramp while preserving its+4/+8 RGB relationship;
 #21 adjacent water shades,not reflection-highlights from the original decals.
 field-=field.mean();lo,hi=.1,12.
 for _ in range(45):
  scale=(lo+hi)/2;value=np.clip(field*scale,-10,10);value-=value.mean();value=np.clip(value,-10,10)
  if value.std()<4.6:lo=scale
  else:hi=scale
 indices=np.rint(value).astype(int)+10;palette=(center+np.arange(-10,11)[:,None]).clip(0,255).astype('uint8');out=palette[indices]
 # Pair native textured profiles;no shoreline/rim/flat border is added.
 out[:,-1]=out[:,0];out[-1]=out[0]
 Image.fromarray(out).convert('RGBA').save(T/'water_texture_01.png')
 Image.fromarray(indices.astype('uint8')).save(S/'03_surface_palette_indices.png')
 (S/'02_substrate_mapping.json').write_text(json.dumps({'source':'art/cemetery_v3/ground/base/veiled_base_01.png','median_luma':median,'mapping':[{'from':c.tolist(),'water_luma_contribution':float(v)} for c,v in zip(colors,steps)],'method':'Approved39-color mud compressed to five very weak submerged levels(-.6,-.3,0,.3,.6),no source pixel blur,averaging,resize or generated mud.'},indent=2)+'\n')
 (S/'03_authored_surface.json').write_text(json.dumps({'fog_regions':FOG,'submerged_leaf_regions':LEAVES,'submerged_twig_paths':TWIGS,'palette':palette.tolist(),'center_from_approved_water':center.tolist(),'reflection_field_contrast_scale':scale,'method':'Hand-authored toroidal regions select adjacent approved-water-derived swatches. No random texture,generated image,puddle silhouette tiling,ripples,white glints or glow. Only final PNG is opaque;reflection geometry fields are source records,not extra runtime layers.'},indent=2)+'\n')
 whole=np.tile(out,(3,3,1));Image.fromarray(whole).save(Q/'water_texture_repeat_3x3_1x.png');Image.fromarray(whole).resize((1344,768),Image.Resampling.NEAREST).save(Q/'water_texture_repeat_3x3_2x.png')
 Image.fromarray(whole[:270,:480]).resize((960,540),Image.Resampling.NEAREST).save(Q/'water_texture_fill_2x.png')
 Image.fromarray(out).resize((1344,768),Image.Resampling.NEAREST).save(Q/'water_texture_native_6x.png')
 wrap=np.tile(out,(2,2,1));Image.fromarray(wrap[104:152,200:248]).resize((384,384),Image.Resampling.NEAREST).save(Q/'water_texture_wrap_8x.png')
 # Mock irregular brush region only;actual shore shape/wet rim remainsClaude's.
 bases=[np.array(Image.open(R/f'art/cemetery_v3/ground/base/veiled_base_{i:02}.png').convert('RGB')) for i in [1,2]]
 ids=np.random.default_rng(20261030).integers(0,2,(3,3));ground=np.empty((384,672,3),np.uint8)
 for y in range(3):
  for x in range(3):ground[y*128:y*128+128,x*224:x*224+224]=bases[ids[y,x]]
 scene=Image.fromarray(ground[:270,:480]).convert('RGBA');mask=Image.new('1',(480,270));d=ImageDraw.Draw(mask)
 shoreline=[(172,65),(196,57),(225,61),(244,52),(274,59),(296,75),(318,78),(332,94),(327,115),(341,130),(332,153),(344,173),(325,191),(308,197),(292,214),(263,218),(243,207),(219,214),(205,199),(181,198),(167,181),(157,164),(146,152),(153,134),(143,115),(157,100),(156,80)]
 d.polygon(shoreline,fill=1);scene.paste(Image.fromarray(whole[:270,:480]),(0,0),mask)
 moss=Image.open(T/'moss_texture_01.png').convert('RGBA');scene.alpha_composite(moss.crop((20,30,100,80)),(34,192))
 puddle=Image.open(R/'art/cemetery_v3/ground/decals/decal_puddle_02.png').convert('RGBA');scene.alpha_composite(puddle,(382-puddle.width//2,226-puddle.height//2))
 for name,foot in [('tombstone_upright_01',(79,130)),('tombstone_upright_02',(397,151)),('tombstone_small_01',(299,254))]:
  for suffix in ['_base','']:
   im=Image.open(R/f'art/cemetery_v3/props/{name}{suffix}.png').convert('RGBA');scene.alpha_composite(im,(foot[0]-im.width//2,foot[1]-im.height))
 hero=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA');scene.alpha_composite(hero,(128-hero.width//2,192-hero.height))
 scene.resize((960,540),Image.Resampling.NEAREST).save(Q/'water_texture_with_ground_2x.png')
 (S/'04_preview_placement.json').write_text(json.dumps({'water_mock_polygon':shoreline,'hero_foot':[128,192],'decal_puddle02_center':[382,226],'base_mix_seed':20261030,'source':'Static mock-up,no runtime changes,water sampled at world-like native coordinates;hard provisional shoreline is not final wet rim.'},indent=2)+'\n')
 report={'status':'WATER_STOPPED_REFLECTION_REPETITION','size':[224,128],'colors':len(np.unique(out.reshape(-1,3),axis=0)),'mean_rgb':out.mean((0,1)).tolist(),'luma_std':float((out@LUMA).std()),'horizontal_change':float(np.any(out[:,1:]!=out[:,:-1],2).mean()*100),'max_rgb':out.max((0,1)).tolist(),'min_rgb':out.min((0,1)).tolist(),'alpha_values':[255],'opposite_left_right_exact':bool(np.array_equal(out[:,0],out[:,-1])),'opposite_top_bottom_exact':bool(np.array_equal(out[0],out[-1])),'bare_native_size':[480,270],'three_by_three_native_size':[672,384],'sha256':hashlib.sha256((T/'water_texture_01.png').read_bytes()).hexdigest(),'runtime_integrated':False,'image_generation_used':False}
 assert 15<=report['colors']<=25 and 4<=report['luma_std']<=7
 assert all(lo<=v<=hi for v,lo,hi in zip(report['mean_rgb'],[44,48,52],[50,54,58]))
 lock=json.loads((S/'protected_approved_assets.json').read_text());assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in lock.items());report['approved_assets_unchanged']=True;report['protected_image_count']=len(lock)
 result=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(T/'water_texture_01.png')],cwd=R,text=True,capture_output=True,check=True);(Q/'water_texture_pixel_check.txt').write_text(result.stdout);(Q/'water_texture_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report);print(result.stdout)
if __name__=='__main__':main()
