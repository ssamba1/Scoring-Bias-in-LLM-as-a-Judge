import json, re, sys

path = r'C:\Users\Admin\Research\research-draft\infrastructure\scoring_bias_final_colab.ipynb'
with open(path) as f:
    nb = json.load(f)

for i in range(min(7, len(nb['cells']))):
    src = ''.join(nb['cells'][i]['source'])
    lines = nb['cells'][i]['source']

    issues = []

    # Check for unterminated backslash at end of source lines
    for j, line in enumerate(lines):
        # A source line ending with single \n is normal (JSON newline)
        # But make sure they all end properly
        pass

    # Check if the source starts with code or has issues
    first_line = lines[0] if lines else ''
    last_line = lines[-1] if lines else ''

    # Count various problematic patterns
    bs_count = sum(1 for l in lines if '\\\\' in l)
    fn_count = sum(1 for l in lines if '\\n' in l)

    print(f"Cell {i}: {len(lines)} lines, {len(src)} chars")
    print(f"  First: {first_line.strip()[:80]}...")
    print(f"  Has backslashes: {bs_count}, Has escaped newlines: {fn_count}")

    # Check for trailing content issues in JSON
    cell_keys = list(nb['cells'][i].keys())
    print(f"  Keys: {cell_keys}")
    print()
