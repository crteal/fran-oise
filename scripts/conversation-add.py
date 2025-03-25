#!/usr/bin/env python3

import argparse
import os

if __name__ == '__main__' and __package__ is None:
    import sys
    # __file__ should be defined in this case
    PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(PARENT_DIR)

from dotenv import load_dotenv
from françoise.db import open_db

load_dotenv()

parser = argparse.ArgumentParser(
        description="Adds a conversation to the database.")

parser.add_argument("-u", "--user", type=int, required=True)
parser.add_argument("-a", "--agent", type=int, required=True)
parser.add_argument("-p", "--proficiency", type=str, required=True)
parser.add_argument("-m", "--model", type=str, default='gemma3')
parser.add_argument("-db", "--database", type=str, default=os.environ.get('DATABASE_URL', 'data.db'))

args = parser.parse_args()

with open_db(args.database) as db:
    conversation = db.create_conversation(user_id=args.user,
                                          agent_id=args.agent,
                                          proficiency=args.proficiency,
                                          model=args.model)
    id, *remaining = conversation
    print('created conversation with id `%d`' % (id,))
