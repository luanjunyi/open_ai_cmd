# Using ChatGPT in terminal

## Install

* Replace `your_open_ai_key_here` with your actual API key in the `config.ini.sampe` file.
  * Don't include quotes around the key, just replace with your key's literal.
  * You can register an API key from OpenAI [here](https://platform.openai.com/signup).
* Rename `config.ini.sample` to `config.ini`
* Install the required dependencies using `pip install -r requirements.txt`.
* Run `python chat.py` and start using it.

### Userful commands

* `/r` to get rid of all chat history. Otherwise they will be sent back to OpenAI for context.
* `/tldr` to input multiline contents.
* `/m gpt4` to use GPT-4 model if you are part of the Beta users. `/m gpt3` to use GPT-3 model which is faster, cheaper, but less smart.
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
