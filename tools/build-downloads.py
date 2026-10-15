"""Build a dependency-free, CSP-protected offline edition of WinShelf."""
from pathlib import Path
import base64
import hashlib
import re
import zipfile

root = Path(__file__).resolve().parents[1]
html = (root / "index.html").read_text(encoding="utf-8")
css = "\n" + (root / "style.css").read_text(encoding="utf-8") + "\n"
js = "\n" + (root / "app.js").read_text(encoding="utf-8") + "\n"
if "</script" in js.lower() or "</style" in css.lower():
    raise ValueError("An embedded source contains a closing HTML tag")

def csp_hash(source):
    return base64.b64encode(hashlib.sha256(source.encode("utf-8")).digest()).decode("ascii")

html = html.replace('<link rel="stylesheet" href="style.css">', "<style>" + css + "</style>")
html = html.replace('<script src="app.js" defer></script>', "")
html = html.replace("script-src 'self'; style-src 'self';",
                    "script-src 'sha256-" + csp_hash(js) + "'; style-src 'sha256-" + csp_hash(css) + "';")
html = re.sub(r"<!-- offline-downloads:start -->.*?<!-- offline-downloads:end -->",
              '<aside class="offline-downloads"><p>单文件版 · 下载后可离线使用。<br>'
              '<small>记录保存在当前浏览器，请定期使用「本地备份」。 / Single-file edition</small></p></aside>',
              html, flags=re.S)
html = html.replace("</body>", "<script>" + js + "</script>\n</body>")

downloads = root / "downloads"
downloads.mkdir(exist_ok=True)
(downloads / "WinShelf.html").write_text(html, encoding="utf-8")
offline_readme = """# 今日有成 / WinShelf 离线版

双击 WinShelf.html，在 Chrome、Edge 等浏览器中打开。无需安装、注册或联网。
写下一件完成的小事，选物件，放上架子；点击物件回看或编辑。
“精选导出”只导出你勾选的记录；可保存高清 PNG。

记录仅保存在当前浏览器。清除浏览器数据、换浏览器或移动文件都可能让原记录无法读取。
请用“本地备份”下载全部记录的 JSON，再在新版本恢复。PNG 不能恢复可编辑记录。
在线版、离线文件、不同浏览器的记录相互独立，没有云同步。

Open WinShelf.html in a browser. No installation or network is required.
Data stays in this browser. Export a JSON backup before moving the file or changing browsers.

反馈：https://github.com/tryu-ai/winshelf/issues （需 GitHub 账号）。可写设备、问题和是否愿意再次使用；请勿公开个人记录。
Feedback: https://github.com/tryu-ai/winshelf/issues (GitHub account required). Include your device, the problem, and whether you would use WinShelf again. Do not post personal records.

在线试玩：https://tryu-ai.github.io/winshelf/
项目源码：https://github.com/tryu-ai/winshelf
代码与原创素材采用 MIT 许可证，见 LICENSE。
"""
(downloads / "README-offline.md").write_text(offline_readme, encoding="utf-8")
with zipfile.ZipFile(downloads / "WinShelf-offline.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("WinShelf/WinShelf.html", html)
    archive.writestr("WinShelf/README.md", offline_readme)
    archive.write(root / "LICENSE", "WinShelf/LICENSE")
print("Built downloads/WinShelf.html and downloads/WinShelf-offline.zip")
