import unittest

from term_chat_gpt.inner_loop.vanilla_chat_gpt_agent import ChatGPTAgent


class TestVanillaChatGPTAgent(unittest.TestCase):
    def setUp(self):
        self.chat_gpt = ChatGPTAgent(model_name="gpt-3.5-turbo")

    def test_short_memory(self):
        answer = self.chat_gpt.answer(
            question="That's how many seconds?",
            chat_history="""
              Human: Who are you?
              AI: I am an AI created by OpenAI. How can I help you today?
              Human: How many days are in a week?
              AI: There are 7 days in a week.
            """)
        self.assertRegex(answer, r".*604,800.*")

    def test_context(self):
        answer = self.chat_gpt.answer(
            question="What year is it now?",
            context="The year is 2051 and the world is in a state of perpetual war."
        )
        self.assertRegex(answer, r".*2051.*")
