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
    """Compare a quoted value with the data behind it.

    The tolerance is capped at half a unit in the quoted number's last printed
    place. The call sites almost all pass 0.006, which is looser than the 0.005
    that separates two-decimal values: a datum drifting to 0.455 would keep
    passing beside a paper printing 0.45, even though it now rounds to 0.46.
    The cap makes the check mean what it reads as -- the printed digits are the
    right digits -- while an explicitly coarser tolerance still applies where a
    number is quoted deliberately roughly.
    """
    if actual is None:
        FAILS.append(f"{desc}: prose says {quoted}, data says {actual}")
        return
    decimals = len(f"{quoted!r}".split(".")[1]) if "." in f"{quoted!r}" else 0
    if decimals >= 2:
        tol = min(tol, 0.5 * 10 ** -decimals + 1e-9)
    if abs(quoted - actual) > tol:
        FAILS.append(f"{desc}: prose says {quoted}, data says {actual}")


# ---- mechanism ----
close("pooled entropy-bias rho", -0.41, mech["entropy_bias_link"]["spearman_rho"], 0.006)
close("sqrtvar-bias rho", -0.25, mech["var_bias_link"]["spearman_rho"], 0.006)
close("LOO R2", 0.27, mech["predictor"]["loo_r2"], 0.006)
close("size-partial rho", -0.38, mech["size_confound_control"]["partial_rank_rho_given_log10_params"], 0.006)
close("size-bias rho", 0.18, mech["size_confound_control"]["size_bias_spearman_rho"], 0.006)
close("mixed-effects coef", 0.16, mech["lmm"]["instruct_coef"], 0.006)
# Proposition 1 claimed Var_sigma(v) is "maximal when sigma is uniform". It is
# not: uniform maximises entropy, while the variance is maximised by the
# two-point distribution on the extreme values (Popoviciu). On a 1-5 scale that
# is 4 against uniform's 2, and the measured cells contain the discrepancy --
# the highest-variance distribution has MORE variance and LESS entropy than
# uniform. The corrected sentences quote these, so they are pinned to the data.
# Corollary 2 asserted that format perturbations act mainly through sqrt(Var)
# while content ones additionally raise ||delta_pi||. Nothing emitted the
# per-probe responsiveness split, so the assertion could not be checked against
# the run it describes. Measured, responsiveness rises for both families by a
# similar amount, and the largest single rise is on a FORMAT probe.
_rpp = mech.get("responsiveness_per_probe")
if _rpp:
    close("format responsiveness rise", 0.11, _rpp["format_mean_change"], 0.006)
    close("content responsiveness rise", 0.10, _rpp["content_mean_change"], 0.006)
    _largest = max(_rpp["per_probe"], key=lambda k: _rpp["per_probe"][k]["mean_change"])
    if _rpp["per_probe"][_largest]["family"] != "format":
        FAILS.append(
            f"the paper says the largest per-probe responsiveness rise is on a "
            f"format probe; it is now {_largest}, a "
            f"{_rpp['per_probe'][_largest]['family']} probe"
        )
    if _largest != "score_id":
        FAILS.append(
            f"the paper names score ID as the largest responsiveness rise; the "
            f"release gives {_largest}"
        )
_evr = mech.get("entropy_variance_relation")
if _evr:
    close("H-vs-sqrtVar correlation", 0.70, _evr["spearman_rho"], 0.006)
    close("uniform variance", 2.0, _evr["uniform_variance"], 0.006)
    close("attainable max variance", 4.0, _evr["attainable_max_variance"], 0.006)
    close("max measured variance", 3.10, _evr["max_measured_variance"], 0.006)
    close("entropy at max variance", 1.79, _evr["entropy_at_max_variance"], 0.006)
    if _evr["max_measured_variance"] <= _evr["uniform_variance"]:
        FAILS.append(
            "the paper says a measured cell exceeds the uniform distribution's "
            "variance; the release no longer contains one, so the correction to "
            "Proposition 1 has lost its empirical illustration"
        )
    if _evr["entropy_at_max_variance"] >= _evr["uniform_entropy"]:
        FAILS.append(
            "the highest-variance cell no longer has less entropy than uniform, "
            "which is the point the corrected proposition makes"
        )
# The control-only reading of the entropy-bias link repeats each checkpoint's
# entropy once per probe: rubric_order/control, score_id/numeric,
# reference_answer/none, authority/none and verbosity/control all reduce to the
# same prompt, so a checkpoint has one control measurement, not five. Its 130
# rows therefore carry 26 distinct entropies, and a p computed over 130 rows
# counts repeats as independent. The paper states this and quotes the collapsed
# reading; both the structural count and the collapsed statistic are pinned.
_col = mech["entropy_bias_link_control_only"]
close("control-only collapsed rho", -0.64,
      _col["collapsed_to_checkpoints"]["spearman_rho"], 0.006)
