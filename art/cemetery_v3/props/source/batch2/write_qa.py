from pathlib import Path
from PIL import Image
import json,numpy as np,shutil
W=Path('/tmp/english-game-props-batch2-20261025');R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');O=R/'art/cemetery_v3/props';Q=O/'qc';S=O/'source/batch2';rec=json.loads((W/'finish_records.json').read_text());met=json.loads((Q/'batch2_metrics.json').read_text())
order=['tombstone_upright_01_tilted','tombstone_flat_01','tombstone_pointed_01','tombstone_small_01','obelisk_01','grave_slab_01','tombstone_upright_02_broken','tombstone_cross_01_broken','rubble_pile_01','grave_vase_01','candles_01','grave_lantern_01']
ideas={
'tombstone_upright_01_tilted':('圆拱01母碑重绘的左歪状态，估测11.257°；不是旋转、镜像或剪切原图。保留左冠苔藓、冠下雨痕、三道模糊刻痕、左下地衣和右侧厚度/裂纹。','左侧压扁的泥草、右侧较高的撬起土块；灰褐石面上的浅块为地衣/崩口，暗细线为原有裂纹和刻痕。母碑只是身份依据，重画的小斑点不逐像素相同。'),
'tombstone_flat_01':('厚实平顶方碑，磨圆顶角，与圆拱、尖顶形成不同轮廓。','浅灰褐为顶面磨损，冷灰为凹陷面，深褐斜线为旧裂纹，左下浅簇为地衣，冠边暗橄榄为苔藓，面板三道痕迹不可读。'),
'tombstone_pointed_01':('窄高哥特尖拱，顶尖有小缺口；和宽圆碑有明显宽高差。','尖拱左肩的暗橄榄是苔藓，右侧深灰为厚度，面板竖长暗痕是雨渍，斜刻痕不组成文字。原生中段删除8行以控制85px高度，未缩放。'),
'tombstone_small_01':('单块低矮、偏宽的脚碑，39px高，没有底座台阶。','凹面细小灰阶是侵蚀和浅刻痕，外圈浅灰为磨圆边/地衣，脚部橄榄褐为苔藓与湿泥。删去5行面板空段；48种颜色均从三件母碑已有颜色中选取。'),
'obelisk_01':('细长方尖碑，四面锥尖和小阶脚；121px，超过96px主角。','浅面、暗右面区分立体石柱；斜暗线为裂纹，浅簇为地衣，脚部暗橄榄为苔藓。初稿原生柱身过长，删除38行中段，保留锥尖/柱脚，不作整图缩小。'),
'grave_slab_01':('直接平躺地上的薄石墓板，广阔顶面是俯视投影，没有石棺底箱。','浅边是磨损刻边，深线是浅刻痕/裂缝，右角有旧缺口，边缘泥和苔藓覆盖。三个侧面垂直截线约8/8/9px；整张投影框高61px不是离地高度。'),
'tombstone_upright_02_broken':('保留02下半截母碑，原图y>=67的1449个不透明像素及该区域全部RGBA逐点相同；断口顶两行从母碑旧冠边搬用。','旧断口灰褐、橄榄和磨圆小台阶，没有新鲜白茬。新画俯视的上半块平铺左前地面，母碑缺右上角、左冠苔藓和一条刻痕仍能辨认。碎片只在_base层。'),
'tombstone_cross_01_broken':('只去掉画面左横臂并整理根部，其他区域2562个母碑不透明像素及该区域RGBA完全一致。','原件灰石、浅地衣、根部垂苔都保留；断臂另画落地视角，压在碑脚左前的暗草中。断臂只在_base，不属于碰撞/遮挡立体层。'),
'rubble_pile_01':('低矮碎石堆，17px，作为无碰撞穿插物。','不同大小角石的浅面是崩角，深沟是夹泥，少量橄榄为石缝积苔，不是随机撒点。'),
'grave_vase_01':('26px旧石花瓶，三株弯折的枯茎和枯头，没有活花。','深口、崩唇、灰石肚和暗埋脚均可辨；褐色折线是干茎。重新生成粗格版本后，删除7行长茎中段；接触泥取自母碑01底座的原生选区，剪去矩形切口。'),
'candles_01':('四根高低不同的旧蜡烛，黑灯芯，全部熄灭，16px。','暗灰米色为旧蜡，浅小团为凝固蜡泪，石片下面是泥，黑点为灯芯。小物件仅25色、78.906%换色，低于大件80%的目标；依照小物件数字仅供参考的规定保留，未加噪点。'),
'grave_lantern_01':('32px落地旧铁墓灯，提环、顶盖、框架和暗玻璃；不点亮。','灰暗边为铁框受光/氧化，玻璃褐灰小块为污垢、映入环境的冷暖和暗内部，没有火苗或发光面。粗格重生成后只删2行玻璃中段，土取自十字碑底座。')}
lines=['# 墓园物件第二批 QA','', '日期：2026-10-25。制作：Codex 角色设计组。状态：**交付待游戏验收，尚未宣称用户通过**。','', '按 `docs/CEMETERY_PROPS_BATCH2.md` 完整制作12件，每件立体+底座，共24张正式PNG。先做并内部检查左歪01，再继续本批；没有开始骷髅。实际仓库位于 `GitHub.nosync/English-Game`。','', '## 查看顺序','', '- [全部新旧墓碑一行2倍](batch2_lineup_2x.png)','- [三组原件/状态6倍](batch2_states_6x.png)','- [15件新旧物件与B1拼装2倍](batch2_cluster_2x.png)（中性暗色检查底色，不是新制作的游戏地面）','- [墓板侧厚6倍](batch2_slab_thickness_6x.png)','- [pixel_check.py原始输出](batch2_pixel_check.txt) / [精确指标和哈希](batch2_metrics.json)','', '## 硬规格与原件保护','', '24张均为RGBA PNG，Alpha只有0/255，饱和青蓝为0，最后一行均保留透明。立体/底座同尺寸、同底边中心原点，不按可见框自动裁切。上左光、没有新增投影/光晕；灯和蜡烛都未点亮。墓碑只有不可读刻痕。','', '检查了1341个既有美术文件，SHA-256全部不变；仅既有props_manifest.json新增12项及批次信息，旧条目保持原值。清单原件备份：`/Users/mac/.codex/backups/English-Game/before-props-batch2-20261025/props_manifest.json`。所有主角、旧物件、已通过动画均未改。','', '## 指标','', '换色为横向相邻且均不透明的像素RGB不同的比例，与项目pixel_check.py同算法。下表保留精确值；脚本输出本身会四舍五入。','', '|物件|画布 / 底边原点|立体可见高|立体颜色 / 换色|底座颜色 / 换色|6倍参照|','|---|---|---:|---:|---:|---|']
for n in order:
 v=rec[n];p=v['prop'];b=v['base'];hi='侧厚约8–9；投影61' if n=='grave_slab_01' else str(p['height']);can='×'.join(map(str,v['canvas']));origin=','.join(map(str,v['origin']));lines.append(f"|`{n}`|{can} / ({origin})|{hi}|{p['colors']} / {p['adjacent_change']:.3f}%|{b['colors']} / {b['adjacent_change']:.3f}%|[图](batch2_sources/{n}/05_vs_hero_6x.png)|")
