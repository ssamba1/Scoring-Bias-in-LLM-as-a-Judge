with open('paper/camera_ready_full.tex', 'r') as f:
    content = f.read()
opens = content.count('{')
closes = content.count('}')
print(f'Open braces: {opens}, Close braces: {closes}, Diff: {opens-closes}')
starts = content.count(r'\begin{')
ends = content.count(r'\end{')
print(f'\\begin{{}}: {starts}, \\end{{}}: {ends}, Diff: {starts-ends}')
