---
name: onsite-audit-hreflang
description: Audit multilingual discovery, locale URL structure and Screaming Frog hreflang results using shared onsite configuration, and produce a checklist Excel report with a conditional issue sheet.
---

# Onsite Hreflang Audit

Produce `Onsite_hreflang_{company name}_{YYYY-MM-DD}.xlsx` for checks 15.1–15.3. Read [audit rules](references/audit-rules.md) and [output contract](references/output-contract.md) before judging evidence. These user-selected first-check rules take precedence over generic SEO recommendations.

## Workflow

1. Obtain site/company, supplied global config and existing crawl/exports. Read [shared configuration](references/shared-config.md). Honor `checks.hreflang=false` by not running this flow. Reuse site-matched evidence and the common handover; do not reload a profile per audit.
2. Preflight a writable unique run directory and Python with openpyxl before expensive retrieval. Resolve paths on the executing host; do not assume another user's runtime or Downloads path. Use the supplied config directory as the base for relative paths.
3. For supplied `.seospider`, follow the shared saved-crawl contract: reuse exports or open once using verified supported SF operations, preserve active/unsaved sessions, and fall back once to manual saved-crawl Open plus exact exports. Never deserialize arbitrary binaries. `allow_new_crawl=false` still allows reading saved evidence. New preparation, when permitted and needed, belongs to `sf-shared-config`; it owns profile selection, sitemap confirmation and manual Start.
4. Use the Python code workflow in [homepage inspection](references/homepage-inspection.md) for 15.1/15.2. No computer-use, native UI or browser-control MCP capability is required or to be invoked. Start with saved HTML/SF evidence or bounded HTTP parsing. Read discovered hrefs, options, hreflang and target responses before considering optional programmatic Playwright rendering. Classify actual alternate URLs independently of click success. Never ask for desktop control as a prerequisite. JS-only behavior uses the optional code runner if available; missing runtime/blocked resources are evidence limitations, not website defects. A JS library string, HTML lang, or single self-reference alone does not prove multiple versions. Record exactly which URL/content changed and which interaction was tested; avoid vague “could not verify switch” findings.

   Use the shared 2-second minimum request interval (configurable via budget.min_request_interval_seconds). On any HTTP 429, stop further live requests in that run, including optional rendering. Record Retry-After and retry_not_before in the shared manifest; do not immediately rerun or switch clients to escape the limit. Retain usable cached/SF evidence. A live homepage 429 is an access limitation, not proof of failed switching; preserve the separate six-filter policy for actual SF findings.
5. Read complete SF Hreflang exports using the six filters in the rules. Retain source Address, target URL, language value and error detail where present. An issue in Missing is raised directly under this checklist. Do not add page-applicability screening. Do not infer missing export rows from a truncated preview.
6. Write reviewed `findings.json` using the output contract, including its easy-to-read wording rules. Use short, plain sentences in Findings, Issue, Instruction, Coverage and missing-evidence reminders; explain technical terms when needed, state the observed result first, and give a concrete next step. Missing SF evidence is the explicit 15.3 exception: tick √ with a missing-result reminder and unverified Coverage, unless any known issue makes the result X. Never describe this as verified website health. Other uncertain judgments use Human check.
7. Run `python scripts/build_report.py --input <findings.json> --output-dir <unique-run-directory>`. It validates structure, writes literal text, verifies the saved workbook and refuses overwrite. Inspect worksheet layout, especially long issue text, using an available spreadsheet renderer or viewer. Preserve evidence and findings on failure; rerun only the affected export step after correcting the error.

## Delivery

Always return the three-row Checklist. Create `15. HREFLANG` only when any check is X; include every X's issue details. Report first-check exceptions and actual crawl scope/date. Do not claim an all-pages clean audit when coverage is partial or unavailable. Read [README](README.md) for installation, examples and testing. No site repair, automatic crawling, scheduling, messaging or GitHub publication is included in invocation.
