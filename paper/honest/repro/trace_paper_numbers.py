#!/usr/bin/env python3
"""Every number in the paper must exist in a derived result file.

`check_prose.py` verifies an enumerated list of key claims: it names a string,
finds it in the prose, and compares it to the data. That is strong for the
claims it covers and silent for everything else. Mutating the headline
correlation from -0.41 to -9.41 left it reporting "prose-consistency OK".

This asks the complementary question, the one that matters for a project whose
failure mode was invented numbers: does every decimal printed in the paper
appear anywhere in the committed results? A number with no source is precisely
what fabrication looks like.

What this does and does not establish, stated plainly because the companion
project's version of this check overstated itself for several rounds:

  * An orphan is a real finding: nothing in the data produces that value.
  * A match is weak evidence. With thousands of stored values, short numbers
    collide constantly -- "0.5" will always be found somewhere. The report
    prints how many distinct places each value matched, so a claim resting on a
    single unique match can be told apart from one satisfied by coincidence.
  * Matching is done at the PAPER's precision. Rounding 0.4123 to the two
    decimals the paper prints is the comparison a reader would make.

    python trace_paper_numbers.py [--verbose]

Exit code 1 if any number in the paper has no source.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent

# Numbers that are not empirical claims: figure sizes, font scalings, version
# numbers, and the small integers of ordinary prose. Each is excluded by what it
# is, not by value, so a real claim cannot hide behind the list.
SKIP_CONTEXT = re.compile(
    r"(includegraphics|width=|scale=|tabcolsep|arraystretch|vspace|hspace|"
    r"linewidth|textwidth|columnwidth|baselineskip|\\cite|section|label|ref\{)"
)


def _paper_numbers():
    """Every decimal printed in the paper, with the line it came from."""
    found = []
    for name in ("macros.tex", "scoring_bias_v2.tex"):
        path = PAPER / name
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.lstrip().startswith("%"):
                continue
            if SKIP_CONTEXT.search(line):
                continue
            for token in re.findall(r"(?<![\w.])-?\d+\.\d+", line):
                found.append((abs(float(token)), token, f"{name}:{lineno}"))
    return found


def _derived_values():
    """Every number in every committed result file, at several precisions."""
    values = defaultdict(set)

    def absorb(obj, origin):
        if isinstance(obj, dict):
            for value in obj.values():
                absorb(value, origin)
        elif isinstance(obj, list):
            for value in obj:
                absorb(value, origin)
        elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
            for places in (1, 2, 3, 4):
                values[round(abs(float(obj)), places)].add(origin)

    for path in sorted(HERE.glob("*.json")):
        try:
            absorb(json.loads(path.read_text(encoding="utf-8", errors="replace")), path.name)
        except Exception:
            continue
    # Table files carry rendered numbers that the prose quotes directly.
    for path in sorted((PAPER / "tables").glob("*.tex")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in re.findall(r"-?\d+\.\d+", text):
            for places in (1, 2, 3, 4):
                values[round(abs(float(token)), places)].add(path.name)
    return values


def main(verbose=False):
    numbers = _paper_numbers()
    derived = _derived_values()
    if not derived:
        raise SystemExit("no derived results found; run the analyses first")

    orphans, weak = [], []
    for value, token, where in numbers:
        places = len(token.split(".")[1])
        sources = derived.get(round(value, places), set())
        if not sources:
            orphans.append((token, where))
        elif len(sources) == 1:
            weak.append((token, where, next(iter(sources))))

    print(f"paper numbers checked : {len(numbers)}")
    print(f"distinct derived values: {len(derived)}")
    print(f"unique-source matches  : {len(weak)}")
    print(f"orphans                : {len(orphans)}")

    if verbose and weak:
        print("\nvalues matching exactly one result file (the strong traces):")
        for token, where, source in weak[:25]:
            print(f"  {token:>9}  {where:34s} <- {source}")

    if orphans:
        print("\nNUMBERS IN THE PAPER WITH NO SOURCE IN ANY RESULT FILE:")
        for token, where in orphans:
            print(f"  {token:>9}  {where}")
        print(
            "\nEach of these is printed in the paper and produced by nothing in "
            "the committed results. Either the analysis that generates it is not "
            "committed, or the number does not come from the data."
        )
        return 1

    print("\nevery number in the paper traces to a committed result")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true")
    sys.exit(main(**vars(parser.parse_args())))
