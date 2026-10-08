# Onsite Hreflang Audit

<p align="center"><img src="assets/onsite-audit-cover.png" alt="Onsite Audit 系列封面：网站检查、放大镜和审计报告" width="640"></p>

用于 onsite audit **15. HREFLANG** 的 Codex skill。复用现有 [SF Shared Config](https://github.com/timn-firstpage/On-_site_SF_shared_config)，检查多语言切换、URL 结构及 SF hreflang 结果，输出固定格式 Excel。

Skill 名称：`onsite-audit-hreflang`。入口：[SKILL.md](SKILL.md)。本包由 agent 负责取证和判断，Python 生成器负责校验与排版；不是独立网站爬虫，也不直接解析 SF 二进制数据库。

## 安装与使用

把本仓库根目录复制或链接为 Codex skills 目录下的 `onsite-audit-hreflang`，然后刷新技能列表。SF 新 crawl 准备依赖另行安装的 `sf-shared-config`；已有适用 crawl/exports 可直接复用。仓库 clone 本身不代表 skill 已安装。

在实际执行机器使用 Python 3.9+，安装一次报告依赖：

```text
python -m pip install -r requirements.txt
```

使用示例：

> 使用 $onsite-audit-hreflang，检查 https://example.com，公司名 Example。沿用我的 onsite global config 和已保存的 .seospider，输出 hreflang 初审 Excel。

提供网站、公司名、global config 路径及 crawl/导出位置。日期默认按用户时区当天填写。无 global config 时可复制 [config.template.json](config.template.json) 到独立 run 目录填写。模板中的 MCP 名称是待发现的提示，不代表已建立连接。

## 检查逻辑

| Item | 判定 |
| --- | --- |
| 15.1 Multi-language / country? | 确认单语言、单地区 N/A；确认多版本且首页切换正常 √；确认多版本但无可用切换入口或切换失败 X；尚不能确认 Human check。 |
| 15.2 URL structure | ccTLD、语言/地区子目录、子域名 √；语言/地区参数 URL X，以温和建议说明；15.1 确认单语言时 N/A。切换失败不会让此项自动 N/A。 |
| 15.3 Hreflang issues | 用户明确跳过 → N/A；否则，六项 SF filters 任何一项有问题 URL → X；没有发现问题 URL → √。其中「结果为空」与「未取得结果」必须在 Findings / Coverage 分别说明，详见下表。 |

六个 filters：Missing、Missing Return Links、Missing Self Reference、Non-Canonical Return Links、Incorrect Language & Region Codes、Non-200 Hreflang URLs。SF Missing 有记录直接 raise，不再逐页判断是否需要其他语言版本。单语言本身不自动跳过 15.3；用户可以明确排除。

参数 URL 是此 checklist 的优化项，不等于 hreflang 必然无效，不建议直接要求网站迁移。仅 HTML lang 或单个自引用不能证明多语言。规则和措辞详见 [audit-rules.md](references/audit-rules.md)。

### 15.3 具体怎样打勾或报问题？

按以下顺序判断，命中后即确定结果：

| 顺序 | 实际情况 | Check Result | Findings / Coverage 怎么写 | 进入问题页？ |
| --- | --- | --- | --- | --- |
| 1 | 用户明确说本次不用检查 15.3 | N/A | Findings 写「用户指定本次不检查 hreflang」；Coverage 写「本次未执行」。 | 否 |
| 2 | 六项中任意一项出现至少一个实际问题 URL，包括 Missing；即使其他项为空或未取得 | X | Findings 写问题类型和实际数量；Coverage 列出已读取及缺失的 filters、来源与范围。 | 是，列出所有已取得的问题记录 |
| 3 | 六项结果都已取得，均没有问题 URL：0 条、空表、空白、null、none 或 NaN | √ | Findings 写「已读取的六项 SF 结果均未发现问题 URL」；Coverage 写实际来源、crawl 日期和覆盖范围。 | 否 |
| 4 | 只取得部分结果，已取得的部分没有问题 URL | √ | Findings 写「已取得的结果暂未发现问题；尚缺少〔具体 filters〕，建议补充后确认」；Coverage 写「部分结果未取得，未完成完整验证」。 | 否 |
| 5 | 六项结果全部未取得，例如没有导出、无法打开或读取失败 | √ | Findings 写「按本次初审约定暂记 √；尚未取得 SF hreflang 结果，建议补充后确认」；Coverage 写「未取得结果，未验证」。 | 否 |

**「Missing filter 有 URL」与「缺少 SF 导出结果」是两回事。** 前者代表 SF 已列出问题，记 X；后者按你的 first-check 约定记 √，同时必须提醒。空白/NaN 只表示没有有效问题记录，不能覆盖同一份结果里其他真实 URL。

例如：Missing 有 3 个 URL，其他五项没有拿到 → **X**，这 3 个 URL 进入问题页，Coverage 同时说明其他五项未取得。只有 Missing 已取得且为 0 条，其他五项没有拿到 → **√**，但必须说明这是部分结果的初审。

**缺少结果时的 √ 仅表示按约定暂未报出问题。** 不得写成「已验证全部正常」或「全站 hreflang 无问题」。即使六项为空，也只描述所提供 crawl 的实际范围；不额外要求 Crawl Analysis 完成证明才接受空结果。

## Global config 与 saved crawl

共用 `site/source/mcp/budget/cache/output`，只执行 `checks.hreflang`。配置由 agent 解释，读取 JSON 不会启动 SF。相对路径按 config 所在目录解析；累计预算和 handover 与其他 onsite audits 共用。详见 [shared-config.md](references/shared-config.md)。

已有 `.seospider` 使用 `source.mode=saved_crawl` 和 `source.crawl_file`；优先复用匹配的完整 exports，否则通过 SF 支持的功能打开一次。没有 reader 时请用户打开保存文件并导出指定结果，不重新 Load config 或 Start。保护当前未保存的 SF session。

确需新 crawl 且允许时交给 shared skill：共用 profile、确认网站/sitemap、用户手动开始并保存。`allow_new_crawl=false` 不阻止读取已有结果；`live_checks=false` 禁止新的网页访问，依靠已有证据。浏览器操作和跨域覆盖以实际可用能力为准。

## Excel 输出

文件名：`Onsite_hreflang_{company name}_{YYYY-MM-DD}.xlsx`。

| Worksheet | 创建条件 | 列 |
| --- | --- | --- |
| Checklist | 始终，含 15.1–15.3 | Item No. / Item Name / Check Result / Findings / Coverage |
| 15. HREFLANG | 至少一个 X | Address / Issue / Instruction |

所有 X 都有问题详情；一条 source/issue/target 一行，target 放 Issue。Human check 和 N/A 不进入问题页。无 X 时只输出 Checklist。保留冻结表头、自动筛选、换行及结果颜色，客户文本以 literal text 保存。

Agent 先按 [output-contract.md](references/output-contract.md) 写 findings.json，运行：

```text
python scripts/build_report.py --input path/to/findings.json --output-dir path/to/unique-run
```

生成器检查三项齐全、状态和问题对应关系、缺失证据提醒、写后内容一致性，并拒绝覆盖。错误时保留 findings/原始证据，修正后只重跑报告生成。长行超出可显示高度会报错，需拆分问题行或精简结论，完整原始证据留在 archive。

## 如何测试

先运行模拟案例（无网络、非真实审计）：

```text
python -m unittest discover -s tests -v
python scripts/build_report.py --input examples/findings.json --output-dir runs/demo-001
```

示例包含正常切换、参数 URL 优化项和未取得 SF 结果，预期两张表，问题页只有 15.2。再次运行需换 run 目录。测试覆盖无 X 只有一页、所有 X 进入详情、缺失结果提醒、N/A、非法输入、公式样式文本按文字保存及防覆盖。

真实验收：提供一个正常网站和一个已知异常网站的保存 crawl/exports，人工对照六个 filters 的实际问题数量与代表 URL，再核对首页切换、报告全部问题行和两页排版。模拟测试不证明真实 SF/MCP 接入或 SEO 结论正确。

## 文件与团队运行

- `SKILL.md`：执行入口；`references/`：判定、输出与 shared config 合约。
- `scripts/build_report.py`：固定报告生成器；`examples/findings.json`：明确标注的模拟数据。
- `runs/`：忽略的本地报告、完整导出、manifest 和 findings；不提交客户数据或凭据。

同事在各自执行机器安装 skill 和 Python 依赖，并提供该机器可访问的 SF 文件和可写输出目录。GitHub 导入不会自动提供 SF 权限、运行环境或客户数据。执行 audit 不会自动修改网站或发布仓库内容。
