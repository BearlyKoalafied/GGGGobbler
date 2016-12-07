Instructions to run

1. Install packages
```
	pip install -r requirements.txt
```
2. Setup OAuth on the reddit account to be used as well as OAuth2Util instructions spefified here https://github.com/SmBe19/praw-OAuth2Util

3. Create a file called settings.py and specify the following variables:
```
	# Time in seconds to wait between checking for new posts on /r/poe and poe.com specify it to what you like
	WAIT_TIME = 300

	# Time to wait between commenting, useful if you run into rate limiting problems, but these can be ignored if the bot has some karma or is an approved poster
	TIME_BETWEEN_COMMENTS = 0

	# Character limit in a reddit comment, currently 1000
	COMMENT_CHAR_LIMIT = 10000

	# Timezone offset from UTC in hours, used to translate times given in pathofexile.com pages served to bot
	TIMEZONE_OFFSET = 0

	# Logging options
	LOGGING_ON = True
	LOGGER_NAME = "GGGGobblerVomitter"
	LOGFILE_NAME = "GGGGobblerVomit.log"
```
4. Do
```
	python grabber.py
```
The bot should run forever until it's stopped without needing attention.  It might need fixing if the layout of pathofexile.com changes or some element I didn't consider is introduced in a news post or something that breaks my bad code :^)
