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

# ---- P17 granularity (confirmed) ----
gp = HERE / "results_gran_analysis.json"
if gp.exists():
    g17 = json.loads(gp.read_text())
    for kind in ("base", "instruct"):
        if not g17["P17a_growth"][kind]["monotone_increasing"]:
            FAILS.append(f"P17a {kind} monotone claim stale")
    if not all(g17["P17b_instruct_gt_base"].values()):
        FAILS.append("P17b instruct>base at every K stale")
    close("gran K10 instruct", 0.664, g17["per_scale"]["K10"]["mean_bias_instruct"], 0.006)

# ---- P19 chat-template control ----
cpth = HERE / "results_chat_analysis.json"
if cpth.exists():
    c19 = json.loads(cpth.read_text())
    close("chat mean delta", 0.38, c19["P19a"]["mean_chat_delta"], 0.006)
    if c19["P19a"]["chat_ge_raw_cells"] != "4/6":
        FAILS.append("chat 4/6 stale")
    close("chat raw corr", 0.49, c19["P19b"]["raw_chat_spearman"], 0.006)
    close("chat minus base", 0.07, c19["P19c"]["mean_chat_minus_base"], 0.006)

# ---- P16 sampled readout (failed; corrects confound framing) ----
sp16 = HERE / "results_sampled_analysis.json"
if sp16.exists():
    s16 = json.loads(sp16.read_text())
    close("sampled parse base", 0.80, s16["P16a_parse_rate"]["base"], 0.006)
    close("sampled parse instruct", 0.83, s16["P16a_parse_rate"]["instruct"], 0.006)
    close("sampled ev disagreement", -0.20,
          s16["P16b_delta_agreement"]["spearman_ev_vs_sampled_delta"], 0.006)

# ---- P15 ten templates (split) ----
tp = HERE / "results_t10_analysis.json"
if tp.exists():
    t15 = json.loads(tp.read_text())
    close("t10 entropy-bias", -0.51, t15["P15a_entropy_bias"]["spearman_rho"], 0.006)
    if t15["P15b_summary"] != "6/10 templates with instruct>base":
        FAILS.append("P15b 6/10 stale")

# ---- P18 readout variants (confirmed) ----
tv = HERE / "results_tokvar_analysis.json"
if tv.exists():
    t18 = json.loads(tv.read_text())
    close("tokvar bare~space corr", 0.79,
          t18["P18a_pairwise_delta_corr"]["bare~space_appended"], 0.006)
    if t18["P18b_union_effect"]["families_positive"] != "4/4":
        FAILS.append("P18b 4/4 stale")
    close("tokvar space mass instruct", 0.955,
          t18["mean_mass"]["space_appended"]["instruct"], 0.006)
    close("tokvar space effect", 0.06,
          t18["P18c_effect_by_readout"]["space_appended"]["mean_effect"], 0.006)

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

# ---- P20 frontier judges ----
fp = HERE / "results_closed_analysis.json"
if fp.exists():
    f20 = json.loads(fp.read_text())
    if not f20["P20a"]["all_judges_ge_half_probes"]:
        FAILS.append("P20a stale")
    close("frontier pooled rho", -0.45, f20["pooled"]["pooled_rho"], 0.006)
    close("frontier mean delta", 0.89, f20["P20c"]["frontier_mean_delta"], 0.006)
    close("frontier mean entropy", 0.64, f20["pooled"]["frontier_mean_entropy"], 0.006)
    if f20["P20c"]["frontier_below_open"]:
        FAILS.append("P20c framing stale (frontier now below open?)")

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

# ---- headline statistics quoted in the abstract-level macros ----
#
# These were the gap. Everything above verifies structural claims -- fractions,
# monotonicity flags, sign agreement -- against the derived JSON, and does it
# well. The continuous statistics the paper actually leads with were unchecked:
# changing the headline correlation in macros.tex from -0.41 to -9.41 left this
# script reporting "prose-consistency OK".
#
# Each is pinned to the specific key that produces it, not to "some value
# somewhere". That distinction matters here: sixteen different derived values
# round to 0.41, so a search of the whole result set would have accepted the
# mutated number too.
link = mech["entropy_bias_link"]
close("entropy-bias rho (headline)", -0.41, link["spearman_rho"], 0.006)
check("entropy-bias rho in prose", r"\rho=-0.41", link["spearman_rho"])
if not link["spearman_p"] < 1e-3:
    FAILS.append(f"headline rho p is {link['spearman_p']}, prose claims p<10^-3")

