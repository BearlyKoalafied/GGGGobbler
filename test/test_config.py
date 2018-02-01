import unittest
from unittest import mock

import configparser
from config import config


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        configparser.ConfigParser.set = mock.MagicMock()
        configparser.ConfigParser.getboolean = mock.MagicMock()
        configparser.ConfigParser.getint = mock.MagicMock()

    def test_set_currently_running(self):
        config.set_currently_running(True)
        configparser.ConfigParser.set.assert_called_with('features', 'currently_running', str(True))

    def test_set_currently_running_False(self):
        config.set_currently_running(False)
        configparser.ConfigParser.set.assert_called_with('features', 'currently_running', str(False))

    def test_set_error_messaging(self):
        config.set_error_messaging(True)
        configparser.ConfigParser.set.assert_called_with('features', 'error_messaging_enabled', str(True))

    def test_set_error_messaging_False(self):
        config.set_error_messaging(False)
        configparser.ConfigParser.set.assert_called_with('features', 'error_messaging_enabled', str(False))

    def test_set_wait_time_main(self):
        config.set_wait_time_main(300)
        configparser.ConfigParser.set.assert_called_with('thread_delays', 'wait_time_main', str(300))

    def test_set_wait_time_check_messages(self):
        config.set_wait_time_check_messages(5)
        configparser.ConfigParser.set.assert_called_with('thread_delays', 'wait_time_check_messages', str(5))

    