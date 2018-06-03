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
    elif tag.name == "strong":
        return "**" + content_inside_this_tag + "**"
    elif tag.name == "span":
        return content_inside_this_tag
    elif tag.name == "em":
        return "*" + content_inside_this_tag + "*"
    elif tag.name == "img":
        return process_img(tag)
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
            output = "[Embedded Video](" + tag["src"] + ")"
        elif tag.children is not None and tag.find("source").has_attr("src"):
            output = "[Embedded Video](" + tag.find("source")["src"] + ")"
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


def process_img(img):
    text = "Image Link"
    # use alt text instead if available
    if img.has_attr("alt") and img["alt"]:
        text = img["alt"]
    link = img["src"]
    return "[" + text + "](" + link + ")"

def process_quote_box(quotebox):
    for child in quotebox:
        if child.has_attr("class") and child["class"] == 'top':
            # author_info = "> " + child.find("a").
            pass
        if child.has_attr("class") and child["class"] == 'bot':
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
    return "[" + text + "](" + link + ")"

def quote_boxify(md):
    output = []
    for line in md.split(ITEM_SEPARATOR):
        line = line.strip()
        if line:
            output.append("> " + line + "\n>\n")
    return "".join(output)

def contains_tags(tag):
    for child in tag:
        if isinstance(child, Tag):
            return True
    return False

def is_excluded_tag(tag):
    # I don't know why these are here but I'm ignoring them
    excluded = ['noscript', 'style']
    return tag.name in excluded
