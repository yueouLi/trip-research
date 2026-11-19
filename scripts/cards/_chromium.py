"""找本机的 Chromium 或 Chrome。"""
import shutil, os


def find_chromium():
    env = os.environ.get("CHROMIUM")
    if env and shutil.which(env):
        return shutil.which(env)
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    for p in ("/usr/sbin/chromium", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if os.path.exists(p):
            return p
    raise SystemExit("找不到 Chromium/Chrome。请安装，或设置环境变量 CHROMIUM=/path/to/chromium")
