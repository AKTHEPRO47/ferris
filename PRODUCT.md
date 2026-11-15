# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Researchers and analysts who need to inspect regional climate records, judge the strength of a trend claim, and see how an estimate was produced. They arrive to check evidence rather than to be persuaded, and they expect methods, uncertainty, and source provenance to be reachable from the result.

## Product Purpose

Ferris is an Earth-data workspace for exploring real NASA POWER climate records and NASA GIBS imagery, and for demonstrating a rigorous, reproducible scientific pipeline. Success means an analyst can move from a regional question to a defensible, caveated result — and regenerate that result from the shipped data and scripts.

## Positioning

Every published chart, test, model, and scenario is regenerated from raw NASA-derived records by scripts in the repository, and every result carries its uncertainty, validation, and limitations in the interface. A neighboring climate dashboard could copy the visual presentation but not the claim that its outputs are reproducible end to end and honest about what they do not establish.

## Operating Context

- Prepared monthly records live in `data/raw`; Python scripts produce the JSON artifacts served by the site.
- Analysts compare regions, inspect seasonal anomalies and residuals, export evidence as JSON, and read methods, catalog, FAQ, and reports.
- Satellite browsing uses dated NASA GIBS browse imagery for geographic context.
- Machine-learning work trains in Python and runs inference in the browser, including held-out historical-month testing and editable inputs.
- Scenario and paired-data tools are exploratory: users supply or declare inputs, and the tool reports what those inputs can and cannot support.

## Capabilities and Constraints

- Six NASA POWER temperature/rainfall investigations covering 2001–2025.
- Trend estimates with HAC uncertainty, seasonal anomalies, residual diagnostics, and evidence export.
- Interactive 3D Earth and dated satellite browse imagery.
- Guided discovery, browser-local notebooks, and a rule-based evidence assistant.
- Regional Contradiction Atlas with adjusted significance tests.
- Green Mirage: paired vegetation/fluorescence import plus an explicitly synthetic teaching example.
- Digital Twin Lite: conditional regional scenarios with validation baselines.
- Machine Learning Lab: six trained ridge models, held-out testing, custom-input predictions, and model export.
- Editable research drafts, methods, catalog, FAQ, and educational examples.
- Constraints: no fabricated evidence; reproducibility must stay intact; scientific caveats remain visible; the site is static and browser-local, with no accounts or server state.

## Brand Commitments

- Name: Ferris, presented as "Ferris Earth Intelligence".
- Voice: scientific, caveat-forward, plain-language where possible; never overstates causality.
- Existing identity uses an Earth/orbital framing with a text wordmark, `earth.jpg`, and a PDF research report.

## Evidence on Hand

- Original NASA responses in `data/raw` (Borneo, Singapore, Sumatra).
- Generated artifacts in `apps/web/public`: `missions.json`, `atlas.json`, `twins.json`, `ml-models.json`, `evidence.json`.
- Scientific checks in `tests/` and reproduction steps in the README and `docs/advanced-features.md`.
- `apps/web/public/reports/Ferris_Eight_Features.pdf` as the existing report asset.
- No real paired NDVI/SIF dataset is bundled; the Green Mirage example is explicitly synthetic. Do not invent testimonials, customers, benchmarks, or deployment claims.

## Product Principles

1. Show the evidence chain: a result is only as credible as the method and provenance beside it.
2. Reproducibility is a product feature, not documentation debt.
3. State limits in the same breath as findings; uncertainty is part of the answer.
4. Keep analysis inspectable — exports, editable inputs, and visible model assumptions.
5. Prefer honest exploration over persuasive conclusions.
