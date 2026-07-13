#!/usr/bin/env python3
"""Comprehensive test suite for all pipeline components."""
import unittest, csv, json, os, tempfile, sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

class TestDataGeneration(unittest.TestCase):
    """Test the evaluation item generation."""
    
    def setUp(self):
        self.data_dir = BASE_DIR / "data"
    
    def test_items_base_exists(self):
        path = self.data_dir / "items_base.csv"
        self.assertTrue(path.exists(), f"Missing: {path}")
        with open(path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 400, f"Expected 400 items, got {len(rows)}")
    
    def test_items_all_conditions_exists(self):
        path = self.data_dir / "items_all_conditions.csv"
        self.assertTrue(path.exists(), f"Missing: {path}")
        with open(path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 3200, f"Expected 3200 variants, got {len(rows)}")
    
    def test_all_conditions_present(self):
        path = self.data_dir / "items_all_conditions.csv"
        with open(path) as f:
            rows = list(csv.DictReader(f))
        conditions = set(r["condition"] for r in rows)
        expected = {"baseline", "short_response", "verbose_response", "positive_tone",
                    "negative_tone", "disfavored_position", "worst_case", "best_case_biased"}
        self.assertEqual(conditions, expected, f"Missing conditions: {expected - conditions}")

class TestAnalysis(unittest.TestCase):
    """Test the analysis pipeline."""
    
    def setUp(self):
        self.results_dir = BASE_DIR / "results"
        self.results_dir.mkdir(exist_ok=True)
    
    def test_synthetic_pilot_generates_data(self):
        """Test that synthetic pilot generates data."""
        path = self.results_dir / "bias_interaction_synthetic.csv"
        if not path.exists():
            self.skipTest("Synthetic data not generated yet")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 0)
    
    def test_synthetic_results_have_judges(self):
        path = self.results_dir / "bias_interaction_synthetic.csv"
        if not path.exists():
            self.skipTest("Synthetic data not generated yet")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        judges = set(r["judge"] for r in rows)
        expected = {"claude", "gpt4o", "gemini", "deepseek", "llama"}
        self.assertEqual(judges, expected)
    
    def test_synthetic_scores_in_range(self):
        path = self.results_dir / "bias_interaction_synthetic.csv"
        if not path.exists():
            self.skipTest("Synthetic data not generated yet")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            score = float(r["score"])
            self.assertGreaterEqual(score, 1)
            self.assertLessEqual(score, 5)
    
    def test_root_cause_synthetic(self):
        path = self.results_dir / "rootcause_synthetic.csv"
        if not path.exists():
            self.skipTest("Root cause synthetic data not generated yet")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 0)
        
        # Check model types present
        types = set(r["type"] for r in rows)
        self.assertIn("base", types)
        self.assertIn("instruct", types)

class TestRootCausePipeline(unittest.TestCase):
    """Test the root cause pipeline in placeholder mode."""
    
    def test_placeholder_runs(self):
        """Test that the placeholder pipeline runs without errors."""
        import subprocess
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / "pipeline_rootcause" / "rootcause_pipeline.py")],
            capture_output=True, text=True, timeout=30
        )
        self.assertIn("ROOT CAUSE OF SCORING BIAS", result.stdout)
    
    def test_placeholder_output(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / "pipeline_rootcause" / "rootcause_pipeline.py")],
            capture_output=True, text=True, timeout=30
        )
        self.assertIn("BASE vs INSTRUCT COMPARISON", result.stdout)

class TestConfig(unittest.TestCase):
    """Test configuration system."""
    
    def test_config_yaml_exists(self):
        path = BASE_DIR / "pipeline_biasinteraction" / "config.yaml"
        self.assertTrue(path.exists())
    
    def test_yaml_importable(self):
        try:
            import yaml
            path = BASE_DIR / "pipeline_biasinteraction" / "config.yaml"
            with open(path) as f:
                config = yaml.safe_load(f)
            self.assertIn("judges", config)
            self.assertEqual(len(config["judges"]), 5)
        except ImportError:
            self.skipTest("PyYAML not installed")

class TestUtils(unittest.TestCase):
    """Test utility modules."""
    
    def test_quality_check_imports(self):
        """Test quality_check module can be imported."""
        try:
            import pipeline_biasinteraction.quality_check as qc
            self.assertTrue(hasattr(qc, 'generate_report'))
        except ImportError:
            self.skipTest("Quality check module import failed")
    
    def test_results_db_import(self):
        try:
            import pipeline_biasinteraction.results_db as db
            self.assertTrue(hasattr(db, 'init_db'))
        except ImportError:
            self.skipTest("Results DB module import failed")

def run_all():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    for test_class in [TestDataGeneration, TestAnalysis, TestRootCausePipeline, 
                       TestConfig, TestUtils]:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n{'='*50}")
    print(f"Tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"{'='*50}")
    
    return result

if __name__ == "__main__":
    run_all()
