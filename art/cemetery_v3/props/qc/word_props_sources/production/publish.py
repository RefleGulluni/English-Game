from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');W=Path('/Users/mac/.codex/work/cemetery-word-props-20261029');O=W/'staged';Q=O/'qc';S=Q/'word_props_sources';P=R/'art/cemetery_v3/props';m=json.loads((Q/'word_props_metrics.json').read_text());rec=json.loads((S/'cleanup_index.json').read_text());names=list(m)
words={'raven_ground_01':['raven'],'tombstone_raven_01':['raven'],'tombstone_mossy_01':['moss','conceal','epitaph'],'grave_bell_01':['bell','bury','linger'],'bell_frame_01':['bell','echo','silence'],'crypt_sealed_01':['seal','bind'],'old_well_01':['toxic'],'fresh_grave_mound_01':['bury']}
desc={
'raven_ground_01':'粗壮喙、蓬松喉羽、折叠的翅与楔尾；侧身朝右，头略转向镜头。近黑羽毛用冷灰紫受光面分组，不用纯黑剪影。少量踩乱的土单独在base里。',
'tombstone_raven_01':'以已通过 tombstone_upright_01 的立体层和底座原生像素为底，整数位移添加同一只渡鸦，整个立体物件一张PNG按碑脚排序。逐像素保留原石头、刻痕和泥土；两只脚贴合碑顶，不独立生成第二种石头。',
'tombstone_mossy_01':'苔藓从下半部和左缘爬进中央碑面，遮住下方刻痕，只剩上半段不可辨识的浅凿痕。灰绿苔团有亮侧、深侧和湿缝；石头沿用旧墓碑与高门柱的色系，苔在底座继续铺到地面。',
'grave_bell_01':'旧铜铃的钟口、铃舌和锈钩形成小剪影；细绳从铃下垂入压实土中的深色小孔。杆和绳的直段用原生像素补长2行，达到40px可见高；没有整件缩放。',
'bell_frame_01':'两根开裂的粗木柱与斜旧雨帽，榫接横梁下悬一口大铜钟；绳尾散成毛边。木纹、节点、磨亮的边和铁箍锈沿用旧路牌/木十字架的材质，铜钟另保留生成稿的暗铜色。',
'crypt_sealed_01':'低山墙、短方柱、两级台阶组成墓室门面。两根横铁条、锈链与大锁共同封门，门缝整理为暗铅/旧灰浆，非敞开黑洞。门楣不写字；石头接近同一石匠的高门柱，进深仅由短侧墙和台阶表达。',
'old_well_01':'偏斜木架、盘绳和旧桶跨过圆井圈，前井沿挡住水。水面保留生成稿横向油痕和浑浊层次，仅调成近黑褐灰，不发亮、不变绿。井边完全没有草苔，裸露灰褐死土形成清楚的荒圈。',
'fresh_grave_mound_01':'土块、湿暗缝与铁锹拍痕形成低隆土堆，整堆全部在base层；prop层只有铁锹。使用小土堆稿与另一同物件稿中完整的铁锹原生选区，整数合成，保留更清楚的木柄和锈铁铲；未压缩、旋转或穿过斜边删行。'}
rows=[]
for n,a in m.items():
 w,h=a['canvas'];p=a['prop'];b=a['base'];bb=p['bbox'];vis=f"{bb[2]-bb[0]}×{bb[3]-bb[1]}" if bb else '空';rows.append(f"| `{n}` | {w}×{h} | ({w//2},{h}) | {vis} | {p['colors']} / {p['change']}% | {b['colors']} / {b['change']}% |")
