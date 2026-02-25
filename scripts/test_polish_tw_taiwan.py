import unittest

from polish_tw_taiwan import polish_html, polish_text


class TestPolishTwTaiwan(unittest.TestCase):
    def test_fix_common_taiwan_glyphs(self):
        text = "爲什麼在這裏看着內容"
        self.assertEqual(polish_text(text), "為什麼在這裡看著內容")

    def test_avoid_unnatural_neng_qing_bang_wo(self):
        text = "HappyCapy 能幫我做什麼？"
        self.assertEqual(polish_text(text), "HappyCapy 能幫我做什麼？")

    def test_keep_polite_request_when_sentence_starts_with_bang_wo(self):
        text = "幫我整理這份文件"
        self.assertEqual(polish_text(text), "請幫我整理這份檔案")

    def test_skip_script_and_style_blocks(self):
        html = """
<p>在這裏幫我生成文檔</p>
<script>var x = '在這裏幫我生成文檔';</script>
<style>.x:after{content:'在這裏幫我生成文檔';}</style>
"""
        out = polish_html(html)
        self.assertIn("在這裡幫我生成文件", out)
        self.assertIn("var x = '在這裏幫我生成文檔';", out)
        self.assertIn("content:'在這裏幫我生成文檔';", out)


if __name__ == "__main__":
    unittest.main()
