#!/usr/bin/env python3
"""
Enhanced Synthetic Data Generator v2  Bayesian hierarchical model with realistic noise.
Generates synthetic scores that mimic real LLM judge behavior patterns including:
- Individual bias effects (position, verbosity, sentiment)
- Interaction effects (compound, additive, or cancelling)
- Model-specific bias profiles
- Heteroscedastic noise (variance differs by condition)
- Score rounding to 1-5 integer scale
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
import json, csv, os, random

random.seed(42)
np.random.seed(42)

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"
DATA_DIR = BASE_DIR / "data"

class BiasDataGenerator:
    """Generate synthetic evaluation data with controlled bias patterns."""

    def __init__(self, n_items=400, n_judges=5, n_repeats=3):
        self.n_items = n_items
        self.n_judges = n_judges
        self.n_repeats = n_repeats

        # Judge models with calibrated bias profiles (based on literature)
        self.judge_profiles = {
            "claude": {
                "baseline_score": 3.50,
                "position_bias": 0.12,     # prefers first position
                "verbosity_long_bias": -0.08,  # Claude prefers concise (unique!)
                "verbosity_short_bias": 0.02,
                "sentiment_pos_bias": 0.05,
                "sentiment_neg_bias": -0.10,
                "interaction_strength": 0.25,  # strong compounding
                "noise_scale": 0.15,
                "rounding_bias": 0.0,
            },
            "gpt4o": {
                "baseline_score": 3.48,
                "position_bias": 0.08,
                "verbosity_long_bias": 0.04,   # GPT-4o roughly length-neutral
                "verbosity_short_bias": -0.03,
                "sentiment_pos_bias": 0.08,
                "sentiment_neg_bias": -0.12,
                "interaction_strength": 0.20,
                "noise_scale": 0.12,
                "rounding_bias": 0.0,
            },
            "gemini": {
                "baseline_score": 3.52,
                "position_bias": 0.16,     # strong position bias
                "verbosity_long_bias": 0.15,   # prefers longer
                "verbosity_short_bias": -0.10,
                "sentiment_pos_bias": 0.15,
                "sentiment_neg_bias": -0.20,
                "interaction_strength": 0.05,   # weak interaction (near additive)
                "noise_scale": 0.20,
                "rounding_bias": 0.05,
            },
            "deepseek": {
                "baseline_score": 3.49,
                "position_bias": 0.02,     # low position bias
                "verbosity_long_bias": 0.10,
                "verbosity_short_bias": -0.05,
                "sentiment_pos_bias": 0.06,
                "sentiment_neg_bias": -0.08,
                "interaction_strength": 0.12,
                "noise_scale": 0.18,
                "rounding_bias": 0.0,
            },
            "llama": {
                "baseline_score": 3.51,
                "position_bias": 0.20,     # strongest position bias
                "verbosity_long_bias": 0.22,   # strongest length preference
                "verbosity_short_bias": -0.18,
                "sentiment_pos_bias": 0.10,
                "sentiment_neg_bias": -0.15,
                "interaction_strength": 0.18,
                "noise_scale": 0.25,       # noisiest judge
                "rounding_bias": 0.02,
            },
        }

        # Conditions in full factorial design (simplified to 8 key conditions)
        self.conditions = [
            {"name": "baseline",       "position": "first",  "length": "normal",  "sentiment": "neutral",  "pos_offset": 0,   "len_offset": 0,   "sent_offset": 0},
            {"name": "short_response", "position": "first",  "length": "short",   "sentiment": "neutral",  "pos_offset": 0,   "len_offset": -1,  "sent_offset": 0},
            {"name": "verbose_response","position": "first", "length": "long",    "sentiment": "neutral",  "pos_offset": 0,   "len_offset": 1,   "sent_offset": 0},
            {"name": "positive_tone",   "position": "first",  "length": "normal",  "sentiment": "positive", "pos_offset": 0,   "len_offset": 0,   "sent_offset": 1},
            {"name": "negative_tone",   "position": "first",  "length": "normal",  "sentiment": "negative", "pos_offset": 0,   "len_offset": 0,   "sent_offset": -1},
            {"name": "disfavored_pos",  "position": "second", "length": "normal",  "sentiment": "neutral",  "pos_offset": -1,  "len_offset": 0,   "sent_offset": 0},
            {"name": "worst_case",      "position": "second", "length": "short",   "sentiment": "negative", "pos_offset": -1,  "len_offset": -1,  "sent_offset": -1},
            {"name": "best_case_biased","position": "second", "length": "long",    "sentiment": "positive", "pos_offset": -1,  "len_offset": 1,   "sent_offset": 1},
        ]

    def generate_score(self, judge, condition, item_quality=None):
        """
        Generate a single score using a hierarchical model with:
        - Main effects (position, length, sentiment)
        - Interaction effects (position × length, position × sentiment, length × sentiment)
        - Three-way interaction (position × length × sentiment)
        - Per-item quality variation
        - Heteroscedastic noise
        """
        profile = self.judge_profiles[judge]

        # Base score with per-item quality variation
        if item_quality is None:
            item_quality = np.random.normal(0, 0.15)  # N(0, 0.15) quality distribution
        base = profile["baseline_score"] + item_quality

        # Clip base to 1-5
        base = max(1.5, min(4.5, base))

        # Main effects
        pos_effect = condition["pos_offset"] * profile["position_bias"]
        len_effect = condition["len_offset"] * (
            profile["verbosity_long_bias"] if condition["len_offset"] > 0
            else profile["verbosity_short_bias"]
        )
        sent_effect = condition["sent_offset"] * (
            profile["sentiment_pos_bias"] if condition["sent_offset"] > 0
            else profile["sentiment_neg_bias"]
        )

        # Two-way interactions (position × length)
        pxv_interaction = (
            condition["pos_offset"] * condition["len_offset"]
            * profile["interaction_strength"] * 0.08
        )
        # Two-way interactions (position × sentiment)
        pxs_interaction = (
            condition["pos_offset"] * condition["sent_offset"]
            * profile["interaction_strength"] * 0.04
        )
        # Two-way interactions (length × sentiment)
        vxs_interaction = (
            condition["len_offset"] * condition["sent_offset"]
            * profile["interaction_strength"] * 0.03
        )

        # Three-way interaction
        pxsxv_interaction = (
            condition["pos_offset"] * condition["len_offset"] * condition["sent_offset"]
            * profile["interaction_strength"] * 0.02
        )

        # Noise (heteroscedastic  more noise for extreme conditions)
        base_noise = profile["noise_scale"]
        condition_noise_mult = 1.0 + 0.3 * (
            abs(condition["pos_offset"]) + abs(condition["len_offset"]) + abs(condition["sent_offset"])
        ) / 3.0
        noise = np.random.normal(0, base_noise * condition_noise_mult)

        # Compute raw score
        raw = base + pos_effect + len_effect + sent_effect + \
              pxv_interaction + pxs_interaction + vxs_interaction + \
              pxsxv_interaction + noise + profile["rounding_bias"]

        # Round to discretized 0.5-step score, clip to [1, 5]
        score = max(1.0, min(5.0, raw))
        # Round to nearest 0.5, then to nearest integer for final score
        score = round(score * 2) / 2  # half-integer
        score = max(1, min(5, int(round(score))))

        return score, {
            "raw": raw,
            "base": base,
            "pos_effect": pos_effect,
            "len_effect": len_effect,
            "sent_effect": sent_effect,
            "pxv_interaction": pxv_interaction,
            "pxs_interaction": pxs_interaction,
            "vxs_interaction": vxs_interaction,
            "pxsvx_interaction": pxsxv_interaction,
            "noise": noise,
            "item_quality": item_quality,
        }

    def generate_dataset(self):
        """Generate complete dataset for all judges and conditions."""
        records = []
        judge_names = list(self.judge_profiles.keys())

        # Pre-generate item quality for reproducibility
        item_qualities = {i: np.random.normal(0, 0.15) for i in range(self.n_items)}

        for judge in judge_names:
            for item_id in range(self.n_items):
                item_quality = item_qualities[item_id]
                for cond in self.conditions:
                    for repeat in range(self.n_repeats):
                        score, details = self.generate_score(
                            judge, cond, item_quality
                        )
                        records.append({
                            "judge": judge,
                            "item_id": item_id,
                            "condition": cond["name"],
                            "position": cond["position"],
                            "length": cond["length"],
                            "sentiment": cond["sentiment"],
                            "score": score,
                            "repeat_num": repeat,
                            "raw_score": round(details["raw"], 4),
                            "item_quality": round(details["item_quality"], 4),
                        })

        return pd.DataFrame(records)

    def compute_ground_truth_interaction_ratio(self, judge):
        """Compute the TRUE (noise-free) interaction ratio for a judge."""
        profile = self.judge_profiles[judge]

        # Noise-free main effects
        pos_effect = abs(profile["position_bias"])
        verb_long_effect = abs(profile["verbosity_long_bias"])
        verb_short_effect = abs(profile["verbosity_short_bias"])
        max_verb_effect = max(verb_long_effect, verb_short_effect)

        # Noise-free combined effect for worst case
        worst_combined = (
            abs(profile["position_bias"]) +
            abs(profile["verbosity_short_bias"]) +
            abs(profile["sentiment_neg_bias"]) +
            profile["interaction_strength"] * 0.08 * 1 +    # pxv
            profile["interaction_strength"] * 0.04 * 1 +    # pxs  
            profile["interaction_strength"] * 0.03 * 1 +    # vxs
            profile["interaction_strength"] * 0.02 * (-1)   # pxsxv (negative for worst case)
        )

        sum_individual = pos_effect + abs(profile["verbosity_short_bias"]) + abs(profile["sentiment_neg_bias"])

        if sum_individual > 0:
            ir = worst_combined / sum_individual
        else:
            ir = 1.0

        return ir

    def generate_analysis_ready_data(self):
        """Generate and save the complete dataset + analysis."""
        df = self.generate_dataset()
        os.makedirs(RESULTS_DIR, exist_ok=True)

        # Save to CSV
        csv_path = RESULTS_DIR / "bias_interaction_synthetic_v2.csv"
        df.to_csv(csv_path, index=False)

        # Compute ground-truth interaction ratios
        ground_truth = {}
        for judge in self.judge_profiles:
            ir = self.compute_ground_truth_interaction_ratio(judge)
            ground_truth[judge] = round(ir, 3)

        # Compute empirical statistics
        empirical = {}
        for judge in self.judge_profiles:
            jd = df[df["judge"] == judge]
            conditions = jd.groupby("condition")["score"].agg(["mean", "std", "count"])

            empirical[judge] = {
                "n": len(jd),
                "overall_mean": float(jd["score"].mean()),
                "overall_std": float(jd["score"].std()),
                "baseline_mean": float(conditions.loc["baseline", "mean"]) if "baseline" in conditions.index else None,
                "worst_mean": float(conditions.loc["worst_case", "mean"]) if "worst_case" in conditions.index else None,
                "conditions": {k: {"mean": round(v["mean"], 3), "std": round(v["std"], 3)}
                              for k, v in conditions.iterrows()},
            }

        # Compute empirical interaction ratios
        for judge in self.judge_profiles:
            jd = df[df["judge"] == judge]
            # Position bias
            pos_first = jd[(jd["position"]=="first") & (jd["length"]=="normal") & (jd["sentiment"]=="neutral")]["score"].mean()
            pos_second = jd[(jd["position"]=="second") & (jd["length"]=="normal") & (jd["sentiment"]=="neutral")]["score"].mean()
            pos_bias = abs(pos_first - pos_second)

            # Verbosity bias (long)
            verb_long = jd[(jd["length"]=="long") & (jd["position"]=="first") & (jd["sentiment"]=="neutral")]["score"].mean()
            verb_normal = jd[(jd["length"]=="normal") & (jd["position"]=="first") & (jd["sentiment"]=="neutral")]["score"].mean()
            verb_bias = abs(verb_long - verb_normal)

            # Combined (worst case  disfavored_position + short + negative effects together)
            # The worst case condition name is "worst_case"  position second + short length + negative sentiment
            baseline = jd[jd["condition"]=="baseline"]["score"].mean()
            # Compute expected additive from individual bias effects  
            worst = jd[jd["condition"]=="worst_case"]["score"].mean()
            combined_effect = baseline - worst

            # Interaction ratio
            sum_ind = pos_bias + verb_bias
            if sum_ind > 0:
                empirical_ir = combined_effect / sum_ind
            else:
                empirical_ir = 1.0

            empirical[judge]["ground_truth_ir"] = ground_truth[judge]
            empirical[judge]["empirical_ir"] = round(empirical_ir, 3)
            empirical[judge]["position_bias"] = round(pos_bias, 3)
            empirical[judge]["verbosity_bias"] = round(verb_bias, 3)
            empirical[judge]["combined_effect"] = round(combined_effect, 3)

        # Save metadata
        meta = {
            "generator": "Enhanced Synthetic Data Generator v2",
            "n_items": self.n_items,
            "n_judges": self.n_judges,
            "n_repeats": self.n_repeats,
            "n_conditions": len(self.conditions),
            "total_rows": len(df),
            "judge_profiles": self.judge_profiles,
            "ground_truth_interaction_ratios": ground_truth,
            "empirical": empirical,
        }

        meta_path = RESULTS_DIR / "synthetic_v2_metadata.json"
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)

        # Print summary
        print("="*70)
        print("ENHANCED SYNTHETIC DATA GENERATOR v2  SUMMARY")
        print("="*70)
        print(f"Generated {len(df):,} data points ({n_items} items × {n_judges} judges × {len(self.conditions)} conditions × {n_repeats} repeats)")
        print(f"\nGround Truth vs Empirical Interaction Ratios:")
        print(f"{'Judge':<12} {'True IR':<10} {'Empirical IR':<15} {'Pattern':<15}")
        print("-"*52)
        for judge in self.judge_profiles:
            gt = ground_truth[judge]
            emp = empirical[judge]["empirical_ir"]
            pattern = "compounding" if emp > 1.05 else ("cancelling" if emp < 0.95 else "additive")
            print(f"{judge:<12} {gt:<10.3f} {emp:<15.3f} {pattern:<15}")

        print(f"\nFiles saved:")
        print(f"  Data: {csv_path}")
        print(f"  Meta: {meta_path}")

        return df, meta

if __name__ == "__main__":
    n_items = 400
    n_judges = 5
    n_repeats = 3

    gen = BiasDataGenerator(n_items, n_judges, n_repeats)
    df, meta = gen.generate_analysis_ready_data()

    # Also save a compact version for quick loading
    compact = df[["judge", "item_id", "condition", "score"]]
    compact_path = RESULTS_DIR / "bias_interaction_synthetic.csv"
    compact.to_csv(compact_path, index=False)
    print(f"\nCompact version: {compact_path} ({len(compact):,} rows)")
