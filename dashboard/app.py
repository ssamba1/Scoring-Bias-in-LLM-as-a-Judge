"""
Scoring Bias Dashboard  Interactive Streamlit app for exploring bias results.

Run with:
    streamlit run dashboard/app.py

Tabs:
    1. Model Explorer  Select a model, see probe breakdowns
    2. Comparison     Select 2+ models, side-by-side
    3. Landscape      All models, sorting
    4. About          Paper info, citation
"""

from __future__ import annotations
import sys
from pathlib import Path

# Ensure project root is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import json

# Page config
st.set_page_config(
    page_title="Scoring Bias Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Scoring Bias in LLM-as-a-Judge")
st.markdown("""
*Interactive dashboard for exploring scoring bias across 22 models
with base-instruct comparison.*
""")


# ── Data Loading ──

@st.cache_data
def load_data():
    """Load pre-computed analysis results or generate demo data."""
    results_file = ROOT / "output" / "deltas.json"
    if results_file.exists():
        with open(results_file) as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        return df

    csv_dir = ROOT / "data" / "raw"
    csv_files = list(csv_dir.glob("*.csv"))
    if csv_files:
        df = pd.read_csv(csv_files[0])
        # Aggregate
        summary = df.groupby(["model_name", "probe", "condition"])["score"].mean().reset_index()
        pivot = summary.pivot_table(
            index=["model_name", "probe"],
            columns="condition",
            values="score",
        ).reset_index()
        pivot["delta"] = pivot.iloc[:, 2:].diff(axis=1).iloc[:, -1] if pivot.shape[1] > 3 else 0
        return pivot

    # Generate demo data
    np.random.seed(42)
    probes = ["rubric_order", "score_id", "reference_answer"]
    models = [("llama-3.1-8b", "Llama"), ("llama-3.1-8b-it", "Llama"),
              ("gemma-2-27b", "Gemma"), ("gemma-2-27b-it", "Gemma"),
              ("qwen-2.5-32b", "Qwen"), ("qwen-2.5-32b-it", "Qwen"),
              ("mistral-7b", "Mistral"), ("mistral-7b-it", "Mistral")]
    rows = []
    for model, family in models:
        for probe in probes:
            bias = np.random.choice([-0.5, -0.3, 0, 0.3, 0.5, 0.8])
            rows.append({
                "model_name": model,
                "family": family,
                "probe": probe,
                "delta": round(bias, 4),
                "flip_rate": round(np.random.uniform(0.1, 0.6), 4),
            })
    return pd.DataFrame(rows)


df = load_data()

# Sidebar
st.sidebar.header("Controls")
all_models = sorted(df["model_name"].unique())
all_probes = sorted(df["probe"].unique()) if "probe" in df.columns else []

# ── Tabs ──
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Model Explorer",
    "⚖️ Comparison",
    "🌐 Landscape",
    "ℹ️ About",
])

# ── Tab 1: Model Explorer ──
with tab1:
    st.header("Model Explorer")
    selected_model = st.selectbox("Select a model:", all_models, key="explorer_model")

    if "probe" in df.columns:
        model_data = df[df["model_name"] == selected_model]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Bias Deltas by Probe")
            if "delta" in model_data.columns:
                delta_col = model_data[["probe", "delta"]].copy()
                delta_col.columns = ["Probe", "Bias Delta (Δ)"]
                st.dataframe(delta_col, use_container_width=True)

        with col2:
            st.subheader("Flip Rates")
            if "flip_rate" in model_data.columns:
                flip_col = model_data[["probe", "flip_rate"]].copy()
                flip_col.columns = ["Probe", "Flip Rate"]
                st.dataframe(flip_col, use_container_width=True)

        if "delta" in model_data.columns:
            st.subheader("Delta Visualization")
            chart_data = model_data.set_index("probe")["delta"]
            st.bar_chart(chart_data)

