from pathlib import Path

ROOT = Path(r"d:\howtobestusai1")
MARK_START = "<!-- LANG_TOGGLE_START -->"
MARK_END = "<!-- LANG_TOGGLE_END -->"

SNIPPET = r'''<!-- LANG_TOGGLE_START -->
<style>
#lang-toggle-select {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 9999;
  border: 1px solid #d0d7de;
  background: #ffffff;
  color: #24292f;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08);
}
#lang-toggle-select:hover {
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
    if (/_tw\.html$/i.test(pathname)) return pathname.replace(/_tw\.html$/i, '_en.html');
    return pathname.replace(/\.html$/i, '_en.html');
  }

  function toZh(pathname) {
    if (!/\.html$/i.test(pathname)) return pathname;
    return pathname.replace(/_en\.html$/i, '.html').replace(/_tw\.html$/i, '.html');
  }

  function toZhTw(pathname) {
    if (!/\.html$/i.test(pathname)) return pathname;
    if (/_tw\.html$/i.test(pathname)) return pathname;
    if (/_en\.html$/i.test(pathname)) return pathname.replace(/_en\.html$/i, '_tw.html');
    return pathname.replace(/\.html$/i, '_tw.html');
  }

  var rawPath = decodeURI(window.location.pathname || '');
  var isEn = /_en\.html$/i.test(rawPath);
  var isTw = /_tw\.html$/i.test(rawPath);
  var isZh = !isEn && !isTw;

  if (pref === 'en' && !isEn) {
    var enPath = toEn(rawPath);
    if (enPath !== rawPath) {
      window.location.replace(encodeURI(enPath) + window.location.search + window.location.hash);
      return;
    }
  }

  if (pref === 'zh' && !isZh) {
    var zhPath = toZh(rawPath);
    if (zhPath !== rawPath) {
      window.location.replace(encodeURI(zhPath) + window.location.search + window.location.hash);
      return;
    }
  }

  if (pref === 'zh-tw' && !isTw) {
    var twPath = toZhTw(rawPath);
    if (twPath !== rawPath) {
      window.location.replace(encodeURI(twPath) + window.location.search + window.location.hash);
      return;
    }
  }

  var select = document.createElement('select');
  select.id = 'lang-toggle-select';
  select.setAttribute('aria-label', 'Language');

  var opts = [
    { value: 'zh', label: '简体' },
    { value: 'zh-tw', label: '繁體' },
    { value: 'en', label: 'EN' }
  ];
  opts.forEach(function (item) {
    var option = document.createElement('option');
    option.value = item.value;
    option.textContent = item.label;
    select.appendChild(option);
  });

  select.value = isEn ? 'en' : (isTw ? 'zh-tw' : 'zh');

  select.addEventListener('change', function () {
    var currentPath = decodeURI(window.location.pathname || '');
    var targetLang = select.value;
    var targetPath = currentPath;
    if (targetLang === 'en') targetPath = toEn(currentPath);
    if (targetLang === 'zh') targetPath = toZh(currentPath);
    if (targetLang === 'zh-tw') targetPath = toZhTw(currentPath);
    localStorage.setItem(KEY, targetLang);
    window.location.href = encodeURI(targetPath) + window.location.search + window.location.hash;
  });

  document.addEventListener('DOMContentLoaded', function () {
    document.body.appendChild(select);
  });
})();
</script>
<!-- LANG_TOGGLE_END -->'''


def inject_once(html: str) -> tuple[str, bool]:
    if MARK_START in html and MARK_END in html:
        start = html.find(MARK_START)
        end = html.find(MARK_END, start)
        if end >= 0:
            end += len(MARK_END)
            return html[:start] + SNIPPET + html[end:], True
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
