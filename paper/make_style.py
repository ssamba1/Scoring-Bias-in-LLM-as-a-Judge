#!/usr/bin/env python3
"""NeurIPS style file for the paper. 
Place in same directory as the .tex file and compile with:
  pdflatex paper_neurips_style.tex
"""
STYLE_CONTENT = r"""
%%%% NIPS Style for paper
\makeatletter
\def\aclfmt@name{ACL 2026}
\def\aclfmt@issn{}
\makeatother

\setlength\paperwidth{21.6cm}
\setlength\paperheight{27.9cm}
\setlength\topmargin{0cm}
\setlength\oddsidemargin{0cm}
\setlength\evensidemargin{0cm}
\setlength\textwidth{16cm}
\setlength\textheight{23cm}
\setlength\columnsep{1cm}

\newcommand{\citet}[1]{\citeauthor{#1}~\cite{#1}}
\newcommand{\citep}[1]{\cite{#1}}
\newcommand{\citeauthor}[1]{\textsc{#1}}
"""
with open(__file__.replace('.py', '.sty'), 'w') as f:
    f.write(STYLE_CONTENT)
print("Created: acl_natbib.sty")
