from bs4 import BeautifulSoup, NavigableString, Tag
import re

ITEM_SEPARATOR = "\n\n"

def convert(html, parser='html.parser'):
    # filter out br tags because html.parser treats these incorrectly
    html = re.sub("<br\s*>", "<br/>", html)
    # remove whitespace from between tags
    soup = BeautifulSoup(re.sub(">\s*<", "><", html), parser)
    return process_tag(soup)


def process_tag(tag):
    output = []
    # convert children
    for child in tag.children:
        if isinstance(child, NavigableString):
            output += process_string(child)
        else:
            output += convert_tag(child)
    return "".join(output)


def convert_tag(tag):
    content_inside_this_tag = process_tag(tag)
    # tags that don't auto insert newline are processed first
    if tag.name == "a" and tag.has_attr("href"):
        return "[" + content_inside_this_tag + "]" + "(" + tag["href"] + ")"
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
        return ITEM_SEPARATOR + content_inside_this_tag
    elif is_excluded_tag(tag):
        return ""

    # tags below here insert a newline if not already inserted by previous call to convert_tag
    if tag.name == "p":
        output = content_inside_this_tag
    elif tag.name == "div":
        output = content_inside_this_tag
    elif tag.name == "h2":
        output = "## " + content_inside_this_tag
    elif tag.name == "h3":
        output = "### " + content_inside_this_tag
    elif tag.name == "li":
        output = "* " + content_inside_this_tag
    elif tag.name == "blockquote":
        output = process_quote_box(tag)
    elif tag.name == "iframe":
        output = process_iframe(tag)
    elif tag.name == "video":
        if tag.has_attr("src"):
            output = linkify("Embedded Video", tag["src"])
        elif tag.children is not None and tag.find("source").has_attr("src"):
            output = linkify("Embedded Video", tag.find("source")["src"])
        else:
            output = content_inside_this_tag
    else:
        # default case should be fine for remaining tags
        output = content_inside_this_tag
    if output[-len(ITEM_SEPARATOR):] != ITEM_SEPARATOR and output[-3:] != "\n>\n":
        output += ITEM_SEPARATOR
    return output


def process_string(nav_string):
    return nav_string

def process_strong(content):
    # get leading whitespace
    leading_whitespace = content[:len(content)-len(content.lstrip())]
    # get trailing whitespace
    trailing_whitespace = content[len(content.rstrip()):]
    return leading_whitespace + "**" + content.strip() + "**" + trailing_whitespace

def process_italics(content):
    # get leading whitespace
    leading_whitespace = content[:len(content)-len(content.lstrip())]
    # get trailing whitespace
    trailing_whitespace = content[len(content.rstrip()):]
    return leading_whitespace + "*" + content.strip() + "*" + trailing_whitespace

def process_img(img):
    text = "Image Link"
    # use alt text instead if available
    if img.has_attr("alt") and img["alt"]:
        text = img["alt"]
    link = img["src"]
    return linkify(text, link)

def process_code(tag):
    content = process_tag(tag)
    if len(content.split("\n"))  > 1:
        if content[0] != "\n":
            content = "\n" + content
        if content[-1] != "\n":
            content = content + "\n"
        return "```" + content + "```\n\n"
    else:
        return "`" + content + "`"

def process_quote_box(quotebox):
    for child in quotebox:
        if child.has_attr("class") and child["class"] == 'top':
            # author_info = "> " + child.find("a").
            pass
        elif child.has_attr("class") and child["class"] == 'bot':
            return quote_boxify(process_tag(child))
    return quote_boxify(process_tag(quotebox))

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
    return linkify(text, link)

def process_table(table):
    headers = get_table_headers(table)
    table_width = len(headers)
    rows = get_table_rows(table)
    header_line = "|".join(headers)
    header_underline = "-" + ("|-" * (table_width - 1))
    rows_concatenated = "\n".join(rows)
    return header_line + "\n" + header_underline + "\n" + rows_concatenated + "\n\n"

def get_table_headers(table):
    output = []
    for tag in table.children:
        if tag.name == "th":
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
            output.append("|".join(items))
        if tag.name == "tbody":
            output += (get_table_rows(tag))
    return output

def get_table_row_items(tr):
    output = []
    for tag in tr:
        # should all be td tags just containing text
        output.append(tag.text)
    return output

def quote_boxify(md):
    output = []
    for line in md.replace('\n>\n', ITEM_SEPARATOR).split(ITEM_SEPARATOR):
        line = line.strip()
        if line:
            blockquote_char_count = int(nested_level_of_line(line) + 1)
            newline_builder = []
            for i in range(blockquote_char_count):
                newline_builder.append("> ")
            newline_builder.append(line.strip('>').strip() + "\n")
            for i in range(blockquote_char_count):
                newline_builder.append("> ")
            # cut off extraneous space for compatibility
            newline_builder.pop()
            newline_builder.append(">\n")
            output.append("".join(newline_builder))
    return "".join(output)

def linkify(text, link):
    link = clear_leading_slashes_of_links(link)
    link_builder = list(link)
    escaped = ["(", ")"]
    for i in range(len(link_builder) - 1, -1, -1):
        if link_builder[i] in escaped:
            link_builder.insert(i, '\\')

    return "[" + text + "](" + "".join(link_builder) + ")"

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
