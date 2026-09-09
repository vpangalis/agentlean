> ## ⚠ DRAFTING RECORD — NOT CANONICAL
>
> **This is the draft that was written for founder ratification on 2026-09-09.
> It was ratified and its content now lives in the binding documents.** Read
> those, not this:
>
> | What | Where it lives now |
> |---|---|
> | The five new index fields, the `role` vocabulary, supersession-by-deletion, the write-path trap | `ARCHITECTURE.md` **§23.2** |
> | The structured retrieval record | `ARCHITECTURE.md` **§24** |
> | `citations`' anchor and the `uploads` entry's `consumed_at` | `ARCHITECTURE.md` **§6 / S-C02**, and **S-C09** for `UploadRecord` |
> | Ruling 3's revision, and the provenance of the dry run | `docs/DECISIONS.md` **Part AP2** and **Part AQ** |
> | The migration step and its ordering | `docs/REFACTORING_PROCEDURE.md` **Appendix D, step 6.13** |
>
> **It must never be read as a competing source of truth.** Where this document
> and a binding one differ, the binding one wins — and they already differ:
> this draft still asks three questions under *"Left open for the founder"*
> that were answered at ratification, and its Amendments D and E describe work
> that belongs to **step 6.12**, which has not been built.
>
> **Kept for its two appendices, which are provenance and are not reproduced
> elsewhere in full.** Appendix A is the dry run that produced five findings;
> Appendix B is the method behind it, including the one premise the dry run got
> wrong — that the write path offers no partial update, true of LangChain's
> wrapper and false of Azure AI Search. `DECISIONS.md` Part AQ records both.

# The evidence channel — schema, routing and retrieval

**Draft for founder ratification, 2026-09-09. Not yet in the repo.**
Amends `ARCHITECTURE.md` §23.2 and §24, and revises `DECISIONS.md` Part AP2 ruling 3.
Must be ratified **before** step 6.12 writes its first field, and the schema half
must be ratified **before** the 9.1 reindex runs.

---

## Why this exists

Step 6.11 built the upload path and proved it live. Two things it left open turned
out to be the same thing seen from different sides: an upload that nobody asked for
has no identity, and an upload that answers a question has no route into a
calculation. Both are solved by one field the design was missing — the document's
**role** — and by accepting that similarity search is the wrong mechanism for
getting numbers into a tool.

The pattern is not invented here. It is the standard shape in claims and audit
document intake: logical identity is `(case, role)`, version identity is a content
digest, supersession is a pointer, and retrieval is constrained to the live set.

---

## Amendment A — §23.2 `improve_evidence_index` gains five fields

The live index today is five fields; `phase` and `uploaded_at` are already
**RATIFIED — NOT YET APPLIED** and backfill from `metadata` at reindex time. These
five join them on the same terms and in the same reindex.

| Field | Type | Role |
|---|---|---|
| `role` | String | **Filter + searchable.** The document's function in the project — "cycle time data", "as-is process map", "baseline defect data", "control plan draft". Together with `case_id` this is the document's **logical identity**. Server-set: from the ask when the upload was solicited, from the Belt's declared purpose when it was not |
| `kind` | String | **Filter.** `evidence` or `artefact`. **Derived from `role`, never declared separately** — see below. Retrieval filters to `evidence` **by default** |
| `description` | String | **Searchable + retrievable.** The interpretation's summary. A projection of `UploadRecord.summary`, written once at index time |
| `content_digest` | String | **Filter.** SHA-256 of the uploaded bytes. **Version identity** — the same bytes re-uploaded are not a new version |
| `shape_match` | String | **Filter.** `full`, `partial`, `none`, or `unsolicited`. Whether the file matched the ask's expected shape. Paired with `missing_columns` in `metadata` |

### `kind` is a property of `role`, not a second declaration

The dry run below breaks the original design here. "Process map" is ambiguous — an
**as-is** map describes the world and is evidence; a **to-be** map is what the team
designed and is an artefact. The 6.11 live run classified `purpose=Process map` as
`artefact`, which would filter the current-state description out of evidence
retrieval by default — removing exactly the document a Measure or Analyse coach
needs most.

So the controlled vocabulary carries the pairing, and one declaration sets both:

| `role` | `kind` |
|---|---|
| as-is process map · cycle time data · baseline defect data · voice-of-customer data | `evidence` |
| to-be process map · control plan draft · improvement proposal · FMEA worksheet | `artefact` |

