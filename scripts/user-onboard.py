#!/usr/bin/env python3

import argparse
import os

if __name__ == '__main__' and __package__ is None:
    import sys
    # __file__ should be defined in this case
    PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(PARENT_DIR)

import bcrypt
from dotenv import load_dotenv
from françoise.db import open_db

load_dotenv()

parser = argparse.ArgumentParser(
        description="Onboards a user with an agent and conversation.")

parser.add_argument("-n", "--name", type=str, required=True)
parser.add_argument("-email", "--email", type=str, required=True)
parser.add_argument("-pw", "--password", type=str, required=True)
parser.add_argument("-a", "--agent", type=int, required=True)
parser.add_argument("-model", "--model", type=str, default='gemma')
parser.add_argument("-prof", "--proficiency", type=str, required=True)
parser.add_argument("-db", "--database", type=str, default=os.environ.get('DATABASE_URL', 'data.db'))

args = parser.parse_args()

salt = bcrypt.gensalt()
password = args.password.encode('utf-8')
hashed_password = bcrypt.hashpw(password, salt)

with open_db(args.database) as db:
    user = db.create_user(
            name=args.name,
            email=args.email,
            salt=salt,
            password=hashed_password)

    print('create user with id `%d`' % (user[0],))

    conversation = db.create_conversation(
            user_id=user[0],
            agent_id=int(args.agent),
            model=args.model,
            proficiency=args.proficiency)

    print('created conversation with id `%d` for user `%d` and agent `%d`' % conversation[0:3])
