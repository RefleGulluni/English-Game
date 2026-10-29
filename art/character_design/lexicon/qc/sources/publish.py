from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
W=Path('/tmp/english-lexicon-20261029');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=W/'staged';Q=O/'qc';D=R/'art/character_design/lexicon';T=R/'art/character_design/anim/timing.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();protected=json.loads((W/'protected.json').read_text());entries=json.loads((W/'timing_entries.json').read_text());checks=json.loads((Q/'lexicon_endpoint_checks.json').read_text());sheetrel='art/character_design/lexicon_book_sheet.png'
# Source records, including the rejected side-on trial, are separate from runtime assets.
S=Q/'sources';S.mkdir(exist_ok=True)
for name in ['closed_reference.png','open_reference.png','open_clean_generated.png','fall_topdown_generated.png','tip_mid_generated.png','page_turn_generated.png','fall_topdown_geometry_guide.png','clean_books.py','restore.py','build_animation.py','verify_export.py','publish.py','world_palette.json','clean_edits.json','animation_edits.json','protected.json','lexicon_fall2_prompt.txt','lexicon_tip_prompt.txt','lexicon_page_prompt.txt']:
 shutil.copy2(W/name,S/name)
shutil.copytree(W/'native',S/'native',dirs_exist_ok=True)
unused=S/'unused_side_view_trial';unused.mkdir(exist_ok=True)
for name in ['covers_fall_generated.png','lexicon_fall_prompt.txt']:shutil.copy2(W/name,unused/name)
(S/'README.md').write_text('''# 制作来源

- 原书设计图的两块精确原生裁切作为身份、材质和颜色依据。干净书最终直接清理这些原生像素，不用生成清洁稿替换整本书；open_clean_generated.png 是去图案方向参考。
- 立起中间帧来自 tip_mid_generated.png。倒下中间帧来自 fall_topdown_generated.png；first upright 由其中窄边框原生列整理。翻页只选用 page_turn_generated.png 的两张移动纸叶，书体始终复用干净原图。
- native 中有逐格还原、边界及取样中心；只取一格中心一个像素，并映射到原设计图书体的非青蓝色，不整体缩放素材。
- animation_edits.json 记录窄边列选取、早期展开帧纸面多余列清理、纸叶选区、整数位移及原书脊像素复用。没有图像旋转或镜像。
- unused_side_view_trial 是误画成 V 形侧视的废稿，未用于交付帧。
- 脚本用于生成稿的原生格还原、像素清理、调色板归并、对齐和导出；未用程序形状替代原始美术。
''')
qa='''# Lexicon 开合与翻页 QA

日期：2026-10-29。需求：`docs/LEXICON_BOOK_ANIMATION_REQUEST.md`，采用用户本轮确认后的定位规则。只交素材，不改游戏脚本或接入程序。

## 交付与时长

| 文件 | 尺寸 | 帧数 | 参考节奏 |
|---|---|---|---|
| lexicon_closed_clean.png | 128×128 | 1 | 合书封面亮相 |
| lexicon_open_clean.png | 256×128 | 1 | 摊平的干净书 |
| lexicon_sigil_mask.png | 128×128 | 1 | 透明底白色符印遮罩 |
| lexicon_tip_up.png | 768×128 | 3，单格256×128 | 100 / 100 / 100 ms，共300 ms |
| lexicon_covers_fall.png | 1536×128 | 6，单格256×128 | 每帧100 ms，共600 ms |
| lexicon_page_turn.png | 1024×128 | 4，单格256×128 | 70 / 80 / 80 / 70 ms，共300 ms |

三条动画的锚点为 (128,64)，书脊定位用 x=128；原 timing 顶层主角 96×96 的默认值不改，书的条目写自己的 frame_size 和 anchor。素材节奏仅供参考，不代替游戏已经调好的完整开合约 2.3 / 1.8 秒：升起、唤醒、透光和星座都由程序负责。合上使用相同帧倒放，没有额外合书素材。

## 干净书与符印

合书精确取原设计图 (16,48,128,128) 区域、摊开书取 (168,48,256,128)，清除黑背景为全透明。合书仅将原青蓝印记映射到原皮面已有的暗色和少量皮面边缘色，形成暗刻；圆环、三角、三个角、底边缺口、中心点的位置取自原封面。原纸面去掉青蓝与深色星图，也清理铅笔连线和节点的残边，保留原来的折角、污渍及零星纸面旧痕。没有填新文字或新星图。

遮罩白色像素 **522** 个，逐像素等于原封面的青蓝符印足迹。只有遮罩使用白色 (255,255,255)；这张是程序输入，不受“书体不加新色”的限制。`lexicon_sigil_check_3x.png` 从左至右为干净书、白遮罩、遮罩染 #46CAD5 后叠加，青蓝只存在于这张 QC 检查图，运行书体内为 0。

## 书脊定位：采用用户确认的例外

用户已确认：合书首帧封面居中；立起过程中允许真实左书脊移到 x=128；从立起末帧开始，倒下各帧书脊固定，不能跳。这与旧稿“从第一帧起真实书脊就固定在128”的说法不同，以本段为准。

| 阶段 | 定位 |
|---|---|
| 立起1 | 合书128×128整张放到256画布的 (64,0)，封面居中；左装订带约x87 |
| 立起2 | 半侧封面，左装订带约x109；允许向中线移动 |
| 立起3 | 15 px 宽的窄书边，书脊x128 |
| 倒下1～6 | 每帧书脊x128；复用同一组原书脊像素x127～129 |
| 翻页1～4 | 书体固定，纸叶从中央装订处向左翻；书脊x128 |

立起前两帧的位置是可见装订带的近似中心，不将它伪写成固定128。固定阶段则不仅定位相同：x127～129 三列的 RGBA 也逐帧完全相同。左右纸张的污渍、磨损不同，未镜像复制。

## 端点逐像素校验（RGBA SHA256）

哈希对原生、完整画布 RGBA 字节计算。合书先嵌入256×128后比较，不拿不同尺寸的图直接比哈希。

'''
pairs=[('合书嵌入画布 / 立起第1帧','tip_first_centered_closed_rgba_sha256','tip_first_actual_rgba_sha256'),('立起第3帧 / 倒下第1帧','tip_last_rgba_sha256','fall_first_rgba_sha256'),('干净摊开书 / 倒下第6帧','open_clean_rgba_sha256','fall_last_rgba_sha256'),('干净摊开书 / 翻页第1帧','open_clean_rgba_sha256','page_first_rgba_sha256'),('干净摊开书 / 翻页第4帧','open_clean_rgba_sha256','page_last_rgba_sha256')]
for label,a,b in pairs:
 assert checks[a]==checks[b];qa+=f'- **{label}：完全一致**\n  - 两者 RGBA SHA256：`{checks[a]}`\n'
