import configparser
import openai
import readline
import sys
import signal


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
            return message
        except Exception as err:
            print("Failed to call OpenAI API. I will retry. The error is [%s]." % err )
            retry -= 1


def multiline_input():
    print("============[Enter your multiline content. Ctrl-D or Ctrl-Z ( windows ) to save it]==============\n")

    ret = sys.stdin.readlines()

    print("\n==========[Multiline input finished]==========\n")
    return '\n'.join(ret)

if __name__ == '__main__':
    history = []
    model = "gpt-4"
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

        if prompt.startswith('/sys '):
            prompt = prompt[len("/sys "):]
            role = 'system'

        if prompt == '/tldr':
            prompt = multiline_input()

        try:
            resp = chat_response(prompt, role, history, model)
            if resp is None:
                raise Exception("Response is empty...")
        except Exception as err:
            print(err)
            continue

        print('\n' + resp + '\n')