close("control-only collapsed p", 0.0004,
      _col["collapsed_to_checkpoints"]["spearman_p"], 0.00006)
if _col["n_distinct_entropies"] != 26:
    FAILS.append(
        f"the paper says the control-only reading carries 26 distinct entropies; "
        f"the release has {_col['n_distinct_entropies']}"
    )
if _col["collapsed_to_checkpoints"]["n"] != 26:
    FAILS.append(
        f"the collapsed control-only reading should have one row per checkpoint "
        f"(26); the release has {_col['collapsed_to_checkpoints']['n']}"
    )
mit = mech["mitigation"]
# The two max-min readouts are comparable with each other, and the deviation
# measures are comparable with each other. Comparing across the two families is
# what produced the retired 59% claim, so each pin below stays inside one.
close("mitigation expected", 1.09, mit["expected_maxmin"], 0.006)
close("mitigation argmax", 1.88, mit["argmax_maxmin"], 0.006)
close("single-format cost", 0.45, mit["single_format_cost_mad"], 0.006)
close("unmitigated deviation", 0.41, mit["unmitigated_mad"], 0.006)
if mit["marginalized_maxmin"] != 0.0:
    FAILS.append("marginalized max-min is not 0, but it is 0 by construction")
if mit["argmax_maxmin"] <= mit["expected_maxmin"]:
    FAILS.append("argmax no longer increases the spread over expected value")

# ---- robustness ----
close("exact permutation p", 0.00098, rob["F1_exact_permutation"]["exact_p_two_sided"], 0.00005)
close("headline mean effect", 0.257, rob["B3_sensitivity"]["full_mean_effect"], 0.006)
if rob["B3_sensitivity"]["excl_qwen_positive"] != "8/9":
    FAILS.append("excl-Qwen 8/9 stale")
close("EV/flip concordance", 0.56, rob["B4_readout_concordance"]["spearman_evbias_fliprate"], 0.006)
close("within-checkpoint entropy", -0.05, rob["B1_within_checkpoint"]["mean_within_rho"], 0.006)
close("within-checkpoint responsiveness", 0.65,
      rob["B1_within_checkpoint_responsiveness"]["mean_within_rho"], 0.006)
close("LMM entropy coef", -0.46, rob["B1_lmm"]["entropy_coef"], 0.006)
r2ci = rob["B2_predictor_bootstrap"]["r2_ci95"]
close("R2 CI low", -0.62, r2ci[0], 0.02)
close("R2 CI high", 0.57, r2ci[1], 0.02)
close("split-half SB", 0.99, rob["F4_split_half"]["spearman_brown"], 0.006)
close("bound tightness", 0.45, rob["F5_bound_tightness"]["mean_gradnorm_over_sqrtvar"], 0.006)
close("crossover sign acc", 0.74, rob["D3_crossover"]["sign_accuracy"], 0.006)
close("crossover magnitude rho", 0.60, rob["D3_crossover"]["spearman_dlogpred_dlogact"], 0.006)
vdec = rob["E_variance_decomposition"]
close("anatomy interaction", 0.37, vdec.get("family:probe"), 0.006)
# The leave-one-family-out range. Its maximum is 0.28464; the analyser used to
# round each leave-one-out mean to three decimals BEFORE taking the max, storing
# 0.285, which the paper then rounded again to 0.29 -- a digit the exact value
# never reaches. It aggregates exactly and stores four decimals now, so the
# paper's two-decimal quote is checkable against it.
_b3 = rob.get("B3_sensitivity", {})
_loo = _b3.get("loo_range")
if _loo:
    close("leave-one-out minimum", 0.23, _loo[0], 0.006)
    close("leave-one-out maximum", 0.28, _loo[1], 0.006)
    if round(_loo[1], 2) != 0.28:
        FAILS.append(
            f"the paper quotes the leave-one-out range as ending at +0.28; the "
            f"release maximum {_loo[1]} rounds to {round(_loo[1], 2)}"
        )
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
if not (0.86 <= shares[0] <= 0.88 and 0.93 <= shares[1] <= 0.95):
    FAILS.append(f"87%/94% SFT-share stale: {shares}")
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
states("variance-term correlation (macro)", r"variance term ($\rho=-0.25$)", 1)
states("variance-term correlation (pooled)", r"($\rho=-0.25$, $p=0.004$)", 1)
states("variance-term correlation (base-only)", r"base-only models ($\rho=-0.25$, $p=0.04$)", 1)
# Four distinct results each hold in eleven of thirteen families: the
# decisiveness drop, the bias increase, the alt-readout direction and the
# control-variance shrink. As "11/13" this was a single pin over all of them.
states("decisiveness families (macro)", "bits, 11/13 families", 1)
states("decisiveness families (body)", "bits (11/13 families", 1)
states("bias-increase families", "11/13 families, mean change", 1)
states("alt-readout families", "after tuning, 11/13 families", 1)
states("control-variance families", "($11/13$ families)", 1)
states("responsiveness family count", "12/13", 1)
states("within-checkpoint checkpoint count", "25/26", 1)
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
close("responsiveness after tuning", 0.24, resp_pair["instruct_mean"], 0.006)
check("responsiveness rise in prose", r"0.14\!\to\!0.24", resp_pair["base_mean"])
states("responsiveness rise", r"0.14\!\to\!0.24", 1)
states("responsiveness effect size", "d_z=1.48", 2)
states("responsiveness-bias correlation", r"\rho=+0.82", 2)
states("mixed-model coefficient", "+0.16", 2)
states("mixed-model observations", "n=13{,}000", 2)
states("size-partialled correlation", r"\rho=-0.38", 1)
states("size-bias correlation", r"\rho=+0.18", 1)
states("sub-1B band correlation", r"($\rho=-0.51$ and $-0.42$", 1)
states("ten-template pooled correlation", r"$\rho=-0.51$ ($n=180$)", 1)
states("within-checkpoint responsiveness", r"\rho=+0.65", 2)
states("within-checkpoint entropy", r"\rho=-0.05", 1)
states("readout concordance", r"\rho=0.56", 2)
states("exact permutation p", "0.00098", 1)
# Retired: the 59% compared a mean absolute deviation against a max-min spread,
# and marginalizing over the score-ID formats zeroes score-ID bias by
# construction anyway. The template ensemble is the measured mitigation, and it
# is what the abstract, the mitigation prose and the README now quote.
states("template ensemble mitigation", r"22\%", 2)

