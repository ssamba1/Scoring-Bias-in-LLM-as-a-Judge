#!/usr/bin/env bash
# Push a Kaggle kernel with the harness pinned to the current commit.
#
# The kernel fetches paper/honest/repro/q14b_harness.py from GitHub at COMMIT
# and verifies its sha256, so the run cannot silently use a different harness
# than the one committed here. That means the commit must be PUSHED before the
# kernel runs, or the raw URL 404s.
set -euo pipefail
dir="${1:?usage: push.sh <kernel-dir>}"
sha="$(git rev-parse HEAD)"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "working tree is dirty; commit first so COMMIT names what actually runs" >&2
  exit 1
fi
if [ -n "$(git log origin/main..HEAD --oneline 2>/dev/null)" ]; then
  echo "HEAD is not pushed; the kernel would fetch a commit GitHub cannot serve" >&2
  exit 1
fi

tmp="$(mktemp -d)"
cp "$dir"/kernel-metadata.json "$tmp/"
sed "s/__COMMIT__/$sha/" "$dir/run.py" > "$tmp/run.py"
grep -q "$sha" "$tmp/run.py" || { echo "commit substitution failed" >&2; exit 1; }

echo "pushing $(basename "$dir") pinned at ${sha:0:7}"
kaggle kernels push -p "$tmp"
