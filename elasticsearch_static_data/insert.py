from elasticsearch import Elasticsearch
from elasticsearch import helpers
from urllib.request import Request, urlopen
import time
import datetime


def check_link(url):
    try:
        req = Request(url)
        urlopen(req, timeout=60)
        return True

    except Exception:
        return False

def wait_for_elastic_search(url):
    TIME_SECS = 3 * 60
    STEPS = 10

    waited = 0
    while waited < TIME_SECS:
        if check_link(url):
            print("URL is ready")
            return

        print("Waiting for URL to be ready")
        time.sleep(STEPS)
        waited += STEPS

    print(f"Server {url} is not ready after {TIME_SECS} seconds")
    exit(0)


def main():

    print("Insert corpus")

    URL = 'http://localhost:9200'
    wait_for_elastic_search(URL)

    es = Elasticsearch(URL, timeout=60)

    start_time = datetime.datetime.now()

    BULK_ITEMS = 100000
    bulk_buffer = 0
    bulk_insert = []

    with open("src.txt", "r") as source, open("tgt.txt", "r") as target:
        id = 1
        while True:

            src = source.readline()
            trg = target.readline()

            if not (src and trg):
                break

            doc = {
                'author': 'author_name',
                '_index': "eng-cat",
                '_id': id,
                'src': src,
                'trg': trg,
                'timestamp': datetime.datetime.now()
            }

            bulk_insert.append(doc)
            id += 1
            bulk_buffer += 1

            if bulk_buffer <= BULK_ITEMS:
                continue

            helpers.bulk(es, bulk_insert)
            bulk_buffer = 0
            bulk_insert = []

            print(f"Inserted {id}")

    s = 'Time: {0}'.format(datetime.datetime.now() - start_time)
    print(s)


if __name__ == "__main__":
    main()
