import praw
import sched
import time
import warnings
import logging
import re
import os
import errno

import db
import forum_parse as fparse
import gobOauth
import ErrorHandling
import msgcfg
import timeout
import settings

POE_URL = "pathofexile.com/forum/view-thread"
TIMEOUT_SECONDS = 300
CSS_MAGIC_PREPEND = """#####&#009;\n\n######&#009;\n\n####&#009;\n\n"""

warnings.simplefilter("ignore", ResourceWarning)

# praw and oauth api
global r

def task(next_sched):
    logging.getLogger(settings.LOGGER_NAME).info("Starting run")
    dao = db.DAO()

    @timeout.timeout(TIMEOUT_SECONDS, os.strerror(errno.ETIMEDOUT))
    def repeated_func():
        msgcfg.check_messages(r)
        if msgcfg.currently_running_enabled():
            bot = GGGGobblerBot(dao)
            bot.parse_reddit()



    # run the bot
    ErrorHandling.handle_errors(r, repeated_func, dao)

    # do it again later
    next_sched.enter(settings.WAIT_TIME, 1, task, (next_sched,))
    logging.getLogger(settings.LOGGER_NAME).info("Finished run")


def run():
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(0, 1, task, (scheduler,))
    scheduler.run()


class GGGGobblerBot:
    global r
    def __init__(self, dao=None):
        self.r = r
        if dao is None:
            self.dao = db.DAO()
        else:
            self.dao = dao

    def parse_reddit(self):
        subreddit = self.r.subreddit(settings.SUBREDDIT)
        # collect submissions that link to poe.com
        poe_submissions = []
        ids = []
        for submission in subreddit.hot(limit=25):
            if POE_URL in submission.url:
                poe_submissions.append(submission)
                ids.append(submission.id)
        for submission in subreddit.new(limit=25):
            if POE_URL in submission.url and submission.id not in ids:
                poe_submissions.append(submission)

        self.parse_submissions(poe_submissions)

    def get_comment_by_id(self, submission, comment_id):
        return self.r.comment(comment_id)

    def parse_submissions(self, submissions):
        for submission in submissions:
            self.parse_submission(submission)
        self.dao.rollback()
        self.dao.close()

    def parse_submission(self, submission):
        posts = self.get_current_posts(submission.url)
        # only bother doing stuff if we found staff posts
        if posts == []:
            self.dao.commit()
            return
        # posts = self.remove_unchanged_posts(posts)
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
            logging.getLogger(settings.LOGGER_NAME).info("New reddit thread discovered, thread id = "
                                                         + submission.id)

        self.send_replies(submission, comments_to_post)
        # saving db state between submissions
        self.dao.commit()


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

    def remove_unchanged_posts(self, posts):
        corresponding_posts = self.dao.get_staff_posts_by_id([post.post_id for post in posts])
        for post in posts:
            # find the corresponding post
            for corresponding_post in corresponding_posts:
                if corresponding_post.post_id == post.post_id \
                and corresponding_post.md_text == post.md_text:
                    posts.remove(post)
        return posts

    def create_divided_comments(self, posts):
        """
        returns a list of strings where each string is a comment no more than COMMENT_CHAR_LIMIT long
        """
        comments = []
        preamble = self.create_post_preamble()
        cont_preamble = self.create_continue_post_preamble()
        cur_comment = preamble
        sections = [self.create_ggg_post_section(post) for post in posts]
        total_chars = sum([len(section) for section in sections]) + len(preamble)
        if total_chars <= settings.COMMENT_CHAR_LIMIT:
            return [preamble + "".join(sections)]

        for section in sections:
            if cur_comment == "":
                cur_comment = cont_preamble
            remaining_space = settings.COMMENT_CHAR_LIMIT - len(cur_comment)
            if remaining_space >= len(section):
                cur_comment += section
                continue
            # if the cur_comment has any posts on it, move to the next comment
            elif cur_comment != self.create_continue_post_preamble() \
            and cur_comment != self.create_post_preamble():
                comments.append(cur_comment)
                cur_comment = ""
            parts = []
            while len(section) > settings.COMMENT_CHAR_LIMIT:
                if cur_comment == "":
                    cur_comment = cont_preamble
                chars_to_split_off = settings.COMMENT_CHAR_LIMIT - len(cur_comment)
                index_to_split_at = section[:chars_to_split_off].rfind("\n\n") + 2
                part = cur_comment + section[:index_to_split_at]
                cur_comment = ""
                parts.append(part)
                section = section[index_to_split_at:]
            if section != "":
                if len(cont_preamble + section) > settings.COMMENT_CHAR_LIMIT:
                    chars_to_split_off = settings.COMMENT_CHAR_LIMIT - len(cont_preamble)
                    index_to_split_at = section[:chars_to_split_off].rfind("\n\n") + 2
                    parts.extend([cont_preamble + section[:index_to_split_at], section[index_to_split_at:]])
                else:
                    parts.append(cont_preamble + section)
            comments.extend(parts)
        return comments

    def send_replies(self, submission, comments_to_post):
        num_new_comments = len(comments_to_post)
        if num_new_comments == 0:
            return
        existing_comment_ids = self.dao.get_comment_ids_by_thread(submission.id)
        num_existing_comments = len(existing_comment_ids)

        if num_existing_comments == 0:
            new_comments = []
            # create new comments for thread
            top_level_comment = submission.reply(comments_to_post[0])
            self.sticky_comment(submission, top_level_comment)
            time.sleep(settings.TIME_BETWEEN_COMMENTS)
            comments_to_post.remove(comments_to_post[0])
            new_comments.append(top_level_comment.id)
            for comment in comments_to_post:
                top_level_comment = top_level_comment.reply(comment)
                new_comments.append(top_level_comment.id)
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
            new_comments = []
            # create new comments after existing ones
            for i in range(num_existing_comments, num_new_comments):
                comment = comment.reply(comments_to_post[i])
                new_comments.append(comment.id)
                time.sleep(settings.TIME_BETWEEN_COMMENTS)
            self.dao.add_comments(submission.id, new_comments)

    def sticky_comment(self, submission, comment):
        # code to sticky comments (shelved)
        pass
        # # check if the mods have already posted a sticky comment
        # # and respect it if so
        # submissionHasSticky = False
        # for comment in submission.comments:
        #     if comment.sticky:
        #         submissionHasSticky = True
        #         break
        # # sticky the bot's top level comment in the thread
        # if not submissionHasSticky:
        #     comment.distinguish(as_made_by='mod', sticky=True)

    def create_post_preamble(self):
        return CSS_MAGIC_PREPEND + \
               "BEEP BOOP BEEP.  Grinding Gears have been detected in the linked thread:\n\n***\n\n"

    def create_continue_post_preamble(self):
        return CSS_MAGIC_PREPEND + \
               "(continued from above comment)\n\n***\n\n"

    def create_markdown_from_posts(self, posts):
        markdown = ""
        for posts in posts:
            markdown += self.create_ggg_post_section(posts)
        return markdown

    def create_ggg_post_section(self, post):
        markdown = "> **Posted by " + post.author + "** on " + post.date + " UTC\n\n"
        # body text
        body = post.md_text
        markdown += body
        # post separator
        footer = "\n\n> ***\n\n"
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

    # tools
    def force_update_all(self):
        """
        updates every post made by the bot stored in the db.
        """
        print("Beginning force update all...")
        threads = self.dao.get_all_reddit_threads()
        for thread in threads:
            # get submission by id
            submission = self.r.submission(thread[0])
            self.parse_submission(submission)
        print("Finished force update all")


if __name__ == "__main__":
    global r
    # oauth stuff
    r = gobOauth.get_refreshable_instance()
    # setup logging
    logger = logging.getLogger(settings.LOGGER_NAME)
    fh = logging.FileHandler(settings.LOGFILE_NAME)
    fmt = logging.Formatter('[%(levelname)s] [%(asctime)s]: %(message)s')
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
    if not settings.LOGGING_ON:
        logging.disable(logging.CRITICAL)
    # start bot
    run()
