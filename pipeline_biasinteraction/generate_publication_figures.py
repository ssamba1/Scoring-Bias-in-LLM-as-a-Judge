#!/usr/bin/env python3
"""Generate all publication-quality figures from corrected synthetic data.
Output: paper/figures/*.png
"""
import csv, math, os
from pathlib import Path

BASE = Path(__file__).parent.parent
DATA = BASE / "results" / "bias_interaction_synthetic.csv"
OUT = BASE / "paper" / "figures"
os.makedirs(OUT, exist_ok=True)

with open(DATA) as f:
    rows = list(csv.DictReader(f))
for r in rows:
    r["score"] = float(r["score"])

judges = sorted(set(r["judge"] for r in rows))

def cond_mean(judge, cond):
    s = [r["score"] for r in rows if r["judge"]==judge and r["condition"]==cond]
    return sum(s)/len(s) if s else 0

def scores(judge, pos=None, leng=None, sent=None):
    s = [r for r in rows if r["judge"]==judge]
    if pos: s = [x for x in s if x.get("position")==pos]
    if leng: s = [x for x in s if x.get("length")==leng]
    if sent: s = [x for x in s if x.get("sentiment")==sent]
    return [x["score"] for x in s]

# Compute interaction data
fig1_data = []
for j in judges:
    base = cond_mean(j, "baseline")
    worst = cond_mean(j, "worst_case")
    f_s = scores(j, pos="first", leng="normal", sent="neutral")
    s_s = scores(j, pos="second", leng="normal", sent="neutral")
    l_s = scores(j, leng="long", pos="first", sent="neutral")
    n_s = scores(j, leng="normal", pos="first", sent="neutral")
    ne_s = scores(j, sent="negative", pos="first", leng="normal")
    nu_s = scores(j, sent="neutral", pos="first", leng="normal")

    pos_b = abs(sum(f_s)/len(f_s)-sum(s_s)/len(s_s)) if f_s and s_s else 0
    ver_b = abs(sum(l_s)/len(l_s)-sum(n_s)/len(n_s)) if l_s and n_s else 0
    sen_b = abs(sum(ne_s)/len(ne_s)-sum(nu_s)/len(nu_s)) if ne_s and nu_s else 0
    comb = base - worst
    si = pos_b + ver_b + sen_b
    ir = comb / si if si > 0 else 0

    fig1_data.append((j, pos_b, ver_b, sen_b, comb, ir, base, worst))

# Generate ASCII bar charts (terminal-friendly)
print("="*70)
print("PUBLICATION FIGURES — Bias Interaction Effects")
print("="*70)

print("\n1. Interaction Ratios by Judge")
print("-"*50)
for j, _, _, _, _, ir, _, _ in fig1_data:
    bar = "█" * int(ir * 10)
    label = f"{ir:.2f}"
    print(f"  {j:<10} {bar} {label}")

print("\n2. Baseline vs Worst Case")
print("-"*50)
for j, _, _, _, _, _, base, worst in fig1_data:
    loss = base - worst
    bar_base = "█" * int(base * 8)
    bar_worst = "█" * int(worst * 8)
    print(f"  {j:<10} Base: {bar_base} {base:.2f}")
    print(f"  {'':10} Worst: {bar_worst} {worst:.2f} (Δ={loss:.2f})")

print("\n3. Individual Bias Effects")
print("-"*50)
print(f"{'Judge':<10} {'Position':<10} {'Verbosity':<10} {'Sentiment':<10}")
for j, pb, vb, sb, _, _, _, _ in fig1_data:
    print(f"  {j:<10} {pb:<10.3f} {vb:<10.3f} {sb:<10.3f}")

