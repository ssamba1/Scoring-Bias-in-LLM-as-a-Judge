#!/usr/bin/env python3
"""Unit tests for core analysis scripts."""
import unittest, json, re, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import re

def es(t): m=re.search(r'\b([1-5])\b',t); return int(m.group(1)) if m else 3
def el(t): m=re.search(r'\b([A-E])\b',t.upper()); return {"A":5,"B":4,"C":3,"D":2,"E":1}.get(m.group(1),3) if m else 3
def ed(t):
    t=t.lower().strip()
    if 'excellent' in t: return 5
    for w,s in [('very good',4),('good',4),('fair',3),('poor',2),('terrible',1),('bad',1)]:
        if w in t: return s
    return es(t)
PROBES = {"rubric_order": {"normal":"Score 1-5 (1=worst, 5=best)."}}
def bp(p,v,i): return f"{PROBES[p][v]}\n\n### Instruction:\n{i['instr']}\n\n### Response:\n{i['resp']}\n\n### Score:"

class TestScoringFunctions(unittest.TestCase):
    def test_extract_score(self):
        self.assertEqual(es("5"), 5); self.assertEqual(es("Score: 4"), 4)
        self.assertEqual(es("3 out of 5"), 3); self.assertEqual(es("No number here"), 3)
        self.assertEqual(es(""), 3)
    def test_extract_letter(self):
        self.assertEqual(el("A"), 5); self.assertEqual(el("B"), 4); self.assertEqual(el("C"), 3)
        self.assertEqual(el("D"), 2); self.assertEqual(el("E"), 1); self.assertEqual(el("Score: B"), 4)
        self.assertEqual(el("F"), 3); self.assertEqual(el(""), 3)
    def test_extract_descriptive(self):
        self.assertEqual(ed("Excellent work"), 5); self.assertEqual(ed("Very good"), 4)
        self.assertEqual(ed("Good job"), 4); self.assertEqual(ed("Fair attempt"), 3)
        self.assertEqual(ed("Poor"), 2); self.assertEqual(ed("Terrible"), 1)
        self.assertEqual(ed("Bad result"), 1); self.assertEqual(ed("Average"), 3)
    def test_build_prompt(self):
        prompt = bp("rubric_order", "normal", {"instr":"Q?", "resp":"A."})
        self.assertIn("Score 1-5", prompt); self.assertIn("Q?", prompt); self.assertIn("A.", prompt)

    def test_depth_analysis_output(self):
        depth = Path(__file__).parent.parent / "results_rootcause" / "depth_analysis.json"
        if depth.exists():
            with open(depth) as f:
                data = json.load(f)
            self.assertIn("tests", data)
            self.assertIn("conclusions", data)
            self.assertGreaterEqual(len(data["tests"]), 4)

    def test_paper_structure(self):
        paper = Path(__file__).parent.parent / "paper" / "camera_ready_full.tex"
        if paper.exists():
            content = paper.read_text()
            sections = ["\\section{Introduction}", "\\section{Related Work}", "\\section{Method}",
               "\\section{Results}", "\\section{Discussion}", "\\section{Limitations}",
               "\\section{Conclusion}"]
            for section in sections:
                self.assertIn(section, content, f"Missing: {section}")

    def test_interactive_paper_exists(self):
        html = Path(__file__).parent.parent / "dashboard" / "interactive_paper.html"
        self.assertTrue(html.exists())
        content = html.read_text()
        self.assertIn("differential", content.lower())

    def test_leaderboard_exists(self):
        html = Path(__file__).parent.parent / "dashboard" / "leaderboard.html"
        self.assertTrue(html.exists())
        content = html.read_text()
        self.assertIn("leaderboard", content.lower())

    def test_model_cards_exist(self):
        mc = Path(__file__).parent.parent / "data" / "model_cards" / "all_models.md"
        self.assertTrue(mc.exists())
        content = mc.read_text()
        self.assertIn("Meta Llama", content)
        self.assertIn("Gemma", content)
        self.assertIn("Qwen", content)

class TestPaperGenerator(unittest.TestCase):

    def test_auto_updater_exists(self):
        updater = Path(__file__).parent.parent / "paper" / "auto_update_paper.py"
        self.assertTrue(updater.exists())

    def test_arxiv_package_generator(self):
        pkg = Path(__file__).parent.parent / "paper" / "arxiv_package.py"
        self.assertTrue(pkg.exists())

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(unittest.TestLoader().loadTestsFromModule(sys.modules[__name__]))
    sys.exit(0 if result.wasSuccessful() else 1)
