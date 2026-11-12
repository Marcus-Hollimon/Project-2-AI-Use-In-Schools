"""Each check gets a made-up school that breaks exactly one rule; the check must catch it.

The fixture school "Example University" (unitid 999999, domain example.edu) is fully valid; every
test starts from it and changes one thing.
"""
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
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


def test_s3_rendered_text_with_empty_202_raw_copy_needs_fetch_reason(world):
    # HTTP 202 with an empty body is a bot challenge, treated like 403; a 202 with a body is not.
    text = "Students may use generative AI tools when the instructor allows it"
    archive = write_archive(world["root"], "2026-11-11-waf.rendered.txt", text, status=None,
                            kind="rendered text from Claude's browser pane",
                            url="https://www.example.edu/waf", final_url="https://www.example.edu/waf")
    school = mutate(world, "univ_stance", archive=archive, url="https://www.example.edu/waf")
    write_archive(world["root"], "2026-11-11-waf.html", "", status=202,
                  url="https://www.example.edu/waf", final_url="https://www.example.edu/waf")
    assert only_failures(findings(world, school)) == ["S3"]
    school["values"]["univ_stance"]["fetch_reason"] = "curl gets HTTP 202 with an empty body; read in the browser pane"
    assert only_failures(findings(world, school)) == []
    archive2 = write_archive(world["root"], "2026-11-11-busy.rendered.txt", text, status=None,
                             kind="rendered text from Claude's browser pane",
                             url="https://www.example.edu/busy", final_url="https://www.example.edu/busy")
    write_archive(world["root"], "2026-11-11-busy.html", "<html>Accepted</html>", status=202,
                  url="https://www.example.edu/busy", final_url="https://www.example.edu/busy")
    school = mutate(world, "univ_stance", archive=archive2, url="https://www.example.edu/busy",
                    fetch_reason="anything")
    assert only_failures(findings(world, school)) == ["S3"]


def test_s3_missing_fetch_record_fails(world):
    Path(str(world["root"] / world["archive"]) + ".meta.json").unlink()
    assert failed(findings(world), "S1")


def test_registrable_domain_keeps_campus_of_college_systems():
    assert cs.registrable_domain("www.niagaracc.suny.edu/") == "niagaracc.suny.edu"
    assert cs.registrable_domain("www.umfk.maine.edu/") == "umfk.maine.edu"
    assert cs.registrable_domain("https://twin-cities.umn.edu/") == "umn.edu"
    assert cs.registrable_domain("web.mit.edu/") == "mit.edu"
    assert cs.registrable_domain("www.westminster.edu/") == "westminster.edu"


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


def test_c2_stance_none_found_with_a_tone_passes_only_with_stance_tone_reason(world):
    tone = dict(value="positive", quote="Students may use generative AI tools when the instructor allows it",
                url="https://www.example.edu/ai", archive=world["archive"], source_type="policy page")
    school = mutate(world, "dept_tone", stance_tone_reason="The page talks about AI but sets no rule.", **tone)
    assert only_failures(findings(world, school)) == []
    school["values"]["dept_tone"]["stance_tone_reason"] = ""
    assert only_failures(findings(world, school)) == ["C2"]


def test_c2_tone_none_found_with_a_stance_fails_even_with_stance_tone_reason(world):
    school = copy.deepcopy(world["school"])
    stance = school["values"]["univ_stance"]
    assert stance["value"] != "none found"
    school["values"]["univ_tone"] = {"value": "none found", "search_log": world["school"]["values"]["dept_tone"].get("search_log"),
                                     "reviewed": [world["archive"]], "stance_tone_reason": "should not help"}
    assert "C2" in only_failures(findings(world, school))


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


def test_load_codebook_reads_the_repository_codebook_by_default():
    assert cs.load_codebook() == cs.load_codebook(REPO / "study" / "codebook.json")


# ---- Added after the first mutation score (study/mutation_score.py, 2026-11-11): 120 of 162 planted
# bugs were caught. Each test below closes a gap where a planted bug went unnoticed; the comment names
# the code it guards.

def write_values(world, *schools):
    path = world["root"] / "data" / "coded" / "values.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schools": list(schools)}), encoding="utf-8")


def add_second_school(world):
    """A second school in the sample, never coded, so a run over the whole sample fails on it."""
    sample = world["root"] / "data" / "frame" / "sample.csv"
    sample.write_text(sample.read_text(encoding="utf-8")
                      + "national,random,888888,Other College,ZZ,1,1,1,6,9,www.other.edu/,10,S1\n", encoding="utf-8")