A Belt or an ask names the role. Nothing names the kind. An inconsistent pair
becomes unrepresentable rather than merely discouraged.

### Supersession deletes; it does not flag

An earlier draft of this amendment carried an `is_current` boolean. **Drop it** —
but not for the reason first given.

**The first argument was wrong and is withdrawn.** It claimed the write path offers
no partial update, so flipping the flag would cost a re-chunk and re-embed. That is
true of LangChain's `AzureSearch.add_texts` wrapper and false of Azure AI Search,
which supports `mergeOrUpload` through the push API. The flag is cheap to maintain.

**The real argument is that it earns almost nothing.** Four moments could need it:

| Moment | Needs the flag |
|---|---|
| A Belt asks for their cycle times | No — deleting the superseded chunks does the same, with no filter to forget |
| Step 7.6's cascade reopens an approved gate | No — it needs the old *data* to say what changed, and chunks are text; that comes from re-parsing the old blob |
| A gate document cites its source | No — citations anchor on `blob_path` + digest and never touch the index |
| A Belt asks what the earlier version said | **Yes** — the only case |

One case in four, and it is the one where surfacing superseded evidence to a coach
is arguably wrong behaviour rather than a feature.

So: **when a document is superseded, delete its chunks from the index.** The index
holds only current versions and needs no flag. **History is not lost** — the case
blob is the system of record (§10) and retains every version, which is where a
superseded file belongs.

Two consequences bind:

- **Supersession is scoped to `(case_id, role)`.** A Control-phase measurement does
  not supersede the Measure baseline, because they are different roles. Only a
  correction of the same document supersedes.
- **Citations anchor on `blob_path` + `content_digest`, never on the index id.**
  An index id disappears when its document is superseded; a gate document that
  cited one would break. This is what lets §37 / step 7.6's supersession cascade
  detect that an approved gate rested on a file that has since changed.

**All five are server-set.** A Belt-entered value for any of them makes it
unreliable as a filter, which is the rule §23.2 already applies to `phase` and
`uploaded_at`.

**`description` is a projection and must be declared as one.** The system of record
for the summary is the case blob (§10). The index copy exists because it must be
*searchable*, which the blob cannot serve. A change to the summary requires
re-indexing that document — never an in-place edit of the index copy. This follows
the precedent of `phase_summary_{phase}` in `improve_case_index` (§23.3).

**The structural profile is deliberately NOT indexed.** Columns, types, ranges and
row count stay on `UploadRecord` in the case blob. Copying them into the index
would create a second source of truth for the same fact, which §39.2's
single-authority rule exists to prevent, and would repeat per chunk. The index
carries the pointer; the blob carries the data.

### The write-path trap applies to all five

§23.4 already documents the failure: a metadata key becomes filterable only if the
field is named **and** the vectorstore declares it in `fields=`. Miss either and the
value is written into the JSON blob where `$filter` cannot reach it, **with no error
raised**. That is how `phase_relevance` went unpopulated. Each of these five is two
changes, not one.

### Start writing the metadata keys now

`phase` and `uploaded_at` backfill from `metadata.upload_phase` and
`metadata.timestamp` — values already being written in the wrong shape. Do the same
here: the 6.11 write path should begin writing `metadata.role`,
`metadata.kind`, `metadata.description`, `metadata.content_digest` and
`metadata.shape_match` **as soon as this is ratified**, so that when 9.1 runs there
is something to backfill from. Otherwise the reindex promotes empty fields and every
document uploaded before it is permanently unlabelled.

---

## Amendment B — Part AP2 ruling 3 is revised, not abandoned

**Ruling 3 as taken:** evidence goes to the index; an artefact does not, because
"one bucket would let a proposed future be retrieved later as a fact about the
present."

**Ruling 3 as revised:** both enter the index. They are separated by `kind`, and
`search_evidence` filters to `kind eq 'evidence'` unless a caller explicitly asks
otherwise.

**The original reasoning is answered, not discarded.** The failure mode was
*indistinguishability*, not co-location. Nothing in the index could tell a to-be
design from an as-is measurement, so the only safe move was to keep one of them out.
A declared, server-set `kind` removes that condition.

**What the current ruling costs, measured.** The 6.11 live run confirmed that a
query aimed at an artefact's own content returns the evidence files and not the
artefact. So today a Belt asking *"what did we decide the to-be process would be"*
gets silence, and the team's own design work is unreachable to the coach that helped
produce it.

