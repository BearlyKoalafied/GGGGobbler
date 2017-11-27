from GGGGobbler.thread import starter
from GGGGobbler import goboauth
from log import gobblogger


def main():
    # connect using oauth to reddit
    reddit = goboauth.get_refreshable_instance()
    # setup logging
    gobblogger.prepare()
    starter.start_threads(reddit)

if __name__ == "__main__":
    main()