def messages(fs, check, variable):
    return [f["message"] for f in fs if f["check"] == check and f["variable"] == variable]


# _Text.handle_endtag: an end tag inside a hidden block must not end the hiding early, and the hidden
# block's own end tag ends it exactly once.
def test_s1_text_inside_template_is_hidden_and_text_after_it_is_read(world):
    page = ("<template><p>Students may not use AI here</p> extra hidden words</template>"
            "<p>Students may use generative AI tools when the instructor allows it.</p>")
    archive = write_archive(world["root"], "2026-11-11-tpl.html", page)
    assert only_failures(findings(world, mutate(world, "univ_stance", archive=archive))) == []
    school = mutate(world, "univ_tone", archive=archive, quote="extra hidden words")
    assert only_failures(findings(world, school)) == ["S1"]


# page_text: the text saved beside a PDF is plain text, never parsed as HTML.
def test_s1_text_beside_a_pdf_is_read_as_plain_text(world):
    archive = write_archive(world["root"], "2026-11-11-rules.pdf", "%PDF-1.4 binary")
    (world["root"] / (archive + ".txt")).write_text("Use of <AI> tools is prohibited on exams.", encoding="utf-8")
    school = mutate(world, "univ_stance", value="restrict", archive=archive,
                    quote="Use of <AI> tools is prohibited on exams.")
    assert only_failures(findings(world, school)) == []


# registrable_domain: "www." is dropped before labels are counted, and a campus without "www." keeps three.
def test_registrable_domain_without_www_and_for_a_bare_system_domain():
    assert cs.registrable_domain("umfk.maine.edu/") == "umfk.maine.edu"
    assert cs.registrable_domain("https://www.suny.edu/") == "suny.edu"
    assert cs.registrable_domain("example.edu") == "example.edu"
    assert cs.registrable_domain("https://cs.niagaracc.suny.edu/") == "niagaracc.suny.edu"  # exactly three kept


# S5: the limit is "40 words or fewer", so a quote of exactly the limit passes.
def test_s5_quote_of_exactly_the_limit_passes(world):
    limit = cs.load_codebook(world["root"] / "study" / "codebook.json")["max_quote_words"]
    words = " ".join("word%d" % i for i in range(limit - 2)) + " may use"
    assert len(words.split()) == limit
    archive = write_archive(world["root"], "2026-11-11-limit.html", "<p>" + words + "</p>")
    assert only_failures(findings(world, mutate(world, "univ_tone", archive=archive, quote=words))) == []


# search_log_queries: only "- " lines under a search heading count as results; prose does not.
def test_c4_prose_under_a_search_heading_is_not_a_result(world):
    write_log(world["root"], REQUIRED + SECOND, empty=(REQUIRED[1],))
    log = world["root"] / world["log"]
    heading = "## Search: %s\n" % REQUIRED[1]
    log.write_text(log.read_text(encoding="utf-8").replace(heading, heading + "Nothing useful came up.\n"),
                   encoding="utf-8")
    assert "Nothing useful came up." in log.read_text(encoding="utf-8")
    assert only_failures(findings(world)) == ["C4"]


# cue_matches: a cue ending in * matches words that start with everything before the star.
def test_cue_prefix_is_everything_before_the_star():
    assert cs.cue_matches("Registered users only", "user*")
    assert not cs.cue_matches("This is usual practice", "use*")


# check_school: a problem with one variable never stops the checks on the variables after it, and
# nothing further is checked on the variable that has the problem.
@pytest.mark.parametrize("problem, checked_on_it", [
    ("not coded", {"C1"}),
    ("value outside the codebook", {"C1"}),
    ("empty quote", {"C1", "C2"}),
    ("saved copy missing", {"C1", "C2", "S5", "S1"}),
])
def test_one_bad_variable_never_stops_the_checks_on_the_others(world, problem, checked_on_it):
    school = copy.deepcopy(world["school"])
    first = school["values"]["univ_stance"]
    if problem == "not coded":
        del school["values"]["univ_stance"]
    elif problem == "value outside the codebook":
        first["value"] = "encourage loudly"
    elif problem == "empty quote":
        first["quote"] = ""
    else:
        first["archive"] = "data/sources/%s/never-saved.html" % SLUG
    fs = findings(world, school)
    assert {f["check"] for f in fs if f["variable"] == "univ_stance"} == checked_on_it
    later = {(f["check"], f["variable"]) for f in fs}
    assert {("S1", "disclosure"), ("S2", "disclosure"), ("C2", "se_courses"), ("N1", "se_courses")} <= later


