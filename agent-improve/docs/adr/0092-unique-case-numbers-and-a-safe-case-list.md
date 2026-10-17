# ADR-0092: A case number is reserved by a create-only-if-absent write and retried on conflict; the case list is updated by a conditional write

Status: ACCEPTED (founder, 2026-10-17, with ruling a; drafted by Claude Code from the founder's build item 5)
Requirements: W6, T96 (PROPOSED: case numbers unique); findings 7, 8; G-219
Depends on: ADR-0024 (one case number), the Blob case store

## Context (verified 2026-10-15)

- The number is `IMPR-<year>-` followed by 3 hex characters from uuid4: 4,096 numbers a year. A clash fails
  the creation; there is no overwrite and no retry.
- `registry.json` is loaded, appended to and saved with no ETag, so two cases created at the same moment
  lose one list entry. The case's blob still exists.

## Decision

1. **The suffix gets 6 characters** from an alphabet without look-alikes (0/O, 1/I): about 10⁹ numbers a
   year, so retries are rare.
2. **The number is reserved** by writing the case blob with "create only if absent" (Blob `If-None-Match:
   *`). On a conflict a new number is drawn, up to 5 times; a sixth conflict is a readable error (W10).
3. **The case list is updated** by a conditional write (`If-Match: <ETag>`), re-read and retried on a
   precondition failure.
4. **Existing case numbers stay unchanged** (ruling a): the case number is the thread id (ADR-0024 "The
   thread id is the case id"); only new cases get the longer suffix.
5. **Proof**: many cases created concurrently produce no duplicate number and no lost list entry; a
   forced collision is retried, never overwritten.

## Rejected

- **A counter blob**: one more contended write.
- **A longer uuid prefix without the conditional write**: rare clashes still fail.
