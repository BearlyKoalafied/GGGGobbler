import requests
import bs4


def get_page_soup(page_url):
    """
    returns the soup object of the linked forum thread
    """
    page = requests.get(page_url)
    soup = bs4.BeautifulSoup(page.content.decode("utf-8", "ignore"), "html.parser")
    return soup


def get_page_count(thread_url):
    """
    get number of pages from the page navbar
    """
    soup = get_page_soup(thread_url)
    pagination = soup.find("div", {"class": "pagination"})
    page_buttons = pagination.find_all("a")

    target_button_contents = page_buttons[-1].contents[0]
    if target_button_contents == "Next":
        # there was a next button on this page.  Look at the previous button for page count!
        target_button_contents = page_buttons[-2].contents[0]
    return int(target_button_contents)


def get_staff_forum_post_rows(thread_url, search_start=1):
    """
    returns a list of BSoup Table Rows for each tr that contains a staff post in the page
    search_start is the page nubmer to begin the search from
    """
    rows = []
    page_count = get_page_count(thread_url)
    for i in range(search_start, page_count + 1):
        soup = get_page_soup(thread_url + "/page/" + str(i))
        # get the table of forum rows
        post_table = soup.find("table", class_="forumPostListTable")
        for row in post_table.find_all("tr"):
            # check whether this row is a staff post
            if row.has_attr("class") and "staff" in row["class"]:
                rows.append(row)
    return rows


def get_post_from_row(post_row):
    """
    extracts the post body from a post row
    """
    return post_row.find("td").find("div", class_="content")


def get_news_post(page):
    """
    get_staff_forum_posts fetches plain staff posts, this fetches news posts which are formatted
    a little differently
    returns the div containing the news post body
    page should be the BSoup of the 1st page of a news post thread
    """
    return page.find("tr", class_="newsPost").find("td").find("div", class_="content")


def get_post_author_from_row(post_row):
    """
    returns the name of the author of the post the given row from forumPostListTable contains
    """
    tag_contents = post_row.find("td", class_="post_info")\
                    .find("div")\
                    .find("div", class_="posted-by")\
                    .find("span", class_="profile-link")\
                    .find("a").contents
    # The challenges count image is in this <a> tag, but is missing if the user has zero challenges
    # Checking for that here
    if len(tag_contents) == 1:
        return tag_contents[0]
    else:
        return tag_contents[1]


def convert_html_to_markdown(html):
    """
    returns a string containing markdown to represent the HTML markup of a given post body's HTML contents
    """
    markdown = ""
    parts = html.contents
    for part in parts:
        if isinstance(part, bs4.element.NavigableString):
            markdown += part
        elif isinstance(part, bs4.element.Tag):
            if part.name == "strong":
                markdown += "**" + part.get_text() + "**"
            elif part.name == "em":
                markdown += "*" + part.get_text() + "*"
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
                # text links
                if isinstance(content, bs4.element.NavigableString):
                    text = str(content.encode("utf-8"))
                    markdown += "[" + content + "]" + "(" + link + ")"
                # image links... idk it's probably an image I guess
                else:
                    text = "Image"
                    if content.has_attr("alt"):
                        text = content["alt"]
                    markdown += "[" + text + "]" + "(" + link + ")"
            # <iframe> tags.  I'm going to assume it's a youtube video and link it,
            # otherwise I'll ignore the tag
            elif part.name == "iframe":
                src = part["src"]
                if "youtube.com/embed" in src:
                    # get the video identifier
                    index = src.rfind("/")
                    video_id = src[index+1:]
                    # make the youtube link
                    link = "https://youtube.com/watch?v=" + video_id
                    markdown += "[Youtube Video]" + "(" + link + ")"
    return markdown

def parse_quote(block_quote):
    """
    returns markdown for a blockquote element
    """
    markdown = " > "
    # just get the text body for now
    body = block_quote.find("div", class_="bot")
    markdown += convert_html_to_markdown(body)
    return markdown