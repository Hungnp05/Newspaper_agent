import sqlite3
from datetime import datetime

class NewsDB:
    def __init__(self, db_path="news.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS summaries
                               (id INTEGER PRIMARY KEY, date TEXT, topic TEXT, summary TEXT)''')
        self.conn.commit()

    def save_summary(self, topic, summary):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO summaries (date, topic, summary) VALUES (?, ?, ?)", (date, topic, summary))
        self.conn.commit()

    def get_latest_summary(self, topic):
        self.cursor.execute("SELECT summary FROM summaries WHERE topic=? ORDER BY date DESC LIMIT 1", (topic,))
        result = self.cursor.fetchone()
        return result[0] if result else None