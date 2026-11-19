# 卡片内容 JSON 结构

`scripts/cards/build_cards.py` 读一份内容 JSON 加一个图片目录，输出单文件 HTML。引擎不含任何主题文字，换内容就是换主题，换语言就是换一份 JSON。
完整例子：`examples/tangier/content/zh.json` 和 `en.json`。

## 顶层

```json
{ "theme": { ... }, "cards": [ { ...封面 }, { ...普通卡片 }, ... ] }
```

最后一张“图片来源”页由引擎自动生成，不用写。

## theme

| 字段 | 含义 |
| --- | --- |
| `lang` | html 的 lang，例如 `zh-CN`、`en` |
| `title` | 浏览器标签页标题 |
| `fonts_href` | 网页字体的链接（Google Fonts），可为空。离线时退回系统字体 |
| `extra_css` | 额外的 CSS 文件，放在 `scripts/cards/` 下。拉丁字母语言用 `["theme-latin.css"]`，中文不用 |
| `nobreak` | 不许被换行拆开的词，例如 `["丹吉尔"]` |
| `footer_label` | 每张卡片页脚左边的文字 |
| `credit_prefix` | 页脚照片署名前缀，例如 `图 ` 或 `Photo: ` |
| `credits_title`、`credits_lede`、`credits_note` | 署名页的标题、说明、备注 |

## 封面

```json
{ "type": "cover", "where": "地点一句话", "title": "大标题", "sub": ["副标题第一行", "第二行"], "meta": "小字说明", "image": 5 }
```

`image` 是图片编号，对应 `manifest.json` 里的 `img_005`。封面用竖版图，因为要裁成拱门。

## 普通卡片

```json
{
  "theme": "ink",            // ink 深蓝 / wall 白墙 / door 门蓝 / mint 薄荷
  "stamp": "买",             // 右上角圆章里的一个字，表示分类；可为空
  "title": "卡片标题",
  "lede": "标题下的一句说明",  // 可选
  "blocks": [ ... ],
  "bottom": [ ...拱门照片 ],  // 可选，贴在卡片底部
  "credit_imgs": [0, 1]      // 这张卡片用到的图，用来生成页脚署名和署名页
}
```

## blocks 的类型

| type | 字段 | 说明 |
| --- | --- | --- |
| `rows` | `items`: `[{name, desc, tag}]` | 一行一项。`tag` 是右侧的价格标签，可为空 |
| `steps` | `items`: `[{name, desc}]` | 带序号的步骤。只有内容真的是先后顺序时才用 |
| `photos` | `variant`: `two` 或 `three`；`items`: 拱门照片；`side`: 可选侧边文字，`**加粗**` | 一排照片 |
| `stats` | `items`: `[{value, label}]` | 2×2 的数字块 |
| `lede` | `text` | 正文里的说明段 |
| `note` | `text` | 卡片底部的小字备注 |

## 拱门照片

```json
{ "img": 0, "w": 40, "h": 54, "pos": "40% 50%", "cap": "示意图 · 马拉喀什", "mt": 8 }
```

`w`、`h` 是占卡片宽度的百分比（cqw）。`pos` 是裁切的焦点，`mt` 是向下错开的距离。非目的地实拍的照片一定要写 `cap` 标“示意图”。

## manifest.json（图片目录里）

```json
{ "img_000": { "file": "img_000.jpg", "title": "原文件名", "artist": "作者", "license": "CC BY-SA 4.0", "source_url": "..." } }
```

用 `scripts/images/fetch_images.py licenses` 生成。许可证为空的图不能发布。

## 版面容量（经验值，1080×1920）

- 一张卡片放 5–7 行 `rows`（每行说明不超过两行）。
- 有一排照片时，减到 4–5 行，照片高度 26–36。
- 英文比中文长约三分之一，英文卡片要少放一行或把照片再缩 4。
- 用 `check_cards.py` 检查，它会指出哪张超出、超出多少。
