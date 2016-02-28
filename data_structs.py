
class StaffPost:
    """
    Class to encapsulate a post's contents with its author and parent thread
    """
    def __init__(self, thread_id, author, md_text):
        self.thread_id = thread_id
        self.author = author
        self.md_text = md_text
