import sqlite3


class DAO:
    def __init__(self):
        self.db = sqlite3.connect("GGGGobbler.sqlite")

    def open(self):
        self.db = sqlite3.connect("GGGGobbler.sqlite")

    def close(self):
        self.db.close()

    def create_tables(self):
        """
        db setup function
        """
        cur = self.db.cursor()
        try:
            cur.execute("""CREATE TABLE poethread (
                                    poethread_id TEXT PRIMARY KEY,
                                    poethread_page_count INTEGER)""")

            cur.execute("""CREATE TABLE redthread (
                                    redthread_id TEXT PRIMARY KEY,
                                    poethread_id TEXT,
                                    redthread_comment_id TEXT,
                                    redthread_comment_text TEXT,
                                    FOREIGN KEY(poethread_id) REFERENCES poethread(poethread_id))""")
        finally:
            self.db.commit()
            cur.close()

    def get_bot_comment_(self, thread_id):
        """
        checks whether the given reddit thread has been commented on by this bot
        """
        cur = self.db.cursor()
        try:
            cur.execute("")
            return True if cur.fetchone() is None else False
        finally:
            cur.close()

    def poe_thread_page_count(self, thread_id):
        """
        gets the recorded page counter of given thread
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT poethread_page_count FROM poethread WHERE poethread_id = ?",
                       thread_id)
            row = cur.fetchone()

            return None if row is None else row["poethread_page_count"]
        finally:
            cur.close()

    def poe_thread_exists(self, thread_id):
        """
        checks if the given thread is in the db
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT 1 FROM poethread WHERE poethread_id = ?", (thread_id,))
            return True if cur.fetchone() is None else False
        finally:
            cur.close()

    def add_poe_thread(self, thread_id, page_count):
        """
        adds a new pathofexile.com thread reacord
        """
        cur = self.db.cursor()
        try:
            cur.execute("INSERT INTO poethread (poethread_id, poethread_page_count), "
                             "VALUES (?, ?, ?)", (thread_id, page_count,))
        finally:
            self.db.commit()
            cur.close()

    def update_poe_thread(self, thread_id, page_count):
        """
        updates a threads noted page count
        """
        cur = self.db.cursor()
        try:
            cur.execute("UPDATE poethread SET poethread_page_count = ? "
                             "WHERE poethread_id = ?", (page_count, thread_id,))
        finally:
            self.db.commit()
            cur.close()
    def add_reddit_thread(self, reddit_thread_id, poe_thread_id, comment_id, comment_text):
        """
        adds a new reddit post record
        """
        cur = self.db.cursor()
        try:
            cur.execute("INSERT INTO redthread (redthread_id, poethread_id, "
                        "redthread_comment_id, redthread_comment_text), VALUES (?, ?, ?, ?)",
                        (reddit_thread_id, poe_thread_id, comment_id, comment_text))
        finally:
            self.db.commit()
            cur.close()

    def update_reddit_thread(self, thread_id, comment_text):
        """
        updates a reddit thread's comment with new text
        """
        cur = self.db.cursor()
        try:
            cur.execute("UPDATE redthread SET redthread_comment_text = ? "
                             "WHERE redthread_id = ?", (comment_text, thread_id))
        finally:
            self.db.commit()
            cur.close()