**Two conditions bind the revision:**

1. The default filter lives in `search_evidence` (`knowledge/retriever.py`), **not
   in each caller**. One place, default-on. A caller opts out explicitly.
2. A test must prove an artefact does not surface on an unfiltered evidence query.
   Without it, the first forgotten filter silently restores the original defect.

---

## Amendment C — retrieval returns structure, not prose

§24 is unchanged in mechanism: retrieval is a tool call, never a prepended system
message. What changes is the **shape of what comes back**.

`rag_lookup_evidence` currently returns rendered text. It should return one
structured record per hit:

```
role · kind · description · phase · uploaded_at · shape_match
blob_path · content_digest · excerpt
```

Two reasons, each sufficient. The coach has to **choose** a file, and choosing needs
attributes rather than prose — "which of these three is the current cycle-time
data" is a question about fields, not about similarity. And §50's citations are
built from `source`, `page` and `content_summary`, which the coach can only cite
accurately if it received them as values.

---

## Amendment D — how a number reaches a computation tool

**This is the clause 6.12 carries and has not specified**, and it is the one that
matters most for the coaching product.

**Similarity search is the wrong mechanism for loading data.** You do not retrieve
five hundred rows by vector similarity. Retrieval finds *which* file; a
deterministic fetch loads *the values*.

So the path splits in two, deliberately:

- **Finding** — `rag_lookup_evidence`, semantic, returns descriptions and handles.
- **Loading** — a new tool, `load_evidence_series(blob_path, column)`, which returns
  the typed values for that column together with `n`, `mean`, `sigma`, `min` and
  `max`.

**The loader re-parses the blob; it does not read stored values.** The dry run
caught this: `UploadRecord.rows` is an `Optional[int]` — a row *count*. The parsed
values themselves are stored nowhere, and should stay that way. Re-parsing the
original file with the same deterministic parser 6.11 already built keeps one source
of truth and costs milliseconds. Storing a second copy of the table would create
exactly the drift §39.2 forbids.

**The 20 computation tools are not touched.** They take scalar strings by ruling
AD1, and the loader hands them exactly that. One new tool, zero changes to twenty.

**This is what satisfies 6.12's last done-when clause** — *"a computation tool
consumes a bound upload without the coach retyping a figure."* The coach never sees
the numbers as text, so it cannot transcribe them, which is the §22 anti-pattern
performed on the platform's own evidence.

---

## Amendment E — how an upload is guaranteed to reach the coach

**Retrieval cannot carry this guarantee, and §24 says so on purpose.** Retrieval is
a tool call the model decides to make — *"there is no unconditional retrieval
pipeline. If you find one, it is a violation."* That is the right rule, and its
direct consequence is that **no uploaded document is guaranteed to be read via
`rag_lookup_evidence`**. A coach that never calls the tool never sees the file.

The guarantee therefore lives in three deterministic places, none of them a prompt.

### 1 — Awareness: the upload manifest is injected every turn

`BeforeModelStateInjection` (middleware position 1) already injects `phase_context`
every turn, wired at step 6.8. It gains an **upload manifest** — not content, an
inventory:

```
role · description · phase · uploaded_at · shape_match · consumed
```

one line per entry in `PhaseState.uploads`. Bounded, deterministic, cheap. The coach
cannot fail to know a file exists; it may still choose not to open it.

**§6 already names `uploads`' consumers as "gate document assembly; evidence
context."** Whether the injection half was ever wired is **owed verification** — if
it was not, this is the same defect class as WATCH 19, where `phase_context` was
declared, written by all five mappers and read by nothing for three steps.

### 2 — Opportunity: the planner routes on it, not the model

Per S-F13 DP1 the **planner** owns the field and gate decision and the executor
returns plainly. The planner is code. It can therefore inspect `uploads` and route
deterministically — an upload bound to an open ask, not yet consumed, is a fact the
planner reads, not a hint the model might notice.

**This is the only place a "the coach will call the tool" guarantee can be made at
all**, because it is the only place in the loop that is not the model's discretion.

### 3 — Enforcement: an unused upload blocks the gate

Add **`consumed_at`** to the uploads entry and to `UploadRecord`, set when a
`load_evidence_series` call or a citation references that document.

