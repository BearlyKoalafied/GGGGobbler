
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
    # get number of pages from the page navbar
    soup = get_page_soup(thread_url)
    pagination = soup.find("div", {"class": "pagination"})
    page_buttons = pagination.find_all("a")

    target_button_contents = page_buttons[-1].contents[0]
    if target_button_contents == "Next":
        # there was a next button on this page.  Look at the previous button for page count!
        target_button_contents = page_buttons[-2].contents[0]
    return int(target_button_contents)


def get_staff_forum_posts(thread_url):
    """
    returns a list of BSoup div for each div that contains a staff post
    """
    posts = []
    page_count = get_page_count(thread_url)
    for i in range(1, page_count + 1):
        soup = get_page_soup(thread_url + "/page/" + str(i))
        # get the table of forum posts
        post_table = soup.find("table", class_="forumPostListTable")
        for row in post_table.find_all("tr"):
            # check whether this row is a staff post
            if row.has_attr("class") and row["class"][0] == "staff":
                html_content = row.find("td").find("div", {"class": "content"})
                posts.append(html_content)
    return posts


def convert_html_to_markdown(post_div):
    """
    returns a string containing markdown to represent the HTML markup of a given post
    """
    parts = post_div.contents
    markdown = ""
    for part in parts:
        # plain text content
        if isinstance(part, bs4.element.NavigableString):
            markdown += part
        # handle tags
        elif isinstance(part, bs4.element.Tag):
            # <a href> links
            if part.name == "a":
                contents = part.contents[0]
                link = part["href"]
                # text links
                if isinstance(contents, bs4.element.NavigableString):
                    text = str(contents.encode("utf-8"))
                    markdown += "[" + text + "]" + "(" + link + ")"
                # image links... idk it's probably an image I guess
                else:
                    markdown += "[\n\nImage\n\n]" + "(" + link + ")"

    return markdown
