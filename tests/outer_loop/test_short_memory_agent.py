import unittest

from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory

from term_chat_gpt.outer_loop.short_memory_agent import ShortMemoryAgent


class TestShortMemoryAgent(unittest.TestCase):
    def setUp(self):
        self.short_memory_agent = ShortMemoryAgent(
            model_name="gpt-4",
        )

    def test_change_topic_positive(self):
        ans = self.short_memory_agent.is_change_topic(
            chat_history="""
              User: Who is Nassim Taleb?
              AI: Nassim Nicholas Taleb is a Lebanese-American essayist,
                scholar, mathematical statistician, and former option trader and risk analyst, whose work concerns problems of randomness, probability, and uncertainty.
              User: What is the best book by him?
              AI: Black Swan is the best book by Nassim Taleb.
              User: How old is he?
              AI: 52 years old.
            """,
            new_message="Let's talk about something else.",
        )
        self.assertGreater(ans, 0.8)

    def test_change_topic_negative(self):
        ans = self.short_memory_agent.is_change_topic(
            chat_history="""
              User: Who is Nassim Taleb?
              AI: Nassim Nicholas Taleb is a Lebanese-American essayist,
                scholar, mathematical statistician, and former option trader and risk analyst, whose work concerns problems of randomness, probability, and uncertainty.
              User: What is the best book by him?
              AI: Black Swan is the best book by Nassim Taleb.
              User: How old is he?
              AI: 52 years old.
            """,
            new_message="Is he married?",
        )
        self.assertLess(ans, 0.2)

    def test_retain_chat_history(self):
        hist = ChatMessageHistory()
        hist.add_user_message("Who is Nassim Taleb?")
        hist.add_ai_message(
            "Nassim Nicholas Taleb is a Lebanese-American essayist.")
        hist.add_user_message("What is the best book by him?")
        hist.add_ai_message("Black Swan is the best book by Nassim Taleb.")
        hist.add_user_message("What's the most popular programming language?")
        hist.add_ai_message("Python is the most popular programming language.")

        ans = self.short_memory_agent.retain_chat_history(hist.messages,
                                                          "When did he come to the US?")
        self.assertIn(1, ans)

        ans = self.short_memory_agent.retain_chat_history(hist.messages,
                                                          "Is it easy to learn?")
        self.assertIn(5, ans)

    def test_add_to_memory(self):
        m = self.short_memory_agent.add_to_memory(
            "How to say Hello in Spanish?", "Hola")
        self.assertIn("How to say Hello in Spanish?", m)
        m = self.short_memory_agent.add_to_memory(
            "What about Goodbye?", "Adios")
        self.assertIn("What about Goodbye?", m)
        hist = self.short_memory_agent.generate_chat_history()
        self.assertIn("Spanish", hist)
        self.assertIn("Hola", hist)
        self.assertIn("Adios", hist)
        self.assertIn("Goodbye", hist)

    def test_update_for_new_question_with_empty_memory(self):
        m = self.short_memory_agent.update_for_new_question(question="Howdy?")
        self.assertEqual("", m)

    def test_update_for_new_question_cherry_pick_none(self):
        self.short_memory_agent.add_to_memory("Pronounce like hoody but for greeting.",
                                              answer="Howdy")

        self.short_memory_agent.add_to_memory("A word like multiplex but it’s about"
                                              " seprate the execution flow based on some criteria?",
                                              answer="demultiplex")

        m = self.short_memory_agent.update_for_new_question(
            question="Who invented Linux?")
        self.assertEqual("", m)

    def test_update_for_new_question_cherry_pick_some(self):
        self.short_memory_agent.add_to_memory("What's the most popular game on iOS in 2020?",
                                              "Genshin Impact")

        self.short_memory_agent.add_to_memory("What's the game type?",
                                              "Open world RPG")

        self.short_memory_agent.add_to_memory("What about on Switch?",
                                              "Animal Crossing")

        m = self.short_memory_agent.update_for_new_question(
            question="Which one has more users?")
        print(m)
        self.assertIn("Genshin", m)
        self.assertIn("Crossing", m)
        self.assertNotIn("RPG", m)
