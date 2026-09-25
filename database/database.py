import sqlite3


SEED_QUESTIONS = [
    ("What are your business hours?", "We are open Monday to Saturday, from 9 AM to 6 PM."),
    ("When are you open?", "We are open Monday to Saturday, from 9 AM to 6 PM."),
    ("Where are you located?", "We are based in Chennai, Tamil Nadu."),
    ("How can I contact you?", "You can contact us by email at hello@example.com."),
    ("What services do you offer?", "We provide chatbot development, automation, and NLP solutions."),
    ("Do you work on Sundays?", "Our team is closed on Sundays, but you can still leave us a message."),
    ("How do I get started?", "Send us your requirements and we will help you choose the right next step."),
]


def get_db(database_path):
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database_path):
    connection = get_db(database_path)
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            score REAL NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    if connection.execute("SELECT COUNT(*) FROM knowledge_base").fetchone()[0] == 0:
        connection.executemany("INSERT INTO knowledge_base (question, answer) VALUES (?, ?)", SEED_QUESTIONS)
    connection.commit()
    connection.close()
