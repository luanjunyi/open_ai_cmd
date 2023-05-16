import unittest

from term_chat_gpt.utils.web_content_tool import WebContentTool


class TestWebContentTool(unittest.TestCase):
    def setUp(self):
        self.tool = WebContentTool()

    def test_run(self):
        url = "https://en.wikipedia.org/wiki/World_War_II"
        text = self.tool.run(url)

        terms = ["World War II", "Soviet Union", "United States", "Japan"]
        for t in terms:
            self.assertIn(t, text)
