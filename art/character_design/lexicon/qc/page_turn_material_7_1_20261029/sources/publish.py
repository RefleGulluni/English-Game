from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');D=R/'art/character_design/lexicon';W=Path('/Users/mac/.codex/work/lexicon-paper-7_1');S=W/'staged';Q=D/'qc/page_turn_material_7_1_20261029';Q.mkdir(exist_ok=True)
# Six already-backed-up existing files are the entire modification scope.
for f in ['lexicon_open_clean.png','lexicon_page_turn.png','lexicon_covers_fall.png','qc/lexicon_page_turn_3x.gif','qc/lexicon_opening_3x.gif']:shutil.copy2(S/f,D/f)
for p in (S/'qc').iterdir():
 if p.name in ['lexicon_page_turn_3x.gif','lexicon_opening_3x.gif']:continue
 if p.is_dir():shutil.copytree(p,Q/p.name,dirs_exist_ok=True)
 else:shutil.copy2(p,Q/p.name)
sources=Q/'sources';sources.mkdir(exist_ok=True)
for f in ['revise.py','publish.py','before.json']:shutil.copy2(W/f,sources/f)
shutil.copy2('/Users/mac/.codex/generated_images/01a16768-6cb4-7a02-aee2-ae3ac8b12896/exec-27f46654-931f-4477-b4dc-f2f6ad7b2f32.png',sources/'corner_layering_guide_generated.png')
(sources/'prompt.txt').write_text('Built-in image_gen; precise-object-edit guide. Preserve original book identity, stains, aged margins and leather. Align paper bottoms, join upper inner edges naturally, and lift existing upper folded corners in front of the leather with tiny parchment shadow. No new ornaments/colors/cyan, hard square pixels, transparent background. Guide only: runtime keeps original native generated pixels and accepted leaf silhouettes; texture is sampled directly from original respective pages, with palette-only darker mapping on reverse. No raw guide downsampling into the sprite.\n')
m=json.loads((Q/'metrics.json').read_text());rows=[]
for r in m['frames']:
 b=r['bbox_inclusive'];bb='无；逐像素等于摊开书' if b is None else f'x={b[0]}～{b[2]}，y={b[1]}～{b[3]}'
 rows.append(f"| {r['frame']} | {r['diff_pixels']} | {bb} |")