A gate reached with an upload that is bound to an open ask and has
`consumed_at = None` is a gate where **the Belt supplied evidence and the coaching
proceeded without it.** Layer 2 validation (steps 7.1–7.2) should refuse it. That
converts "hope the coach uses the file" into "the gate will not pass while the
Belt's evidence sits unread" — and puts the guarantee at the control point this
architecture already treats as the constraint on flow.

**Without `consumed_at` the condition is undetectable**, which is why the field is
part of this amendment rather than of Stage 7.

### 4 — A test that needs no model

Assert that the injected block contains one manifest line for every entry in
`PhaseState.uploads`. No model, no network — the same class of check as
`test_the_prompt_asks_for_the_json_it_is_parsed_as`, and for the same reason: it
pins a contract between two artefacts that must agree.

---

## Amendment F — `citations` gains an anchor

§6 / S-C02 specifies `citations` as `source`, `page`, `content_summary`, `turn`.
**None of those identifies the file underneath.** So a citation cannot tell that its
source has since been replaced, and step 7.6's supersession cascade — whose whole
job is to notice that an approved gate rested on evidence that changed — has nothing
to compare.

`citations` gains `blob_path` and `content_digest`.

This is what turns supersession from something the system *records* into something
it can *detect*. Without it, Amendment A's digest chain exists and nothing reads it.

---

## Amendment G — the `role` vocabulary is ratified, not invented per phase

`role` is only a reliable filter if it is drawn from a fixed list. A free-text role
drifts — "cycle times", "cycle time data", "cycle_times" — and every drift is a
retrieval miss that looks like an empty result rather than an error.

The vocabulary is ratified here and extended by amendment, not by a Belt at upload
time. The `kind` column is not separately declarable; it is a property of the row.

| `role` | `kind` | Typical phase |
|---|---|---|
| `as-is process map` | evidence | Define · Measure |
| `voice-of-customer data` | evidence | Define |
| `baseline defect data` | evidence | Measure |
| `cycle time data` | evidence | Measure · Analyse |
| `capability study data` | evidence | Measure · Control |
| `root cause analysis` | artefact | Analyse |
| `fmea worksheet` | artefact | Analyse · Improve |
| `to-be process map` | artefact | Improve |
| `improvement proposal` | artefact | Improve |
| `control plan draft` | artefact | Control |
| `other evidence` | evidence | any |
| `other artefact` | artefact | any |

**The two `other` rows are deliberate.** A Belt with a document that fits nothing
must still be able to upload it, and forcing a wrong role is worse than an honest
catch-all. A rising count of `other` is the signal that the vocabulary needs
extending — which is a governance event, not a code change.

---

## How this lands

Three commits, in this order. Nothing here is big-bang.

**1 — This amendment, as governance.** Spec only, no code: §23.2's seven fields,
§24's retrieval shape, §6's `citations` anchor and `consumed_at`, the `role`
vocabulary, ruling 3's revision, and a `DECISIONS.md` part recording all of it.
§23.5 binds: a schema change lands in the section before it lands anywhere else.

**2 — Step 6.12 as scheduled.** The ask, the binding, the manifest, `consumed_at`,
`load_evidence_series`. This works on `PhaseState` and the case blob and does **not**
depend on the index fields existing, so it is not blocked by commit 3.

**3 — A new step: the evidence index migration.** Schema add → write path →
backfill → filters, in that order, each provable on its own. Anything uploaded
between commits 2 and 3 is picked up by the backfill, because the case blob holds
everything the index needs.

**Two notes on the index migration.** No drop-and-rebuild is required: every one of
the seven fields is *additive*, and Azure assigns `null` to existing documents rather
than rejecting the change. And step 9.1 currently carries "the batched reindex
(evidence + case indexes)" as ⏸ external — its evidence half is superseded by this
step, and 9.1 should be narrowed to the case index rather than left to imply the
evidence work is still external and blocked.

---

## The upload sequence, and what is actually parallel

Stated precisely, because asserting parallelism where a dependency exists is itself
a defect.

1. **Bytes arrive. Digest computed.** Deterministic, synchronous.
2. **Parse attempted.** Deterministic. On failure → 422 with a Belt-readable reason,
   and nothing is written anywhere (ruling 5, already built and proved).
3. **Supersession resolved.** Look up `(case_id, role)`. Same digest → this is not a
   new version; return the existing record and stop. Different digest → this becomes
   the current version, and the previous version's chunks are **deleted from the
   index**. Its blob stays.
