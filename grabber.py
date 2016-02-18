import praw
import sched
import time

import db
import forum_parse as fparse
import settings

POE_URLS = "https://www.pathofexile.com/forum/view-thread"

def task(next_sched):
    print("starting next run...")
    bot = GGGGobblerBot()
    sleep_time = 0
    try:
        bot.parse_reddit()
    except praw.errors.RateLimitExceeded as e:
        sleep_time = e.sleep_time
        bot.dao.rollback()
        print("Rate Limit Exceeded time = " + str(sleep_time) + ", waiting until next cycle")
    # do it again later
    if sleep_time > settings.WAIT_TIME:
        next_sched.enter(sleep_time, 1, task, (next_sched,))
        sleep_time = 0
    else:
        next_sched.enter(settings.WAIT_TIME, 1, task, (next_sched,))
    print("run over...")

def run():
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(5, 1, task, (scheduler,))
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
        for submission in subreddit.get_hot(limit = 10):
            if submission.url.startswith(POE_URLS):
                poe_submissions.append(submission)

        self.parse_submissions(poe_submissions)

    def get_comment_by_id(self, submission, comment_id):
        url = submission.permalink + comment_id
        # permalink submission, one comment stored in submission object here
        return self.r.get_submission(url=url).comments[0]

    def parse_submissions(self, submissions):
        for submission in submissions:
            # get the thread ids
            reddit_id = submission.id
            poe_id = self.extract_poe_id_from_url(submission.url)
            # check if we've been to this link before
            if self.dao.poe_thread_exists(poe_id):
                # only check past the pages we've read already
                page_number = self.dao.poe_thread_page_count(poe_id)
                staff_rows = fparse.get_staff_forum_post_rows(submission.url, page_number)
                comment_body_text = self.create_markdown_from_posts(staff_rows)
            else:
                # parse its pages
                staff_rows = fparse.get_staff_forum_post_rows(submission.url)
                comment_body_text = self.create_markdown_from_posts(staff_rows)
                page_number = fparse.get_page_count(submission.url)
                # add the new thread to the db
                self.dao.add_poe_thread(poe_id, page_number)

            # check if we've seen this thread before
            if self.dao.reddit_thread_exists(reddit_id):
                current_comment_text = self.dao.get_comment_body(reddit_id)
                new_text = current_comment_text + comment_body_text
                # check if we need to bother doing anything
                if new_text != current_comment_text:
                    # update db with new info
                    self.dao.update_reddit_thread(reddit_id, new_text)
                    # find the comment and edit it with new posts
                    comment_id = self.dao.get_comment_id_by_thread(reddit_id)
                    comment = self.get_comment_by_id(submission, comment_id)
                    comment.edit(new_text)
            else:
                # make fresh comment
                comment_text = self.create_post_preamble() + comment_body_text
                new_comment = submission.add_comment(comment_text)
                # create a new comment then add its details to the db
                self.dao.add_reddit_thread(reddit_id, poe_id, new_comment.id, comment_text)
            # saving db state between submissions
            self.dao.commit()
            # waiting some time between submissions because reddit gets mad at new accounts
            time.sleep(35)

        self.dao.close()

    def create_post_preamble(self):
        return "BEEP BOOP BEEP.  Grinding Gears have been detected in the linked thread:\n\n***\n\n"

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

    def extract_poe_id_from_url(self, url):
        """
        extracts the id of a thread from the url
        """
        return url[len(POE_URLS)+1:len(POE_URLS)+8]

if __name__ == "__main__":
    run()
