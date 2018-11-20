import unittest
import os
from util import filepather
from GGGGobbler import htmltomd
from test.testdata import data


class ConvertTestCase(unittest.TestCase):
    def test_basic(self):
        html, expected_output = self.load_values('basic')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_empty_tag(self):
        html, expected_output = self.load_values('empty_tag')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_successive_tags(self):
        html, expected_output = self.load_values('successive')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_list(self):
        html, expected_output = self.load_values('list')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_a(self):
        html, expected_output = self.load_values('a')
        self.assertEqual(expected_output, htmltomd.convert(html))
        html, expected_output = self.load_values('a_no_href')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_italics(self):
        html, expected_output = self.load_values('italics')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_italics_whitespace(self):
        html, expected_output = self.load_values('italics_whitespace')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_italics_inline(self):
        html, expected_output = self.load_values('italics_inline')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_strong(self):
        html, expected_output = self.load_values('strong')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_strong_whitespace(self):
        html, expected_output = self.load_values('strong_whitespace')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_strong_inline(self):
        html, expected_output = self.load_values('strong_inline')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_nested_types(self):
        html, expected_output = self.load_values('nested_types')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_blockquote(self):
        html, expected_output = self.load_values('blockquote')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_quote(self):
        md_input = "line of md 1\n\nline of md 2\n\nline of md 3\n\n"
        md_output = "> line of md 1\n>\n> line of md 2\n>\n> line of md 3\n>\n"
        self.assertEqual(md_output, htmltomd.quote_boxify(md_input))

    def test_nested_level_util(self):
        line1 = "level 0"
        expected1 = 0
        self.assertEqual(expected1, htmltomd.nested_level_of_line(line1))
        line2 = "> level 1"
        expected2 = 1
        self.assertEqual(expected2, htmltomd.nested_level_of_line(line2))
        line3 = "> > level 2"
        expected3 = 2
        self.assertEqual(expected3, htmltomd.nested_level_of_line(line3))

    def test_nested_quote(self):
        html, expected_output = self.load_values('nested_quote')
        self.assertEqual(expected_output, htmltomd.quote_boxify(htmltomd.convert(html)))

    def test_quote_lists(self):
        md_input = "* bullet 1\n\n* bullet2\n\n* bullet3\n\n"
        md_output = "> * bullet 1\n>\n> * bullet2\n>\n> * bullet3\n>\n"
        self.assertEqual(md_output, htmltomd.quote_boxify(md_input))

    def test_iframe_basic(self):
        html, expected_output = self.load_values('iframe_basic')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_iframe_embed(self):
        html, expected_output = self.load_values('iframe_embed')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def test_quote_challenge_titles(self):
        html, expected_output = self.load_values_v2('challenge_quote')
        self.outputfile(htmltomd.quote_boxify(htmltomd.convert(html)))
        self.assertEqual(expected_output, htmltomd.quote_boxify(htmltomd.convert(html)))

    def test_complex(self):
        html, expected_output = self.load_values('complex')
        self.assertEqual(expected_output, htmltomd.quote_boxify(htmltomd.convert(html)))

    def test_complex_2(self):
        html, expected_output = self.load_values('complex_2')
        self.assertEqual(expected_output, htmltomd.quote_boxify(htmltomd.convert(html)))

    def test_raw_embedded_video(self):
        html, expected_output = self.load_values('raw_embedded_video')
        self.assertEqual(expected_output, htmltomd.convert(html))

    def load_values(self, data_name):
        html = data.values[data_name + "_input"]
        expected_output = data.values[data_name + "_output"]
        return html, expected_output

    def load_values_v2(self, data_name):
        path = filepather.relative_file_path(__file__, "testdata")
        with open(os.path.join(path, data_name + "_input.html"), 'r') as f:
            # cut off the trailing \n
            html = f.read()[:-1]
        with open(os.path.join(path, data_name + "_output.md"), 'r') as f:
            expected_output = f.read()[:-1]
        return html, expected_output

    def outputfile(self, string):
        with open('output.txt', 'w')as f:
            f.write(string)
