# Superseded

`scoring_bias_honest.tex` — an intermediate honest paper (7 tiny models ≤7B, t4fam data)
that concluded instruction tuning *reduces* scoring bias.

**It is superseded and should not be cited.** It used **parse-based** scoring, which the
current paper (`../scoring_bias_v2.tex`, Appendix A) shows is a measurement confound: weak
and base models emit no parseable label, so items are silently dropped, biasing the
base-vs-instruct comparison. Re-run with expected-value (logit) scoring on a larger family
set, the direction reverses: instruction tuning *increases* bias. See the current paper.
