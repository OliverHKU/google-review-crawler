import json
import time

import requests

from bs4 import BeautifulSoup


def get_page_by_place_id(place_id: str):
    url = 'https://www.google.com/maps/place/?q=place_id:' + place_id
    rep = requests.get(url)
    time.sleep(1.17)
    return rep.content


def extract_data_list(content):
    soup = BeautifulSoup(content, 'html5lib')
    scripts = soup.find_all('script')
    for script in scripts:
        try:
            s = str(script.string).split('window.APP_INITIALIZATION_STATE=')[1]
            s = s.split('window.APP_FLAGS')[0][:-1]
            s = json.loads(s)
            # return s[3]
            return json.loads(s[3][6][5:])
        except:
            pass
    return None


def crawl(query="Pfalzwerke Charging Station", place_id='ChIJcWoZjChkmUcRUICHj5_I08U'):
    # c = get_page_by_query(query)
    c = get_page_by_place_id(place_id)
    data = extract_data_list(c)

    charging_outlets_data = data[6][140]
    opening_time_data = data[6][34]
    print(charging_outlets_data)
    print(opening_time_data)

    return charging_outlets_data, opening_time_data


if __name__ == '__main__':
    crawl()
