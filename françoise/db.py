from contextlib import contextmanager
import sqlite3

class Database:
    def __init__(self, connection):
        self.connection = connection

    def create_schema(self):
        with self.connection:
            self.connection.execute("CREATE TABLE messages (role TEXT, content TEXT)")

    def add_message(self, role: str, content: str):
        with self.connection:
            self.connection.executemany("INSERT INTO messages VALUES(?, ?)", [
                (role, content)
            ])

    def add_user_message(self, content: str):
        self.add_message('user', content)

    def add_assistant_message(self, content: str):
        self.add_message('assistant', content)

    def get_messages(self):
        res = self.connection.execute("SELECT role, content FROM messages")
        return res.fetchall()

    def delete_messages(self):
        with self.connection:
            self.connection.execute("DELETE FROM messages")
            self.connection.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='messages'")

@contextmanager
def open_db(url: str):
    connection = sqlite3.connect(url)
    try:
        yield Database(connection)
    finally:
        connection.close()
