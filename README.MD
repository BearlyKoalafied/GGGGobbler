Instructions to run

1\. Install packages
```
	pip install -r requirements.txt
```
2\. Setup OAuth on the reddit account to be used.  Follow the instructions here in the Authorisation URL section http://praw.readthedocs.io/en/latest/getting_started/authentication.html

3\. Create a file called settings.py and specify the following variables:
```	
	# Reddit account to PM errors to
	REDDIT_ACC_OWNER = "redditusername"
	# subreddit to post to
	SUBREDDIT = "pathofexile"
	# Time in seconds to wait between checking for new posts on /r/poe and poe.com specify it to what you like
	WAIT_TIME = 300

	# Time to wait between commenting, useful if you run into rate limiting problems, but these can be ignored if the bot has some karma or is an approved poster
	TIME_BETWEEN_COMMENTS = 0

	# Character limit in a reddit comment, currently 10000
	COMMENT_CHAR_LIMIT = 10000

	# Timezone offset from UTC in hours, used to translate times given in pathofexile.com pages served to bot
	TIMEZONE_OFFSET = 0

	# Logging options
	LOGGING_ON = True
	LOGGER_NAME = "GGGGobblerVomitter"
	LOGFILE_NAME = "GGGGobblerVomit.log"
```

4\. Create a file called oauth.ini like this:

```
[app]
scope = identity,edit,flair,history,mysubreddits,privatemessages,read,report,save,submit,subscribe,vote,wikiedit,wikiread
user_agent= User-Agent: ...
client_id = abcdefg
client_secret = hijklmnop

[token]
refresh_token = 11111111-abc-dfg

```
client_id, client_secret, and refresh token are the information kept from step 2 to run the bot.  

5\. Do
```
	python grabber.py
```
The bot should run forever until it's stopped without needing attention.  It might need fixing if the layout of pathofexile.com changes or some element I didn't consider is introduced in a news post or something that breaks my bad code :^)
