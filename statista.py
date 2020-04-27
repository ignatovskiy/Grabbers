import requests
from bs4 import BeautifulSoup, SoupStrainer


statista_url = "https://www.statista.com/chartoftheday/ALL/p/1/"


def read_last() -> list:
    """
    Reads last 10 statista posts' ids from dump file
    :return: List with posts' ids from dump file
    """

    readed_lines = []
    with open("dump_statista.txt", "r", encoding="UTF-8") as f:
        for line in f.readlines():
            readed_lines.append(line.replace("\n", ""))
    return readed_lines


def write_new(new_ids: list):
    """
    Writes new 10 statista posts' ids
    :param new_ids: ids of new 10 posts from statista
    :type new_ids: list
    """
    with open("dump_statista.txt", "w", encoding="UTF-8") as f:
        for line in new_ids:
            f.write(line + "\n")


def parse_statista_links() -> list:
    """
    Parse 10 new links to statista posts from main statista page
    :return: List with 10 links to statista posts
    """

    request_statista = requests.get(statista_url)
    statista_page = request_statista.content
    statista_soup = BeautifulSoup(statista_page, "lxml", parse_only=SoupStrainer('a'))
    statista_links = statista_soup.find_all("a", {"class": "panelBox__coverLink"})[:10]

    return statista_links


def main() -> list or False:
    """
    Handles 10 new posts from statista
    :return: List of new statista posts' ids or False (if there are no new posts)
    """

    statista_links = parse_statista_links()

    statista_ids = [link.get("href")[7:12] for link in statista_links]
    old_ids = read_last()
    new_ids = [element for element in statista_ids if element not in old_ids]

    write_new(statista_ids)

    if new_ids:
        return ["https://cdn.statcdn.com/Infographic/images/normal/{}.jpeg".format(id_) for id_ in statista_ids]
    else:
        return False


if __name__ == "__main__":
    main()
