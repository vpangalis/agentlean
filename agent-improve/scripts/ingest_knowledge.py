"""Ingest the LSS Black Belt eBook into an improve_knowledge_index.

═══════════════════════════════════════════════════════════════════════
THE CORPUS IS ONE DOCUMENT, DELIBERATELY  (ratified 2026-08-25)
═══════════════════════════════════════════════════════════════════════

`improve_knowledge_index` carries **the BB eBook and nothing else** — the
tier-1 methodology spine, one coherent voice.

Source conflict is governed at prompt level by the MEMORY HIERARCHY, which
arbitrates *between* tiers. It cannot arbitrate between two competing tier-1
methodology voices, because they occupy the same tier. One source removes the
conflict rather than resolving it.

Two sources were removed, for different reasons:

  - **`problem_solving_8D`** — 8D is Agent Resolve's methodology, not DMAIC.
    Its presence here was cross-framework contamination: D1/D2 content was
    retrievable during DMAIC *Define* coaching, where it teaches a different
    method under a similar-sounding name. It belongs in Resolve's index only.

  - **`LSS_tools_suite`** (the 21 `.xlsb` sheets) — thin descriptions plus
    example data, redundant against the eBook's far richer coverage of the
    same tools (compare the eBook's multi-level Pareto treatment, pp 53-55).
    Their example-number rows were embedding noise and retrieval attractors.

**`EXCEL_SHEET_TOOL_MAP` moved out of this script rather than being deleted**
— see `docs/EXCEL_TOOL_INVENTORY.md`. The sheet-to-phase mapping is the
build-inventory for the §30 computation layer. It is a spec, not a corpus, and
it has no business in an ingestion script.

`SOURCE_ALLOWLIST` below is the enforcement. Dropping another PDF into
`data/knowledge/` does not silently re-contaminate the index — it is skipped
and logged.

═══════════════════════════════════════════════════════════════════════
HOW A DOCUMENT BECOMES A SEARCHABLE INDEX FIELD  (read before editing)
═══════════════════════════════════════════════════════════════════════

Documents are written through LangChain's `AzureSearch.add_texts`, which
builds each index document as:

    {id, content, content_vector, metadata: json.dumps(<your dict>)}

and then promotes metadata keys to top-level index fields with:

    additional_fields = {k: v for k, v in metadata.items()
                         if k in [x.name for x in self.fields]}

**A metadata key becomes a searchable/filterable field ONLY if its name
exactly matches a field on the index** *and* the vectorstore was constructed
with `fields=KNOWLEDGE_INDEX_FIELDS`. `self.fields` defaults to
`[id, content, content_vector, metadata]` and never introspects the live
index, so either omission buries the value in the JSON blob where `$filter`
cannot reach it — with no error raised (reference §23.4).

This is precisely how the original bug arose: the script emitted `phase`,
which is not a field on the index, so `phase_relevance` was never populated
and phase filtering could not work.

The index has exactly these fields (reference §23.1), confirmed live:

    id  content  content_vector  metadata  source_file  phase_relevance
    page_number

So the metadata dict is deliberately limited to the three promotable keys
plus `char_count`, which stays in the blob by design.

═══════════════════════════════════════════════════════════════════════
`page_number` IS THE PDF INDEX, NOT THE PRINTED PAGE NUMBER
═══════════════════════════════════════════════════════════════════════

**Ruled 2026-08-25: keep the PDF index. A citation must say so.**

The two do not agree, and the offset is not constant. Measured:

    pdf pages 1-3      cover, legal notice, table of contents — unnumbered
    pdf pages 4-693    printed number = pdf index - 3      (690 pages)
    pdf pages 694-700  an appendix, printed numbering restarts at 1

So a chunk stored with `page_number: 47` sits on the page printed **44**,
and a coach citing "page 47 of the BB eBook" sends the Belt three pages
past the content it is quoting.

**A single offset constant would be wrong at both ends** — it would push the
front matter to zero and negative, and it would be 693 out across the
appendix. That piecewise shape, not the size of the error, is why the stored
value stays as the PDF index: it is the one number that is unambiguous for
all 700 pages and identical to what the live index already holds.

**The fix belongs in the citation string, not here.** Cite as "PDF page N"
rather than "page N", so the Belt opens the file at the right place instead
of trusting a printed number the field never carried.

═══════════════════════════════════════════════════════════════════════
EXTRACTION: pdfplumber PLUS A NORMALISER — THE LIBRARY ALONE IS NOT ENOUGH
═══════════════════════════════════════════════════════════════════════

**Measured across all 700 pages, not assumed** (both libraries, same book):

    artifact                        pypdf              pdfplumber
    (cid:N) tokens                      0    1,477 on 51% of pages
    double-struck words                 1        643 on 23 pages
    '%'-as-space                181 on 5 pp        129 on 3 pp
    U+FFFD                              0                      0
    running footer          1,396 on 698 pp    1,396 on 698 pp

Three conclusions, each of which contradicts the obvious reading:

1. **The U+FFFD garble does not exist.** Zero occurrences under either
   library. It was never an extractor artifact.

2. **'%'-as-space is in the PDF, not the extractor.** The book's fonts map
   the space glyph to '%', '$' or '&' on a handful of pages. Both libraries
   reproduce it faithfully. **Swapping libraries cannot fix it** — only a
   repair pass can.

3. **pdfplumber is strictly *worse* on garble** — it is the library that
   introduces the (cid:N) tokens and the double-strike doubling.

**pdfplumber is still the right choice, for the reason the census cannot
measure: reading order.** This book is a slide deck. On two-column pages
pypdf interleaves the columns into semantic nonsense; pdfplumber keeps them
apart. A scrambled chunk cannot be repaired downstream — whereas every
artifact pdfplumber adds is a regex away from gone, which `normalise_page`
does and `--audit` proves.

So the pipeline is **pdfplumber for layout, `normalise_page` for glyphs**,
and neither half is optional.

═══════════════════════════════════════════════════════════════════════
HOW CONTENT MAPS TO A DMAIC PHASE — ONE LLM CALL PER CHUNK
═══════════════════════════════════════════════════════════════════════

**Per-chunk semantic classification — NOT keyword counting, and NOT chapter
or section mapping.**

Chapter mapping was ruled out against the live documents rather than assumed:

  - The BB eBook PDF carries **no outline/bookmarks** (confirmed: 0 entries),
    so there is no chapter structure to read.
  - DMAIC words do not appear as sustained page headings; they occur
    throughout the text.
  - Every 50-page band holds a **mix** of phases. A chapter mapping would
    make each band almost entirely one phase. It does not — the *dominant*
    phase per band advances in DMAIC order, which is why chapter mapping
    looks plausible at first glance, but the book is ordered by phase without
    being partitioned by phase.

**Keyword counting was the previous mechanism and it has been replaced.** It
scored each chunk against a per-phase word list and took the highest count,
which fails in one specific and common way: **it classifies on vocabulary
rather than on subject.** The eBook's Control-phase wrap-up page lists
"Improvement Selected / Develop Training Plan / Implement Training Plan", so
the word *improve* outscores the word *control* and the page is tagged
`improve` — on a page whose entire subject is closing out the Control phase.
The introduction to hypothesis testing was tagged `measure` because it is
dense with measurement vocabulary while teaching an Analyse technique.

So each chunk now gets **one call to the cheap model** (`operational` role →
`operational-model`, gpt-4o-mini) at temperature 0.0, returning exactly one of
six labels. The prompt states what each phase covers and instructs the model
to judge the passage **on what it teaches, not on which words appear in it** —
which is precisely the distinction the keyword scorer could not make.

**`general` is a first-class verdict, not a fallback.** Cross-phase content,
methodology overviews, glossary and definition entries all belong there. A
phase filter ORs `general` into every phase, so a chunk tagged that way stays
reachable from all five (reference §23.1) — which makes it the right answer
for genuinely cross-phase material and strictly better than forcing a wrong
single-phase tag that hides the content from four phases.

**A failed classification is counted and named, not disguised.**
`classify_phase` returns `None` when the call fails or the reply is not one of
the six labels; `classify_corpus` tags those `general` so they stay reachable,
lists their page numbers, **and returns the count** so `--max-classify-failures`
can refuse the run. A silent fallback would make a broken deployment look like
a corpus rich in cross-phase content — the same failure shape as returning `[]`
for a search that never ran (reference §27).

**Two failure modes occur in practice and they need opposite handling:**

  - **HTTP 429, transient.** The `operational-model` deployment rate-limits in
    bursts. Measured: at 8 workers, **603 of 1,184 chunks failed**; at 4
    workers with jittered backoff, **1**. Retry is the whole answer here.
  - **HTTP 400 `content_filter`, permanent.** Azure's content management
    policy refuses a small number of chunks outright — observed on **PDF page
    302**, a passage about statistical power and sample size for a 1-Sample t
    test, with nothing objectionable in it. **This is not retried**, per the
    same rule reference §27 and CLAUDE.md §7.2 apply to retrieval: a 4xx is
    permanent, and retrying spends six calls to learn what the first one said.

That page-302 chunk ships as `general`. It is genuinely Analyse content, so
the tag is a small loss of precision — but `general` is ORed into every phase
filter, so the passage stays retrievable from all five rather than being
dropped or given a tag nobody stands behind. **The run is allowed past it only
by an explicit `--max-classify-failures 1`**, so the exception is a decision
someone made rather than a threshold that quietly absorbs it.

**Classification is cached by document id.** Ids are deterministic, so a
re-run with `--cache` costs nothing and reproduces the same labels. Without
it, two ingests of an unchanged corpus can differ, and a diff against live
then measures the classifier's noise rather than the corpus's change.

**Re-ingestion still reclassifies relative to the LIVE index.** The pipeline
that populated it is not in the repository and cannot be recovered.
**Re-ingesting is a content change, not an idempotent no-op** — which is why
`--index` exists and why the procedure is ingest-fresh, diff, swap.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import logging
import math
import os
import random
import re
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_community.vectorstores.azuresearch import AzureSearch
from openai import BadRequestError

from backend.core.config import settings
from backend.knowledge.retriever import (
    CROSS_PHASE_RELEVANCE,
    KNOWLEDGE_INDEX_FIELDS,
    get_embeddings,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data" / "knowledge"

# Chunking: one chunk per page, split further only when a page is long.
# Keeps page_number truthful — it is a citation field (reference §23.1), so a
# chunk spanning pages could not be cited honestly.
CHUNK_CHARS = 1200
CHUNK_OVERLAP_CHARS = 150
MIN_CHUNK_CHARS = 50

# Documents written per add_texts call. One call per chunk costs ~1,100 HTTP
# round trips and ~1,100 separate embedding requests; batching cuts both.
# `ids=` is still passed per document, so the key contract is unchanged.
BATCH_SIZE = 32

# The corpus, and the enforcement of it. Filename -> the `source_file` label
# stored on the index. The stored values are short stable labels, not
# filenames: filenames carry version suffixes and spaces that would churn the
# citation string on every re-issue of a source document.
#
# **A file not listed here is skipped, loudly.** This is what keeps the
# one-voice corpus decision from decaying the next time somebody drops a PDF
# into data/knowledge/.
SOURCE_ALLOWLIST = {
    "5_BB_EB_MT_v11.1_PDF2_compressed (1).pdf": "BB_LSS_ebook",
}

# Sources deliberately removed, kept by name so the skip message can say *why*
# rather than just "unmapped". See the module docstring.
REMOVED_SOURCES = {
    "Problem Solving 8D.pdf":
        "8D is Agent Resolve's methodology — cross-framework contamination "
        "in a DMAIC index. Belongs in Resolve's index only.",
    "Lean-Six-Sigma Tools suite_20220912.xlsb":
        "Thin tool descriptions + example data, redundant against the eBook "
        "and an embedding-noise attractor. Sheet-to-phase map preserved at "
        "docs/EXCEL_TOOL_INVENTORY.md.",
}

# ── Phase classification ───────────────────────────────────────────────
# The five DMAIC phases plus the cross-phase sentinel. The sentinel value is
# NOT free-form: a phase filter ORs exactly this string in, so a chunk tagged
# anything else meaning "applies broadly" — 'all', 'any', 'cross' — becomes
# unreachable from every phase, silently (reference §23.1).
PHASE_LABELS = ("define", "measure", "analyse", "improve", "control",
                CROSS_PHASE_RELEVANCE)

# Role, not deployment. `operational` resolves through `core/llm.py`'s role map
# to `operational-model` (gpt-4o-mini) — the cheap tier, which is the right one
# for a single-label classification (CLAUDE.md §4.2). Never construct
# AzureChatOpenAI here; §4.1 makes the factory the only path.
CLASSIFIER_ROLE = "operational"

# Temperature 0.0, not the 0.2 default. The same passage must classify the same
# way on every run, or two ingests of an unchanged corpus disagree and the diff
# against live stops meaning anything (CLAUDE.md §4.7 applies the same rule to
# the graders, for the same reason).
CLASSIFIER_TEMPERATURE = 0.0

# Concurrent classification calls.
#
# **Measured the hard way: 8 workers had 603 of 1,184 chunks fail on HTTP 429.**
# The `operational-model` deployment's throughput is the binding constraint,
# not the local machine's, and the factory's `max_retries=3` was nowhere near
# enough to absorb it. 4 workers plus the backoff below is what actually
# completes. Raising this is not a free speedup — it trades directly against
# the failure count, and a failed classification is a fabricated `general`.
CLASSIFIER_WORKERS = 4

# Attempts per chunk before it is given up on, and the base for exponential
# backoff between them. Azure returns 429 in bursts as the per-minute quota
# refills, so the retry that matters is the one that waits seconds, not
# milliseconds.
CLASSIFIER_MAX_ATTEMPTS = 6
CLASSIFIER_BACKOFF_BASE = 2.0

# **The output contract is a single bare label, checked against PHASE_LABELS.**
#
# Not `with_structured_output`, and the reason is governance rather than
# preference: `.claude/config/deprecated_patterns.yaml`'s `pattern-2` blocks
# that call, and **CLAUDE.md §18.1 records the entry as stale but not yet
# amended** — §4.6 now sanctions the builder-style call for plain model
# invocations, and the registry has not caught up. Amending the registry to
# unblock a data rebuild would be exactly the in-passing rule change §0 and
# §56 forbid, and routing around the hook silently would be worse. So the
# classifier does not need the pattern at all.
#
# **This does not weaken §4.3** — that rule bans parsing JSON out of raw model
# text, and there is no JSON here. One label from a closed set of six, matched
# against the set, with anything else treated as a failure rather than coerced
# into a guess.
CLASSIFIER_PROMPT = f"""\
You classify passages from a Lean Six Sigma Black Belt textbook into exactly \
one DMAIC phase.

