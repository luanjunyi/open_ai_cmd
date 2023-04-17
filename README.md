# Using ChatGPT in terminal

## Install

* Put your OpenAI API key in the environment variable `OPENAI_API_KEY`.
  * You can register an API key from OpenAI [here](https://platform.openai.com/signup).
* Rename `chat-log.db.sample` to `chat-log.db`
* Install the required dependencies using `pip install -r requirements.txt`.
* Run `python chat.py` and start using it.

### Features
* Display markdown with color
* Store chat history in chat-log.db -- a Sqlite3 database -- for backup
* Manipulate multiple chatting thread in a stack
* Multipline input

### Userful commands

* `/r` to get rid of all chat history. Otherwise they will be sent back to OpenAI for context.
* `/long` to enter multiline input mode. Type `/short` to switch back to single line input mode.
* `/m gpt4` to use GPT-4 model if you are part of the Beta users. `/m gpt3` to use GPT-3 model which is faster, cheaper, but less smart.
* `/hist` to show chat histories in current thread.
* `/push` to push the current chatting thread into "the" chat thread stack.
* `/pop` to pop last pushed chat thread.
* `/stack` to see the threads in the stack.
* `/info` to show current chat status (model, chat log size, etc).
* `/bye` to quit the chat. Notice CTRL-C is ignored to avoid accidental quit.