# The stance-tone pair is compared only when both are coded; an uncoded one is already a C1 failure.
def test_stance_tone_pair_is_not_compared_when_one_is_uncoded(world):
    school = copy.deepcopy(world["school"])
    del school["values"]["univ_stance"]
    school["values"]["univ_tone"] = {"value": "none found", "search_log": world["log"]}
    fs = findings(world, school)
    assert not [f for f in fs if f["message"].startswith("univ_stance=")]
    assert only_failures(fs) == ["C1"]


# The message beside each result says what was found (checks.json and the printout show it).
def test_messages_say_what_each_check_found(world):
    fs = findings(world)
    assert messages(fs, "C1", "univ_tone") == ["value 'neutral' allowed", "source_type 'policy page' allowed"]
    assert messages(fs, "C2", "univ_tone") == ["quote, url and archive present"]
    assert messages(fs, "S2", "univ_tone") == ["hash matches"]
    assert messages(fs, "C2", "dept_stance") == ["absence backed by search log"]
    bad = findings(world, mutate(world, "univ_tone", value="enthusiastic"))
    assert messages(bad, "C1", "univ_tone") == ["value 'enthusiastic' NOT in codebook"]
    bad = findings(world, mutate(world, "univ_tone", source_type="blog"))
    assert messages(bad, "C1", "univ_tone")[1] == "source_type 'blog' NOT allowed"
    bad = findings(world, mutate(world, "univ_tone", quote=""))
    assert messages(bad, "C2", "univ_tone") == ["missing quote, url or archive"]
    school = copy.deepcopy(world["school"])
    school["values"]["se_courses"] = {"value": "not addressed", "reviewed": [world["archive"]]}
    assert messages(findings(world, school), "C2", "se_courses") == ["absence backed by 1 reviewed pages"]
    (world["root"] / world["archive"]).write_text("edited", encoding="utf-8")
    assert messages(findings(world), "S2", "univ_tone") == ["hash CHANGED since saved"]


# run(): every school in the sample unless some are named; the per-check summary (the Validation tab's
# table) marks exactly the failing check; the report passes only when every school does.
def test_run_covers_the_sample_and_summarizes_each_check(world):
    write_values(world, world["school"])
    assert cs.run(root=world["root"])["pass"] is True
    add_second_school(world)
    report = cs.run(root=world["root"])
    assert [s["unitid"] for s in report["schools"]] == ["999999", "888888"]
    assert report["pass"] is False
    assert report["schools"][1]["checks"] == {"C1": False}
    assert cs.run(["999999"], root=world["root"])["pass"] is True
    write_values(world, mutate(world, "univ_tone", value="enthusiastic"))
    assert cs.run(["999999"], root=world["root"])["schools"][0]["checks"] == {c: c != "C1" for c in cs.CHECKS}


# main(): writes checks.json, prints each failure (a finding with no variable shows "-"), honours
# --only, and exits 0 only when every check passes.
def test_main_writes_the_report_prints_failures_and_sets_the_exit_code(world, capsys):
    write_values(world, world["school"])
    add_second_school(world)
    out = world["root"] / "data" / "coded" / "checks.json"
    assert cs.main(["--only", "999999"], root=world["root"]) == 0
    assert [s["unitid"] for s in json.loads(out.read_text(encoding="utf-8"))["schools"]] == ["999999"]
    write_log(world["root"], REQUIRED[:3] + SECOND)
    assert cs.main([], root=world["root"]) == 1
    printed = capsys.readouterr().out
    assert "C4 -: missing or empty: " + REQUIRED[3] in printed
    assert "C1 -: school not coded yet" in printed
    assert "search logged with results" not in printed  # passing findings are not printed
    assert json.loads(out.read_text(encoding="utf-8"))["pass"] is False


# The command line: started as a script, the checker honours --only and exits 0 only when all pass.
def test_command_line_checks_only_the_named_schools(world):
    write_values(world, world["school"])
    add_second_school(world)
    shutil.copy(cs.__file__, world["root"] / "study" / "check_study.py")
    script = str(world["root"] / "study" / "check_study.py")
    assert subprocess.run([sys.executable, script, "--only", "999999"], capture_output=True).returncode == 0
    assert subprocess.run([sys.executable, script], capture_output=True).returncode == 1
