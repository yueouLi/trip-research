#!/usr/bin/env python3
"""图片工具：下载 markdown 里的远程图、替换为本地路径、查 Wikimedia Commons 作者和许可证。

  python3 fetch_images.py download --out images/ --mapping map.json a.md b.md
  python3 fetch_images.py replace  --mapping map.json a.md b.md          # 原地替换成相对路径
  python3 fetch_images.py licenses --mapping map.json --out images/manifest.json

下载会限速，遇到 429 自动退避；连续被拒就停下，不硬抓。
卡片引擎需要 images/manifest.json（licenses 子命令生成）。
"""
import argparse, html, json, os, pathlib, re, subprocess, sys, time, urllib.parse, urllib.request

IMG_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)\s]+)\)")
UA = "trip-research-skill/1.0 (personal research use)"


def collect(files):
    urls = []
    for f in files:
        if os.path.exists(f):
            urls += IMG_RE.findall(open(f, encoding="utf-8").read())
    return list(dict.fromkeys(urls))


def fetch(url, target):
    """返回 'ok' / 'ratelimited' / 'error'。"""
    delay = 5
    for _ in range(3):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            data = urllib.request.urlopen(req, timeout=60).read()
            if len(data) < 1000:
                return "error"
            pathlib.Path(target).write_bytes(data)
            return "ok"
        except urllib.error.HTTPError as e:
            if e.code != 429:
                return "error"
            time.sleep(delay)
            delay *= 2
        except Exception:
            return "error"
    return "ratelimited"


def download(a):
    os.makedirs(a.out, exist_ok=True)
    mp = json.load(open(a.mapping, encoding="utf-8")) if os.path.exists(a.mapping) else {}
    idx, limited = len(mp), 0
    for url in collect(a.files):
        if url in mp:
            continue
        ext = os.path.splitext(url.split("?")[0])[1].lower()
        ext = ext if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp") else ".jpg"
        local = os.path.join(a.out, f"img_{idx:03d}{ext}")
        res = fetch(url, local)
        print(f"{res:12s} {url[:90]}")
        if res == "ok":
            mp[url] = local
            idx += 1
            limited = 0
        elif res == "ratelimited":
            limited += 1
            if limited >= 3:
                print("连续被限流，先停下。过一阵再运行，会从断点继续。")
                break
        time.sleep(1.2)
        json.dump(mp, open(a.mapping, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(mp, open(a.mapping, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(mp)} 张已下载")


def replace(a):
    mp = json.load(open(a.mapping, encoding="utf-8"))
    for f in a.files:
        p = pathlib.Path(f)
        s = p.read_text(encoding="utf-8")
        for url, local in mp.items():
            rel = os.path.relpath(local, p.parent.resolve()) if os.path.isabs(local) else local
            s = s.replace(f"]({url})", f"]({rel})")
        p.write_text(s, encoding="utf-8")
        print("替换：", f)


def licenses(a):
    mp = json.load(open(a.mapping, encoding="utf-8"))
    entries = {}
    for url, local in mp.items():
        m = re.search(r"/wikipedia/commons/(?:thumb/)?[0-9a-f]/[0-9a-f]{2}/([^/]+)", url)
        if not m:
            continue
        name = urllib.parse.unquote(m.group(1)).replace("_", " ")
        iid = pathlib.Path(local).stem
        entries[iid] = {"file": pathlib.Path(local).name, "title": name, "source_url": url}
    titles = [v["title"] for v in entries.values()]
    meta = {}
    for i in range(0, len(titles), 20):
        q = urllib.parse.urlencode({"action": "query", "titles": "|".join("File:" + t for t in titles[i:i + 20]),
                                    "prop": "imageinfo", "iiprop": "extmetadata",
                                    "iiextmetadatafilter": "Artist|LicenseShortName", "format": "json", "formatversion": 2})
        req = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + q, headers={"User-Agent": UA})
        d = json.load(urllib.request.urlopen(req, timeout=40))
        strip = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(s or ""))).strip()
        for p in d["query"]["pages"]:
            e = p.get("imageinfo", [{}])[0].get("extmetadata", {})
            meta[p["title"][5:]] = (strip(e.get("Artist", {}).get("value")), strip(e.get("LicenseShortName", {}).get("value")))
        time.sleep(1.2)
    for v in entries.values():
        v["artist"], v["license"] = meta.get(v["title"], ("", ""))
    json.dump(entries, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    missing = [k for k, v in entries.items() if not v["license"]]
    print(f"{len(entries)} 张写入 {a.out}" + (f"；缺许可证信息：{missing}（手动补，补完才能发布）" if missing else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    d = sp.add_parser("download"); d.add_argument("--out", required=True); d.add_argument("--mapping", required=True); d.add_argument("files", nargs="+")
    r = sp.add_parser("replace"); r.add_argument("--mapping", required=True); r.add_argument("files", nargs="+")
    l = sp.add_parser("licenses"); l.add_argument("--mapping", required=True); l.add_argument("--out", required=True)
    a = ap.parse_args()
    {"download": download, "replace": replace, "licenses": licenses}[a.cmd](a)


if __name__ == "__main__":
    main()
