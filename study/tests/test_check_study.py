"""Each check gets a made-up school that breaks exactly one rule; the check must catch it.

The fixture school "Example University" (unitid 999999, domain example.edu) is fully valid; every
test starts from it and changes one thing.
"""
import copy
import hashlib
import json
import re
import shutil
from pathlib import Path

import pytest

import check_study as cs

REPO = Path(__file__).resolve().parents[2]
SLUG = "999999-example"
REQUIRED = ["example.edu generative AI policy", "example.edu computer science AI policy",
            "example.edu software engineering syllabus AI", "example.edu ChatGPT academic integrity"]
SECOND = ["example.edu artificial intelligence course policy", "example.edu AI syllabus statement"]

PAGE = """<html><head><title>AI policy</title><script>var s = "Students may not use AI at all";</script>
<style>.x{}</style></head><body><h1>Generative AI</h1>
<p>Students <b>may use</b> generative AI tools when the instructor allows it, and must
disclose any use in their submission.</p>
<p>We see AI as a &ldquo;thought partner&rdquo; &amp; tutor that students can work with.</p>
<p>Use of AI tools is prohibited on exams unless authorized.</p>
</body></html>"""


def write_archive(root, name, content, status=200, final_url="https://www.example.edu/ai", kind="raw bytes from curl",
                  url="https://www.example.edu/ai"):
    folder = root / "data" / "sources" / SLUG
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_bytes(content.encode("utf-8"))
    meta = {"kind": kind, "url": url, "final_url": final_url, "http_status": status,
            "fetched_at": "2026-11-11T11:00:00-05:00", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    Path(str(path) + ".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return "data/sources/%s/%s" % (SLUG, name)


def write_log(root, queries, empty=()):
    lines = ["# Search log"]
    for q in queries:
        lines.append("## Search: " + q)
        if q not in empty:
            lines.append("- https://www.example.edu/ai (opened, saved)")
    (root / "data" / "sources" / SLUG / "search-log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def ev(value, quote, archive, source_type="policy page", **extra):
    d = {"value": value, "quote": quote, "url": "https://www.example.edu/ai", "archive": archive,
         "source_type": source_type}
    d.update(extra)
    return d


@pytest.fixture
def world(tmp_path):
    (tmp_path / "study").mkdir()
    shutil.copy(REPO / "study" / "codebook.json", tmp_path / "study" / "codebook.json")
    (tmp_path / "data" / "frame").mkdir(parents=True)
    (tmp_path / "data" / "frame" / "sample.csv").write_text(
        "group,how,unitid,name,state,region,control,carnegie_research,carnegie_ic,highest_offering,website,cs_degrees_2024,stratum\n"
        "national,random,999999,Example University,ZZ,1,1,1,6,9,www.example.edu/,10,S1\n", encoding="utf-8")
    archive = write_archive(tmp_path, "2026-11-11-ai-policy.html", PAGE)
    write_log(tmp_path, REQUIRED + SECOND)
    log = "data/sources/%s/search-log.md" % SLUG
    school = {"unitid": "999999", "slug": SLUG, "name": "Example University", "values": {
        "univ_stance": ev("permit with conditions", "Students may use generative AI tools when the instructor allows it", archive),
        "univ_tone": ev("neutral", "Students may use generative AI tools when the instructor allows it", archive),
        "dept_stance": {"value": "none found", "search_log": log},
        "dept_tone": {"value": "none found", "search_log": log},
        "collaboration": ev("explicit", 'We see AI as a "thought partner" & tutor that students can work with.', archive, "guidance page"),
        "disclosure": ev("required", "and must disclose any use in their submission", archive),
        "se_courses": {"value": "no public syllabus found", "search_log": log},
    }}
    return {"root": tmp_path, "school": school, "archive": archive, "log": log}


def findings(world, school=None):
    root = world["root"]
    cb = cs.load_codebook(root / "study" / "codebook.json")
    row = cs.load_sample(root / "data" / "frame" / "sample.csv")["999999"]
    return cs.check_school(school or world["school"], row, cb, root)


def failed(fs, check):
    return [f for f in fs if f["check"] == check and not f["ok"]]


def only_failures(fs):
    return sorted({f["check"] for f in fs if not f["ok"]})


def mutate(world, var, **changes):
    school = copy.deepcopy(world["school"])
    school["values"][var].update(changes)
    return school


# The valid fixture passes everything, and each check actually ran on it.
def test_valid_school_passes_every_check(world):
    fs = findings(world)
    assert only_failures(fs) == []
    assert {"S1", "S2", "S3", "S4", "S5", "C1", "C2", "C3", "C4", "N1"} <= {f["check"] for f in fs}


# S1 quote in source
def test_s1_altered_quote_fails(world):
    school = mutate(world, "univ_stance", quote="Students may use generative AI tools whenever they like")
    assert only_failures(findings(world, school)) == ["S1"]


def test_s1_normalizes_tags_entities_and_curly_quotes(world):
    school = mutate(world, "collaboration", quote="We see AI as a “thought partner” & TUTOR that students can work with.")
    assert failed(findings(world, school), "S1") == []


def test_s1_ignores_text_inside_scripts(world):
    school = mutate(world, "univ_stance", value="restrict", quote="Students may not use AI at all")
    assert failed(findings(world, school), "S1")


def test_s1_pdf_without_extracted_text_fails(world):
    archive = write_archive(world["root"], "2026-11-11-policy.pdf", "%PDF-1.4 binary")
    school = mutate(world, "univ_stance", archive=archive)
    assert "no text to search" in failed(findings(world, school), "S1")[0]["message"]


def test_s1_word_file_reads_extracted_text_beside_it(world):
    archive = write_archive(world["root"], "2026-11-11-policy.docx", "PK binary zip")
    school = mutate(world, "univ_stance", archive=archive)
    assert "no text to search" in failed(findings(world, school), "S1")[0]["message"]
    (world["root"] / (archive + ".txt")).write_text(
        "Students may use generative AI tools when the instructor allows it.", encoding="utf-8")
    assert only_failures(findings(world, school)) == []


# S2 hash
def test_s2_archive_edited_after_saving_fails(world):
    path = world["root"] / world["archive"]
    path.write_bytes(path.read_bytes() + b"<!-- edited -->")
    assert only_failures(findings(world)) == ["S2"]


# S3 fetch record
def test_s3_non_200_status_fails(world):
    archive = write_archive(world["root"], "2026-11-11-blocked.html", PAGE, status=403)
    school = mutate(world, "univ_stance", archive=archive)
    assert only_failures(findings(world, school)) == ["S3"]


def test_s3_rendered_text_needs_raw_copy_of_same_url(world):
    archive = write_archive(world["root"], "2026-11-11-js.rendered.txt",
                            "Students may use generative AI tools when the instructor allows it",
                            status=None, kind="rendered text from Claude's browser pane",
                            url="https://www.example.edu/js", final_url="https://www.example.edu/js")
    school = mutate(world, "univ_stance", archive=archive, url="https://www.example.edu/js")
    assert only_failures(findings(world, school)) == ["S3"]
    write_archive(world["root"], "2026-11-11-js.html", "<html></html>", url="https://www.example.edu/js",
                  final_url="https://www.example.edu/js")
    assert only_failures(findings(world, school)) == []


def test_s3_rendered_text_with_blocked_raw_copy_needs_fetch_reason(world):
    text = "Students may use generative AI tools when the instructor allows it"
    archive = write_archive(world["root"], "2026-11-11-wall.rendered.txt", text, status=None,
                            kind="rendered text from Claude's browser pane",
                            url="https://www.example.edu/wall", final_url="https://www.example.edu/wall")
    school = mutate(world, "univ_stance", archive=archive, url="https://www.example.edu/wall")
    write_archive(world["root"], "2026-11-11-wall.html", "<html>Forbidden</html>", status=403,
                  url="https://www.example.edu/wall", final_url="https://www.example.edu/wall")
    assert only_failures(findings(world, school)) == ["S3"]
    school["values"]["univ_stance"]["fetch_reason"] = "site returns 403 to curl; text read in the browser pane"
    assert only_failures(findings(world, school)) == []
    # A 404 raw copy is a page that does not exist, so no reason can excuse it.
    archive404 = write_archive(world["root"], "2026-11-11-gone.rendered.txt", text, status=None,
                               kind="rendered text from Claude's browser pane",
                               url="https://www.example.edu/gone", final_url="https://www.example.edu/gone")
    write_archive(world["root"], "2026-11-11-gone.html", "<html>Not found</html>", status=404,
                  url="https://www.example.edu/gone", final_url="https://www.example.edu/gone")
    school = mutate(world, "univ_stance", archive=archive404, url="https://www.example.edu/gone",
                    fetch_reason="anything")
    assert only_failures(findings(world, school)) == ["S3"]


def test_s3_missing_fetch_record_fails(world):
    Path(str(world["root"] / world["archive"]) + ".meta.json").unlink()
    assert failed(findings(world), "S1")


# S4 right school
def test_s4_other_domain_fails(world):
    archive = write_archive(world["root"], "2026-11-11-other.html", PAGE, final_url="https://www.other.edu/ai")
    school = mutate(world, "univ_stance", archive=archive)
    assert only_failures(findings(world, school)) == ["S4"]


def test_s4_lookalike_domain_fails(world):
    archive = write_archive(world["root"], "2026-11-11-look.html", PAGE, final_url="https://notexample.edu/ai")
    school = mutate(world, "univ_stance", archive=archive)
    assert only_failures(findings(world, school)) == ["S4"]


def test_s4_subdomain_passes_and_reason_overrides(world):
    sub = write_archive(world["root"], "2026-11-11-sub.html", PAGE, final_url="https://cs.example.edu/policy")
    assert failed(findings(world, mutate(world, "univ_stance", archive=sub)), "S4") == []
    off = write_archive(world["root"], "2026-11-11-sys.html", PAGE, final_url="https://www.statesystem.edu/ai")
    school = mutate(world, "univ_stance", archive=off, domain_reason="State system policy the school adopts")
    assert failed(findings(world, school), "S4") == []


# S5 quote length
def test_s5_quote_over_40_words_fails(world):
    long_page = "<p>" + " ".join("word%d" % i for i in range(41)) + " may use</p>"
    archive = write_archive(world["root"], "2026-11-11-long.html", long_page)
    quote = " ".join("word%d" % i for i in range(41)) + " may use"
    school = mutate(world, "univ_tone", archive=archive, quote=quote)
    assert only_failures(findings(world, school)) == ["S5"]


# C1 allowed values
def test_c1_value_outside_codebook_fails(world):
    assert only_failures(findings(world, mutate(world, "univ_tone", value="enthusiastic"))) == ["C1"]


def test_c1_missing_variable_fails(world):
    school = copy.deepcopy(world["school"])
    del school["values"]["disclosure"]
    assert only_failures(findings(world, school)) == ["C1"]


def test_c1_bad_source_type_fails(world):
    assert only_failures(findings(world, mutate(world, "univ_tone", source_type="blog"))) == ["C1"]


def test_c1_uncoded_school_fails_in_run(world):
    report = cs.run(["999999"], root=world["root"])
    assert report["pass"] is False
    assert report["schools"][0]["findings"][0]["message"] == "school not coded yet"


# C2 consistency
def test_c2_stance_none_found_with_a_tone_fails(world):
    school = mutate(world, "dept_tone", value="positive", quote="Students may use generative AI tools when the instructor allows it",
                    url="https://www.example.edu/ai", archive=world["archive"], source_type="policy page")
    assert only_failures(findings(world, school)) == ["C2"]


def test_c2_absence_with_no_backing_fails(world):
    school = copy.deepcopy(world["school"])
    school["values"]["dept_stance"] = {"value": "none found"}
    assert "C2" in only_failures(findings(world, school))


def test_c2_absence_citing_missing_reviewed_page_fails(world):
    school = copy.deepcopy(world["school"])
    school["values"]["disclosure"] = {"value": "not stated", "reviewed": ["data/sources/%s/nope.html" % SLUG]}
    assert only_failures(findings(world, school)) == ["C2"]


def test_c2_value_without_quote_fails(world):
    school = mutate(world, "univ_tone", quote="")
    assert only_failures(findings(world, school)) == ["C2"]


# C3 evidence fits the value
def test_c3_restrict_without_cue_fails_and_reason_overrides(world):
    school = mutate(world, "univ_stance", value="restrict", quote="Students may use generative AI tools when the instructor allows it")
    assert only_failures(findings(world, school)) == ["C3"]
    school["values"]["univ_stance"]["cue_reason"] = "test reason"
    assert only_failures(findings(world, school)) == []


def test_c3_prohibited_quote_satisfies_restrict(world):
    school = mutate(world, "univ_stance", value="restrict", quote="Use of AI tools is prohibited on exams unless authorized.")
    assert only_failures(findings(world, school)) == []


def test_c3_required_disclosure_needs_both_groups(world):
    page = "<p>Students disclose their AI use.</p>"
    archive = write_archive(world["root"], "2026-11-11-disc.html", page)
    school = mutate(world, "disclosure", archive=archive, quote="Students disclose their AI use.")
    assert only_failures(findings(world, school)) == ["C3"]


def test_cue_whole_word_and_prefix_matching():
    assert cs.cue_matches("We use AI here", "ai")
    assert not cs.cue_matches("We maintain the lab", "ai")
    assert cs.cue_matches("This is PROHIBITED.", "prohibit*")
    assert not cs.cue_matches("we may note it", "may not")


# C4 search done
def test_c4_missing_search_log_fails(world):
    (world["root"] / world["log"]).unlink()
    assert "C4" in only_failures(findings(world))


def test_c4_missing_one_required_search_fails(world):
    write_log(world["root"], REQUIRED[:3] + SECOND)
    assert only_failures(findings(world)) == ["C4"]


def test_c4_search_with_no_results_logged_fails(world):
    write_log(world["root"], REQUIRED + SECOND, empty=(REQUIRED[1],))
    assert only_failures(findings(world)) == ["C4"]


# N1 second search for "none found"
def test_n1_none_found_without_second_searches_fails(world):
    write_log(world["root"], REQUIRED)
    assert only_failures(findings(world)) == ["N1"]


def test_n1_not_required_when_nothing_is_none_found(world):
    write_log(world["root"], REQUIRED)
    school = copy.deepcopy(world["school"])
    q = "Students may use generative AI tools when the instructor allows it"
    school["values"]["dept_stance"] = ev("permit with conditions", q, world["archive"])
    school["values"]["dept_tone"] = ev("neutral", q, world["archive"])
    school["values"]["se_courses"] = {"value": "not addressed", "reviewed": [world["archive"]]}
    assert only_failures(findings(world, school)) == []


# The readable codebook and the machine one agree.
def test_codebook_md_lists_every_allowed_value():
    cb = cs.load_codebook(REPO / "study" / "codebook.json")
    md = (REPO / "study" / "codebook.md").read_text(encoding="utf-8")
    assert "version %d" % cb["version"] in md.lower()
    for var, spec in cb["variables"].items():
        assert "`%s`" % var in md, var
        for value in spec["values"]:
            assert re.search(r"\|\s*%s\s*\|" % re.escape(value), md), (var, value)
