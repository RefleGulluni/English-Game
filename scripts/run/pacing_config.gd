extends RefCounted

# Fixed design constraints; all other numbers are provisional QA baselines.
const MIN_MAJOR_GAP := 2
const LEARNING_CAP := 2
const RECOVERY_CAP := 2
const ELITE_CAP := 2
const RISK_WINDOW := 3
const QA := {
	"active_pool_size": 6, "revisit_high_after": 7, "ambient_gain": 4.0,
	"correct_gain": 12.0, "familiarity_decay": 0.5, "decay_after": 8,
	"success_stability": 0.14, "error_stability": 0.18,
	"error_difficulty": 0.16, "success_difficulty": 0.05,
	"learning_repeat": 0.25, "recovery_repeat": 0.2, "elite_repeat": 0.2,
	"recovery_base": 7.0, "elite_base": 5.0, "mystery_base": 5.0,
	"rest_hp": 10, "repair_armor": 6, "calm_corruption": 15,
	"prepare_hp": 3, "prepare_armor": 2, "corrective_reuse_gap": 3,
	"stable_familiarity": 60.0, "stable_confidence": 0.8, "stable_success_streak": 3,
	"familiarity_recognition_below": 25.0, "hint_stability_factor": 0.5,
	"new_min_usefulness": 0.4, "new_max_difficulty": 0.85, "semantic_repeat": 0.65,
	"ratio_min": 0.25, "ratio_max": 0.85, "ratio_per_streak": 0.015, "ratio_adjust_limit": 0.15,
	"revisit_max_bonus": 3.0, "familiarity_priority": 0.4, "pending_priority": 0.5,
	"personal_difficulty_weight": 1.0, "stability_priority": 1.0, "pool_unstable_bonus": 4.0,
	"hp_pressure": 2.0, "armor_pressure": 0.7, "corruption_pressure": 1.0,
	"risk_pressure": 0.3, "elite_pressure": 0.5, "safety_cap": 4.0,
	"recovery_safety_base": 0.25, "content_repetition": 0.15,
	"mode_new": {"Adaptive": 0.6, "More Discovery": 0.72, "Balanced": 0.6, "More Review": 0.42},
}
