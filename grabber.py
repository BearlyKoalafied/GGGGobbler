import praw

import settings

r = praw.Reddit(user_agent = settings.APP_USER_AGENT)
r.set_oauth_app_info(settings.APP_ID, settings.APP_SECRET, settings.APP_URI)
r.refresh_access_information(settings.APP_REFRESH)
rPathOfExile = r.get_subreddit('pathofexile')

for submission in rPathOfExile.get_hot(limit = 5):
    print(submission.domain)



if __name__ == "__main__":
    pass