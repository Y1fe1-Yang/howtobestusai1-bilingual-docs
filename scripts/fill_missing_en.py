from pathlib import Path

from deep_translator import GoogleTranslator

from translate_html_to_en import translate_html_file


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    files = sorted(
        p for p in root.rglob("*.html") if not p.name.lower().endswith("_en.html")
    )
    missing = [
        p for p in files if not p.with_name(f"{p.stem}_en{p.suffix}").exists()
    ]

    translator = GoogleTranslator(source="zh-CN", target="en")
    cache: dict[str, str] = {}

    created = 0
    for path in missing:
        _, out_path = translate_html_file(path, translator, cache)
        if out_path.exists():
            created += 1

    remaining = 0
    files_after = sorted(
        p for p in root.rglob("*.html") if not p.name.lower().endswith("_en.html")
    )
    for path in files_after:
        if not path.with_name(f"{path.stem}_en{path.suffix}").exists():
            remaining += 1

    print(f"created={created}")
    print(f"remaining={remaining}")


if __name__ == "__main__":
    main()
