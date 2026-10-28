# ADR-0089: A case carries its location — country and site — chosen from lists the customer ships as configuration

Status: ACCEPTED (founder, 2026-10-28, review of the wave-0 report, ruling 2; drafted by Claude Code 2026-10-16 from the founder's ruling of 2026-10-15 on W20)
Requirements: W20 (ACCEPTED 2026-10-15), R16 (audit trail), C5 (ships inside the intranet); finding 1 of 2026-10-15, finding 1 of 2026-10-27 (G-274, G-342)
Depends on: ADR-0065 (T88: schema version and migration), ADR-0066 (the case record holds what is decided)

## Context

The create form has a department, but no country or site (finding 1). For multi-country use, the case
list must be filterable by location, and the Define report must name it.

## Decision

1. The case record gains `location: {country, site}`. Both are required at creation.
   - `country` is an ISO 3166 code from a standard list.
   - `site` is chosen from the customer's site list for that country.
2. The site lists ship per customer as configuration (`config/sites.json`, C5): no directory lookup, no
   network call. Until a customer ships its list, a small sample list ships so test cases can pick a site:
   Austria: Vienna, Linz; Germany: Munich (founder, 2026-10-28).
3. The location is shown in the header, in the case list (filterable), and in Define report section A.
4. The project lead can change the location. Each change is written to the case record (a decided value,
   ADR-0066) with an audit entry (R16).
5. Schema bump with a migration: existing cases read `location` as "not set". The lead is asked to set it on
   the next open.

## Rejected

- **Free text**: breaks the filters and the per-site reports.
- **A directory lookup**: needs single sign-on (R8), which is before customers.
