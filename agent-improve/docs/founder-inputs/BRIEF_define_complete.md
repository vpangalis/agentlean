# Brief for Claude Code: finish Define (M2 pilot, M2 later, M3)

From Desktop, 2026-09-30. Send AFTER the T69 / cost-ceiling prompt is pushed. The founder tests Define himself only when
all three milestones are finished.
Long-running brief: work in packages until the done-when is met, stopping only for the stop conditions below.
Save this file to `docs/founder-inputs/` (add; never replace the folder).

## Part 0: Record the pilot cut (founder ruling)

The founder rules the M2 pilot cut as proposed on 2026-09-30, with Desktop's corrections:

- **Pilot (41):** DEF-009, DEF-016, DEF-017, DEF-019, DEF-021, DEF-022, DEF-038, DEF-042, DEF-046, DEF-053,
  DEF-055, DEF-056, DEF-058, DEF-061, DEF-064, DEF-080, DEF-081, DEF-082, DEF-084, DEF-085, DEF-086, DEF-088,
  DEF-091, DEF-093, DEF-096, DEF-097, DEF-099, DEF-100, DEF-103, DEF-104, DEF-108, DEF-114, DEF-115, DEF-116,
  DEF-122, DEF-129, DEF-134, DEF-137, DEF-139, DEF-141, DEF-142
- **Later (20):** DEF-013, DEF-014, DEF-015, DEF-018, DEF-020, DEF-023, DEF-044, DEF-045, DEF-052, DEF-057,
  DEF-059, DEF-083, DEF-102, DEF-119, DEF-120, DEF-127, DEF-131, DEF-133, DEF-135, DEF-138
- **Retire (1):** DEF-051 (editing a field at the paused gate), because it conflicts with R6's amendment: changes are
  made through coaching, never by editing fields on the report screen. Retire the feature only; R6 is unchanged.

Set `pilot: true|false` on every M2 feature in the registry (rank.py --check must pass), so the board shows
"Ready for pilot" and "Before customers". If any id above is not an M2 feature at this commit, or an M2 feature is
missing from both lists, stop and report it; don't guess.
Commit trailer: `Ruling: 2026-09-30 M2 pilot cut 41 pilot / 20 later / DEF-051 retired`

## Part 0b: Housekeeping first (from Desktop review of 7181264)

1. **Re-prove M1.** Item 1 of the last prompt changed the executor and the lookup, so M1 reads 25 proven / 22 awaiting a
   fresh run. Run one live run-through on main (strict mode, tracing off) before Stage A; it must bring M1 back to 46/46
   under USD 1.50. If it doesn't, stop condition 3 applies.
2. **Rule 17 widening accepted:** it reads the generated layout and now covers 102 files. Keep it.
3. **Langfuse removal:** delete the unused settings fields in `core/config.py`, the `langfuse` pin in `requirements.txt`
   and the three names in the root `.env.example` (inventory row Z16). The founder removes the lines from his `.env` files.
4. Fix the mis-encoded character in the `/registry` handler's docstring and regenerate `docs/api-routes.md`.

## Part 1: The order of work (three stages)

1. **Stage A: M2 pilot (41 features)**, as below.
2. **Stage B: M2 later (20 features)**, in computed rank, once Stage A's done-when is met.
3. **Stage C: M3 (Should and Could, the open ones)**, in computed rank, once Stage B is proven.

Report at the end of each stage with the board counts; don't stop between stages unless a stop condition applies.

### Within Stage A

- **DEF-108 first.** Its run-through check is G-143's open prevention (D7).
- Then the computed rank (ADR-0058) within the pilot set. Structural work (data, audit, persistence, schema:
  DEF-038, DEF-061, DEF-082, DEF-097, DEF-115, DEF-021, DEF-022) must come before the screens that show it. If
  the computed rank puts a screen before its data, report it rather than overriding the rank silently.
- Keep packages of about 60 minutes, one feature group each.

## Part 2: How to work (same loop as M1)

- Fast tests per commit, full suite once per package and before every push.
- A live run-through only after a change to coaching behaviour, or at the end of a package that touched the
  journey; strict mode, tracing off. Every live run must stay under the USD 1.50 ceiling and keep M1 at 46/46.
- Board freshness rule applies: a feature proven on earlier code counts as awaiting a fresh run.
- Every defect found gets a G-number and an 8D (occurrence and escape cause) before its fix.
- Do not touch the parked items (coach charter, decision-trail extension, EU AI Act purpose statement).
- Update `docs/board_waiting.md` whenever something needs the founder.

## Stop conditions (stop and report; don't work around)

1. A requirement looks wrong, missing or conflicting (it needs a founder ruling).
2. A design choice with real alternatives that no ADR covers.
3. M1 drops below 46/46 and the cause isn't found in one package.
4. A live run exceeds USD 1.50 or a turn exceeds 45 s.
5. The guard blocks an ordinary Belt message (T91).
6. Anything that would need a key, a secret or an Azure change from the founder.
7. Two packages in a row move no feature to "proven".

## Done when (per stage)

**Stage A**

- All 41 pilot features are proven on current code (green on the board, none awaiting a fresh run).
- M1 is 46/46; two consecutive clean live run-throughs on main in strict mode, including an upload whose
  interpretation appears in the report, both under USD 1.50.
- `docs/board_waiting.md` lists only open founder decisions.

**Stage B:** all 20 "later" features proven; M1 46/46; one clean live run under USD 1.50.

**Stage C (Define complete):** every Define feature not marked Won't is proven on current code (the board's
"All of Define" shows no amber or grey), M1 46/46, and two consecutive clean live run-throughs on main in strict mode,
including an upload, each under USD 1.50. Then write `docs/board_waiting.md`: "Define complete, ready for the
founder's test".

## Report (after every package)

| Package | Features proven | Commits | Live run? cost | M1 | Stop? |
|---|---|---|---|---|---|

End each report with the counts per milestone (proven / built / not started for pilot, later and M3) and a timing line.