define   — problem definition, project selection, project charter, business \
case, Voice of the Customer, SIPOC, project scope, goal statement, COPQ.
measure  — baseline data, data collection planning, measurement system \
analysis and Gage R&R, process capability, sigma level, DPMO, detailed \
process mapping of the current state.
analyse  — root cause analysis, hypothesis testing, t-tests, ANOVA, \
regression, correlation, fishbone, 5-Why, identifying the vital few X's, \
statistical vs practical significance.
improve  — generating and selecting solutions, design of experiments, \
piloting, impact/effort assessment, implementation planning.
control  — control charts, statistical process control, control plans, \
monitoring and response plans, sustaining the gains, handover, documentation, \
training plans, project close-out.
{CROSS_PHASE_RELEVANCE}  — cross-phase content, methodology overviews, \
glossary or definition entries, front and back matter, tables of contents, \
and statistics fundamentals that serve several phases equally.

Return '{CROSS_PHASE_RELEVANCE}' when the passage is cross-phase, an overview, \
or a glossary/definition entry. '{CROSS_PHASE_RELEVANCE}' is ORed into every \
phase filter, so content tagged that way stays reachable from all five \
phases — prefer it over forcing a wrong single-phase tag.

Judge the passage on what it TEACHES, not on which words appear in it. A \
passage that mentions a control chart while explaining how to select a \
project is define, not control.

