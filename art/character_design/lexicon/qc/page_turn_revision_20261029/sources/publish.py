from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,subprocess,sys
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/tmp/lexicon-page-revision-20261029');D=R/'art/character_design/lexicon';O=W/'staged';Q=O/'qc/page_turn_revision_20261029';S=Q/'sources';T=R/'art/character_design/anim/timing.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();protected=json.loads((W/'protected.json').read_text());m=json.loads((Q/'page_turn_metrics.json').read_text());oldqa=(D/'qc/lexicon_book_QA.md').read_text();oldtiming=json.loads(T.read_text())
# Existing-character protection before overwrite.
assert all((R/p).exists() and sha(R/p)==h for p,h in protected.items())
for n in ['page_leaves_square_generated.png','prompt_square.txt','build.py','publish.py','protected.json']:shutil.copy2(W/n,S/n)
unused=S/'unused_short_leaf_trial';unused.mkdir(exist_ok=True)
for n in ['page_leaves_generated.png','prompt.txt']:shutil.copy2(W/n,unused/n)
run=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),str(O/'lexicon_page_turn.png'),*map(str,sorted((Q/'frames').glob('*.png')))],cwd=R,capture_output=True,text=True,check=True);(Q/'pixel_check.txt').write_text(run.stdout)
rows=[]
poses=['摊开（标准图）','右页外角小幅掀起','弯曲抬起','竖立，仅1 px纸边','纸背面落到左页上方','落平（标准图）']
for f,label in zip(m['frames_metrics'],poses):
 b=f['different_from_open_bbox_inclusive'];bb='—（与标准图相同）' if b is None else f"x={b[0]}～{b[2]}，y={b[1]}～{b[3]}"
 rows.append(f"| {f['frame']} | {label} | {f['different_from_open_count']} | {bb} | {f['different_from_previous_count']} |")
new='''# Lexicon 书 QA · 当前翻页为六帧返修版

日期：2026-10-29。按 `docs/LEXICON_BOOK_ANIMATION_REQUEST.md` §7 执行。**以下本轮六帧记录是当前翻页的验收依据；后面的历史四帧翻页与“7 px 竖立纸边”描述已作废。开合书素材保持已通过版本。**

## 当前交付

- `lexicon_page_turn.png`：1536×128，横排六格，每格256×128。
- ①摊开 → ②右页外角掀起 → ③弯曲抬起 → ④竖立1 px纸边 → ⑤背面落在左页上方 → ⑥落平。
- 每帧100 ms，总600 ms。锚点仍为(128,64)，书脊x=128。只更新原 timing 中的 `lexicon_page_turn`，其他条目、顶层字段逐值不变。
- [当前3倍GIF](lexicon_page_turn_3x.gif)；[本轮六帧3倍接触表](page_turn_revision_20261029/page_turn_contact_3x.png)；[从最终条带提取的六张原生帧](page_turn_revision_20261029/frames/)；[本轮逐帧metrics](page_turn_revision_20261029/page_turn_metrics.json)。

## 从最终条带重新提取的差异实测

比较对象始终是未修改的 `lexicon_open_clean.png`，逐像素比较完整RGBA。下面的坐标范围**两端包含**。第1、6帧按要求与标准图相同；中间第2～5帧均有真实变化，任意相邻帧也都有变化。

| 帧 | 动作 | 相对摊开书不同的像素数 | 变化像素包围范围 | 相对上一帧变化像素数 |
|---|---|---:|---|---:|
'''+ '\n'.join(rows)+'''

第4帧差异恰好全部在 **x=128、y=7～104**，共 **98像素**，宽度恰好 **1 px**。这组变化已从正式条带解码后实测，纸边确实进入成品；不是只检查临时纸层或在QA里描述。

第5帧书脊左侧（x<128）的变化像素为 **'''+str(m['frames_metrics'][4]['left_of_spine_changed_pixels'])+'''**，右侧变化为0；可证明纸已越过书脊落到左页，而不是在右页闪一下后消失。第2帧除了书脊贴合的少量像素，仅处理右外角；第3帧纸的自由边明显收向书脊。

## 贴合书脊与薄纸

单独保存本轮浮起纸层 `leaf_layer_02/03/04/05.png` 作为检查证据。每层内侧边都到达x=128；逐行检查实际纸层，而不是拿下面本来不透明的书当作“连接”。

| 帧 | x=128 连续贴合的y范围（含两端） | 缺失行 | 纸层每行内部透明断缝 |
|---|---|---|---|
| 2 | 10～111 | 0 | 0 |
| 3 | 7～105 | 0 | 0 |
| 4 | 7～104 | 0 | 0 |
| 5 | 7～110 | 0 | 0 |

浮起纸页只用原纸色 #CDBDAC、#C3AA91、#BA9B7D；没有黑色、深棕轮廓或厚暗楔。纸边通过原有轮廓**向内一像素**着稍暗纸色表现，不向轮廓外加描边。第3帧用两档纸色表现弯曲，第5帧纸背面略暗、旧痕更少，来自独立左落姿态，不是右侧翻转。第4帧使用生成边视纸叶逐行整理为1px，颜色为原纸色#C3AA91，在原暗书脊前有明确差异。

## 首尾哈希、颜色与GIF核验

标准摊开书、第1帧、第6帧完整256×128 RGBA的SHA256均为：

`'''+m['rgba_open_sha256']+'''`

'''
for f in m['frames_metrics'][1:5]:new+=f"- 第{f['frame']}帧 RGBA SHA256：`{f['rgba_sha256']}`\n"
new+='''
- 六帧均只用原设计书已有颜色，新增颜色0、半透明像素0、青蓝像素0。透明像素RGB也为0。
- 原生素材没有旋转、镜像或整体缩放。新纸叶稿按实际约5.3源像素一格逐格取中心还原；保留格线边界、原生稿与提示词。第一轮纸叶过小，未用于交付，留在unused目录。
- 只选取生成原生纸页，进行调色、单像素边缘清理与整数对齐；第2帧复用标准右页，只换外角与贴合边；第3、5帧清理采样小孔，确保贴着装订。未用程序形状替代纸叶原稿。
- GIF为nearest3倍、六帧、各100ms，总600ms。重解码逐帧验证RGB、Alpha、时长与最终PNG条带一致；保存时保留与首帧相同的落平末帧。
- 已运行仓库 `scripts/tools/pixel_check.py`，完整结果在 `page_turn_revision_20261029/pixel_check.txt`。

## 保护范围与备份

覆盖前备份四个文件：翻页PNG、翻页GIF、主角anim/timing.json和本QA，目录为 `qc/backups/before_page_turn_6frame_20261029/`，保持其相对仓库路径。除了这四个文件，没有改动任何已有文件；开合两条、干净书、遮罩、原设定图及主角翻书动画均保持原文件字节。

为遵守“其他文件不要动”，旧的 `lexicon_page_turn_metrics.json`、旧接触表及旧frames目录保留未改，属于第一版档案，**不用于本轮六帧验收**。本轮全部核验结果与六张原生帧放在新的 `qc/page_turn_revision_20261029/`，以本节链接为准。

## 仍需游戏里判断

第4帧按要求只有1px纸边，3倍显示为3px宽，持续100ms；数字检查已证明它可见且进入成品，但能否在开书星座和文字叠加后仍清楚，需要实际游戏验证。第5帧是较安静的纸背面，未画额外阴影强化悬空感；薄纸翻动的轻重与连贯性仍由用户验收。尚未在游戏中触发新版翻页。

---

# 以下为上一轮记录（开合仍有效，旧四帧翻页已被上面的六帧记录替代）

'''
(W/'lexicon_book_QA.md').write_text(new+oldqa)
# Update only the authorized timing entry.
newtiming=json.loads(json.dumps(oldtiming));t=newtiming['animations']['lexicon_page_turn'];t.update(frames=6,durations_ms=[100]*6,duration_ms=600,spine_x_by_frame=[128]*6)
(W/'timing.json').write_text(json.dumps(newtiming,ensure_ascii=False,indent=2)+'\n')
targets={D/'lexicon_page_turn.png':O/'lexicon_page_turn.png',D/'qc/lexicon_page_turn_3x.gif':W/'lexicon_page_turn_3x.gif',D/'qc/lexicon_book_QA.md':W/'lexicon_book_QA.md',T:W/'timing.json'}
backup=D/'qc/backups/before_page_turn_6frame_20261029';assert not backup.exists()
for dest in targets:
 b=backup/dest.relative_to(R);b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,b);assert sha(b)==protected[str(dest.relative_to(R))]
