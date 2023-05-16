import sys
import os
import argparse
import readline

from langchain.vectorstores import FAISS
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain.text_splitter import TokenTextSplitter
from langchain.chat_models.openai import ChatOpenAI

from term_chat_gpt.inner_loop.vanilla_chat_gpt_agent import ChatGPTAgent
from term_chat_gpt.outer_loop.chat_master import ChatMaster
from term_chat_gpt.human_io import read_user_prompt, present_answer
from term_chat_gpt.utils.google_web_tool import GoogleWebLoader
from term_chat_gpt.utils.web_content_tool import WebContentTool
from term_chat_gpt.utils.logger_config import setup_logger


LOG = setup_logger(__name__, "INFO")

chat_gpt = ChatGPTAgent()


def qq():
    print(chat_gpt.answer(sys.argv[1]))


def fetch_web():
    url = sys.argv[1]
    w = WebContentTool()
    return w.run(url)


def google():
    cmd = argparse.ArgumentParser(
        description="Query Google and answer your questions.")

    cmd.add_argument('-k', '--keywords', type=str,
                     required=True, help='Keywords for google search')
    cmd.add_argument('-n', '--num_google', type=int, default=10,
                     required=False, help='Number of google results')
    cmd.add_argument('-q', '--question', type=str,
                     required=False, help='Your question, empty for reactive')
    cmd.add_argument('--retrieve-num', type=int, default=5,
                     help='Number of documents to retrieve from Vector Index')

    args = cmd.parse_args()

    num_google = args.num_google

    query = args.keywords
    LOG.info(f"Querying Google: {query}")
    google_loader = GoogleWebLoader(query=query, k=num_google, type="")

    llm = ChatOpenAI(model_name="gpt-4", temperature=1.0)

    qa = VectorstoreIndexCreator(
        vectorstore_cls=FAISS,
        text_splitter=TokenTextSplitter(
            encoding_name="cl100k_base",
            chunk_size=100,
            chunk_overlap=0
        ),
    ).from_loaders([google_loader,])

    if args.question:
        m = args.question
        if m == "same":
            m = query
        # ans = qa.query_with_sources(m, llm=llm)
        # text = ans['answer']
        # sources = ans['sources']
        # present_answer(f"GPT: {text}\n\n[Sources]\n\n{sources}")

        ans = qa.query(m, llm=llm, retriever_kwargs={"k": args.retrieve_num})
        present_answer(f"GPT: {ans}")
    else:
        while True:
            m = read_user_prompt(mode='long')

            if m == '/bye':
                break

            answer = qa.query(m, llm=llm, retriever_kwargs={
                              "k": args.retrieve_num})
            present_answer(f"GPT: {answer}\n")


def chat_full_loop():
    chat_master = ChatMaster(
        inner_loop_model_name="gpt-4",
        long_memory_retrieval_size=5,
        chat_db_full_path=os.getenv("TERM_CHAT_GPT_DB_PATH", "./chat.db"),
    )
    while True:
        m = read_user_prompt(mode='long')

        if m == '/bye':
            break

        answer = chat_master.chat_response(m)
        present_answer(f"\nChatGPT: {answer}\n")


if __name__ == "__main__":
    chat_full_loop()
