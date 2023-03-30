import configparser
import openai
import readline
import sys
import signal
import sqlite3
import datetime
from rich import print
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

conf = configparser.ConfigParser()
conf.read("config.ini")

OPENAI_API_KEY = conf.get("open_ai", "api_key")

def ignore_sig(sig, frame):
    print("To quite, input '/bye'. I ignore SIGINT to avoid accidental CTRL-C or alike")

signal.signal(signal.SIGINT, ignore_sig)


openai.api_key = OPENAI_API_KEY

model_dict = {
    "gpt3": "gpt-3.5-turbo",
    "gpt4": "gpt-4",
}


def chat_response(prompt, role='user', history=[], model="gpt-4"):
    history.append({"role": role, "content": prompt})
    retry = 5
    while retry > 0:
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=history      
            )

            message = resp.choices[0].message['content'].strip()
            history.append({"role": "assistant", "content": message})
            usage = resp.usage
            return message, usage.prompt_tokens, usage.completion_tokens
        except Exception as err:
            print("Failed to call OpenAI API. I will retry. The error is [%s]." % err )
            retry -= 1

    return None, None, None


def multiline_input():
    def multiline_input_exit(event):
        # Event handler to exit from the multiline input when Ctrl+D is pressed
        event.current_buffer.validate_and_handle()

    key_bindings = KeyBindings()
    key_bindings.add(Keys.ControlD)(multiline_input_exit)

    session = PromptSession("==============[Enter your multi-line input (Press Ctrl+D to finish input)]==============\n\n", key_bindings=key_bindings)
    text = session.prompt(multiline = True)
    print("\n==============[Multiline input finished]==============\n")
    return text

def log_chat(db_conn, prompt, response, num_prompt_tocken, num_completion_token):
    cursor = db_conn.cursor()
    insert_query = (" INSERT INTO chat (datetime,"
                    "question,"
                    "answer, "
                    "num_prompt_token, "
                    "num_completion_token)"
                    "VALUES (?, ?, ?, ?, ?)")
    data = (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            prompt,
            response,
            num_prompt_tocken,
            num_completion_token)
    cursor.execute(insert_query, data)
    db_conn.commit()    

def print_markdown(text):
    md = Markdown(text)
    print(md)
    
if __name__ == '__main__':
    history = []
    model = "gpt-4"
    db = sqlite3.connect('chat-log.db')
    stack = []
    while True:
        prompt = input("> ")
        role = 'user'
        if prompt == '/bye':
            break

        if prompt in ['/reset', '/r']:
            print("\nConversation is reset, %d log deleted\n" % len(history))
            history = []
            continue

        if prompt.startswith('/m '):
            m = prompt[len('/m '):]
            if m in model_dict:
                model = model_dict[m]
            else:
                print("Unknown model (%s), possible models are: %s" % (m, model_dict.keys()))
            continue

        if prompt == "/push":
            print("%d log pushed for later" % len(history))
            stack.append(history)
            hisotry = []
            continue

        if prompt.startswith("/pop"):
            if len(stack) == 0:
                print("thread stack is empty, can't pop")
            else:
                if prompt == "/pop":
                    history = stack.pop()
                elif prompt.startswith("/pop "):
                    idx = prompt[len("/pop "):]
                    if idx.isdigit() and int(idx) < len(stack):
                        history = stack.pop(int(idx))
                    elif idx == "all":
                        stack = []
            continue

        if prompt == "/stack":
            for i, hist in enumerate(stack):
                print("%d\t%s" % (i, hist[0]["content"][:128]))
            continue
            

        if prompt == "/g3":
            model = model_dict["gpt3"]
            continue

        if prompt == "/g4":
            model = model_dict["gpt4"]
            continue
        

        if prompt.startswith('/sys '):
            prompt = prompt[len("/sys "):]
            role = 'system'

        if prompt == '/tldr':
            prompt = multiline_input()

        try:
            resp, num_prompt_tocken, num_completion_token = chat_response(prompt, role, history, model)
            if resp is None:
                raise Exception("Response is empty...")
        except Exception as err:
            print(err)
            continue

        log_chat(db, prompt, resp, num_prompt_tocken, num_completion_token)
        print_markdown('\n' + resp + '\n')

    db.commit()
    db.close()

