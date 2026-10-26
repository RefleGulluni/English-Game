from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/english-game-skeleton-animation-20261026');S=R/'art/character_design/enemies/skeleton';P=W/'prepared';P.mkdir(exist_ok=True)
pal=np.unique(np.concatenate([np.array(Image.open(S/(n+'.png')).convert('RGBA'))[np.array(Image.open(S/(n+'.png')).convert('RGBA'))[:,:,3]>0,:3] for n in ['skeleton_B','skeleton_B_remains']]),axis=0)
def clean(a):
 a=a.copy();c=a[:,:,:3].astype(int);bad=(c[:,:,0]-c[:,:,1]>26)&(c[:,:,2]-c[:,:,1]>26);a[bad]=0;rgb=a[a[:,:,3]>0,:3].astype(int);ix=((rgb[:,None]-pal.astype(int)[None])**2).sum(2).argmin(1);a[a[:,:,3]>0,:3]=pal[ix];return a
records=[];board=Image.new('RGBA',(4*110,2*120),'#403D3F');d=ImageDraw.Draw(board)
for k in range(8):
 a=clean(np.array(Image.open(W/'walk'/f'frame_{k+1:02}.png').convert('RGBA')));bb=Image.fromarray(a).getbbox();a=a[bb[1]:bb[3],bb[0]:bb[2]];H,WW=a.shape[:2];rm=[20,26,33,43,56,65,74,82,87,91,94,97][:max(0,H-96)];rows=[y for y in range(H) if y not in rm];assert len(rows)<=96
 a=a[rows];can=np.zeros((96,96,4),dtype=np.uint8)
 # Register pelvis/rope midpoint at x48 using inspected source torso, no bbox fitting.
 torso=a[30:48];ys,xs=np.where(torso[:,:,3]>0);cx=int(np.median(xs));ox=48-cx;oy=96-a.shape[0];can[oy:oy+a.shape[0],ox:ox+WW]=a;Image.fromarray(can).save(P/f'walk_{k+1:02}.png');records.append({'frame':k+1,'crop':bb,'removed_rows':rm,'row_lookup':rows,'offset':[ox,oy]})
 x=k%4*110;y=k//4*120;board.alpha_composite(Image.fromarray(can),(x,y));
 for yy in [20,45,60,75,90,95]:d.line((x,y+yy,x+95,y+yy),fill='#755555');d.text((x,y+yy),str(yy),fill='white')
 for xx in [35,45,55,65]:d.line((x+xx,y,x+xx,y+95),fill='#555566');d.text((x+xx,y),str(xx),fill='white')
 d.text((x,y+102),str(k+1),fill='white')
board.resize((1760,960),Image.Resampling.NEAREST).save(W/'walk_native_grid_4x.png');(P/'prep.json').write_text(json.dumps(records,indent=2));(W/'palette.json').write_text(json.dumps(pal.tolist()))
