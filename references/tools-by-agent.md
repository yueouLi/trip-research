# 各 agent 在丹吉尔调研里实际用到的工具

这一份记录的是作者环境里观察到的做法，用来告诉你各个 agent 擅长什么、怎么派活；换成别的 agent 框架时，按“能力”对应到你那边的工具。

数据来源：Hermes 的 `~/.hermes/state.db`（旅行期间的 WhatsApp 会话，2026-09-15 至 09-22）、Codex 的 `~/.codex/sessions/2026/09/19/` 草药调研和评审会话、Hermes 的 skills 文档，以及 Claude Code 本次做卡片时的实际操作。次数是当时的调用次数，用来看哪些工具是主力，不是配额。

## 一眼看：谁适合做什么

| 任务 | 首选 | 用到的工具 |
| --- | --- | --- |
| 读机票、酒店截图 | Hermes | `image-ocr` skill（tesseract）；模型看不了图时用 `claude -p @图片路径` |
| 联网调研写初稿 | Claude（由 Hermes 或用户派） | `WebSearch`、`WebFetch` |
| 交叉评审、挑错 | Codex | `web__run`（带 `site:` 限定）、`exec_command` |
| 查路线、距离、坐标 | Hermes | `maps` skill（OpenStreetMap：Nominatim、Overpass、OSRM） |
| 长期陪伴、问路问价 | Hermes | `terminal`、`web_search`、`clarify`、`cronjob_manage` |
| 翻译、做 PDF | Hermes 派 Claude + chromium | `claude -p ... --allowedTools Read`、`chromium --print-to-pdf` |
| 做手机卡片、截图验收 | Claude Code | `Bash`（chromium headless、ImageMagick）、`Read` 看截图 |

## Hermes（项目经理和长期助手）

旅行期间那个 WhatsApp 会话的工具调用，从多到少：

| 工具 | 次数 | 用途 |
| --- | --- | --- |
| `terminal` | 962 | 跑一切命令：派 Claude 和 Codex、OCR、转 PDF、读写文件 |
| `web_search` | 253 | 查交通、票价、有没有通票、spa 价格、营业时间 |
| `write_file` | 226 | 写行程、调研稿、任务书 |
| `read_file` | 123 | 读任务书和已有稿 |
| `process_manage` | 117 | 管后台任务（派出去的 Claude 和 Codex 调研） |
| `skill_view` | 90 | 读 skill 文档 |
| `patch` | 47 | 改稿 |
| `web_extract` | 44 | 抓取网页正文 |
| `skill_manage` | 39 | 把踩过的坑写进 skill |
| `tool_describe`、`tool_search` | 24、19 | 查有哪些工具 |
| `cronjob_manage` | 22 | 定时任务，例如每日早报、夜班调度 |
| `search_files` | 13 | 搜本地文件 |
| `browser_exec` | 11 | 浏览器抓取 |
| `clarify` | 7 | 向用户确认，一次只问一件事 |
| `execute_code` | 3 | 跑代码片段 |

这个 WhatsApp 会话从 9 月 9 日开始，整段会话里还出现过下面几个，旅行那一周没用到：

| 工具 | 次数 | 用途 |
| --- | --- | --- |
| `session_search` | 114 | 搜过往会话，找之前说过的偏好和决定 |
| `vision_analyze` | 25 | 读图（模型自己看不了图时的备用） |
| `memory` | 16 | 记住用户偏好 |
| `computer_use` | 1 | 操作桌面，基本不用 |

这趟旅行里它读过的 skill：`claude-code`（15）、`bilingual-report-pdf`（13）、`hermes-agent`（12）、`multi-agent-work-orchestration`（9）、`codex`（9）、`image-ocr`（8）、`travel-planning`（7）、`maps`（7）、`pdf`（6）。

**Hermes 派活的命令：**