lines+=['', '8件墓碑家族立体层（含状态）颜色均在30–50，换色均>=80%；四件小物件使用各自的真实尺寸，不人为撒点追数字。底座单列：深泥合色后常只有13–15色，断件底座因叠加“原泥土+新画落地石块”有69/72色；它们不满足和立体层相同的数字区间，已如实列出。','', '## 每件意图和色块含义','']
for n in order:
 a,b=ideas[n];lines += ['### '+n,'',a,'',b,'']
lines+=['## 实际制作与还原审计','', '使用内置image_gen逐件生成大方格像素稿。每件原图、逐格还原图、网格核对、原生合成、分层8倍、B1并排6倍、检查输出均在 `qc/batch2_sources/物件名/`。断件的生成原图是新落地碎片，另附parent_original_prop/base原件；立碑未断部分直接继承原件，不伪称整件重新生成。','', '横竖边界由图像边缘周期和局部路径找出，**每格只取中心一个源像素**。验证了12件全部还原图的每个不透明像素，均和grid.json对应的源格中心RGB精确一致；没有整图resize、非整数缩放、平均采样或插值。之后只做材质合色、品红清理、原生选区/删中段/整数位移、分层和尺寸登记。','', '石头和小物件立体的颜色都从既有01/02/十字碑的原有RGB中选取；小矮碑使用三者合并色库中最常用的50个候选（最终48色），方尖碑补入少量十字碑已有灰阶（最终49色），以免过度合色抹掉有意义的坑蚀与地衣细节。没有增加随机纹理。底座收暗到已有泥土颜色，压暗的草是压倒枯草，不做亮橙环。','', '需要说明：生成格不绝对均匀，实际格边距会变化，网格边界是根据原图估计，不保证每一处生成方块都数学整齐。实际边界、原图与抽查叠线都公开，未把源稿称为完美原生手绘。下面列周期和还原尺寸（整理前）：','', '|物件|源图尺寸|估计周期x/y|实际格宽范围 / 格高范围|逐格还原尺寸|','|---|---|---|---|---|']
for n in order:
 d=Q/'batch2_sources'/n;g=json.loads((d/'grid.json').read_text());dx=np.diff(g['x_boundaries']);dy=np.diff(g['y_boundaries']);lines.append(f"|`{n}`|{'×'.join(map(str,g['source_size']))}|{g['period'][0]}/{g['period'][1]}|{min(dx)}–{max(dx)} / {min(dy)}–{max(dy)}|{'×'.join(map(str,g['native_size']))}|")
