#!/usr/bin/env bash
# Push a Kaggle kernel with the harness pinned to the current commit AND to the
# digest of the exact bytes GitHub will serve for it.
#
# The kernel downloads paper/honest/repro/q14b_harness.py from the raw URL and
# refuses to run unless its sha256 matches. That turns "pinned" from a comment
# into a check: a raw URL resolving to anything else stops the run instead of
# producing numbers attributed to a commit that did not generate them.
#
# The digest is taken from `git show HEAD:<path>` -- the stored blob -- not from
# the working file. This repository checks out CRLF on Windows and GitHub serves
# what git stores, which is LF, so hashing the working copy yields a digest that
# can never match.
set -euo pipefail

dir="${1:?usage: push.sh <kernel-dir>}"
harness="paper/honest/repro/q14b_harness.py"
sha="$(git rev-parse HEAD)"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "working tree is dirty; commit first so COMMIT names what actually runs" >&2
  exit 1
fi
if [ -n "$(git log origin/main..HEAD --oneline 2>/dev/null)" ]; then
  echo "HEAD is not pushed; the kernel would fetch a commit GitHub cannot serve" >&2
  exit 1
fi

digest="$(git show "HEAD:$harness" | sha256sum | cut -d' ' -f1)"

tmp="$(mktemp -d)"
cp "$dir/kernel-metadata.json" "$tmp/"
sed -e "s/__COMMIT__/$sha/" -e "s/__SHA256__/$digest/" "$dir/run.py" > "$tmp/run.py"
grep -q "$sha" "$tmp/run.py" || { echo "commit substitution failed" >&2; exit 1; }
grep -q "$digest" "$tmp/run.py" || { echo "digest substitution failed" >&2; exit 1; }
grep -q "__COMMIT__\|__SHA256__" "$tmp/run.py" && {
  echo "a placeholder survived substitution" >&2; exit 1; }

# Confirm the raw URL already serves those exact bytes, before spending a
# session on a kernel that would refuse to run.
url="https://raw.githubusercontent.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge/$sha/$harness"
served="$(curl -sSf "$url" | sha256sum | cut -d' ' -f1)"
if [ "$served" != "$digest" ]; then
  echo "raw URL serves $served, expected $digest" >&2
  exit 1
fi

echo "pushing $(basename "$dir")"
echo "  commit ${sha:0:7}  digest ${digest:0:16}...  (verified live)"
kaggle kernels push -p "$tmp"
