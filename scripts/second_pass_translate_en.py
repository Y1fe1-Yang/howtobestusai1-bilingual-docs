from pathlib import Path
import re
import time
from typing import Dict

from bs4 import BeautifulSoup, Comment
from deep_translator import GoogleTranslator

ROOT = Path(r"d:\howtobestusai1")
SKIP_TAGS = {"script", "style", "pre", "code", "svg", "noscript", "textarea"}
PROTECTED_TERMS = [
    "HappyCapy",
    "MCP",
    "Skills",
    "Multi-Agent Team",
    "Automations",
    "Notion",
    "GitHub",
]

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
TOKEN_RE = re.compile(r"\b(?:ghp|ntn|sk|xoxb|xoxp)_[A-Za-z0-9_\-]+\b")
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def protect_segments(text: str):
    protected: Dict[str, str] = {}
    counter = 0

    def add_placeholder(value: str) -> str:
        nonlocal counter
        key = f"__PH_{counter}__"
        protected[key] = value
        counter += 1
        return key

    out = text
    out = URL_RE.sub(lambda m: add_placeholder(m.group(0)), out)
    out = EMAIL_RE.sub(lambda m: add_placeholder(m.group(0)), out)
    out = TOKEN_RE.sub(lambda m: add_placeholder(m.group(0)), out)

    for term in sorted(PROTECTED_TERMS, key=len, reverse=True):
        if term in out:
            out = out.replace(term, add_placeholder(term))

    return out, protected


def restore_segments(text: str, protected: Dict[str, str]) -> str:
    out = text
    for key, value in protected.items():
        out = out.replace(key, value)
    return out


def should_translate_node(node) -> bool:
    if not node:
        return False
    if isinstance(node, Comment):
        return False

    parent = node.parent
    if parent is None:
        return False
    if parent.name and parent.name.lower() in SKIP_TAGS:
        return False

    text = str(node)
    if not text.strip():
        return False
    return has_cjk(text)


def translate_text(translator: GoogleTranslator, text: str, cache: Dict[str, str]) -> str:
    if text in cache:
        return cache[text]

    src, protected = protect_segments(text)
    translated = src

    for attempt in range(1, 4):
        try:
            translated = translator.translate(src)
            break
        except Exception:
            if attempt == 3:
                translated = src
            else:
                time.sleep(1.2 * attempt)

    translated = restore_segments(translated, protected)
    cache[text] = translated
    return translated


def process_file(file_path: Path, translator: GoogleTranslator, cache: Dict[str, str]) -> int:
    html = file_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")

    changed = 0
    for node in soup.find_all(string=True):
        if not should_translate_node(node):
            continue
        original = str(node)
        translated = translate_text(translator, original, cache)
        if translated != original:
            node.replace_with(translated)
            changed += 1

    if changed:
        file_path.write_text(str(soup), encoding="utf-8")
    return changed


def main() -> None:
    files = sorted(ROOT.rglob("*_en.html"))
    translator = GoogleTranslator(source="zh-CN", target="en")
    cache: Dict[str, str] = {}

    changed_files = 0
    changed_nodes = 0

    for fp in files:
        c = process_file(fp, translator, cache)
        if c:
            changed_files += 1
            changed_nodes += c
            safe_path = str(fp).encode("ascii", "backslashreplace").decode("ascii")
            print(f"[UPDATED] {safe_path} ({c} nodes)")

    print(f"Done. files={len(files)}, changed_files={changed_files}, changed_nodes={changed_nodes}")


if __name__ == "__main__":
    main()
