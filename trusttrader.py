import os
import sys
import csv
import argparse
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

DESCRIPTION = 'This script scrap trusttrader.com search, and save the companies details in a CSV file'

DEFAULT_SEARCH_URL = 'https://www.trustatrader.com/search?trade_name=Builder&search_trade_id=5b4cbdcb8811d346b846d974&location_str=Bury+St+Edmunds&lat=&lon=&trader=&search_trader_id='
BASE_URL = 'https://www.trustatrader.com'
SEARCH_RESULT_FILE = 'search_result.csv'


def get_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--url', type=str, default= DEFAULT_SEARCH_URL,
                        help="Trust trader search Url")

    parser.add_argument('--all_pages', action='store_true',
                        help="search all pages")

    parser.add_argument('--file_path', type=str,
                        help="Path where to save the search result CSV file")

    return parser


def get_html(my_url):
    try:
        # Make request
        uClient = uReq(my_url)

        page_html = uClient.read()

        uClient.close()
    except Exception as e:
        print(f"An error occured while making request: '{e}'")
        return None

    return page_html


def scrap_pages(my_url, all_pages=False):
    # Search first page
    main_page = get_html(my_url)

    if not main_page:
        return None

    try:
        main_page_soup = soup(main_page, "html.parser")
    except Exception as e:
        print(f"Could not parse the page: '{e}'")
        return None

    profiles = []
    page_search_result = scrap_trust_trader_page(main_page_soup)

    if not page_search_result:
        print("Could not find any result")
        return None

    for profile in page_search_result:
        profiles.append(profile)

    # Scrap all search result pages
    if all_pages:
        # Find next page link
        next_page = main_page_soup.find("a", {"class": "pagination__btn pagination__btn--next"} )
        if next_page:
            next_page_href = next_page.get("href")

        # Go through all pages
        while next_page:
            page_html = get_html(BASE_URL + next_page_href)
            page_soup = soup(page_html, "html.parser")

            page_search_result = scrap_trust_trader_page(page_soup)
            if page_search_result:
                for profile in page_search_result:
                    profiles.append(profile)

            next_page = page_soup.find("a", {"class": "pagination__btn pagination__btn--next"} )
            if next_page:
                next_page_href = next_page.get("href")
            else:
                break

    return profiles


def scrap_trust_trader_page(page_soup):
    search_page = page_soup.find("section", {"class": "main"})

    search_page_list = search_page.find("div", {"class": "search-page__list | profile-cards"})
    if not search_page_list:
        print("Invalid search")
        return None

    profile_cards_list = search_page_list.ul

    # Find all companies profile
    profile_cards = profile_cards_list.findAll("li", {"class": "profile-card"})

    page_profiles_search = []
    
    for profile_card in profile_cards:
        profile_card_content = profile_card.find("div", {"class": "profile-card__content"})

        profile_card_details = profile_card_content.find("div", {"class": "profile-card__details"})
        company_name = profile_card_details.h3.text.strip()

        tels = profile_card_content.ul.findAll("li", {"class": "profile-card__tel"})

        telephone_number = ""
        mobile_number = ""

        for tel in tels:
            if (tel.b.abbr.text == "Tel"):
                telephone_number = tel.span.text.strip()
            elif (tel.b.abbr.text == "Mob"):
                mobile_number = tel.span.text.strip()

        profile_page_link = profile_card_details.h3.a.get("href")   # Company profile page link
        profile_page_html = get_html(BASE_URL + profile_page_link)
        profile_page_soup = soup(profile_page_html, "html.parser")

        address_locality = ""
        post_code = ""

        profile_location_address = profile_page_soup.find("address", {"class": "profile-location__address"})

        # Some companies does not have address information
        if profile_location_address:
            address_locality = profile_location_address.find("span", {"itemprop": "addressLocality"}).text
            post_code = profile_location_address.b.text

        rating = profile_page_soup.find("span", {"class": "profile-rating__total-value"}).text

        page_profiles_search.append([company_name, telephone_number, mobile_number, address_locality, post_code, rating])

    return page_profiles_search
        

def main(args=None):
    parser = get_parser()
    args = parser.parse_args(args)

    # By deafult save in the project directory
    file_path = SEARCH_RESULT_FILE 

    if args.file_path:
        if not os.path.isdir(args.file_path):
            print(f"The directory: '{args.file_path}' does not exist")
            return False

        file_path = os.path.join(args.file_path + SEARCH_RESULT_FILE) 

    profiles = scrap_pages(args.url, all_pages=args.all_pages)

    if not profiles:
        print("Could not find any result")   
        return False

    try:  
        with open(file_path, 'w') as file:
            writer = csv.writer(file, delimiter = '\t')
            writer.writerow(["Company", "Telefone number", "Mobile number", "Location", "Post code", "rating"])

            for profile in profiles:
                writer.writerow(profile)
    except Exception as e:
        print(f"An error occured while writing to {file_path}: '{e}'")
        return False

    return True
    

if __name__ == '__main__':
    main(sys.argv[1:])