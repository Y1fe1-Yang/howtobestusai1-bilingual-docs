import argparse
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Protocol, Tuple

from bs4 import BeautifulSoup, Comment, NavigableString
from deep_translator import GoogleTranslator
import requests

SKIP_TAGS = {
    "script",
    "style",
    "code",
    "pre",
    "svg",
    "noscript",
    "textarea",
}

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


def should_skip_text_node(node: NavigableString) -> bool:
    if not node or not str(node).strip():
        return True

    if isinstance(node, Comment):
        return True

    parent = node.parent
    if parent is None:
        return True

    if parent.name and parent.name.lower() in SKIP_TAGS:
        return True

    classes = parent.get("class", [])
    if any("code" in cls.lower() for cls in classes):
        return True

    text = str(node)
    if not has_cjk(text):
        return True

    return False


def protect_segments(text: str) -> Tuple[str, Dict[str, str]]:
    protected: Dict[str, str] = {}
    counter = 0

    def add_placeholder(value: str) -> str:
        nonlocal counter
        key = f"__PH_{counter}__"
        protected[key] = value
        counter += 1
        return key

    def repl_regex(pattern: re.Pattern[str], source: str) -> str:
        return pattern.sub(lambda m: add_placeholder(m.group(0)), source)

    out = text
    out = repl_regex(URL_RE, out)
    out = repl_regex(EMAIL_RE, out)
    out = repl_regex(TOKEN_RE, out)

    for term in sorted(PROTECTED_TERMS, key=len, reverse=True):
        if term in out:
            out = out.replace(term, add_placeholder(term))

    return out, protected


def restore_segments(text: str, protected: Dict[str, str]) -> str:
    out = text
    for key, value in protected.items():
        out = out.replace(key, value)
    return out


class TextTranslator(Protocol):
    def translate(self, text: str) -> str:
        ...


class DeepTranslatorAdapter:
    def __init__(self) -> None:
        self.translator = GoogleTranslator(source="zh-CN", target="en")

    def translate(self, text: str) -> str:
        return self.translator.translate(text)


class GeminiTranslator:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", timeout: int = 60) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.model_candidates = self._build_model_candidates(model)
        self.endpoint = self._endpoint_for(self.model_candidates[0])

    def _build_model_candidates(self, preferred: str) -> List[str]:
        candidates = [
            preferred,
            "gemini-2.0-flash-exp",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
        ]
        deduped: List[str] = []
        for item in candidates:
            if item and item not in deduped:
                deduped.append(item)
        return deduped

    def _endpoint_for(self, model: str) -> str:
        return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def translate(self, text: str) -> str:
        prompt = (
            "Translate the following text from Simplified Chinese to English in concise "
            "product-documentation style. Keep placeholders exactly unchanged if they look "
            "like __PH_0__, __PH_1__, etc. Return only the translated text, no explanation.\n\n"
            f"TEXT:\n{text}"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.8,
                "topK": 20,
            },
        }

        body = None
        last_error: Exception | None = None

        for model in self.model_candidates:
            endpoint = self._endpoint_for(model)
            try:
                response = requests.post(
                    endpoint,
                    params={"key": self.api_key},
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                body = response.json()
                self.model = model
                self.endpoint = endpoint
                break
            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else None
                if status == 404:
                    last_error = exc
                    continue
                raise

        if body is None:
            if last_error is not None:
                raise last_error
            raise RuntimeError("Gemini request failed with no response body")

        candidates = body.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned no candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError("Gemini returned empty content")

        translated = parts[0].get("text", "")
        if not translated:
            raise RuntimeError("Gemini returned empty translation")

        return translated.strip()


def translate_text(
    translator: TextTranslator,
    text: str,
    cache: Dict[str, str],
    retries: int = 3,
) -> str:
    if text in cache:
        return cache[text]

    src, protected = protect_segments(text)

    translated = src
    for attempt in range(1, retries + 1):
        try:
            translated = translator.translate(src)
            break
        except Exception:
            if attempt == retries:
                translated = src
            else:
                time.sleep(1.2 * attempt)

    translated = restore_segments(translated, protected)
    cache[text] = translated
    return translated


def collect_html_files(root: Path) -> List[Path]:
    files = [
        p
        for p in root.rglob("*.html")
        if not p.name.lower().endswith("_en.html")
    ]
    return sorted(files)


def output_path_for(source: Path) -> Path:
    return source.with_name(f"{source.stem}_en{source.suffix}")


def translate_html_file(file_path: Path, translator: TextTranslator, cache: Dict[str, str]) -> Tuple[int, Path]:
    html = file_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    translated_count = 0

    if soup.title and soup.title.string and has_cjk(soup.title.string):
        original_title = soup.title.string
        new_title = translate_text(translator, original_title, cache)
        if new_title != original_title:
            soup.title.string.replace_with(new_title)
            translated_count += 1

    text_nodes = soup.find_all(string=True)
    for node in text_nodes:
        if should_skip_text_node(node):
            continue

        original_text = str(node)
        new_text = translate_text(translator, original_text, cache)

        if new_text != original_text:
            node.replace_with(new_text)
            translated_count += 1

    out_path = output_path_for(file_path)
    out_path.write_text(str(soup), encoding="utf-8")

    return translated_count, out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate Chinese text in HTML files to English while preserving links/code.")
    parser.add_argument("root", type=str, nargs="?", default=".", help="Root folder to scan for HTML files")
    parser.add_argument("--limit", type=int, default=0, help="Only process first N files (for trial run)")
    parser.add_argument("--provider", choices=["google", "gemini"], default="google", help="Translation provider")
    parser.add_argument("--gemini-model", type=str, default="gemini-2.0-flash", help="Gemini model name")
    parser.add_argument("--only-missing", action="store_true", help="Only create missing *_en.html files")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = collect_html_files(root)

    if args.only_missing:
        files = [f for f in files if not output_path_for(f).exists()]

    if args.limit > 0:
        files = files[: args.limit]

    if not files:
        print("No HTML files found.")
        return

    if args.provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Please set it in your environment.")
        translator: TextTranslator = GeminiTranslator(api_key=api_key, model=args.gemini_model)
    else:
        translator = DeepTranslatorAdapter()

    cache: Dict[str, str] = {}

    total_nodes = 0
    for index, file_path in enumerate(files, start=1):
        translated_count, out_path = translate_html_file(file_path, translator, cache)
        total_nodes += translated_count
        print(f"[{index}/{len(files)}] {file_path} -> {out_path} | translated nodes: {translated_count}")

    print(f"Done. files={len(files)}, translated_nodes={total_nodes}")


if __name__ == "__main__":
    main()
