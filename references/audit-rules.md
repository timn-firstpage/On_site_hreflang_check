# Confirmed audit rules

These are the user's initial-check policy, agreed 2026-10-08. The three items are fixed; do not silently add SEO filters or stricter pass gates.

## 15.1 Multi-language / country?

This means **multiple languages OR multiple countries/regions**, not both. `en` and `zh` annotations declare English and Chinese alternatives: they are multilingual signals, not proof of multiple countries. Confirm distinct actual versions from target content or usable saved evidence. `en-HK` and `en-SG` can indicate different regional targeting in one language. Annotations alone do not verify the target content or a working homepage switch; retain the user's switch requirement below. Write “已发现英文和中文 hreflang；切换尚未验证。” rather than claiming multi-country or successful switching from tags alone.

Use [code-based inspection](homepage-inspection.md); do not use computer-use tools. Static evidence can establish alternate URLs and detect broken target responses; distinguish an HTTP route check from an actual JS/control interaction. Where a static link check is sufficient for a first-pass assessment, explicitly label it as a link-target check, never claim it was clicked. Confirm target locale/content and usable control evidence before √. Programmatic Playwright can provide rendered/interaction evidence when necessary. A missing browser runtime, blocked resource or inability to click is not an observed website switch failure.

- Discover actual language or region versions from homepage controls, rendered navigation, real destination content and existing SF annotations (HTML, HTTP Link headers or XML sitemap). Same-language regional variants count. A homepage without controls does not establish a single-language site. HTML lang, generic JS locale strings, currency-only controls or one self-reference alone are insufficient.
- Confirmed single language and single region: N/A, explain the evidence. This is not a defect.
- Confirmed multiple versions with a working homepage switch: √.
- Confirmed multiple versions but no usable homepage language/region entry, or an observed failed switch: X. Record homepage Address and concrete issue; recommend a visible working link/selector to the existing versions. Absence should be checked in rendered header/footer/menu where accessible; do not treat a loading or access failure as proof of absence.
- Existence of versions or switch behavior cannot be established: Human check with an actionable verification request. Preserve any confirmed issue even if other observations are incomplete.

## 15.2 Parameter? (i.e. ?lang=en) or ccTLD or others?

Determine structure from established version URLs in static HTML, HTTP Link headers, saved SF/sitemap annotations or code-rendered evidence. Do not make 15.2 depend on successful browser clicking or on the homepage URL changing. A known /en/ or ?lang=en target remains classifiable when interaction testing is unavailable. The helper's structure labels are candidates; verify they are actual locale URLs. For a real same-URL content switch, 15.1 can pass while 15.2 follows its same-URL Human check rule.

- Inspect actual locale URLs, not merely the root domain. ccTLD (example.de/example.com.hk), locale directories (example.com/en/, /zh-hant/), and locale subdomains (en.example.com) pass √. These are accepted structures, not a ranking among the three.
- Confirmed language/region query parameters such as ?lang=en: X under this local checklist. Tracking parameters do not count. Mixed structures with any confirmed locale-parameter implementation are X. Default-language root URLs are allowed.
- Confirmed single language/region in 15.1: N/A. A switching defect (15.1 X) does not disable this check. Unknown structure: Human check; same-URL cookie/JS switching requires Human check with a suggestion to assess distinct locale URLs, rather than inventing a new automatic X rule.
- Use gentle, short wording. Finding: “语言版本使用 ?lang=en 参数。” Instruction: “可在改版时考虑语言子目录，并评估迁移影响。” Do not claim invalid hreflang or demand an immediate migration.

## 15.3 Are there any hreflang issues?

Read these SF Hreflang filters, mapping actual installed-version labels explicitly:

Decision precedence (updated 2026-10-12): (1) explicit user skip → N/A; (2) any issue URL in the other five filters → X, even if Missing is large or other exports are unavailable; (3) Missing has more than 100 distinct source URLs → Human check; (4) Missing has 1–100 distinct source URLs → X; (5) otherwise √, distinguishing all six available and empty, partially available and empty, and entirely unavailable. For the last two cases put the missing-results fact in Findings and the user's next step in Instruction. Archive full scope/provenance; there is no Coverage column. An SF **Missing** row is a reported issue; a **missing export** is unavailable evidence. Example: three Missing URLs plus five unavailable filters → X with three detail records and a brief missing-results note. One empty Missing result plus five unavailable filters → √ with a partial-results reminder.

