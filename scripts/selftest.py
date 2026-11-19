#!/usr/bin/env python3
"""自检：用自带的丹吉尔示例重新生成所有产物，确认这套 skill 在你的机器上能复现。
用法：python3 scripts/selftest.py
通过的标志：卡片 HTML 的哈希和 examples/tangier/expected.json 一致；溢出检查通过；PDF 能生成（装了 markdown 库时）。
"""
import hashlib, json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
EX = ROOT / "examples" / "tangier"
SC = ROOT / "scripts"
ok = True


def step(name, passed, detail=""):
    global ok
    ok = ok and passed
    print(("通过  " if passed else "失败  ") + name + (f"  {detail}" if detail else ""))


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)


def main():
    exp = json.loads((EX / "expected.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        for lang in ("zh", "en"):
            out = tmp / f"{lang}.html"
            r = run(SC / "cards/build_cards.py", "--content", EX / f"content/{lang}.json", "--images", EX / "images", "--out", out)
            step(f"生成卡片 {lang}", r.returncode == 0, r.stderr.strip()[-200:])
            if r.returncode:
                continue
            h = hashlib.sha256(out.read_bytes()).hexdigest()
            step(f"卡片 {lang} 与预期完全一致", h == exp["cards_sha256"][lang], "" if h == exp["cards_sha256"][lang] else f"得到 {h[:12]}，预期 {exp['cards_sha256'][lang][:12]}")
            r = run(SC / "cards/check_cards.py", "--html", out)
            step(f"卡片 {lang} 溢出检查", r.returncode == 0, r.stdout.strip()[:200])
        r = run(SC / "cards/export_cards.py", "--html", tmp / "zh.html", "--out", tmp / "png")
        n = len(list((tmp / "png").glob("*.png"))) if (tmp / "png").exists() else 0
        step("导出 PNG", r.returncode == 0 and n == exp["card_count"], f"{n} 张")
        r = run(SC / "pdf/make_report_pdf.py",
                "--part", f"中文版=" + str(EX / "reports/websites.zh.md"), "--part", f"Deutsche Fassung=" + str(EX / "reports/websites.de.md"),
                "--title", "自检", "--out", tmp / "r.pdf")
        if "markdown" in (r.stderr + r.stdout) and "缺少" in (r.stderr + r.stdout):
            print("跳过  PDF：没装 markdown 库（python3 -m pip install markdown）")
        else:
            size = (tmp / "r.pdf").stat().st_size if (tmp / "r.pdf").exists() else 0
            step("生成 PDF", r.returncode == 0 and size > 10000, f"{size} bytes")
    print("\n全部通过，可以开始用了。" if ok else "\n有失败项，先看上面的提示。")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
