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
        description="Adds an agent persona to the database.")

parser.add_argument("-n", "--name", type=str, required=True)
parser.add_argument("-lang", "--language", type=str, required=True)
parser.add_argument("-prof", "--proficiency", type=str, required=True)
parser.add_argument("-p", "--prompt", type=str, default='./prompt.md')
parser.add_argument("-tz", "--timezone", type=str, required=True)
parser.add_argument("-db", "--database", type=str, default=os.environ.get('DATABASE_URL', 'data.db'))

args = parser.parse_args()

with open(args.prompt, 'r', encoding='utf8') as file:
    prompt = file.read()
    with open_db(args.database) as db:
        agent = db.create_agent(name=args.name,
                                language=args.language,
                                proficiency=args.proficiency,
                                prompt=prompt,
                                timezone=args.timezone)
        id, *remaining = agent
        print('created agent with id `%d`' % (id,))
