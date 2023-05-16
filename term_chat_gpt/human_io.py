import readline

from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.html import HtmlLexer
from rich import print
from rich.markdown import Markdown


def multiline_input():

    key_bindings = KeyBindings()

    @key_bindings.add(Keys.ControlD)
    def _(event):
        # Event handler to exit from the multiline input when Ctrl+D is pressed
        event.current_buffer.validate_and_handle()

    @key_bindings.add(Keys.ControlC)
    def _(event):
        print("To quite, input '/bye'. I ignore SIGINT to avoid accidental CTRL-C or alike")

    text = prompt("> ",
                  multiline=True,
                  key_bindings=key_bindings,
                  lexer=PygmentsLexer(HtmlLexer))
    return text.strip()


def read_user_prompt(mode: str = 'short'):
    if mode == 'short':
        return input("> ").strip()
    assert mode == 'long'
    return multiline_input()


def present_answer(ans):
    print(Markdown(ans))
