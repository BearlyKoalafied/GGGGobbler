import praw
import configparser

from util import filepather

def read_ini():
    cfg = configparser.ConfigParser()
    cfg.read(filepather.relative_file_path(__file__, 'oauth.ini'))
    return cfg


def get_refreshable_instance():
    cfg = read_ini()
    reddit = praw.Reddit(client_id=cfg['app']['client_id'],
                         client_secret=cfg['app']['client_secret'],
                         refresh_token=cfg['token']['refresh_token'],
                         user_agent=cfg['app']['user_agent'])
    return reddit
