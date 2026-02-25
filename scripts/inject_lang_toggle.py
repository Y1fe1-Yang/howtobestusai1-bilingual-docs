from pathlib import Path

ROOT = Path(r"d:\howtobestusai1")
MARK_START = "<!-- LANG_TOGGLE_START -->"
MARK_END = "<!-- LANG_TOGGLE_END -->"

SNIPPET = r'''<!-- LANG_TOGGLE_START -->
<style>
#lang-toggle-btn {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 9999;
  border: 1px solid #d0d7de;
  background: #ffffff;
  color: #24292f;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08);
}
#lang-toggle-btn:hover {
  background: #f6f8fa;
}
</style>
<script>
(function () {
  var KEY = 'site_lang_pref';
  var pref = localStorage.getItem(KEY);
  if (!pref) {
    pref = 'en';
    localStorage.setItem(KEY, pref);
  }

  function toEn(pathname) {
    if (!/\.html$/i.test(pathname)) return pathname;
    if (/_en\.html$/i.test(pathname)) return pathname;
    return pathname.replace(/\.html$/i, '_en.html');
  }

  function toZh(pathname) {
    if (!/\.html$/i.test(pathname)) return pathname;
    return pathname.replace(/_en\.html$/i, '.html');
  }

  var rawPath = decodeURI(window.location.pathname || '');
  var isEn = /_en\.html$/i.test(rawPath);

  if (pref === 'en' && !isEn) {
    var enPath = toEn(rawPath);
    if (enPath !== rawPath) {
      window.location.replace(encodeURI(enPath) + window.location.search + window.location.hash);
      return;
    }
  }

  if (pref === 'zh' && isEn) {
    var zhPath = toZh(rawPath);
    if (zhPath !== rawPath) {
      window.location.replace(encodeURI(zhPath) + window.location.search + window.location.hash);
      return;
    }
  }

  var btn = document.createElement('button');
  btn.id = 'lang-toggle-btn';
  btn.type = 'button';
  btn.textContent = isEn ? '中文' : 'EN';
  btn.title = isEn ? '切换到中文' : 'Switch to English';

  btn.addEventListener('click', function () {
    var currentPath = decodeURI(window.location.pathname || '');
    var currentIsEn = /_en\.html$/i.test(currentPath);
    var targetPath = currentIsEn ? toZh(currentPath) : toEn(currentPath);
    var targetLang = currentIsEn ? 'zh' : 'en';
    localStorage.setItem(KEY, targetLang);
    window.location.href = encodeURI(targetPath) + window.location.search + window.location.hash;
  });

  document.addEventListener('DOMContentLoaded', function () {
    document.body.appendChild(btn);
  });
})();
</script>
<!-- LANG_TOGGLE_END -->'''


def inject_once(html: str) -> tuple[str, bool]:
    if MARK_START in html and MARK_END in html:
        return html, False

    lower_html = html.lower()
    idx = lower_html.rfind("</body>")
    if idx >= 0:
        return html[:idx] + SNIPPET + html[idx:], True
    return html + "\n" + SNIPPET + "\n", True


def main() -> None:
    html_files = sorted(p for p in ROOT.rglob("*.html") if "\\scripts\\" not in str(p).lower())

    changed = 0
    for fp in html_files:
        original = fp.read_text(encoding="utf-8", errors="ignore")
        updated, did = inject_once(original)
        if did:
            fp.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"[UPDATED] {fp}")

    print(f"Done. files={len(html_files)}, changed={changed}")


if __name__ == "__main__":
    main()