# ── Tab 2: Comparison ──
with tab2:
    st.header("Model Comparison")
    selected_models = st.multiselect(
        "Select 2+ models to compare:",
        all_models,
        default=all_models[:2] if len(all_models) >= 2 else all_models,
        key="compare_models",
    )

    if len(selected_models) >= 2 and "probe" in df.columns and "delta" in df.columns:
        compare_df = df[df["model_name"].isin(selected_models)]
        pivot = compare_df.pivot_table(
            index="probe",
            columns="model_name",
            values="delta",
            aggfunc="first",
        ).fillna(0)

        st.subheader("Side-by-Side Delta Comparison")
        st.dataframe(pivot, use_container_width=True)

        st.subheader("Chart")
        st.bar_chart(pivot)

        if "family" in compare_df.columns:
            st.subheader("Model Families")
            family_info = compare_df[["model_name", "family"]].drop_duplicates()
            st.dataframe(family_info, use_container_width=True)
    else:
        st.info("Select at least 2 models to compare.")

# ── Tab 3: Landscape ──
with tab3:
    st.header("Bias Landscape Overview")

    if "delta" in df.columns and "probe" in df.columns:
        # Aggregate
        pivot = df.pivot_table(
            index="model_name",
            columns="probe",
            values="delta",
            aggfunc="first",
        ).fillna(0)

        # Sort by mean absolute delta
        pivot["avg_abs_delta"] = pivot.abs().mean(axis=1)
        pivot = pivot.sort_values("avg_abs_delta", ascending=False)

        st.subheader("Models ranked by average |Δ|")
        display_cols = [c for c in pivot.columns if c != "avg_abs_delta"] + ["avg_abs_delta"]
        st.dataframe(pivot[display_cols], use_container_width=True)

        st.subheader("Landscape Chart")
        st.bar_chart(pivot.drop(columns="avg_abs_delta"))

        # Summary stats
        st.subheader("Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Models", len(pivot))
        with col2:
            st.metric("Probes", len([c for c in pivot.columns if c != "avg_abs_delta"]))
        with col3:
            max_model = pivot["avg_abs_delta"].idxmax()
            st.metric("Most Biased", max_model, f"{pivot.loc[max_model, 'avg_abs_delta']:.3f}")
        with col4:
            min_model = pivot["avg_abs_delta"].idxmin()
            st.metric("Least Biased", min_model, f"{pivot.loc[min_model, 'avg_abs_delta']:.3f}")

# ── Tab 4: About ──
with tab4:
    st.header("About This Dashboard")

    st.markdown("""
    ### 📄 Paper
    **Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape with Base-Instruct Comparison**

    *Sricharan Samba* (2026)

    ### 📝 Abstract
    *LLM-as-a-Judge scoring exhibits systematic biases depending on how the
    rubric is presented, how score IDs are labeled, and whether reference
    answers are provided. This paper presents a comprehensive 22-model
    landscape of scoring bias with a focus on the base-vs-instruct comparison.*

    ### 📚 Citation
    ```bibtex
    @article{samba2026scoring,
      title     = {Scoring Bias in {LLM-as-a-Judge} Models: A 22-Model Landscape
                   with Base-Instruct Comparison},
      author    = {Samba, Sricharan},
      journal   = {arXiv preprint},
      year      = {2026},
      doi       = {10.5281/zenodo.21361920},
    }
    ```

    ### 🔗 Links
    - [Paper on arXiv](https://arxiv.org/abs/2607.xxxxx)
    - [GitHub Repository](https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge)
    - [Colab Notebook](https://colab.research.google.com/github/ssamba1/Scoring-Bias-in-LLM-as-a-Judge/blob/main/notebooks/colab_reproduction.ipynb)
    - [Binder Demo](https://mybinder.org/v2/gh/ssamba1/Scoring-Bias-in-LLM-as-a-Judge/main?labpath=notebooks%2Fbinder_demo.ipynb)

    ### 💻 Data
    | Metric | Value |
    |--------|-------|
    | Models | {len(all_models)} |
    | Probes | {len(all_probes)} |
    | Data loaded | {'Yes' if len(df) > 0 else 'No'} |
    """.format(all_models=all_models, all_probes=all_probes, df=df))

    st.caption("Built with Streamlit · Scoring Bias Analysis Toolkit v1.0.0")
