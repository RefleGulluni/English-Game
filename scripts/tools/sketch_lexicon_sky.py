from PIL import Image, ImageDraw, ImageFont
import math, random
BOOK='art/cemetery_v3/../character_design/lexicon/lexicon_open_clean.png'
FONT='art/ui/fonts/CormorantGaramond.ttf'
S=5; PADT=10; PADR=0
PAPER=(205,189,172); INK=(44,31,24); PENCIL=(128,116,104); CYAN=(108,219,242)
BAYER=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
def base():
    b=Image.open(BOOK).convert('RGBA')
    im=Image.new('RGBA',(256,128+PADT),(0,0,0,0)); im.paste(b,(0,PADT),b); return im
def is_paper(px,x,y):
    r,g,b,a=px[x,y]; return a>200 and (0.299*r+0.587*g+0.114*b)/255>=0.55
LEFT=(26,14+PADT,118,104+PADT)
def blank(im, rect):
    px=im.load()
    for y in range(rect[1],rect[3]):
        for x in range(rect[0],rect[2]):
            if is_paper(px,x,y): px[x,y]=PAPER+(255,)
def wash(im,cx,cy,r,dens,seed,tint=0.89,rect=LEFT):
    px=im.load(); rnd=random.Random(seed); k=[rnd.uniform(0,6.28) for _ in range(3)]
    for y in range(rect[1],rect[3]):
        for x in range(rect[0],rect[2]):
            if not is_paper(px,x,y): continue
            a=math.atan2(y-cy,x-cx); d=math.hypot((x-cx)/1.3,y-cy)
            rr=r*(1+0.18*math.sin(3*a+k[0])+0.1*math.sin(5*a+k[1]))
            if d>rr: continue
            t=1-d/rr; dd=dens*min(1,t*2.2)
            if random.Random(x*7919+y*104729+seed).random() < dd*0.9:
                c=px[x,y]; px[x,y]=(int(c[0]*tint),int(c[1]*tint),int(c[2]*tint*0.98),255)
