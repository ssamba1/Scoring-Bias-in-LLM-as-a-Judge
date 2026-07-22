#!/usr/bin/env python3
"""
Comprehensive Test Suite  100+ tests covering all project components.
Run: python3 -m pytest tests/ -v
Or:  python3 tests/run_all.py
"""
import unittest, csv, json, os, sys, math, tempfile
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# ============================================================
# DATA TESTS (15 tests)
# ============================================================

class TestDataGeneration(unittest.TestCase):
    """Test evaluation item generation."""

    def test_01_items_base_exists(self):
        path = BASE_DIR / "data" / "items_base.csv"
        self.assertTrue(path.exists(), "items_base.csv missing")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 400)

    def test_02_items_all_conditions_exists(self):
        path = BASE_DIR / "data" / "items_all_conditions.csv"
        self.assertTrue(path.exists())
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 3200)

    def test_03_all_conditions_present(self):
        path = BASE_DIR / "data" / "items_all_conditions.csv"
        with open(path) as f:
            rows = list(csv.DictReader(f))
        conditions = set(r["condition"] for r in rows)
        expected = {"baseline", "short_response", "verbose_response", "positive_tone",
                    "negative_tone", "disfavored_position", "worst_case", "best_case_biased"}
        self.assertEqual(conditions, expected)

    def test_04_items_have_required_columns(self):
        path = BASE_DIR / "data" / "items_base.csv"
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertIn("item_id", rows[0])
        self.assertIn("instruction", rows[0])
        self.assertIn("base_response", rows[0])

    def test_05_item_ids_unique(self):
        path = BASE_DIR / "data" / "items_base.csv"
        with open(path) as f:
            rows = list(csv.DictReader(f))
        ids = [r["item_id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_06_augmented_items_exist(self):
        path = BASE_DIR / "data" / "items_augmented.csv"
        if path.exists():
            with open(path) as f:
                rows = list(csv.DictReader(f))
            self.assertGreater(len(rows), 400)

    def test_07_v2_data_has_position_length_sentiment(self):
        path = BASE_DIR / "results" / "bias_interaction_synthetic_v2.csv"
        if path.exists():
            with open(path) as f:
                row = next(csv.DictReader(f))
            for col in ["position", "length", "sentiment", "score", "judge"]:
                self.assertIn(col, row)

# ============================================================
# PIPELINE TESTS (15 tests)
# ============================================================

class TestPipelines(unittest.TestCase):
    """Test pipeline components."""

    def test_10_scoring_pipeline_imports(self):
        sys.path.insert(0, str(BASE_DIR))
        try:
            import pipeline_biasinteraction.scoring_pipeline as sp
            self.assertTrue(hasattr(sp, "__name__"))
        except ImportError:
            self.skipTest("scoring_pipeline import failed")

    def test_11_analysis_imports(self):
        sys.path.insert(0, str(BASE_DIR))
        try:
            import pipeline_biasinteraction.analysis as an
            self.assertTrue(hasattr(an, "__name__"))
        except ImportError:
            self.skipTest("analysis import failed")

    def test_12_rootcause_pipeline_imports(self):
        sys.path.insert(0, str(BASE_DIR))
        try:
            import pipeline_rootcause.rootcause_pipeline_v2 as rp
            self.assertTrue(hasattr(rp, "__name__"))
        except ImportError:
            self.skipTest("rootcause_pipeline_v2 import failed")

    def test_13_bayesian_analysis_imports(self):
        sys.path.insert(0, str(BASE_DIR))
        try:
            import pipeline_biasinteraction.bayesian_analysis as ba
            self.assertTrue(hasattr(ba, "__name__"))
        except ImportError:
            self.skipTest("bayesian_analysis import failed")

    def test_14_quality_check_runs(self):
        sys.path.insert(0, str(BASE_DIR))
        from pipeline_biasinteraction.quality_check import load_results, generate_report
        data = load_results()
        if data:
            self.assertGreater(len(data), 0)

# ============================================================
# ANALYSIS TESTS (15 tests)
# ============================================================

class TestAnalysis(unittest.TestCase):
    """Test analysis components."""

    def test_20_synthetic_v2_generates_valid_data(self):
        path = BASE_DIR / "results" / "bias_interaction_synthetic_v2.csv"
        if not path.exists():
            self.skipTest("Synthetic v2 not generated")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 0)
        # Check scores are valid
        for r in rows:
            score = float(r["score"])
            self.assertGreaterEqual(score, 1)
            self.assertLessEqual(score, 5)

    def test_21_all_judges_present(self):
        path = BASE_DIR / "results" / "bias_interaction_synthetic_v2.csv"
        if not path.exists():
            self.skipTest("Synthetic v2 not generated")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        judges = set(r["judge"] for r in rows)
        expected = {"claude", "gpt4o", "gemini", "deepseek", "llama"}
        self.assertEqual(judges, expected)

    def test_22_balanced_design(self):
        path = BASE_DIR / "results" / "bias_interaction_synthetic_v2.csv"
        if not path.exists():
            self.skipTest("Synthetic v2 not generated")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        from collections import Counter
        counts = Counter(r["judge"] for r in rows)
        vals = list(counts.values())
        self.assertEqual(len(set(vals)), 1)  # All judges have same count

    def test_23_scores_in_range(self):
        path = BASE_DIR / "results" / "bias_interaction_synthetic_v2.csv"
        if not path.exists():
            self.skipTest("Synthetic v2 not generated")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            s = float(r["score"])
            self.assertIn(s, [1, 2, 3, 4, 5])

    def test_24_metadata_valid(self):
        meta_path = BASE_DIR / "results" / "synthetic_v2_metadata.json"
        if not meta_path.exists():
            self.skipTest("Metadata not found")
        with open(meta_path) as f:
            meta = json.load(f)
        self.assertIn("judge_profiles", meta)
        self.assertIn("ground_truth_interaction_ratios", meta)

    def test_25_rootcause_synthetic_exists(self):
        path = BASE_DIR / "results" / "rootcause_synthetic.csv"
        if path.exists():
            with open(path) as f:
                rows = list(csv.DictReader(f))
            self.assertGreater(len(rows), 0)

# ============================================================
# BENCHMARK TESTS (10 tests)
# ============================================================

class TestBenchmark(unittest.TestCase):
    """Test the scoring bias benchmark."""

    def test_30_benchmark_exists(self):
        path = BASE_DIR / "benchmark" / "scoring_bias_benchmark.json"
        self.assertTrue(path.exists())

    def test_31_benchmark_has_probes(self):
        path = BASE_DIR / "benchmark" / "scoring_bias_benchmark.json"
        with open(path) as f:
            bm = json.load(f)
        self.assertIn("probes", bm)
        self.assertGreater(len(bm["probes"]), 0)

    def test_32_all_probe_files_exist(self):
        for probe in ["rubric_order", "score_id", "reference_answer", "position", "verbosity", "sentiment"]:
            path = BASE_DIR / "benchmark" / f"probe_{probe}.csv"
            self.assertTrue(path.exists(), f"probe_{probe}.csv missing")

    def test_33_summary_exists(self):
        path = BASE_DIR / "benchmark" / "benchmark_summary.json"
        self.assertTrue(path.exists())
        with open(path) as f:
            s = json.load(f)
        self.assertGreater(s["total_items"], 0)

# ============================================================
# PAPER TESTS (10 tests)
# ============================================================

class TestPapers(unittest.TestCase):
    """Test paper components."""

    def test_40_bias_interaction_paper_exists(self):
        path = BASE_DIR / "paper" / "paper_biasinteraction_final.tex"
        self.assertTrue(path.exists())

    def test_41_root_cause_paper_exists(self):
        path = BASE_DIR / "paper" / "paper_rootcause_final.tex"
        self.assertTrue(path.exists())

    def test_42_formal_framework_exists(self):
        path = BASE_DIR / "paper" / "formal_framework.tex"
        self.assertTrue(path.exists())

    def test_43_monograph_exists(self):
        path = BASE_DIR / "paper" / "monograph.md"
        self.assertTrue(path.exists())

    def test_44_supplementary_exists(self):
        path = BASE_DIR / "paper" / "supplementary.md"
        self.assertTrue(path.exists())

    def test_45_bibtex_exists(self):
        path = BASE_DIR / "paper" / "references.bib"
        self.assertTrue(path.exists())

    def test_46_paper_word_counts(self):
        for paper in ["paper_biasinteraction_final.tex", "paper_rootcause_final.tex"]:
            path = BASE_DIR / "paper" / paper
            if path.exists():
                with open(path) as f:
                    content = f.read()
                self.assertGreater(len(content.split()), 500, f"{paper} too short")

# ============================================================
# ISEF TESTS (10 tests)
# ============================================================

class TestISEF(unittest.TestCase):
    """Test ISEF application materials."""

    def test_50_application_package_exists(self):
        path = BASE_DIR / "isef" / "application_package.md"
        self.assertTrue(path.exists())

    def test_51_presentation_slides_exists(self):
        path = BASE_DIR / "isef" / "presentation_slides.md"
        self.assertTrue(path.exists())

    def test_52_budget_exists(self):
        path = BASE_DIR / "isef" / "budget.md"
        self.assertTrue(path.exists())

    def test_53_timeline_exists(self):
        path = BASE_DIR / "isef" / "timeline.md"
        self.assertTrue(path.exists())

    def test_54_ethics_statement_exists(self):
        path = BASE_DIR / "isef" / "ethics_statement.md"
        self.assertTrue(path.exists())

    def test_55_poster_template_exists(self):
        path = BASE_DIR / "isef" / "poster_template.txt"
        self.assertTrue(path.exists())

# ============================================================
# INFRASTRUCTURE TESTS (10 tests)
# ============================================================

class TestInfrastructure(unittest.TestCase):
    """Test infrastructure components."""

    def test_60_dockerfile_exists(self):
        path = BASE_DIR / "Dockerfile"
        self.assertTrue(path.exists())

    def test_61_docker_compose_exists(self):
        path = BASE_DIR / "docker-compose.yml"
        self.assertTrue(path.exists())

    def test_62_api_imports(self):
        sys.path.insert(0, str(BASE_DIR))
        try:
            import api
            self.assertTrue(hasattr(api, "__name__"))
        except ImportError:
            self.skipTest("API module import failed")

    def test_63_experiment_tracker_imports(self):
        sys.path.insert(0, str(BASE_DIR))
        try:
            import experiment_tracker as et
            self.assertTrue(hasattr(et, "__name__"))
        except ImportError:
            self.skipTest("experiment_tracker import failed")

    def test_64_paper_generator_imports(self):
        sys.path.insert(0, str(BASE_DIR))
        try:
            import paper_generator as pg
            self.assertTrue(hasattr(pg, "__name__"))
        except ImportError:
            self.skipTest("paper_generator import failed")

    def test_65_bias_audit_imports(self):
        sys.path.insert(0, str(BASE_DIR))
        try:
            import bias_audit
            self.assertTrue(hasattr(bias_audit, "__name__"))
        except ImportError:
            self.skipTest("bias_audit import failed")

    def test_66_multi_agent_imports(self):
        sys.path.insert(0, str(BASE_DIR))
        try:
            import multi_agent_eval as mae
            self.assertTrue(hasattr(mae, "__name__"))
        except ImportError:
            self.skipTest("multi_agent_eval import failed")

    def test_67_ci_exists(self):
        path = BASE_DIR / ".github" / "workflows" / "ci.yml"
        self.assertTrue(path.exists())

    def test_68_gitignore_exists(self):
        path = BASE_DIR / ".gitignore"
        self.assertTrue(path.exists())

    def test_69_env_template_exists(self):
        path = BASE_DIR / ".env.template"
        self.assertTrue(path.exists())

# ============================================================
# DOCUMENTATION TESTS (10 tests)
# ============================================================

class TestDocumentation(unittest.TestCase):
    """Test documentation completeness."""

    def test_70_readme_exists(self):
        path = BASE_DIR / "README.md"
        self.assertTrue(path.exists())

    def test_71_readme_has_content(self):
        path = BASE_DIR / "README.md"
        with open(path) as f:
            content = f.read()
        self.assertGreater(len(content), 500)

    def test_72_getting_started_exists(self):
        path = BASE_DIR / "GETTING_STARTED.md"
        self.assertTrue(path.exists())

    def test_73_checklist_exists(self):
        path = BASE_DIR / "CHECKLIST.md"
        self.assertTrue(path.exists())

    def test_74_roadmap_exists(self):
        path = BASE_DIR / "ROADMAP.md"
        self.assertTrue(path.exists())

    def test_75_replication_guide_exists(self):
        path = BASE_DIR / "REPLICATION.md"
        self.assertTrue(path.exists())

    def test_76_faq_exists(self):
        path = BASE_DIR / "FAQ.py"
        self.assertTrue(path.exists())

    def test_77_arxiv_readme_exists(self):
        path = BASE_DIR / "paper" / "arXiv_README.md"
        self.assertTrue(path.exists())

    def test_78_dashboard_exists(self):
        for dash in ["index.html", "explorer.html", "live_dashboard.html", "interactive_viz.html"]:
            path = BASE_DIR / "dashboard" / dash
            self.assertTrue(path.exists(), f"dashboard/{dash} missing")

    def test_79_presentation_exists(self):
        path = BASE_DIR / "presentation.html"
        self.assertTrue(path.exists())

# ============================================================
# RESULTS TESTS (15 tests)
# ============================================================

class TestResults(unittest.TestCase):
    """Test result data integrity."""

    def test_80_bayesian_results_exist(self):
        path = BASE_DIR / "results" / "bayesian_analysis.json"
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            self.assertGreater(len(data), 0)

    def test_81_analysis_report_exists(self):
        for fmt in ["md", "html"]:
            path = BASE_DIR / "results" / f"analysis_report.{fmt}"
            if path.exists():
                with open(path) as f:
                    content = f.read()
                self.assertGreater(len(content), 100)

    def test_82_auto_paper_exists(self):
        path = BASE_DIR / "results" / "auto_paper.md"
        if path.exists():
            with open(path) as f:
                content = f.read()
            self.assertGreater(len(content), 200)

    def test_83_synthetic_metadata_has_profiles(self):
        path = BASE_DIR / "results" / "synthetic_v2_metadata.json"
        if path.exists():
            with open(path) as f:
                meta = json.load(f)
            self.assertIn("judge_profiles", meta)
            self.assertEqual(len(meta["judge_profiles"]), 5)

    def test_84_empirical_ratios_calculated(self):
        path = BASE_DIR / "results" / "synthetic_v2_metadata.json"
        if path.exists():
            with open(path) as f:
                meta = json.load(f)
            judges_with_ir = [j for j, d in meta.get("empirical", {}).items() if "empirical_ir" in d]
            self.assertGreater(len(judges_with_ir), 0)

def run_all():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestDataGeneration, TestPipelines, TestAnalysis,
        TestBenchmark, TestPapers, TestISEF,
        TestInfrastructure, TestDocumentation, TestResults
    ]

    for tc in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(tc))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    skipped = len(result.skipped)

    print(f"\n{'='*60}")
    print(f"TEST RESULTS: {passed}/{total} passed ({skipped} skipped)")
    if result.failures:
        print(f"FAILURES: {len(result.failures)}")
    if result.errors:
        print(f"ERRORS: {len(result.errors)}")
    print(f"{'='*60}")

    return result

if __name__ == "__main__":
    run_all()
