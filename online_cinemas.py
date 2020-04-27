from bs4 import BeautifulSoup, SoupStrainer
import lxml
import requests


baskino_url = "http://baskino.me/index.php?do=search"
kinokrad_url = "https://kinokrad.co"


def parse_player_page(page_url: str) -> str or False:
    """
    Parses film link to player from Baskino
    :param page_url: url of fikm in Baskino site
    :type: str
    :returns: Link to player with film from Baskino or False (in site error case)
    """

    try:
        baskino_request = requests.get(page_url, stream=True, allow_redirects=False, timeout=1).content
        only_div_tags = SoupStrainer("div", {"id": "player-holder-1"})
        baskino_soup = BeautifulSoup(baskino_request, "lxml", parse_only=only_div_tags)
        baskino_url_list = baskino_soup.find_all("div", {"id": "player-holder-1"})
        player_url = baskino_url_list[0].get("data-url")
        return player_url
    except Exception:
        return False


def parse_page_baskino(page_url: str) -> str:
    """
    Parses direct link to film from Baskino
    :param page_url: Baskino player's link with needed film
    :returns: Link to video in the best quality (720p max) or error string
    """

    player_url = parse_player_page(page_url)

    if player_url:
        try:
            film_request = requests.get(player_url, stream=True, allow_redirects=False, timeout=1).content
            only_script_tags = SoupStrainer("script")
            film_soup = BeautifulSoup(film_request, "lxml", parse_only=only_script_tags)
            film_url_list = film_soup.find_all("script")
            film_script = str(film_url_list[3])

            film_url = "Не найдено"

            for line in film_script.split():
                if "720.mp4'" in line:
                    film_url = line[:-1]
                elif "480.mp4'" in line and film_url == "Не найдено":
                    film_url = line[:-1]
                elif "360.mp4'" in line and film_url == "Не найдено":
                    film_url = line[:-1]
            return film_url

        except Exception:
            return "Ошибка сайта"
    else:
        return "Некорректный сайт."


def parse_page_kinokrad(page_url: str) -> str:
    """
    Parses direct link to film from Kinokrad
    :param page_url: Baskino player's link with needed film
    :returns: Link to video in the best quality (720p max) or error string
    """

    film_request = requests.get(page_url, stream=True, allow_redirects=False, timeout=1).content
    only_script_tags = SoupStrainer("script")
    film_soup = BeautifulSoup(film_request, "lxml", parse_only=only_script_tags)
    film_url_list = film_soup.find_all("script")
    film_script = " ".join([str(film) for film in film_url_list])
    for line in film_script.split("\""):
        if ".m3u8" in line:
            return line


def parse_baskino(search_query: str) -> str:
    """
    Handles search query to Baskino
    :param search_query: search query from user
    :returns: direct link to film in best quality or error string
    """

    search_list = []
    old_search_links = []
    start_counter = 1

    while True:
        searh_request = requests.post(url=baskino_url,
                                      data={
                                          "do": "search",
                                          "subaction": "search",
                                          "actors_only": "0",
                                          "search_start": str(start_counter),
                                          "full_search": "0",
                                          "result_from": "1",
                                          "story": str(search_query)
                                      }).text
        only_a_tags = SoupStrainer("a")
        search_soup = BeautifulSoup(searh_request, "lxml", parse_only=only_a_tags)
        search_links = search_soup.find_all("a")
        if search_links != old_search_links:
            old_search_links = search_links

            for link in search_links:
                if "http://baskino.me/" in str(link) and ".html" in str(link) and link.text.strip():
                    search_list.append((link.get("href"), link.text))

            start_counter += 1
        else:
            break
    if search_list:
        result_list = []

        for pair in search_list:
            if search_query.lower() in pair[1].lower() and not pair[1].startswith("Сериал "):
                film_url = parse_page_baskino(pair[0])
                film_title = pair[1]
                if "https://" in film_url:
                    result_list.append((film_url, film_title))

        if result_list:
            result_text = "".join('<a href="{}">{}</a>\n'
                                  .format(film[0],
                                          film[1], )
                                  for film in result_list)
        else:
            result_text = "Нет результатов поиска."
    else:
        result_text = "Некорректный запрос или фильма не существует на сайте."
    return result_text


def parse_kinokrad(search_query: str) -> str:
    """
    Handles search query to Kinokrad
    :param search_query: search query from user
    :returns: direct link to film in best quality or error string
    """

    search_list = []

    searh_request = requests.post(url=kinokrad_url,
                                  data={
                                      "MIME Type": "application/x-www-form-urlencoded",
                                      "do": "search",
                                      "subaction": "search",
                                      "story": str(search_query),
                                      "x": "0",
                                      "y": "0"
                                  }).text

    only_a_tags = SoupStrainer("a")
    search_soup = BeautifulSoup(searh_request, "lxml", parse_only=only_a_tags)
    search_links = search_soup.find_all("a")

    for link in search_links:
        if "https://kinokrad.co/" in str(link) and ".html" in str(link) and link.text.strip():
            search_list.append((link.get("href"), link.text.replace("\xa0", " ")))
    if search_list:
        result_list = []

        for pair in search_list:
            if search_query.lower() in pair[1].lower() and "сезон)" not in pair[1]:
                film_url = parse_page_kinokrad(pair[0])
                film_title = pair[1]
                if "https://" in film_url:
                    result_list.append((film_url, film_title))

        if result_list:
            result_text = "".join('<a href="{}">{}</a>\n'
                                  .format(film[0],
                                          film[1], )
                                  for film in result_list)
        else:
            result_text = "Нет результатов поиска."
    else:
        result_text = "Некорректный запрос или фильма не существует на сайте."
    return result_text


def parse_search(search_query: str) -> (str, str):
    """
    Get direct links to films from Baskino and Kinokrad
    :param search_query: film user request
    :returns: direct link to films by search request / error string(s)
    """

    baskino_result = parse_baskino(search_query)
    kinokrad_result = parse_kinokrad(search_query)
    return baskino_result, kinokrad_result


if __name__ == "__main__":
    parse_search("test")