Reply with exactly one of these words and nothing else:
{" ".join(PHASE_LABELS)}"""

# ── Extraction repair ──────────────────────────────────────────────────
# Every pattern here corresponds to a counted artifact. `--audit` re-counts
# them after repair; all of them reach zero or near-zero. Do not add a rule
# without a count to justify it, and do not remove one without re-running the
# audit.

# Appears on 698 of 700 pages, twice each. The single largest source of
# repeated text in the corpus, and pure noise in an embedding.
FOOTER_RE = re.compile(
    r"^\s*LSS Black Belt eBook.*Open Source Six Sigma, LLC\s*$", re.M)

# pdfplumber emits unmapped glyphs as (cid:N). Only five codes occur in this
# book (1-5), all of them quotation marks around UI labels: "(cid:4)Options
# (cid:5) button". Stripped rather than mapped to a guessed glyph — quotes
# carry no embedding weight, and a wrong guess is worse than an absence.
CID_RE = re.compile(r"\(cid:\d+\)")

# The book's fonts substitute a visible glyph for the space character on a few
# pages, and WHICH glyph depends on the font: 'The%Problem', 'Six&Sigma&Belt',
# 'Full$Factorial', 'Selecting)Projects', '7"Components"of"Waste'. All five
# were observed by census, not guessed.
#
# **Requiring a letter on both sides is what makes this safe.** Every
# legitimate use of these characters in the book is either digit-adjacent
# ('95%'), space-delimited (' & '), or bracket-like ('(Mentor) Projects',
# '"quoted" text') — and all of those put a space or digit on at least one
# side. Letter-glyph-letter with no space is the artifact, every time.
#
# The {1,4} run allows for a page that is also N-struck, where the substituted
# glyph is repeated along with everything else: '&&&' between two letters is
# one artifact space, never three ampersands.
SPACE_GLYPH_RE = re.compile(r"(?<=[A-Za-z])[%$&)\"]{1,4}(?=[A-Za-z(])")

# Minimum struck tokens on a page before the collapse rule runs at all.
STRIKE_PAGE_THRESHOLD = 3


def _strike_factor(token: str) -> int:
    """N-fold character repetition in a token, or 1 if there is none.

    'BBllaacckk' -> 2, 'PPPrrreeeppp' -> 3, 'WWWWeeee' -> 4.

    **The book strikes at 2x, 3x AND 4x** — counted: 428 tokens at 2x,
    29 at 3x, 66 at 4x. A rule written for doubling alone leaves the other
    two mangled, and worse, halving a 4x token produces a 2x token that then
    looks repaired. Deriving N from the run lengths handles all three.

    **A single-run token returns 1, which is what makes this safe.** 'XXXX'
    and a row of underscores are indistinguishable from struck text on their
    own evidence, so they are left alone. Any token containing a character
    that occurs once — which is nearly every real English word — also returns
    1, because the gcd of its run lengths is 1.
    """
    if len(token) < 4:
        return 1
    lengths = [len(list(g)) for _, g in itertools.groupby(token)]
    if len(lengths) < 2:
        return 1
    n = math.gcd(*lengths)
    return n if n >= 2 else 1


def _collapse_strike(token: str, n: int) -> str:
    """Divide every character run in `token` by `n`. 'PPiizzzzaa' -> 'Pizza'."""
    return "".join(ch * (len(list(g)) // n)
                   for ch, g in itertools.groupby(token))


def normalise_page(text: str) -> str:
    """Repair the extraction artifacts counted in the module docstring.

    **Order is load-bearing.** The strike collapse runs *before* the
    space-glyph repair, because on a struck page the substituted glyph is
    struck too: 'WWWWeeeellllccccoooommmmeeee%%%%ttttoooo' has no single
    '%' between two letters for the space rule to match. Collapse first and
    it becomes 'Welcome%to', which the space rule then fixes. Reversing the
    two leaves both artifacts in place.

    **The collapse is page-scoped, deliberately.** A page must show at least
    STRIKE_PAGE_THRESHOLD struck tokens before the rule runs at all. Striking
    is a property of how a page was rendered, so it is concentrated on ~27
    pages and absent from the other 673 — gating on the page is both more
    accurate and a far smaller blast radius than a book-wide token rule.

    **Within a struck page each token is collapsed by its own factor, not by
    the page's dominant one.** Pages mix factors — page 107 carries 2x and 4x
    tokens together — and keying every token to the majority left the
    minority mangled.
    """
    if not text:
        return ""

    text = FOOTER_RE.sub("", text)
    text = CID_RE.sub("", text)

    factors = [n for n in map(_strike_factor, text.split()) if n >= 2]
    if len(factors) >= STRIKE_PAGE_THRESHOLD:
        text = "\n".join(
            " ".join(_collapse_strike(t, _strike_factor(t)) for t in line.split())
            for line in text.split("\n")
        )

    text = SPACE_GLYPH_RE.sub(" ", text)

    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


@lru_cache(maxsize=1)
def _classifier():
    """The classification model, built once through the factory.

    `core/llm.py`'s `get_llm` is the only permitted construction path
    (CLAUDE.md §4.1) — never `AzureChatOpenAI(...)` here.
    """
    from backend.core.llm import get_llm
    return get_llm(CLASSIFIER_ROLE, temperature=CLASSIFIER_TEMPERATURE,
                   max_tokens=8)


def classify_phase(text: str) -> str | None:
    """Classify one chunk into a DMAIC phase. Returns None if it could not be.

    **None means "the classifier did not answer", and the caller must be able
    to tell that apart from a real `general` verdict.** Collapsing a failure
    into `general` here would make a broken deployment look like a corpus full
    of cross-phase content — the same shape of mistake as returning `[]` for a
    failed search (reference §27), and just as invisible.
    """
    for attempt in range(CLASSIFIER_MAX_ATTEMPTS):
        try:
            reply = _classifier().invoke(
                [("system", CLASSIFIER_PROMPT), ("human", text)])
        except BadRequestError as e:
            # **A 4xx is permanent — do not retry it.** Reference §27 and
            # CLAUDE.md §7.2 state this rule for retrieval and it holds
            # identically here: a rejected request fails the same way every
            # time, so retrying spends six calls to learn what the first one
            # said. Azure's content filter is the case that actually occurs —
            # it refuses on false positives over ordinary statistics prose.
            logger.warning("Classification permanently rejected (%s): %s",
                           getattr(e, "code", "400"), str(e)[:160])
            return None
        except Exception as e:
            if attempt == CLASSIFIER_MAX_ATTEMPTS - 1:
                logger.warning("Classification failed after %d attempts: %s",
                               CLASSIFIER_MAX_ATTEMPTS, e)
                return None
            # Jittered exponential backoff. The jitter matters as much as the
            # backoff: every worker hits the quota wall at the same instant,
            # so a fixed sleep marches them back into the wall together.
            delay = CLASSIFIER_BACKOFF_BASE ** attempt * (0.5 + random.random())
            time.sleep(delay)
            continue

        # `content` is read, not string-indexed or substring-searched (CLAUDE.md
        # §4.5). The whole reply must BE a label; a sentence containing one is a
        # failure, because it means the instruction was not followed and the
        # rest of the answer is unknown.
        label = str(getattr(reply, "content", "")).strip().strip(".").lower()
        if label not in PHASE_LABELS:
            logger.warning("Classifier returned %r, not a phase label", label[:80])
            return None
        return label
    return None


def classify_corpus(docs: list[dict], workers: int = CLASSIFIER_WORKERS,
                    cache_path: Path | None = None) -> int:
    """Classify every chunk in parallel, writing `phase_relevance` in place.

    Returns the number of chunks the classifier could not label. Those fall
    back to CROSS_PHASE_RELEVANCE — the one value reachable from every phase,
    so a failure costs a chunk its precision rather than its reachability —
    **and the count is returned so a corpus that was mostly guessed can be
    refused rather than shipped.**

    `cache_path` makes a re-run cheap and, more usefully, reproducible: doc
    ids are deterministic, so the same chunk keeps the same label without
    paying for the call again.
    """
    cache: dict[str, str] = {}
    if cache_path and cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        logger.info("Loaded %d cached classifications from %s",
                    len(cache), cache_path)

    todo = [d for d in docs if d["id"] not in cache]
    logger.info("Classifying %d chunks (%d from cache) on role '%s', %d workers",
                len(todo), len(docs) - len(todo), CLASSIFIER_ROLE, workers)

    if todo:
        done = 0
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(classify_phase, d["content"]): d for d in todo}
            for fut in as_completed(futures):
                phase = fut.result()
                # **Only a real verdict is cached.** Caching the fallback was a
                # bug that cost a full run: 603 rate-limited chunks were stored
                # as 'general', so the re-run the cache exists to make cheap
                # would have treated every one of them as already decided and
                # never retried it — turning a transient 429 into a permanent
                # mislabel, invisibly. A missing key is retried; a cached
                # guess is forever.
                if phase is not None:
                    cache[futures[fut]["id"]] = phase
                done += 1
                if done % 100 == 0:
                    logger.info("  ...%d/%d classified", done, len(todo))

    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=0, sort_keys=True),
                              encoding="utf-8")
        logger.info("Classification cache written to %s (%d verdicts)",
                    cache_path, len(cache))

    unclassified = []
    for d in docs:
        phase = cache.get(d["id"])
        if phase is None:
            unclassified.append(d)
            phase = CROSS_PHASE_RELEVANCE
        d["metadata"]["phase_relevance"] = phase

    if unclassified:
        # Named, not just counted. A count says "something is wrong"; the page
        # numbers say which passages carry a tag nobody stands behind, which is
        # what an operator needs to decide whether to ship or re-run.
        logger.error(
            "%d of %d chunks could not be classified and fell back to '%s'. "
            "They stay reachable from every phase, but they are NOT a verdict:",
            len(unclassified), len(docs), CROSS_PHASE_RELEVANCE)
        for d in unclassified[:20]:
            logger.error("    p%-4s id=%s  %s",
                         d["metadata"]["page_number"], d["id"],
                         " ".join(d["content"].split())[:90])
    return len(unclassified)


def chunk_text(text: str, chunk_size: int = CHUNK_CHARS,
               overlap: int = CHUNK_OVERLAP_CHARS) -> list[str]:
    """Split one page's text into overlapping character chunks."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    i = 0
    step = chunk_size - overlap
    while i < len(text):
        chunks.append(text[i:i + chunk_size])
        i += step
    return chunks