# "Entropy" denotes two different quantities in this analysis -- the control
# variant for the decisiveness shift, the mean over a probe's variants for the
# link. Recomputing the link from raw scores under the reader's likely reading
# gives -0.34, not -0.41, so the paper now names which one it means and quotes
# both. Pin both, and pin that they still differ: if they ever coincide, one of
# the two definitions has silently stopped being computed.
ctrl_link = mech["entropy_bias_link_control_only"]
close("entropy-bias rho (control-variant reading)", -0.34, ctrl_link["spearman_rho"], 0.006)
check("control-variant rho in prose", r"\rho=-0.34", ctrl_link["spearman_rho"])
if not ctrl_link["spearman_p"] < 1e-4:
    FAILS.append(f"control-variant rho p is {ctrl_link['spearman_p']}, prose claims p<10^-4")
if abs(ctrl_link["spearman_rho"] - link["spearman_rho"]) < 1e-9:
    FAILS.append("the two entropy definitions give identical rho; one is not being computed")
if "mean over a probe's variants" not in text:
    FAILS.append("the paper no longer says which entropy the headline link uses")

var_link = mech["var_bias_link"]
close("variance-term rho", -0.25, var_link["spearman_rho"], 0.006)
check("variance-term rho in prose", r"\rho=-0.25", var_link["spearman_rho"])

dec = mech["decisiveness"]
close("entropy base mean", 2.04, dec["base_mean"], 0.006)
close("entropy instruct mean", 1.45, dec["instruct_mean"], 0.006)
check("entropy shift in prose", "2.04", dec["base_mean"])
check("entropy shift in prose", "1.45", dec["instruct_mean"])
if f"{dec['n_decreased']}/{dec['n']}" != "11/13":
    FAILS.append(
        f"decisiveness families is {dec['n_decreased']}/{dec['n']}, prose says 11/13"
    )

resp = mech["responsiveness_bias_link"]
close("responsiveness-bias rho", 0.82, resp["spearman_rho"], 0.006)

# The responsiveness claim is a *count* of families, not only a correlation:
# "12/13 families". The analysis records how many decreased, so the count the
# prose states must be the complement.
resp_fam = mech["responsiveness"]
rose = resp_fam["n"] - resp_fam["n_decreased"]
if f"{rose}/{resp_fam['n']}" != "12/13":
    FAILS.append(
        f"responsiveness rose in {rose}/{resp_fam['n']} families, prose says 12/13"
    )

# The predictor sentence quotes a rank correlation. It previously quoted the
# *Pearson* p-value beside it (0.004 rather than 0.002) -- the coefficient and
# the p-value came from two different tests, and neither the analysis nor this
# checker emitted the rank p at all, so nothing could notice. Both are pinned
# now, each to its own statistic.
pred = mech["predictor"]
close("predictor rank rho", 0.58, pred["loo_spearman_rho"], 0.006)
check("predictor rank rho in prose", r"\rho=0.58", pred["loo_spearman_rho"])
close("predictor rank p", 0.002, pred["loo_spearman_p"], 0.0006)
check("predictor rank p in prose", "p=0.002", pred["loo_spearman_p"])
close("predictor LOO R^2", 0.27, pred["loo_r2"], 0.006)
if abs(pred["loo_p"] - pred["loo_spearman_p"]) < 1e-9:
    FAILS.append("predictor Pearson and Spearman p are identical; one is not being computed")

# ---- every statement of a figure, not merely one -----------------------------
# `check()` asks whether a value appears somewhere in the paper. Most headline
# figures are stated in two to five places, so drifting one of them leaves the
# others satisfying it -- a mutation drifted the entropy pair, both correlations
# and the predictor statistics, and this file caught none of them.
#
# Worse, several count claims were compared only against a literal written into
# this checker ("12/13", "24/26"). Those verify that the data still says what we
# expect; they never look at the paper, so the prose could say anything at all.
#
# `states()` closes both: it pins how many times the paper makes each claim, so
# a drifted statement changes the count and fails, and it reads the paper's text
# rather than this file's expectations.
def states(desc, literal, expected_count):
    seen = text.count(literal)
    if seen != expected_count:
        FAILS.append(
            f"{desc}: the paper states {literal!r} {seen} time(s), expected "
            f"{expected_count} -- a statement drifted, or one was added without "
            f"updating this pin"
        )


states("entropy before tuning", "2.04", 2)
states("entropy after tuning", "1.45", 2)
states("entropy-bias correlation", r"\rho=-0.41", 5)
states("variance-term correlation", r"\rho=-0.25", 3)
states("decisiveness family count", "11/13", 5)
states("responsiveness family count", "12/13", 1)
states("within-checkpoint checkpoint count", "24/26", 1)
states("predictor rank correlation", r"\rho=0.58", 3)
states("predictor R^2", "R^2=0.27", 2)
states("control-variant correlation", r"\rho=-0.34", 1)

