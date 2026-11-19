#!/usr/bin/env python3
"""内容 JSON -> 单文件 HTML 卡片集（9:16，所有尺寸用 cqw，导出和手机上看一致）。

用法：
  python3 build_cards.py --content zh.json --images ../../examples/tangier/images --out cards.html

content.json 结构见 references/cards-schema.md。
引擎本身不含任何主题内容，只含版式；同一份引擎配不同的 content.json 就是不同的主题或语言。
"""
import argparse, base64, html, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent


def e(s):
    return html.escape(html.unescape(str(s)), quote=False)


def rich(s):
    """文本里允许 **加粗**。"""
    parts = e(s).split("**")
    return "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))


class Deck:
    def __init__(self, content, images_dir):
        self.t = content["theme"]
        self.cards = content["cards"]
        self.dir = pathlib.Path(images_dir)
        self.man = json.loads((self.dir / "manifest.json").read_text(encoding="utf-8"))
        self.used = []
        self.n = len(self.cards) + 1  # +1: 自动生成的署名页

    def uri(self, img):
        iid = img if isinstance(img, str) else f"img_{int(img):03d}"
        data = (self.dir / self.man[iid]["file"]).read_bytes()
        return "data:image/jpeg;base64," + base64.b64encode(data).decode()

    def iid(self, img):
        return img if isinstance(img, str) else f"img_{int(img):03d}"

    def protect(self, text):
        out = e(text)
        for w in self.t.get("nobreak", []):
            out = out.replace(w, "⁠".join(w))
        return out

    def arch(self, a):
        cap = f'<span class="cap">{e(a["cap"])}</span>' if a.get("cap") else ""
        return (f'<figure class="arch" style="width:{a["w"]}cqw;height:{a["h"]}cqw;margin-top:{a.get("mt", 0)}cqw">'
                f'<img src="{self.uri(a["img"])}" style="object-position:{a.get("pos", "50% 50%")}" alt="">{cap}</figure>')

    def block(self, b):
        k = b["type"]
        if k == "lede":
            return f'<p class="lede">{e(b["text"])}</p>'
        if k == "note":
            return f'<p class="note">{e(b["text"])}</p>'
        if k == "rows":
            out = []
            for it in b["items"]:
                tag = f'<span class="tag">{e(it["tag"])}</span>' if it.get("tag") else ""
                d = f'<span class="d">{e(it["desc"])}</span>' if it.get("desc") else ""
                out.append(f'<div class="row"><div><b>{e(it["name"])}</b>{d}</div>{tag}</div>')
            return '<div class="rows">' + "".join(out) + "</div>"
        if k == "steps":
            return '<ol class="steps">' + "".join(
                f'<li><span class="n">{i}</span><div><b>{e(it["name"])}</b><span class="d">{e(it["desc"])}</span></div></li>'
                for i, it in enumerate(b["items"], 1)) + "</ol>"
        if k == "photos":
            side = f'<p class="side">{rich(b["side"])}</p>' if b.get("side") else ""
            cls = "photos three" if b.get("variant") == "three" else "photos"
            return f'<div class="{cls}">' + "".join(self.arch(a) for a in b["items"]) + side + "</div>"
        if k == "stats":
            return '<div class="stats">' + "".join(
                f'<div><b>{e(i["value"])}</b><span>{e(i["label"])}</span></div>' for i in b["items"]) + "</div>"
        raise SystemExit(f"未知 block 类型：{k}")

    def credit_names(self, imgs):
        names = []
        for i in imgs:
            a = e(self.man[self.iid(i)]["artist"]).split(" from ")[0]
            if a not in names:
                names.append(a)
        return names

    def card(self, no, c):
        if c.get("type") == "cover":
            return self.cover(no, c)
        for i in c.get("credit_imgs", []):
            self.used.append(self.iid(i))
        stamp = f'<span class="stamp">{e(c["stamp"])}</span>' if c.get("stamp") else ""
        lede = f'<p class="lede">{e(c["lede"])}</p>' if c.get("lede") else ""
        body = "".join(self.block(b) for b in c.get("blocks", []))
        btm = ('<div class="btm">' + "".join(self.arch(a) for a in c["bottom"]) + "</div>") if c.get("bottom") else ""
        names = self.credit_names(c.get("credit_imgs", []))
        credit = (self.t["credit_prefix"] + " / ".join(names)) if names else ""
        return (f'<section class="card {c["theme"]}" id="c{no}" data-n="{no}">{stamp}'
                f'<div class="in"><h2 class="t">{self.protect(c["title"])}</h2>{lede}{body}{btm}</div>'
                f'<div class="ft"><span>{e(self.t["footer_label"])}</span><span class="cr">{credit}</span>'
                f'<span>{no}/{self.n}</span></div></section>')

    def cover(self, no, c):
        self.used.append(self.iid(c["image"]))
        sub = "<br>".join(e(x) for x in c["sub"])
        return (f'<section class="card ink cover" id="c{no}" data-n="{no}">\n<div class="in cv">\n'
                f'  <p class="where">{e(c["where"])}</p>\n  <h1>{e(c["title"])}</h1>\n  <p class="sub">{sub}</p>\n'
                f'  <p class="meta">{e(c["meta"])}</p>\n'
                f'  <figure class="arch door"><img src="{self.uri(c["image"])}" alt=""></figure>\n</div></section>')

    def credits_card(self, no):
        seen, lis = set(), []
        for iid in self.used:
            if iid in seen:
                continue
            seen.add(iid)
            m = self.man[iid]
            lis.append(f'<li><span>{e(m["artist"].split(" from ")[0])}</span><span>{e(m["license"])}</span></li>')
        t = self.t
        return (f'<section class="card ink" id="c{no}" data-n="{no}"><div class="in"><h2 class="t">{e(t["credits_title"])}</h2>'
                f'<p class="lede">{e(t["credits_lede"])}</p><ul class="credits">{"".join(lis)}</ul>'
                f'<p class="note">{e(t["credits_note"])}</p></div>'
                f'<div class="ft"><span>{e(t["footer_label"])}</span><span class="cr"></span><span>{no}/{self.n}</span></div></section>')

    def render(self):
        body = [self.card(i, c) for i, c in enumerate(self.cards, 1)]
        body.append(self.credits_card(len(self.cards) + 1))
        css = (HERE / "base.css").read_text(encoding="utf-8")
        for extra in self.t.get("extra_css", []):
            css += "\n" + (HERE / extra).read_text(encoding="utf-8")
        js = (HERE / "cards.js").read_text(encoding="utf-8")
        fonts = self.t.get("fonts_href")
        link = (f'<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="stylesheet" href="{fonts}">\n') if fonts else ""
        return (f'<!doctype html>\n<html lang="{self.t["lang"]}">\n<head>\n<meta charset="utf-8">\n'
                f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
                f'<title>{e(self.t["title"])}</title>\n{link}<style>\n{css}\n</style>\n</head>\n<body>\n'
                f'<main class="deck">\n' + "\n".join(body) + f'\n</main>\n<script>\n{js}\n</script>\n</body>\n</html>')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--content", required=True, type=pathlib.Path)
    ap.add_argument("--images", required=True, type=pathlib.Path, help="含 manifest.json 的图片目录")
    ap.add_argument("--out", required=True, type=pathlib.Path)
    a = ap.parse_args()
    deck = Deck(json.loads(a.content.read_text(encoding="utf-8")), a.images)
    a.out.write_text(deck.render(), encoding="utf-8")
    print(f"cards: {deck.n} -> {a.out} ({a.out.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
