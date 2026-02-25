from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import re

from opencc import OpenCC

ROOT = Path(r"d:\howtobestusai1")
HREF_PATTERN = re.compile(r'href="([^"]+)"', re.IGNORECASE)
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "javascript:", "#")


def get_zh_files() -> list[Path]:
    return sorted(
        p
        for p in ROOT.rglob("*.html")
        if "\\scripts\\" not in str(p).lower()
        and p.name.lower() != "index.html"
        and not p.name.lower().endswith("_en.html")
        and not p.name.lower().endswith("_tw.html")
    )


def to_tw_filename(path_text: str) -> str:
    if path_text.lower().endswith(".html") and not path_text.lower().endswith("_tw.html"):
        return path_text[:-5] + "_tw.html"
    return path_text


def rewrite_local_href(href: str) -> str:
    raw = (href or "").strip()
    if not raw:
        return href

    low = raw.lower()
    if low.startswith(SKIP_PREFIXES):
        return href

    split = urlsplit(raw)
    if split.scheme or split.netloc:
        return href

    new_path = to_tw_filename(split.path)
    if new_path == split.path:
        return href

    return urlunsplit((split.scheme, split.netloc, new_path, split.query, split.fragment))


def rewrite_hrefs(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        src = match.group(1)
        dst = rewrite_local_href(src)
        return f'href="{dst}"'

    return HREF_PATTERN.sub(repl, html)


def main() -> None:
    converter = OpenCC("s2t")
    zh_files = get_zh_files()

    changed = 0
    for src in zh_files:
        raw = src.read_text(encoding="utf-8", errors="ignore")
        converted = converter.convert(raw)
        converted = rewrite_hrefs(converted)

        dst = src.with_name(src.stem + "_tw.html")
        dst.write_text(converted, encoding="utf-8")
        changed += 1

    print(f"Done. zh_files={len(zh_files)}, tw_written={changed}")


if __name__ == "__main__":
    main()