# The rest of the paper's published figures, pinned the same way. Every one of
# these is a number a reader could quote; leaving any of them unpinned means the
# gate covers the claims that happened to get attention rather than the claims
# the paper makes.
# The responsiveness pair is compared against the data, not merely counted.
# It was published as 0.15 -> 0.26 while the mean is 0.1446, which rounds to
# 0.14; states() counted the statement happily because counting a claim is not
# checking it. Every figure pinned only by occurrence has this limitation, and
# the ones that are also derivable are compared numerically as well.
resp_pair = mech["responsiveness"]
close("responsiveness before tuning", 0.14, resp_pair["base_mean"], 0.006)
close("responsiveness after tuning", 0.26, resp_pair["instruct_mean"], 0.006)
check("responsiveness rise in prose", r"0.14\!\to\!0.26", resp_pair["base_mean"])
states("responsiveness rise", r"0.14\!\to\!0.26", 1)
states("responsiveness effect size", "d_z=1.44", 2)
states("responsiveness-bias correlation", r"\rho=+0.82", 2)
states("mixed-model coefficient", "+0.16", 2)
states("mixed-model observations", "n=13{,}000", 2)
states("size-partialled correlation", r"\rho=-0.38", 1)
states("size-bias correlation", r"\rho=+0.18", 1)
states("sub-1B band correlation", r"\rho=-0.51", 2)
states("within-checkpoint responsiveness", r"\rho=+0.64", 2)
states("within-checkpoint entropy", r"\rho=-0.05", 1)
states("readout concordance", r"\rho=0.56", 2)
states("exact permutation p", "0.00098", 1)
states("marginalization mitigation", r"59\%", 3)
states("argmax readout", "1.88", 2)
states("frontier pooled correlation", r"\rho=-0.45", 2)
states("frontier pooled n", "n=145", 3)
states("14B attenuated effect", "+0.06", 3)
states("14B probes positive", "3/5", 1)
states("preregistered-analyzer families", "4/4", 2)
states("SFT stage cells", "10/10", 1)
states("public-item families", "7/8", 2)
states("alt-template families", "8/9", 1)

# Secondary and appendix figures. These carry less weight individually, but they
# are the ones a referee recomputes precisely because nobody is watching them.
states("score-ID flip rates", "0.75$/$0.71", 1)
states("reference-answer flip rise", r"0.22\!\to\!0.38", 1)
states("authority flip rise", r"0.24\!\to\!0.41", 1)
states("frontier rubric-order maximum", "2.02", 1)
states("frontier mean bias", "0.89", 3)
states("open-instruct mean bias", "0.69", 1)
states("cumulant family count", "11/13 families", 4)
states("panel mean effect", "+0.26", 2)
states("predictor R^2 interval", "[-0.62", 1)
states("dose-response cells", "8/16", 1)
states("dose-response slope pairs", "3/8", 1)
states("template direction", "6/10", 1)
states("chat-template cells", "4/6", 1)
states("smallest-family count", "2/4", 2)
states("chat-vs-raw families", "1/3", 1)

# ---- count claims ("8/9 families", "24/26 checkpoints") ----------------------
# Fractions are the easiest claim to leave behind: they are typed as literals,
# they change whenever a family is added or an exclusion is revised, and nothing
# about a stale one looks wrong on the page. Each is pinned to the value the
# analysis emits. Where the analysis stored only a proportion (the within-
# checkpoint counts), the count is reconstructed from it rather than trusted.
b3 = rob["B3_sensitivity"]
for label, quoted, actual in [
    ("families positive (headline)", "11/13",
     f"{b3['n_families_positive']}/{b3['n_families']}"),
    ("families positive excluding Qwen", "8/9", b3["excl_qwen_positive"]),
    ("families positive at >=1B", "9/10", b3["only_ge1B_positive"]),
    ("families positive on public items", "7/8", rob["C5_public_items"]["families_positive"]),
    ("families positive on alt templates", "8/9",
     rob["G2_cross_dataset"]["alt_templates"]["families_positive"]),
    ("decrease cells the decomposition catches", "12/20",
     rob["D3_crossover"]["decrease_cells_caught"]),
]:
    if quoted != actual:
        FAILS.append(f"{label}: data says {actual}, prose says {quoted}")
    elif quoted not in text:
        FAILS.append(f"{label}: prose no longer contains '{quoted}' (data says {actual})")

wcr = rob["B1_within_checkpoint_responsiveness"]
n_pos = round(wcr["frac_positive"] * wcr["n_checkpoints"])
if f"{n_pos}/{wcr['n_checkpoints']}" != "24/26":
    FAILS.append(
        f"responsiveness ranks probes in {n_pos}/{wcr['n_checkpoints']} checkpoints, "
        f"prose says 24/26"
    )
close("within-checkpoint responsiveness rho", 0.64, wcr["mean_within_rho"], 0.006)
close("within-checkpoint entropy rho", -0.05, rob["B1_within_checkpoint"]["mean_within_rho"], 0.006)

if FAILS:
    print("PROSE-CONSISTENCY FAILURES:")
    for f in FAILS:
        print(" -", f)
    sys.exit(1)
print(f"prose-consistency OK ({len(FAILS)} failures)")