def statrow(name,s):return f"| {name} | {s['pixels']} | {', '.join(map(str,s['mean_rgb']))} | {s['mean_luma']} | {s['luma_std']} | {s['colors']} |"
stats=[statrow('摊开书右页（实际纸面）',m['actual_right_page_reference']),statrow('摊开书左页（实际纸面）',m['actual_left_page_reference']),statrow('第3帧，抬起纸的正面',m['frames'][2]['leaf_material']),statrow('第5帧，落向左侧的背面',m['frames'][4]['leaf_material'])]
oldqa=(D/'qc/lexicon_book_QA.md').read_text()
new=f'''# §7.1 第二轮翻页与纸页修整 — 2026-10-29

**当前交付以本节为准；下方旧报告为历史记录。** `page_turn_material_7_1_20261029/metrics.json`、`frames/`、`page_turn_contact_3x.png` 为本轮最终条带实测。旧版 QC 文件保留，不混写为当前数据。

## 本轮改动

- 保留已通过的原生纸叶轮廓、六帧结构与 x=128 书脊。只制作从右往左翻；程序负责逆播。
- 抬起纸的正面直接逐像素取右页的旧纸纹、污渍、零星旧痕和黄褐色边；按既有弯曲轮廓逐行投影取样，无平滑插值、无随机纹理。正面10色，不再用3色填满。背面逐行取左页的独立纸纹，映射到书上已有颜色的暗一档，未镜像正面；暗档归并后4色，仍保留纸面污渍和老化边的分布。
- 第2帧变化只在外角 x212～235、y2～33；原书脊一带完全不变。外角明显抬高，折口下露黄褐色纸影，纸边1px，没有浅色竖线。
- 摊开书两页主纸面下沿统一 y=109；内侧上沿在书脊两侧接到相同的 y=14，保留中间暗装订槽。两个上外角沿用原折角像素形状，仅向前、向上整理到皮边前面；纸下用原纸色留少量阴影，没有桌面投影。纸层下方原有纸叠/皮封轮廓不截断、不删行列。
- `covers_fall` 第6帧同步为新摊开书。检查后第5帧只调整两个上角的10个像素，让纸尖在皮边前；几何、时长和其他像素不动。第1～4帧完全未改。

## 最终条带逐帧差异

每格256×128，条带1536×128，坐标从0起、范围含首尾。与**本轮摊开书**比较完整 RGBA，读取已保存条带重新切帧计算。

| 帧 | 不同像素数 | 差异范围 |
|---|---:|---|
{chr(10).join(rows)}

第4帧只在 x128 有纸叶，原生1px宽，共98行（y7～104）；其中92个像素与底书不同，另6个恰与该位置底书原色一致，不是缺行。第3、5帧的纸叶轮廓各行都接到 x128，无透明断缝。第2帧的主体仍平贴右页，只有外角抬起，不能把“整条亮缝”当作铰链。各帧的图层和独立帧留在本轮 QC 中供检查。

## 材质颜色对比

亮度 Y=0.299R+0.587G+0.114B，标准差为总体标准差。不含透明像素。摊开书参照区：右 x135～234、左 x26～124，y8～109；排除 Y<110 的皮封/装订色，包含纸边和污渍。移动纸叶统计完整可见纸叶蒙版，含变深的边缘；采样口径不同，不能要求标准差完全相等。第2帧只翘一角，第4帧只露纸边，二者不作为整张纸面的统计参照，细项在 JSON。

| 纸面 | 像素数 | 平均 RGB | 平均亮度 | 亮度标准差 | 颜色数 |
|---|---:|---|---:|---:|---:|
{chr(10).join(stats)}

正面纸叶与实际右页平均亮度相差约 {abs(m['frames'][2]['leaf_material']['mean_luma']-m['actual_right_page_reference']['mean_luma']):.2f}，材质接近；背面较左页暗约 {m['actual_left_page_reference']['mean_luma']-m['frames'][4]['leaf_material']['mean_luma']:.2f}，是受光较少的同类旧纸。数字只验证色彩分布，纸张轻薄感仍需游戏播放验收。

## 端点、像素与时长

新摊开书、`covers_fall`第6帧、`page_turn`第1/6帧，完整 RGBA SHA256 完全一致：
`{m['open_rgba_sha256']}`

- 六帧各100ms，总600ms；`timing.json`已是该值，**本轮不改它**。
- 新摊开书27色、翻页条带27色、倒下条带40色。相对原书体颜色集合新增0；alpha只有0/255；青蓝0；没有抗锯齿、光晕或新增投影。
- 仓库 `pixel_check.py` 已运行，报告见本轮 `pixel_check.txt`。
- 两张3倍 GIF nearest 放大，解码逐帧比较 RGBA 和100ms时长完全一致。开合 GIF 仍为立起3帧+倒下6帧，共900ms的素材预览；游戏完整时序由程序负责。

## 备份、保护与来源

修改前六个文件分别备份在 `backups/before_paper_material_7_1_20261029/`。本轮仅修改干净摊开书、翻页条带、倒下条带、两个相应GIF、此QA；合书、遮罩、立起条带、原设计图、主角及骷髅动画、时序和游戏程序不改。逐文件校验见 `preservation.json`。

制作沿用已生成并验收的原生素材。内置 image_gen 另出一张折角前后关系参考，存于本轮 `sources/`，只用于核对层次；没有把整张参考缩小替换原素材。正式改动是原生像素局部清理、原纸纹取样和既有调色板映射；没有新画随机污点。完整处理记录和提示词同目录留档。

已完成本轮交付，**停下等待用户在游戏里验收**；未宣称已经在游戏中验证。

---

# 历史记录（以下哈希、4帧/旧纸面描述不代表本轮）

'''
(D/'qc/lexicon_book_QA.md').write_text(new+oldqa)
# Audit every preexisting character file; backups and QC evidence are additional.
before=json.loads((W/'before.json').read_text());changed=[];missing=[]
for rel,h in before.items():
 p=R/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(rel)
expected={'art/character_design/lexicon/'+f for f in ['lexicon_open_clean.png','lexicon_page_turn.png','lexicon_covers_fall.png','qc/lexicon_page_turn_3x.gif','qc/lexicon_opening_3x.gif','qc/lexicon_book_QA.md']}
assert set(changed)==expected,(changed,missing);assert not missing
# Recheck installed endpoint images.
a=np.array(Image.open(D/'lexicon_open_clean.png').convert('RGBA'));f=np.array(Image.open(D/'lexicon_covers_fall.png').convert('RGBA'));t=np.array(Image.open(D/'lexicon_page_turn.png').convert('RGBA'))
assert np.array_equal(a,f[:,-256:]) and np.array_equal(a,t[:,:256]) and np.array_equal(a,t[:,-256:])
(Q/'preservation.json').write_text(json.dumps({'preexisting_files_checked':len(before),'changed_existing_files':changed,'missing_files':missing,'timing_unchanged':True,'installed_endpoints_exact':True},indent=2))
print('Published; protected audit passed:',len(before),'preexisting files; only6 authorized changed.')
