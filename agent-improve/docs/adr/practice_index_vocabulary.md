# Practice index: proposed vocabulary (draft, 2026-10-17)

Status: proposal by Desktop, not ratified. Validated against the downloaded documents in ingestion step 4 (sample check of ~50 chunks); entries are added, merged or renamed then.

## process_area (one per chunk)

| Key | Covers | Scope |
|---|---|---|
| sales_and_orders | bids, quotes, contracts, order entry, order changes | cross-industry |
| project_management | project planning and execution, milestones, project risk | cross-industry (central in rail) |
| procurement | sourcing, supplier qualification, purchasing, supplier performance | cross-industry |
| logistics_and_supply_chain | planning, inbound, warehouse, inventory, distribution | cross-industry |
| production | manufacturing, assembly, testing, work instructions, shop floor | manufacturing only |
| engineering | requirements, design, design reviews, verification and validation, homologation | industry-specific content |
| change_and_configuration | engineering change requests, change boards, baselines, document control | cross-industry, strongest in engineering firms |
| quality | inspection, nonconformance, audits, corrective actions | cross-industry |
| maintenance_and_service | maintenance, repair, field service, warranty, spare parts | cross-industry, rolling-stock specifics |
| customer_service | complaints, enquiries, service desk | cross-industry |
| finance | invoicing, payables, receivables, closing, cost control | cross-industry |
| risk_and_compliance | risk assessment, safety, regulatory compliance, controls | cross-industry with industry variants |
| hr | recruiting, onboarding, training, competence | cross-industry |
| it_operations | IT incidents, IT changes, access, service management | cross-industry |

Industry-specific areas are added when an industry is onboarded, e.g. banking: lending, payments, treasury, kyc_and_onboarding.

## content_type (one per chunk)

| Key | Meaning | Used in |
|---|---|---|
| process_description | what the process is, its steps and roles | Measure (mapping), Analyse |
| typical_failure | known failure points and their usual causes | Analyse (candidate causes) |
| kpi_and_benchmark | how the process is measured, typical values | Measure, Control |
| practice | a proven way of doing it, a solution that worked | Improve |
| regulation_or_requirement | rules the process must meet | Define, Improve, Control |
| example | a worked example or case | any phase |

## Free-text and per-document fields

- process_step: extracted from the text at ingestion (e.g. "supplier qualification").
- industries, jurisdiction, source, version, url, section, licence, tenant: from the download manifest, per document.
