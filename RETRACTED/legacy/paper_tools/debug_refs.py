#!/usr/bin/env python3
"""Debug broken patterns and fix them."""
path = r'C:\Users\Admin\Research\research-draft\paper\camera_ready_full.tex'

with open(path, 'rb') as f:
    data = f.read()

# Find all occurrences of 'ef{'
idx = 0
count = 0
while True:
    idx = data.find(b'ef{', idx)
    if idx == -1:
        break
    start = max(0, idx - 30)
    end = min(len(data), idx + 30)
    chunk = data[start:end]
    count += 1
    print('Match %d at byte %d:' % (count, idx))
    print('  Hex: ' + chunk.hex())
    # Try to print as text, replacing non-ASCII
    text = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
    print('  Text: ' + text)
    idx += 1

# Now fix: replace broken patterns in binary mode
# Pattern: Figure~\r\nef{fig:...} -> Figure~\ref{fig:...}
# The \ref got split such that \r in CRLF consumed the \ backslash
# So we have: Figure~ + \r\n + ef{fig:...}
# which means Figure~ + CR + LF + ef{fig:...}

import re

# Fix binary-level: replace Figure~\r\nef with Figure~\ref
data = data.replace(b'Figure~\r\nef{', b'Figure~\\ref{')
data = data.replace(b'Table~\r\nef{', b'Table~\\ref{')

with open(path, 'wb') as f:
    f.write(data)

print('\nFixed. Checking for remaining ef{ without \\ref prefix...')

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines, 1):
    s = line.strip()
    if 'ef{' in s and '\\ref' not in s and 'label' not in s:
        print('  Line %d: %s' % (i, s[:60]))
