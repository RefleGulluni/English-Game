from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,re,subprocess,sys,numpy as np
R=Path('/Users/mac/Documents/GitHub.nosync/English-Game');S=R/'art/character_design/enemies/skeleton';W=Path('/tmp/english-game-skeleton-batch2-20261026');O=W/'staged';A=S/'anim';Q=O/'qc';protected=json.loads((W/'protected.json').read_text());assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protected.items());newtim=json.loads((O/'timing.json').read_text());oldtim=json.loads((A/'timing.json').read_text());assert all(newtim['animations'][k]==v for k,v in oldtim['animations'].items());assert len(newtim['animations'])==15
# Supplemental native-scale/style row beside B1, using only existing art composites.
items=[('B1',Image.open(R/'art/character_design/hero_B1_front_straight.png').convert('RGBA')),('B front',Image.open(S/'skeleton_B.png').convert('RGBA')),('walk front3',Image.open(O/'frames/skeleton_B_walk_front/03.png').convert('RGBA')),('B back',Image.open(S/'skeleton_B_back.png').convert('RGBA')),('walk back3',Image.open(O/'frames/skeleton_B_walk_back/03.png').convert('RGBA')),('B left',Image.open(S/'skeleton_B_left.png').convert('RGBA')),('walk left3',Image.open(O/'frames/skeleton_B_walk_left/03.png').convert('RGBA')),('headless8',Image.open(O/'frames/skeleton_B_reassemble_front/08.png').convert('RGBA')),('restored12',Image.open(O/'frames/skeleton_B_reassemble_front/12.png').convert('RGBA'))]
board=Image.new('RGBA',(len(items)*108,140),'#403D3F');d=ImageDraw.Draw(board)
for i,(label,im) in enumerate(items):board.alpha_composite(im,(i*108+6,15));d.text((i*108+6,117),label,fill='#C8BFAF')
board.save(Q/'skeleton_B_batch2_vs_hero_1x.png');board.resize((board.width*6,board.height*6),Image.Resampling.NEAREST).save(Q/'skeleton_B_batch2_vs_hero_6x.png')
# Production code is provenance, not gameplay logic.
pd=Q/'batch2_sources/production';pd.mkdir(exist_ok=True)
for name in ['recover.py','build.py','qc.py','write_qa.py','publish.py','protected.json']:
 shutil.copy2(W/name,pd/name)
(pd/'README.md').write_text('Built-in image_gen supplies the whole walking/reassembly poses. Native editors preserve original pixels for the small idle/hit/remains motions, exact endpoints, heads and feet. Source grid center points are audited in metrics. Scripts retain historical work directory /tmp/english-game-skeleton-batch2-20261026; recoverable archive ~/.Trash/english-game-skeleton-batch2-working-20261026. Adapt paths and use a NEW staging directory to reproduce. Publisher intentionally refuses overwrite except the backed-up timing table.\n')
# The only preexisting file allowed to change is the timing table; backup first.
bk=A/'qc/backups/before_batch2_20261026';bk.mkdir(parents=True,exist_ok=False);shutil.copy2(A/'timing.json',bk/'timing.json')
for p in O.rglob('*'):
 if not p.is_file():continue
 dest=A/p.relative_to(O)
 if dest==A/'timing.json':
  assert hashlib.sha256(dest.read_bytes()).hexdigest()==protected[str(dest)]
 else:assert not dest.exists(),str(dest)
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
# Checker against ACTUAL final file paths, not a staging-only log.
paths=sorted(p for p in A.glob('skeleton_B_*.png') if str(p) not in protected)
z=subprocess.run([sys.executable,str(R/'scripts/tools/pixel_check.py'),'--hero',str(S/'skeleton_B.png'),*[str(p) for p in paths]],capture_output=True,text=True);assert z.returncode==0;(A/'qc/skeleton_B_anim_batch2_pixel_check.txt').write_text(z.stdout)
# Integrity and integration checks on final artifacts.
changed=[p for p,h in protected.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h];assert changed==[str(A/'timing.json')],changed
assert hashlib.sha256((bk/'timing.json').read_bytes()).hexdigest()==protected[str(A/'timing.json')]
assert json.loads((A/'timing.json').read_text())==newtim
for name,t in newtim['animations'].items():
 im=Image.open(A/t['sprite_sheet']);assert im.size==(96*t['frames'],96);assert len(t['durations_ms'])==t['frames']
for first,last in [(A/'frames/skeleton_B_reassemble_front/01.png',A/'frames/skeleton_B_collapse_front/09.png'),(A/'frames/skeleton_B_reassemble_front/12.png',A/'frames/skeleton_B_idle_front/01.png'),(A/'frames/skeleton_B_remains_idle/01.png',A/'frames/skeleton_B_reassemble_front/01.png')]:assert Image.open(first).convert('RGBA').tobytes()==Image.open(last).convert('RGBA').tobytes()
# Walk-left never reuses a mirrored approved right frame.
right=Image.open(A/'skeleton_B_walk_right.png').convert('RGBA');left=Image.open(A/'skeleton_B_walk_left.png').convert('RGBA');assert all(not np.array_equal(np.array(left.crop((96*k,0,96*(k+1),96))),np.array(right.crop((96*k,0,96*(k+1),96)))[:,::-1]) for k in range(8))
for q in [A/'qc/skeleton_B_anim_batch2_QA.md',A/'qc/skeleton_B_anim_index.md']:
 missing=[p for p in re.findall(r'\]\(([^)]+)\)',q.read_text()) if not (q.parent/p).exists()];assert not missing,missing
proof={'protected_original_files':len(protected),'unchanged_original_files':len(protected)-1,'only_changed_file':'anim/timing.json','timing_backup':'qc/backups/before_batch2_20261026/timing.json','old_animation_entries_identical':True,'new_actions':13,'new_frames':68,'total_actions_with_trial':15,'integration_endpoints_rgba_exact':True,'left_is_not_mirrored_right':True,'all_QA_links_resolve':True,'accepted_trial_png_gif_frame_and_QA_hashes_unchanged':True};(A/'qc/skeleton_B_anim_batch2_verification.json').write_text(json.dumps(proof,indent=2));print(z.stdout);print(json.dumps(proof))
