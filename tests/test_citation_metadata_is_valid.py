r"""Is the machine-readable citation record actually valid?

CITATION.cff is the metadata that travels furthest: GitHub's citation widget
reads it, and Zenodo reads it when minting a DOI. It is also the file nobody
looks at again after writing it once, and an invalid one does not announce
itself -- the widget simply shows nothing.

This one was invalid. It carried `orcid: ""` as a top-level key. An ORCID is a
property of a person, so it belongs to an entry under `authors`; at the top
level the CFF 1.2.0 schema rejects it outright, because the schema sets
additionalProperties: false. The file parsed as YAML perfectly well, which is
why it looked fine -- the companion projects had the same class of defect
through a different mechanism (unclosed quote, so not even YAML).

Validating properly needs the schema, and cffconvert is not installed in the
environment that runs these tests. So the top-level key set from CFF 1.2.0 is
checked directly, which is what caught this, and cffconvert is used as well when
it happens to be available.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CFF = REPO / "CITATION.cff"

# Top-level properties permitted by CFF 1.2.0. The schema allows nothing else.
ALLOWED_TOP_LEVEL = {
    "abstract", "authors", "cff-version", "commit", "contact", "date-released",
    "doi", "identifiers", "keywords", "license", "license-url", "message",
    "preferred-citation", "references", "repository", "repository-artifact",
    "repository-code", "title", "type", "url", "version",
}

# Properties of a person; these are the ones misplaced at the top level.
PERSON_ONLY = {"orcid", "family-names", "given-names", "affiliation", "email", "name-particle"}


def _text():
    if not CFF.exists():
        pytest.skip("[metadata] CITATION.cff not present")
    return CFF.read_text(encoding="utf-8", errors="replace")


def _top_level_keys():
    """Keys at indentation zero, ignoring comments and list items."""
    keys = []
    for line in _text().splitlines():
        if not line.strip() or line.lstrip().startswith("#") or line[:1].isspace():
            continue
        m = re.match(r"([A-Za-z0-9_-]+)\s*:", line)
        if m:
            keys.append(m.group(1))
    return keys


def test_no_person_property_sits_at_the_top_level():
    misplaced = sorted(set(_top_level_keys()) & PERSON_ONLY)
    assert not misplaced, (
        f"{misplaced} describe a person and must be indented under an entry in "
        f"`authors`. At the top level the CFF 1.2.0 schema rejects the file, so "
        f"GitHub and Zenodo ignore the whole record."
    )


def test_every_top_level_key_is_in_the_schema():
    unknown = sorted(set(_top_level_keys()) - ALLOWED_TOP_LEVEL)
    assert not unknown, (
        f"top-level key(s) {unknown} are not in CFF 1.2.0, which sets "
        f"additionalProperties: false -- the record will not validate"
    )


def test_it_validates_against_the_real_schema_when_that_is_possible():
    """Belt and braces: run the actual validator wherever it is installed."""
    try:
        from cffconvert import Citation
    except ImportError:
        pytest.skip("[cffconvert] not installed; key-set check above still applies")
    Citation(_text()).validate()


def test_the_archived_doi_matches_the_one_the_paper_cites():
    """A citation record pointing at a different archive than the paper is worse than none."""
    paper = REPO / "paper" / "honest" / "scoring_bias_v2.tex"
    if not paper.exists():
        pytest.skip("[paper] scoring_bias_v2.tex not present")
    in_paper = set(re.findall(r"10\.5281/zenodo\.\d+", paper.read_text(encoding="utf-8", errors="replace")))
    in_cff = set(re.findall(r"10\.5281/zenodo\.\d+", _text()))
    cited_cff = {d for d in in_cff if re.search(r"^doi:\s*" + re.escape(d), _text(), re.M)}
    assert cited_cff <= in_paper or not in_paper, (
        f"CITATION.cff cites {cited_cff} but the paper cites {in_paper}"
    )


def test_the_retracted_record_is_not_the_one_being_advertised():
    """The superseded Zenodo record may be named as retracted, never as the DOI."""
    text = _text()
    m = re.search(r"^doi:\s*(\S+)", text, re.M)
    assert m, "CITATION.cff declares no DOI"
    assert "21361920" not in m.group(1), (
        "CITATION.cff advertises the withdrawn Zenodo record whose results were fabricated"
    )
