"""Mutation score: how many small planted bugs in study/check_study.py do the study tests catch?

A "mutant" is a copy of check_study.py with exactly one small change, the kind of slip a programmer
makes: a comparison turned around, "and" swapped for "or", a "not" dropped, True swapped for False,
a number off by one, a function returning nothing. For each mutant the study tests run against the
changed copy, in a temporary folder (the real file is never touched). If at least one test fails,
the tests caught ("killed") the bug. If every test still passes, the bug "survived": either the
change makes no difference to what the checker does, or the tests have a gap there.

The score is killed / total. It measures the tests against these kinds of bugs only; it cannot
measure bugs nobody thought to plant (see OPERATORS for the full list, and NOT_TRIED).

Run from the repo root (takes several minutes):
  uv run --project pipeline python study/mutation_score.py
Writes validation/mutation-runs/<start time>.json; every run is kept, so a score can be compared
with the one before it. Standard library plus pytest only.
"""
import ast
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = "study/check_study.py"
TESTS = "study/tests/test_check_study.py"
# Files the tests read besides the checker, copied beside each mutant at the same relative paths.
SUPPORT = ["study/tests/conftest.py", TESTS, "study/codebook.json", "study/codebook.md"]
OUT_DIR = ROOT / "validation" / "mutation-runs"
TIMEOUT_SECONDS = 120

OPERATORS = {
    "comparison": "a comparison changed: == and != swapped, < to <=, <= to <, > to >=, >= to >, in and not in swapped, is and is not swapped",
    "boolean": "\"and\" and \"or\" swapped",
    "not": "a \"not\" removed",
    "constant": "True and False swapped, or a whole number made one larger",
    "arithmetic": "+ and - swapped (also += and -=)",
    "return": "a function returns None instead of its value",
    "loop": "break and continue swapped",
}
NOT_TRIED = [
    "changes to text strings (messages, cue words, regular expressions)",
    "deleting whole lines or statements",
    "two bugs at once",
]

SWAP_CMP = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE,
            ast.GtE: ast.Gt, ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Is: ast.IsNot, ast.IsNot: ast.Is}
SWAP_BIN = {ast.Add: ast.Sub, ast.Sub: ast.Add}


def sites(tree):
    """Every possible single change in the tree, as (node index in ast.walk order, operator, detail)."""
    found = []
    for i, node in enumerate(ast.walk(tree)):
        if isinstance(node, ast.Compare):
            found += [(i, "comparison", k) for k, op in enumerate(node.ops) if type(op) in SWAP_CMP]
        elif isinstance(node, ast.BoolOp):
            found.append((i, "boolean", None))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            found.append((i, "not", None))
        elif isinstance(node, ast.Constant) and (isinstance(node.value, bool) or type(node.value) is int):
            found.append((i, "constant", None))
        elif isinstance(node, (ast.BinOp, ast.AugAssign)) and type(node.op) in SWAP_BIN:
            found.append((i, "arithmetic", None))
        elif isinstance(node, ast.Return) and node.value is not None and not (
                isinstance(node.value, ast.Constant) and node.value.value is None):
            found.append((i, "return", None))
        elif isinstance(node, (ast.Break, ast.Continue)):
            found.append((i, "loop", None))
    return found


def _replace_child(tree, old, new):
    for parent in ast.walk(tree):
        for field, value in ast.iter_fields(parent):
            if value is old:
                setattr(parent, field, new)
                return
            if isinstance(value, list):
                for k, item in enumerate(value):
                    if item is old:
                        value[k] = new
                        return
    raise ValueError("node not found")


def mutate(tree, site):
    """A copy of the tree with one change applied, and the changed node (for describing it)."""
    tree = copy.deepcopy(tree)
    index, operator, detail = site
    node = list(ast.walk(tree))[index]
    if operator == "comparison":
        node.ops[detail] = SWAP_CMP[type(node.ops[detail])]()
        changed = node
    elif operator == "boolean":
        node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        changed = node
    elif operator == "not":
        changed = node.operand
        _replace_child(tree, node, changed)
    elif operator == "constant":
        node.value = (not node.value) if isinstance(node.value, bool) else node.value + 1
        changed = node
    elif operator == "arithmetic":
        node.op = SWAP_BIN[type(node.op)]()
        changed = node
    elif operator == "return":
        node.value = ast.Constant(None)
        changed = node
    elif operator == "loop":
        changed = ast.Continue() if isinstance(node, ast.Break) else ast.Break()
        ast.copy_location(changed, node)
        _replace_child(tree, node, changed)
    else:
        raise ValueError(operator)
    return ast.fix_missing_locations(tree), changed


def enclosing_function(tree, line):
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.lineno <= line <= node.end_lineno:
            if best is None or node.lineno > best.lineno:
                best = node
    return best.name if best else "(module level)"


