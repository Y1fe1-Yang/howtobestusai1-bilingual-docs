from pathlib import Path
import sys
import os
import socket
sys.path.insert(0, r"d:\howtobestusai1\scripts")
from deep_translator import GoogleTranslator
from translate_html_to_en import translate_html_file

paths = [
    Path(r"d:\howtobestusai1\HappyCapy\Skills 指南 3096ea0499868071be29cad4ee14f954.html"),
    Path(r"d:\howtobestusai1\HappyCapy\与其他平台的集成 3096ea04998680d3b4d2f992b732da62.html"),
]

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
socket.setdefaulttimeout(20)

translator = GoogleTranslator(source="zh-CN", target="en")
cache = {}
log_lines = []
for p in paths:
    try:
        count, out = translate_html_file(p, translator, cache)
        line = f"OK\t{out}\ttranslated_nodes={count}\texists={out.exists()}"
        print(line)
        log_lines.append(line)
    except Exception as exc:
        line = f"ERR\t{p}\t{type(exc).__name__}: {exc}"
        print(line)
        log_lines.append(line)

Path(r"d:\howtobestusai1\scripts\_run_translate_selected.log").write_text("\n".join(log_lines), encoding="utf-8")
