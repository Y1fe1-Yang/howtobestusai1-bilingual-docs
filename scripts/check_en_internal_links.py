from pathlib import Path
from urllib.parse import urlsplit, unquote
import re

ROOT = Path(r"d:\howtobestusai1")
HREF_PATTERN = re.compile(r'href="([^"]+)"', re.IGNORECASE)
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "javascript:", "#")


def main() -> None:
    pending: list[tuple[str, str, str]] = []
    for fp in sorted(ROOT.rglob("*_en.html")):
        text = fp.read_text(encoding="utf-8", errors="ignore")
        for match in HREF_PATTERN.finditer(text):
            href = match.group(1).strip()
            low = href.lower()
            if not href or low.startswith(SKIP_PREFIXES):
                continue

            split = urlsplit(href)
            path_part = split.path
            if not path_part.lower().endswith(".html") or path_part.lower().endswith("_en.html"):
                continue

            candidate = path_part[:-5] + "_en.html"
            target = (ROOT / unquote(candidate.lstrip("/"))) if candidate.startswith("/") else (fp.parent / unquote(candidate))
            if target.exists():
                pending.append((str(fp), href, candidate))

    print(f"PENDING {len(pending)}")
    for row in pending[:50]:
        print(f"{row[0]} => {row[1]} -> {row[2]}")


if __name__ == "__main__":
    main()
