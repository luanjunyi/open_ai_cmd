import unittest

from term_chat_gpt.outer_loop.chat_master import ChatMaster


class TestChatMaster(unittest.TestCase):
    def setUp(self):
        self.chat_master = ChatMaster(
            inner_loop_model_name="gpt-3.5-turbo",
            long_memory_retrieval_size=3,
        )

    def test_short_memory_clear(self):
        before_session_id = self.chat_master.chat_log.session_id
        self.chat_master.log_chat_iteration("Who is Nassim Taleb?",
                                            "Nassim Taleb is a Lebanese-American essayist.")
        self.chat_master.log_chat_iteration("What is the best book by him?",
                                            "His best book is Black Swan.")

        ans = self.chat_master.chat_response(
            "Which is easier to learn, Java or Python?")
        after_session_id = self.chat_master.chat_log.session_id
        self.assertNotEqual(before_session_id, after_session_id)

    def test_short_memory_retain(self):
        self.chat_master.log_chat_iteration("Who is Nassim Taleb?",
                                            "Nassim Taleb is a Lebanese-American essayist.")
        self.chat_master.log_chat_iteration("What is the best book by him?",
                                            "His best book is Black Swan.")

        ans = self.chat_master.chat_response("When is he born?")
        self.assertIn("1960", ans)
