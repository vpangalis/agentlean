# Reference DMAIC case — IMPR-2026-0E5

**Reduce invoice handling errors** · Finance shared services · Green Belt · target 2026-12-31

This is the coaching reference for the case already sitting in your registry. It exists so
that every phase has real data behind it and I can tell you whether what the agent coaches
you toward is right or wrong. Nothing here is aspirational — every figure below is
recoverable from the five data files, and was verified statistically before this was written.

The data is synthetic but not arbitrary. It was generated with planted structure and then
tested to confirm the structure survives the analysis a Belt would actually run.

---

## The files

| File | Phase | Rows | What it is |
|---|---|---|---|
| `define_baseline_weekly.csv` | Define | 12 | Weekly error rate over the 12-week baseline |
| `measure_invoice_records.csv` | Measure · Analyse | 5,472 | Transaction-level detail, one row per invoice |
| `measure_msa_attribute_study.csv` | Measure | 180 | Attribute agreement study, 3 appraisers × 30 invoices × 2 trials |
| `improve_pilot_results.csv` | Improve | 12 | Six weeks before and after the pilot, email channel |
| `control_phase_pchart.csv` | Control | 10 | Ten weeks post-implementation, one special cause planted |

**Upload `define_baseline_weekly.csv` first.** Its first numeric column is
`error_rate_pct` — the metric itself — so the routed read resolves the right column and you
see the happy path.

`measure_invoice_records.csv` is deliberately the opposite: its first numeric column is
`month_end_period`, a 0/1 flag, not the metric. That file is the stress test for the
column-inference weakness — use it when you want to see the guess go wrong, not before.

---

## Define — what the data supports

Baseline period 2026-06-05 to 2026-08-21, twelve weeks, 5,472 invoices.

| Field | What the data gives you |
|---|---|
| **baseline_estimate** | 10.5% invoice error rate (575 of 5,472). Weekly range 7.04% – 16.01% |
| **target_value** | 3.0% |
| **target_date** | 2026-12-31 |
| **goal_statement** | Reduce invoice handling error rate from 10.5% to 3.0% by 31 Dec 2026 |
| **secondary_metrics** | Rework hours (153 h over 12 weeks ≈ 663 h/year); days-to-pay (18 days clean vs 31 days errored) |
| **metric_definitions** | *Invoice error* = any invoice requiring correction or re-entry before posting. Counted once per invoice regardless of number of defects on it. Denominator = all invoices received in the week. Source = AP workflow log |

**business_case** — the rework hours annualise to roughly 663 hours. You supply the loaded
hourly rate; at €45/h that is about €30k/year in rework alone, before late-payment penalties
or lost early-settlement discounts. Those two you will need to source from Treasury — I have
deliberately not invented them, because a Belt who cannot source his own financials has not
done Define.

**voc_summary** — the 13-day payment delay on errored invoices is the customer-facing fact.
Supplier complaints and any penalty correspondence are yours to bring.

**project_scope** — in: supplier invoices received through all three channels, EU entity,
from receipt to posting. Out: purchase-order creation, supplier master data, disputes
already in the escalation queue.

**process_map_sipoc** — Supplier → invoice (email PDF, portal, or EDI) → AP receipt,
validation, matching, coding, approval routing, posting → posted invoice → Treasury payment run.

**issues_and_barriers** — the measurement system is marginal (see Measure); month-end volume
peaks coincide with quality drops; tail suppliers are the hardest to move because they have
least incentive to change how they submit.

---

## Measure — the phase has its own finding

The attribute agreement study is not a formality here. It says the measurement system is
not yet trustworthy:

- Overall agreement with the reference standard: **78.9%**
- By appraiser: A 88.3%, B 83.3%, **C 65.0%**
- Within-appraiser repeatability: **68.9%**
- Kappa vs standard: **0.58** — marginal, below the 0.7 usually required to proceed

**The correct conclusion is that the baseline of 10.5% carries measurement error, and error
classification needs an operational definition and re-training before Analyse conclusions are
trusted.** If the agent coaches you past this without raising it, that is a coaching defect
worth recording.

Note also: this is attribute data, so attribute agreement analysis is the right study.
A Gage R&R would be wrong here, and if the agent proposes one, that is also a defect.

---

## Analyse — three real factors, one deliberate red herring

| Factor | Result | Significant? |
|---|---|---|
| **Channel** | email_pdf 16.6% · supplier_portal 7.1% · edi 3.2% | χ² = 185.9, p ≈ 4e-41 — dominant |
| **Month-end period** | 14.9% vs 9.4% outside it | χ² = 28.7, p ≈ 8e-08 |
| **Supplier tier** | tail 13.1% · preferred 9.6% · strategic 7.5% | χ² = 28.5, p ≈ 7e-07 |
| **Processor** | spread across seven operators | χ² = 6.65, **p = 0.354 — not significant** |

The processor result is planted on purpose. The obvious managerial instinct is to look for a
person, and the data refuses to support it. The causes are the intake channel and the
month-end volume spike — process, not operator. If the agent steers toward an individual, or
lets you do it, that is a finding.

**Pareto of error types:** missing_po 32.9% · price_mismatch 28.0% · tax_code 15.3% ·
qty_mismatch 13.6% · missing_approval 5.7% · duplicate 4.5%. The top two carry 60.9%, the
top three 76.2%.

The interaction worth reaching: missing_po is overwhelmingly an email_pdf failure, because
nothing on that path forces a PO reference at intake. That is the causal link between the
dominant factor and the dominant defect.

---

## Improve — the pilot

Mandatory PO validation at intake on the email channel, plus portal onboarding for the
twenty highest-volume tail suppliers. Six weeks either side:

- Pre-pilot **15.12%** (1,243 invoices) → post-pilot **6.51%** (1,183 invoices)
- Two-proportion test: **z = 6.80, p ≈ 1e-11**
- Relative reduction **57%**

Sound, and note what it is not: a designed experiment. It is a before/after on one channel,
so it cannot separate the validation change from the portal migration, and it is exposed to
anything else that changed in those six weeks. Naming that limitation is part of a good
Improve gate.

---

## Control — stability with one signal

Ten weeks post-implementation. Centre line **4.13%**, control limits computed per week
because subgroup size varies.

Week 7 reads **7.32%** against a UCL of **6.86%** — a genuine special cause, planted so the
control plan has something to respond to. Every other week sits inside the limits.

A complete Control gate needs the response plan for exactly that point: who notices, within
what time, and what they do.

---

## How to use this

The case is already created as `IMPR-2026-0E5`. Upload `define_baseline_weekly.csv` to it and
ask the coach a question that needs the file. Work the phases in order and tell me what the
agent asks and what it accepts — I will tell you whether it is coaching correctly, because
I know what the right answers are.

The data is reproducible: `generate_case_0e5.py` is seeded, so regenerating gives byte-identical
files.
