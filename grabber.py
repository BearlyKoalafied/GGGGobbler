import praw
import sched
import time
import warnings
import logging
import re

import db
import forum_parse as fparse
import settings


from praw.errors import RateLimitExceeded, APIException, ClientException
from requests.exceptions import ConnectionError, HTTPError

POE_URL = "www.pathofexile.com/forum/view-thread"

warnings.simplefilter("ignore", ResourceWarning)

def task(next_sched):
    if settings.LOGGING_ON:
        logging.getLogger(settings.LOGGER_NAME).info("Starting new run")

    bot = GGGGobblerBot()
    RECOVERABLE_EXCEPTIONS = (RateLimitExceeded,
                              APIException,
                              ClientException,
                              ConnectionError,
                              HTTPError)
    try:
        bot.parse_reddit()
    except RECOVERABLE_EXCEPTIONS as e:
        if settings.LOGGING_ON:
            logging.getLogger(settings.LOGGER_NAME).error("Hit Recoverable exception, output: " + str(e))
        bot.dao.rollback()
    except Exception as e:
        if settings.LOGGING_ON:
            logging.getLogger(settings.LOGGER_NAME).critical("Hit unexpected exception, output: " + str(e))
        bot.dao.rollback()
        raise

    # do it again later
    next_sched.enter(settings.WAIT_TIME, 1, task, (next_sched,))
    if settings.LOGGING_ON:
        logging.getLogger(settings.LOGGER_NAME).info("Run over")

def run():
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(5, 1, task, (scheduler,))
    scheduler.run()


