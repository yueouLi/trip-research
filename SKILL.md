---
name: trip-research
description: 旅行前调研与规划，可复现。从一份行程 md（机票、酒店、预订）出发，问偏好，按固定维度清单调度 agent 联网调研、交叉评审、核实，产出三种成品：Obsidian/Markdown 笔记、双语 A4 PDF 报告、9:16 手机卡片（中英文）。Triggers - trip planning, travel research, travel guide, 旅行攻略, 出发前调研, 做行程, 目的地调研, 旅行 PDF, 手机卡片.
---

# 旅行前调研与规划

把"一个人要去某地旅行"变成一套可重复的流程：**行程 md → 偏好问答 → 按维度调研 → 核实 → 交付三种成品**。

## 先说清楚什么能复现、什么不能

| 环节 | 能否一比一复现 | 原因 |
| --- | --- | --- |
| 流程、维度、问题、任务书 | 能 | 都写在本 skill 的文件里，照做即可 |
| 卡片 HTML | **字节级一致** | 引擎加内容 JSON 加图片是确定的，`scripts/selftest.py` 校验哈希 |
| 导出的 PNG 和 PDF | 版面一致，像素可能略有差异 | 取决于本机字体。中文需要 Noto Sans/Serif CJK，英文版需要联网加载 Fraunces 和 DM Sans，否则退回系统字体 |
| 联网调研的文字内容 | 结构一致，措辞和部分数字会不同 | 网页内容会变，模型输出有随机性 |
| 价格、营业状态 | 以调研当天为准 | 所以每个价格要标性质和日期 |

所以“同样的规划”指：同样的维度、同样的质量标准、同样的版式和产物，不是同样的每一句话。丹吉尔的完整成品放在 `examples/tangier/`，作为对照。

## 先跑自检

```bash
python3 scripts/selftest.py
```

它会用自带的丹吉尔示例重新生成中英文卡片（和预期哈希对比）、溢出检查、导出 PNG、生成 PDF。通过了再开始。
依赖：Python 3.9+、Chromium 或 Chrome（找不到时设 `CHROMIUM=/path`）；PDF 另需 `python3 -m pip install markdown`。

## 流程

### 1. 建行程 md（先把事实钉住）

在旅行文件夹里建 `YYYY-MM 目的地/00-行程信息.md`，用 `references/intake-template.md`。

- 用户发来机票、酒店、预订的截图时，先 OCR 抽字段（日期、时间、航班号、预订号、地址），**把抽到的内容复述给用户确认**，不要让用户重打一遍。工具见 `references/tools-by-agent.md`。
- 未知的值留明确占位符，**不猜**。
- 先钉“机票和住宿时间线”当锚点，后面所有安排都围绕它。

### 2. 问偏好

按 `references/preference-questions.md` 提问。

- 一次问 3–4 个，优先选择题（Claude Code 用 AskUserQuestion）。在聊天软件里则**一次只确认一件事**。
- 用户说话可能乱、会自我更正：先把更正后的版本干净复述一遍，末尾只抛一个确认点。
- 回答写进行程 md 的“偏好”一节。已经答过的不再问。
- **必问交付形式**：笔记、PDF、手机卡片，哪几个，要不要双语（哪两种语言），是否公开发布。

### 3. 定调研范围

读 `references/research-dimensions.md`，按兴趣重点决定哪几个维度写深、哪几个只做摘要。把选定的维度写成行程 md 里的待办清单（`- [ ]`），每个维度一行。

### 4. 逐维度调研

**每个维度单独一份任务书**，用 `references/brief-template.md`，必须带上里面的“资料质量要求”。

- 量大的维度拆成两路并行（前半、后半），完成后合并。
- 起草者和评审者用不同的 agent：一个起草，另一个只做批判（事实错误、编造来源、遗漏、安全风险），再由起草者整合。
- 每个维度只保留一份主稿。双语、PDF、卡片**只对最终稿做**，不要给每个中间版本都出多格式。

### 5. 核实

交付前逐条过：

- 价格是否标了性质（实测、官方列价、按层级推算）和日期？
- 店名和地点是否联网核实？核实不了的写“未核实”，**不放进行程**。
- URL 是否真实可打开？图片是否记了作者和许可证？
- 交通类（往返车程、票价、有没有通票）一律联网查，不凭记忆。

