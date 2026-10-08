# Report and findings contract

Filename: `Onsite_hreflang_{site_name}_{audit_date}.xlsx`, date YYYY-MM-DD. Invalid filename characters are sanitized; excessively long names are rejected. A unique writable run directory prevents overwriting prior reports.

Always create `Checklist`: `Item No. | Item Name | Check Result | Findings | Coverage`.
Create `15. HREFLANG` only when at least one result is X: `Address | Issue | Instruction`.
All three checks appear exactly once, ordered 15.1–15.3. Results are √ / X / N/A / Human check. All X checks must have one or more issue records; other results have none. Issue text starts with its item number in Excel. Human check next steps remain in Findings. No screenshots column or extra worksheets. No customer strings are executed as formulas.

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
