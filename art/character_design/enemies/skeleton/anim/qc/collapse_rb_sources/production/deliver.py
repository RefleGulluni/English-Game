from pathlib import Path
import json,hashlib,shutil
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';A=S/'anim';W=Path('/tmp/english-game-skeleton-collapse-rb-213-20261028');O=W/'staged';Q=O/'qc';V=Q/'collapse_rb_sources';results=json.loads((V/'verification.json').read_text());records=json.loads((V/'frame_records.json').read_text());timings=json.loads((V/'timing_entries.json').read_text());protected=json.loads((W/'protected.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for direct,result in results.items():
 name=result['name'];frames=result['frames'];isback=direct=='back';direction='背面' if isback else '右侧'
 lines=['# 骷髅 B '+direction+'散架（§21.3）','','本次与另一方向一起交付，**12 帧 / 1280 ms**；横条1152×96，每格96×96，脚底锚点(48,96)。不循环，保持第12帧。已通过的左侧、正面散架、全部标准图与其他动画不变。','','## 动作与方向','','背面单独生成后脑、脊柱与肩胛的失力姿势；第2～7帧头骨仍是背面视面，第8帧仍可见颅后部在右下方落地，第9帧才滚成朝外的共同骨堆视面。身体没有先转正站立。' if isback else '右侧单独生成右向失力姿势，保持近侧右肩双钉、裹尸布及空手关系；没有翻转左侧图，也没有镜像、软件旋转任何原生骨头。骨盆失力往下，肩与头滞后；手臂软垂，不伸掌撑地。', '', '头骨在早期就歪垂，关节松开，之后继续下坠。末段沿用左侧已验收的“无头身体 + 唯一头骨”方式；头骨一直只有一个来源实例，落地后回弹再落定。']
 if not isback:lines+=['','右侧第5帧的生成稿因腿向左展开，把头骨带得过于靠右；原生整理时仅把头骨与短颈骨选区向左登记10 px，使第5～9帧以向下落为主。相应骨头在原处先清除，再平移到新位置，没有复制两份。第6～7帧颈骨选区也按同样位置登记。参数写在 frame_records.json。']
 lines+=['','## 每个骨组只出现一次','','身体落定层先去掉整个头骨选区，不把带头的整张骨堆放在掉落头骨后面。每帧只合成一张single_skull层，与body_no_skull层重建后必须等于正式PNG。','', '骨组交接表：collapse_rb_sources/'+direct+'/bone_group_handoff.md。第1～5帧全部取同一张该方向姿势；第6～7帧只保留空中的肩/胸/骨盆/手臂，撤掉原来的腿，显示已落下的地面长骨。此时不显示骨堆里的肩、胸与手组。第8帧先撤掉空中组，再显示落地后的对应组，避免两副胸廓、两对手或两份骨盆同时在场。布的上段与下摆视为同一块布的不同部分，最后才落平。','', '24张最终图已逐帧目视检查主要骨组，没有重复头骨或多余的胸廓、手脚。选区分层与归属表用于核对交接，并非自动解剖识别器。终态骨盆被布覆盖，对照图4号标的是遮挡位置，不是在布外新画另一块骨盆。','','## 时长与头骨轨迹','','表内中心是实际输出头骨选区包围盒中心，单位为原生像素。头在不同视面中轮廓变化，故中心允许半像素数值，但实际像素位置都是整数。','','|帧|ms|头骨中心 x,y|姿态阶段|','|---|---:|---|---|']
 stages=['原方向标准图','头歪垂、手腕松开','膝/髋松开，骨盆先坠','上身与骨盆分开','骨组无支撑下坠','头骨及上身继续下落','悬落的肩、手臂和骨盆接近地面','上身与手臂落地，头骨继续滚转','头骨落位，带轻微过冲','回弹，布继续落下','回弹收回，布归位','公共骨堆，逐像素相同']
 for f,stage in zip(frames,stages):lines.append(f"|{f['frame']}|{f['duration_ms']}|{f['head_center']}|{stage}|")
 lines+=['','## 哪块骨头去了哪里','','`'+name+'_map.png`：1 头骨→骨堆右侧；2 右肩与双钉→左侧；3 胸廓/脊柱→中后部；4 骨盆→中部布下；5 斜披布→中部覆盖；6 长骨/足骨→下缘；7 前臂/手→前缘。','', '`'+name+'_skull_track_4x.png` 在每张最终图上框出唯一头骨的实际位置；同目录 contact_4x.png 是没有标框的原图逐帧总览。原生分层保存在 collapse_rb_sources/'+direct+'/layers/。','','## 严格端点与哈希','','第1帧与 `skeleton_B_'+direct+'.png` 解码RGBA逐像素相同。RGBA SHA-256：`'+result['first_rgba_sha256']+'`。','','第12帧与正面散架末帧、已通过左侧散架末帧，以及96×48原骨堆贴在(0,48)的结果，四者逐像素相同。RGBA SHA-256：`'+result['last_rgba_sha256']+'`。','','## 真像素检查','','12张原生帧全部运行仓库pixel_check.py，完整输出：collapse_rb_sources/'+direct+'/pixel_check.txt。所有输出Alpha仅0/255，新增色0，只用原48色集合；最低不透明行均为95。无青蓝、光晕、阴影、抗锯齿。GIF已逐帧解码，12帧的时长、透明度与可见RGBA都严格等于原图nearest放大8倍。','','|帧|颜色数|横向相邻换色率 %|最低不透明行|头骨层实例|','|---|---:|---:|---:|---:|']
 for f in frames:lines.append(f"|{f['frame']}|{f['colors']}|{f['neighbor_change_pct']:.3f}|95|1|")
 lines+=['','## 来源与原生整理','','两方向各调用一次内置image_gen生成独立的前期下落姿势，分别使用该方向标准图。右侧实际原图布局为2列×3行；背面生成器实际画成3列×2行，恢复时按实际六格读取，没有按错误布局切帧。原图、逐格恢复、色表整理和网格边界均归档于collapse_rb_sources/'+direct+'/。','', '可辨色块周期约4个显示像素，以边界拟合后取每格中心为一个原生像素，不将大图整体resize到96。生成网格并非严格数学等距，边界是据实际色块作出的估计。第1帧直接取原站姿，第2～5帧取新生成的完整姿势；第6个生成姿势只用于单独头骨落地视面，不把其完整身体再贴到骨堆上。','', '生成姿势的站立等效比例仍需整理：在原生骨干和布面内部选取扫描行，使前期姿势逐步降低到96画布。头骨上部与足端保留源行。所有保留/删去的源行和位移都列在frame_records.json，没有做平滑插值、整体非整数缩放、旋转或镜像。']
 lines+=['','|早期帧|原生源高度|整理后高度|移除内部行数|','|---|---:|---:|---:|']
 for rr in records[direct][1:5]:
  # Palette source retains transparent crop shape dimensions in restoration metadata.
  grid=json.loads((V/direct/'restoration_grid.json').read_text());h=grid[rr['frame']-1]['native_size'][1];kept=len(rr['row_lookup']);lines.append(f"|{rr['frame']}|{h}|{kept}|{len(rr['removed_internal_rows'])}|")
 lines+=['','## 文件保护与后续验收','','原文件逐个存档SHA-256并在交付前后核对。唯一更新的已有文件是timing.json：先备份到collapse_rb_sources/backups/timing_before_right_back.json，再追加右侧、背面两条；原53条保持内容相同，更新后55条。标准图、已通过的左侧及其他动画均未修改。','', '请在游戏内重点看第7→8帧身体落地换面的速度，以及第8→9帧头骨从下落视面滚到共同骨堆视面的衔接。静态数量、端点与色表检查不能代替动作观感验收。此次没有修改Godot工程；两条一起交付后停下，等待用户验收。']
 (Q/(name+'_QA.md')).write_text('\n'.join(lines),encoding='utf8')
