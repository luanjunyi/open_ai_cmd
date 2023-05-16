"""
Implemented by a LLMChain that wrap around ChatGPT's API, this
agent serve as the "inner loop" of the chatbot.
"""

import logging

from pydantic import BaseModel, Field, root_validator
from langchain.chat_models.openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from term_chat_gpt.utils.logger_config import setup_logger

LOGGING_LEVEL = logging.DEBUG
LOG = setup_logger(__name__, LOGGING_LEVEL)

MASTER_PROMPT = """
As a powerful AI, please answer a [NEW QUESTION] from a human beased on history [CHAT LOG] and [CONEXT]:

[CHAT LOG]: 

{chat_history}

[CONTEXT]:

{context}

[NEW QUESTION]:

{question}
"""


class ChatGPTAgent(BaseModel):
    model_name: str = Field("gpt-3.5-turbo")
    llm: ChatOpenAI
    prompt: PromptTemplate = Field(PromptTemplate.from_template(MASTER_PROMPT))
    chain: LLMChain = Field(default_factory=LLMChain)

    @root_validator(pre=True)
    def _prepare(cls, values):
        if "model_name" not in values:
            values["model_name"] = "gpt-3.5-turbo"
        if "llm" not in values:
            values["llm"] = ChatOpenAI(
                temperature=1.0,
                model_name=values["model_name"]
            )
        if "prompt" not in values:
            values["prompt"] = PromptTemplate.from_template(MASTER_PROMPT)
        if "chain" not in values:
            values["chain"] = LLMChain(
                llm=values["llm"],
                prompt=values["prompt"]
            )

        return values

    def answer(self,
               question: str,
               chat_history: str = "N/A",
               context: str = "N/A") -> str:
        if not chat_history:
            chat_history = "N/A"
        if not context:
            context = "N/A"
        current_prompt = self.prompt.format(
            question=question,
            chat_history=chat_history,
            context=context)
        LOG.debug(f"Inner loop prompt:\n{current_prompt}")
        ans = self.chain.run(
            question=question,
            chat_history=chat_history,
            context=context)
        return ans
