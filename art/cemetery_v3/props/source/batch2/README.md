# Batch2 production provenance

Built-in image_gen was used; no external CLI image generator. See prompt_set.json and generation.json for prompts, and qc/batch2_sources/<name>/ for the selected full source PNG, exact recovered native cells, recorded grid boundaries and final comparison.

The Python recipes are a historical, inspectable record, not a game dependency. They contain the working directory used during this session. The recoverable working directory (including rejected drafts and boundary recovery files) is archived at `/Users/mac/.Trash/english-game-props-batch2-working-20261025` after delivery. Source images also remain at their tool-generated paths. Set the W constant to a reconstructed scratch directory if replaying; never run publish.py against already accepted assets without a fresh backup.

No native asset was resized, mirrored, rotated or interpolated. Native row/column selections and integer translations are explicitly recorded in finish_records.json and per-object native_edit.json. Only QC/reference enlargements call nearest resize. The closed-world palette is drawn from existing approved cemetery stone and soil RGBs. All source files remain intact.

The manifest backup is outside the repository: `/Users/mac/.codex/backups/English-Game/before-props-batch2-20261025/props_manifest.json`. Existing art hash audit is in qc/batch2_metrics.json.