```bash
# 联网调研，量大拆两路并行
claude -p '<任务书内容>' --allowedTools 'WebSearch,WebFetch' --max-turns 60 --max-budget-usd 3 --output-format text > out.md

# 翻译，按 part 分开译，别一次译 700 行以上，输出会截断
claude -p '读取 <中文.md> 翻译成德语，保持 markdown 结构，专有名词、数字、URL、[n] 保留' --allowedTools Read --max-turns 8 > out-de.md

# Codex 作业
codex exec --sandbox workspace-write '<任务>'      # 放后台，用 pty
# 做 PDF：markdown 转 HTML，再
chromium --headless --disable-gpu --no-sandbox --no-pdf-header-footer --print-to-pdf=out.pdf in.html
pdftotext out.pdf -    # 验证文本层
```

派活前先看各个 agent 还有没有额度，谁有额度用谁，不要因为某个耗尽就停下。

## Codex（评审和第二作者）

草药调研和评审两个会话（共 42 次工具调用），它的工具只有三类：每次调用还会被包在一个 JS 的 `tools.*` 调用里：

| 工具 | 用法 |
| --- | --- |
| `exec_command`（shell，18 次） | `cat` 读任务书和已有稿；`python` 解析 markdown；用 `requests` 调 Wikimedia Commons API 拿图片 URL；`curl` 循环检查 URL 能否打开；用正则把报告里所有 URL 抽出来逐个验证 |
| `apply_patch`（4 次） | 把稿子写入和修改文件 |
| `web__run`（`search_query`，20 次） | 一次传多条查询，**用 `site:` 限定权威来源**，例如 `site:gov.ma`、`site:visitmorocco.com`、`site:poison.org`、`site:nccih.nih.gov`、`site:commons.wikimedia.org/wiki/File:...`；也直接搜店名和地址核实真实存在 |

它做的事：起草草药手册、批判 Claude 的草药稿（事实错误、编造来源、安全风险）。评审时盯最危险的点：精油稀释比例、黑皂、ghassoul、熏香用法。

## Claude Code

| 工具 | 用法 |
| --- | --- |
| `WebSearch`、`WebFetch` | 联网调研的主力。事实、价格、店铺、票价全部走这两个，`WebSearch` 的 `mode` 默认 standard，查不到或很冷门再用 extended |
| `Bash` | `curl` 调 Wikimedia Commons API 取作者和许可证；`chromium --headless --screenshot` 逐张截图验收卡片；`magick montage` 拼联系表；`sqlite3` 读 Hermes 的 `state.db` |
| `Read` | 读截图检查版式，读 agent 产出的稿 |
| `Write`、`Edit` | 写行程 md、调研稿、卡片生成脚本 |
| `AskUserQuestion` | 问偏好，一次 3–4 个选择题 |
| `Agent` | 并行跑独立的调研维度 |
| Skill | `frontend-design`（做卡片前加载）、`markitdown`（读 PDF 和 Office） |

## 这些经验写给所有 agent

- **Wikimedia 会限流（HTTP 429）**：连续批量下载图片会被拒。分批、慢速、带 User-Agent；出现 429 就停下，改用已有的图，不要硬抓。
- **模型看不了图的 agent（如 Hermes 的本地模型）**：图片先 OCR，或交给 Claude 读。
- 机器上**没有** pandoc、weasyprint、wkhtmltopdf、xelatex，用 chromium 转 PDF。先 `command -v chromium` 确认路径（这台是 `/usr/bin/chromium`，Hermes 文档里写的是 `/usr/sbin/chromium`）。
- `claude -p` 的输出常带开场白（“调研已完成……”）和 `---` 分隔线，转 PDF 前要删掉第一个 `# ` 标题之前的所有内容。
- 派活给 Claude 时限制预算和轮数：`--max-turns 60 --max-budget-usd 3`，防止失控。
- 同一内容别反复出版本。每个维度只保留一份主稿，双语和多格式只对最终稿做。
- Hermes 里已有一个 `travel-planning` skill，是为特定用户的沟通方式写的（分步确认、欧元报价）。这个 skill 是通用版，不含个人信息，两者可以并存。
