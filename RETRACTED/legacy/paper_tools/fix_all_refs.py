#!/usr/bin/env python3
"""Final comprehensive fix for all broken ref patterns."""
path = r'C:\Users\Admin\Research\research-draft\paper\camera_ready_full.tex'

with open(path, 'rb') as f:
    data = bytearray(f.read())

# The problem: JSON \r in \ref became CR (0x0D) character in the file
# So "Figure~\ref{fig:...}" became "Figure~" + 0x0D + "ef{fig:...}"
# And 0x0D next to 0x0A (LF) looks like Windows CRLF line ending

# Find all instances of "Figure~" followed soon after by "ef{"
# and "Table~" followed soon after by "ef{"
# and fix them by inserting the missing backslash

fixes = [
    (b'Figure~', b'ef{fig:domain_bias} visualizes'),
    (b'Figure~', b'ef{fig:error_analysis} examines'),
    (b'Figure~', b'ef{fig:item_analysis} examines'),
    (b'Figure~', b'ef{fig:item_discrimination} provides'),
    (b'Table~', b'ef{tab:domain} shows bias'),
]

for prefix, rest in fixes:
    # Find the pattern "prefix" + any garbage + "rest"
    idx = 0
    while True:
        # Find prefix
        pidx = data.find(prefix, idx)
        if pidx == -1:
            break
        # Look for rest within 50 bytes after prefix
        rest_start = pidx + len(prefix)
        rest_end = rest_start + min(50, len(data) - rest_start)
        chunk = data[rest_start:rest_end]
        rstart = chunk.find(rest)
        if rstart != -1:
            # Found! Replace everything between prefix and rest with \ref
            mid_len = rstart
            replacement = b'\\ref{'
            # Replace the region
            old_section = data[pidx:rest_start + rstart + len(rest)]
            new_section = prefix + replacement + rest[len('ef{'):]
            print(f'Fixing at byte {pidx}:')
            print(f'  Old ({len(old_section)}b): {old_section[:80]}')
            print(f'  New ({len(new_section)}b): {new_section[:80]}')
            data[pidx:rest_start + rstart + len(rest)] = new_section
            idx = pidx + len(new_section)
        else:
            idx = pidx + len(prefix)

with open(path, 'wb') as f:
    f.write(data)

print('\nVerifying...')
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

issues = 0
for i, line in enumerate(lines, 1):
    s = line.strip()
    if 'ef{' in s:
        if '\\ref' not in s and '\\label' not in s and 'href' not in s:
            print(f'  Line {i}: {s[:80]}')
            issues += 1

if issues == 0:
    print('All fixes applied successfully!')
else:
    print(f'{issues} issues remaining.')
