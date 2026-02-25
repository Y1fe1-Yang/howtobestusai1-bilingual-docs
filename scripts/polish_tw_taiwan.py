from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(r"d:\howtobestusai1")
TOKEN_RE = re.compile(r"(<[^>]+>)")

# 词汇优先替换（偏台湾用语）
LEXICAL_REPLACEMENTS: list[tuple[str, str]] = [
    ("視頻", "影片"),
    ("數據", "資料"),
    ("文件", "檔案"),
    ("文檔", "文件"),
    ("軟件", "軟體"),
    ("支持", "支援"),
    ("默認", "預設"),
    ("信息", "資訊"),
    ("用戶", "使用者"),
    ("用户", "使用者"),
    ("界面", "介面"),
    ("平臺", "平台"),
    ("登錄", "登入"),
    ("代碼", "程式碼"),
    ("配置", "設定"),
    ("調用", "呼叫"),
    ("創建", "建立"),
    ("創建後", "建立後"),
    ("獲取", "取得"),
    ("獲取到", "取得"),
    ("複製", "複製"),
    ("上傳", "上傳"),
    ("下載", "下載"),
    ("鏈接", "連結"),
    ("鏈接：", "連結："),
    ("點擊", "點選"),
    ("按鈕", "按鈕"),
    ("運行", "執行"),
    ("運行在", "執行於"),
    ("官網直通車", "官方網站"),
    ("搞定", "完成"),
    ("最棒的是", "另外"),
    ("沒反應", "沒有反應"),
    ("控制檯", "主控台"),
    ("幫你", "協助你"),
]

# 句级微调（维持原结构，只调整语气）
PHRASE_REPLACEMENTS: list[tuple[str, str]] = [
    ("在這裏，你可以看到機智可愛的 HappyCapy 如何成爲你的 AI 夥伴，一起探索無限可能！", "在這裡，你可以看看機智可愛的 HappyCapy 如何成為你的 AI 夥伴，一起探索更多可能。"),
    ("你不用再追着最新模型跑了！", "你不用再一直追著最新模型。"),
    ("別想了。HappyCapy 會幫你選。", "不用糾結，HappyCapy 會協助你選擇。"),
    ("不需要配環境，不需要學命令行，不需要懂技術。", "不需要設定環境，不需要學命令列，也不需要技術背景。"),
    ("你只需要用自然語言告訴 HappyCapy 你想做什麼就行了！", "你只要用自然語言告訴 HappyCapy 想完成什麼即可。"),
    ("只需要簡單的 Token 配置就能使用。", "只要簡單設定 Token 就能使用。"),
]


def get_tw_files() -> list[Path]:
    return sorted(
        p
        for p in ROOT.rglob("*_tw.html")
        if "\\scripts\\" not in str(p).lower()
    )


def polish_text(text: str) -> str:
    out = text
    for src, dst in PHRASE_REPLACEMENTS:
        out = out.replace(src, dst)
    for src, dst in LEXICAL_REPLACEMENTS:
        out = out.replace(src, dst)
    out = re.sub(r"(?<!請)幫我", "請幫我", out)
    out = re.sub(r"請請幫我", "請幫我", out)
    return out


def polish_html(html: str) -> str:
    parts = TOKEN_RE.split(html)
    in_script = False
    in_style = False

    for i, part in enumerate(parts):
        if not part:
            continue

        if part.startswith("<"):
            tag_l = part.lower()
            if tag_l.startswith("<script"):
                in_script = True
            elif tag_l.startswith("</script"):
                in_script = False
            elif tag_l.startswith("<style"):
                in_style = True
            elif tag_l.startswith("</style"):
                in_style = False
            continue

        if in_script or in_style:
            continue

        parts[i] = polish_text(part)

    return "".join(parts)


def main() -> None:
    tw_files = get_tw_files()
    changed = 0

    for path in tw_files:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        new = polish_html(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed += 1

    print(f"Done. tw_files={len(tw_files)}, changed={changed}")


if __name__ == "__main__":
    main()
