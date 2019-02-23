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
    "list_output": "\n\n* List point 1.\n"
                   "* List point 2.\n"
                   "* List point 3.\n"
                   "* List point 4.\n"
                   "* List point 5.\n\n",

    "a_input": "<a href=\"https://example.com\">a tag with href</a>",
    "a_output": "[a tag with href](https://example.com)",

    "a_no_href_input": "<a>tag with no href</a>",
    "a_no_href_output": "tag with no href",

    "italics_input": "<em>italics text</em>",
    "italics_output": "*italics text*",

    "italics_whitespace_input": "<em>italics with space at end </em>",
    "italics_whitespace_output": "*italics with space at end* ",

    "italics_inline_input": "<p>here is some text <em>here is some more italicised text</em> more text...</p>",
    "italics_inline_output": "here is some text *here is some more italicised text* more text...\n\n",

    "strong_input": "<strong>strong text</strong>",
    "strong_output": "**strong text**",

    "strong_whitespace_input": "<strong>The realm goes down and patching begins at: </strong>",
    "strong_whitespace_output": "**The realm goes down and patching begins at:** ",

    "strong_inline_input": "<p>here is some text <strong>here is some strong text</strong> more text...</p>",
    "strong_inline_output": "here is some text **here is some strong text** more text...\n\n",

    "img_input":'<img src="https://www.example.com/2.jpg" alt="">',
    "img_output":"[Image Link](https://www.example.com/2.jpg)",

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
    "blockquote_output": "> * p1\n"
                         "> * p2\n"
                         "> * p3\n\n",

    "nested_quote_input": "<blockquote>"
                          "<blockquote>"
                          "<div class='bot'>"
                          "Nested blockquote"
                          "</div>"
                          "</blockquote>"
                          "unnested blockquote"
                          "</blockquote>",
    "nested_quote_output": "> > Nested blockquote\n"
                           "> > \n"
                           "> \n"
                           "> unnested blockquote\n"
                           "\n",
    "iframe_basic_input": "<iframe width=\"900\" height=\"506\" src=\"www.youtube.com/watch?v=sFumzUFaQvE\" frameborder=\"0\" allowfullscreen=\"\"></iframe>",
    "iframe_basic_output": "[Youtube Video](https://www.youtube.com/watch?v=sFumzUFaQvE)\n\n",
    "iframe_embed_input": "<iframe width=\"900\" height=\"506\" src=\"//www.youtube.com/embed/sFumzUFaQvE\" frameborder=\"0\" allowfullscreen=\"\"></iframe>",
    "iframe_embed_output": "[Youtube Video](https://www.youtube.com/watch?v=sFumzUFaQvE)\n\n",

    "raw_embedded_video_input": """<video id="ascendancy-video" autoplay="" loop="" muted="" style="width: 100%;">
  <source src="//i.imgur.com/Ftma8bj.mp4?v=2" type="video/mp4">
</video>""",
    "raw_embedded_video_output": "[Embedded Video](https://i.imgur.com/Ftma8bj.mp4?v=2)\n\n"
}
