#!/usr/bin/env python3
"""多语言 markdown 报告 -> 一份 A4 PDF（封面 + 每种语言一部分）。

用法（中德双语）：
  python3 make_report_pdf.py \
    --part "第一部分 · 中文版|Teil 1 · Chinesische Fassung=cn.md" \
    --part "第二部分 · Deutsche Fassung|Teil 2 · 德语版=de.md" \
    --title "丹吉尔草药铺<br>完全使用手册" --sub "Kräuter- und Gewürzläden in Tanger" \
    --meta "调研日期 2026-09" --edition "中德双语版 · Zweisprachig" --out report.pdf

  --part "横幅标题|横幅副标题=file1.md,file2.md"，可重复；单语言就只给一个 --part。
  markdown 里的图片用本地路径（相对 md 文件），远程图先用 scripts/images/fetch_images.py 下载并替换。

依赖：python 的 markdown 库（pip install markdown）和本机的 Chromium 或 Chrome。
"""
import argparse, html as htmllib, os, pathlib, re, subprocess, sys

try:
    import markdown
except ImportError:
    sys.exit("缺少 markdown 库。运行：python3 -m pip install markdown（建议在虚拟环境里）")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _chromium import find_chromium

HERE = pathlib.Path(__file__).resolve().parent


def read_joined(spec):
    """逗号分隔多文件，按顺序拼接；每个文件去掉第一个标题之前的开场白。"""
    out = ""
    for f in spec.split(","):
        f = f.strip()
        if not f:
            continue
        part = pathlib.Path(f).read_text(encoding="utf-8")
        m = re.search(r"(?m)^#\s+", part)
        if m:
            part = part[m.start():]
        out += part + "\n\n"
    return out


def strip_first_h1(md):
    out, first = [], True
    for ln in md.split("\n"):
        if first and ln.startswith("# "):
            first = False
            continue
        out.append(ln)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--part", action="append", required=True, help='"横幅标题|横幅副标题=文件1.md,文件2.md"')
    ap.add_argument("--title", required=True, help="封面标题，<br> 换行")
    ap.add_argument("--sub", default="", help="封面副标题")
    ap.add_argument("--edition", default="", help="封面上的版本说明，例如 中德双语版")
    ap.add_argument("--meta", action="append", default=[], help="封面底部信息行，可重复")
    ap.add_argument("--lang", default="zh", help="html lang")
    ap.add_argument("--out", required=True, type=pathlib.Path)
    a = ap.parse_args()

    ext = ["tables", "sane_lists", "fenced_code"]
    parts_html, first_dir = [], None
    for spec in a.part:
        head, _, files = spec.partition("=")
        if not files:
            sys.exit(f'--part 格式应为 "标题|副标题=文件.md"，收到：{spec}')
        title, _, sub = head.partition("|")
        first_dir = first_dir or pathlib.Path(files.split(",")[0].strip()).resolve().parent
        body = markdown.markdown(strip_first_h1(read_joined(files)), extensions=ext)
        sub_html = f"<p>{sub}</p>" if sub else ""
        parts_html.append(f'<div class="part-banner"><h2>{title}</h2>{sub_html}</div>\n{body}')

    meta = "".join(f"<div>{m}</div>\n" for m in a.meta)
    edition = f'<p class="sub2">{a.edition}</p>' if a.edition else ""
    cover = (f'<div class="cover"><div class="band"><h1>{a.title}</h1><p class="sub">{a.sub}</p>{edition}</div>'
             f'<div class="meta">{meta}</div></div>')
    css = (HERE / "report.css").read_text(encoding="utf-8")
    page = (f'<!DOCTYPE html>\n<html lang="{a.lang}"><head><meta charset="utf-8">\n'
            f'<base href="file://{first_dir}/">\n'
            f'<title>{htmllib.unescape(re.sub("<br ?/?>", " ", a.title))}</title>\n<style>{css}</style></head><body>\n'
            f'{cover}\n' + "\n".join(parts_html) + "\n</body></html>")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    out_html = a.out.with_suffix(".html")
    out_html.write_text(page, encoding="utf-8")
    r = subprocess.run([find_chromium(), "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={a.out.resolve()}", str(out_html.resolve())], capture_output=True, text=True)
    if not a.out.exists():
        sys.exit("PDF 生成失败：" + r.stderr[-500:])
    print(f"PDF: {a.out} ({a.out.stat().st_size} bytes)；HTML: {out_html}")


if __name__ == "__main__":
    main()
