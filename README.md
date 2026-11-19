# trip-research

旅行前调研与规划的 Claude Code skill，流程可复现。从一份行程 md 出发，问偏好，按固定维度联网调研、交叉评审、核实，产出三种成品：

- Markdown 笔记
- 双语 A4 PDF 报告
- 9:16 手机卡片（中文、英文各一份）

附带完整的丹吉尔示例（`examples/tangier/`），可以对照着复现。

## 安装

```bash
git clone https://github.com/yueouLi/trip-research ~/.claude/skills/trip-research
cd ~/.claude/skills/trip-research
python3 scripts/selftest.py
```

自检通过说明这套引擎在你的机器上能复现示例。

依赖：Python 3.9+，Chromium 或 Chrome（找不到时设置 `CHROMIUM=/path/to/chromium`）。生成 PDF 另需 `python3 -m pip install markdown`。

## 怎么用

在 Claude Code 里说“帮我做 XX 的旅行攻略”，skill 会按 `SKILL.md` 里的流程走。入口文档是 [`SKILL.md`](SKILL.md)。

## 能复现什么

| 环节 | 能否复现 |
| --- | --- |
| 流程、维度、问题、任务书 | 能 |
| 卡片 HTML | 字节级一致（自检校验哈希） |
| 导出的 PNG 和 PDF | 版面一致，像素可能因本机字体略有差异 |
| 联网调研的文字 | 结构一致，措辞和部分数字会不同 |

## 目录

```
SKILL.md          流程说明（入口）
references/       清单、模板、偏好问题、任务书、卡片结构
scripts/cards/    卡片引擎：构建、溢出检查、导出
scripts/pdf/      PDF 报告生成
scripts/images/   图片下载、许可证查询
scripts/selftest.py
examples/tangier/ 完整示例
```

## 许可

代码和文档使用 MIT 许可，见 [LICENSE](LICENSE)。

`examples/tangier/images/` 里的照片来自 Wikimedia Commons，各自按原作者的 Creative Commons 许可使用，作者和许可证见 `examples/tangier/images/manifest.json`。使用或再发布这些照片时需要署名，CC BY-SA 的还需要以相同方式共享。
