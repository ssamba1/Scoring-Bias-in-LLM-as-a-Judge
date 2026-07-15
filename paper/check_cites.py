import re

# Read .tex file
with open(r'C:\Users\Admin\Research\research-draft\paper\camera_ready_full.tex', 'r') as f:
    tex = f.read()

# Find all \cite{...} patterns
cite_pattern = re.compile(r'\\cite\{([^}]+)\}')
cite_keys = set()
for match in cite_pattern.finditer(tex):
    content = match.group(1)
    for key in content.split(','):
        cite_keys.add(key.strip())

print('=== Cite keys from .tex ===')
for k in sorted(cite_keys):
    print(f'  {k}')

# Read .bib file
with open(r'C:\Users\Admin\Research\research-draft\paper\references.bib', 'r') as f:
    bib = f.read()

bib_pattern = re.compile(r'@\w+\{(\w+),')
bib_keys = set()
for match in bib_pattern.finditer(bib):
    bib_keys.add(match.group(1))

print()
print('=== Bib keys from .bib ===')
for k in sorted(bib_keys):
    print(f'  {k}')

# Check mismatches
in_tex_not_bib = cite_keys - bib_keys
in_bib_not_tex = bib_keys - cite_keys

print()
if in_tex_not_bib:
    print(f'!!! CITATIONS WITHOUT BIB ENTRY: {in_tex_not_bib}')
else:
    print('✓ All \\cite{} keys have matching bib entries.')

if in_bib_not_tex:
    print(f'!!! BIB ENTRIES NOT CITED: {in_bib_not_tex}')
else:
    print('✓ All bib entries are cited in the text.')
