import configparser
import openai
import readline
import sys
import signal
import sqlite3
import datetime


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
    print("============[Enter your multiline content. Ctrl-D or Ctrl-Z ( windows ) to save it]==============\n")

    ret = sys.stdin.readlines()

    print("\n==========[Multiline input finished]==========\n")
    return '\n'.join(ret)

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

if __name__ == '__main__':
    history = []
    model = "gpt-4"
    db = sqlite3.connect('chat-log.db')
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
        print('\n' + resp + '\n')

    db.commit()
    db.close()

