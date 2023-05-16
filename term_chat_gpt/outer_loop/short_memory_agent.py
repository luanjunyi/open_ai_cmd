import logging
import ast

from pydantic import BaseModel, Field, root_validator
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatMessage, get_buffer_string
from langchain.memory.buffer import ConversationBufferMemory

from term_chat_gpt.inner_loop.vanilla_chat_gpt_agent import ChatGPTAgent
from term_chat_gpt.utils.logger_config import setup_logger

LOGGING_LEVEL = logging.DEBUG
LOG = setup_logger(__name__, LOGGING_LEVEL)

CHECK_TOPIC_CHANGE_PROMPT = """
Given the chat history between an AI and a human, your job is to
determine whether the new message from the human is a change of topic.

{chat_history}

New question from human: 

===============

{new_message}

===============

Do you think the chat history is irrelevant for the new message?
Your answer will be used by the AI to decide whether to remove the chat history
from its memory. Answer with ONLY a number between 0.00 and 1.00. 0 means we
should definitely keep the log. 1 means we should definitely remove the log.
"""

PICK_CHAT_HISTORY_PROMPT = """
Given the chat log between an AI and a human, your job is to
pick up the items that makes complete context to a new question from the human.
The rest will be removed from the AI's memory.

{chat_history}

New question from the human: 

====================

{new_message}

====================

In the format of a Python list, give me the log items that are relevant to 
the new question.

Important: Response with the list ONLY. For example: [2, 9, 18]. If you belive
the user has changed the tpoc, response with [].
"""


def _chat_log_item_to_str(m: ChatMessage) -> str:
    return f"{m.type}: {m.content}"


class ShortMemoryAgent(BaseModel):
    llm_chain: LLMChain
    model_name: str = Field("gpt-4")
    memory: ConversationBufferMemory = Field(
        default_factory=ConversationBufferMemory)

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def prepare(cls, values):
        if "model_name" not in values:
            values["model_name"] = "gpt-4"

        if "llm_chain" not in values:
            llm = ChatOpenAI(temperature=0, model_name=values['model_name'])
            prompt = PromptTemplate(
                input_variables=["chat_history", "new_message"],
                template=CHECK_TOPIC_CHANGE_PROMPT
            )
            values["llm_chain"] = LLMChain(llm=llm, prompt=prompt,
                                           verbose=(LOGGING_LEVEL == logging.DEBUG))

        return values

    def is_change_topic(self, chat_history: str, new_message: str) -> float:
        chat_history = chat_history.strip()
        new_message = new_message.strip()

        if not chat_history or not new_message:
            return 0.0

        self.llm_chain.prompt = PromptTemplate(
            input_variables=["chat_history", "new_message"],
            template=CHECK_TOPIC_CHANGE_PROMPT
        )

        resp = self.llm_chain.run(chat_history=chat_history,
                                  new_message=new_message)
        try:
            changed_prob = float(resp)
            LOG.info("Topic change probability: %s" % changed_prob)
            return changed_prob
        except ValueError:
            LOG.error("Failed to parse response from topic change answer(%s). "
                      "Will return 0.0 to be conservative" % resp)
            return 0.0

    def retain_chat_history(self,
                            chat_history: list[ChatMessage],
                            new_message: str) -> list[int]:
        new_message = new_message.strip()
        if not chat_history or not new_message:
            return []

        log = []
        for i, msg in enumerate(chat_history):
            log.append(f"[{i}] {_chat_log_item_to_str(msg)}")

        self.llm_chain.prompt = PromptTemplate(
            input_variables=["chat_history", "new_message"],
            template=PICK_CHAT_HISTORY_PROMPT
        )
        resp = self.llm_chain.run(chat_history="\n".join(log),
                                  new_message=new_message)
        LOG.debug(f"Response from LLM about chat log retaining: {resp}")
        try:
            retained_ids = ast.literal_eval(resp)
            LOG.info(f"Relevant chat history: {retained_ids}")
            return retained_ids
        except ValueError:
            LOG.error("Failed to parse response from relevant chat history(%s). "
                      "Will return empty list to be conservative" % resp)
            return []

    def add_to_memory(self, question: str, answer: str) -> str:
        self.memory.chat_memory.add_user_message(question)
        self.memory.chat_memory.add_ai_message(answer)
        summary = "%s: %s\n%s: %s\n" % (
            self.memory.human_prefix, question,
            self.memory.ai_prefix, answer)
        return summary

    def generate_chat_history(self) -> str:
        return get_buffer_string(self.memory.chat_memory.messages).strip()

    def update_for_new_question(self, question: str) -> str:
        question = question.strip()
        mem: list[ChatMessage] = self.memory.chat_memory.messages
        if not mem or not question:
            return ""

        retained_ids = self.retain_chat_history(mem, question)
        if len(retained_ids) == 0:
            LOG.info("No chat history is relevant to the new question."
                     " Clearing memory.")
            self.memory.clear()
            return ""

        relevant_messages = [mem[i] for i in retained_ids if 0 <= i < len(mem)]
        if len(relevant_messages) != len(retained_ids):
            LOG.error(f"LLM suggested retaining messages out of range."
                      " retained_ids: {retained_ids}, messages size: {len(mem)}")
        return get_buffer_string(messages=relevant_messages).strip()