4. **Shape checked** against the ask, if there was one. A mismatch sets
   `shape_match` and does not stop the upload — a mismatch is a coaching question,
   not a refusal (ruling AP2.5 governs unreadable files, not incomplete ones).
5. **In parallel:** the blob write ∥ the interpretation model call.
6. **Index write.** Depends on both — it needs `description` from the model call and
   `blob_path` from the blob write.
7. **`UploadRecord` and the `PhaseState.uploads` entry.**

**Step 5 is the only genuine parallelism.** Parse cannot overlap interpretation,
because ruling 4 feeds the parse *result* to the model — that is precisely what
makes it one cheap call instead of shipping the whole file.

**The interpretation is already structured.** `UploadInterpretation` is a Pydantic
model with `summary`, `supports`, `caveats` and its two source fields. It is not
plain text today. The only open question about it is *how the structure is bound* —
by schema or by hand-parsed JSON — which is G-48, not a schema question.

**An asynchronous variant is available and not required.** Returning 200 after step
4 with `indexed=pending` and running 5–7 in the background would keep uploads fast
during a coaching turn. `UploadRecord.classification` already carries
`<indexed|pending>`, so the design anticipated it. Synchronous is simpler and 6.12
does not need async — this is a founder call, not a constraint.

---

## Sequencing and cost

The reindex is the expensive event and **it has not run**. 9.1 is currently ⏸
external. This amendment makes 9.1's scope larger but not later. Adding any of these
fields after 9.1 buys a second reindex, so the cheap moment to decide is now.

Nothing here blocks 6.12 from starting, provided the schema is ratified first so
that 6.12 writes the metadata keys as it goes.

---

## Left open for the founder

1. **Is `role` a controlled vocabulary or free text?** Controlled filters reliably
   and makes "the current cycle-time data" a well-formed query; free text is easier
   on the Belt and will drift. Recommendation: controlled per phase, drawn from the
   SKILL.md worked examples that already carry the asks.
2. **Synchronous or asynchronous indexing** (steps 5–7 above).
3. **Retention for superseded versions.** Production practice is delete-and-insert
   per commit with a short rollback window rather than keeping every revision and
   filtering forever. This interacts with step 8.7, which already owes a deletion
   behaviour for orphaned upload blobs.

---

# Appendix — dry run

**Case `IMPR-2026-ED8`, invoice handling, Measure phase.** Eight events traced
through the design above. Five of them broke something; the amendment has been
corrected accordingly, and this appendix is the evidence.

### 1 — The coach asks

Measure coach: *"To set the baseline I need cycle times per station — one row per
observation, with station, cycle_seconds, operator and date, over the last 30 days."*

Ask `A1` recorded: `role = "cycle time data"`, `phase = measure`,
expected shape `{station: str, cycle_seconds: num, operator: str, date: date}`.

### 2 — The Belt uploads `cycle_times.xlsx`

Digest `d1`. Parse yields four columns, 120 rows, `cycle_seconds` decimal 12–63.
No prior `(ED8, "cycle time data")`, so this is version 1. Blob write and the
interpretation call run in parallel; the index write follows both.

Shape check against `A1`: **full match.**

> **FINDING 1 — nowhere to record the shape check.** A `partial` result had no home.
> A file missing `reason_code` would be stored, indexed and described exactly like a
> complete one, and the next session's coach would retrieve it and treat it as
> answering the ask. The mismatch would live only in a conversation nobody re-reads.
> **`shape_match` added to the schema.**

### 3 — The Belt uploads the as-is process map, unprompted

No ask. The Belt declares purpose "process map".

> **FINDING 2 — the classifier sends it to the wrong side.** The 6.11 live run
> mapped `purpose=Process map` to `kind=artefact`. An **as-is** map describes
> reality; it is evidence. Filed as an artefact it is filtered out of evidence
> retrieval by default, so the coach loses the current-state description at exactly
> the phases that need it. **`kind` now derives from a controlled `role`**, which
> distinguishes as-is from to-be at the point of declaration.

### 4 — The Belt re-uploads the identical file

Digest `d1` again, matching the current digest for `(ED8, "cycle time data")`.
Not a new version. No blob write, no index write, no version increment — the
existing record is returned. **Works as designed; this is what the digest is for.**

### 5 — The Belt uploads a corrected file

`cycle_times_v2.xlsx`, digest `d2`. Same role, different bytes → version 2
supersedes version 1.

