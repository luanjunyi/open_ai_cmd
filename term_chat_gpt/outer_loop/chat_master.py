import time
import secrets
import hashlib

from pydantic import BaseModel, Field, root_validator
import faiss
from langchain.docstore import InMemoryDocstore
from langchain.vectorstores import FAISS, VectorStore
from langchain.memory import VectorStoreRetrieverMemory
from langchain.memory.chat_message_histories import SQLChatMessageHistory
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate

from term_chat_gpt.inner_loop.vanilla_chat_gpt_agent import ChatGPTAgent
from term_chat_gpt.outer_loop.short_memory_agent import ShortMemoryAgent
from term_chat_gpt.utils.logger_config import setup_logger

LOGGING_LEVEL = "DEBUG"
LOG = setup_logger(__name__, LOGGING_LEVEL)


def generate_session_id():
    current_time = time.time()
    random_string = secrets.token_hex(8)
    session_id = hashlib.sha256(
        f"{current_time}{random_string}".encode('utf-8')).hexdigest()
    return session_id[:16]


class ChatMaster(BaseModel):
    inner_loop_model_name: str = Field("gpt-4")
    chat_gpt: ChatGPTAgent
    chat_log: SQLChatMessageHistory
    long_memory: VectorStore
    long_memory_retrieval_size: int = 10
    short_memory_agent: ShortMemoryAgent
    change_topic_probability_threshold: float = 0.75
    chat_db_full_path: str = Field(default="/tmp/chat.db")

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def _prepare(cls, values):
        if "chat_gpt" not in values:
            values["chat_gpt"] = ChatGPTAgent(
                model_name=values["inner_loop_model_name"]
            )

        if "chat_db_full_path" not in values:
            values["chat_db_full_path"] = "/tmp/chat.db"

        if "chat_log" not in values:
            values["chat_log"] = SQLChatMessageHistory(
                connection_string=f"sqlite:///{values['chat_db_full_path']}",
                session_id=generate_session_id(),
            )

        if 'long_memory' not in values:
            embedding_size = 1536  # Dimensions of the OpenAIEmbeddings
            index = faiss.IndexFlatL2(embedding_size)
            embedding_fn = OpenAIEmbeddings().embed_query
            vectorstore = FAISS(embedding_fn, index, InMemoryDocstore({}), {})
            values['long_memory'] = vectorstore

        if 'short_memory_agent' not in values:
            values["short_memory_agent"] = ShortMemoryAgent(modle_name="gpt-4")

        return values

    def _renew_session(self):
        self.chat_log.session_id = generate_session_id()

    def log_chat_iteration(self, question: str, answer: str):
        summary = self.short_memory_agent.add_to_memory(question, answer)
        self.long_memory.add_texts([summary,])
        self.chat_log.add_user_message(question)
        self.chat_log.add_ai_message(answer)

    def chat_response(self, question: str) -> str:
        chat_history = self.short_memory_agent.update_for_new_question(
            question)
        if chat_history == "":
            self._renew_session()

        ans = self.chat_gpt.answer(
            question=question, chat_history=chat_history, context="N/A")

        self.log_chat_iteration(question, ans)

        return ans
