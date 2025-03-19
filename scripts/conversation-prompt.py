#!/usr/bin/env python3

import argparse
import os

if __name__ == '__main__' and __package__ is None:
    import sys
    # __file__ should be defined in this case
    PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(PARENT_DIR)

from dotenv import load_dotenv
from françoise.chat import get_prompt_message_from_conversation
from françoise.db import open_db

load_dotenv()

parser = argparse.ArgumentParser(
        description="Expands a conversation prompt.")

parser.add_argument("-id", "--id", type=int, required=True)
parser.add_argument("-db", "--database", type=str, default=os.environ.get('DATABASE_URL', 'data.db'))

args = parser.parse_args()

with open_db(args.database) as db:
    conversation = db.conversation_to_dict(db.get_conversation(args.id))

prompt = get_prompt_message_from_conversation(conversation)
print(prompt)