# The quantization control that discharges the 14B caveat. Both deltas are
# quoted in the prose, so both are pinned to the released measurement.
qpath = HERE / "results_quantization.json"
if qpath.exists():
    quant = json.loads(qpath.read_text())
    close("quantization fp16 delta", 0.54, quant["fp16_tuning_delta"], 0.006)
    close("quantization nf4 delta", 0.58, quant["nf4_tuning_delta"], 0.006)
    if quant["quantization_attenuates_delta"]:
        FAILS.append(
            "the prose says 4-bit inflates the tuning delta; the release says "
            "it attenuates, which would restore the confound on the 14B point"
        )
# The >3B size band. results_bands.json was pinned by nothing, and the paper
# quotes four of its numbers. The point estimate was printed as -0.02: the
# stored value is -0.0149, which rounds to -0.015 at three decimals and then to
# -0.02 at two. The true correlation never rounds to -0.02 -- only the rounded
# copy of it does. close() caps its tolerance at half a unit in the last printed
# place, so pinning the value here is what makes a re-rounding fail.
bpath = HERE / "results_bands.json"
if bpath.exists():
    bands = json.loads(bpath.read_text())
    hi_band = bands["bands"][">3B"]
    close(">3B band point estimate", -0.01, hi_band["spearman_rho"], 0.006)
    close(">3B clustered CI low", -0.71, hi_band["clustered_ci95"][0], 0.006)
    close(">3B clustered CI high", 0.19, hi_band["clustered_ci95"][1], 0.006)
    close("band difference naive p", 0.017, bands["difference"]["naive_p"], 0.0006)
    # close() ties this checker's constant to the data; states() ties the
    # paper's printed digit to this checker. Both links are needed -- a pin
    # on the data alone would not notice the paper drifting away from it.
    states(">3B point estimate in prose",
           "the point estimate is $\\rho=-0.01$", 1)
    if not bands["difference"]["clustered_ci_crosses_zero"]:
        FAILS.append(
            "the prose says the clustered interval for the band difference "
            "includes zero; the release says it does not"
        )