def make_doc_id(source_file: str, page_number: int, chunk_idx: int) -> str:
    """Deterministic document key.

    Deterministic on purpose: Azure Search upserts on key, so re-ingesting the
    same source replaces its documents instead of duplicating them. LangChain
    generates a random UUID when none is supplied, which is why the key must
    be passed explicitly via `ids=` (reference §23.4).
    """
    raw = f"{source_file}_{page_number}_{chunk_idx}"
    return hashlib.md5(raw.encode()).hexdigest()


def build_metadata(source_file: str, page_number: int, content: str) -> dict:
    """Metadata dict for one chunk, before classification.

    Key names are the contract: `source_file`, `page_number` and
    `phase_relevance` match index fields and are promoted to top-level
    filterable fields. `char_count` has no matching field and stays inside the
    JSON blob — that asymmetry is intentional and matches every document
    already in the index. Renaming any of the first three silently demotes it
    to blob-only. See the module docstring.

    **`phase_relevance` is deliberately ABSENT here, not defaulted.**
    `classify_corpus` adds it, and `write_corpus` refuses to ship a document
    without it. A placeholder would ship as a real tag the moment
    classification were skipped by accident; a missing key cannot.
    """
    return {
        "source_file": source_file,
        "page_number": page_number,
        "char_count": len(content),
    }


