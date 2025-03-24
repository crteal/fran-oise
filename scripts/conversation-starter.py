#!/usr/bin/env python3

import argparse
import os

if __name__ == '__main__' and __package__ is None:
    import sys
    # __file__ should be defined in this case
    PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(PARENT_DIR)

from dotenv import load_dotenv
from françoise.chat import chat, get_prompt_message_from_conversation,  message_tuple_to_dict
from françoise.db import open_db
from françoise.mail import send_mail

load_dotenv()

parser = argparse.ArgumentParser(
        description="Starts a new, or bumps a dormant, conversation.")

parser.add_argument("-id", "--id", type=int, required=True)
parser.add_argument("-t", "--type", type=str, default='welcome')
parser.add_argument("-db", "--database", type=str, default=os.environ.get('DATABASE_URL', 'data.db'))

LLM_API_CHAT_URL = os.environ.get('LLM_API_CHAT_URL', 'http://localhost:11434/api/chat')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_API_SENDER = os.environ.get('MAILGUN_API_SENDER')
MAILGUN_API_URL = os.environ.get('MAILGUN_API_URL')

args = parser.parse_args()

with open_db(args.database) as db:
    conversation = db.conversation_to_dict(db.get_conversation(args.id))

    data = {
        "from": "%s.%d <%s>" % (conversation.get('agent_name'), args.id, MAILGUN_API_SENDER),
        "to": conversation.get('user_email')
    }

    if args.type == 'welcome':
        prompt = get_prompt_message_from_conversation(conversation)

        response = chat([message_tuple_to_dict(prompt)],
                        model=conversation.get('model'),
                        url=LLM_API_CHAT_URL)
        db.add_assistant_message(args.id, response)

        data['subject'] = '{user_name}, meet {agent_name} ({agent_language} {agent_proficiency})'.format(**conversation)
        data['text'] = response

send_mail(MAILGUN_API_URL, api_key=MAILGUN_API_KEY, data=data)
