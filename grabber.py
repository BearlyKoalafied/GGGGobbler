import praw
import sched
import time

import db
import forum_parse as fparse
import settings

TARGET_URLS = "https://www.pathofexile.com/forum/view-thread"

def task(next_sched):
    print("starting next run...")
    bot = GGGGobblerBot()
    bot.parse_reddit()
    print("run over...")
    # do it again later
    next_sched.enter(settings.WAIT_TIME, 1, task, (next_sched,))


def run():
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(settings.WAIT_TIME, 1, task, (scheduler,))
    scheduler.run()


class GGGGobblerBot:
    def __init__(self):
        self.r = praw.Reddit(user_agent = settings.APP_USER_AGENT)
        self.r.set_oauth_app_info(settings.APP_ID, settings.APP_SECRET, settings.APP_URI)
        self.r.refresh_access_information(settings.APP_REFRESH)
        self.dao = db.DAO()

    def parse_reddit(self):
        subreddit = self.r.get_subreddit('test')
        # collect submissions that link to poe.com from top 25 hot
        poe_submissions = []
        for submission in subreddit.get_hot(limit = 25):
            if submission.url.startswith(TARGET_URLS):
                poe_submissions.append(submission)
        self.dao.open()
        self.parse_submissions(poe_submissions)

    def get_comment_by_id(self, submission, comment_id):
        url = submission.url + "/" + comment_id
        # permalink submission, one comment stored
        return self.r.get_submission(url=url).comments[0]

    def parse_submissions(self, submissions):
        for submission in submissions:
            # get the thread ids
            reddit_id = submission.id
            poe_id = submission.url[42:]
            # check if we've been to this link before
            if self.dao.poe_thread_exists(int(poe_id)):
                # only check past the pages we've read already
                page_number = self.dao.poe_thread_page_count(int(poe_id))
                staff_rows = fparse.get_staff_forum_post_rows(submission.url, page_number)
                comment_text = self.create_markdown_from_posts(staff_rows)
            else:
                # parse its pages
                staff_rows = fparse.get_staff_forum_post_rows(submission.url)
                comment_text = self.create_markdown_from_posts(staff_rows)
                page_number = fparse.get_page_count(submission.url)
                # add the new thread to the db
                self.dao.add_poe_thread(poe_id, page_number)

            # check if we've commented on this thread before
            comment_id = self.dao.get_bot_comment_(reddit_id)
            if comment_id is not None:
                # find the comment and edit it with new posts
                comment = self.get_comment_by_id(submission, comment_id)
                comment.edit(comment_text)
                # update db with new info
                self.dao.update_reddit_thread(reddit_id, comment_text)
            else:
                # create a new comment then add its details to the db
                new_comment = submission.add_comment(comment_text)
                self.dao.add_reddit_thread(reddit_id, poe_id, new_comment.id, comment_text)

    def create_markdown_from_posts(self, staff_rows):
        markdown = ""
        for row in staff_rows:
            markdown += self.create_ggg_post_section(row)
        return markdown

    def create_ggg_post_section(self, post_row):
        # author label
        author = fparse.get_post_author_from_row(post_row)
        markdown = "**" + author + " wrote:**\n\n"
        # body text
        body = fparse.convert_html_to_markdown(fparse.get_post_from_row(post_row))
        markdown += body
        # line separator
        footer = "***\n\n"
        markdown += footer
        return markdown

if __name__ == "__main__":
    run()