### 6. 交付（三种成品，按用户选的做）

**A. 笔记**：写进用户的笔记库，一份行程计划加每个维度一篇。

**B. 双语 PDF 报告**（A4，封面加每种语言一部分）

```bash
python3 -m pip install markdown      # 一次性
python3 scripts/pdf/make_report_pdf.py \
  --part "第一部分 · 中文版|Teil 1 · Chinesische Fassung=cn.md" \
  --part "第二部分 · Deutsche Fassung|Teil 2 · 德语版=de.md" \
  --title "目的地<br>主题" --sub "副标题" --edition "中德双语版" --meta "调研日期" --out report.pdf
```

- 单语言只给一个 `--part`。语言组合不限。
- 要配照片：md 里写 `![描述](图片URL)`，先 `fetch_images.py download` 再 `replace`（见下）。
- 翻译要分 part 并行译，别一次译 700 行以上，输出会截断。
- 输出里常有开场白，脚本会自动去掉第一个标题之前的内容。
- 验证：`pdftotext report.pdf -` 看文本层，`pdfinfo report.pdf` 看页数。

**C. 9:16 手机卡片**（中文、英文各一份，同一套版式）

1. 把最终稿浓缩成卡片文案，写成内容 JSON（结构见 `references/cards-schema.md`，例子见 `examples/tangier/content/`）。一张卡片一个主题，5–7 行。
2. 取图并查许可证：

   ```bash
   python3 scripts/images/fetch_images.py download --out images/ --mapping map.json cn.md
   python3 scripts/images/fetch_images.py licenses --mapping map.json --out images/manifest.json
   ```

   Wikimedia 会限流（429）：脚本已限速和退避，连续被拒就停下，**不要硬抓**，过一阵再跑会从断点继续。
3. 生成、检查、导出：

   ```bash
   python3 scripts/cards/build_cards.py --content zh.json --images images/ --out cards.html
   python3 scripts/cards/check_cards.py --html cards.html      # 有溢出就改文案或缩照片，再来
   python3 scripts/cards/export_cards.py --html cards.html --out png/
   ```

4. 英文版：另写一份英文内容 JSON，`extra_css` 加 `["theme-latin.css"]`，同样三步。英文比中文长约三分之一，每张卡片要少放一行。
5. **检查必须通过才能交付**。检查器会指出哪张超出、超出多少。

**公开发布前**：个人信息（航班、住宿、花费、同行人）不放进成品；图片署名页必须在；非目的地实拍的照片一律标“示意图”；内容写成“出发前调研整理”，没去过就不要写成亲身体验。

### 7. 旅行中

用 `references/intake-template.md` 里的“记账”一节，分银行卡和现金两块记，汇率写实测值。

## 铁律

- 先查用户偏好和已有笔记，不重复提问、不重复调研。
- 短行程（≤4 天）报任何一日游前先算往返车程。单程超过 2 小时大概率被判“太远”，先提车程再问去不去。
- 推荐景点看**现场实际看头**，不是历史意义。纯历史意义的点只配“路过顺便看一眼”，并明说“别专程去”。
- 与伴侣同行时，spa、汗蒸、按摩类要主动确认男女能否同去、能否订私人双人房。
- 预算以用户常用货币为主，附当地货币参考。
- 廉航：只有手提行李、必须在线值机、数字登机牌——读到票时主动提醒。
- 当地货币、SIM 或 eSIM、插座、瓶装水、老城拖行李的路面，按目的地补进“落地事项”。

## 文件地图

- `references/intake-template.md`：行程 md 模板。
- `references/preference-questions.md`：偏好问题。
- `references/research-dimensions.md`：调研维度。
- `references/brief-template.md`：任务书、评审、整合模板和资料质量要求。
- `references/cards-schema.md`：卡片内容 JSON 结构和版面容量。
- `references/tools-by-agent.md`：Claude Code、Codex、Hermes 实际用到的工具和派活命令。
- `scripts/cards/`：卡片引擎（构建、检查、导出）。
- `scripts/pdf/`：PDF 报告生成。
- `scripts/images/`：图片下载、路径替换、许可证查询。
- `scripts/selftest.py`：自检。
- `examples/tangier/`：完整示例：中英文卡片内容、41 张带署名的图、双语报告原文、预期哈希。图片是 CC 许可，使用时要署名，作者和许可证见 `images/manifest.json`。
