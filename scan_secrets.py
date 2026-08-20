#!/usr/bin/env python3
"""Scan the whole git history for credentials, not just the current files.

This repository is public. Publishing a repository publishes its *history*: a
key redacted at HEAD is still served by the commit that introduced it, reachable
by SHA long after the file looks clean.

That is not hypothetical here. GitHub push protection once blocked a HuggingFace
token and two Kaggle tokens in this project, and the paths were redacted. A note
then circulated for weeks claiming the originals "remain in the public history".
When that was finally checked (2026-08-02), it was false -- every object
reachable from every ref, plus unreachable objects, was clean. The belief had
hardened into a fact by repetition and was driving a recommendation to rewrite
published history.

Both halves of that story are why this script exists. Run it before making any
repository public, and run it instead of trusting a memory of having run it.

    python scan_secrets.py [--quiet]

Values are never printed. A match reports the pattern, the blob and the path --
enough to find and remove it, without copying the secret somewhere new.
"""

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent

PATTERNS = {
    "huggingface token": rb"\bhf_[A-Za-z0-9]{30,}",
    "kaggle key (json)": rb'"key"\s*:\s*"[0-9a-f]{28,}"',
    "kaggle key (env)": rb"KAGGLE_KEY\s*[=:]\s*['\"]?[0-9a-f]{28,}",
    # Kaggle rotated to a prefixed token (KGAT_...) read from
    # ~/.kaggle/access_token or KAGGLE_API_TOKEN. The two patterns above match
    # only the legacy 28-hex key, so a token in the new format would have
    # scanned clean. Added after one was pasted into a chat window, which is
    # the likeliest way it reaches a file in the first place.
    "kaggle token (prefixed)": rb"KGAT_[A-Za-z0-9]{24,}",
    "kaggle token (env)": rb"KAGGLE_API_TOKEN\s*[=:]\s*['\"]?KGAT_[A-Za-z0-9]{8,}",
    "openrouter key": rb"sk-or-v1-[a-f0-9]{16,}",
    "openai key": rb"\bsk-[A-Za-z0-9]{32,}",
    "anthropic key": rb"\bsk-ant-[A-Za-z0-9\-]{24,}",
    "aws access key": rb"\bAKIA[0-9A-Z]{16}\b",
    "google api key": rb"\bAIza[0-9A-Za-z_\-]{35}\b",
    "github token": rb"\bgh[pousr]_[A-Za-z0-9]{36,}",
    "private key block": rb"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----",
    "generic api key": rb"api[_-]?key\s*[=:]\s*['\"][A-Za-z0-9_\-]{24,}['\"]",
}

# This file necessarily contains every pattern above.
SELF = "scan_secrets.py"


def _git(*args, binary=False):
    result = subprocess.run(
        ["git", "-C", str(BASE), *args], capture_output=True, timeout=1800
    )
    return result.stdout if binary else result.stdout.decode("utf-8", "replace")


def _refuse_shallow():
    """A shallow clone would scan one commit and report clean.

    CI checks out at depth 1 by default, so a scan there is worse than none: it
    produces a green result that means nothing. Refuse rather than mislead.
    """
    if (BASE / ".git" / "shallow").exists():
        raise SystemExit(
            "this is a shallow clone; the scan would read a truncated history and "
            "report clean. Run `git fetch --unshallow` first."
        )


def scan(quiet=False):
    _refuse_shallow()

    commits = _git("rev-list", "--count", "--all").strip()
    listing = _git("rev-list", "--objects", "--all").splitlines()
    named = {}
    for line in listing:
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            named[parts[0]] = parts[1]

    # Unreachable objects too: a rewritten branch can leave a blob that is still
    # served by SHA on the forge.
    dangling = [
        token
        for token in _git("fsck", "--lost-found", "--no-progress").split()
        if len(token) == 40 and all(c in "0123456789abcdef" for c in token)
    ]

    if not quiet:
        print(f"commits: {commits}   named objects: {len(named)}   dangling: {len(dangling)}")

    hits = defaultdict(set)
    checked = 0
    seen = set()

    def inspect(sha, path):
        nonlocal checked
        if sha in seen:
            return
        seen.add(sha)
        if _git("cat-file", "-t", sha).strip() != "blob":
            return
        data = _git("cat-file", "blob", sha, binary=True)
        if len(data) > 8_000_000:
            return
        checked += 1
        if path == SELF:
            return
        for label, pattern in PATTERNS.items():
            if re.search(pattern, data):
                hits[(label, path)].add(sha[:10])

    for sha, path in named.items():
        inspect(sha, path)
    for sha in dangling:
        kind = _git("cat-file", "-t", sha).strip()
        if kind == "blob":
            inspect(sha, "(unreachable blob)")
        elif kind in {"commit", "tree"}:
            for line in _git("ls-tree", "-r", sha).splitlines():
                parts = line.split()
                if len(parts) > 3:
                    inspect(parts[2], f"(unreachable) {' '.join(parts[3:])}")

    if not quiet:
        print(f"blobs inspected: {checked}")

    if not hits:
        print("no credential patterns in any blob, at any commit, reachable or not")
        return 0

    print("\nMATCHES (values withheld):")
    for (label, path), shas in sorted(hits.items()):
        print(f"  {label:22s} {path}   blobs: {', '.join(sorted(shas)[:4])}")
    print(
        "\nRedacting at HEAD does not remove these: the commit that introduced "
        "each one still serves it. Rotate the credential first -- that is the "
        "only step that actually revokes access -- then decide about history."
    )
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true")
    sys.exit(scan(**vars(parser.parse_args())))
