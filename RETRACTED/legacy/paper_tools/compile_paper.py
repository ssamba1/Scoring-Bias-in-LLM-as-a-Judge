#!/usr/bin/env python3
"""Paper compilation script  assembles all paper sections into a single document.
Usage: python3 compile_paper.py --option 2 --format md
"""
import argparse, os, datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
PAPER_DIR = BASE_DIR  # compile_paper.py is in the paper/ directory
    
def compile_option2_md():
    """Compile the Option 2 paper from sections."""
    sections = [
        ("title_authors.md", None),  # Will generate
        ("abstract.md", None),
        ("1_introduction.md", None),
        ("2_related_work.md", None),
        ("3_methodology.md", None),
        ("4_results.md", None),
        ("5_discussion.md", None),
        ("6_conclusion.md", None),
        ("references.md", None),
        ("appendix.md", None),
    ]
    
    # Single file already exists as paper_biasinteraction.md
    path = PAPER_DIR / "paper_biasinteraction.md"
    if path.exists():
        with open(path) as f:
            content = f.read()
        return content
    
    return "# Paper not found  use paper_biasinteraction.md directly"

def compile_option1_md():
    path = PAPER_DIR / "paper_rootcause.md"
    if path.exists():
        with open(path) as f:
            content = f.read()
        return content
    return "# Paper not found  use paper_rootcause.md directly"

def extract_sections(md_content):
    """Extract sections from markdown for HTML conversion."""
    sections = []
    current_section = {"heading": "Title", "content": []}
    
    for line in md_content.split("\n"):
        if line.startswith("## "):
            sections.append(current_section)
            current_section = {"heading": line[3:].strip(), "content": []}
        else:
            current_section["content"].append(line)
    
    sections.append(current_section)
    return sections

def convert_to_html(md_content, title="Research Paper"):
    """Convert markdown paper to simple HTML."""
    html = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        f"<title>{title}</title>",
        "<style>",
        "body{font-family:Georgia,serif;max-width:800px;margin:auto;padding:40px 20px;line-height:1.6;color:#333}",
        "h1{font-size:2em;text-align:center;margin-bottom:5px}",
        "h2{font-size:1.5em;margin-top:30px;border-bottom:1px solid #ddd;padding-bottom:5px}",
        "h3{font-size:1.2em;margin-top:20px}",
        "p{text-align:justify;margin:10px 0}",
        "table{border-collapse:collapse;width:100%;margin:15px 0}",
        "th,td{border:1px solid #ccc;padding:8px;text-align:left}",
        "th{background:#f0f0f0}",
        "code{background:#f4f4f4;padding:2px 5px;border-radius:3px;font-size:0.9em}",
        "pre{background:#f8f8f8;padding:15px;border-radius:5px;overflow-x:auto}",
        ".abstract{font-style:italic;margin:20px 0;padding:15px;background:#f9f9f9;border-left:3px solid #4CAF50}",
        ".references{font-size:0.9em}",
        "@media print{body{font-size:12pt}}",
        "</style></head><body>"
    ]
    
    sections = extract_sections(md_content)
    
    for section in sections:
        content = "\n".join(section["content"])
        
        if section["heading"] == "Title":
            # Find title (first # line)
            for line in section["content"]:
                if line.startswith("# ") and not line.startswith("## "):
                    html.append(f"<h1>{line[2:]}</h1>")
                    break
            # Check for abstract
            if "abstract" in content.lower():
                abstract_text = content.split("abstract", 1)[-1].strip()
                # Get first paragraph
                abstract_text = abstract_text.split("\n\n")[0]
                html.append(f"<div class='abstract'><strong>Abstract:</strong> {abstract_text}</div>")
        else:
            html.append(f"<h2>{section['heading']}</h2>")
            
            # Process content
            in_table = False
            in_code = False
            for line in section["content"]:
                stripped = line.strip()
                
                if stripped.startswith("```"):
                    if in_code:
                        html.append("</pre>")
                        in_code = False
                    else:
                        html.append("<pre><code>")
                        in_code = True
                    continue
                
                if in_code:
                    html.append(line + "\n")
                    continue
                
                if stripped.startswith("| ") and "|" in stripped[2:]:
                    if not in_table:
                        html.append("<table>")
                        in_table = True
                    cells = [c.strip() for c in stripped.split("|")[1:-1]]
                    if all(c == "---" for c in cells):
                        continue
                    html.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
                else:
                    if in_table:
                        html.append("</table>")
                        in_table = False
                    
                    if stripped == "":
                        html.append("<br>")
                    elif stripped.startswith("- "):
                        html.append(f"<li>{stripped[2:]}</li>")
                    elif stripped.startswith("1. ") or stripped.startswith("2. "):
                        html.append(f"<li>{stripped[3:]}</li>")
                    elif "**" in stripped:
                        html.append(f"<p>{stripped}</p>")
                    elif stripped:
                        html.append(f"<p>{stripped}</p>")
            
            if in_table:
                html.append("</table>")
    
    html.append("</body></html>")
    return "\n".join(html)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--option", type=int, choices=[1, 2], default=2)
    parser.add_argument("--format", choices=["md", "html", "both"], default="both")
    args = parser.parse_args()
    
    if args.option == 2:
        md = compile_option2_md()
        base_name = "paper_biasinteraction"
    else:
        md = compile_option1_md()
        base_name = "paper_rootcause"
    
    if args.format in ("md", "both"):
        out_path = os.path.join(PAPER_DIR, f"{base_name}_compiled.md")
        with open(out_path, "w") as f:
            f.write(md)
        print(f"Markdown: {out_path}")
    
    if args.format in ("html", "both"):
        html = convert_to_html(md, f"Research Paper  {'Bias Interaction' if args.option == 2 else 'Root Cause'}")
        out_path = os.path.join(PAPER_DIR, f"{base_name}_compiled.html")
        with open(out_path, "w") as f:
            f.write(html)
        print(f"HTML:     {out_path}")
    
    print(f"\nPaper compiled successfully!")
    print(f"Word count: ~{len(md.split())} words")

if __name__ == "__main__":
    main()
