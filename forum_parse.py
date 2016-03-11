import requests
import bs4
import re
from data_structs import StaffPost

def get_page_soup(page_url):
    """
    returns the soup object of the linked forum thread
    """
    page = requests.get(page_url)
    soup = bs4.BeautifulSoup(page.content.decode("utf-8", "ignore"), "html.parser")
    if forum_is_down(soup):
        raise PathofexileDownException("pathofexile.com is down for maintenance")
    return soup


def url_of_id(thread_id):
    return "https://www.pathofexile.com/forum/view-thread/" + thread_id

def filter_staff(thread_url):
    """
    Dirty and quick way to trim some stuff off the end of a url
    """
    if "/page" in thread_url:
        index = thread_url.rfind("/page")
    elif "#p" in thread_url:
        index = thread_url.rfind("#p")
    else:
        return thread_url + "/filter-account-type/staff"
    return thread_url[:index] + "/filter-account-type/staff"

def get_page_count(thread_url):
    """
    get number of pages from the page navbar
    """
    soup = get_page_soup(thread_url)
    pagination = soup.find("div", {"class": "pagination"})
    # apparently the pagination div will be present but empty if there are no staff posts and 1 page,
    # but is not present at all if there is 1 page and any staff posts.  Handling that here.
    if pagination is None or pagination.get_text() == "":
        return 1
    page_buttons = pagination.find_all("a")

    target_button_contents = page_buttons[-1].contents[0]
    if target_button_contents == "Next":
        # there was a next button on this page.  Look at the previous button for page count!
        target_button_contents = page_buttons[-2].contents[0]
    return int(target_button_contents)

def forum_is_down(page):
    down_header = page.find("h1", class_="topBar")
    return down_header is not None and down_header.get_text() == "Down For Maintenance"

def get_staff_forum_posts(thread_id, search_start=1):
    """
    returns:
        a list of StaffPosts for each post made by a staff member in the page
        the new page count value that has been searched to
    search_start is the page number to begin the search from
    """
    posts = []
    # forum has feature to only get staff posts from the thread
    page_count = get_page_count(filter_staff(url_of_id(thread_id)))
    for i in range(search_start, page_count + 1):
        soup = get_page_soup(filter_staff(url_of_id(thread_id)) + "/page/" + str(i))
        # get the table of forum rows
        post_table = soup.find("table", class_="forumPostListTable")
        for row in post_table.find_all("tr"):
            # if this row is one of the newspost details rows, ignore it
            if row.has_attr("class") and "newsPostInfo" in row["class"]:
                continue
            author = get_post_author_from_row(row)
            post_id = get_post_id_from_row(row)
            text = re.sub(r"[\n\r]+", "\n\n> ",
                          "> " + convert_html_to_markdown(get_post_from_row(row)))
            posts.append(StaffPost(post_id, thread_id, author, text))
    return posts, page_count

def get_post_from_row(post_row):
    """
    extracts the post body from a post row
    """
    return post_row.find("td").find("div", class_="content")

def get_post_author_from_row(post_row):
    """
    returns the name of the author of the post the given row from forumPostListTable contains
    """
    # news posts are wierd, author info is stored in a separate row
    if "newsPost" in post_row["class"]:
        info_row = post_row.parent.find("tr", class_="newsPostInfo")
        tag_contents = info_row.find("td") \
            .find("div", class_="posted-by") \
            .find("span", class_="profile-link") \
            .find("a").contents
    else:
        tag_contents = post_row.find("td", class_="post_info") \
            .find("div") \
            .find("div", class_="posted-by") \
            .find("span", class_="profile-link") \
            .find("a").contents
    # The challenges count image is in this <a> tag, but is missing if the user has zero challenges
    # Checking for that here
    if len(tag_contents) == 1:
        return tag_contents[0]
    else:
        return tag_contents[1]

def get_post_id_from_row(post_row):
    """
    returns the post id of the post
    """
    if "newsPost" in post_row["class"]:
        info_row = post_row.parent.find("tr", class_="newsPostInfo")
        # they moved it into a slightly different spot
        post_id = info_row.find("td") \
            .find("div", class_="posted-by")\
            .find("a", class_="posted-by-link").get("href")[1:]
    else:
        post_id = post_row.find("td", class_="post_info") \
            .find("div") \
            .find("div", class_="post_anchor").get("id")

    return post_id

def convert_html_to_markdown(html):
    """
    returns a string containing markdown to represent the HTML markup of a given post body's HTML contents
    """
    if isinstance(html, bs4.element.NavigableString):
        return html.strip()
    markdown = ""
    parts = html.contents
    for part in parts:
        if isinstance(part, bs4.element.NavigableString):
            if part.parent.name == "div" and "content" not in part.parent["class"]:
                markdown += part.strip() + "\n\n"
            else:
                markdown += part.strip()
        elif isinstance(part, bs4.element.Tag):
                if part.name == "div":
                    markdown += convert_html_to_markdown(part)
                elif part.name == "p":
                    markdown += convert_html_to_markdown(part)
                elif part.name == "br":
                    markdown += "\n\n"
                # lists
                elif part.name == "ul":
                    markdown += "\n\n"
                    for list_item in part.find_all("li"):
                        markdown += "* " + convert_html_to_markdown(list_item) + "\n\n"
                # headers
                elif part.name == "h2":
                    markdown += "## " + part.get_text() + "\n\n"
                # bold
                elif part.name == "strong":
                    markdown += "**" + part.get_text().rstrip(" ") + "**"
                # italics
                elif part.name == "em":
                    markdown += "*" + convert_html_to_markdown(part).rstrip(" ") + "*"
                # this is how the forum marks up underlines.  Markdown (for good enough reason)
                # doesn't have underlining syntax, so i'll put <strong> tags instead I guess
                elif part.name == "span" and part.has_attr("style") and part["style"][0] == "text-decoration: underline;":
                    markdown += "**" + part.get_text() + "**"
                elif part.name == "blockquote":
                    markdown += parse_quote(part)
                # <a href> links
                elif part.name == "a":
                    content = part.contents[0]
                    link = part["href"]
                    # image links... idk it's probably an image I guess
                    if isinstance(content, bs4.element.Tag) and content.name == "img":
                        # not sure what I should output so I guess I'll do this
                        text = "Graphic that links somewhere"
                        if content.has_attr("alt") and content["alt"] != "":
                            text = content["alt"]
                        markdown += "[" + text + "]" + "(" + link + ")"
                    else:
                        # text links
                        text = convert_html_to_markdown(content)
                        markdown += "[ " + text + " ]" + "(" + link + ")"
                elif part.name == "img":
                    markdown += "[Image Link]" + "(" + part["src"] + ")"
                # <iframe> tags.  I'm going to assume it's a youtube video and link it,
                # otherwise I'll ignore the tag
                elif part.name == "iframe":
                    src = part["src"]
                    if "youtube.com/embed" in src:
                        # get the video identifier
                        index = src.rfind("/")
                        video_id = src[index + 1:]
                        # make the youtube link
                        link = "https://youtube.com/watch?v=" + video_id
                        markdown += "[Youtube Video]" + "(" + link + ")"
    return markdown


def parse_quote(block_quote):
    """
    returns markdown for a blockquote element
    """
    markdown = "> "
    # just get the text body for now
    body = block_quote.find("div", class_="bot")
    markdown += convert_html_to_markdown(body)
    markdown = markdown.replace("\n", "\n> ")
    return markdown + "\n\n> "

class PathofexileDownException(Exception):
    """
    Exception thrown when Poe is down for maintenance
    """
    pass