class GGGGobblerBot:
    def __init__(self):
        self.r = praw.Reddit(user_agent=settings.APP_USER_AGENT)
        self.r.set_oauth_app_info(settings.APP_ID, settings.APP_SECRET, settings.APP_URI)
        self.r.refresh_access_information(settings.APP_REFRESH)
        self.dao = db.DAO()

    def parse_reddit(self):
        if fparse.forum_is_down():
            logging.getLogger(settings.LOGGER_NAME).info("Pathofexile.com is down for maintenance")
            return
        subreddit = self.r.get_subreddit('pathofexile')
        # collect submissions that link to poe.com
        poe_submissions = []
        ids = []
        for submission in subreddit.get_hot(limit=25):
            if POE_URL in submission.url:
                poe_submissions.append(submission)
                ids.append(submission.id)
        for submission in subreddit.get_new(limit=15):
            if POE_URL in submission.url and submission.id not in ids:
                poe_submissions.append(submission)

        self.parse_submissions(poe_submissions)

    def get_comment_by_id(self, submission, comment_id):
        url = submission.permalink + comment_id
        # permalink submission, one comment stored in submission object here
        return self.r.get_submission(url=url).comments[0]

    def parse_submissions(self, submissions):
        for submission in submissions:
            posts = self.get_current_posts(submission.url)

            # only bother doing stuff if we found staff posts
            if posts == []:
                self.dao.commit()
                continue

            # if a GGG post was linked to directly, put that one up at the top
            result = re.search("#p[0-9]*", submission.url)
            if result is not None:
                target_post_id = result.group(0)[1:]
                for i in range(len(posts)):
                    if posts[i].post_id == target_post_id:
                        # move this post to the front of the list
                        posts.insert(0, posts.pop(i))
                        break

            comments_to_post = self.create_divided_comments(posts)
            if not self.dao.reddit_thread_exists(submission.id):
                self.dao.add_reddit_thread(submission.id, self.extract_poe_id_from_url(submission.url))

            self.send_replies(submission, comments_to_post)
            # saving db state between submissions
            self.dao.commit()
        self.dao.rollback()
        self.dao.close()

    def get_current_posts(self, url):
        poe_thread_id = self.extract_poe_id_from_url(url)
        # check if we've been to this link before
        if self.dao.poe_thread_exists(poe_thread_id):
            # get posts that have been read in the past and placed in the db
            old_posts = self.dao.get_old_staff_posts_by_thread_id(poe_thread_id)
            current_posts, new_page_count = fparse.get_staff_forum_posts(poe_thread_id)
            new_posts = list(current_posts)
            # remove posts with ids that match an id stored in db
            # and keep the new copy of the post
            for current_post in current_posts:
                for old_post in old_posts:
                    # dont add posts to the db if they're already there
                    if current_post.post_id == old_post.post_id:
                        new_posts.remove(current_post)
                        # update db with new post texts
                        if current_post.md_text != old_post.md_text:
                            self.dao.update_staff_post(current_post)
                            old_posts.remove(old_post)
            if new_posts != []:
                self.dao.add_staff_posts(new_posts)
            return current_posts
        else:
            new_posts, new_page_count = fparse.get_staff_forum_posts(poe_thread_id)
            # add the new thread to the db
            self.dao.add_poe_thread(poe_thread_id, new_page_count)
            self.dao.add_staff_posts(new_posts)
            return new_posts

    def create_divided_comments(self, posts):
        """
        returns a list of strings where each string is a comment no more than COMMENT_CHAR_LIMIT long
        """
        comments = []
        cur_comment = self.create_post_preamble()
        sections = [self.create_ggg_post_section(post) for post in posts]

        for section in sections:
            remaining_space = settings.COMMENT_CHAR_LIMIT - len(cur_comment)
            if remaining_space >= len(section):
                cur_comment += section
            else:
                comments.append(cur_comment)
                if len(section) <= settings.COMMENT_CHAR_LIMIT:
                    cur_comment = section
                else:
                    # lazily split crap up
                    parts = []
                    while len(section) > settings.COMMENT_CHAR_LIMIT:
                        part = section[:settings.COMMENT_CHAR_LIMIT]
                        parts.append(part)
                        section = section[settings.COMMENT_CHAR_LIMIT:]
                    if section != "":
                        parts.append(section)
                    comments.extend(parts)
                    cur_comment = ""
        if cur_comment != "":
            comments.append(cur_comment)
        return comments

    def send_replies(self, submission, comments_to_post):
        existing_comment_ids = self.dao.get_comment_ids_by_thread(submission.id)
        num_existing_comments = len(existing_comment_ids)
        num_new_comments = len(comments_to_post)
        if num_new_comments == 0:
            return
        if num_existing_comments == 0:
            new_comments = []
            # create new comments for thread
            thing_to_reply = submission.add_comment(comments_to_post[0])
            time.sleep(settings.TIME_BETWEEN_COMMENTS)
            comments_to_post.remove(comments_to_post[0])
            new_comments.append(thing_to_reply.id)
            for comment in comments_to_post:
                thing_to_reply = thing_to_reply.reply(comment)
                new_comments.append(thing_to_reply.id)
                time.sleep(settings.TIME_BETWEEN_COMMENTS)
            self.dao.add_comments(submission.id, new_comments)

        elif num_new_comments == num_existing_comments:
            for i in range(num_existing_comments):
                comment = self.get_comment_by_id(submission, existing_comment_ids[i])
                comment.edit(comments_to_post[i])
                time.sleep(settings.TIME_BETWEEN_COMMENTS)

        elif num_new_comments > num_existing_comments:
            for i in range(num_existing_comments):
                comment = self.get_comment_by_id(submission, existing_comment_ids[i])
                comment.edit(comments_to_post[i])
                time.sleep(settings.TIME_BETWEEN_COMMENTS)
            # num_existing_comments is guaranteed to be greater than 0 so the loop is
            # guaranteed to run at least 1 time
            # noinspection PyUnboundLocalVariable
            new_comments = [comment.id]
            # create new comments after existing ones
            for i in range(num_existing_comments + 1, num_existing_comments + num_new_comments + 1):
                # noinspection PyUnboundLocalVariable
                comment = comment.reply(comments_to_post[i])
                new_comments.append(comment.id)
                time.sleep(settings.TIME_BETWEEN_COMMENTS)
            self.dao.add_comments(submission.id, new_comments)

    def create_post_preamble(self):
        return "BEEP BOOP BEEP.  Grinding Gears have been detected in the linked thread:\n\n***\n\n"

    def create_markdown_from_posts(self, posts):
        markdown = ""
        for posts in posts:
            markdown += self.create_ggg_post_section(posts)
        return markdown

    def create_ggg_post_section(self, post):
        markdown = "**" + post.author + " wrote:**\n\n"
        # body text
        body = post.md_text
        markdown += body
        # post separator
        footer = "\n\n***\n\n"
        markdown += footer
        return markdown

    def extract_poe_id_from_url(self, url):
        """
        extracts the id of a thread from the url
        """
        start_index = url.find("view-thread") + len("view-thread") + 1
        end_index = url[start_index:].find("/")
        if end_index == -1:
            return url[start_index:]
        return url[start_index:start_index + end_index]


if __name__ == "__main__":
    # setup logging
    logger = logging.getLogger(settings.LOGGER_NAME)
    fh = logging.FileHandler(settings.LOGFILE_NAME)
    fmt = logging.Formatter('[%(levelname)s] [%(asctime)s]: %(message)s')
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
    # start bot
    run()
