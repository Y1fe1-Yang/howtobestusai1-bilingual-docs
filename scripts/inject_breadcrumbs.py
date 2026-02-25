from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit, unquote, quote
import re
import os

ROOT = Path(r"d:\howtobestusai1")
MARK_START = "<!-- BREADCRUMB_START -->"
MARK_END = "<!-- BREADCRUMB_END -->"

HREF_PATTERN = re.compile(r'href="([^"]+)"', re.IGNORECASE)
TITLE_PATTERN = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
PAGE_TITLE_PATTERN = re.compile(r"<h1[^>]*class=\"page-title\"[^>]*>", re.IGNORECASE)

SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "javascript:", "#")


def is_lang_match(path: Path, is_en: bool) -> bool:
    return path.name.lower().endswith("_en.html") if is_en else (path.name.lower().endswith(".html") and not path.name.lower().endswith("_en.html"))


def get_html_files() -> list[Path]:
    files = sorted(
        p
        for p in ROOT.rglob("*.html")
        if "\\scripts\\" not in str(p).lower() and p.name.lower() != "index.html"
    )
    return files


def get_title(text: str, fallback: str) -> str:
    m = TITLE_PATTERN.search(text)
    if not m:
        return fallback
    return re.sub(r"\s+", " ", m.group(1)).strip() or fallback


def resolve_href(current_file: Path, href: str) -> Path | None:
    h = (href or "").strip()
    if not h:
        return None
    low = h.lower()
    if low.startswith(SKIP_PREFIXES):
        return None

    split = urlsplit(h)
    if split.scheme or split.netloc:
        return None

    path_part = unquote(split.path)
    if not path_part.lower().endswith(".html"):
        return None

    if path_part.startswith("/"):
        target = ROOT / path_part.lstrip("/")
    else:
        target = current_file.parent / path_part

    try:
        return target.resolve()
    except OSError:
        return None