def build_corpus(filepath: Path, source_file: str) -> list[dict]:
    """Extract, normalise, chunk and classify one PDF. Writes nothing.

    Separated from the write path so `--dry-run` can produce the exact corpus
    that would be indexed and diff it **before** spending embedding calls on
    it. Every decision that determines index content happens here.
    """
    import pdfplumber

    logger.info("Reading %s", filepath.name)
    docs: list[dict] = []

    with pdfplumber.open(str(filepath)) as pdf:
        total_pages = len(pdf.pages)
        # Chunk PER PAGE, never across pages. page_number is a citation field;
        # a chunk spanning a page boundary could not carry an honest one.
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = normalise_page(page.extract_text() or "")
            for chunk_idx, chunk in enumerate(chunk_text(page_text)):
                if len(chunk.strip()) < MIN_CHUNK_CHARS:
                    continue
                docs.append({
                    "id": make_doc_id(source_file, page_number, chunk_idx),
                    "content": chunk,
                    "metadata": build_metadata(
                        source_file=source_file,
                        page_number=page_number,
                        content=chunk,
                    ),
                })
            if page_number % 100 == 0:
                logger.info("  ...%d/%d pages, %d chunks",
                            page_number, total_pages, len(docs))

    logger.info("Built %d chunks from %s (%d pages)",
                len(docs), source_file, total_pages)
    return docs