lines+=['', '生成器未一次命中全部尺寸，最终采用原生几何整理，没有伪装成缩放：尖碑删除8行、脚碑5行、方尖碑38行柱身、花瓶7行长茎、墓灯2行玻璃；这些是连续中段省去后整数接回。落地上半碑删去12行无关键身份标记的面中段，横臂删27列中段并将右端整数上移6px，使碎片和母件尺度相符。每步记录见各件native_edit.json和source/batch2/finish.py，源稿仍完整保留。','', '## 状态件核对','', '- 左歪碑角度是对中段边界中心线拟合的约11.257°，是重画后的轮廓测量，不是执行的旋转参数；冠部/底部不参与拟合。','- 断碑02母件登记偏移(24,32)，原y>=67整个区域RGBA一致；保留1449个原不透明像素。断口顶边重做、下段苔藓和裂纹不改。碎片在左前底座，立体层不含碎片。','- 断十字母件登记偏移(8,16)，仅画面左臂移除区和x38根部整理区不同；其余RGBA一致，保留2562个原不透明像素。','', '## 人工检查和待游戏确认','', '已查看1倍、6倍、三组状态和15件拼装：新旧石材、左上光、暗草底座基本一致；形状可分，两个断片是俯视贴地画法，不是位图旋转。平躺墓板的侧厚为人工识别边界约8–9px，6倍图标了三个截线；指标中的61px含整块顶面的纵深投影。','', '尚未在Godot试走：碰撞、遮挡和贴地观感须由Claude/用户验收。特别请看歪斜01与母碑的身份感、两个断片落地是否自然，以及很小的蜡烛/花瓶在实际地面上的辨识度。统计合格不能代替游戏里的判断。','', '提示词、工具模式、还原/整理配方存于 `source/batch2/`；仅预览做整数nearest放大。没有修改场景或脚本。交付后停止，等待本批验收。','']
(Q/'batch2_QA.md').write_text('\n'.join(lines))
for f in ['preview.py','verify.py','write_qa.py','publish.py']:shutil.copy2(W/f,S/f)
(S/'README.md').write_text('''# Batch2 production provenance

Built-in image_gen was used; no external CLI image generator. See prompt_set.json and generation.json for prompts, and qc/batch2_sources/<name>/ for the selected full source PNG, exact recovered native cells, recorded grid boundaries and final comparison.

The Python recipes are a historical, inspectable record, not a game dependency. They contain the working directory used during this session. The recoverable working directory (including rejected drafts and boundary recovery files) is archived at `/Users/mac/.Trash/english-game-props-batch2-working-20261025` after delivery. Source images also remain at their tool-generated paths. Set the W constant to a reconstructed scratch directory if replaying; never run publish.py against already accepted assets without a fresh backup.

No native asset was resized, mirrored, rotated or interpolated. Native row/column selections and integer translations are explicitly recorded in finish_records.json and per-object native_edit.json. Only QC/reference enlargements call nearest resize. The closed-world palette is drawn from existing approved cemetery stone and soil RGBs. All source files remain intact.

The manifest backup is outside the repository: `/Users/mac/.codex/backups/English-Game/before-props-batch2-20261025/props_manifest.json`. Existing art hash audit is in qc/batch2_metrics.json.
''')
print('QA written',len(lines),'lines')
