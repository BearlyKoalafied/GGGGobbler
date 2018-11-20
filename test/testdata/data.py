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
    "list_output": "\n\n* List point 1.\n\n"
                   "* List point 2.\n\n"
                   "* List point 3.\n\n"
                   "* List point 4.\n\n"
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
    "blockquote_output": "> * p1\n>\n"
                         "> * p2\n>\n"
                         "> * p3\n>\n",

    "nested_quote_input": "<blockquote>"
                          "<div class='bot'>"
                          "Nested blockquote"
                          "</div>"
                          "</blockquote>"
                          "unnested blockquote",
    "nested_quote_output": "> > Nested blockquote\n"
                           "> >\n"
                           "> unnested blockquote\n"
                           ">\n",
    "iframe_basic_input": "<iframe width=\"900\" height=\"506\" src=\"www.youtube.com/watch?v=sFumzUFaQvE\" frameborder=\"0\" allowfullscreen=\"\"></iframe>",
    "iframe_basic_output": "[Youtube Video](https://www.youtube.com/watch?v=sFumzUFaQvE)\n\n",
    "iframe_embed_input": "<iframe width=\"900\" height=\"506\" src=\"//www.youtube.com/embed/sFumzUFaQvE\" frameborder=\"0\" allowfullscreen=\"\"></iframe>",
    "iframe_embed_output": "[Youtube Video](https://www.youtube.com/watch?v=sFumzUFaQvE)\n\n",
    "complex_input": """<tr class="newsPost">
		            <td colspan="2"><div class="content">
<div class="lbox-container" style=""><div class="lbox"><div class="box-content s-pad">
<img src="https://web.poecdn.com/public/news/2018-03-24/news/BEChallengeRewardsHeader.jpg" alt="">
</div></div></div><div class="lbox-container" style=""><div class="lbox"><div class="box-content m-pad">
In the Bestiary League, you will have the option to complete 40 new challenges and earn exclusive microtransaction rewards! At 12, 24 and 36 challenges you will earn the Bestiary Helmet, Bestiary Wings and Bestiary Portal respectively. Completing challenges also grants you pieces of the Bestiary Totem Pole Hideout decoration.
<br><br>
<iframe width="900" height="506" src="//www.youtube.com/embed/J0v6IAnWvPk" frameborder="0" allowfullscreen="">
            </iframe>
<br><br>
Traditionally, we post the challenges alongside the rewards. This always puts us in an awkward situation because we try not to change stuff after it has been announced, but the final week before release is a critical period for fine-tuning and testing. We have decided not to announce the challenges before the league starts, so that the team have freedom to keep adjusting the challenges as final testing continues. This league's challenges follow a similar format to the ones you're familiar with, so there should be no unexpected surprises there.
<br><br>
You'll be able to check them out when you jump into Bestiary League on March 2nd!
</div></div></div></div></td>
</tr>
""",
    "complex_output": """> [Image Link](https://web.poecdn.com/public/news/2018-03-24/news/BEChallengeRewardsHeader.jpg)
>
> In the Bestiary League, you will have the option to complete 40 new challenges and earn exclusive microtransaction rewards! At 12, 24 and 36 challenges you will earn the Bestiary Helmet, Bestiary Wings and Bestiary Portal respectively. Completing challenges also grants you pieces of the Bestiary Totem Pole Hideout decoration.
>
> [Youtube Video](https://www.youtube.com/watch?v=J0v6IAnWvPk)
>
> Traditionally, we post the challenges alongside the rewards. This always puts us in an awkward situation because we try not to change stuff after it has been announced, but the final week before release is a critical period for fine-tuning and testing. We have decided not to announce the challenges before the league starts, so that the team have freedom to keep adjusting the challenges as final testing continues. This league's challenges follow a similar format to the ones you're familiar with, so there should be no unexpected surprises there.
>
> You'll be able to check them out when you jump into Bestiary League on March 2nd!
>
""",
    "complex_2_input": """<tr class="newsPost">
		            <td colspan="2"><div class="content">
<div class="lbox-container" style=""><div class="lbox"><div class="box-content s-pad">
<img src="https://web.poecdn.com/public/news/2018-01-25/3.1.3PatchHeader.jpg" alt="">
</div></div></div><div class="lbox-container" style=""><div class="lbox"><div class="box-content m-pad">
Tomorrow (Friday NZDT), we're planning to release Patch 3.1.3 which contains <a href="https://www.youtube.com/watch?v=cfk3-0Ds15c">a new, faster, Burning Ground effect</a> and some other high-priority bug fixes. As a preview to this update, we're making the patch notes available to share today.
<br><br><ul><li>We have made a new effect for Burning Ground which doesn't have the performance issues that the previous one did. While it has a few visual bugs still, we are releasing it for feedback and to get the improvement onto the realm as soon as possible. We plan to update the other ground effects in a similar way in the future.</li><li>Fixed a client crash that occurred when typing various symbols into the search box in the Map Stash Tab.</li><li>Fixed a client crash that occurred when right clicking on a Map Stash Tab if that tab was not already loaded.</li><li>Fixed a bug causing the effects for a skill in the High Templar Avarius encounter to not be displayed.</li><li>Fixed a bug where some Rogue Exiles were not counting towards the "Kill Rogue Exiles" challenge.</li><li>Fixed a bug where Desecrate cast by monsters would not create any corpses.</li><li>Fixed a bug where a Divine Vessel was incorrectly consumed if the Map boss was replaced by the Elder or an Elder Guardian.</li><li>Fixed a bug where Vaal Spectral Throw was not interacting correctly with the Volley Support gem.</li><li>Fixed a bug where the quest tracker was displaying incorrect quest information while in Maps.</li><li>Fixed a bug where the Twice Blessed Darkshrine effect was not always given to the player who clicked the Darkshrine.</li><li>Fixed a rare bug preventing some characters from completing the Lighting the Way quest.</li></ul>

</div></div></div></div></td>
		        </tr>""",
    "complex_2_output": """> [Image Link](https://web.poecdn.com/public/news/2018-01-25/3.1.3PatchHeader.jpg)
>
> Tomorrow (Friday NZDT), we're planning to release Patch 3.1.3 which contains [a new, faster, Burning Ground effect](https://www.youtube.com/watch?v=cfk3-0Ds15c) and some other high-priority bug fixes. As a preview to this update, we're making the patch notes available to share today.
>
> * We have made a new effect for Burning Ground which doesn't have the performance issues that the previous one did. While it has a few visual bugs still, we are releasing it for feedback and to get the improvement onto the realm as soon as possible. We plan to update the other ground effects in a similar way in the future.
>
> * Fixed a client crash that occurred when typing various symbols into the search box in the Map Stash Tab.
>
> * Fixed a client crash that occurred when right clicking on a Map Stash Tab if that tab was not already loaded.
>
> * Fixed a bug causing the effects for a skill in the High Templar Avarius encounter to not be displayed.
>
> * Fixed a bug where some Rogue Exiles were not counting towards the "Kill Rogue Exiles" challenge.
>
> * Fixed a bug where Desecrate cast by monsters would not create any corpses.
>
> * Fixed a bug where a Divine Vessel was incorrectly consumed if the Map boss was replaced by the Elder or an Elder Guardian.
>
> * Fixed a bug where Vaal Spectral Throw was not interacting correctly with the Volley Support gem.
>
> * Fixed a bug where the quest tracker was displaying incorrect quest information while in Maps.
>
> * Fixed a bug where the Twice Blessed Darkshrine effect was not always given to the player who clicked the Darkshrine.
>
> * Fixed a rare bug preventing some characters from completing the Lighting the Way quest.
>
""",
    "raw_embedded_video_input": """<video id="ascendancy-video" autoplay="" loop="" muted="" style="width: 100%;">
  <source src="//i.imgur.com/Ftma8bj.mp4?v=2" type="video/mp4">
</video>""",
    "raw_embedded_video_output": "[Embedded Video](i.imgur.com/Ftma8bj.mp4?v=2)\n\n"
}
