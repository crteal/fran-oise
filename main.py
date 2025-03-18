import os
import re

from dotenv import load_dotenv
from flask import Flask, make_response, request

from françoise.chat import chat, get_prompt_message, message_tuple_to_dict
from françoise.db import open_db
from françoise.mail import send_mail

load_dotenv()

URL = os.environ.get('URL', '0.0.0.0')
PORT = os.environ.get('PORT', 8080)
DATABASE_URL = os.environ.get('DATABASE_URL', 'data.db')
LLM_MODEL = os.environ.get('LLM_MODEL', 'llama3.2')
LLM_PROMPT_PATH = os.environ.get('LLM_PROMPT_PATH', 'prompt.txt')
LLM_API_CHAT_URL = os.environ.get('LLM_API_CHAT_URL', 'http://localhost:11434/api/chat')
EMAIL_SENDER_WHITELIST = os.environ.get('EMAIL_SENDER_WHITELIST')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_API_SENDER = os.environ.get('MAILGUN_API_SENDER')
MAILGUN_API_URL = os.environ.get('MAILGUN_API_URL')

app = Flask(__name__)

@app.route('/mailgun', methods=['POST'])
def mailgun():
    sender = request.form.get('sender')

    # NOTE as a security measure, if there is a whitelist for sender email
    # addresses, and the sender of the mail is not in that list, we will error
    # out (to help limit the possibility of receiving bad/malacious input)
    if EMAIL_SENDER_WHITELIST and sender not in EMAIL_SENDER_WHITELIST:
        return make_response('Not Applicable', 406)

    # NOTE we load the prompt on each request so that it can be tweaked outside
    # the band of application deployment
    prompt = get_prompt_message(LLM_PROMPT_PATH)

    message = request.form.get('body-plain')

    # TODO this should be a background task, pursue FastAPI
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
    match = re.search('"Message-Id","([^\"]*)"', request.form.get('message-headers'))
    if match:
        data["h:In-Reply-To"] = match.group(1)

    subject = request.form.get('subject')
    # NOTE only add the subject if it exists
    if subject:
        data['subject'] = subject

    send_mail(MAILGUN_API_URL, api_key=MAILGUN_API_KEY, data=data)

    return make_response('OK', 200);

if __name__ == '__main__':
    app.run(host=URL, port=PORT, debug=True)