def line(im,a,b,col,dash=False):
    px=im.load(); x0,y0=a; x1,y1=b; n=max(abs(x1-x0),abs(y1-y0))
    for i in range(n+1):
        if dash and (i//2)%2: continue
        x=round(x0+(x1-x0)*i/n); y=round(y0+(y1-y0)*i/n); px[x,y]=col+(255,)
def star(im,p,kind):
    px=im.load(); x,y=p
    if kind=='pencil': px[x,y]=PENCIL+(255,)
    elif kind=='ink': px[x,y]=INK+(255,)
    elif kind=='cyan':
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            c=px[x+dx,y+dy]; px[x+dx,y+dy]=tuple(int(c[i]*0.5+CYAN[i]*0.5) for i in range(3))+(255,)
        px[x,y]=(220,248,255,255)
def up(im): return im.resize((im.width*S,im.height*S),Image.NEAREST)
def text(d,xy,s,size,col,alpha=255,anchor='la'):
    d.text((xy[0]*S,xy[1]*S),s,font=ImageFont.truetype(FONT,size),fill=col+(alpha,),anchor=anchor)
def tabs(im):
    px=im.load()
    for i,(c) in enumerate([(120,46,40),(58,74,62),(150,118,60),(64,70,96)]):
        x0=150+i*14
        for y in range(PADT-7,PADT+9):
            for x in range(x0,x0+9):
                if True:
                    k=0.82 if x in (x0,x0+8) else 1
                    px[x,y]=(int(c[0]*k),int(c[1]*k),int(c[2]*k),255)
        px[x0+4,PADT-7]=(0,0,0,0)
def right_panel(d,title,lines):
    text(d,(144,22+PADT),title,40,INK)
    y=34+PADT
    for s,col,sz in lines:
        text(d,(144,y),s,sz,col); y+=8
def tab_labels(d):
    for i,s in enumerate(['find','recent','review','stage']):
        text(d,(154.5+i*14,PADT-1.2),s,13,(235,224,206),anchor='mm')

ST={ # constellations: stars (book px) and links with stage
 'BREAK':([(40,40),(46,36),(52,41),(49,47),(43,49)],[(0,1,'cyan'),(1,2,'ink'),(2,3,'pencil'),(3,4,'pencil')]),
 'SEE':([(84,32),(90,29),(96,34),(92,40)],[(0,1,'ink'),(1,2,'ink'),(2,3,'pencil')]),
 'HOLD':([(56,74),(63,70),(70,75),(64,82)],[(0,1,'cyan'),(1,2,'cyan'),(2,3,'ink')]),
 'GRIEF':([(94,80),(100,86)],[(0,1,'pencil')]),
}
def draw_consts(im, style):
    for name,(stars,links) in ST.items():
        off=(0,PADT)
        S2=[(x,y+PADT) for x,y in stars]
        for a,b,k in links:
            col={'pencil':PENCIL,'ink':INK,'cyan':(70,150,170)}[k]
            if style=='pin' and k!='cyan': col=(170,155,140)
            line(im,S2[a],S2[b],col,dash=(k=='pencil'))
        for i,p in enumerate(S2):
            k=max([l[2] for l in links if i in l[:2]],key=['pencil','ink','cyan'].index)
            star(im,p,k)

def variant(name, style):
    im=base(); blank(im,LEFT); blank(im,(140,14+PADT,232,102+PADT)); tabs(im)
    if style=='wash':
        wash(im,46,43+PADT,17,0.55,1); wash(im,90,35+PADT,15,0.4,2); wash(im,63,76+PADT,16,0.7,3); wash(im,98,84+PADT,10,0.25,4)
    if style=='atlas':
        px=im.load(); cx,cy=72,58+PADT
        for r in (22,38):
            for t in range(0,720):
                a=t/720*6.283; x=round(cx+r*1.25*math.cos(a)); y=round(cy+r*math.sin(a))
                if LEFT[0]<=x<LEFT[2] and LEFT[1]<=y<LEFT[3] and is_paper(px,x,y) and (t//6)%2==0: px[x,y]=(176,162,146,255)
        for x in range(LEFT[0],LEFT[2]):
            y=cy
            if is_paper(px,x,y) and (x//3)%2==0: px[x,y]=(176,162,146,255)
        for y in range(LEFT[1],LEFT[3]):
            if is_paper(px,cx,y) and (y//3)%2==0: px[cx,y]=(176,162,146,255)
    if style=='pin':
        px=im.load()
        for y in range(LEFT[1],LEFT[3]):
            for x in range(LEFT[0],LEFT[2]):
                if is_paper(px,x,y):
                    c=px[x,y]; px[x,y]=(int(c[0]*0.55),int(c[1]*0.55),int(c[2]*0.62),255)
    draw_consts(im,style)
    big=up(im).convert('RGBA'); d=ImageDraw.Draw(big)
    namecol=PENCIL if style!='pin' else (200,190,176)
    for nm,(x,y) in {'Breaking':(34,26),'Seeing':(84,20),'Holding':(52,90),'Grief':(92,95)}.items():
        text(d,(x,y+PADT),nm,24,namecol, 220)
    right_panel(d,'Breaking',[('a region of the sky',PENCIL,22),('2 constellations found',INK,24),('',INK,10),('BREAK   · 4 of 5 stars',INK,24),('SCATTER · 1 of 3 stars',PENCIL,24),('',INK,10),('drag to look around',PENCIL,20),('closer: the words',PENCIL,20)])
    tab_labels(d)
    bg=Image.new('RGBA',(big.width+60,big.height+60),(24,26,28,255)); bg.paste(big,(30,30),big)
    bg.convert('RGB').save(f'docs/reference/lexicon_sky/sky_{name}.png'); return bg
a=variant('A_ink_wash','wash'); b=variant('B_atlas','atlas'); c=variant('C_pinholes','pin')
W=a.width; out=Image.new('RGB',(W,a.height*3),(24,26,28))
for i,v in enumerate([a,b,c]): out.paste(v.convert('RGB'),(0,i*a.height))
out.save('docs/reference/lexicon_sky/sky_sketches_ABC.png'); print(out.size)