def get_vectorstore(index_name: str) -> AzureSearch:
    """Vectorstore bound to an explicit index name.

    Not `retriever.get_knowledge_vectorstore()`, which is `lru_cache`d onto
    the *live* index name from settings. The whole point of `--index` is to
    write somewhere that is not live.

    `fields=KNOWLEDGE_INDEX_FIELDS` is mandatory, not decorative — without it
    `source_file`, `phase_relevance` and `page_number` are buried in the
    metadata blob and the index is silently unfilterable (reference §23.4).
    """
    return AzureSearch(
        azure_search_endpoint=settings.AZURE_SEARCH_ENDPOINT,
        azure_search_key=settings.AZURE_SEARCH_API_KEY,
        index_name=index_name,
        embedding_function=get_embeddings(),
        search_type="hybrid",
        fields=KNOWLEDGE_INDEX_FIELDS,
    )


def write_corpus(docs: list[dict], index_name: str) -> int:
    """Write a built corpus to Azure in batches. Returns documents written.

    Refuses a corpus whose documents are not all classified. `build_metadata`
    omits `phase_relevance` and `classify_corpus` adds it, so a missing key
    means classification was skipped — and an unclassified document written to
    the index is invisible to every phase filter rather than obviously broken.
    """
    missing = [d["id"] for d in docs if "phase_relevance" not in d["metadata"]]
    if missing:
        raise RuntimeError(
            f"{len(missing)} document(s) have no phase_relevance — run "
            f"classify_corpus() before writing. First: {missing[0]}")

    vs = get_vectorstore(index_name)
    written = 0
    for start in range(0, len(docs), BATCH_SIZE):
        batch = docs[start:start + BATCH_SIZE]
        try:
            vs.add_texts(
                texts=[d["content"] for d in batch],
                metadatas=[d["metadata"] for d in batch],
                ids=[d["id"] for d in batch],
            )
            written += len(batch)
        except Exception as e:
            # One bad batch must not abort 1,100 documents, but it must be
            # visible — the summary reports the shortfall against len(docs).
            logger.warning("Batch at offset %d failed (%d docs): %s",
                           start, len(batch), e)
        if written and written % (BATCH_SIZE * 10) == 0:
            logger.info("  ...%d/%d written", written, len(docs))
    return written


