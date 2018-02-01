values = {
    "basic_input": "<div>inner html text</div>",
    "basic_output": "inner html text\n\n",

    "empty_tag_input": "<a></a>",
    "empty_tag_output": "",

    "successive_input": "<div>the first tag</div><div>the second tag</div><div>the third tag</div>",
    "successive_output": "the first tag\n\nthe second tag\n\nthe third tag\n\n",

    "list_input": "<ul>"
                  "<li>List point 1.</li>"
                  "<li>List point 2.</li>"
                  "<li>List point 3.</li>"
                  "<li>List point 4.</li>"
                  "<li>List point 5.</li>"
                  "</ul>",
    "list_output": "* List point 1.\n\n"
                   "* List point 2.\n\n"
                   "* List point 3.\n\n"
                   "* List point 4.\n\n"
                   "* List point 5.\n\n",

    "a_input": "<a href=\"https://example.com\">a tag with href</a>",
    "a_output": "[a tag with href](https://example.com)",

    "a_no_href_input": "<a>tag with no href</a>",
    "a_no_href_output": "tag with no href",

    "strong_input": "<strong>strong text</strong>",
    "strong_output": "**strong text**",

    "strong_inline_input": "<p>here is some text <strong>here is some strong text</strong> more text...</p>",
    "strong_inline_output": "here is some text **here is some strong text** more text...\n\n",

    "nested_types_input": "<li><p>Point 1 <strong>with strong</strong>...</p></li>"
                          "<li><p>Point 2 <strong>with strong</strong>...</p></li>"
                          "<li><p>Point 3 <strong>with strong</strong>...</p></li>",
    "nested_types_output": "* Point 1 **with strong**...\n\n"
                           "* Point 2 **with strong**...\n\n"
                           "* Point 3 **with strong**...\n\n",

    "blockquote_input": "<blockquote>"
                        "<li>p1</li>"
                        "<li>p2</li>"
                        "<li>p3</li>"
                        "</blockquote>",
    "blockquote_output": "> * p1\n\n"
                         "> * p2\n\n"
                         "> * p3\n\n",

}
