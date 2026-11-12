"""Tests for study/mutation_score.py, the tool that plants bugs to measure the study tests.

The last two tests run the tool on a two-line program whose right answer is known in advance."""
import ast

import mutation_score as ms

SNIPPET = """def f(a, b):
    if not a == 1 and b < 2:
        return a + 1
    for i in a:
        break
    return True
"""


def test_every_kind_of_change_is_found_once_per_place():
    found = [op for _, op, _ in ms.sites(ast.parse(SNIPPET))]
    counts = {op: found.count(op) for op in ms.OPERATORS}
    # a == 1 and b < 2; one "and"; one "not"; the numbers 1, 2, 1 and True; one "+"; two returns; one break
    assert counts == {"comparison": 2, "boolean": 1, "not": 1, "constant": 4, "arithmetic": 1,
                      "return": 2, "loop": 1}


def test_each_mutant_is_valid_python_that_differs_from_the_original_in_one_place():
    tree = ast.parse(SNIPPET)
    original = ast.unparse(tree)
    seen = set()
    for site in ms.sites(tree):
        mutated, info = ms.describe(SNIPPET, tree, site)
        program = ast.unparse(mutated)
        compile(program, "mutant", "exec")
        assert program != original, info
        assert info["before"] != info["after"], info
        seen.add(program)
    assert len(seen) == len(ms.sites(tree))  # no two mutants are the same program
    assert ast.unparse(tree) == original  # describing mutants never changes the original tree


TARGET = "def big(x):\n    return x > 3\n"


def write(tmp_path, test_body):
    (tmp_path / "m.py").write_text(TARGET, encoding="utf-8")
    (tmp_path / "test_m.py").write_text("from m import big\n\n\ndef test_big():\n" + test_body, encoding="utf-8")


def test_a_test_that_misses_the_boundary_lets_boundary_bugs_survive(tmp_path):
    write(tmp_path, "    assert big(10) and not big(0)\n")
    result = ms.score(root=tmp_path, target="m.py", support=["test_m.py"], tests="test_m.py", workers=2)
    outcome = {(m["operator"], m["after"]): m["result"] for m in result["mutants"]}
    assert outcome == {("comparison", "x >= 3"): "survived", ("constant", "4"): "survived",
                       ("return", "return None"): "killed"}
    assert (result["total"], result["killed"], result["survived"]) == (3, 1, 2)


def test_a_test_at_the_boundary_kills_every_mutant(tmp_path):
    write(tmp_path, "    assert big(10) and not big(0)\n    assert big(4) and not big(3)\n")
    result = ms.score(root=tmp_path, target="m.py", support=["test_m.py"], tests="test_m.py", workers=2)
    assert (result["total"], result["killed"], result["survived"]) == (3, 3, 0)
    assert all(m["killedBy"] == "test_big" for m in result["mutants"])