def summarise(docs: list[dict]) -> None:
    """Print the distribution a diff against the live index will compare."""
    phases = Counter(d["metadata"].get("phase_relevance", "<unclassified>")
                     for d in docs)
    sources = Counter(d["metadata"]["source_file"] for d in docs)
    chars = [d["metadata"]["char_count"] for d in docs]
    logger.info("-" * 60)
    logger.info("CORPUS: %d documents", len(docs))
    logger.info("  source_file      : %s", dict(sources))
    logger.info("  phase_relevance  : %s", dict(phases.most_common()))
    logger.info("  chars            : total %d, mean %d, min %d, max %d",
                sum(chars), sum(chars) // max(len(chars), 1),
                min(chars, default=0), max(chars, default=0))
    if CROSS_PHASE_RELEVANCE not in phases:
        logger.error(
            "NO '%s' DOCUMENTS. A phase filter ORs this value in; without it "
            "cross-phase methodology is unreachable from every phase.",
            CROSS_PHASE_RELEVANCE)
    logger.info("-" * 60)


def audit_extraction(filepath: Path) -> None:
    """Re-count the docstring's artifact table, before and after repair.

    This exists so the repair rules stay honest. If a future PDF re-issue
    changes the fonts, the counts move and the rules can be re-derived from
    evidence instead of inherited on faith.
    """
    import pdfplumber

    def census(t: str) -> Counter:
        c = Counter()
        c["chars"] = len(t)
        c["cid"] = len(CID_RE.findall(t))
        c["space_glyph"] = len(SPACE_GLYPH_RE.findall(t))
        c["footer"] = len(FOOTER_RE.findall(t))
        c["struck_tokens"] = sum(1 for n in map(_strike_factor, t.split()) if n >= 2)
        c["replacement_char"] = t.count("�")
        return c

    before, after = Counter(), Counter()
    with pdfplumber.open(str(filepath)) as pdf:
        for page in pdf.pages:
            raw = page.extract_text() or ""
            before.update(census(raw))
            after.update(census(normalise_page(raw)))

    logger.info("-" * 60)
    logger.info("EXTRACTION AUDIT - %s", filepath.name)
    logger.info("  %-20s %12s %12s", "artifact", "raw", "normalised")
    for k in ("cid", "struck_tokens", "space_glyph", "replacement_char",
              "footer", "chars"):
        logger.info("  %-20s %12s %12s", k, f"{before[k]:,}", f"{after[k]:,}")
    logger.info("-" * 60)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Ingest the BB eBook into an improve_knowledge_index.")
    ap.add_argument(
        "--index", default=settings.AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX,
        help="Target index. Defaults to the LIVE index — pass a fresh index "
             "name to follow the ingest-fresh / diff / swap procedure.")
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Build and summarise the corpus without writing to Azure.")
    ap.add_argument(
        "--out", type=Path,
        help="Write the built corpus to this JSONL file (for diffing).")
    ap.add_argument(
        "--audit", action="store_true",
        help="Report extraction-artifact counts before/after repair, then exit.")
    ap.add_argument(
        "--cache", type=Path,
        help="JSON file of id->phase classifications. Reused when present and "
             "written after. Makes a re-run free and, more importantly, "
             "reproducible.")
    ap.add_argument(
        "--workers", type=int, default=CLASSIFIER_WORKERS,
        help=f"Concurrent classification calls (default {CLASSIFIER_WORKERS}).")
    ap.add_argument(
        "--max-classify-failures", type=int, default=0,
        help="Abort if more than this many chunks fail classification. "
             "Default 0 — a corpus that was partly guessed should not ship "
             "without someone deciding it may.")
    args = ap.parse_args()

    if not DATA_DIR.exists():
        logger.error("Data directory not found: %s", DATA_DIR)
        return 1

    pdfs: list[tuple[Path, str]] = []
    for f in sorted(DATA_DIR.iterdir()):
        if f.name in SOURCE_ALLOWLIST:
            pdfs.append((f, SOURCE_ALLOWLIST[f.name]))
        elif f.name in REMOVED_SOURCES:
            logger.info("SKIP (removed from corpus) %s\n       %s",
                        f.name, REMOVED_SOURCES[f.name])
        else:
            logger.warning(
                "SKIP (not in SOURCE_ALLOWLIST) %s - this index is the BB "
                "eBook alone. Add an allowlist entry only with a ratified "
                "corpus decision behind it.", f.name)

    if not pdfs:
        logger.error("No allowlisted source found in %s. Expected: %s",
                     DATA_DIR, ", ".join(SOURCE_ALLOWLIST))
        return 1

    if args.audit:
        for filepath, _ in pdfs:
            audit_extraction(filepath)
        return 0

    docs: list[dict] = []
    for filepath, source_file in pdfs:
        docs.extend(build_corpus(filepath, source_file))

    failures = classify_corpus(docs, workers=args.workers,
                               cache_path=args.cache)
    summarise(docs)

    if failures > args.max_classify_failures:
        logger.error(
            "ABORTING — %d classification failures exceeds the permitted %d. "
            "Nothing written. Re-run to retry (use --cache so the chunks that "
            "did classify are not paid for twice).",
            failures, args.max_classify_failures)
        return 1

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8") as fh:
            for d in docs:
                fh.write(json.dumps(d, ensure_ascii=False) + "\n")
        logger.info("Corpus written to %s", args.out)

    if args.dry_run:
        logger.info("DRY RUN - nothing written to Azure.")
        return 0

    if args.index == settings.AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX:
        # **Measured against the live index, 2026-08-25: ZERO of its 1,369
        # document ids are reproduced by make_doc_id().** The pipeline that
        # populated it is not in this repository and used a different key
        # formula. Azure Search upserts on key, so a write here does not
        # replace anything — it ADDS this corpus alongside the existing one,
        # and every document from the two removed sources survives untouched.
        #
        # That is what makes the fresh-index procedure mandatory rather than
        # merely tidy, and it is why this prompt is not a formality.
        logger.warning(
            "TARGET IS THE LIVE INDEX (%s).\n"
            "  No live document id is reproduced by this script, so writing "
            "here ADDS\n"
            "  %d documents beside the existing corpus and replaces nothing.\n"
            "  The ratified procedure is: ingest to a FRESH index, diff, then "
            "swap.\n"
            "  Re-run with --index <fresh_name> unless you truly mean this.",
            args.index, len(docs))
        if input("Type 'write-live' to proceed: ").strip() != "write-live":
            logger.info("Aborted.")
            return 1

    logger.info("Writing %d documents to %s", len(docs), args.index)
    written = write_corpus(docs, args.index)
    if written != len(docs):
        logger.error("INCOMPLETE - %d of %d documents written", written, len(docs))
        return 1
    logger.info("Ingestion complete - %d documents in %s", written, args.index)
    return 0


if __name__ == "__main__":
    sys.exit(main())