# The specification curve. check_prose.py did not read results_speccurve.json
# either, and the prose quotes a range from it: the six expected-value
# specifications are all positive, in 9--11 of 13 families. The per-spec family
# counts were computable but unstored, so the range was unverifiable -- the same
# gap that let the span-patch peak band drift.
scpath = HERE / "results_speccurve.json"
if scpath.exists():
    _sc = json.loads(scpath.read_text())
    _fp = _sc.get("per_spec_families_positive", {})
    _ev = {k: v for k, v in _fp.items() if k.startswith("ev|")}
    _means = {k: v for k, v in _sc["per_spec_mean_effect"].items() if k.startswith("ev|")}
    if len(_ev) != 6:
        FAILS.append(
            f"the paper says six expected-value specifications; the release has "
            f"{len(_ev)}"
        )
    if _ev and (min(_ev.values()), max(_ev.values())) != (9, 11):
        FAILS.append(
            f"the paper says the expected-value specifications are positive in "
            f"9--11 of 13 families; the release gives "
            f"{min(_ev.values())}--{max(_ev.values())}"
        )
    _neg = [k for k, v in _means.items() if v <= 0]
    if _neg:
        FAILS.append(
            f"the paper says all six expected-value specifications give a "
            f"positive mean effect; these do not: {_neg}"
        )
    states("spec-curve family range", "$9$--$11$/13 families positive", 1)

states("shared control disclosure", "carry only $26$ distinct entropies", 1)
# close() above ties this checker's constant to the released value; this ties
# the paper's printed range to the checker. Without both, mutating the page
# alone changes nothing -- which is how the registered mutation for this fix
# failed to fire the first time.
states("leave-one-out range", "within $[+0.23, +0.28]$", 1)
states("argmax readout", "1.88", 2)
states("frontier pooled correlation", r"\rho=-0.45", 2)
states("frontier pooled n", "n=145", 3)
# Pinned on the sentence, not the numeral. As "+0.06" this counted three
# unrelated statements sharing the value -- the 14B extension, the high-mass
# readout position, and (until it was corrected) OLMo-2-7B's SFT
# responsiveness step, which should have read +0.07. A pin that counts a bare
# number cannot tell the claim it names from any other printing the same
# digits, so it kept passing while one of the three was wrong.
states("14B attenuated effect", "$+0.06$ vs the panel's $+0.26$", 1)
states("high-mass readout effect", "on average ($+0.06$) but in only 2/4", 1)
states("14B probes positive", "3/5", 1)
states("preregistered-analyzer families", "mean bias in 4/4 families", 1)
states("union-readout families", "union readout (4/4 families)", 1)
states("SFT stage cells", "10/10", 1)
states("public-item families", "7/8", 2)
states("alt-template families", "8/9", 1)

# Secondary and appendix figures. These carry less weight individually, but they
# are the ones a referee recomputes precisely because nobody is watching them.
states("score-ID flip rates", "0.75$/$0.71", 1)
states("reference-answer flip rise", r"0.22\!\to\!0.37", 1)
states("authority flip rise", r"0.24\!\to\!0.42", 1)
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

# ---- the SFT share of the responsiveness rise --------------------------------
# The readout comparison is already pinned above; this keeps the direction the
# surrounding claim depends on. "Where raising confidence increases it" only
# means anything while the argmax readout -- the maximally confident one -- is
# the more biased of the two, and both sides are max-min spreads, so the
# comparison is like-for-like. That was the flaw in the retired 59%: it put a
# mean absolute deviation against a max-min spread.
if mech["mitigation"]["argmax_maxmin"] <= mech["mitigation"]["expected_maxmin"]:
    FAILS.append(
        "the mitigation claim contrasts nuisance removal against raising "
        f"confidence; argmax ({mech['mitigation']['argmax_maxmin']}) is no "
        f"longer the more biased readout"
    )

# "SFT installs 87--94% of the total rise." An integer percentage range, which
# the earlier range sweep did not match -- it looked for decimals. Recomputed
# per family from the stage table.
shares = {}
for fam in {c["family"] for c in stages["per_cell"]}:
    cells = [c for c in stages["per_cell"] if c["family"] == fam]
    by_stage = {}
    for c in cells:
        by_stage.setdefault(c["stage"], []).append(c["resp"])
    means = {s: sum(v) / len(v) for s, v in by_stage.items()}
    if "base" not in means:
        continue  # Tulu-3 has no base checkpoint
    last = max(by_stage, key=lambda s: next(c["order"] for c in cells if c["stage"] == s))
    total = means[last] - means["base"]
    if abs(total) > 1e-9 and "SFT" in means:
        shares[fam] = (means["SFT"] - means["base"]) / total

if shares:
    lo, hi = min(shares.values()) * 100, max(shares.values()) * 100
    if not (86.5 <= lo <= 87.5) or not (93.5 <= hi <= 94.5):
        FAILS.append(
            f"prose says SFT installs 87--94% of the responsiveness rise; measured "
            f"{lo:.1f}--{hi:.1f}% over {sorted(shares)}"
        )

