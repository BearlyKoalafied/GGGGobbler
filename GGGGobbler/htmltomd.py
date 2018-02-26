from bs4 import BeautifulSoup, NavigableString, Tag
import re

def convert(html, parser='html.parser'):
    # filter out br tags because html.parser treats these incorrectly
    html = re.sub("<br\s*>", "<br/>", html)
    # remove whitespace from between tags
    soup = BeautifulSoup(re.sub(">\s*<","><", html), parser)

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
    # tags that don't auto insert newline first
    if tag.name == "a" and tag.has_attr("href"):
        return "[" + content_inside_this_tag + "]" + "(" + tag["href"] + ")"
    elif tag.name == "a":
        return content_inside_this_tag
    elif tag.name == "strong":
        return "**" + content_inside_this_tag + "**"
    elif tag.name == "em":
        return "*" + content_inside_this_tag + "*"
    elif tag.name == "img":
        text = "Image Link"
        # use alt text instead if available
        if tag.has_attr("alt") and tag["alt"]:
            text = tag["alt"]
        link = tag["src"]
        return "[" + text + "](" + link + ")"

    # tags below here insert a newline if not already inserted by previous call to convert_tag
    if tag.name == "p":
        output = content_inside_this_tag
    elif tag.name == "h2":
        output = "## " + content_inside_this_tag
    elif tag.name == "h3":
        output = "### " + content_inside_this_tag
    elif tag.name == "div":
        output = content_inside_this_tag
    elif tag.name == "li":
        output = "* " + content_inside_this_tag
    elif tag.name == "blockquote":
        output = quote_boxify(content_inside_this_tag)
    elif tag.name == "iframe":
        # these are used for youtube videos.  I'll make the text something else
        # if the src doesn't point to youtube
        if "youtube" in tag["src"]:
            text = "Youtube Video"
        else:
            text = "Embedded content"
        output = "[" + text + "](" + tag["src"] + ")"
    elif tag.name == "video":
        output = "[Embedded Video](" + tag["src"] + ")"
    else:
        # default case should be fine for remaining tags
        output = content_inside_this_tag
    if output[-2:] != "\n\n":
        output += "\n\n"
    return output


def process_string(nav_string):
    return nav_string


def quote_boxify(md):
    output = []
    for line in md.split("\n\n"):
        line = line.strip()
        if not line:
            continue
        output.append("> " + line + "\n\n")
    return "".join(output)


def contains_tags(tag):
    for child in tag:
        if isinstance(child, Tag):
            return True
    return False
