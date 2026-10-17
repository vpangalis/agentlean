# ADR-0099: Practice content: sources, licence gate and waves

Status: ACCEPTED (founder, 2026-10-17; drafted by Desktop, 2026-10-17). Scheduled after Define — no build now.
Requirements: R22 (Practice intelligence for Analyse and Improve)
Depends on: ADR-0098 "A fourth index: industry practice", ADR-0062 "PII handling"
Sources: [practice_index_downloads.csv](practice_index_downloads.csv)

## Decision

1. **Manifest first.** Every file is listed in a manifest (source, document, version, URL, industry, jurisdiction, licence status) before it is ingested. A file not in the manifest is skipped loudly, as the methodology ingest does.
2. **Licence status is mandatory:** open (reuse allowed), prototype_only (free to read or non-commercial; internal prototype only), licensed (permission obtained), client_private (customer's own).
3. **Wave 1 ingested:** rail and light rail + cross-industry sources. Other industries (telecom, banking, …) are listed in the manifest but not ingested until a customer in that industry is in view.
4. **Before the first paying customer:** all prototype_only content is removed or licensed — one filtered delete on `licence`.
5. **Customer-private content only after a signed contract** (with a data-processing agreement): uploaded into the same index with `tenant` = that customer, never visible to others, deleted on contract end. Demos to prospects use open content and the founder's write-ups only.

## Rejected

Ingesting without a licence record; customer documents before a contract.