# ---- frontier API call count -------------------------------------------------
# The compute disclosure said ~4,500 single-token logprob calls. The harness
# issues exactly one call per (judge, probe, variant, item), and its design
# maximum is 4 x 5 x 3 x 50 = 3,000 -- so 4,500 exceeded what the run could have
# made, let alone what it kept. Counted from the released data instead, which is
# what a reader can check.
closed_raw = json.loads((HERE / "results_closed.json").read_text())["results"]
calls = sum(
    len(variant["per_item"])
    for arms in closed_raw.values()
    if isinstance(arms, dict)
    for probes in arms.values()
    if isinstance(probes, dict)
    for cell in probes.values()
    if isinstance(cell, dict)
    for variant in cell.values()
    if isinstance(variant, dict) and "per_item" in variant
)
stated_calls = re.search(r"\$([\d{},]+)\$\s*\n?single-token logprob calls", text)
if not stated_calls:
    FAILS.append("the compute disclosure no longer states a logprob call count")
else:
    n = int(re.sub(r"[^\d]", "", stated_calls.group(1)))
    if n != calls:
        FAILS.append(
            f"compute disclosure claims {n:,} logprob calls; the released frontier "
            f"data accounts for {calls:,}"
        )

# ---- attention null ----------------------------------------------------------
# The paper reports that attention to nuisance tokens does *not* explain the
# responsiveness rise: the instruct/base ratio stays in 0.95--1.00 across all six
# model x perturbation cells. This is the explicit null that refutes the
# retracted version's fabricated "IIAR" attention mechanism, and it is computed
# from raw attn_results.json by no analyzer at all -- so the ratios are derived
# here rather than read from a summary that does not exist.
attn = json.loads((HERE / "attn_results.json").read_text())["results"]
ratios = []
for model, arms in attn.items():
    base, instruct = arms.get("base", {}), arms.get("instruct", {})
    for cell in base:
        if cell in instruct and base[cell]:
            ratios.append((f"{model}/{cell}", instruct[cell] / base[cell]))

if len(ratios) != 6:
    FAILS.append(f"prose says six model x perturbation cells, attn_results has {len(ratios)}")
if ratios:
    lo = min(r for _, r in ratios)
    hi = max(r for _, r in ratios)
    if lo < 0.95 - 1e-9:
        worst = min(ratios, key=lambda x: x[1])
        FAILS.append(f"attention ratio range starts at 0.95; {worst[0]} is {worst[1]:.4f}")
    if hi > 1.00 + 1e-9:
        worst = max(ratios, key=lambda x: x[1])
        FAILS.append(f"attention ratio range ends at 1.00; {worst[0]} is {worst[1]:.4f}")
    # The claim is that attention does not rise with tuning. If any cell rose
    # materially the null would be wrong regardless of the stated range.
    if hi > 1.05:
        FAILS.append(f"prose reports attention does not rise with tuning; a cell is at {hi:.4f}")

# ---- per-template correlations -----------------------------------------------
# Three rho values quoted for three prompt templates. They were computed once and
# written into the prose; no analysis emitted them, so the release could not be
# used to check them. Now emitted as C8b and pinned here, in the order the
# sentence states them.
per_template = rob.get("C8b_per_template_link", {})
if not per_template:
    FAILS.append("no per-template entropy-bias link in results_robustness.json")
else:
    quoted = [(-0.46, 0.011), (-0.43, 0.016), (-0.63, None)]
    names = sorted(per_template)
    if len(names) != len(quoted):
        FAILS.append(f"prose quotes {len(quoted)} templates, the analysis has {len(names)}")
    for name, (rho, pval) in zip(names, quoted):
        got = per_template[name]
        close(f"template {name} rho", rho, got["spearman_rho"], 0.006)
        if pval is not None:
            close(f"template {name} p", pval, got["p"], 0.0006)
        if got["n"] != 30:
            FAILS.append(f"prose says n=30 points per template, {name} has {got['n']}")
        if got["spearman_rho"] >= 0:
            FAILS.append(f"template {name} correlation is {got['spearman_rho']}, prose says negative")

# ---- stage trajectory and the concentration arrows ---------------------------
# A four-step trajectory is four claims sharing one sentence, so a single stale
# step hides among three correct ones. Recomputed per stage from the per-cell
# table rather than read from a summary field.
stages = json.loads((HERE / "results_stages_analysis.json").read_text())
by_stage = {}
for cell in stages["per_cell"]:
    if cell["family"] == "OLMo-2-1B":
        by_stage.setdefault(cell["stage"], []).append(cell)

