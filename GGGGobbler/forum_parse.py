import re
import datetime
import requests
import bs4

from db.data_structs import StaffPost
from GGGGobbler import htmltomd
from config import settings


def get_page_soup(page_url):
    """
    returns the soup object of the linked forum thread
    """
    page = requests.get(page_url)
    soup = bs4.BeautifulSoup(page.content.decode("utf-8", "ignore"), "html5lib")
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
        if post_table is None:
            # catch all for cases where the page returns something that isn't a forum post list
            # for whatever reason
            return [], 0
        for row in post_table.find_all("tr"):
            # ignore if this isn't a staff post at all (I've seen this for poll threads)
            if not row.has_attr("class"):
                continue
            # if this row is one of the newspost details rows, ignore it
            if "newsPostInfo" in row["class"]:
                continue
            author = get_post_author_from_row(row)
            post_id = get_post_id_from_row(row)
            # convert the retrieved html into markdown
            text = htmltomd.quote_boxify(htmltomd.convert(str(get_post_from_row(row))))
            post_date = get_post_date_from_row(row)
            # a bug in the website sometimes causes 2 pages of forum posts to return the same forum post
            if not check_for_duplicate(posts, post_id):
                posts.append(StaffPost(post_id, thread_id, author, text, post_date))
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
    # news posts are weird, author info is stored in a separate row
    if "newsPost" in post_row["class"]:
        info_row = post_row.parent.find("tr", class_="newsPostInfo")
        profile_link = info_row.find("td") \
            .find("div", class_="posted-by") \
            .find("span", class_="profile-link")
    else:
        profile_link = post_row.find("td", class_="post_info") \
            .find("div") \
            .find("div", class_="posted-by") \
            .find("span", class_="profile-link")
    # check for deleted profile link
    if profile_link.find("span" , class_="deleted") is not None:
        return "Deleted"
    tag_contents = profile_link.find("a").contents
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
                      .find("div", class_="posted-by") \
                      .find("a", class_="posted-by-link").get("href")[1:]
    else:
        post_id = post_row.find("td", class_="post_info") \
            .find("div") \
            .find("div", class_="post_anchor").get("id")

    return post_id


def get_post_date_from_row(post_row):
    """
    returns the date of the post
    """
    if post_row.has_attr("class") and "newsPost" in post_row["class"]:
        info_row = post_row.parent.find("tr", class_="newsPostInfo")
        str_date = info_row.find("td") \
            .find("div", class_="posted-by") \
            .find("span", class_="post_date").get_text()
    else:
        str_date = post_row.find("td", class_="post_info") \
            .find("div") \
            .find("div", class_="posted-by") \
            .find("span", class_="post_date").get_text()
    # convert to GMT+0 timezone
    format = "%b %d, %Y, %I:%M:%S %p"
    date = datetime.datetime.strptime(str_date, format)
    date = date + datetime.timedelta(hours=-settings.TIMEZONE_OFFSET)
    str_date = date.strftime(format)
    return str_date


def check_for_duplicate(posts, post_id):
    """
    fix duplicate posts in a list of posts
    returns true if post_id is in posts
    """
    for post in posts:
        if post_id == post.post_id:
            return True
    return False


class PathofexileDownException(Exception):
    """
    Exception thrown when Poe is down for maintenance
    """
    pass
