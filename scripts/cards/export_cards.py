#!/usr/bin/env python3
"""把卡片 HTML 的每一张导出成 1080x1920 的 PNG。
用法：python3 export_cards.py --html cards.html --out png/
"""
import argparse, pathlib, re, subprocess
from _chromium import find_chromium


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--size", default="1080,1920", help="宽,高，必须是 9:16")
    a = ap.parse_args()
    html = a.html.resolve()
    n = len(re.findall(r'<section class="card', html.read_text(encoding="utf-8")))
    a.out.mkdir(parents=True, exist_ok=True)
    chrome = find_chromium()
    for i in range(1, n + 1):
        target = a.out / f"{i:02d}.png"
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={a.size}",
                        "--virtual-time-budget=4000", f"--screenshot={target}", f"file://{html}#c{i}"],
                       check=True, capture_output=True)
    print(f"exported {n} cards to {a.out}")


if __name__ == "__main__":
    main()
