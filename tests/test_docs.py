"""Documentation that contradicts the code is worse than none.

CLAUDE.md is what a future session reads to orient itself. Its layout table
drifted silently for seven modules because the edits that should have added
them used a string replace that no-ops when the anchor is missing. These checks
make that class of drift fail loudly.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _layout_section():
    text = (ROOT / "CLAUDE.md").read_text()
    start = text.index("## Layout")
    end = text.index("## Strategy contract")
    return text[start:end]


def test_every_module_is_in_the_layout_table():
    layout = _layout_section()
    modules = sorted(p.name for p in (ROOT / "quant").glob("*.py") if p.name != "__init__.py")
    missing = [m for m in modules if f"quant/{m}" not in layout]
    assert not missing, f"CLAUDE.md layout table is missing: {missing}"


def test_every_cli_is_in_the_layout_table():
    layout = _layout_section()
    clis = sorted(p.name for p in ROOT.glob("*.py"))
    missing = [c for c in clis if f"`{c}`" not in layout]
    assert not missing, f"CLAUDE.md layout table is missing: {missing}"


def test_layout_table_lists_nothing_that_does_not_exist():
    layout = _layout_section()
    referenced = {m for m in re.findall(r"`([a-z_]+(?:/[a-z_.-]+)*\.(?:py|service))`", layout)}
    absent = sorted(path for path in referenced if not (ROOT / path).exists())
    assert not absent, f"layout table references files that do not exist: {absent}"


def test_docs_do_not_reference_missing_files():
    """Every path mentioned in the docs must actually be there."""
    for doc in ("README.md", "CLAUDE.md"):
        text = (ROOT / doc).read_text()
        referenced = set(re.findall(r"`((?:quant|tests|web|deploy)/[a-z_.-]+\.(?:py|service|json))`", text))
        absent = sorted(path for path in referenced if not (ROOT / path).exists())
        assert not absent, f"{doc} references files that do not exist: {absent}"


def test_docs_do_not_hardcode_a_test_count():
    """A number in prose goes stale on the next commit and misleads quietly.

    Both docs carried one and both were wrong — 51 and 42 against an actual 108.
    """
    for doc in ("README.md", "CLAUDE.md"):
        text = (ROOT / doc).read_text()
        stale = re.findall(r"\b\d+\s+(?:self-checks?|checks passed)", text)
        assert not stale, f"{doc} hardcodes a test count ({stale}); it will go stale"


def test_every_test_file_keeps_its_runner_last():
    """The runner collects from globals(), so anything below it never runs.

    That has already silently skipped five tests once.
    """
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        text = path.read_text()
        # Match at column zero and take the LAST one: this very file mentions the
        # runner line as a string inside a test, and a naive search finds that
        # instead — which is how this check first failed against itself.
        runners = list(re.finditer(r"^if __name__ == ", text, re.MULTILINE))
        assert runners, f"{path.name} has no runner"
        after = text[runners[-1].end():]
        assert not re.search(r"^def test_", after, re.MULTILINE), \
            f"{path.name} defines tests after its runner — they will never execute"


def test_non_negotiables_are_stated_as_rules():
    """The section a future session is most likely to skim must stay concrete."""
    text = (ROOT / "CLAUDE.md").read_text()
    start = text.index("## Non-negotiables")
    end = text.index("## Testing conventions")
    rules = text[start:end]
    for topic in ("execution lag", "atomic", "veto", "Deflation", "exchangeInfo"):
        assert topic.lower() in rules.lower(), f"non-negotiables no longer mention {topic!r}"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
