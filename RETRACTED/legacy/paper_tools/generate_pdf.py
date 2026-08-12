#!/usr/bin/env python3
"""Generate publication-quality camera-ready PDF.
Creates proper two-column HTML → print to PDF from browser.
Uses the existing camera_ready.tex content with better formatting.
"""
import re
from pathlib import Path

BASE = Path(__file__).parent
TEX = BASE / "camera_ready.tex"
OUT = BASE / "camera_ready_publishable.html"

with open(TEX) as f:
    tex = f.read()

# ── Convert LaTeX to well-formatted HTML ──
def latex_to_html(latex):
    """Convert LaTeX paper to two-column publication-quality HTML."""
    
    # Extract title
    title = re.search(r'\\title\{(.*?)\}', latex).group(1) if re.search(r'\\title\{(.*?)\}', latex) else "Title"
    title = title.replace('\\\\', '<br>')
    
    # Extract abstract
    abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', latex, re.DOTALL)
    abstract = abstract.group(1).strip() if abstract else ""
    abstract = clean_text(abstract)
    
    # Extract sections
    sections = re.findall(r'\\(?:section|subsection)\*?\{(.*?)\}', latex)
    
    # Extract body
    body = latex.split(r'\begin{document}')[1].split(r'\end{document}')[0] if r'\begin{document}' in latex else latex
    
    # Remove abstract (already extracted)
    body = re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}', '', body, flags=re.DOTALL)
    
    # Remove bibliography
    biblio = ""
    if r'\begin{thebibliography}' in body:
        bib_match = re.search(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}', body, re.DOTALL)
        if bib_match:
            biblio_raw = bib_match.group(0)
            biblio = convert_bibliography(biblio_raw)
            body = body.replace(bib_match.group(0), '<!-- BIBLIOGRAPHY -->')
    
    # Remove maketitle
    body = body.replace(r'\maketitle', '')
    
    # Convert sections
    body = re.sub(r'\\section\{(.*?)\}', r'<h2>\1</h2>', body)
    body = re.sub(r'\\subsection\{(.*?)\}', r'<h3>\1</h3>', body)
    
    # Convert environments
    body = re.sub(r'\\begin\{itemize\}(.*?)\\end\{itemize\}', 
                  lambda m: '<ul>' + re.sub(r'\\item\s+', '<li>', m.group(1)) + '</ul>', body, flags=re.DOTALL)
    body = re.sub(r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}', 
                  lambda m: '<ol>' + re.sub(r'\\item\s+', '<li>', m.group(1)) + '</ol>', body, flags=re.DOTALL)
    
    # Convert formatting
    body = re.sub(r'\\textbf\{(.*?)\}', r'<strong>\1</strong>', body)
    body = re.sub(r'\\emph\{(.*?)\}', r'<em>\1</em>', body)
    body = re.sub(r'\\textit\{(.*?)\}', r'<i>\1</i>', body)
    body = re.sub(r'\$([^$]+)\$', r'<span class="math">\(\1\)</span>', body)
    
    # Convert citations
    body = re.sub(r'\\cite\{([^}]+)\}', lambda m: f'<sup class="cite">[{m.group(1).split(",")[0].strip()}]</sup>', body)
    
    # Convert references
    body = re.sub(r'\\label\{(.*?)\}', '', body)
    body = re.sub(r'\\ref\{(.*?)\}', r'[\1]', body)
    
    # Convert URLs
    body = re.sub(r'\\url\{(.*?)\}', r'<a href="\1">\1</a>', body)
    
    # Convert paragraphs
    body = re.sub(r'\n\n+', '</p><p>', body)
    body = re.sub(r'\n', ' ', body)
    
    # Clean remaining LaTeX commands
    body = re.sub(r'\\[a-zA-Z]+\*?\{[^}]*\}', '', body)
    body = re.sub(r'\\[a-zA-Z]+\*?', '', body)
    body = re.sub(r'\{|\}', '', body)
    body = re.sub(r'~', ' ', body)
    body = re.sub(r'\\textasciitilde', '~', body)
    
    # Handle tables
    body = re.sub(r'\\begin\{table\}.*?\\end\{table\}', '[TABLE]', body, flags=re.DOTALL)
    body = re.sub(r'\\begin\{tabular\}.*?\\end\{tabular\}', '[TABLE CONTENT]', body, flags=re.DOTALL)
    
    # Handle comments
    body = re.sub(r'%.*?\n', '', body)
    
    return clean_text(body), biblio, clean_text(abstract)

def clean_text(text):
    """Remove LaTeX artifacts."""
    text = text.replace('``', '"').replace("''", '"')
    text = text.replace('---', '').replace('--', '–')
    text = text.replace("\\'", "'").replace("\\`", "`")
    text = re.sub(r' +', ' ', text)
    return text.strip()

