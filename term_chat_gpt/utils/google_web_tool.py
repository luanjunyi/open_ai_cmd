from pydantic import BaseModel, Field
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.vectorstores.base import VectorStore, VectorStoreRetriever, BaseRetriever
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import TokenTextSplitter


from term_chat_gpt.utils.web_content_tool import WebContentTool
from term_chat_gpt.utils.logger_config import setup_logger

LOGGING_LEVEL = "DEBUG"
LOG = setup_logger(__name__, LOGGING_LEVEL)


class GoogleWebLoader(BaseLoader):
    def __init__(self, query, **serper_api_kwargs):
        self.query = query
        self.google_serper = GoogleSerperAPIWrapper(**serper_api_kwargs)
        self.browser = WebContentTool()

    def google(self, query) -> dict:
        return self.google_serper.results(query)

    def load_for_query(self, query) -> list[Document]:
        google_results = self.google(query)
        docs: list[Document] = []

        for r in google_results["organic"]:
            url = r["link"]
            content = self.browser.run(url)
            docs.append(Document(page_content=content,
                        metadata={"source": url}))

        return docs

    def load(self) -> list[Document]:
        return self.load_for_query(self.query)


class GoogleWebSummary(BaseModel):
    google_query: str
    num_google_results: int = Field(10)
    vector_store_retriever: VectorStoreRetriever
    docs: list[Document]

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def __init__(self, google_query, num_google_results):
        goog = GoogleWebLoader(query=google_query, k=num_google_results)
        google_results = goog.load()
        text_splitter = TokenTextSplitter(
            encoding_name="cl100k_base",
            chunk_size=100,
            chunk_overlap=0
        )
        docs = text_splitter.split_documents(google_results)
        for doc in docs:
            LOG.debug(f"doc length: {len(doc.page_content)}")
        embeddings = OpenAIEmbeddings()
        vector_store_retriever = FAISS.from_documents(
            docs, embeddings).as_retriever()
        super().__init__(
            google_query=google_query,
            num_google_results=num_google_results,
            vector_store_retriever=vector_store_retriever,
            docs=docs,
        )

    def get_retriever(self) -> BaseRetriever:
        return self.vector_store_retriever

    def context_docs(self, query, k=5) -> list[Document]:
        self.vector_store_retriever.search_kwargs = {"k": k}
        return self.vector_store_retriever.get_relevant_documents(
            query)

    def context(self, question) -> str:
        return ""
