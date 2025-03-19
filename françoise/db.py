from contextlib import contextmanager
import sqlite3

class Database:
    def __init__(self, connection):
        self.connection = connection

    def create_schema(self):
        with self.connection:
            self.connection.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role INTEGER NOT NULL,
                    name TEXT,
                    email TEXT UNIQUE
                );

                CREATE TABLE agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    language TEXT NOT NULL,
                    proficiency TEXT NOT NULL,
                    prompt TEXT NOT NULL
                );

                CREATE TABLE conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT NOT NULL,
                    proficiency TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    agent_id INTEGER NOT NULL,
                    UNIQUE(model, user_id, agent_id),
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(agent_id) REFERENCES agents(id)
                );

                CREATE TABLE messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                );
            """)

    def get_conversation(self, id: int):
        res = self.connection.execute("""
            SELECT
                id,
                model,
                proficiency,
                user_id,
                user.email AS user_email,
                user.name AS user_name,
                agent_id,
                agent.name AS agent_name,
                agent.language AS agent_language,
                agent.proficiency AS agent_proficiency,
                agent.prompt AS agent_prompt
            FROM conversations conversation
            JOIN users user
            ON conversation.user_id = user.id
            JOIN agents agent
            ON conversation.agent_id = agent.id
            WHERE id = ?
        """, (id,))
        return res.fetchone()

    def conversation_to_dict(self, conversation: tuple) -> dict[str, str]:
        return dict(zip(('id', 'model', 'proficiency', 'user_id', 'user_email', 'user_name', 'agent_id', 'agent_name', 'agent_language', 'agent_proficiency', 'agent_prompt'), conversation))

    def add_message(self, conversation_id: int, role: str, content: str):
        with self.connection:
            self.connection.executemany("INSERT INTO messages VALUES(?, ?, ?)", [
                (conversation_id, role, content)
            ])

    def add_user_message(self, conversation_id: int, content: str):
        self.add_message(conversation_id, 'user', content)

    def add_assistant_message(self, conversation_id: int, content: str):
        self.add_message(conversation_id, 'assistant', content)

    def get_messages(self):
        res = self.connection.execute("SELECT role, content FROM messages")
        return res.fetchall()

    def get_messages_by_conversation(self, conversation_id: int):
        res = self.connection.execute("SELECT role, content FROM messages WHERE conversation_id = ?", (conversation_id,))
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