def convert_bibliography(bib):
    """Convert thebibliography to HTML."""
    entries = re.findall(r'\\bibitem\{([^}]*)\}(.*?)(?=\\bibitem|$)', bib, re.DOTALL)
    html = '<div class="references"><h2>References</h2><ol>'
    for key, content in entries:
        ref = clean_text(content)
        html += f'<li id="ref-{key}">{ref}</li>'
    html += '</ol></div>'
    return html

body_html, biblio_html, abstract = latex_to_html(tex)

# ── Assemble full HTML ──
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Where Does Scoring Bias Come From?  Camera Ready</title>
<style>
@page {{ size: letter; margin: 0.75in; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ 
    font-family: 'Times New Roman', 'Georgia', Times, serif; 
    font-size: 10pt; line-height: 1.35; color: #000; background: #fff;
    column-count: 2; column-gap: 0.5in;
    padding: 0.75in; max-width: 8.5in; margin: auto;
}}
h1 {{ 
    font-size: 16pt; text-align: center; margin-bottom: 4pt; font-weight: bold;
    column-span: all;
}}
.authors {{ 
    text-align: center; font-size: 10pt; margin-bottom: 2pt;
    column-span: all;
}}
.affiliation {{
    text-align: center; font-size: 9pt; color: #444; margin-bottom: 10pt;
    column-span: all;
}}
.abstract {{ 
    background: #f8f9fa; border: 1px solid #dee2e6; padding: 10pt 12pt; 
    margin: 0 0 12pt 0; font-size: 9pt; line-height: 1.4;
    column-span: all;
}}
.abstract h2 {{ font-size: 10pt; text-transform: uppercase; text-align: center; margin-bottom: 6pt; letter-spacing: 1pt; }}
h2 {{ font-size: 11pt; margin: 12pt 0 4pt 0; font-weight: bold; break-after: avoid; }}
h3 {{ font-size: 10pt; margin: 8pt 0 3pt 0; font-weight: bold; font-style: italic; break-after: avoid; }}
p {{ margin-bottom: 6pt; text-align: justify; text-indent: 0; }}
ul, ol {{ margin: 3pt 0 3pt 18pt; }}
li {{ margin-bottom: 1pt; }}
.math {{ font-family: 'Times New Roman', serif; font-style: italic; }}
.cite {{ font-size: 8pt; color: #2563eb; cursor: pointer; }}
strong {{ font-weight: bold; }}
em {{ font-style: italic; }}
a {{ color: #2563eb; text-decoration: none; }}
.references {{ column-span: all; margin-top: 16pt; border-top: 1px solid #000; padding-top: 8pt; }}
.references h2 {{ font-size: 11pt; text-align: center; }}
.references ol {{ font-size: 8pt; line-height: 1.3; }}
.references li {{ margin-bottom: 2pt; }}
.table-placeholder {{ 
    background: #f8f9fa; border: 1px dashed #adb5bd; padding: 20pt; 
    text-align: center; margin: 10pt 0; font-size: 9pt; color: #6c757d;
}}
table {{ 
    width: 100%; border-collapse: collapse; font-size: 8pt; margin: 6pt 0;
}}
th, td {{ padding: 4pt 6pt; text-align: left; border-bottom: 1px solid #dee2e6; }}
th {{ font-weight: bold; background: #f8f9fa; }}
.note {{ font-size: 8pt; color: #6c757d; font-style: italic; margin-top: 4pt; }}
</style>
</head>
<body>

<h1>Where Does Scoring Bias Come From?</h1>
<p class="authors">Author Name¹, Author Name¹</p>
<p class="affiliation">¹Department of Computer Science, School/Institution<br>
Email: {{author1,author2}}@institution.edu</p>

<div class="abstract">
<h2>Abstract</h2>
<p>{abstract}</p>
</div>

<p>{body_html}</p>

<!-- Static tables (replace with auto-generated when data arrives) -->
<div class="table-placeholder">
<strong>Table 1:</strong> Main Results  Aggregate across 44 model families<br>
<span class="note">Data from Kaggle experiment (running).</span>
</div>

<div class="table-placeholder">
<strong>Table 2:</strong> Per-Family Comparison<br>
<span class="note">Data from Kaggle experiment (running).</span>
</div>

<div class="table-placeholder">
<strong>Table 3:</strong> Comparison with Li et al. (2025)<br>
<span class="note">Data from Kaggle experiment (running).</span>
</div>

{biblio_html}

<p class="note" style="column-span:all;text-align:center;margin-top:12pt">
Generated on {__import__('time').strftime('%B %d, %Y')}.
Open in browser → Ctrl+P → Save as PDF for camera-ready copy.
</p>

</body>
</html>"""

with open(OUT, "w") as f:
    f.write(html)
print(f"Generated: {OUT}")
print(f"To get PDF: Open {OUT.name} in browser → Ctrl+P → Save as PDF")
print(f"Page size: Letter, two-column, 10pt Times New Roman")
