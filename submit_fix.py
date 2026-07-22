import json, sys
sys.path.insert(0, r'C:\Users\Admin\Research\research-draft')
from infrastructure.kaggle_auto import *
KAGGLE_USERNAME = 'sricharansamba'

# Load the final verified notebook
with open(r'C:\Users\Admin\Research\research-draft\infrastructure\scoring_bias_final_colab.ipynb') as f:
    nb = json.load(f)

cells = [''.join(c.get('source', [])) for c in nb['cells']]

ok = write_and_submit('sb-t4-fix', cells)
print(f'Submit: {ok}')
print(f'URL: https://www.kaggle.com/code/sricharansamba/sb-t4-fix')
