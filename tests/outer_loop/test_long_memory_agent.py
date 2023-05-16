
import unittest
import os

from langchain.memory.chat_message_histories import SQLChatMessageHistory

from term_chat_gpt.outer_loop.long_memory_agent import LongMemoryAgent


class TestLongMemoryAgent(unittest.TestCase):
    def setUp(self):
        self.db_path = "/tmp/tmp_chat.db"
        self.chat_history = self._createNewChatDB()
        self.long_memory_agent = LongMemoryAgent(
            chat_db_full_path=self.db_path
        )

    def _createNewChatDB(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        self.chat_history = SQLChatMessageHistory(
            session_id="test_session_1",
            connection_string=f"sqlite:///{self.db_path}",
        )

        self.chat_history.add_user_message("When is WWII?")
        self.chat_history.add_ai_message("World War II started in 1939.")
        self.chat_history.add_user_message("When did it end?")
        self.chat_history.add_ai_message("World War II ended in 1945.")
        self.chat_history.add_user_message("How did WWII start?")
        self.chat_history.add_ai_message("World War II started on September 1, "
                                         "1939, when Nazi Germany, led by Adolf Hitler, invaded Poland. This event led to the United Kingdom and France declaring war on Germany on September 3, 1939. The conflict eventually escalated into a global war involving many countries from different parts of the world, including the Soviet Union, the United States, and Japan. The war lasted for six years, ending on September 2, 1945, when Japan officially surrendered to the Allies.")

        self.chat_history.session_id = "test_session_2"
        self.chat_history.add_user_message("Who invented the light bulb?")
        self.chat_history.add_ai_message(
            "Thomas Edison invented the light bulb in 1879.")
        self.chat_history.add_user_message(
            "What are great inventions from Tesla?")
        self.chat_history.add_ai_message(
            "Tesla invented the alternating current motor, the radio, the remote control, and the electric car.")

        return self.chat_history

    def test_load_chat_from_db(self):
        def _test(query, ins, outs):
            ans = self.long_memory_agent.get_context(
                query=query,
                k=1)
            self.assertEqual(len(ans), 1)
            text, score = ans[0]
            print(f"Query: {query}\ncontext: {text}\nscore:{score}")
            for t in ins:
                self.assertIn(t, text)
            for t in outs:
                self.assertNotIn(t, text)

        _test(query="Did China participated?",
              ins=["Nazi", "Germany"],
              outs=["Edison", "Tesla"])

        _test(query="Has Elon Musk been inspired by it?",
              ins=["Edison", "Tesla"],
              outs=["Nazi", "Germany"])
