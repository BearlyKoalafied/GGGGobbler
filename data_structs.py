
class StaffPost:
    """
    Class to encapsulate a post's contents with its author and parent thread
    """
    def __init__(self, post_id, thread_id, author, md_text):
        self.thread_id = thread_id
        self.post_id = post_id
        self.author = author
        self.md_text = md_text

    def __eq__(self, other):
        return self.thread_id == other.thread_id and \
            self.post_id == other.post_id and \
            self.author == other.author and \
            self.md_text == other.md_text