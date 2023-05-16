import logging
import json

from pydantic import BaseModel, Field, root_validator
import faiss
import sqlite3
from langchain.vectorstores import FAISS, VectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore import InMemoryDocstore

from term_chat_gpt.utils.logger_config import setup_logger

LOGGING_LEVEL = "DEBUG"
LOG = setup_logger(__name__, LOGGING_LEVEL)


class LongMemoryAgent(BaseModel):
    chat_db_full_path: str
    vector_store: VectorStore

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def __init__(self, chat_db_full_path):
        chat_db_full_path = chat_db_full_path
        embedding_size = 1536  # Dimensions of the OpenAIEmbeddings
        index = faiss.IndexFlatL2(embedding_size)
        embedding_fn = OpenAIEmbeddings().embed_query
        vector_store = FAISS(embedding_fn, index, InMemoryDocstore({}), {})

        super().__init__(
            chat_db_full_path=chat_db_full_path,
            vector_store=vector_store,
        )

        self._load_chat_from_db(chat_db_full_path)

    def _load_chat_from_db(self, path):
        LOG.info(f"Loading chat from {path}")
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute("SELECT DISTINCT(session_id) FROM message_store")
        rows = c.fetchall()
        session_ids = [r[0] for r in rows]

        LOG.info(f"Found {len(session_ids)} sessions")

        for session_id in session_ids:
            c.execute(
                f"SELECT message FROM message_store WHERE session_id='{session_id}'")
            rows = c.fetchall()
            LOG.info("Found %d message for session(%s)" %
                     (len(rows), session_id))
            content_lst = []
            for row in rows:
                r = json.loads(row[0])
                content = f"{r['type']}: {r['data']['content']}"
                content_lst.append(content)
            summary = "\n".join(content_lst)
            self.vector_store.add_texts([summary,])

        conn.close()

    def get_context(self, query, k=4) -> list[tuple[str, float]]:
        contexts = self.vector_store.similarity_search_with_score(query, k)
        return [(c[0].page_content, c[1]) for c in contexts]