if by_stage:
    ladder = sorted(by_stage, key=lambda s: by_stage[s][0]["order"])
    ent = [sum(c["entropy"] for c in by_stage[s]) / len(by_stage[s]) for s in ladder]
    bias = [sum(c["bias"] for c in by_stage[s]) / len(by_stage[s]) for s in ladder]
    for measured, quoted in zip(ent, (2.21, 1.80, 1.04, 0.99)):
        close(f"OLMo-1B entropy ladder step {quoted}", quoted, measured, 0.006)
    close("OLMo-1B bias at base", 0.24, bias[0], 0.006)
    close("OLMo-1B bias at SFT", 0.80, bias[1], 0.006)
    if len(ladder) != 4:
        FAILS.append(f"the OLMo-1B ladder has {len(ladder)} stages; the prose quotes four")

# The caption asserted that every stage sharpens the distribution. Seven of the
# eight transitions do; Tulu-3-8B's RLVR step raises entropy. A universal claim
# is falsified by one counterexample and nothing was counting them, so the count
# and the exception are both recomputed here.
paths = stages["P8_paths"]
falls, rises = 0, []
for family, rec in paths.items():
    path = rec["entropy_path"]
    for before, after, stage in zip(path, path[1:], rec["stages"][1:]):
        if after < before:
            falls += 1
        else:
            rises.append((family, stage, before, after))
total = falls + len(rises)
if f"seven of the eight stage transitions" in text and (falls, total) != (7, 8):
    FAILS.append(
        f"the paper says entropy falls at seven of eight stage transitions; "
        f"the data give {falls} of {total}"
    )
for family, stage, before, after in rises:
    # Naming the family proves nothing -- every family is named somewhere in the
    # section. The exception is pinned to its numbers, which appear nowhere else.
    quoted = f"${before:.2f}\\!\\to\\!{after:.2f}$"
    if quoted not in text:
        FAILS.append(
            f"entropy rises at {family}'s {stage} step and the paper does not "
            f"state it as {quoted}"
        )

# "the largest fall is at a preference stage in two of the three families"
preference_largest = 0
for rec in paths.values():
    path, names = rec["entropy_path"], rec["stages"]
    drops = {names[i + 1]: path[i] - path[i + 1] for i in range(len(path) - 1)}
    if drops and max(drops, key=drops.get) in ("DPO", "RLVR"):
        preference_largest += 1
if "in two of the three families" in text and (preference_largest, len(paths)) != (2, 3):
    FAILS.append(
        f"the paper says the largest fall is at a preference stage in two of "
        f"three families; the data give {preference_largest} of {len(paths)}"
    )

# Concentration, not leniency: the top-token probability rises while the mass on
# the top scores is flat. Both halves matter -- the second is what rules out the
# deflationary reading, and it is the one nobody would notice going stale.
collapse = rob["E3_score_collapse"]
close("max answer-token probability (base)", 0.40, collapse["base"]["maxp"], 0.006)
close("max answer-token probability (instruct)", 0.53, collapse["instruct"]["maxp"], 0.006)
close("top-score mass (base)", 0.54, collapse["base"]["top2_mass"], 0.006)
close("top-score mass (instruct)", 0.51, collapse["instruct"]["top2_mass"], 0.006)

# Template ensembling: the percentage and the two means it comes from.
ens = rob["C8_template_ensemble"]
close("single-template bias", 0.67, ens["mean_single_template_bias"], 0.006)
close("ensembled bias", 0.53, ens["mean_ensembled_bias"], 0.006)
if round(ens["reduction_frac"] * 100) != 22:
    FAILS.append(f"prose says ensembling cuts bias by 22%, data give {ens['reduction_frac']:.3f}")

# ---- stated ranges must contain their data -----------------------------------
# Twice now a range has been quoted with an endpoint that excludes the value it
# is meant to bound: the frontier means began at 0.84 with a judge at 0.820, and
# the bound-tightness range began at 0.38 with a cell at 0.375. Rounding an
# endpoint inward is the failure -- it always narrows the reported spread, and
# it always looks tidier than the truth. Endpoints are rounded outward here.
bound = rob["F5_bound_tightness"]
stated_lo, stated_hi = 0.37, 0.57
if bound["min"] < stated_lo - 1e-9:
    FAILS.append(f"bound-tightness range starts at {stated_lo}, data reach {bound['min']}")
if bound["max"] > stated_hi + 1e-9:
    FAILS.append(f"bound-tightness range ends at {stated_hi}, data reach {bound['max']}")