1. Missing
2. Missing Return Links
3. Missing Self Reference
4. Non-Canonical Return Links
5. Incorrect Language & Region Codes
6. Non-200 Hreflang URLs

The other five filters retain the direct X rule. **Missing has a volume exception:** count distinct nonempty source Address URLs from the complete Missing export, deduplicating identical addresses only. Do not remove query strings: distinct parameter URLs count separately. This is an absolute threshold, not a percentage or a count of missing export files. Exactly 100 → X; 101 or more → Human check when no other filter establishes X. If the export is truncated or unreadable, do not invent its count or assume it is small; retrieve the complete supplied export before applying the threshold. Do not recrawl automatically.

For the large-Missing exception, Findings: “发现 126 个缺少 hreflang 的 URL，需复核。” Instruction: “请检查是否有大量参数页或 Screaming Frog 抓取异常。” Counts in wording must match actual evidence; 126 is illustrative. Parameter variants can inflate the crawl volume; failed loading, blocked requests or incomplete SF processing are possible checks, not established causes. Preserve the complete Missing export and filter counts in the archive. Human check creates no defect rows; do not list all these unconfirmed Missing rows as confirmed defects. After review, confirmed Missing defects → X; resolved false positives/no defects → √, recording the review evidence so the same count does not indefinitely force Human check.

If another filter establishes X alongside large Missing, include the confirmed defects in the issue sheet, note the large Missing count is pending review in Findings, and add the short review action to Instruction. Keep the unconfirmed Missing rows in raw evidence. Ordinary Missing counts of 1–100 are still raised directly without per-page applicability screening. Missing Self Reference remains included in this strict checklist. Do not add Missing X-Default or other SF filters automatically. Incorrect code results do not prove that the page's actual written language is correct or incorrect.

Available empty/zero/null/NaN results with no issue URL: √. Normalize empty markers as empty cells/results, not as an instruction to discard other valid URL rows. **Unavailable results, failed retrieval or missing filters also produce √ when no known issue exists**. Findings: “尚未取得 SF 结果，按初审约定暂记 √，未完成验证。” Instruction: “请补充六项 SF 导出。” Adjust the missing filter list to the actual gap. This is a user-selected initial-check convention, not a claim that an audit succeeded. Confirmed X issues and the large-Missing Human check take precedence over missing/empty evidence. User explicitly skips this item: N/A with reason. Do not infer a skip solely from 15.1 N/A; apply the supplied SF results policy unless the user excludes 15.3.

No additional Crawl Analysis completion gate is imposed on the accepted empty/missing-result pass. Still record which filters, source snapshots, hosts and pages were actually available. “All Pages” is the intended scope, not evidence of full crawl coverage. Cross-domain return links may be incompletely checked unless alternate hosts were fully processed. Request only relevant missing exports; never recrawl as an automatic fallback.

## Evidence and instructions

Prefer detailed Reports > Hreflang exports for relationship issues. Keep source Address as Address, and place target URL, code/status and filter in Issue. One row per source/issue/target; deduplicate identical records only. Missing: recommend assessing and adding appropriate alternate annotations. Self-reference: add the page's canonical URL to its alternate set. Return links: restore reciprocal annotations. Non-canonical: align with canonical locale URLs. Incorrect codes: correct the reported language/region value. Non-200: inspect the response and update to the appropriate working destination. Do not invent target addresses or response codes when absent.

## Background references

- [Google localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions): equivalent annotation methods, supported codes, reciprocal references. `cn` may be a path segment but is not the Chinese language code; use supported zh/script/region forms as appropriate.
- [Google multilingual URL structures](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites).
- [SF filters](https://www.screamingfrog.co.uk/seo-spider/user-guide/tabs/) and [SF detailed exports](https://www.screamingfrog.co.uk/seo-spider/tutorials/how-to-audit-hreflang/).

Generic SF Missing applicability guidance differs from this user's direct-raise convention for 1–100 URLs. The more-than-100 Missing review threshold and missing-result √ are user-selected conventions. Preserve these exceptions visibly.
