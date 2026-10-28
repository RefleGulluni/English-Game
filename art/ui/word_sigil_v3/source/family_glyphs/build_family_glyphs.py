"""Hand-designed 11px language alphabet. No generated bitmap, blur or AA."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,datetime,zipfile,itertools
S=Path(__file__).resolve().parent;O=S.parents[1];R=O.parents[2];G=O/'glyphs';Q=O/'qc'
CYAN=(107,219,242);BG=(12,18,23);INK=(195,207,210);DIM=(134,153,160)
ORDER=['force','direct','decay','toxicity','perception','control','reaction','protection','restoration']
# Every path is explicitly authored native geometry, never random decoration.
DESIGNS={
 'force':{'word':'SHATTER','meaning':'向外碎开','paths':[
  [(1,3),(1,1),(3,1)],[(7,1),(9,1),(9,3)],[(1,7),(1,9),(3,9)],[(7,9),(9,9),(9,7)]],
  'points':[(3,3),(7,3),(3,7),(7,7)],
  'logic':'Four outward90deg fragments with four detached chips at registered diagonal positions; empty3x3 core. No center spark or radial star.'},
 'direct':{'word':'STRIKE','meaning':'直达命中','paths':[
  [(5,9),(5,1)],[(3,3),(5,1),(7,3)],[(3,9),(7,9)]],
  'logic':'One uninterrupted axis and pointed terminal; perpendicular datum at the origin.'},
 'decay':{'word':'ERODE','meaning':'逐层剥落','paths':[
  [(2,1),(2,3),(8,3)],[(3,5),(6,5)],[(4,7),(5,7)]],
  'points':[(8,5),(7,7),(5,9)],
  'logic':'Registered material strokes shorten in3 stages; detached end samples retain the erosion direction.'},
 'toxicity':{'word':'TOXIC','meaning':'逐层渗入','paths':[
  [(1,1),(9,1),(9,9)],[(1,4),(6,4),(6,9)],[(1,7),(3,7),(3,9)]],
  'logic':'Three nested right-angle ingress channels, spacing3; inward propagation rather than a poison pictogram.'},
 'perception':{'word':'OBSERVE','meaning':'开口显现','paths':[
  [(3,2),(1,2),(1,8),(3,8)],[(7,2),(9,2),(9,8),(7,8)],[(5,1),(5,2)],[(5,8),(5,9)]],
  'points':[(5,5)],
  'logic':'Two open measurement apertures isolate a single resolved center sample; no eye outline.'},
 'control':{'word':'BIND','meaning':'反向扣合','paths':[
  [(3,1),(1,1),(1,7),(5,7)],[(7,9),(9,9),(9,3),(5,3)],[(5,3),(5,7)]],
  'logic':'Opposing stepped jaws close onto a common locking spine;180deg paired structure, no drawn padlock.'},
 'reaction':{'word':'DEFLECT','meaning':'转向引开','paths':[
  [(1,5),(5,5),(9,1)],[(7,1),(9,1),(9,3)],[(1,4),(1,6)],[(5,7),(5,9)]],
  'logic':'An incoming straight trace changes direction at the center and leaves on45deg; separated lower normal records the rejected axis, no circular return arrow.'},
 'protection':{'word':'STABILIZE','meaning':'对齐稳定','paths':[
  [(5,1),(5,9)],[(4,1),(6,1)],[(4,9),(6,9)],[(2,3),(2,7)],[(8,3),(8,7)],[(2,5),(8,5)]],
  'logic':'Three parallel rails registered by one common transverse axis; center rail has matched end datums. No shield or closed square resembling a written character.'},
 'restoration':{'word':'RESTORE','meaning':'跨断口复接','paths':[
  [(1,4),(1,2),(4,2)],[(6,8),(9,8),(9,6)],[(3,7),(7,3)],[(3,6),(3,8)],[(6,3),(8,3)]],
  'logic':'Two offset remaining fragments are joined by an ascending coupling trace with registered ends; no medical cross.'},
}

def make(name):
 mask=Image.new('L',(11,11));d=ImageDraw.Draw(mask)
 for points in DESIGNS[name]['paths']:d.line(points,fill=255,width=1)
 for point in DESIGNS[name].get('points',[]):d.point(point,fill=255)
 a=np.zeros((11,11,4),dtype=np.uint8);m=np.array(mask)>0;a[m]=[255,255,255,255]
 return Image.fromarray(a)
def tint(im,color):
 out=Image.new('RGBA',im.size,color+(0,));out.putalpha(im.getchannel('A'));return out
def text(im,xy,s,size=12,c=INK):
 f=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',size);d=ImageDraw.Draw(im);d.text(xy,s,font=f,fill=c)
def label_board(images):
 im=Image.new('RGB',(720,588),BG)
 text(im,(24,14),'Word Sigil / 9 个词类符号',22)
 text(im,(24,46),'11×11 原生 · 图形放大8倍 · 同一套1像素几何语法',12,DIM)
 for i,name in enumerate(ORDER):
  x=24+(i%3)*232;y=85+(i//3)*162
  text(im,(x,y),name.upper(),13)
  icon=tint(images[name],CYAN).resize((88,88),Image.Resampling.NEAREST);im.paste(icon,(x+4,y+26),icon)
  text(im,(x+103,y+43),DESIGNS[name]['meaning'],12)
  text(im,(x+103,y+65),DESIGNS[name]['word'],11,DIM)
  # True native size shown separately next to the enlarged glyph.
  original=tint(images[name],CYAN);im.paste(original,(x+108,y+94),original)
 text(im,(24,565),'白色透明成品由程序染青蓝和发光；此图不烘焙光晕。',12,DIM)
 im.save(Q/'family_glyphs_labeled_8x.png')
def with_words(images):
 f=ImageFont.truetype(str(R/'art/ui/fonts/CormorantGaramond.ttf'),18);f.set_variation_by_name('SemiBold')
 im=Image.new('RGB',(960,302),BG);d=ImageDraw.Draw(im)
 text(im,(24,12),'原生词旁检查 / Cormorant + 已选第3档的基线节点关系',18)
 text(im,(24,40),'符号原生11×11；词框只作位置检查，不替换Claude已通过的实现；不另加光晕。',11,DIM)
 for i,name in enumerate(ORDER):
  col=i%3;row=i//3;x=42+col*310;y=88+row*68;w=140
  text(im,(x,y-18),name.upper(),10,DIM)
  icon=tint(images[name],CYAN);im.paste(icon,(x+6,y+9),icon)
  d.fontmode='1';d.text((x+23,y+4),DESIGNS[name]['word'],font=f,fill=CYAN)
  base=y+28;mid=x+w//2
  for start,end in [(x+1,mid-8),(mid+8,x+w-2)]:
   d.line((start,base,start+8,base),fill=CYAN)
   for xx in range(start+10,end,2):d.point((xx,base),fill=(41,81,90))
   d.line((start,base+3,end,base+3),fill=(26,45,50))
  for node in [x+1,x+w-2,mid-4,mid+4]:
   d.polygon([(node,base-1),(node+1,base),(node,base+1),(node-1,base)],fill=CYAN)
 im.save(Q/'family_glyphs_with_words_1x.png');im.resize((3840,1208),Image.Resampling.NEAREST).save(Q/'family_glyphs_with_words_4x.png')

def main():
 existing=list(G.glob('*.png'))+list(Q.glob('family_glyphs_*'))
 if existing:
  with zipfile.ZipFile(S/f'before_rebuild_{datetime.datetime.now():%Y%m%d_%H%M%S}.zip','w',zipfile.ZIP_DEFLATED) as z:
   for p in existing:
    if p.is_file():z.write(p,str(p.relative_to(O)))
 images={name:make(name) for name in ORDER};rows={};stats={}
 sheet=Image.new('RGBA',(51,51))
 for i,name in enumerate(ORDER):
  im=images[name];im.save(G/f'family_{name}.png');a=np.array(im);m=a[:,:,3]>0
  sheet.paste(im,(3+(i%3)*17,3+(i//3)*17),im)
  rows[name]=[''.join('X' if p else '.' for p in row) for row in m]
  ys,xs=np.where(m);stats[name]={'size':[11,11],'opaque_pixels':int(m.sum()),'bbox_xyxy':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'alpha_values':np.unique(a[:,:,3]).tolist(),'opaque_rgb':[[255,255,255]],'sha256':hashlib.sha256((G/f'family_{name}.png').read_bytes()).hexdigest()}
 sheet.save(G/'family_glyphs_sheet_1x.png');sheet.resize((408,408),Image.Resampling.NEAREST).save(G/'family_glyphs_sheet_8x.png')
 label_board(images);with_words(images)
 pairs=[]
 for a,b in itertools.combinations(ORDER,2):
  aa=np.array(images[a])[:,:,3]>0;bb=np.array(images[b])[:,:,3]>0
  pairs.append({'pair':[a,b],'same_alignment_different_pixels':int((aa!=bb).sum()),'rotated_or_mirrored_exact_match':any(np.array_equal(aa,np.rot90(bb,k)) or np.array_equal(aa,np.fliplr(np.rot90(bb,k))) for k in range(4))})
 assert all(p['same_alignment_different_pixels']>0 and not p['rotated_or_mirrored_exact_match'] for p in pairs)
 lock=json.loads((S/'protected_files.json').read_text());protected_changed=[p for p,h in lock.items() if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h];assert not protected_changed,protected_changed
 (S/'family_glyphs_geometry.json').write_text(json.dumps({'canvas':[11,11],'center':[5,5],'safe_bounds':[1,1,10,10],'stroke':1,'axes':'horizontal,vertical,45deg; integer coordinates','order':ORDER,'designs':DESIGNS,'godot_rows':rows},ensure_ascii=False,indent=2)+'\n')
 (Q/'family_glyphs_verification.json').write_text(json.dumps({'status':'STEP2_NINE_GLYPHS_READY_FOR_USER_REVIEW','glyphs':stats,'pairs':pairs,'protected_files_unchanged':True,'protected_file_count':len(lock),'runtime_integrated':False,'baked_glow':False,'sheet_native_size':[51,51],'sheet_scale':8},ensure_ascii=False,indent=2)+'\n')
 print(stats);print('Min aligned difference',min(p['same_alignment_different_pixels'] for p in pairs))

if __name__=='__main__':main()
