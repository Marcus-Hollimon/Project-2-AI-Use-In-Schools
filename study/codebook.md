# Codebook, version 2 (2026-11-11, after the 5-school pilot)

The allowed values and cue words live in `study/codebook.json`; the checker loads that file, and a
test fails if this page and that file disagree about the allowed values. Version 1 was frozen
before the first school was coded. Version 2 came out of the pilot; the changes and reasons are in
"Changes in version 2" at the end, and the 5 pilot schools were recoded under it.

## What is coded
Two levels for every school, kept apart because they often disagree:
- **University**: provost, teaching and learning center, academic integrity office, university
  policy library.
- **Department**: the computer science department's own pages, handbooks, and the public pages or
  syllabi of its courses. A statement counts as the department's only if it is on a department
  page. A department page that says "follow the university policy" is coded with the university's
  value, quoting the department page. News articles published on the department's site count as
  department text (source type "news or announcement", the lowest in decision rule 1). (v2)

## Variables

### `univ_stance`, `dept_stance`: what the official text lets students do with generative AI
| Value | Use when |
|---|---|
| encourage | The text actively promotes AI use in learning or teaching (for example, AI built into courses or tools offered to all students), beyond permitting it. |
| permit with conditions | Use is allowed by default, with conditions such as disclosure or limits. |
| restrict | Use is banned by default; it needs explicit permission. |
| instructor decides | The text leaves the rule to each course and sets no default. If a default exists, code the default instead. |
| none found | Nothing found after the fixed search (see the search log). |

A rule that bans only misuse described by degree ("inappropriate or excessive use") sets no
default ban, so it is "permit with conditions". A rule that bans "unauthorized" use implies use
needs permission, so it is "restrict". (v2)

### `univ_tone`, `dept_tone`: how the text talks about AI
| Value | Use when |
|---|---|
| positive | AI is presented mainly as an opportunity. |
| neutral | Procedural rules with little evaluative language. |
| cautionary | Risks (integrity, accuracy, privacy, learning loss) dominate. |
| none found | No text at that level. |

### `collaboration`: does official text describe working *with* AI?
| Value | Use when |
|---|---|
| explicit | AI is described as a partner, tutor, assistant, or pair programmer, as a recommended way to learn or work, in more than one sentence. |
| in passing | Mentioned once, without development. |
| not discussed | Not found in any page reviewed. |

### `disclosure`: must students say when they used AI?
| Value | Use when |
|---|---|
| required | A rule says students must disclose, cite, or acknowledge AI use. |
| encouraged | Students should or are encouraged to disclose. Also use this for example or suggested syllabus language that tells students to disclose, when instructors may adopt it but no rule makes it binding (v2). |
| not stated | No page reviewed says either. |

### `se_courses`: how the department's software engineering course handles AI
The course named "software engineering", or the department's nearest equivalent (for example
"Software Design" or a software engineering capstone). If several have public syllabi, code the
first in catalog order and note the others in the reason field.
| Value | Use when |
|---|---|
| AI built into the course | The course assigns or teaches AI tool use. |
| allowed with conditions | AI use permitted under stated conditions. |
| prohibited | AI use banned in the course. |
| not addressed | A public syllabus or course page for a term in 2023 or later exists but says nothing about AI. |
| no public syllabus found | No public syllabus or course page found after the fixed search, or only ones for terms before 2023 (before ChatGPT; v2). |

### `source_type` (recorded for every value that has a quote)
policy page, guidance page, handbook, syllabus, news or announcement.

## Decision rules
1. Several statements at one level: code the most authoritative (policy page over guidance page
   over handbook over news), and among equals the most recent.
2. Every value other than an absence value ("none found", "not discussed", "not stated",
   "not addressed", "no public syllabus found") carries a quote of at most 40 words, copied
   exactly from the archived page.
3. An absence value lists the archived pages that were reviewed, or points to the search log.
4. If the quote contains none of the value's cue words (see `codebook.json`), the value must carry
   a written reason why the quote still supports it. The reasons are published.
5. A page off the school's own web domain needs a written reason (for example, a state system's
   policy that the school adopts).

## Fixed search, the same for every school
1. The university's main AI guidance page.
2. The CS department site: home, undergraduate pages, handbook, academic integrity page.
3. Four web searches (in `codebook.json`, `required_searches`), each logged with its results.
4. For each "none found": two more searches (`second_searches`), logged.
5. Stop after 25 minutes per school or when every variable has a source.

## Changes in version 2 (2026-11-11, after the 5-school pilot)
Allowed values, cue words and searches are unchanged; only the rules for applying them changed.
1. **Course pages before 2023 do not count for `se_courses`.** Johns Hopkins' only official page
   for its software engineering course is from Fall 2018, before ChatGPT; v1 coded it "not
   addressed", which reads as if the course chose to say nothing about AI. Changed values: Johns
   Hopkins `se_courses`, "not addressed" to "no public syllabus found".
2. **Example syllabus language gets "encouraged" for disclosure.** Johns Hopkins and Valparaiso
   both publish suggested statements that tell students to acknowledge AI; v1 needed a written
   reason each time to code them "encouraged". The rule now says so. No value changed.
3. **News on the department's site counts as department text.** Minnesota's only department text
   on AI is a news article; v1 allowed it as the lowest source type but did not say so. No value
   changed.
4. **A rule against "inappropriate or excessive" use is "permit with conditions".** Coppin State's
   only university rule is one Code of Conduct clause of that kind; v1 had no clear value for a
   limit with no default. No value changed.
The before-and-after values for the pilot schools are in `data/coded/codebook-v2-recode.json`.
