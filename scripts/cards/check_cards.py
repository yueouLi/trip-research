#!/usr/bin/env python3
"""检查每张卡片的内容有没有溢出（压到页脚或超出右边）。有问题时退出码为 1。
用法：python3 check_cards.py --html cards.html
"""
import argparse, json, pathlib, re, subprocess, sys
from _chromium import find_chromium


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True, type=pathlib.Path)
    a = ap.parse_args()
    r = subprocess.run([find_chromium(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1080,1920",
                        "--virtual-time-budget=4000", "--dump-dom", f"file://{a.html.resolve()}#check"],
                       capture_output=True, text=True)
    m = re.search(r'<script type="application/json" id="qa">(.*?)</script>', r.stdout, re.S)
    if not m:
        sys.exit("没有取到检查结果。检查 Chromium 是否能运行，以及 cards.js 是否是新版。")
    bad = [c for c in json.loads(m.group(1)) if c["overflow"] > 0 or c["right"] > 0]
    for c in bad:
        why = []
        if c["overflow"] > 0:
            why.append(f"内容压到页脚，超出 {c['overflow']} cqw（最靠下的元素：{c.get('who', '?')}）")
        if c["right"] > 0:
            why.append(f"超出右边 {c['right']} cqw")
        print(f"第 {c['n']} 张：" + "；".join(why))
    if bad:
        print("修法：先删字，其次缩小照片，最后拆成两张。")
        sys.exit(1)
    print("所有卡片通过溢出检查。")


if __name__ == "__main__":
    main()
