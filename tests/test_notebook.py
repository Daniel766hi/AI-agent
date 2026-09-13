"""The Colab notebook is a deliverable: it must be valid and it must run.

A notebook that errors on cell five is worse than no notebook — the reader has
no way to tell a broken example from a broken idea.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

NOTEBOOK = ROOT / "notebooks" / "quickstart.ipynb"


def _cells():
    return json.loads(NOTEBOOK.read_text())["cells"]


def test_notebook_is_valid_and_well_formed():
    document = json.loads(NOTEBOOK.read_text())
    assert document["nbformat"] == 4
    assert document["cells"], "no cells"
    for index, cell in enumerate(document["cells"]):
        assert cell["cell_type"] in ("markdown", "code"), f"cell {index}"
        assert isinstance(cell["source"], list), f"cell {index} source must be a list of lines"
        if cell["cell_type"] == "code":
            assert cell["outputs"] == [], f"cell {index} ships stale output"
            assert cell["execution_count"] is None, f"cell {index} ships an execution count"


def test_every_code_cell_parses():
    """Shell lines are stripped the way Colab strips them, then it must be Python."""
    import ast
    for index, cell in enumerate(_cells()):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        body = "\n".join(line for line in source.splitlines()
                         if not line.lstrip().startswith(("!", "%")))
        try:
            ast.parse(body)
        except SyntaxError as exc:
            raise AssertionError(f"cell {index} is not valid Python: {exc}") from exc


def test_notebook_clones_the_branch_that_exists():
    source = "".join("".join(c["source"]) for c in _cells())
    import subprocess
    branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                            capture_output=True, text=True, cwd=ROOT).stdout.strip()
    assert branch in source, f"notebook does not clone the current branch ({branch})"


def test_notebook_only_uses_functions_that_exist():
    """Guards against the notebook drifting from the API it calls."""
    import quant.agents, quant.data, quant.risk, quant.strategies, quant.validate
    import screen

    referenced = {
        "data.fetch_many_yahoo": quant.data, "data.synthetic": quant.data,
        "validate.walk_forward": quant.validate, "validate.block_bootstrap_pvalue": quant.validate,
        "validate.deflate": quant.validate, "screen.evaluate_all": screen,
        "risk.breakeven": quant.risk, "risk.cost_drag": quant.risk,
        "risk.kelly_fraction": quant.risk, "risk.leverage_table": quant.risk,
        "agents.Desk": quant.agents, "agents.Proposal": quant.agents,
    }
    source = "".join("".join(c["source"]) for c in _cells())
    for dotted, module in referenced.items():
        name = dotted.split(".", 1)[1]
        if name in source:
            assert hasattr(module, name), f"notebook calls {dotted}, which no longer exists"


def test_notebook_states_what_to_expect():
    """It must not read as a promise of profit."""
    source = "".join("".join(c["source"]) for c in _cells()).lower()
    assert "no significant edge" in source, "must set the expectation up front"
    assert "nothing trades" in source or "nothing here places an order" in source
    assert "testnet" in source, "must point at testnet before real funds"


def test_notebook_explains_the_desk_screen_disagreement():
    """The desk can approve what the screen rejected; that needs explaining, not hiding."""
    source = "".join("".join(c["source"]) for c in _cells())
    assert "desk approved what the screen rejected" in source.lower(), \
        "the notebook must address the case where the two disagree"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