def common_prefix_len(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    return n


def to_rel_href(src_file: Path, dst_file: Path) -> str:
    rel_str = os.path.relpath(dst_file, start=src_file.parent).replace("\\", "/")
    return quote(unquote(rel_str), safe="/%:@()+,;=-_.~")


def choose_parent(target: Path, inbounds: list[Path], home: Path, is_en: bool) -> Path:
    same_lang = [p for p in inbounds if is_lang_match(p, is_en) and p != target]
    if not same_lang:
        return home

    target_rel = target.relative_to(ROOT)
    t_parts = target_rel.parts
    target_dir_parts = target_rel.parent.parts

    def ancestor_distance(src: Path) -> int | None:
        src_dir_parts = src.relative_to(ROOT).parent.parts
        if len(src_dir_parts) >= len(target_dir_parts):
            return None
        if target_dir_parts[: len(src_dir_parts)] != src_dir_parts:
            return None
        return len(target_dir_parts) - len(src_dir_parts)

    hierarchical_candidates: list[tuple[int, Path]] = []
    for src in same_lang:
        dist = ancestor_distance(src)
        if dist is not None:
            hierarchical_candidates.append((dist, src))

    if hierarchical_candidates:
        hierarchical_candidates.sort(key=lambda row: (row[0], len(row[1].relative_to(ROOT).parts)))
        return hierarchical_candidates[0][1]

    def score(src: Path) -> tuple[int, int, int, int]:
        s_parts = src.relative_to(ROOT).parts
        s_depth = len(s_parts)
        t_depth = len(t_parts)
        shallower_flag = 0 if s_depth < t_depth else 1
        cpl = common_prefix_len(t_parts, s_parts)
        one_level_gap = abs((t_depth - 1) - s_depth)
        return (shallower_flag, -cpl, one_level_gap, s_depth)

    return sorted(same_lang, key=score)[0]


def structural_parent_by_directory(target: Path, files: list[Path], is_en: bool) -> Path | None:
    target_rel = target.relative_to(ROOT)
    target_parts = target_rel.parts
    if len(target_parts) <= 1:
        return None

    same_lang_files = [p for p in files if is_lang_match(p, is_en)]

    # Walk from nearest ancestor directory outward.
    for depth in range(len(target_parts) - 2, -1, -1):
        ancestor_dir = ROOT.joinpath(*target_parts[: depth + 1])
        dir_name = ancestor_dir.name
        container_dir = ancestor_dir.parent

        candidates = [
            p
            for p in same_lang_files
            if p.parent == container_dir and p.name.startswith(dir_name + " ")
        ]
        if candidates:
            return sorted(candidates, key=lambda p: len(p.name))[0]

    return None


def inject_breadcrumb(html: str, snippet: str) -> tuple[str, bool]:
    if MARK_START in html and MARK_END in html:
        start = html.find(MARK_START)
        end = html.find(MARK_END, start)
        if end >= 0:
            end += len(MARK_END)
            return html[:start] + snippet + html[end:], True
        return html, False

    m = PAGE_TITLE_PATTERN.search(html)
    if m:
        idx = m.start()
        return html[:idx] + snippet + html[idx:], True

    lower = html.lower()
    body_idx = lower.find("<body")
    if body_idx >= 0:
        gt = html.find(">", body_idx)
        if gt >= 0:
            return html[: gt + 1] + snippet + html[gt + 1 :], True

    end_body = lower.rfind("</body>")
    if end_body >= 0:
        return html[:end_body] + snippet + html[end_body:], True

    return html + "\n" + snippet + "\n", True


def build_snippet(current_file: Path, title: str, home_file: Path, parent_file: Path, title_map: dict[Path, str], is_en: bool) -> str:
    home_text = "Home" if is_en else "首页"
    parent_text = title_map.get(parent_file, "Parent" if is_en else "父页面")
    current_text = title

    home_href = to_rel_href(current_file, home_file)
    parent_href = to_rel_href(current_file, parent_file)

    return f'''{MARK_START}
<style>
.hc-breadcrumb {{
  font-size: 14px;
  margin-bottom: 0.75em;
}}
.hc-breadcrumb-sep {{
  margin: 0 0.35em;
  opacity: 0.6;
}}
</style>
<nav class="hc-breadcrumb" aria-label="Breadcrumb">
  <a href="{home_href}">{home_text}</a>
  <span class="hc-breadcrumb-sep">/</span>
  <a href="{parent_href}">{parent_text}</a>
  <span class="hc-breadcrumb-sep">/</span>
  <span aria-current="page">{current_text}</span>
</nav>
{MARK_END}
'''


def main() -> None:
    files = get_html_files()
    file_set = {p.resolve() for p in files}

    title_map: dict[Path, str] = {}
    links_out: dict[Path, list[Path]] = {}
    links_in: dict[Path, list[Path]] = {p.resolve(): [] for p in files}

    for fp in files:
        resolved_fp = fp.resolve()
        text = fp.read_text(encoding="utf-8", errors="ignore")
        title_map[resolved_fp] = get_title(text, fp.stem)

        out_targets: list[Path] = []
        for m in HREF_PATTERN.finditer(text):
            target = resolve_href(fp, m.group(1))
            if target and target in file_set:
                out_targets.append(target)
                links_in[target].append(resolved_fp)
        links_out[resolved_fp] = out_targets

    zh_home_candidates = [p.resolve() for p in files if p.name.startswith("WaytoAGI x Happycapy ") and p.name.lower().endswith(".html") and not p.name.lower().endswith("_en.html")]
    en_home_candidates = [p.resolve() for p in files if p.name.startswith("WaytoAGI x Happycapy ") and p.name.lower().endswith("_en.html")]

    if not zh_home_candidates or not en_home_candidates:
        raise RuntimeError("Cannot find zh/en home files.")

    zh_home = sorted(zh_home_candidates, key=lambda p: len(p.name))[0]
    en_home = sorted(en_home_candidates, key=lambda p: len(p.name))[0]

    changed = 0
    skipped_has_marker = 0
    fallback_to_home = 0

    for fp in files:
        resolved_fp = fp.resolve()
        is_en = resolved_fp.name.lower().endswith("_en.html")
        home_file = en_home if is_en else zh_home

        if resolved_fp == home_file:
            parent_file = home_file
        else:
            inbounds = links_in.get(resolved_fp, [])
            parent_file = choose_parent(resolved_fp, inbounds, home_file, is_en)
            if parent_file == home_file:
                structural_parent = structural_parent_by_directory(resolved_fp, files, is_en)
                if structural_parent is not None and structural_parent != resolved_fp:
                    parent_file = structural_parent
            if parent_file == home_file and resolved_fp != home_file:
                fallback_to_home += 1

        original = fp.read_text(encoding="utf-8", errors="ignore")
        snippet = build_snippet(
            current_file=resolved_fp,
            title=title_map.get(resolved_fp, fp.stem),
            home_file=home_file,
            parent_file=parent_file,
            title_map=title_map,
            is_en=is_en,
        )

        updated, did = inject_breadcrumb(original, snippet)
        if did:
            fp.write_text(updated, encoding="utf-8")
            changed += 1
        else:
            skipped_has_marker += 1

    print(f"Done. files={len(files)}, changed={changed}, skipped_existing={skipped_has_marker}, fallback_to_home={fallback_to_home}")


if __name__ == "__main__":
    main()
