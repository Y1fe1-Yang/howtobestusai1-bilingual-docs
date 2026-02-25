from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, unquote, quote
import re

ROOT = Path(r"d:\howtobestusai1")
HREF_PATTERN = re.compile(r'href="([^"]+)"', re.IGNORECASE)
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "javascript:", "#")


def should_skip(href: str) -> bool:
    h = (href or "").strip().lower()
    return (not h) or h.startswith(SKIP_PREFIXES)


def to_en_path(path_part: str) -> str | None:
    if not path_part.lower().endswith(".html"):
        return None
    if path_part.lower().endswith("_en.html"):
        return None
    return path_part[:-5] + "_en.html"


def resolve_target(current_file: Path, path_part: str) -> Path:
    decoded = unquote(path_part)
    if decoded.startswith("/"):
        return ROOT / decoded.lstrip("/")
    return current_file.parent / decoded


def rewrite_href(current_file: Path, href: str) -> str:
    split = urlsplit(href)
    if split.scheme or split.netloc:
        return href

    new_path = to_en_path(split.path)
    if not new_path:
        return href

    target = resolve_target(current_file, new_path)
    if not target.exists():
        return href

    encoded_path = quote(unquote(new_path), safe="/%:@()+,;=-_.~")
    return urlunsplit((split.scheme, split.netloc, encoded_path, split.query, split.fragment))


def process_file(file_path: Path) -> tuple[int, str]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    changed = 0

    def repl(match: re.Match) -> str:
        nonlocal changed
        old_href = match.group(1)
        if should_skip(old_href):
            return match.group(0)
        new_href = rewrite_href(file_path, old_href)
        if new_href != old_href:
            changed += 1
            return f'href="{new_href}"'
        return match.group(0)

    new_text = HREF_PATTERN.sub(repl, text)
    if changed:
        file_path.write_text(new_text, encoding="utf-8")
    return changed, str(file_path)


def main() -> None:
    files = sorted(ROOT.rglob("*_en.html"))
    changed_files = 0
    changed_links = 0

    for file_path in files:
        count, path_str = process_file(file_path)
        if count:
            changed_files += 1
            changed_links += count
            print(f"[UPDATED] {path_str} ({count} links)")

    print(f"Done. files={len(files)}, changed_files={changed_files}, changed_links={changed_links}")


if __name__ == "__main__":
    main()
