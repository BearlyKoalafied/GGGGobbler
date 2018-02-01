import unittest
from GGGGobbler import htmltomd
from test.testdata import data


class ConvertTestCase(unittest.TestCase):
    def test_basic(self):
        html, expected_output = self.load_values('basic')
        self.assertEqual(htmltomd.convert(html), expected_output)

    def test_empty_tag(self):
        html, expected_output = self.load_values('empty_tag')
        self.assertEqual(htmltomd.convert(html), expected_output)

    def test_successive_tags(self):
        html, expected_output = self.load_values('successive')
        self.assertEqual(htmltomd.convert(html), expected_output)

    def test_list(self):
        html, expected_output = self.load_values('list')
        self.assertEqual(htmltomd.convert(html), expected_output)

    def test_a(self):
        html, expected_output = self.load_values('a')
        self.assertEqual(htmltomd.convert(html), expected_output)
        html, expected_output = self.load_values('a_no_href')
        self.assertEqual(htmltomd.convert(html), expected_output)

    def test_strong(self):
        html, expected_output = self.load_values('strong')
        self.assertEqual(htmltomd.convert(html), expected_output)

    def test_strong_inline(self):
        html, expected_output = self.load_values('strong_inline')
        self.assertEqual(htmltomd.convert(html), expected_output)

    def test_nested_types(self):
        html, expected_output = self.load_values('nested_types')
        self.assertEqual(htmltomd.convert(html), expected_output)

    def test_blockquote(self):
        html, expected_output = self.load_values('blockquote')
        self.assertEqual(htmltomd.convert(html), expected_output)

    def test_quote(self):
        md_input = "line of md 1\n\nline of md 2\n\nline of md 3\n\n"
        md_output = "> line of md 1\n\n> line of md 2\n\n> line of md 3\n\n"
        self.assertEqual(htmltomd.quote_boxify(md_input), md_output)

    def test_quote_lists(self):
        md_input = "* bullet 1\n\n* bullet2\n\n* bullet3\n\n"
        md_output = "> * bullet 1\n\n> * bullet2\n\n> * bullet3\n\n"
        self.assertEqual(htmltomd.quote_boxify(md_input), md_output)

    def load_values(self, data_name):
        html = data.values[data_name + "_input"]
        expected_output = data.values[data_name + "_output"]
        return html, expected_output
