"""Native 15px route alphabet, sharing grammar with the approved11px word alphabet."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,itertools,zipfile,datetime
S=Path(__file__).resolve().parent;O=S.parent;R=O.parents[2];Q=O/'qc'
CYAN=(107,219,242);BG=(12,18,23);INK=(197,209,211);DIM=(134,152,158)
ORDER=['combat','elite','event','mystery','relic','rest','final','area','unknown']
FAMILIES=['force','direct','decay','toxicity','perception','control','reaction','protection','restoration']
THRESHOLD=[[(2,11),(2,13),(12,13),(12,11)]]
HAZARD=[[(3,2),(6,5),(3,8)],[(11,2),(8,5),(11,8)]]
RAILS=[[(1,2),(1,9)],[(13,2),(13,9)]]
DESIGNS={
 'combat':{'name':'战斗','paths':HAZARD,'meaning':'Opposing hazard traces approach a1px empty center break; the common encounter core.'},
 'elite':{'name':'精英','paths':HAZARD+RAILS,'meaning':'Same encounter core constrained by two13px-span exterior pressure rails.'},
 'event':{'name':'事件','paths':[[(7,9),(7,6),(3,2)],[(7,6),(11,2)],[(2,2),(4,2)],[(10,2),(12,2)]],'meaning':'One approach branches into two registered alternatives, a choice rather than a question-mark pictogram.'},
 'mystery':{'name':'未知路线','paths':[[(4,1),(10,1),(12,3),(12,7),(10,9),(4,9),(2,7),(2,3),(4,1)],[(5,4),(7,4)],[(8,6),(10,6)]],'meaning':'A fully registered closed aperture with two offset horizontal samples; the route is understood as uncertain, not unreadable.'},
 'relic':{'name':'遗物','paths':[[(3,3),(3,1),(11,1),(11,3)],[(3,7),(3,9),(11,9),(11,7)],[(7,3),(9,5),(7,7),(5,5),(7,3)]],'points':[(7,5)],'meaning':'A single resolved key sample retained between balanced upper/lower datums; no chest or treasure illustration.'},
 'rest':{'name':'休息','paths':[[(3,4),(3,8),(11,8),(11,4)],[(5,5),(9,5)]],'meaning':'Low open cradle and quiet horizontal sample; no inward pressure or pointed hazard core.'},
 'final':{'name':'最终 / Boss','paths':HAZARD+RAILS+[[(1,1),(13,1)],[(7,1),(7,9)]],'meaning':'Same hazard core and pressure rails, now closed by a ceremonial upper register with a full central axis; maximum gravity.'},
 'area':{'name':'换区域','paths':[[(1,5),(13,5)],[(11,3),(13,5),(11,7)],[(5,1),(5,3)],[(5,7),(5,9)],[(9,1),(9,3)],[(9,7),(9,9)]],'meaning':'One continuous traversal across two interrupted boundary planes, proceeding outward.'},
 'unknown':{'name':'尚未理解','paths':[[(3,1),(1,1),(1,3)],[(11,1),(13,1),(13,3)],[(7,5),(7,7)]],'points':[(3,9),(11,9)],'meaning':'Stable incomplete registration: upper corner anchors, partial center axis, two lower samples; missing structure, never scrambled or glitching.'},
}
def make(name):
 m=Image.new('L',(15,15));d=ImageDraw.Draw(m)
 for path in THRESHOLD+DESIGNS[name]['paths']:d.line(path,fill=255,width=1)
 for xy in DESIGNS[name].get('points',[]):d.point(xy,fill=255)
 a=np.zeros((15,15,4),np.uint8);a[np.array(m)>0]=[255,255,255,255];return Image.fromarray(a)
def tint(im):
 o=Image.new('RGBA',im.size,CYAN+(0,));o.putalpha(im.getchannel('A'));return o
def text(im,xy,s,size=12,color=INK):
 f=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',size);ImageDraw.Draw(im).text(xy,s,font=f,fill=color)
def paste(im,icon,xy):im.paste(icon,xy,icon)
def labeled(images):
 im=Image.new('RGB',(810,708),BG)
 text(im,(24,14),'出口符号 / 路线节点',22);text(im,(24,48),'15×15 · 中间13×13作画 · 8倍图与原生小图 · 共同门槛，不是词类',12,DIM)
 for i,n in enumerate(ORDER):
  x=24+(i%3)*266;y=85+(i//3)*198
  text(im,(x,y),DESIGNS[n]['name']+' / '+n.upper(),13)
  a=tint(images[n]);paste(im,a.resize((120,120),Image.Resampling.NEAREST),(x+4,y+27));paste(im,a,(x+155,y+92))
  text(im,(x+142,y+119),'1×',11,DIM)
 text(im,(24,679),'白色透明成品由程序染青蓝、发光；检查板不烘焙光晕。',12,DIM)
 im.save(Q/'exit_glyphs_labeled_8x.png')
def with_family(images):
 im=Image.new('RGB',(1032,708),BG)
 text(im,(24,14),'同一语言，两套用途 / 地点有门槛，词类无门槛',22)
 text(im,(24,49),'每格左：15×15出口　右：11×11词类；均8倍，配对仅供比较，不表示类别映射。',12,DIM)
 for i,(name,family) in enumerate(zip(ORDER,FAMILIES)):
  x=24+(i%3)*340;y=87+(i//3)*199
  text(im,(x,y),DESIGNS[name]['name'],12)
  text(im,(x+172,y),family.upper(),12,DIM)
  a=tint(images[name]).resize((120,120),Image.Resampling.NEAREST)
  b=tint(Image.open(R/f'art/ui/word_sigil_v3/glyphs/family_{family}.png')).resize((88,88),Image.Resampling.NEAREST)
  paste(im,a,(x,y+28));paste(im,b,(x+172,y+44))
  paste(im,tint(images[name]),(x+130,y+123));paste(im,tint(Image.open(R/f'art/ui/word_sigil_v3/glyphs/family_{family}.png')),(x+277,y+125))
 text(im,(24,679),'共用1px整数轴线、直角肩部、45°与规则断口；出口统一带下方门槛。',12,DIM)
 im.save(Q/'exit_glyphs_with_family_8x.png')
def in_scene(images):
 # Overlay only; original3x screenshot is preserved byte-for-byte outside icon.
 original=Image.open(R/'docs/reference/combat_v1_standoff.png').convert('RGB');assert original.size==(2880,1620)
 at=(898,56);outputs={}
 for n in ORDER:
  im=original.copy();icon=tint(images[n]).resize((45,45),Image.Resampling.NEAREST);paste(im,icon,(at[0]*3,at[1]*3));outputs[n]=im
 outputs['combat'].save(Q/'exit_glyphs_in_scene.png')
 Image.fromarray(np.array(outputs['combat'])[1::3,1::3]).save(Q/'exit_glyphs_in_scene_1x.png')
 # Same placement for every type, no false room with nine physical exits.
 im=Image.new('RGB',(1260,1080),BG)
 for i,n in enumerate(ORDER):
  x=(i%3)*420;y=(i//3)*360
  text(im,(x+14,y+10),DESIGNS[n]['name']+' / '+n.upper(),15)
  crop=outputs[n].crop((820*3,20*3,960*3,120*3));im.paste(crop,(x,y+45))
 im.save(Q/'exit_glyphs_scene_comparison_3x.png')
 return at,original,outputs['combat']
def main():
 old=list(O.glob('exit_*.png'))+list(Q.glob('exit_glyphs_*'))
 if old:
  with zipfile.ZipFile(S/f'before_rebuild_{datetime.datetime.now():%Y%m%d_%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
   for p in old:
    if p.is_file():z.write(p,str(p.relative_to(O)))
 images={n:make(n) for n in ORDER};rows={};stats={}
 for n,im in images.items():
  p=O/f'exit_{n}.png';im.save(p);a=np.array(im);m=a[:,:,3]>0
  assert im.size==(15,15) and set(np.unique(a[:,:,3]))=={0,255};assert np.all(a[m,:3]==255)
  assert not m[0].any() and not m[-1].any() and not m[:,0].any() and not m[:,-1].any()
  assert np.all(m[13,2:13]) and np.all(m[11:14,2]) and np.all(m[11:14,12])
  rows[n]=[''.join('X' if p else '.' for p in row) for row in m];stats[n]={'size':[15,15],'opaque_pixels':int(m.sum()),'upper_body_pixels':int(m[:11].sum()),'alpha_values':[0,255],'opaque_color':[255,255,255],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 assert stats['combat']['upper_body_pixels']<stats['elite']['upper_body_pixels']<stats['final']['upper_body_pixels']
 labeled(images);with_family(images);at,original,composed=in_scene(images)
 changed=np.any(np.array(original)!=np.array(composed),2);changed[at[1]*3:(at[1]+15)*3,at[0]*3:(at[0]+15)*3]=False;assert not changed.any()
 pairs=[]
 for a,b in itertools.combinations(ORDER,2):
  ma=np.array(images[a])[:,:,3]>0;mb=np.array(images[b])[:,:,3]>0
  pairs.append({'pair':[a,b],'different_pixels':int((ma!=mb).sum())});assert pairs[-1]['different_pixels']>0
 lock=json.loads((S/'protected_files.json').read_text());assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in lock.items())
 (S/'exit_geometry.json').write_text(json.dumps({'canvas':[15,15],'safe_draw_bounds':[1,1,14,14],'center':[7,7],'body_y':[1,9],'common_threshold':THRESHOLD,'order':ORDER,'designs':DESIGNS,'rows':{k.upper():v for k,v in rows.items()}},ensure_ascii=False,indent=2)+'\n')
 (Q/'exit_glyphs_verification.json').write_text(json.dumps({'status':'NINE_EXIT_GLYPHS_READY_FOR_USER_REVIEW','glyphs':stats,'pair_checks':pairs,'shared_threshold_pixel_count':15,'scene_source':'docs/reference/combat_v1_standoff.png','source_size':[2880,1620],'scene_overlay_native_xy':at,'scene_unchanged_outside_glyph':True,'protected_file_count':len(lock),'protected_files_unchanged':True,'runtime_integrated':False,'baked_glow':False},ensure_ascii=False,indent=2)+'\n')
 print(stats)
if __name__=='__main__':main()
