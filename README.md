# Onsite Hreflang Audit

<p align="center"><img src="assets/onsite-audit-cover.png" alt="Onsite Audit 系列封面：网站检查、放大镜和审计报告" width="640"></p>

用于 onsite audit **15. HREFLANG** 的 Codex skill。复用 [SF Shared Config](https://github.com/timn-firstpage/On-_site_SF_shared_config)，检查语言切换、版本 URL 结构和 SF hreflang 结果，生成 Excel。

Skill 名称：`onsite-audit-hreflang`。入口：[SKILL.md](SKILL.md)。Agent 负责取证和判断，Python 负责校验与报告输出。

## 安装与使用

将仓库复制或链接为 Codex skills 目录下的 `onsite-audit-hreflang`，刷新技能列表。已有 SF crawl／exports 可直接复用；新 crawl 准备由另行安装的 `sf-shared-config` 负责。Clone 仓库不等于安装 skill。

实际执行机器需要 Python 3.9+，安装报告依赖：

```text
python -m pip install -r requirements.txt
```

示例：

> 使用 $onsite-audit-hreflang，检查 https://example.com，公司名 Example。沿用我的 onsite global config 和已保存的 .seospider，输出 hreflang 初审 Excel。

提供网站、公司名、global config 和 crawl／导出路径。日期按用户时区填写。无 global config 时可复制 [config.template.json](config.template.json) 到独立 run 目录使用。模板不会自动连接 MCP 或启动 crawl。

## 检查逻辑

### 15.1 Multi-language / country?

检查是否有**多语言或多地区版本**，并检查首页能否切换。

- `en` 和 `zh` 是英文、中文的多语言线索，不代表多个国家。
- 真实英文和中文版本符合“多语言”，不要求同时具备多个国家版本。
- `en-HK` 和 `en-SG` 可以表示同一语言面向不同地区。
- hreflang 标签声明了版本，但不能单凭标签确认目标内容或首页切换正常。结合实际内容或已有 SF 证据判断。

| Check Result | 何时使用 |
| --- | --- |
| √ | 确认有多个语言／地区版本，且首页切换正常。 |
| X | 确认有多个版本，但首页无可用入口或切换失败。 |
| N/A | 确认只有单语言、单地区版本。 |
| Human check | 版本内容或切换行为尚未确认。 |

Findings 示例：「已发现英文和中文 hreflang；切换尚未验证。」Instruction 示例：「请确认首页语言切换正常。」不能把“找到标签”写成“已验证多国家及切换正常”。

### 15.2 URL structure

使用真实版本 URL 判断结构，**不要求先点击成功，也不要求首页 URL 改变**。

| Check Result | 何时使用 |
| --- | --- |
| √ | ccTLD、语言／地区子目录或子域名，例如 example.de、example.com/en/、en.example.com。默认语言根目录也可以。 |
| X | 用 ?lang=en 等参数区分版本；混合结构中发现这种形式也列为优化项。普通 tracking 参数不计入。 |
| N/A | 15.1 已确认单语言、单地区。切换失败不会让此项自动 N/A。 |
| Human check | 版本 URL 尚未确认，或只用同一 URL 的 cookie／JS 切换。 |

参数 URL 按本 checklist 温和提醒：Findings 写「语言版本使用 ?lang=en 参数」；Instruction 写「可在改版时考虑语言子目录，并评估迁移影响」。

### 15.3 Hreflang issues

读取六项 SF filters：**Missing、Missing Return Links、Missing Self Reference、Non-Canonical Return Links、Incorrect Language & Region Codes、Non-200 Hreflang URLs**。

按以下顺序判断：

| 情况 | Check Result | Findings 示例 | Instruction 示例 | 进入问题页 |
| --- | --- | --- | --- | --- |
| 用户明确跳过 15.3 | N/A | 用户指定本次不检查。 | 无需处理。 | X |
| 任一 filter 有问题 URL，包括 Missing | X | 发现 3 个缺少 hreflang 的页面。 | 请按问题页修正。 | √ |
| 六项已取得，均没有问题 URL | √ | 六项 SF 结果未发现问题。 | 无需处理。 | X |
| 只取得部分结果，已取得的部分没有问题 | √ | 已取得结果未发现问题；其余五项未验证。 | 请补充其余五项 SF 导出。 | X |
| 六项结果均未取得／读取失败 | √ | 尚未取得 SF 结果，按初审约定暂记 √，未完成验证。 | 请补充六项 SF 导出。 | X |

**Missing 中有 URL 是问题，记 X；缺少导出是未取得结果，按初审约定记 √ 并提醒。** 空结果包括 0 条、空表、空白、null、none 或 NaN；不能覆盖其他实际问题 URL。

例如：Missing 有 3 个 URL，其他五项没有拿到 → X，并列出这 3 个问题。Missing 为 0 条，其他五项没有拿到 → √，Findings 说明未验证，Instruction 请求补充导出。

不额外要求 Crawl Analysis 完成证明才接受空结果。15.1 单语言 N/A 不自动跳过 15.3。未取得结果时的 √ 不能写成“全站已验证正常”。详细边界见 [审计规则](references/audit-rules.md)。

## 代码取证与 HTTP 429

15.1／15.2 使用代码，不需要 computer use。各模型运行同一套 Python 脚本并读取 JSON；没有代码执行能力时，需要外部执行器。

```text
# 离线解析已有首页 HTML，不访问网络
python scripts/inspect_homepage.py --config path/to/global-config.json --html path/to/homepage.html --output-dir runs/home-offline-001

# 从共享剩余预算分配 12 次请求，最多检查 6 个候选地址
python scripts/inspect_homepage.py --config path/to/global-config.json --remaining-requests 12 --max-targets 6 --output-dir runs/home-http-001
```

输出 `homepage-evidence.json` 和 HTML 存档，包括入口、候选 URL、响应、内容及未验证部分。每次使用新目录，实际请求数计入共享预算。HTTP／离线解析使用 Python 标准库；纯 JS 控件可选安装 `requirements-browser.txt` 和 Chromium，使用 `--render`、已识别的 `--selector` 及 `--option-value`。

默认请求间隔至少 2 秒，可用 `budget.min_request_interval_seconds` 调整。遇到 429 停止本轮后续请求，不自动重试或转用 Playwright。记录 `Retry-After`，后续运行先遵守等待时间；无有效等待头时建议至少等 60 秒再评估，不保证届时恢复。优先复用保存的证据。

429 报告写：「首页请求被限流，未检查语言切换。」下一步写：「请提供已保存的首页 HTML 或 SF 结果。」访问或运行环境限制不能直接判定网站切换坏了。详情见 [代码取证说明](references/homepage-inspection.md)。

## Global config 与 saved crawl

共用 `site/source/mcp/budget/cache/output`，只执行 `checks.hreflang`。配置中的相对路径按 config 目录解析；显式 CLI 路径按当前目录解析。复用累计预算及 handover，不复制 SF profiles。

已有 `.seospider` 使用 `source.mode=saved_crawl`、`source.crawl_file`。优先读取匹配 exports，必要时通过 SF 支持的功能打开一次；无 reader 时请用户打开已有文件并导出指定结果，保护当前未保存的 session。

确需新 crawl 且允许时交给 shared skill：用户确认网站／sitemap、手动开始并保存。`allow_new_crawl=false` 不阻止读取已有结果；`live_checks=false` 禁止新的网页访问。详见 [共享配置合约](references/shared-config.md)。

## Excel 输出

文件名：`{name}_onsite_hreflang_audit_{date}.xlsx`，date 为 YYYY-MM-DD。例如 `Example_onsite_hreflang_audit_2026-10-12.xlsx`。

| Worksheet | 创建条件 | 列 |
| --- | --- | --- |
| Checklist | 始终，含 15.1–15.3 | Item No. / Item Name / Check Result / Findings / Instruction |
| 15. HREFLANG | 至少一个 X | Address / Issue / Instruction |

**没有 Coverage 列。Findings 写发现，Instruction 写人需要做的下一步。** √／X 表示通过／问题，不使用 Yes／No；保留 N/A 和 Human check。所有 X 都进入问题页，一条 source／issue／target 一行。无 X 时只有 Checklist。

措辞要清晰、简短，特别是 Instruction：通常一条短句，一个具体动作。正常且无需处理时写「无需处理」。完整来源、范围和日期放证据存档；影响结论的缺失资料在 Findings 简短说明。

| Findings | Instruction |
| --- | --- |
| 中文和英文版本可正常切换。 | 无需处理。 |
| 英文页面缺少指回中文页面的 hreflang 链接。 | 请添加指向对应中文页面的 hreflang 链接。 |
| 尚未取得六项 SF 结果，未完成验证。 | 请补充六项 SF 导出。 |
| 语言版本使用 ?lang=en 参数。 | 可在改版时考虑语言子目录，并评估迁移影响。 |

Agent 按 [输出合约](references/output-contract.md) 写 findings.json，每项都包含 `finding` 和 `instruction`；无需 `coverage`。旧 JSON 需补充 instruction，并将下一步从 finding 中分离。

```text
python scripts/build_report.py --input path/to/findings.json --output-dir path/to/unique-run
```

生成器校验三项齐全、状态、下一步及 X 问题详情；文字按 literal text 保存，写后重新校验并拒绝覆盖。错误时保留证据，修正后只重跑输出。长行超出可显示高度时需精简结论或拆分问题行，完整原始数据留在 archive。

## 测试与团队运行

```text
python -m unittest discover -s tests -v
python scripts/build_report.py --input examples/findings.json --output-dir runs/demo-001
```

模拟案例包含正常切换、参数 URL 和缺少 SF 结果，预期两张表，问题页只有 15.2。测试覆盖表头与下一步、缺失结果提醒、X 筛选、文字安全、防覆盖、HTML 解析、预算与 429；可选浏览器测试需要 Playwright／Chromium。

真实验收仍需网站与 SF 数据，对照六项 filters、代表 URL 和切换行为，检查 Excel 排版。模拟数据不证明真实网站检查通过。

- `SKILL.md`、`references/`：流程、规则及输出合约。
- `scripts/build_report.py`：报告生成器。
- `scripts/inspect_homepage.py`、`scripts/render_homepage.py`：基础与可选 JS 取证。
- `examples/findings.json`：模拟数据。
- `runs/`：忽略的报告、完整导出和 manifest；不提交客户数据或凭据。

同事在实际执行机器准备 skill、Python 依赖、可读的 SF 文件及可写目录。GitHub 导入不会自动提供 SF 权限、网络或运行环境；执行 audit 不自动修改网站或发布仓库内容。
