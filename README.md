# Using ChatGPT in terminal

## Install

* Replace `your_open_ai_key_here` with your actual API key in the `config.ini.sampe` file.
  * Don't include quotes around the key, just replace with your key's literal.
  * You can register an API key from OpenAI [here](https://platform.openai.com/signup).
* Rename `config.ini.sample` to `config.ini`
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
* `/tldr` to input multiline contents.
* `/m gpt4` to use GPT-4 model if you are part of the Beta users. `/m gpt3` to use GPT-3 model which is faster, cheaper, but less smart.
* `/push` to push the current chatting thread into "the" chat thread stack.
* `/pop` to pop last pushed chat thread.
* `/stack` to see the threads in the stack.
* `/bye` to quit the chat. Notice CTRL-C is ignored to avoid accidental quit.

# Using the speaker

The speaker is still in a very early stage. Treat it as a toy.

## Install

* Replace `your_open_ai_key_here` with your actual API key in the `config.ini.sampe` file.
  * Don't include quotes around the key, just replace with your key's literal.
  * You can register an API key from OpenAI [here](https://platform.openai.com/signup).
* Rename `config.ini.sample` to `config.ini`
* Install the required dependencies using `pip install -r requirements.txt`.
* Run `python speaker.py` and start using it.

## Usage
* Activate by saying "Show me the money.". It's similar to "OK, Google" or "Hey, Siri."
* De-activate it by saying "Dismissed"
