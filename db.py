import sqlite3


class DAO:
    def __init__(self):
        self.db = sqlite3.connect("GGGGobbler.sqlite")

    def open(self):
        self.db = sqlite3.connect("GGGGobbler.sqlite")

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.commit()
        self.db.close()

    def rollback(self):
        self.db.rollback()

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
            cur.close()

    def get_old_staff_posts_by_thread_id(self, poe_thread_id):
        """
        returns a list of strings containing the markdown-ed posts stored in old comments
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT redthread_comment_text FROM redthread "
                        "WHERE poethread_id = ?", (poe_thread_id,))
            # In theory, any row will do as they'll all have the same data
            # maybe I should refactor this db...
            result = cur.fetchone()
            if result is None:
                return []
            result = result[0]
            parts = result.split("***")
            # trim off preamble
            posts = parts[1:]
            return posts
        finally:
            cur.close()

    def poe_thread_page_count(self, thread_id):
        """
        gets the recorded page counter of given thread
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT poethread_page_count FROM poethread WHERE poethread_id = ?",
                        (thread_id,))
            row = cur.fetchone()

            return None if row is None else row[0]
        finally:
            cur.close()

    def poe_thread_exists(self, thread_id):
        """
        checks if the given thread is in the db
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT 1 FROM poethread WHERE poethread_id = ?", (thread_id,))
            return False if cur.fetchone() is None else True
        finally:
            cur.close()

    def add_poe_thread(self, thread_id, page_count):
        """
        adds a new pathofexile.com thread reacord
        """
        cur = self.db.cursor()
        try:
            cur.execute("INSERT INTO poethread (poethread_id, poethread_page_count) "
                        "VALUES (?, ?)", (thread_id, page_count))
        finally:
            cur.close()

    def update_poe_thread(self, thread_id, page_count):
        """
        updates a threads noted page count
        """
        cur = self.db.cursor()
        try:
            cur.execute("UPDATE poethread SET poethread_page_count = ? "
                             "WHERE poethread_id = ?", (page_count, thread_id))
        finally:
            cur.close()

    def get_reddit_threads_linking_here(self, poe_thread_id):
        """
        returns a list of reddit thread ids that link to the given poe thread
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT redthread_id FROM redthread "
                        "WHERE poethread_id = ?", (poe_thread_id,))
            results = cur.fetchall()
            return [result[0] for result in results]
        finally:
            cur.close()

    def get_comment_id_by_thread(self, thread_id):
        """
        returns the id of the bot comment in the specified thread,
        returns None if the thread has no recorded comment
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT redthread_comment_id FROM redthread "
                        "WHERE redthread_id = ?", (thread_id,))
            row = cur.fetchone()
            return None if row is None else row[0]
        finally:
            cur.close()

    def get_comment_body(self, thread_id):
        """
        returns the text body of a stored comment in the given thread
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT redthread_comment_text FROM redthread "
                        "WHERE redthread_id = ?", (thread_id,))
            row = cur.fetchone()
            return None if row is None else row[0]
        finally:
            cur.close()

    def reddit_thread_exists(self, thread_id):
        """
        checks whether we have a specified reddit post recorded
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT 1 FROM redthread WHERE redthread_id = ?", (thread_id,))
            return False if cur.fetchone() is None else True
        finally:
            cur.close()

    def add_reddit_thread(self, reddit_thread_id, poe_thread_id, comment_id, comment_text):
        """
        adds a new reddit post record
        """
        cur = self.db.cursor()
        try:
            cur.execute("INSERT INTO redthread (redthread_id, poethread_id, "
                        "redthread_comment_id, redthread_comment_text) VALUES (?, ?, ?, ?)",
                        (reddit_thread_id, poe_thread_id, comment_id, comment_text))
        finally:
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
            cur.close()