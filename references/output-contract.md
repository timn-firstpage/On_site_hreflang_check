# Report and findings contract

Filename: `{name}_onsite_hreflang_audit_{date}.xlsx`. Map name to findings.site_name and date to findings.audit_date (YYYY-MM-DD). Sanitize invalid filename characters and reject excessively long names. Use a unique writable run directory; never overwrite prior reports.

## Worksheets

- Always create `Checklist`: `Item No. | Item Name | Check Result | Findings | Instruction`.
- Create `15. HREFLANG` only when at least one check is X: `Address | Issue | Instruction`.
- There is **no Coverage column**. Archive source details, counts, scope and timestamps in evidence/manifest instead. Keep material limitations in Findings, so an incomplete √ cannot be mistaken for verified success.
- Include 15.1–15.3 exactly once, in order. Results are √ / X / N/A / Human check; never Yes/No or Y/N. N/A and Human check retain their previously agreed meanings.
- Every X requires one or more detail issues; other results have none. Prefix detail Issue with the item number. Store customer strings as literal text, never formulas. No screenshots column or extra worksheets.

## Findings versus Instruction

**Findings = what was found. Instruction = the next thing a person needs to do.** Use the configured report language, short sentences and familiar words. Do not put next steps in Findings or repeat the whole finding in Instruction.

- Findings: one short conclusion; include a brief missing-data reminder when needed. Issue: one specific defect, plus the target URL if known.
- Instruction: usually one short, concrete action. Begin with a verb: “请补充…”, “请添加…”, “请修正…”. A pass with nothing to do uses “无需处理。” / “No action needed.” N/A also uses this when no follow-up is needed.
- Human check and any unverified 15.3 √ must give a real next step. X uses a summary action in Checklist and the specific fix on each detail row.
- Keep essential URL/count/limitations; avoid jargon, background paragraphs, broad “optimize hreflang” advice and long chains of actions. Do not invent causes or claim a homepage 429 proves switching is broken.
- Parameter URL advice stays gentle and brief: “可在改版时考虑语言子目录，并评估迁移影响。”

| Case | Findings | Instruction |
| --- | --- | --- |
| Confirmed working versions | 中文和英文版本可正常切换。 | 无需处理。 |
| Missing return link | 英文页面缺少指回中文页面的 hreflang 链接。 | 请添加指向对应中文页面的 hreflang 链接。 |
| Missing SF results | 尚未取得六项 SF 结果，按初审约定暂记 √，未完成验证。 | 请补充六项 SF 导出。 |
| Homepage HTTP 429 | 首页请求被限流，未检查语言切换。 | 请提供已保存的首页 HTML 或 SF 结果。 |
| Parameter URLs | 语言版本使用 ?lang=en 参数。 | 可在改版时考虑语言子目录，并评估迁移影响。 |

## Findings input

The agent reviews evidence and writes JSON. The generator validates and formats it; it does not crawl or independently judge SEO.

```json
{
  "site_name": "Example",
  "site_url": "https://example.com/",
  "audit_date": "2026-10-12",
  "checks": [
    {
      "id": "15.1",
      "item_name": "Multi-language / country?",
      "result": "√",
      "finding": "中文和英文版本可正常切换。",
      "instruction": "无需处理。",
      "evidence_state": "available",
      "evidence": ["raw/homepage-observation.json"],
      "issues": []
    }
  ]
}
```

The fragment shows one row; real input requires all three. Every finding/instruction must be nonempty. evidence_state is `available`, `partial`, `unavailable` or `not_applicable`. evidence is a list of actual archived references, which may be empty for unavailable or skipped checks.

X issue object: `{"address":"https://example.com/","issue":"语言版本使用 ?lang=en 参数。","instruction":"可在改版时考虑语言子目录，并评估迁移影响。"}`. Use real source addresses; retain known target URLs/codes in Issue.

For 15.3 √ with partial/unavailable evidence, require nonempty `missing_evidence_note` describing what is missing and that verification is incomplete. The generator appends this fact to Findings; put the user's action in `instruction`. Do not add a second mixed-language notice. Other passes require available evidence. N/A requires not_applicable; skipping 15.3 is an explicit user instruction, not automatically inherited from 15.1.

**Migration:** older findings.json must add `instruction` to every check and separate any existing next steps from `finding`. `coverage` is no longer required or exported; legacy extra fields are ignored. Do not move old coverage paragraphs into Instruction. Keep full provenance in the run archive.

Archive findings.json, manifest.json, complete raw exports and final workbook under ignored runs/. The validator checks types, IDs, statuses, issue inclusion and missing-evidence disclosure, not evidence truth or wording quality. The generator reopens the workbook to check text, sheet names and row counts. Inspect layout, preserve complete raw evidence and avoid silently truncating long text.