> **FINDING 3 — `is_current` costs more than it is worth.** Flipping the flag on
> version 1 means rewriting an already-indexed document, and the write path is
> add-or-replace by id with no partial update — a re-chunk and re-embed to change
> one boolean. **Superseded chunks are now deleted from the index instead**, the
> flag is gone, and the case blob keeps the history.

> **FINDING 4 — deletion would have broken citations.** A gate document that cited
> version 1 by index id would point at nothing once version 1 was deleted.
> **Citations now anchor on `blob_path` + `content_digest`**, which survive
> supersession and are precisely what step 7.6's cascade needs in order to notice
> that an approved gate rested on a file that has since changed.

### 6 — The coach runs a capability study

`rag_lookup_evidence("cycle time data")` returns the record for version 2 —
role, description, phase, `blob_path`, digest. The coach calls
`load_evidence_series(blob_path, "cycle_seconds")` and receives `n=120`, mean,
sigma, min, max. It then calls `calculate_cpk` with those scalars plus the spec
limits, which the Belt supplies in conversation because they are not in the file.

**No figure is ever transcribed**, which is the clause 6.12 owed.

> **FINDING 5 — the loader had no data to read.** The draft said it reads parsed
> values "from the case record". It cannot: `UploadRecord.rows` is a row *count*,
> and the values are stored nowhere. **The loader re-parses the blob** with the
> parser 6.11 already built — one source of truth, milliseconds, no second copy.

### 7 — Leakage check

Query *"what is our approval process"* under the default `kind eq 'evidence'`
filter. The control plan draft (artefact) does not surface. The as-is process map
does — correct under Finding 2's fix, and the opposite of what the design would
have done before it.

### 8 — Cross-phase check

A Control Belt asks for the Measure baseline. `phase`'s filter defaults OFF by
§23.2, so it is reachable. Supersession does not touch it, because Control's
post-improvement data carries a different `role` and therefore never supersedes the
baseline. **Works.**

---

## What the dry run changed

| # | Finding | Fix |
|---|---|---|
| 1 | A partial shape match had nowhere to live | `shape_match` field added |
| 2 | As-is and to-be maps collapse to one purpose string | `kind` derives from a controlled `role` |
| 3 | `is_current` requires rewriting indexed documents | Delete superseded chunks; flag removed |
| 4 | Deletion breaks citations by index id | Citations anchor on `blob_path` + digest |
| 5 | The loader had no stored values to read | It re-parses the blob |

Findings 2 and 3 are the substantive ones. Finding 2 was already latent in the
shipped 6.11 code, not introduced by this amendment — the live run recorded
`purpose=Process map → artefact` and nobody noticed what that would cost once
artefacts became retrievable.

---

## Appendix B — how the dry run was done, and what it does not prove

**Method, in order:**

1. Took the ratified rulings (Part AP2) and the field definitions in §23.2, §6 /
   S-C02 and S-C09 as the specification — read from the live tree, not from memory.
2. Fixed a concrete scenario with real values: one case, one phase, four documents,
   one deliberate re-upload and one deliberate correction.
3. Walked each event through the sequence step by step, **writing down the actual
   field value at each step** rather than describing the step.
4. At every step asked three questions: *does a field exist to hold this value; does
   the operation this step requires actually exist in the write path; does this
   contradict a ruling already taken.*
5. Chose the events to include failure shapes, not only the happy path — an
   identical re-upload, a correction, an ambiguous document type, a cross-phase read
   and a leakage check.

**What this establishes.** Findings 1, 4 and 5 are structural: a value had no field,
or a reference would dangle. Those hold on the documents alone. Finding 2 rests on a
fact recorded in the 6.11 live-run report — `purpose=Process map → kind=artefact` —
which is observed behaviour, not inference.

**What it does not establish, and one thing it got wrong.** Nothing was executed.
Finding 3 originally rested on a claim about the library — that the write path offers
no partial update — and **that claim was false.** Azure AI Search supports
`mergeOrUpload`; only LangChain's wrapper lacks it. The finding's conclusion survived
re-argument on different grounds (see Amendment A), but the premise did not, and it
was caught by checking the vendor documentation rather than by the dry run. **A dry
run tests a design against the documents it was run against. It does not test the
documents.**

**This project has learned twice that a document can be confidently wrong** — a
commit body asserting an edit that was never made, and 781 green tests over a dead
code path. A dry run is a cheaper instrument than either, and no more authoritative
than what it was run against.