sections=[]
for n in names:sections.append('### '+n+' — '+', '.join(words[n])+'\n\n'+desc[n]+'\n\n来源：`word_props_sources/'+n+'/`；选定生成稿、逐格还原图、格线检查、原生清理结果与6倍图可逐项核对。')
qa=f'''# 墓园词汇物件8件 — QA / 2026-10-29

状态：**制作与离线检查完成，等待用户在游戏内验收**。未修改游戏房间、脚本、碰撞或已通过的物件。

## 交付

`art/cemetery_v3/props/`：8张立体PNG + 8张同名 `_base` PNG；两层画布、底边中心原点完全一致，画布底部透明留白不裁。`props_manifest.json` 只新增这8件和本批登记，已有字段与条目逐值保护；原manifest已备份。

- `qc/word_props_lineup_2x.png`：8件一字排开，正式 `ground_base_01.png` 铺底，旁边主角与骷髅，整数nearest2倍；另有原生1倍。
- `qc/word_props_with_entry_2x.png`：选渡鸦、苔碑、小铃和井，与上一批哀悼天使喷泉、枯树、旧墓碑同场，原生960×540后nearest2倍。仅为检查拼摆，不是游戏内截图；不替代用户走过验收。
- `qc/*_vs_hero_6x.png`：每件与96px主角并排；原生1倍同存。
- `qc/word_props_pixel_check.txt`、`qc/word_props_metrics.json`：最终PNG实测，含透明度、颜色、换色、青蓝、bbox、文件SHA256。
- `qc/word_props_sources/`：每个最终物件的生成原图、真实格线记录、逐格中心还原图、原生清理、6倍透明图和处理记录；早期过细/过大稿在各目录或 `unused_initial` 中留作来源记录，不用于交付。

## 数字

换色比例使用仓库脚本的口径：同一行水平相邻、两边均不透明的像素对；不是把透明边算进去。颜色数分别列立体层与底座层，不把它们混成一个数字。

| 文件名（省略.png） | 画布 | 原点 | 立体可见宽×高 | 立体颜色数 / 换色 | 底座颜色数 / 换色 |
|---|---|---|---|---|---|
{chr(10).join(rows)}

主角对照为44色 / 88%。所有16张运行PNG：alpha只含0/255、透明RGB归零、饱和青蓝0、无抗锯齿/发光/地面投影。`pixel_check.py`已对每张图运行；纸面或水面没有为凑数加杂点。多数底座是安静的土面，不能用立体材质≥80%的要求去强加随机纹理；新坟土堆本身承担主要体积，底座仍达到88%。渡鸦的base仅几粒土，3色/20%是有意很小。

## 每件设计与小色块的含义

{chr(10).join(sections)}

## 真实像素流程与材质

制作沿用 `docs/PIXEL_ASSET_PIPELINE.md`：内置image_gen单件生成大方块稿 → 从方块边界推算实际行列 → 每格只取中心一个颜色点 → 一格成为一个原生像素。没有整幅resize、平滑、旋转或镜像；所有最终摆放和组件合成是整数平移。nearest放大仅用于QC。每次提示词和原图路径记录在各 `generation.json`，格边、取样格距与裁掉的纯背景记录在 `grid.json`；格距随工具实际输出而定，没有拿目标尺寸反推一个虚假的网格。

颜色先按材质映射：石头参照 `tombstone_upright_01/02`、`gate_pillar_tall_01`；木头参照 `signpost_01`、`wooden_cross_01`；铁杆/铁锹参照 `iron_fence_01`。铜钟和渡鸦允许自己的材质色。苔和底座压到正式地面/草地的低饱和色域；新坟保持原土块分布，只调整颜色明暗，不能把纹理映射成几档平涂。合并近似色不抖色，清除品红污染和1～2像素游离碎点。裂缝、雨痕、地衣、木纹和锈点来自具体材质，而非随机加噪。

两件原生合成单列说明：碑顶渡鸦复用**同一已通过墓碑**，主干像素不改；新坟土堆和铁锹选自同物件的两张独立生成稿（两张原图、格线和恢复图均保留）。不是对已通过物件做覆盖，也不是把整件缩成需要的大小。

## 如实说明 / 需游戏验收

1. **尺寸不是全部卡死上限**：渡鸦35×28，比26～32长/18～24高略大，用于保留粗喙、喉羽和足趾；苔碑51px、小铃40px、钟架115px、墓室129px、老井105px、铁锹43px均在高度参考内。钟架可见宽约{m['bell_frame_01']['prop']['bbox'][2]-m['bell_frame_01']['prop']['bbox'][0]}，比60～80的参考宽；墓室与新坟的最外侧泥土/碎石也比主体参考宽。按需求允许超出，在这里注明，未为卡尺寸削断斜梁/石阶/土块。请用并排图判断占地。
2. **碑顶渡鸦68色**：原墓碑立体44色 + 同一渡鸦24色，合成后68色；没有强行减到50而改变已通过石头或另造一只变色的鸟。颜色“约30～50”在这里作为参考而非声称严格达标。
3. 地上渡鸦base有少量本来生成的土点，已压暗，不铺大接触阴影。碑顶渡鸦是固定合成物，不包含鸟类动画。
4. 老井的油光只表示浑浊暗水，周边荒圈没有草；在纯泥背景上，“无草”本来就较含蓄，最终毒性提示是否够明显仍需游戏里摆在草地边缘看。没有额外画绿光或毒符号来强化。
5. 全部运行物件经目视无可读字母。墓碑上的几道残刻、门楣磨痕不组成单词；QC图的文件名标签只用于检查，不进入运行素材。
6. 未执行Godot组装和实机验收；尺寸比例、沉入地面的深浅、底座边界与“同一个世界”的直观效果，最终由用户在游戏里判断。

## 保护与备份

`qc/backups/before_word_props_20261029/props_manifest.json` 为修改前manifest。已有物件、主角、骷髅与动画逐文件哈希核对见 `word_props_preservation.json`；只修改manifest以追加登记，其他既有素材不改。

完成本批后停下，等待用户验收。
'''
(Q/'word_props_QA.md').write_text(qa)
manifest=json.loads((P/'props_manifest.json').read_text());original=json.loads(json.dumps(manifest));family={'raven_ground_01':'raven','tombstone_raven_01':'stone_and_raven','tombstone_mossy_01':'stone_moss','grave_bell_01':'iron_bronze','bell_frame_01':'wood_bronze','crypt_sealed_01':'B_ashlar_iron','old_well_01':'stone_wood','fresh_grave_mound_01':'wet_earth_shovel'}
for n,a in m.items():
 assert n not in manifest['items'],n
 manifest['items'][n]={'prop':n+'.png','base':n+'_base.png','canvas':a['canvas'],'origin':a['origin'],'visible_height_px':a['visible_height_px'],'family':family[n],'vocabulary':words[n],'source_record':'qc/word_props_sources/'+n+'/cleanup.json','qa':'qc/word_props_QA.md','status':'pending_user_review','flat_base_only':False,'no_auto_trim':True}
