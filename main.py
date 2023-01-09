import csv
import json
import time

import requests

from bs4 import BeautifulSoup


def process_query(query):
    return query.replace(" ", "+")


def get_page_by_query(query="aspria berlin ku'damm"):
    url = "https://www.google.com/maps/search/" + process_query(query)
    rep = requests.get(url)
    return rep.content


def extract_bytes(content):
    soup = BeautifulSoup(content, "html5lib")
    scripts = soup.find_all("script")
    b = ""
    n = []
    for script in scripts:
        try:
            s = str(script.string).split("window.APP_OPTIONS=")[1]
            s = s.split(";")[0]
            s = json.loads(s)
            b = s[11]
        except:
            pass
        try:
            s = str(script.string).split("window.APP_INITIALIZATION_STATE=")[1]
            s = s.split("window.APP_FLAGS")[0][:-1]
            s = json.loads(s)
            n = s[2][3][0][4][0][0]
        except:
            pass
    return b, n


def extract_review_page(b, n, after_id=""):
    after_id_part = "" if not after_id else "3s" + after_id
    url = f"https://www.google.com/maps/preview/review/listentitiesreviews?authuser=0&hl=en&gl=hk&pb=!1m2!1y{n[0]}!2y{n[1]}!2m1!2i10!{after_id_part}3e1!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1s{b}A0!7e81"
    rep = requests.get(url)
    reviews = json.loads(rep.content[5:])[2]
    return [
        {
            "reviewer_name": review[0][1],
            "content": review[3],
            "full_url": review[18],
            "rating": int(review[4]) if review[4] else 0,
            "time": review[1],
            "owner_replied": bool(review[9]),
            "owner_reply": "" if not bool(review[9]) else review[9][1],
        }
        for review in reviews if review
    ], reviews[-1][61] if reviews and len(reviews[-1]) > 61 else None


def extract_all_reviews(b, n):
    reviews = []
    after_id = ""
    counter = 1
    try:
        while True:
            new_page, next_after_id = extract_review_page(b, n, after_id)
            reviews.extend(new_page)
            print(f'Got page number {counter} with {len(new_page)} reviews.')
            if not next_after_id:
                break
            time.sleep(1)
            counter += 1
            after_id = next_after_id
    except Exception as e:
        raise e
    finally:
        return reviews


def export_to_csv(reviews, file_name='result.csv'):
    if not reviews:
        return
    keys = reviews[0].keys()
    with open(file_name, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(reviews)


def crawl(query="aspria berlin ku'damm"):
    c = get_page_by_query(query)
    b, n = extract_bytes(c)
    reviews = extract_all_reviews(b, n)
    export_to_csv(reviews)
    return reviews