qa+=f'''\n固定书脊三列 SHA256：`{checks['fixed_binding_x127_through129_rgba_sha256']}`。完整结果在 `lexicon_endpoint_checks.json`，每个帧的 PNG / RGBA 哈希在对应 metrics。

## 颜色、透明度与预览检查

- 颜色集合取自原设计图书体的 45 种非青蓝颜色。干净合书 38 色，干净摊开书 27 色；所有动画像素也都是这组已有颜色，没有新造颜色。白遮罩单列为功能性例外。
- 运行六张 PNG 及13张原生单帧的 Alpha 仅0/255，半透明像素0；透明像素的 RGB 也为0。书体青蓝0，无光晕、地面/桌面投影、额外描边或速度线。
- 已运行仓库 `scripts/tools/pixel_check.py`；结果在 `lexicon_pixel_check.txt`。空白纸面换色比例较低（干净摊开书约26%），没有为刷细节数字往纸上加噪点。
- 生成稿先按实际方格边界取中心，还原原生像素，再归并到原调色板。tip 中间稿观测格距约9.3；俯视倒下稿约2.8；翻页稿约3个源像素一格。原稿、逐格边界、取样点、原生稿、选区与整数移动全部保留在 `sources/`，未对原画做整体缩放、旋转或镜像。
- 倒下早期第2帧从原生稿删去左右纸面内部各16列，保留皮边和中央装订，以整理投影宽度；窄边从生成稿选取15列，并复用原书脊。不是把整张书用缩放工具压窄。
- 翻页只选用两个生成纸叶的原生像素选区，其余书体逐像素复用干净摊开书。只翻一张，右侧抬起、越过中线落向左侧，最后回到干净书。
- `lexicon_opening_3x.gif` 有9个槽（立起3+倒下6），总900 ms；交接处相同的两帧仍保留各自100 ms，方便和两条运行条带核对。`lexicon_page_turn_3x.gif` 4帧、300 ms。均 nearest3倍，重解码检查每帧 RGB、Alpha、时长完全一致。

## 原素材保护与 timing

原设计图 PNG 修改前 SHA256：`{protected[sheetrel]}`。交付后复核仍是同一值；原设计图、主角已有翻书动画、所有其他已有角色素材都不改。

仅给 `art/character_design/anim/timing.json` 的 animations 追加 `lexicon_tip_up`、`lexicon_covers_fall`、`lexicon_page_turn` 三项（4→7），旧四项与顶层字段逐值相同。sprite_sheet 相对该 timing 文件指向 `../lexicon/`。原 timing 已备份在本次新目录 `qc/backups/before_lexicon_20261029/hero_anim_timing.json`。

旧文件字节校验与最终源图哈希见 `lexicon_preservation.json`。既有游戏场景、脚本以及工作区原有的其他改动都没有处理。

## 如实说明：需要游戏里判断的部分

1. 俯视视角下，用中央多层纸边和稍晚铺平的纸面表达散开，没有采用侧视示意中的大 V 形扇面。厚皮封面与纸张的轻重感仍需按 Tab 连续开合验收；数字检查不能证明动作有分量。
2. 立起的半侧封面是单独画的透视中间帧，暗刻、磨损和纸纹不像首末端点那样逐像素固定；不能声称每一处污渍在三维旋转中都严格追踪同一个表面点。倒下中间帧的旧痕也有细小变化。
3. 只有4帧翻页，左右纸叶中间姿态能读出单页翻动，但没有额外的“完全竖立”停顿帧。薄纸受光和轮廓的连续感需实际播放判断。
4. 干净纸上留少量原有铅笔点、短划与污迹，未画成第二套星图。程序星座叠加后的可读性尚未在游戏内验证。
5. 首版动作生成稿误成 V 形侧视，已弃用，未拿它充当俯视动画；在 sources/unused_side_view_trial 留档。干净书采用原图逐像素清理，生成清洁稿只作参考，未冒称整本生成稿是正式书。

完成本轮交付后停下，等待用户在游戏里验收。
'''
(Q/'lexicon_book_QA.md').write_text(qa)
(Q/'lexicon_index.md').write_text('''# Lexicon 书 · 开合与翻页

[开启动画3倍 GIF](lexicon_opening_3x.gif) · [翻页3倍 GIF](lexicon_page_turn_3x.gif) · [暗刻与遮罩对位检查](lexicon_sigil_check_3x.png) · [QA](lexicon_book_QA.md)

- [干净合书](../lexicon_closed_clean.png)
- [干净摊开书](../lexicon_open_clean.png)
- [白色符印遮罩](../lexicon_sigil_mask.png)
- [立起3帧条带](../lexicon_tip_up.png) / [逐帧图](lexicon_tip_up_contact_2x.png)
- [两边倒下6帧条带](../lexicon_covers_fall.png) / [逐帧图](lexicon_covers_fall_contact_2x.png)
- [翻页4帧条带](../lexicon_page_turn.png) / [逐帧图](lexicon_page_turn_contact_2x.png)

书脊定位按用户修正：封面先居中，立起末帧起书脊固定 x=128。语言层由程序绘制。
''')
# Do not touch any existing asset; assert the recorded character tree is unchanged first.
changed=[rel for rel,h in protected.items() if not (R/rel).exists() or sha(R/rel)!=h];assert not changed,changed
assert not D.exists();old=json.loads(T.read_text());assert len(old['animations'])==4
for n in entries:assert n not in old['animations']
backup=Q/'backups/before_lexicon_20261029';backup.mkdir(parents=True);shutil.copy2(T,backup/'hero_anim_timing.json');assert sha(backup/'hero_anim_timing.json')==protected['art/character_design/anim/timing.json']
shutil.copytree(O,D)
new=json.loads(json.dumps(old));new['animations'].update(entries);T.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n');read=json.loads(T.read_text());assert len(read['animations'])==7
for k,v in old.items():
 if k!='animations':assert read[k]==v
for k,v in old['animations'].items():assert read['animations'][k]==v
changed=[rel for rel,h in protected.items() if not (R/rel).exists() or sha(R/rel)!=h];assert changed==['art/character_design/anim/timing.json'],changed
for p in O.rglob('*'):
 if p.is_file():assert sha(p)==sha(D/p.relative_to(O))
report={'date':'2026-10-29','previous_character_files_checked':len(protected),'changed_existing_files':changed,'existing_assets_byte_identical':True,'old_timing_entries':4,'new_timing_entries':7,'all_old_timing_values_equal':True,'new_entries':list(entries),'design_sheet_before_sha256':protected[sheetrel],'design_sheet_after_sha256':sha(R/sheetrel),'backup_timing_sha256':sha(D/'qc/backups/before_lexicon_20261029/hero_anim_timing.json'),'published_files':{str(p.relative_to(O)):sha(p) for p in O.rglob('*') if p.is_file()}}
(D/'qc/lexicon_preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'published_files':len(report['published_files']),'protected_character_files':len(protected),'only_existing_change':changed,'old_sheet_unchanged':report['design_sheet_before_sha256']==report['design_sheet_after_sha256'],'runtime_files':6,'frames':13,'timing_entries_added':list(entries)},indent=2))