newfolder=D/'qc/page_turn_revision_20261029';assert not newfolder.exists();shutil.copytree(Q,newfolder)
for dest,src in targets.items():shutil.copy2(src,dest);assert sha(src)==sha(dest)
# Re-open final installed PNG and extract all differences AGAIN.
base=np.array(Image.open(D/'lexicon_open_clean.png').convert('RGBA'));strip=np.array(Image.open(D/'lexicon_page_turn.png').convert('RGBA'));assert strip.shape==(128,1536,4)
for k,row in enumerate(m['frames_metrics']):
 a=strip[:,k*256:(k+1)*256];assert hashlib.sha256(a.tobytes()).hexdigest()==row['rgba_sha256'];assert int((a!=base).any(2).sum())==row['different_from_open_count']
actual=json.loads(T.read_text());assert actual==newtiming
for k,v in oldtiming.items():
 if k=='animations':
  for n,item in v.items():
   if n!='lexicon_page_turn':assert actual[k][n]==item
 else:assert actual[k]==v
allowed={str(p.relative_to(R)) for p in targets};diff={p for p,h in protected.items() if not (R/p).exists() or sha(R/p)!=h};assert diff==allowed,(diff,allowed)
report={'date':'2026-10-29','protected_existing_files':len(protected),'changed_existing_files':sorted(diff),'only_authorized_four_files_changed':True,'other_timing_entries_equal':True,'all_other_existing_files_byte_identical':True,'installed_strip_sha256':sha(D/'lexicon_page_turn.png'),'installed_gif_sha256':sha(D/'qc/lexicon_page_turn_3x.gif'),'final_strip_metrics':m['frames_metrics'],'backup':str(backup.relative_to(R))}
(newfolder/'preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'files_checked':len(protected),'changed_existing':sorted(diff),'frames':6,'duration_ms':600,'frame_diff_counts':[f['different_from_open_count'] for f in m['frames_metrics']],'frame5_left_changed':m['frames_metrics'][4]['left_of_spine_changed_pixels'],'all_checks_passed':True},indent=2))