check("bound-tightness range in prose", f"${stated_lo}$--${stated_hi}$", bound["min"])
close("bound-tightness mean", 0.45, bound["mean_gradnorm_over_sqrtvar"], 0.006)

# Granularity: bias per unit of rating range, quoted as two ranges.
gran = json.loads((HERE / "results_gran_analysis.json").read_text())["per_scale"]
for arm, lo, hi in (("base", 0.04, 0.06), ("instruct", 0.07, 0.10)):
    vals = [s[f"bias_per_unit_range_{arm}"] for s in gran.values()]
    if min(vals) < lo - 1e-9 or max(vals) > hi + 1e-9:
        FAILS.append(
            f"prose bounds {arm} bias-per-unit-range at [{lo}, {hi}]; data span "
            f"[{min(vals):.4f}, {max(vals):.4f}]"
        )

# ---- frontier judges: the stated range must bracket the measured means -------
# The prose quoted "mean Delta of 0.84--1.01" while the judges' means are 0.820,
# 0.843 and 1.007. The low end was the second-smallest value, not the smallest.
# A range is two claims and it is easy to check only the memorable one, so both
# ends are computed from the per-judge means here.
closed = json.loads((HERE / "results_closed_analysis.json").read_text())
per_judge = next(
    (v for k, v in closed.items()
     if isinstance(v, dict) and any(isinstance(r, dict) and "mean_delta" in r for r in v.values())),
    None,
)
if per_judge:
    means = sorted(r["mean_delta"] for r in per_judge.values() if isinstance(r, dict))
    lo, hi = means[0], means[-1]
    stated = re.search(r"mean \$\\Delta\$ of \$([\d.]+)\$--\$([\d.]+)\$", text)
    if not stated:
        FAILS.append("prose no longer states a frontier mean-delta range")
    else:
        s_lo, s_hi = float(stated.group(1)), float(stated.group(2))
        # Half a unit in the last printed place, as in close(): the range is
        # quoted to two decimals, so 0.006 would let an endpoint drift into a
        # different printed value.
        if abs(s_lo - lo) > 0.005:
            FAILS.append(f"frontier range starts at {s_lo}, smallest judge mean is {lo:.3f}")
        if abs(s_hi - hi) > 0.005:
            FAILS.append(f"frontier range ends at {s_hi}, largest judge mean is {hi:.3f}")
    if len(means) < 3:
        FAILS.append(f"only {len(means)} frontier judges parsed; the range check is vacuous")

# ---- causal patching layer profile -------------------------------------------
# The paper's only intervention, and its shape is the claim: inert early, a jump
# at one layer, full transfer thereafter. Each of those three parts is pinned to
# the measured per-layer fractions.
patch = json.loads((HERE / "patch_results.json").read_text())
frac = {int(k): v for k, v in patch["frac_toward_instruct"].items()}

close("patch layer 9", 0.06, frac[9], 0.006)
close("patch layer 10", 0.89, frac[10], 0.006)
check("patch jump in prose", "0.06", frac[9])
check("patch jump in prose", "0.89", frac[10])

# "reaches 100% from layer 14 onward" -- every later layer, not just layer 14.
not_full = [layer for layer, v in frac.items() if layer >= 14 and v < 1.0]
if not_full:
    FAILS.append(f"prose says full transfer from layer 14 onward; layers {not_full} are below 1.0")

# The early-layer clause said "approx 0" while layer 0 is 0.17. It now states
# the real bound, so the bound is what gets checked.
early = {layer: v for layer, v in frac.items() if layer <= 9}
if max(early.values()) > 0.18 + 1e-9:
    FAILS.append(
        f"prose bounds the early-layer fraction at 0.18; the data reach "
        f"{max(early.values())} at layer {max(early, key=early.get)}"
    )
if sum(1 for v in early.values() if v == 0.0) != 6:
    FAILS.append(
        f"prose says the fraction is exactly zero at six of layers 0-9; the data "
        f"show {sum(1 for v in early.values() if v == 0.0)}"
    )
if patch["n_items_used"] != 35:
    FAILS.append(f"prose says n=35 patched items, the run used {patch['n_items_used']}")

# ---- gold-standard discrimination ("accuracy 0.98 -> 0") ---------------------
# An abstract headline that was pinned to nothing. The arrow is arm-specific:
# under rubric reversal the instruct arm falls to exactly 0.00 while the base arm
# lands at 0.02, so quoting "-> 0" is right for instruct and wrong for base. The
# check encodes which arm it is, otherwise a later edit could swap arms and still
# look correct.
gold = json.loads((HERE / "results_gold.json").read_text())
gold_control = gold["control"]
gold_reversed = gold["degradation"]["reversed"]

