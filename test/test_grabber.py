import unittest
from GGGGobbler.grabber import GGGGobblerBot
from GGGGobbler import htmltomd
from db.data_structs import StaffPost
from util import filepather
import os


class GrabberTestCase(unittest.TestCase):
    # quick dirty test
    def test_splitting(self):
        bot = GGGGobblerBot(None, None)
        path = filepather.relative_file_path(__file__, os.path.join('testdata', 'longpost.txt'))
        with open(path) as md:
            staffposts = [StaffPost('abcdef', '123456', 'Bex', md.read(), 'date-test')]
            posts = bot.create_divided_comments(staffposts)
            self.assertEqual(len(posts), 7)
