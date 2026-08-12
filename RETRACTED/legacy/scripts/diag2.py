import json

paths = [
    r'C:\Users\Admin\Research\research-draft\infrastructure\kaggle_kernels\simple-struct-test\simple-struct-test.ipynb',
    r'C:\Users\Admin\Research\research-draft\infrastructure\kaggle_kernels\f-sb-v8\f-sb-v8.ipynb',
]

for path in paths:
    with open(path) as f:
        nb = json.load(f)

    name = path.rsplit('\\', 1)[-1]
    print(f'=== {name} ===')
    print(f'  nbformat: {nb.get("nbformat")}')
    print(f'  nbformat_minor: {nb.get("nbformat_minor")}')
    meta = nb.get('metadata', {})
    print(f'  metadata keys: {list(meta.keys())}')
    ks = meta.get('kernelspec', {})
    print(f'  kernelspec: {ks}')
    li = meta.get('language_info', {})
    print(f'  language_info keys: {list(li.keys())}')
    print(f'  kaggle present: {"kaggle" in meta}')
    print()
