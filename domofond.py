from bs4 import BeautifulSoup
import lxml
import csv
import requests

domofond_url = "https://www.domofond.ru/prodazha-kvartiry-nizhniy_novgorod-c1023?Page="


def get_max_page() -> int:
    """
    Parse amount of pages at Domofond
    :return: Amount of Domofond pages
    """

    start_request = requests.get(domofond_url + "1", stream=True, allow_redirects=False).content
    domofond_soup = BeautifulSoup(start_request, "lxml")
    max_page = int(domofond_soup.find_all("li", {"class": "pagination__page___2dfw0"})[-1].text)
    return max_page


def info_handler(temp_info: str) -> (int or str, float, int, int):
    """
    Handles main info about each flat at Domofond - rooms amount, metres amount,
     flat's stage and all stages in flat's house
    :param temp_info:
    :type: str
    :returns: tuple of main flat's parameters - rooms amount, metres amount,
     flat's stage and all stages in flat's house
    """

    pre_info_list = temp_info.split(",")
    try:
        rooms_amount = int(pre_info_list[0].split("-")[0])
    except ValueError:
        rooms_amount = "Н/Д"
    metres_amount = float(pre_info_list[1].split()[0])
    current_stage = int(pre_info_list[2].split("/")[0])
    all_stages = int(pre_info_list[2].split("/")[1].split()[0])
    return rooms_amount, metres_amount, current_stage, all_stages


def parse_page(suggestion, link) -> tuple:
    """
    Parses additional information about each flat at Domofond - price,
    price per meter, flat's type, address and link
    :param suggestion: bs4 container with additional info of the flat
    :param link: link to each flat at Domofond
    :returns: tuple of main flat's parameters - price,
    price per meter, flat's type, address and link
    """

    temp_price = suggestion.find("div", {"class": "long-item-card__priceContainer___29DcY"}).text
    temp_price = int(temp_price.replace(" ", "").replace("₽", ""))
    temp_price_per_m = suggestion.find("div", {"class": "additional-price-info__additionalPriceInfo___lBqNv"}).text
    temp_price_per_m = float(temp_price_per_m.replace(" ", "").replace("₽зам²", ""))
    temp_info = suggestion.find("div", {"class": "long-item-card__informationHeaderRight___3bkKw"}).text
    temp_address = suggestion.find("span", {"class": "long-item-card__address___PVI5p"}).text
    temp_link = "https://www.domofond.ru" + link.get("href")
    return temp_price, temp_price_per_m, *info_handler(temp_info), temp_address, temp_link


def request_page(page: int):
    """
    Gets page with flats at Domofond
    :param page: number of the page
    :type page: int
    :returns: Content of the page
    """

    try:
        page_content = requests.get(domofond_url + str(page), stream=True, allow_redirects=False, timeout=1).content
    except:
        page_content = request_page(page)
    return page_content


def parse_pages(max_page: int) -> list:
    """
    Get main flat's parameters
    :param max_page: maximum number of page at Domofond
    :type max_page: int
    :returns: List with parsed data about each flat
    """

    domofond_list = []

    for page in range(1, max_page + 1):
        page_content = request_page(page)
        soup = BeautifulSoup(page_content, "lxml")
        suggestions_list = soup.find_all("div", {"class": "long-item-card__information___YXOtb"})
        links_list = soup.find_all("a", {"class": ["long-item-card__item___ubItG search-results__itemCardNotFirst___3fei6",
                                                   "long-item-card__item___ubItG"]})
        for index in range(len(suggestions_list)):
            domofond_list.append(parse_page(suggestions_list[index], links_list[index]))
        print(page, "/", max_page)
    return domofond_list


def main():
    """
    Parse all available flats at Domofond and save to CSV file
    """

    max_page = get_max_page()
    domofond_list = parse_pages(max_page)
    with open('some.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(domofond_list)


if __name__ == "__main__":
    main()
