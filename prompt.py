# The prompt to response to one user input. Interate with tools.
# Use all langchain tools but fetch context and chat history on demant.
INNER_LOOP_PROMPT = """
Answer the question with tools:

<tools>

Important: response in the following JSON format and ENSURE it can be parsed by Python json.loads:

{
  "thoughts": {
    "text": "thought",
    "reasoning": "reasoning",
    "plan": "- short bulleted\n- list that conveys\n- long-term plan",
    "criticism": "constructive self-criticism",
    "speak": "thoughts summary to say to user"
  },
  "command": {
    "name": "command name",
    "args": {
      "arg name": "value"
    }
  }
}

"""