print("\n4. Interaction Table (LaTeX-ready)")
print("-"*70)
print("\\begin{tabular}{lcccccc}")
print("\\toprule")
print("Judge & Position & Verbosity & Sentiment & Combined & IR & Pattern \\\\")
print("\\midrule")
for j, pb, vb, sb, comb, ir, _, _ in fig1_data:
    pat = "Compounding" if ir > 1.05 else ("Cancelling" if ir < 0.95 else "Additive")
    print(f"{j} & {pb:.3f} & {vb:.3f} & {sb:.3f} & {comb:.3f} & {ir:.2f} & {pat} \\\\")
print("\\bottomrule")
print("\\end{tabular}")

# Save figure data to CSV for plotting
fig_csv = OUT / "interaction_data.csv"
with open(fig_csv, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["judge","position_bias","verbosity_bias","sentiment_bias","combined","interaction_ratio","baseline","worst"])
    for row in fig1_data:
        w.writerow(row)
print(f"\nFigure data saved: {fig_csv}")

# Create an HTML with embedded Chart.js figures
html = """<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><title>Publication Figures</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{font-family:sans-serif;background:#0f172a;color:#e2e8f0;max-width:1000px;margin:auto;padding:20px}
h2{color:#93c5fd;margin:30px 0 15px}
canvas{max-height:300px;margin:15px 0}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
</style></head><body>
<h1>Publication Figures — Bias in LLM-as-a-Judge</h1>
<div class='grid'>
<div><h2>Interaction Ratios</h2><canvas id='c1'></canvas></div>
<div><h2>Baseline vs Worst</h2><canvas id='c2'></canvas></div>
</div>
<div><h2>Bias Effect Sizes</h2><canvas id='c3' style='max-height:200px'></canvas></div>

<script>
const d = """ + str([{"j":j,"pb":pb,"vb":vb,"sb":sb,"co":co,"ir":ir,"ba":ba,"wo":wo}
        for j,pb,vb,sb,co,ir,ba,wo in fig1_data]).replace("'",'"') + """;
const judges = d.map(x=>x.j);
const jColors = {claude:'#4C72B0',gpt4o:'#DD8452',gemini:'#55A868',deepseek:'#C44E52',llama:'#8172B2'};

new Chart('c1',{type:'bar',data:{labels:judges,
  datasets:[{label:'Interaction Ratio',data:d.map(x=>x.ir),
    backgroundColor:judges.map(j=>d.find(x=>x.j==j).ir>1.05?'#f8717180':'#6ee7b780'),
    borderColor:judges.map(j=>d.find(x=>x.j==j).ir>1.05?'#f87171':'#6ee7b7'),borderWidth:2}]},
  options:{responsive:true,scales:{y:{min:0,grid:{color:'#334155'}}},
  plugins:{annotation:{annotations:{line:{type:'line',yMin:1,yMax:1,borderColor:'red',borderWidth:2,borderDash:[5,5]}}}}}});

new Chart('c2',{type:'bar',data:{labels:judges,
  datasets:[{label:'Baseline',data:d.map(x=>x.ba),backgroundColor:'#55A86880',borderColor:'#55A868',borderWidth:2},
  {label:'Worst Case',data:d.map(x=>x.wo),backgroundColor:'#C44E5280',borderColor:'#C44E52',borderWidth:2}]},
  options:{responsive:true,scales:{y:{min:2.5,max:4,grid:{color:'#334155'}}}}});

new Chart('c3',{type:'bar',data:{labels:judges,
  datasets:[{label:'Position',data:d.map(x=>x.pb),backgroundColor:'#4C72B080'},
    {label:'Verbosity',data:d.map(x=>x.vb),backgroundColor:'#DD845280'},
    {label:'Sentiment',data:d.map(x=>x.sb),backgroundColor:'#55A86880'}]},
  options:{responsive:true,scales:{y:{min:0,grid:{color:'#334155'}}}}});
</script></body></html>"""

fig_html = OUT / "figures.html"
with open(fig_html, "w") as f:
    f.write(html)
print(f"Interactive figures: {fig_html}")
print("\nDone.")