# Production source retained for audit. Originals and accepted canonical layers are untouched.
production=V/'production';production.mkdir(exist_ok=True)
for n in ['recover.py','build.py','verify_qc.py','deliver.py']:shutil.copy2(W/n,production/n)
shutil.copy2(W/'protected.json',V/'protected_old_files.json')
assert all(sha(Path(p))==h for p,h in protected.items()),'An existing skeleton file changed during preparation.'
backup=V/'backups';backup.mkdir(exist_ok=True);shutil.copy2(A/'timing.json',backup/'timing_before_right_back.json');old=json.loads((A/'timing.json').read_text());assert len(old['animations'])==53;assert not set(timings)&set(old['animations']);new=json.loads(json.dumps(old));new['animations'].update(timings);assert len(new['animations'])==55
for p in O.rglob('*'):
 if p.is_file():assert not (A/p.relative_to(O)).exists(),str(A/p.relative_to(O))
for p in O.rglob('*'):
 if p.is_file():dest=A/p.relative_to(O);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(A/'timing.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for p,h in protected.items():
 if Path(p)!=A/'timing.json':assert sha(Path(p))==h,p
actual=json.loads((A/'timing.json').read_text());assert len(actual['animations'])==55;assert {k:v for k,v in actual['animations'].items() if k not in timings}==old['animations']
print('Delivered two new 12-frame strips, 24 frame PNGs, 8x GIFs, maps, skull trajectories and per-direction QA. timing53 ->55, backed up. All earlier skeleton files unchanged.')