manifest['cemetery_word_props_batch1']={'items':names,'count':8,'ground':'art/cemetery_v3/ground/base/ground_base_01.png','qa':'qc/word_props_QA.md','status':'pending_user_review','production':'built-in image_gen single props / painted-cell center restoration / native cleanup and integer assembly','no_whole_image_resize':True}
# Copy new delivery files only. Existing asset names are guarded above.
for n in names:
 for suffix in ['','_base']:
  p=P/(n+suffix+'.png');assert not p.exists(),p;shutil.copy2(O/p.name,p)
for p in Q.iterdir():
 d=P/'qc'/p.name
 assert not d.exists(),d
 if p.is_dir():shutil.copytree(p,d)
 else:shutil.copy2(p,d)
(P/'props_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Verify pre-existing content and old manifest entries.
for key,v in original.items():
 if key=='items':
  for n,entry in v.items():assert manifest['items'][n]==entry
 else:assert manifest[key]==v
before=json.loads((W/'before.json').read_text());changed=[];missing=[]
for rel,h in before.items():
 p=R/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(rel)
assert changed==['art/cemetery_v3/props/props_manifest.json'],changed;assert not missing,missing
# Delivered PNGs must match the staged, measured bytes exactly.
for n in names:
 for suffix,k in [('', 'prop'),('_base','base')]:assert hashlib.sha256((P/(n+suffix+'.png')).read_bytes()).hexdigest()==m[n][k]['png_sha256']
(P/'qc/word_props_preservation.json').write_text(json.dumps({'existing_files_checked':len(before),'changed_existing_files':changed,'missing_files':missing,'old_manifest_entries_unchanged':True,'new_runtime_pngs':16,'delivered_hashes_match_metrics':True},indent=2))
shutil.copy2(W/'publish.py',P/'qc/word_props_sources/production/publish.py')
print('Published8props +8bases; existing files protected:',len(before),'checked; onlymanifest appended.')
