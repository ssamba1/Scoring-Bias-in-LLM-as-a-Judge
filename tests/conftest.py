"""Make the shared helpers importable without installing the package.

`fabricated_signatures` holds the retraction vocabulary that several guards need.
Adding this directory to the path keeps those imports plain, and keeps the
strings in exactly one file -- which matters here, because a guard that spells
out the fabricated names trips the sweep that searches for them.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
