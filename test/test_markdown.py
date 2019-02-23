import unittest
import os
from util import filepather
from GGGGobbler import markdown as md


class MarkdownTestCase(unittest.TestCase):
    def test_basic(self):
        expected_output = self.load_md("basic")
        doc = md.MarkdownDocument()
        doc.add(md.MarkdownParagraph("some words follow by more words after them"))
        self.assertEqual(expected_output, str(doc))

    def test_paragraphs(self):
        expected_output = self.load_md("paragraphs")
        doc = md.MarkdownDocument()
        doc.add(md.MarkdownParagraph("This is paragraph number 1"))
        doc.add(md.MarkdownParagraph("This is paragraph number 2"))
        self.assertEqual(expected_output, str(doc))

    def test_strong(self):
        expected_output = self.load_md("strong")
        strong = md.MarkdownStrong("Strong text")
        self.assertEqual(expected_output, str(strong))

    def test_italics(self):
        expected_output = self.load_md("italics")
        italics = md.MarkdownItalics("Italics text")
        self.assertEqual(expected_output, str(italics))

    def test_strong_with_whitespace(self):
        expected_output = self.load_md("strong_with_whitespace")
        strong = md.MarkdownStrong("Strong text ")
        self.assertEqual(expected_output, str(strong))

    def test_italics_with_whitespace(self):
        expected_output = self.load_md("italics_with_whitespace")
        italics = md.MarkdownItalics("Italics text ")
        self.assertEqual(expected_output, str(italics))

    def test_paragraphs_with_inline(self):
        expected_output = self.load_md("paragraphs_with_inline")
        para = md.MarkdownParagraph()
        para.add("Starting text ")
        para.add(md.MarkdownStrong("followed by strong text "))
        para.add(md.MarkdownItalics("followed by italics "))
        para.add("followed by normal text.")
        self.assertEqual(expected_output, str(para))

    def test_list(self):
        expected_output = self.load_md("list")
        list_md = md.MarkdownList()
        list_md.add("List item 1")
        list_md.add("List item 2")
        list_md.add("List item 3")
        self.assertEqual(expected_output, str(list_md))

    def test_list_whitespace(self):
        expected_output = self.load_md("list_whitespace")
        doc = md.MarkdownDocument()
        doc.add(md.MarkdownListItem("List item 1"))
        doc.add(md.MarkdownListItem("List item 2"))
        doc.add(md.MarkdownParagraph("proceeding paragraph"))
        self.assertEqual(expected_output, str(doc))

    def test_link(self):
        expected_output = self.load_md("link")
        link = md.MarkdownLink("link text", "example.com/link")
        self.assertEqual(expected_output, str(link))

    def test_link_with_parentheses(self):
        expected_output = self.load_md("link_escapes")
        link = md.MarkdownLink("escaped parentheses", "https://example.com/long_item_name_with(parentheses)")
        self.assertEqual(expected_output, str(link))

    def test_basic_quote(self):
        expected_output = self.load_md("basic_quote")
        quotebox = md.MarkdownQuotebox()
        quotebox.add(md.MarkdownParagraph("The text of paragraph 1"))
        para = md.MarkdownParagraph()
        para.add("Some text before ")
        para.add(md.MarkdownStrong("the strong text"))
        quotebox.add(para)
        self.assertEqual(expected_output, str(quotebox))

    def test_nested_quotes(self):
        expected_output = self.load_md("nested_quote2")
        quotebox = md.MarkdownQuotebox()
        quotebox.add(md.MarkdownParagraph("Paragraph 1"))
        nested_quotebox = md.MarkdownQuotebox()
        nested_quotebox.add(md.MarkdownParagraph("Paragraph 2 (nested)"))
        quotebox.add(nested_quotebox)
        quotebox.add(md.MarkdownParagraph("Paragraph 3"))
        self.assertEqual(expected_output, str(quotebox))
        expected_output = self.load_md("nested_quote3")
        level_0 = md.MarkdownDocument()
        level_1 = md.MarkdownQuotebox()
        level_2 = md.MarkdownQuotebox()
        level_3 = md.MarkdownQuotebox()
        level_0.add(md.MarkdownParagraph("Outside quotes!"))
        level_1.add(md.MarkdownParagraph("First level"))
        level_2.add(md.MarkdownParagraph("Second level"))
        level_3.add(md.MarkdownParagraph("Third level"))
        level_0.add(level_1)
        level_1.add(level_2)
        level_2.add(level_3)
        level_1.add(md.MarkdownParagraph("Back on the first level"))
        level_0.add(md.MarkdownLink("Link at the end of the document", "https://nowhere.com"))
        self.assertEqual(expected_output, str(level_0))

    def test_basic_header(self):
        expected_output = self.load_md("basic_header")
        h = md.MarkdownHeader("Basic header")
        self.assertEqual(expected_output, str(h))

    def test_level_header(self):
        expected_output = self.load_md("level_header")
        h = md.MarkdownHeader("Level 3 header", 3)
        self.assertEqual(expected_output, str(h))

    def test_basic_table(self):
        expected_output = self.load_md("basic_table")
        row1 = ["Just a normal table", "yup, normal", "nothing here"]
        row2 = ["more rows", "blah blah", "yep yep"]
        table = md.MarkdownTable([row1, row2])
        self.assertEqual(expected_output, str(table))

    def test_headers_table(self):
        expected_output = self.load_md("headers_table")
        headers = ["header 1", "header 2"]
        row1 = ["under header 1", "under header 2"]
        table = md.MarkdownTable([row1], headers=headers)
        self.assertEqual(expected_output, str(table))

    def test_variable_width_table(self):
        expected_output = self.load_md("variable_width_table")
        headers = ["header 1", "header 2", "header 3"]
        row1 = ["", "under header 2"]
        row2 = ["under header 1", "under header 2"]
        row3 = ["under header 1", "under header 2", "under header 3"]
        table = md.MarkdownTable([row1, row2, row3], headers=headers)
        self.assertEqual(expected_output, str(table))

    def test_code_span(self):
        expected_output = self.load_md("code_span")
        code = md.MarkdownCodeSpan("int x = 5")
        self.assertEqual(expected_output, str(code))

    def test_code_fence(self):
        expected_output = self.load_md("code_fence")
        code = md.MarkdownCodeBlock("int x = 5\nx++\nfloat b = 0.0\nexit()\n")
        self.assertEqual(expected_output, str(code))

    def test_quoted_code_fence(self):
        expected_output = self.load_md("quoted_code_fence")
        qcf = md.MarkdownDocument()
        qcf.add(md.MarkdownParagraph("Outside quotes!"))
        quote = md.MarkdownQuotebox()
        code = md.MarkdownCodeBlock("int x = 5\nx++\n")
        quote.add(code)
        quote.add(md.MarkdownParagraph("Below the code fence"))
        qcf.add(quote)
        self.assertEqual(expected_output, str(qcf))

    def test_quoted_list(self):
        expected_output = self.load_md("quoted_list")
        quote = md.MarkdownQuotebox()
        quote.add(md.MarkdownListItem("Item 1"))
        quote.add(md.MarkdownListItem("Item 2"))
        quote.add(md.MarkdownListItem("Item 3"))
        self.assertEqual(expected_output, str(quote))

    def load_md(self, data_name):
        path = filepather.relative_file_path(__file__, os.path.join("testdata", "markdown"))
        with open(os.path.join(path, data_name + ".md"), 'r') as f:
            # cut off trailing \n
            file_contents = f.read()
            if file_contents[-1] != "\n":
                raise TestDataFileFormatException("Test data files should contain the tested text data following by an extraneous newline character")
            return file_contents[:-1]


class TestDataFileFormatException(Exception):
    pass
