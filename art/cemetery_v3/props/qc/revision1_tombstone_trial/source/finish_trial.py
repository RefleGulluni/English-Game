from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
W=Path('/tmp/english-game-props-revision1-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props/qc/revision1_tombstone_trial';assert not O.exists();O.mkdir()
grid=json.loads((W/'grid_recovery.json').read_text());src=Path(grid['source']);shutil.copy2(src,O/'01_generated_original.png');shutil.copy2(W/'source_grid_check.png',O/'source_grid_check_1x.png');shutil.copy2(W/'grid_recovery.json',O/'grid_recovery.json')
im=Image.open(W/'recovered_cells_unquantized.png').convert('RGBA');a=np.array(im);alpha=a[:,:,3]>0
# Pick colors from the generated painted cells only, without creating texture.
# The palette is generated once, no dithering / noise. Alpha is preserved separately.
fg=Image.fromarray(a[alpha,:3].reshape(1,-1,3));quant=fg.quantize(colors=44,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);pal=np.array(quant.getpalette(),dtype=np.uint8).reshape(-1,3);active=pal[np.unique(np.array(quant))]
out=np.zeros_like(a)
for y,x in zip(*np.where(alpha)):
 rgb=a[y,x,:3].astype(int);j=((active.astype(int)-rgb)**2).sum(1).argmin();out[y,x,:3]=active[j];out[y,x,3]=255
# Remove residual magenta contaminated cells; no replacement drawing.
bad=(out[:,:,0].astype(int)-out[:,:,1].astype(int)>28)&(out[:,:,2].astype(int)-out[:,:,1].astype(int)>28);out[bad]=0
# Delete only tiny detached islands from the source (never add speckle / pixels).
seen=set();removed=[]
for y,x in zip(*np.where(out[:,:,3]>0)):
 if (y,x) in seen:continue
 stack=[(y,x)];seen.add((y,x));comp=[]
 while stack:
  yy,xx=stack.pop();comp.append((yy,xx))
  for dy,dx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
   ny,nx=yy+dy,xx+dx
   if 0<=ny<out.shape[0] and 0<=nx<out.shape[1] and out[ny,nx,3] and (ny,nx) not in seen:seen.add((ny,nx));stack.append((ny,nx))
 if len(comp)<=2:
  removed+=comp
  for yy,xx in comp:out[yy,xx]=0
# Reassign two isolated edge colors to their immediate in-material neighbor tone.
# These are source-cell cleanup edits, not code-generated motif/texturing.
edits=[]
for y,x in [(24,13),(52,12)]:
 if y<out.shape[0] and x<out.shape[1] and out[y,x,3] and x+1<out.shape[1] and out[y,x+1,3]:
  old=out[y,x].tolist();new=out[y,x+1].tolist()
  if old!=new:out[y,x]=new;edits.append({'xy':[x,y],'old':old,'new':new,'reason':'Source contour speck merges into adjoining stone/moss edge, no new color.'})
clean=Image.fromarray(out);clean.save(O/'02_restored_native_cells.png')
# Layer separation mask selects existing pixels only. Upper stone includes moss on it.
# The base holds source wet mud, sunken stone chips and pressed grass.
mask=Image.new('L',clean.size,0);d=ImageDraw.Draw(mask)
d.polygon([(0,0),(76,0),(76,63),(64,63),(64,76),(60,78),(52,78),(46,76),(40,76),(35,73),(29,76),(23,74),(16,72),(12,70),(12,63),(0,63)],fill=255)
m=np.array(mask)>0;prop=out.copy();base=out.copy();prop[~m]=0;base[m]=0
# All artwork copied at integer coordinates onto shared canvas; never resized.
canvas=(96,112);shift=(9,20)
pim=Image.new('RGBA',canvas);bim=Image.new('RGBA',canvas);pim.alpha_composite(Image.fromarray(prop),shift);bim.alpha_composite(Image.fromarray(base),shift)
pim.save(O/'tombstone_upright_01.png');bim.save(O/'tombstone_upright_01_base.png');combined=bim.copy();combined.alpha_composite(pim);combined.save(O/'03_tombstone_with_base_native.png')
h=Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA')
preview=Image.new('RGBA',(232,132),'#403D3F');preview.alpha_composite(h,(12,16));preview.alpha_composite(combined,(124,0));dr=ImageDraw.Draw(preview);dr.text((12,117),'B1 96px',fill='#BEB7A9');dr.text((126,117),'Tombstone trial',fill='#BEB7A9');preview.save(O/'detail_vs_hero_1x.png');preview.resize((1392,792),Image.Resampling.NEAREST).save(O/'04_detail_vs_hero_6x.png')
layers=Image.new('RGBA',(288,112),'#403D3F');layers.alpha_composite(pim,(0,0));layers.alpha_composite(bim,(96,0));layers.alpha_composite(combined,(192,0));layers.resize((1728,672),Image.Resampling.NEAREST).save(O/'layers_6x.png')
def metrics(img):
 a=np.array(img);valid=a[:,:,3]==255;pair=valid[:,:-1]&valid[:,1:];diff=np.any(a[:,:-1,:3]!=a[:,1:,:3],axis=2);ys,xs=np.where(valid)
 return {'canvas':list(img.size),'opaque_bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'visible_height':int(ys.max()-ys.min()+1),'colors':int(len(np.unique(a[valid,:3],axis=0))),'opaque_horizontal_pairs':int(pair.sum()),'different_horizontal_pairs':int((pair&diff).sum()),'change_percent':float(100*(pair&diff).sum()/pair.sum()),'alpha_values':np.unique(a[:,:,3]).tolist(),'rgba_sha256':hashlib.sha256(a.tobytes()).hexdigest()}
metrics_all={n:metrics(img) for n,img in [('hero',h),('prop',pim),('base',bim),('combined',combined)]}
for img in [pim,bim]:
 a=np.array(img);assert set(np.unique(a[:,:,3]))<={0,255};c=a[a[:,:,3]>0,:3].astype(int);assert not np.any((c[:,1]>c[:,0]+20)&(c[:,2]>c[:,0]+20)&(c.max(1)-c.min(1)>55))
(O/'trial_metrics.json').write_text(json.dumps({'metrics':metrics_all,'cleanup':{'palette':'44 colors, derived from source painted cells only; no dithering','removed_magenta_cells':int(bad.sum()),'removed_detached_small_components':[[int(x),int(y)] for y,x in removed],'explicit_neighbor_color_merges':edits},'origin':[48,112],'source_native_shift':list(shift)},indent=2))
# Verify production delivery and every outside artwork stayed intact.
b=R/'art/cemetery_v3/props/qc/backups/round1';assert all((R/'art/cemetery_v3/props'/p.name).read_bytes()==p.read_bytes() for p in b.glob('*.png'))
state=json.loads((W/'protected_hashes.json').read_text());assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==v for p,v in state.items())
lines=['# 单块墓碑 · 返修试样 QA','', '日期：2026-10-25。仅本块试样，等待验收；没有继续其他8件。','', '## 流程与证据','', '用户本轮允许先生成大像素块，再找到生成稿中实际的色块格，一格还原一个原生像素。采用第二次生成稿：提示词明确以B1的8倍图为像素大小参考，要求大方块、非写实、72px逻辑碑高；实际工具导出1254×1254，未遵守要求的768×768导出尺寸。原始导出文件完整保留为 `01_generated_original.png`，没有修图或裁切。','', '还原不是把1254×1254整体缩放到96×96：从原稿石面相邻像素差的周期峰找到格边，逐行/列追踪约12px的源色块边界；每一个检测到的源格只取中心一个像素，写为一个原生像素。没有调用resize生成素材，没有非整数比例缩放、平滑、均值混色或插值。边界列表见 `grid_recovery.json`；原稿局部叠网格见 `source_grid_check_1x.png`。','', '**局限如实说明：** 生成器画的格子不是精确等宽网格，检测格宽10～14px，以12px为主；格边依据重复结构推断，而不是获得了生成器提供的原生索引。网格核对图有部分边界仍存在约1～2个输出像素偏差，不能声称数学上恢复了每一格的唯一真值。这是本试样最需要用户确认的流程限制。未把此前非整数整图采样版当作本次交付。','', '还原结果为77×92：`02_restored_native_cells.png`。整理包括无抖色44色归并、品红污染清除、1～2px孤立碎点删除、少量边缘色并入相邻材质；无自动噪点、无程序新增纹理、无程序绘制新的石头/草。所有形状和材质纹理来自独立生成稿。再以整数位移(9,20)置入96×112画布，拆出同原点(48,112)的碑身与base。预览放大均nearest整数6倍。','', '## 统计','', '算法：只统计水平相邻且双方完全不透明的像素对；RGB不同计为一次换色；不计透明边界。与需求文档一致。','', '|对象|颜色数|水平有效像素对|换色像素对|换色比例|可见高|','|---|---:|---:|---:|---:|---:|']
for n,label in [('hero','主角标准图'),('prop','立体墓碑'),('base','底座贴花'),('combined','墓碑+底座合成')]:
 v=metrics_all[n];lines.append(f"|{label}|{v['colors']}|{v['opaque_horizontal_pairs']}|{v['different_horizontal_pairs']}|{v['change_percent']:.2f}%|{v['visible_height']}px|")
lines+=['','数值用于发现平涂差距，不以换色比例越高越好来添加噪点。碑身高在64～80px目标范围内；底座高度另算，包含压草和翻土。','', '## 细节各自代表什么','', '- 偏冷的暗灰/中灰：潮湿石面、凹槽与右侧厚度；偏暖灰：左上受光的破损石边。','- 橄榄绿/土黄绿：拱顶裂口、碑侧与脚部长期积水处的苔藓，沿裂缝下垂而非均匀撒点。','- 灰米色斑：附着石面的地衣；大斑块内的深浅差用于凹凸，不是发光。','- 赭灰/深褐竖痕：从拱顶向下的雨痕和矿物污渍；深线用于断裂与残损刻痕。','- 底座深褐：湿泥压槽与翻土；暖灰小块：风化石屑；黄褐弯折形：压倒的枯草。不是地面投影。','', '## 交付与保护','', '- `tombstone_upright_01.png` + `_base.png`：试样两层，仅本目录，不覆盖生产目录。','- `03_tombstone_with_base_native.png`：1×透明合成，便于肉眼看原生效果。','- `04_detail_vs_hero_6x.png`：与标准B1同6倍nearest并排。','- 第一版完整备份：`../backups/round1/`。正式9对PNG均与备份逐字节相同；其余已有美术逐文件哈希未变。','- 两层Alpha仅0/255，无饱和青蓝，无新增阴影、光晕或glitch。','- 不同于第一版偏细长的碑，本试样石材厚、宽度较大。形体是否过厚、苔藓是否偏黄、密度是否与B1一致，仍需1×及游戏验收。','- 还未把该试样放进Godot，也未制作其他物件。通过后再继续。']
(O/'tombstone_trial_QA.md').write_text('\n'.join(lines)+'\n');print(json.dumps(metrics_all,indent=2));print('output',O)
