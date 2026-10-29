from pathlib import Path
from PIL import Image
import json,hashlib,shutil,numpy as np
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');D=R/'art/character_design/lexicon';W=Path('/tmp/english-lexicon-20261029');O=W/'staged';Q=O/'qc';S=Q/'sources';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
qa=(Q/'lexicon_book_QA.md').read_text();qa=qa.replace('翻页只选用两个生成纸叶的原生像素选区，其余书体逐像素复用干净摊开书。只翻一张，右侧抬起、越过中线落向左侧，最后回到干净书。','翻页第2帧选用生成纸叶的原生像素选区，第3帧从同一纸叶取7×103 px原生纸面窄带，放在 (125,13)，表示纸叶完全竖立的边视。其余书体逐像素复用干净摊开书。只翻一张：右侧抬起、竖立、落向左侧，最后回到干净书。').replace('只有4帧翻页，左右纸叶中间姿态能读出单页翻动，但没有额外的“完全竖立”停顿帧。薄纸受光和轮廓的连续感需实际播放判断。','只有4帧翻页，第3帧为7 px宽的边视纸叶，没有在竖立位置另加停顿；从竖立落到左侧用末帧完成，不另加左斜半落帧。薄纸受光和轮廓的连续感需实际播放判断。');(Q/'lexicon_book_QA.md').write_text(qa)
# Refresh archival scripts/records to correspond to the final page-edge pose.
for name in ['build_animation.py','verify_export.py','animation_edits.json']:shutil.copy2(W/name,S/name)
readme=(S/'README.md').read_text().replace('翻页只选用 page_turn_generated.png 的两张移动纸叶','翻页选用 page_turn_generated.png 的右侧抬纸叶，以及该纸叶的7像素原生窄带作为完全竖立帧');(S/'README.md').write_text(readme)
rec=json.loads((S/'clean_edits.json').read_text());rec['closed_sigil_pixels']=522;(S/'clean_edits.json').write_text(json.dumps(rec,indent=2))
# Revisions before final hand-off are still recoverable, and never affect originals outside the new lexicon folder.
files={str(p.relative_to(O)):p for p in O.rglob('*') if p.is_file()};changed=[rel for rel,p in files.items() if (D/rel).exists() and sha(D/rel)!=sha(p)];B=D/'qc/backups/before_vertical_leaf_cleanup_20261029';assert not B.exists()
for rel in changed:
 dest=B/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/rel,dest)
for rel,p in files.items():
 dest=D/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(p)==sha(dest)
# Final protection audit against the pre-task tree.
protected=json.loads((W/'protected.json').read_text());diff=[rel for rel,h in protected.items() if not (R/rel).exists() or sha(R/rel)!=h];assert diff==['art/character_design/anim/timing.json']
old=json.loads((W/'timing_original.json').read_text());new=json.loads((R/'art/character_design/anim/timing.json').read_text());assert len(new['animations'])==len(old['animations'])+3
for k,v in old.items():
 if k=='animations':
  for name,item in v.items():assert new[k][name]==item
 else:assert new[k]==v
for n in ['lexicon_tip_up','lexicon_covers_fall','lexicon_page_turn']:
 t=new['animations'][n];a=np.array(Image.open(D/(n+'.png')).convert('RGBA'));assert a.shape==(128,256*t['frames'],4)
 for k in range(t['frames']):assert np.array_equal(a[:,k*256:(k+1)*256],np.array(Image.open(D/'frames'/n/f'{k+1:02}.png').convert('RGBA')))
for n,count in [('lexicon_opening',9),('lexicon_page_turn',4)]:
 g=Image.open(D/'qc'/f'{n}_3x.gif');assert g.n_frames==count
 for k in range(count):g.seek(k);g.load()
P=D/'qc/lexicon_preservation.json';report=json.loads(P.read_text());backup=B/'qc/lexicon_preservation.json';backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P,backup);report['published_files']={rel:sha(D/rel) for rel in files};report['page_turn_vertical_frame_width_px']=7;report['final_audit_passed']=True;P.write_text(json.dumps(report,indent=2)+'\n')
# Keep the final verification procedure beside the sources.
shutil.copy2(W/'finish.py',D/'qc/sources/finish.py')
print(json.dumps({'original_files_checked':len(protected),'only_existing_change':diff,'runtime_pngs':6,'frames':13,'tip_frames':3,'fall_frames':6,'page_frames':4,'final_audit':True},indent=2))
