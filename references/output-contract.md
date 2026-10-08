# Report and findings contract

Filename: `Onsite_hreflang_{site_name}_{audit_date}.xlsx`, date YYYY-MM-DD. Invalid filename characters are sanitized; excessively long names are rejected. A unique writable run directory prevents overwriting prior reports.

Always create `Checklist`: `Item No. | Item Name | Check Result | Findings | Coverage`.
Create `15. HREFLANG` only when at least one result is X: `Address | Issue | Instruction`.
All three checks appear exactly once, ordered 15.1–15.3. Results are √ / X / N/A / Human check. All X checks must have one or more issue records; other results have none. Issue text starts with its item number in Excel. Human check next steps remain in Findings. No screenshots column or extra worksheets. No customer strings are executed as formulas.

## Easy-to-read wording

All customer-facing text (Findings, Issue, Instruction, Coverage and missing_evidence_note) must be easy for a non-specialist to read, in the configured report language. This is an agent writing requirement, not a keyword test in the generator.

- Lead with what was found. Prefer one or two short sentences per finding or instruction; use line breaks for separate facts. Keep one issue per detail row. Preserve necessary URLs, counts and limitations even when more text is needed.
- Use familiar words and concrete actions. Avoid unexplained jargon, stacked abbreviations, long policy explanations and generic instructions such as “optimize hreflang.” Keep exact SF filter names for traceability, alongside a plain-language explanation when needed.
- Findings summarizes the observed result. Issue identifies the specific problem and affected target when known. Instruction says what to check or change. Coverage states the actual source/scope and what remains unchecked. Do not repeat the entire finding in all columns.
- Do not invent counts, affected targets, causes or SEO impact to make prose sound complete. Missing evidence must stay explicit, including on a √ result. Use neutral language for defects and gentle suggestions for parameter URL improvements.
- Example finding: “网站有中文和英文版本，首页可正常切换。” Example issue: “英文页面没有 hreflang 链接指回中文页面（Missing Return Links）。目标页面：〔实际 URL〕。” Example instruction: “请在英文页面添加指向对应中文页面的 hreflang 链接。”
- Missing-evidence reminder: “尚未取得 SF 结果，本次先记 √。请补充结果后确认。” Coverage: “未取得六项 SF 结果，尚未验证。” Partial coverage: “已读取 Missing，未发现问题。其余五项尚未取得。”
- Parameter finding: “语言版本使用 ?lang=en 区分，列为可优化项。” Parameter instruction: “可在后续改版时考虑语言子目录或子域名，并评估收录影响和调整成本。”

## Findings input

The agent reviews evidence and writes this schema; the generator validates and formats it, it does not crawl or independently judge SEO:

```json
{
  "site_name": "Example",
  "site_url": "https://example.com/",
  "audit_date": "2026-10-08",
  "checks": [
    {
      "id": "15.1",
      "item_name": "Multi-language / country?",
      "result": "√",
      "finding": "已确认英文和中文版本，首页切换正常。",
      "coverage": "首页渲染和两个版本的实际跳转。",
      "evidence_state": "available",
      "evidence": ["raw/homepage-observation.json"],
      "issues": []
    }
  ]
}
```

The fragment shows one row; real input requires all three. evidence_state is `available`, `partial`, `unavailable` or `not_applicable`. evidence is a list of actual archived evidence references; it may be empty for unavailable or skipped checks. Every finding/coverage is nonempty. X issue object: `{"address":"https://example.com/","issue":"15.2 语言参数版本：https://example.com/?lang=en","instruction":"可在后续规划中评估语言子目录。"}`. Use real source addresses; keep target/code in issue when known. Required X/Human check actions are written in instructions/findings respectively.

For 15.3 √ with partial/unavailable evidence, additionally require nonempty `missing_evidence_note`; the generator appends it to Findings and an explicit unverified notice to Coverage. It does not assert overall health. Other check passes require available evidence. N/A requires not_applicable; 15.3 skipping is explicit user instruction, not automatically inherited from 15.1.

Archive findings.json, manifest.json, complete raw exports and final workbook under ignored runs/. Evidence truth and required prose tone are agent responsibilities. The script validates types, IDs, statuses, issue inclusion and missing-evidence disclosure; it cannot verify the original crawl. Reopen verification covers text, sheet names and row counts. Inspect layout in a viewer, particularly long rows; avoid silently truncating evidence, retaining raw data separately.
