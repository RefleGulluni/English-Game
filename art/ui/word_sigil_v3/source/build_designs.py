"""Native-pixel Word Sigil design specification, not production UI integration."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math,zipfile,datetime

ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parents[1]
D=OUT/'design';Q=OUT/'qc';S=OUT/'source'
BG=(12,18,23);INK=(194,202,202);MUTED=(126,142,148);RULE=(39,52,59);CYAN=(107,219,242)
CN='/System/Library/Fonts/Hiragino Sans GB.ttc'
SERIF=ImageFont.truetype(str(ROOT/'art/ui/fonts/CormorantGaramond.ttf'),18)
SERIF.set_variation_by_name('SemiBold')
FONTS={n:ImageFont.truetype(CN,n) for n in [10,11,12,14,22]}
# These are only the letters needed by the first-step words, not a full font.
LETTERS={
'A':['01110','10001','10001','10001','11111','10001','10001','10001','10001'],
'B':['11110','10001','10001','10001','11110','10001','10001','10001','11110'],
'D':['11100','10010','10001','10001','10001','10001','10001','10010','11100'],
'E':['11111','10000','10000','10000','11110','10000','10000','10000','11111'],
'H':['10001','10001','10001','10001','11111','10001','10001','10001','10001'],
'I':['111','010','010','010','010','010','010','010','111'],
'L':['10000','10000','10000','10000','10000','10000','10000','10000','11111'],
'N':['10001','11001','11001','10101','10101','10101','10011','10011','10001'],
'O':['01110','10001','10001','10001','10001','10001','10001','10001','01110'],
'R':['11110','10001','10001','10001','11110','10100','10010','10001','10001'],
'S':['01111','10000','10000','10000','01110','00001','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100','00100','00100'],
'V':['10001','10001','10001','10001','10001','10001','10001','01010','00100'],
'Z':['11111','00001','00001','00010','00100','01000','10000','10000','11111'],
}
DIGITS={'1':['010','110','010','010','010','010','111'],'2':['110','001','001','010','100','100','111'],'3':['110','001','001','010','001','001','110']}
INFO={
'A':('端括 · 开放锚点','保留熟悉的四角，但不合成卡框；文字始终是主体。'),
'B':('基线 · 一条语句','把词放在精确的断基线上；状态只改变基线与端点。'),
'C':('收束 · 调用焦点','两端向词心收束；把词看成一次即将发生的调用。'),
}
STATE_NAMES=[('available','能用'),('hover','悬停'),('selected','选中 / 调用'),('retain','保留'),('disabled','不能用')]
METRICS=[]

def color(f):return tuple(round(v*f) for v in CYAN)
def label(im,xy,text,size=11,fill=INK):
 dr=ImageDraw.Draw(im);dr.fontmode='1';dr.text(xy,text,font=FONTS[size],fill=fill,stroke_width=0)
def bitmap_word(word):
 widths=[len(LETTERS[c][0]) for c in word];im=Image.new('1',(sum(widths)+2*(len(word)-1),9));d=ImageDraw.Draw(im);x=0
 for ch,w in zip(word,widths):
  for y,row in enumerate(LETTERS[ch]):
   for xx,b in enumerate(row):
    if b=='1':d.point((x+xx,y),fill=1)
  x+=w+2
 return im
def word_mask(word,font):
 if font=='pixel':return bitmap_word(word)
 box=SERIF.getbbox(word);im=Image.new('1',(box[2]-box[0],box[3]-box[1]));d=ImageDraw.Draw(im);d.fontmode='1';d.text((-box[0],-box[1]),word,font=SERIF,fill=1)
 return im
def diamond(d,x,y,c,solid=True):
 pts=[(x,y-2),(x+2,y),(x,y+2),(x-2,y)]
 d.polygon(pts,fill=c if solid else None,outline=c)
def sample_glyph(d,x,y,c):
 # Same anonymous 11x11 placement marker everywhere; not a proposed family glyph.
 d.line((x+5,y,x+5,y+10),fill=c);d.line((x,y+5,x+10,y+5),fill=c)
 d.point((x+3,y+3),fill=c);d.point((x+7,y+3),fill=c);d.point((x+3,y+7),fill=c);d.point((x+7,y+7),fill=c)
def retain_mark(d,x,y,c):
 d.line((x,y+1,x+6,y+1,x+6,y+6,x+3,y+4,x,y+6,x,y+1),fill=c)
def replace_mark(d,x,y,c):
 # Offset return arrow, kept in top-right so it never crosses the word.
 d.line((x,y+2,x+7,y+2,x+7,y+7,x+2,y+7),fill=c)
 d.line((x+2,y+7,x+4,y+5),fill=c);d.line((x+2,y+7,x+4,y+9),fill=c)

def sigil(direction,word,font='serif',state='available',cost=2,replace=False,record=False):
 mask=word_mask(word,font);tw,th=mask.size
 # 7px left pad +11px category slot +6px gap +word +8px right pad.
 w=max(56,tw+32);h=40
 if w>130:raise ValueError((word,font,w))
 im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im)
 strength={'available':.86,'hover':.95,'selected':1.,'retain':.86,'disabled':.50}[state]
 c=color(strength);f=color(max(.3,strength-.24));edge=c if state in ['hover','selected'] else f
 left,right=1,w-2;top,bottom=3,28;mid=(w-1)//2
 if direction=='A':
  length=9 if state in ['hover','selected'] else 5
  for x,dx in [(left,1),(right,-1)]:
   for y,dy in [(top,1),(bottom,-1)]:
    d.line((x,y,x+dx*length,y),fill=edge)
    d.line((x,y,x,y+dy*(5 if state!='disabled' else 2)),fill=edge)
  if state=='hover':d.line((mid-5,top,mid+5,top),fill=edge)
 elif direction=='B':
  by=28
  if state in ['hover','selected']:
   d.line((left,by,mid-5,by),fill=edge);d.line((mid+5,by,right,by),fill=edge)
  else:
   d.line((left,by,left+9,by),fill=edge);d.line((right-9,by,right,by),fill=edge)
  for x in [left,right]:d.line((x,by-3,x,by),fill=edge)
  if state=='selected':
   d.line((left+4,by+2,mid-7,by+2),fill=c);d.line((mid+7,by+2,right-4,by+2),fill=c)
 elif direction=='C':
  for x,dx in [(left,1),(right,-1)]:
   d.line((x+4*dx,9,x,13,x,17,x+4*dx,21),fill=edge)
  if state=='hover':d.line((mid-3,top,mid+3,top),fill=edge)
 # Word and 11x11 anonymous category marker share a fixed centerline y16.
 sample_glyph(d,7,10,c if state!='disabled' else f)
 im.paste((*c,255),(24,16-th//2),mask)
 # Calling is brighter, with two paired precise 1px target ticks (local2px).
 if state=='selected':
  d.line((mid-3,0,mid+3,0),fill=c,width=1);d.line((mid,0,mid,2),fill=c)
  d.line((mid-2,30,mid+2,30),fill=c);d.line((mid-1,31,mid+1,31),fill=c)
 if state=='retain':retain_mark(d,w-21,0,c)
 if state=='disabled':
  d.line((w-11,0,w-7,4),fill=c);d.line((w-7,0,w-11,4),fill=c)
 if replace:replace_mark(d,w-13,0,CYAN)
 # Focus stays below the word, never in the category-symbol slot.
 if direction=='A':
  start=mid-4*(cost-1)
  for i in range(cost):diamond(d,start+8*i,35,c,state!='disabled')
 elif direction=='B':
  start=mid-3*(cost-1)
  for i in range(cost):
   x=start+i*6;d.line((x,33,x,37),fill=c)
   if state!='disabled':d.point((x+1,35),fill=c)
 else:
  pattern=DIGITS[str(cost)]
  for y,row in enumerate(pattern):
   for x,b in enumerate(row):
    if b=='1':d.point((mid-1+x,32+y),fill=c)
  d.line((mid-5,33,mid-5,37),fill=f);d.line((mid+5,33,mid+5,37),fill=f)
 if record:METRICS.append({'direction':direction,'word':word,'font':font,'state':state,'replace':replace,'cost':cost,'size':[w,h],'word_ink_size':[tw,th],'glyph_slot':[7,10,11,11],'word_left':24})
 return im

def paste(im,s,xy):im.paste(s,xy,s)
def export(im,path):
 im.save(path.with_name(path.stem+'_1x.png'));im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(path)
def sheet(key):
 im=Image.new('RGB',(960,736),BG);d=ImageDraw.Draw(im)
 name,desc=INFO[key];label(im,(24,17),f'{key}   {name}',22);label(im,(24,48),desc,12,MUTED)
 label(im,(24,77),'01  字体并排 / 长度伸缩',12)
 label(im,(48,101),'字体 A · Cormorant Garamond SemiBold 18',11,MUTED)
 label(im,(524,101),'字体 B · 自绘大写字母 9 px',11,MUTED)
 for col,font in [(0,'serif'),(476,'pixel')]:
  for x,word in [(38,'BIND'),(172,'OBSERVE'),(310,'STABILIZE')]:
   s=sigil(key,word,font,record=True);paste(im,s,(x+col,127))
   label(im,(x+col,172),f'{s.width} × 40',10,MUTED)
 d.line((24,199,936,199),fill=RULE)
 rule={'A':'左端四角 + 字宽留白区 + 右端四角；中段只增加间距，不画底板。','B':'左端短竖 + 水平基线段 + 右端短竖；悬停时延长，常态只留两端。','C':'左折线端 + 字宽留白区 + 右折线端；宽度变化时只移动右端。'}[key]
 label(im,(24,208),'拼接：'+rule,11,MUTED)
 label(im,(24,235),'02  五种状态 · 同一词 SHATTER，同一消耗 2',12)
 for i,(state,zh) in enumerate(STATE_NAMES):
  y=266+i*43
  for col,font in [(0,'serif'),(476,'pixel')]:
   label(im,(32+col,y+9),f'{i+1:02}  {zh}',11,MUTED)
   s=sigil(key,'SHATTER',font,state,record=True);paste(im,s,(211+col-s.width//2,y))
  label(im,(350,y+11),{'available':'端点稳定','hover':'端点展开','selected':'顶部调用刻度','retain':'右上保留折签','disabled':'右上叉记'}[state],10,MUTED)
 d.line((24,488,936,488),fill=RULE)
 label(im,(24,502),'03  开局换词 · 标记单独叠加，不划掉单词',12)
 for col,font in [(0,'serif'),(476,'pixel')]:
  s=sigil(key,'SHATTER',font,replace=True,record=True);paste(im,s,(211+col-s.width//2,530))
 label(im,(24,580),'04  专注消耗 · 1 / 2 / 3',12)
 for col,font in [(0,'serif'),(476,'pixel')]:
  for x,cost in [(38,1),(172,2),(310,3)]:paste(im,sigil(key,'BIND',font,cost=cost,record=True),(x+col,606))
 label(im,(24,661),'词左侧预留 11×11 类别符号位；此处十字只是同一个定位占位，不是正式词类符号。',11,MUTED)
 label(im,(24,684),'词框始终透明 · 几何线宽 1 px · 不画光晕 · 点击区域使用稳定的 40 px 高透明矩形',11,MUTED)
 label(im,(24,708),'选择可交叉组合：任一方向的词框 + 任一字体。下一步才设计九类正式符号。',10,MUTED)
 export(im,D/f'word_sigil_direction_{key}.png')

def reference_native(name):
 source=Image.open(ROOT/'docs/reference'/name).convert('RGB');assert source.size==(2880,1620)
 # Screenshot is3x native. Take one center per3x3 block, never rescale artwork.
 return Image.fromarray(__import__('numpy').array(source)[1::3,1::3])
def clean_bar(native):
 im=native.copy()
 # Only remove prior five words in this comparison copy. Existing UI background
 # is sampled at unused x800 at the same y; no changes to source screenshot.
 a=__import__('numpy').array(im);a[475:526,246:790]=a[475:526,800:801];return Image.fromarray(a)
def scene(key,font):
 im=clean_bar(reference_native('combat_v1_preview.png'))
 row=[('SHATTER',2,'hover'),('OBSERVE',1,'available'),('STABILIZE',1,'disabled'),('BIND',2,'retain'),('ERODE',1,'available')]
 widgets=[sigil(key,w,font,state,c) for w,c,state in row];total=sum(s.width for s in widgets)+10*4
 assert total<=560,(key,font,total)
 # Keep first word centered near original tooltip; end before END TURN.
 x=246
 for s in widgets:paste(im,s,(x,481));x+=s.width+10
 stem=f'word_sigil_in_scene_{key}'+('_pixel' if font=='pixel' else '')
 export(im,D/f'{stem}.png')
 return im,total

def main():
 existing=[p for folder in [D,Q] for p in folder.glob('*') if p.is_file()]
 if existing:
  backup=S/f'before_rebuild_{datetime.datetime.now():%Y%m%d_%H%M%S}.zip'
  with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
   for p in existing:z.write(p,str(p.relative_to(OUT)))
 strips=[];rows=[]
 for key in INFO:
  sheet(key)
  for font in ['serif','pixel']:
   im,total=scene(key,font);strips.append((key,font,im))
   six=['BIND','ERODE','SHATTER','BIND','OBSERVE','BIND'];body=sum(sigil(key,w,font).width for w in six)
   gap=max(4,min(10,(560-body)//5));assert body+5*gap<=560
   rows.append({'direction':key,'font':font,'five_word_total_width':total,'six_word_probe':six,'six_word_probe_width':body+5*gap,'six_word_gap':gap,'row_available_width':560})
 contact=Image.new('RGB',(960,696),BG)
 label(contact,(20,14),'战斗底栏对照 · 每个方向均可选两种字体',22)
 for i,(key,font,im) in enumerate(strips):
  y=55+i*105;label(contact,(20,y),f'{key}  {INFO[key][0]}   /   '+('字体 A：衬线' if font=='serif' else '字体 B：9 px 大写'),12)
  contact.paste(im.crop((0,465,960,540)),(0,y+23))
 contact.save(Q/'word_sigil_scene_comparison_1x.png');contact.resize((1920,1392),Image.Resampling.NEAREST).save(Q/'word_sigil_scene_comparison_2x.png')
 (S/'pixel_letters_9px.json').write_text(json.dumps(LETTERS,indent=2)+'\n')
 (Q/'native_metrics.json').write_text(json.dumps({'samples':METRICS,'row_probes':rows,'design_native_size':[960,736],'design_scale':4,'scene_native_size':[960,540],'scene_scale':4,'stroke_width':1,'category_slot_size':[11,11],'canonical_color':CYAN,'font_serif':'CormorantGaramond.ttf SemiBold 18; binary native glyph mask','font_pixel':'Custom partial alphabet,9px high; variable3/5px wide;2px letter space','screenshot_center_sample':'2880x1620 screenshot ->960x540, one center pixel per3x3; no average','screenshot_edit_rect':[246,475,790,526],'placeholder':'one anonymous11x11 placement cross shared by all words, no family semantics yet'},ensure_ascii=False,indent=2)+'\n')
 print('Rendered3 directions,6 full scene composites,1 scene comparison; native and4x copies.');print(rows)

if __name__=='__main__':main()