def describe(source, tree, site):
    index, operator, _ = site
    original = list(ast.walk(tree))[index]
    mutated_tree, changed = mutate(tree, site)
    before = ast.get_source_segment(source, original) or ast.unparse(original)
    after = ast.unparse(changed)
    if operator == "loop":
        before, after = type(original).__name__.lower(), type(changed).__name__.lower()
    return mutated_tree, {
        "line": original.lineno,
        "column": original.col_offset + 1,  # tells apart two identical expressions on one line
        "function": enclosing_function(tree, original.lineno),
        "operator": operator,
        "before": " ".join(before.split())[:160],
        "after": " ".join(after.split())[:160],
    }


def run_tests(program, root, target, support, tests, timeout=TIMEOUT_SECONDS):
    """Run the tests against one version of the target in a fresh temporary folder.

    Returns ("passed" | "failed" | "timed out", first failing test name or None)."""
    work = Path(tempfile.mkdtemp(prefix="mutant-"))
    try:
        for rel in support:
            (work / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(Path(root) / rel, work / rel)
        (work / target).parent.mkdir(parents=True, exist_ok=True)
        (work / target).write_text(program, encoding="utf-8")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        try:
            proc = subprocess.run([sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", tests],
                                  cwd=work, capture_output=True, text=True, timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            return "timed out", None
        if proc.returncode == 0:
            return "passed", None
        if proc.returncode in (1, 2):  # 1: a test failed; 2: the tests could not even start (counts as caught)
            m = re.search(r"^(?:FAILED|ERROR) \S+?::(\w+)", proc.stdout, re.M)
            return "failed", (m.group(1) if m else "collection error (the changed code broke loading)")
        raise RuntimeError("pytest exit code %s:\n%s\n%s" % (proc.returncode, proc.stdout[-2000:], proc.stderr[-2000:]))
    finally:
        shutil.rmtree(work, ignore_errors=True)


def sha256(path):
    # Line endings are made "\n" first: git stores the files with "\n" and this Windows checkout writes
    # "\r\n", so the web test on GitHub's servers must get the same fingerprint as this machine.
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def score(root=ROOT, target=TARGET, support=SUPPORT, tests=TESTS, workers=None):
    source = (Path(root) / target).read_text(encoding="utf-8")
    tree = ast.parse(source)
    # The rewritten (unparsed) original must pass, or every result below would mean nothing.
    baseline, why = run_tests(ast.unparse(tree), root, target, support, tests)
    if baseline != "passed":
        raise RuntimeError("the unchanged program fails its tests (%s): no score possible" % why)
    jobs = [describe(source, tree, s) for s in sites(tree)]

    def one(job):
        mutated_tree, info = job
        result, killer = run_tests(ast.unparse(mutated_tree), root, target, support, tests)
        info["result"] = {"failed": "killed", "passed": "survived", "timed out": "timed out"}[result]
        info["killedBy"] = killer
        return info

    with ThreadPoolExecutor(max_workers=workers or max(2, (os.cpu_count() or 4) // 2)) as pool:
        mutants = list(pool.map(one, jobs))
    for k, m in enumerate(mutants, 1):
        m["id"] = k
    killed = sum(m["result"] != "survived" for m in mutants)
    return {
        "target": target,
        "tests": tests,
        "targetSha256": sha256(Path(root) / target),
        "testsSha256": sha256(Path(root) / tests),
        "operators": OPERATORS,
        "notTried": NOT_TRIED,
        "baseline": baseline,
        "total": len(mutants),
        "killed": killed,
        "survived": len(mutants) - killed,
        "timedOut": sum(m["result"] == "timed out" for m in mutants),
        "byOperator": {op: {"total": sum(m["operator"] == op for m in mutants),
                            "killed": sum(m["operator"] == op and m["result"] != "survived" for m in mutants)}
                       for op in OPERATORS},
        "mutants": mutants,
    }


def main():
    started = datetime.now().astimezone().isoformat(timespec="seconds")
    result = score()
    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    result = {"startedAt": started, "finishedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
              "gitCommit": git.stdout.strip() or None, **result}
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / (started[:19].replace(":", "-") + ".json")
    out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("%d mutants: %d killed (%d by timeout), %d survived. Wrote %s" % (
        result["total"], result["killed"], result["timedOut"], result["survived"], out.relative_to(ROOT).as_posix()))
    for m in result["mutants"]:
        if m["result"] == "survived":
            print("  survived #%d line %d col %d in %s (%s): %s  ->  %s" % (
                m["id"], m["line"], m["column"], m["function"], m["operator"], m["before"], m["after"]))


if __name__ == "__main__":
    main()
