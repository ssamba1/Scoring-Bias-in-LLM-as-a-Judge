"""Prose-consistency gate: assert the key numbers quoted in the paper's prose
(macros.tex + scoring_bias_v2.tex) equal the values in the derived result files.

The numbers-match CI verifies raw -> derived JSON. This closes the second gap:
derived JSON -> prose. Every assertion failure names the stale claim.
Exit code 1 on any mismatch.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent

mech = json.loads((HERE / "results_mechanism.json").read_text())
rob = json.loads((HERE / "results_robustness.json").read_text())
stages = json.loads((HERE / "results_stages_analysis.json").read_text())
macros = (PAPER / "macros.tex").read_text(encoding="utf-8")
tex = (PAPER / "scoring_bias_v2.tex").read_text(encoding="utf-8")
text = macros + tex

FAILS = []


def check(desc, claim_in_text, actual, fmt=lambda x: x):
    shown = fmt(actual)
    if claim_in_text not in text:
        FAILS.append(f"{desc}: prose does not contain '{claim_in_text}' (data says {shown})")


def close(desc, quoted, actual, tol=0.006):
    if actual is None or abs(quoted - actual) > tol:
        FAILS.append(f"{desc}: prose says {quoted}, data says {actual}")


# ---- mechanism ----
close("pooled entropy-bias rho", -0.41, mech["entropy_bias_link"]["spearman_rho"], 0.006)
close("sqrtvar-bias rho", -0.25, mech["var_bias_link"]["spearman_rho"], 0.006)
close("LOO R2", 0.27, mech["predictor"]["loo_r2"], 0.006)
close("size-partial rho", -0.38, mech["size_confound_control"]["partial_rank_rho_given_log10_params"], 0.006)
close("size-bias rho", 0.18, mech["size_confound_control"]["size_bias_spearman_rho"], 0.006)
close("mixed-effects coef", 0.16, mech["lmm"]["instruct_coef"], 0.006)
mit = mech["mitigation"]
close("mitigation expected", 1.09, mit["expected"], 0.006)
close("mitigation argmax", 1.88, mit["argmax"], 0.006)
close("mitigation marginalized", 0.45, mit["marginalized"], 0.006)
red = 1 - mit["marginalized"] / mit["expected"]
check("59% reduction", "59\\%", round(red * 100))
if not (58.5 <= red * 100 < 59.5):
    FAILS.append(f"59% claim: data gives {red*100:.1f}%")

# ---- robustness ----
close("exact permutation p", 0.00098, rob["F1_exact_permutation"]["exact_p_two_sided"], 0.00005)
close("headline mean effect", 0.257, rob["B3_sensitivity"]["full_mean_effect"], 0.006)
if rob["B3_sensitivity"]["excl_qwen_positive"] != "8/9":
    FAILS.append("excl-Qwen 8/9 stale")
close("EV/flip concordance", 0.56, rob["B4_readout_concordance"]["spearman_evbias_fliprate"], 0.006)
close("within-checkpoint entropy", -0.05, rob["B1_within_checkpoint"]["mean_within_rho"], 0.006)
close("within-checkpoint responsiveness", 0.64,
      rob["B1_within_checkpoint_responsiveness"]["mean_within_rho"], 0.006)
close("LMM entropy coef", -0.46, rob["B1_lmm"]["entropy_coef"], 0.006)
r2ci = rob["B2_predictor_bootstrap"]["r2_ci95"]
close("R2 CI low", -0.62, r2ci[0], 0.02)
close("R2 CI high", 0.57, r2ci[1], 0.02)
close("split-half SB", 0.99, rob["F4_split_half"]["spearman_brown"], 0.006)
close("bound tightness", 0.45, rob["F5_bound_tightness"]["mean_gradnorm_over_sqrtvar"], 0.006)
close("crossover sign acc", 0.75, rob["D3_crossover"]["sign_accuracy"], 0.006)
close("crossover magnitude rho", 0.64, rob["D3_crossover"]["spearman_dlogpred_dlogact"], 0.006)
vdec = rob["E_variance_decomposition"]
close("anatomy interaction", 0.37, vdec.get("family:probe"), 0.006)
close("anatomy probe", 0.24, vdec.get("probe"), 0.006)
close("item-consistency null", 0.01, rob["E2_item_consistency"]["mean_cross_judge_item_corr"], 0.006)
c5 = rob["C5_public_items"]
close("dolly rho", -0.44, c5["entropy_bias_rho"], 0.006)
close("dolly mean effect", 0.13, c5["mean_effect"], 0.006)
if c5["families_positive"] != "7/8":
    FAILS.append("dolly 7/8 stale")
c8 = rob["C8_template_ensemble"]
close("template-ensemble reduction", 0.22, c8["reduction_frac"], 0.006)
g1 = rob["G1_variant_decomposition"]
close("verbosity padded share", 0.99, g1["verbosity"]["verbose"], 0.006)
close("authority novice share", 0.67, g1["authority"]["novice"], 0.006)
g2 = rob["G2_cross_dataset"]["_combined"]
close("cross-dataset weighted mean", 0.23, g2["weighted_mean_effect"], 0.006)

# ---- P10 new probes ----
p2path = HERE / "results_probes2_analysis.json"
if p2path.exists():
    p2 = json.loads(p2path.read_text())["per_probe"]
    close("sycophancy change", 0.46, p2["sycophancy"]["mean_change"], 0.006)
    close("sycophancy instruct level", 1.37, p2["sycophancy"]["mean_instruct"], 0.006)
    if p2["sycophancy"]["families_positive"] != "11/13":
        FAILS.append("sycophancy 11/13 stale")
    close("anchoring null", 0.015, p2["anchoring"]["mean_change"], 0.003)

# ---- P11 Chinese replication ----
zpath = HERE / "results_zh_analysis.json"
if zpath.exists():
    z = json.loads(zpath.read_text())
    zeff = z["per_family_effect"]
    mean_z = sum(zeff.values()) / len(zeff)
    close("zh mean effect", 0.43, mean_z, 0.006)
    if sum(v > 0 for v in zeff.values()) != 4:
        FAILS.append("zh 4/4 stale")
    close("zh entropy-bias rho", -0.36, z["entropy_bias_link"]["spearman_rho"], 0.006)

# ---- P14 dose-response (failed) ----
dp = HERE / "results_dose_analysis.json"
if dp.exists():
    d14 = json.loads(dp.read_text())
    close("dose monotonic null", 0.06, d14["P14a_monotonic"]["mean_dose_spearman"], 0.006)
    if d14["P14b_slope"]["instruct_steeper"] != "3/8":
        FAILS.append("P14b 3/8 stale")

# ---- P13 span patching ----
sp = HERE / "spanpatch_analysis.json"
if sp.exists():
    s13 = json.loads(sp.read_text())["probes"]
    auth = s13["authority_expert"]
    if not auth["p13_met"]:
        FAILS.append("P13 authority confirmed claim stale")
    band = auth["layers_with_reduction_ge_50pct"]
    if not (band and band[0] == 3 and band[-1] == 14):
        FAILS.append(f"span-patch layer band 3-14 stale: {band}")
    ref = s13["reference_good"]
    if ref["max_reduction"] > 0.10:
        FAILS.append(f"reference span-patch null stale: max {ref['max_reduction']}")

# ---- stages ----
if stages["P7"]["sft_resp_up_cells"] != "10/10":
    FAILS.append("P7 10/10 stale")
shares = stages["P7"]["sft_share_of_total_rise"]
if not (0.83 <= shares[0] <= 0.85 and 0.98 <= shares[1] <= 1.0):
    FAILS.append(f"84%/99% SFT-share stale: {shares}")
lel = stages.get("ladder_entropy_bias_link", {})
close("ladder entropy-bias null", 0.01, lel.get("spearman_rho"), 0.006)
if stages["P9"]["sign_agreement"] != "7/8":
    FAILS.append("P9 7/8 stale")

if FAILS:
    print("PROSE-CONSISTENCY FAILURES:")
    for f in FAILS:
        print(" -", f)
    sys.exit(1)
print(f"prose-consistency OK ({len(FAILS)} failures)")
