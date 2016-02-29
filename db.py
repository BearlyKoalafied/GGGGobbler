import sqlite3
from data_structs import StaffPost

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
                                    poethread_page_count INTEGER
                                    )""")

            cur.execute("""CREATE TABLE redthread (
                                    redthread_id TEXT PRIMARY KEY,
                                    poethread_id TEXT,
                                    FOREIGN KEY(poethread_id) REFERENCES poethread(poethread_id)
                                    )""")

            cur.execute("""CREATE TABLE comment (
                                    comment_id TEXT PRIMARY KEY,
                                    comment_order_index INTEGER,
                                    redthread_id TEXT,
                                    FOREIGN KEY(redthread_id) REFERENCES redthread(redthread_id)
                                    )""")

            cur.execute("""CREATE TABLE staffpost (
                                    staffpost_id TEXT PRIMARY KEY,
                                    poethread_id TEXT,
                                    staffpost_text TEXT,
                                    staffpost_author TEXT,
                                    FOREIGN KEY(poethread_id) REFERENCES poethread(poethread_id)
                                    )""")

        finally:
            cur.close()

    def get_old_staff_posts_by_thread_id(self, poe_thread_id):
        """
        returns a list of StaffPosts of posts stored in the db for the specified thread
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT staffpost_id, staffpost_author, staffpost_text "
                        "FROM staffpost WHERE poethread_id = ?", (poe_thread_id,))
            results = cur.fetchall()
            if results is None:
                return []
            return [StaffPost(result[0], poe_thread_id, result[1], result[2]) for result in results]
        finally:
            cur.close()

    def poe_thread_page_count(self, poe_thread_id):
        """
        gets the recorded page counter of given thread
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT poethread_page_count FROM poethread WHERE poethread_id = ?",
                        (poe_thread_id,))
            row = cur.fetchone()

            return None if row is None else row[0]
        finally:
            cur.close()

    def poe_thread_exists(self, poe_thread_id):
        """
        checks if the given thread is in the db
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT 1 FROM poethread WHERE poethread_id = ?", (poe_thread_id,))
            return False if cur.fetchone() is None else True
        finally:
            cur.close()

    def add_poe_thread(self, poe_thread_id, page_count):
        """
        adds a new pathofexile.com thread reacord
        """
        cur = self.db.cursor()
        try:
            cur.execute("INSERT INTO poethread (poethread_id, poethread_page_count) "
                        "VALUES (?, ?)", (poe_thread_id, page_count))
        finally:
            cur.close()

    def add_staff_posts(self, posts):
        """
        adds a given list of StaffPosts to the db
        """
        cur = self.db.cursor()
        try:
            params = []
            for post in posts:
                params.append((post.post_id, post.thread_id, post.md_text, post.author))
            if params != []:
                cur.executemany("INSERT INTO staffpost (staffpost_id, poethread_id, staffpost_text, staffpost_author)"
                                " VALUES (?, ?, ?, ?)", params)
        finally:
            cur.close()

    def update_staff_post(self, post):
        """
        updates post text in the db that matches the given post's id
        """
        cur = self.db.cursor()
        try:
            cur.execute("UPDATE staffpost SET staffpost_text = ? WHERE staffpost_id = ?",
                            (post.md_text, post.post_id))
        finally:
            cur.close()

    def update_poe_thread(self, poe_thread_id, page_count):
        """
        updates a threads noted page count
        """
        cur = self.db.cursor()
        try:
            cur.execute("UPDATE poethread SET poethread_page_count = ? "
                         "WHERE poethread_id = ?", (page_count, poe_thread_id))
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

    def get_comment_ids_by_thread(self, reddit_thread_id):
        """
        returns an ordered list of ids for the bot comments in the specified thread
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT comment_id, comment_order_index FROM comment "
                        "WHERE redthread_id = ?", (reddit_thread_id,))
            results = cur.fetchall()
            count = len(results)
            out = []

            for i in range(count):
                next = min(results, key = lambda k: k[1])
                out.append(next[0])
                results.remove(next)
            return out
        finally:
            cur.close()

    def reddit_thread_exists(self, reddit_thread_id):
        """
        checks whether we have a specified reddit post recorded
        """
        cur = self.db.cursor()
        try:
            cur.execute("SELECT 1 FROM redthread WHERE redthread_id = ?", (reddit_thread_id,))
            return False if cur.fetchone() is None else True
        finally:
            cur.close()

    def add_reddit_thread(self, reddit_thread_id, poe_thread_id):
        """
        adds a new reddit post record
        """
        cur = self.db.cursor()
        try:
            cur.execute("INSERT INTO redthread (redthread_id, poethread_id) VALUES (?, ?)",
                        (reddit_thread_id, poe_thread_id))
        finally:
            cur.close()

    def add_reddit_comment(self, comment_id, reddit_thread_id, ordinal):
        """
        adds a new reddit comment record
        """
        cur = self.db.cursor()
        try:
            cur.execute("INSERT INTO comment (comment_id, comment_order_index, redthread_id)"
                        " VALUES (?, ?, ?)", (comment_id, ordinal, reddit_thread_id))
        finally:
            cur.close()

    def add_comments(self, reddit_thread_id, comment_ids):
        """
        adds a list of new reddit comment records
        """
        cur = self.db.cursor()
        try:
            # get the number of comments already here
            cur.execute("SELECT COUNT(*) FROM comment WHERE redthread_id = ?", (reddit_thread_id,))
            num_old_comments = cur.fetchone()[0]

            new_order_indexes = [i for i in range(num_old_comments + 1, num_old_comments + len(comment_ids) + 1)]

            params = [(comment_ids[i], new_order_indexes[i], reddit_thread_id)
                      for i in range(len(new_order_indexes))]
            cur.executemany("INSERT INTO comment (comment_id, comment_order_index, redthread_id) "
                        "VALUES (?, ?, ?)", params)
        finally:
            cur.close()
