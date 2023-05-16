import unittest

from term_chat_gpt.utils.google_web_tool import GoogleWebLoader
from term_chat_gpt.utils.google_web_tool import GoogleWebSummary


class TestGoogleWebLoader(unittest.TestCase):
    def setUp(self):
        self.gw = GoogleWebLoader(query="NOT USED IN THIS TEST", k=2)

    def test_google(self):
        query = "Genshin Impact"
        res = self.gw.google(query)

        self.assertIn("organic", res)
        results = res["organic"]
        snippets = ' '.join(
            [(r["snippet"] if "snippet" in r else "") for r in results])
        self.assertIn("game", snippets)

    def test_load_for_query(self):
        query = "Black Swan Book"
        docs = self.gw.load_for_query(query)
        self.assertEqual(len(docs), 2)
        all_text = ' '.join([d.page_content for d in docs])
        self.assertIn("Nassim Taleb", all_text)
        self.assertNotIn("miHoYo", all_text)


class TestGoogleWebSummary(unittest.TestCase):
    def test_context_docs(self):
        gws = GoogleWebSummary(
            google_query="Covid-19 origniation",
            num_google_results=5
        )
        query = "Is Covid-19 a bioweapon?"
        docs = gws.context_docs(query, k=20)
        self.assertLessEqual(len(docs), 20)
        all_text = '\n\n===============\n\n'.join(
            [d.page_content for d in docs])
        self.assertIn("Wuhan", all_text)
        self.assertIn("COVID", all_text)

    def test_init(self):
        gws = GoogleWebSummary(
            google_query="OpenAI GPT-4",
            num_google_results=4
        )
        self.assertEqual(4, gws.num_google_results)
        for d in gws.docs:
            content = d.page_content
            self.assertLessEqual(len(content), 1024)

    # def test_context(self):
    #     # question = "What is the Black Swan Book?"
    #     # context = self.gws.context(question)
    #     # self.assertIn("Nassim Taleb", context)
    #     # self.assertNotIn("miHoYo", context)
    #     pass
