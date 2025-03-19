import os
import re
from typing import Annotated, Optional

from fastapi import BackgroundTasks, FastAPI, Form, Response, status

from .chat import chat, get_prompt_message, message_tuple_to_dict
from .db import open_db
from .mail import send_mail

def get_config(config: dict[str, str], k: str, default: Optional[str] = None) -> str:
    # NOTE checks the configuration first, then the environment, then default
    return config.get(k, os.environ.get(k, default))

def App(**kwargs):

    app = FastAPI()


    DATABASE_URL = get_config(kwargs, 'DATABASE_URL', 'data.db')
    LLM_MODEL = get_config(kwargs, 'LLM_MODEL', 'llama3.2')
    LLM_PROMPT_PATH = get_config(kwargs, 'LLM_PROMPT_PATH', 'prompt.txt')
    LLM_API_CHAT_URL = get_config(kwargs, 'LLM_API_CHAT_URL', 'http://localhost:11434/api/chat')
    EMAIL_SENDER_WHITELIST = get_config(kwargs, 'EMAIL_SENDER_WHITELIST')
    MAILGUN_API_KEY = get_config(kwargs, 'MAILGUN_API_KEY')
    MAILGUN_API_SENDER = get_config(kwargs, 'MAILGUN_API_SENDER')
    MAILGUN_API_URL = get_config(kwargs, 'MAILGUN_API_URL')

    def chat_and_reply(headers: Optional[str], message: str, sender: Optional[str], subject: Optional[str]) -> None:
        # NOTE we load the prompt on each request so that it can be tweaked outside
        # the band of application deployment
        prompt = get_prompt_message(LLM_PROMPT_PATH)

        with open_db(DATABASE_URL) as db:
            db.add_user_message(message)
            messages = db.get_messages()
            message_objects = list(map(message_tuple_to_dict, [prompt] + messages))
            response = chat(message_objects, model=LLM_MODEL, url=LLM_API_CHAT_URL)
            db.add_assistant_message(response)

        data = {
            "from": MAILGUN_API_SENDER,
            "to": sender,
            "text": response
        }

        # NOTE what follows is integral to threaded replies
        match = re.search('"Message-Id","([^\"]*)"', headers)
        if match:
            data["h:In-Reply-To"] = match.group(1)

        # NOTE only add the subject if it exists
        if subject:
            data['subject'] = subject

        send_mail(MAILGUN_API_URL, api_key=MAILGUN_API_KEY, data=data)

    @app.post('/mailgun', status_code=200)
    async def mailgun(headers: Annotated[str, Form(alias='message-headers')], message: Annotated[str, Form(alias='body-plain')], sender: Annotated[str, Form()], subject: Annotated[str, Form()], background_tasks: BackgroundTasks, response: Response) -> None:
        # NOTE as a security measure, if there is a whitelist for sender email
        # addresses, and the sender of the mail is not in that list, we will error
        # out (to help limit the possibility of receiving bad/malacious input)
        if EMAIL_SENDER_WHITELIST and sender not in EMAIL_SENDER_WHITELIST:
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            return
        background_tasks.add_task(chat_and_reply, headers, message, sender, subject)

    return app
