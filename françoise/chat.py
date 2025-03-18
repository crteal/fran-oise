from collections.abc import Sequence
import requests

def message_tuple_to_dict(values: tuple[str, str]):
    return dict(zip(('role', 'content'), values))

def get_prompt(filepath: str):
    with open(filepath, 'r', encoding='utf8') as file:
        return file.read()

def get_prompt_message(filepath: str):
    return ('system', get_prompt(filepath))

def chat(messages: Sequence[dict[str, str]], **kwargs):
    if not messages:
        raise Exception('messages is empty or unspecified')

    model = kwargs.get('model')
    if not model:
        raise Exception('model is unspecified')

    url = kwargs.get('url')
    if not url:
        raise Exception('url is unspecified')

    data = {
      "model": model,
      "messages": messages,
      "stream": False
    }

    response = requests.post(url, json=data)
    # throw an error if we got a failure from the LLM
    response.raise_for_status()

    json = response.json()
    return json['message']['content']