close("gold control accuracy (instruct)", 0.98, gold_control["instruct"]["mean_accuracy"], 0.006)
# Reversal does not take accuracy to chance; it takes it PAST chance, to
# inversion. These are binary good-vs-bad pairs, so chance is 0.5, and the
# release measures 0.02 and 0.00 -- the judge ordering almost every pair the
# wrong way round. The prose read "collapses accuracy to chance", which names a
# weaker and different result than the one measured.
for _arm in ("base", "instruct"):
    _acc = gold_reversed[_arm]["accuracy_under_bias"]
    if _acc >= 0.5:
        FAILS.append(
            f"gold reversed accuracy for {_arm} is {_acc}, at or above the 0.5 "
            f"chance level for binary pairs; the paper describes near-total "
            f"inversion, which that number would no longer support"
        )
states("gold inversion wording", "past it to near-total inversion", 1)
check("gold control accuracy in prose", "0.98", gold_control["instruct"]["mean_accuracy"])
if gold_reversed["instruct"]["accuracy_under_bias"] != 0.0:
    FAILS.append(
        f"prose says rubric reversal drops instruct accuracy to 0, but the "
        f"analysis reports {gold_reversed['instruct']['accuracy_under_bias']}"
    )
if gold_reversed["base"]["accuracy_under_bias"] == gold_reversed["instruct"]["accuracy_under_bias"]:
    FAILS.append(
        "base and instruct collapse to the same value; the arm-specific '-> 0' "
        "claim can no longer be distinguished and this check is vacuous"
    )
if not re.search(r"0\.98.{0,12}to.{0,12}0[^.\d]", text):
    FAILS.append("prose no longer states the 0.98 -> 0 discrimination collapse")

# ---- the registered per-probe test -------------------------------------------
# The paper now states that the registered analysis -- paired Wilcoxon,
# Holm-corrected across the five probes -- is null for every probe. That
# sentence has to keep matching the corrected p-values it summarises, in both
# directions: if a probe ever does survive, the disclosure becomes false in the
# paper's own favour, which is the direction that goes unnoticed.
peritem = json.loads((HERE / "results_peritem.json").read_text())
holm = {p: v["wilcoxon_p_holm"] for p, v in peritem["summary"].items()}
survivors = sorted(p for p, v in holm.items() if v <= 0.05)
if survivors:
    FAILS.append(
        f"the paper says the registered per-probe test is null for every probe; "
        f"{survivors} now survive Holm correction"
    )
smallest = min(holm.values())
if f"$p_{{\\text{{Holm}}}}={smallest:.2f}$" not in text:
    FAILS.append(
        f"the paper quotes a smallest Holm-corrected p that is not {smallest:.2f}"
    )
smallest_probes = sorted(peritem["summary"][p]["label"] for p, v in holm.items()
                         if v == smallest)
if len(smallest_probes) != 2:
    FAILS.append(
        f"the paper names two probes at the smallest corrected p; the data give "
        f"{smallest_probes}"
    )

# ---- the per-domain claim ----------------------------------------------------
# "The effect is not domain-specific: instruct bias exceeds base bias in every
# one of the five item domains." Unchecked until now, which is a poor place to
# leave a gap: the audit's FABRICATED verdict was on a per-domain table, whose
# split was invented because the pipeline could not compute it. A per-domain
# claim in this paper is the one a sceptical reader should reach for first.
domains = json.loads((HERE / "results_peritem.json").read_text())["domain"]
if len(domains) != 5:
    FAILS.append(f"prose says five item domains, the data has {len(domains)}")
not_higher = [d for d, v in domains.items() if v["instruct"] <= v["base"]]
if not_higher:
    FAILS.append(
        f"prose says instruct bias exceeds base bias in every domain; it does not "
        f"in {not_higher}"
    )
if not re.search(r"(?i)every one of the five item domains", text):
    FAILS.append("prose no longer states the per-domain claim; update this check with it")

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
if f"{n_pos}/{wcr['n_checkpoints']}" != "25/26":
    FAILS.append(
        f"responsiveness ranks probes in {n_pos}/{wcr['n_checkpoints']} checkpoints, "
        f"prose says 25/26"
    )
close("within-checkpoint responsiveness rho", 0.65, wcr["mean_within_rho"], 0.006)
close("within-checkpoint entropy rho", -0.05, rob["B1_within_checkpoint"]["mean_within_rho"], 0.006)

if FAILS:
    print("PROSE-CONSISTENCY FAILURES:")
    for f in FAILS:
        print(" -", f)
    sys.exit(1)
print(f"prose-consistency OK ({len(FAILS)} failures)")
