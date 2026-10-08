# Confirmed audit rules

These are the user's initial-check policy, agreed 2026-10-08. The three items are fixed; do not silently add SEO filters or stricter pass gates.

## 15.1 Multi-language / country?

- Discover actual language or region versions from homepage controls, rendered navigation, real destination content and existing SF annotations (HTML, HTTP Link headers or XML sitemap). Same-language regional variants count. A homepage without controls does not establish a single-language site. HTML lang, generic JS locale strings, currency-only controls or one self-reference alone are insufficient.
- Confirmed single language and single region: N/A, explain the evidence. This is not a defect.
- Confirmed multiple versions with a working homepage switch: √.
- Confirmed multiple versions but no usable homepage language/region entry, or an observed failed switch: X. Record homepage Address and concrete issue; recommend a visible working link/selector to the existing versions. Absence should be checked in rendered header/footer/menu where accessible; do not treat a loading or access failure as proof of absence.
- Existence of versions or switch behavior cannot be established: Human check with an actionable verification request. Preserve any confirmed issue even if other observations are incomplete.

## 15.2 Parameter? (i.e. ?lang=en) or ccTLD or others?

- Inspect actual locale URLs, not merely the root domain. ccTLD (example.de/example.com.hk), locale directories (example.com/en/, /zh-hant/), and locale subdomains (en.example.com) pass √. These are accepted structures, not a ranking among the three.
- Confirmed language/region query parameters such as ?lang=en: X under this local checklist. Tracking parameters do not count. Mixed structures with any confirmed locale-parameter implementation are X. Default-language root URLs are allowed.
- Confirmed single language/region in 15.1: N/A. A switching defect (15.1 X) does not disable this check. Unknown structure: Human check; same-URL cookie/JS switching requires Human check with a suggestion to assess distinct locale URLs, rather than inventing a new automatic X rule.
- Use gentle wording in both finding and instruction. Finding: “目前使用语言参数区分版本，按本 checklist 列为可优化项。” Instruction: “可在后续网站规划时考虑采用语言子目录或子域名；建议结合现有收录情况与迁移成本评估。” Do not claim invalid hreflang or demand an immediate migration.

## 15.3 Are there any hreflang issues?

Read these SF Hreflang filters, mapping actual installed-version labels explicitly:

1. Missing
2. Missing Return Links
3. Missing Self Reference
4. Non-Canonical Return Links
5. Incorrect Language & Region Codes
6. Non-200 Hreflang URLs

Any issue URL in any listed filter is X. **Missing records are raised directly**, without screening whether a page needs alternatives. Missing Self Reference remains included in this strict checklist. Do not add Missing X-Default or other SF filters automatically. Incorrect code results do not prove that the page's actual written language is correct or incorrect.

Available empty/zero/null/NaN results with no issue URL: √. Normalize empty markers as empty cells/results, not as an instruction to discard other valid URL rows. **Unavailable results, failed retrieval or missing filters also produce √ when no known issue exists**, with an explicit reminder in Findings and an unverified/partial statement in Coverage. Example: “本次初审暂未发现问题；尚未取得此项 SF 结果，建议补充后确认。” This is a user-selected initial-check convention, not a claim that an audit succeeded. Known issues always win over missing/empty evidence. User explicitly skips this item: N/A with reason. Do not infer a skip solely from 15.1 N/A; apply the supplied SF results policy unless the user excludes 15.3.

No additional Crawl Analysis completion gate is imposed on the accepted empty/missing-result pass. Still record which filters, source snapshots, hosts and pages were actually available. “All Pages” is the intended scope, not evidence of full crawl coverage. Cross-domain return links may be incompletely checked unless alternate hosts were fully processed. Request only relevant missing exports; never recrawl as an automatic fallback.

## Evidence and instructions

Prefer detailed Reports > Hreflang exports for relationship issues. Keep source Address as Address, and place target URL, code/status and filter in Issue. One row per source/issue/target; deduplicate identical records only. Missing: recommend assessing and adding appropriate alternate annotations. Self-reference: add the page's canonical URL to its alternate set. Return links: restore reciprocal annotations. Non-canonical: align with canonical locale URLs. Incorrect codes: correct the reported language/region value. Non-200: inspect the response and update to the appropriate working destination. Do not invent target addresses or response codes when absent.

## Background references

- [Google localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions): equivalent annotation methods, supported codes, reciprocal references. `cn` may be a path segment but is not the Chinese language code; use supported zh/script/region forms as appropriate.
- [Google multilingual URL structures](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites).
- [SF filters](https://www.screamingfrog.co.uk/seo-spider/user-guide/tabs/) and [SF detailed exports](https://www.screamingfrog.co.uk/seo-spider/tutorials/how-to-audit-hreflang/).

Generic SF Missing applicability guidance differs from this user's direct-raise convention. Missing-result √ also intentionally differs from standard evidence-completeness scoring. Preserve these exceptions visibly.
