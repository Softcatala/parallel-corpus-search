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
    exit(1)


def main():

    print("Insert corpus")

    URL = 'http://localhost:9200' 
    wait_for_elastic_search(URL)

    es = Elasticsearch(URL, timeout=60)

    start_time = datetime.datetime.now()

    BULK_ITEMS = 10000
    bulk_buffer = 0
    bulk_insert = []

    with open("corpus.tsv", "r") as source:
        id = 1
        while True:

            src = source.readline().strip()

            if not src:
                break

            components = src.split("\t")
            doc = {
                '_index': "eng-cat",
                '_id': id,
                'src': components[0],
                'trg': components[1],
                'prio': int(components[2]),
                'license': components[3],
                'project': components[4],
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

            #if id > 10000:
            #    break

    res = es.indices.stats(index='eng-cat')
    docs = res['indices']['eng-cat']['primaries']['docs']['count']
    size_in_bytes = res['indices']['eng-cat']['primaries']['store']['size_in_bytes']
    size_in_GB = size_in_bytes / 1024/1024/1024

    s = 'Time used: {0}'.format(datetime.datetime.now() - start_time)
    print(f"documents indexed {docs}, size in bytes {size_in_bytes} ({size_in_GB:.2f} GB)")
    print(s)

if __name__ == "__main__":
    main()
