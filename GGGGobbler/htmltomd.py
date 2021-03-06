from bs4 import BeautifulSoup, NavigableString, Tag
import re

from GGGGobbler import markdown as md

ITEM_SEPARATOR = "\n\n"

def convert(html, parser='html.parser'):
    # filter out br tags because html.parser treats these incorrectly
    html = re.sub("<br\s*>", "<br/>", html)
    # remove whitespace from between tags
    soup = BeautifulSoup(re.sub(">\s*<", "><", html), parser)
    comment = md.MarkdownDocument()
    comment.add(process_tag(soup))
    return str(comment)


def process_tag(tag):
    output = []
    # convert children
    for child in tag.children:
        if isinstance(child, NavigableString):
            output.append(process_string(child))
        else:
            output.append(str(convert_tag(child)))
    return "".join(output)


def convert_tag(tag):
    content_inside_this_tag = process_tag(tag)
    # tags that don't auto insert newline are processed first
    if tag.name == "a" and tag.has_attr("href"):
        return md.MarkdownLink(content_inside_this_tag, tag["href"])
    elif tag.name == "a":
        return content_inside_this_tag
    # these can be handled the same as far as I can tell
    elif tag.name == "code" or tag.name == "pre":
        return process_code(tag)
    elif tag.name == "strong":
        return process_strong(content_inside_this_tag)
    elif tag.name == "span":
        return content_inside_this_tag
    elif tag.name == "em":
        return process_italics(content_inside_this_tag)
    elif tag.name == "img":
        return process_img(tag)
    elif tag.name == "table":
        return process_table(tag)
    elif tag.name == "ul":
        temp = ITEM_SEPARATOR + content_inside_this_tag
        if len(temp) > 2 and temp[-2:] != "\n\n":
            temp += "\n"
        return temp
    elif tag.name == "br":
        return "\n\n"
    elif is_excluded_tag(tag):
        return ""

    # tags below here insert a newline if not already inserted by previous call to convert_tag
    if tag.name == "p":
        output = md.MarkdownParagraph(content_inside_this_tag)
    elif tag.name == "div":
        output = md.MarkdownParagraph(content_inside_this_tag)
    elif tag.name == "h2":
        output = md.MarkdownHeader(content_inside_this_tag, 2)
    elif tag.name == "h3":
        output = md.MarkdownHeader(content_inside_this_tag, 3)
    elif tag.name == "li":
        output = md.MarkdownListItem(content_inside_this_tag)
    elif tag.name == "blockquote":
        output = process_quote_box(tag, content_inside_this_tag)
    elif tag.name == "iframe":
        output = process_iframe(tag)
    elif tag.name == "video":
        if tag.has_attr("src"):
            output = str(md.MarkdownLink("Embedded Video", tag["src"])) + ITEM_SEPARATOR
        elif tag.children is not None and tag.find("source").has_attr("src"):
            output = str(md.MarkdownLink("Embedded Video", tag.find("source")["src"])) + ITEM_SEPARATOR
        else:
            output = md.MarkdownParagraph(content_inside_this_tag)
    else:
        # default case should be fine for remaining tags
        output = content_inside_this_tag
    #if isinstance(output, md.MarkdownQuotebox) and len(output.items) == 3 and "Level 1 Cast when" in output.items[0]:
    #    print(output.items)
    return output


def process_string(nav_string):
    return nav_string

def process_strong(content):
    return md.MarkdownStrong(content)

def process_italics(content):
    return md.MarkdownItalics(content)

def process_img(img):
    # use alt text instead if available
    if img.has_attr("alt") and img["alt"]:
        text = img["alt"]
    else:
        text = "Image Link"
    link = img["src"]
    return md.MarkdownLink(text, link)

def process_code(tag):
    content = process_tag(tag)
    split_content = content.splitlines()
    if len(split_content) > 1:
        return md.MarkdownCodeBlock(content)
    else:
        return md.MarkdownCodeSpan(content)

def process_quote_box(quotebox, content):
    md_quote = md.MarkdownQuotebox()
    md_quote.add(content)
    return md_quote

def process_iframe(iframe):
    # these are used for youtube videos.  I'll make the text something else
    # if the src doesn't point to youtube
    src = iframe["src"]
    if "youtube" in src:
        text = "Youtube Video"
    else:
        text = "Embedded content"
    # do some filtering for different kinds of youtube links
    id_indicators = ["youtube.com/embed/", "youtube.com/watch?v="]
    video_id = ""
    for indic in id_indicators:
        if src.find(indic) != -1:
            video_id = src[src.find(indic) + len(indic):]

    if video_id:
        link = "https://www.youtube.com/watch?v=" + video_id
    else:
        link = src
    return str(md.MarkdownLink(text, link)) + ITEM_SEPARATOR

def process_table(table):
    headers = get_table_headers(table)
    rows = get_table_rows(table)
    return md.MarkdownTable(rows, headers)

def get_table_headers(table):
    output = []
    for tag in table.children:
        if tag.name == "th" or tag.name == "td":
            output.append(process_string(tag.text))
        else:
            output += (get_table_headers(tag))
            # if we found any headers, we can return immediately
            if len(output) > 0:
                return output
    return output

def get_table_rows(table):
    output = []
    for tag in table.children:
        if tag.name == "tr":
            items = get_table_row_items(tag)
            output.append(items)
        if tag.name == "tbody":
            output += (get_table_rows(tag))
    return output

def get_table_row_items(tr):
    output = []
    for tag in tr:
        # should all be td tags just containing text
        output.append(tag.text)
    return output

def quote_boxify(content):
    quotebox = md.MarkdownQuotebox()
    quotebox.add(content)
    return str(quotebox)

def contains_tags(tag):
    for child in tag:
        if isinstance(child, Tag):
            return True
    return False

def is_excluded_tag(tag):
    # I don't know why these are here but I'm ignoring them
    excluded = ['noscript', 'style']
    return tag.name in excluded

def nested_level_of_line(line):
    if len(line) < 2:
        return False
    index = 0
    while line[index:index+2] == "> ":
        index += 2
    return index / 2

def clear_leading_slashes_of_links(url):
    if len(url) == 0 or url[0] != "/":
        return url
    while url[0] == "/":
        url = url[1:]
    return "https://" + url
