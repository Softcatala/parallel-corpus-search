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

def create_index(es, index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)

    settings = {
        "analysis": {
          "filter": {
            "catalan_elision": {
              "type":       "elision",
              "articles":   [ "d", "l", "m", "n", "s", "t"],
              "articles_case": True
            },
            "catalan_stop": {
              "type":       "stop",
              "stopwords":  "_catalan_"
            },
            "catalan_keywords": {
              "type":       "keyword_marker",
              "keywords":   ["example"]
            },
            "catalan_stemmer": {
              "type":       "stemmer",
              "language":   "catalan"
            }
          },
          "analyzer": {
            "rebuilt_catalan": {
              "tokenizer":  "standard",
              "filter": [
                "catalan_elision",
                "lowercase",
                "asciifolding",
#                "catalan_stop",
#                "catalan_keywords",
#                "catalan_stemmer"
              ]
            }
          }
        }
    }

    es.indices.create(index=index_name, ignore=400, settings=settings)

    mappings = {
          "properties": {
            "trg": {
              "type": "text",
              "fields": {
                  "keyword": {
                        "type": "keyword",
                        "ignore_above": "256"
                   }
              },
              "analyzer": "rebuilt_catalan"
            }
        }
    }

    es.indices.put_mapping(index=index_name,body=mappings)

def main():

    print("Insert corpus")

    URL = 'http://localhost:9200' 
    wait_for_elastic_search(URL)

    es = Elasticsearch(URL, request_timeout=60)

    start_time = datetime.datetime.now()

    BULK_ITEMS = 10000
    bulk_insert = []

    create_index(es, "eng-cat")
    with open("corpus.tsv", "r") as source:
        id = 1
        while True:

            src = source.readline().strip()

            if len(bulk_insert) >= BULK_ITEMS or not src:
                helpers.bulk(es, bulk_insert, refresh=False)
                seconds = (datetime.datetime.now() - start_time).total_seconds()
                itemssec = id / seconds if seconds > 0 else 1
                print(f"Items inserted {id} - {itemssec:.2f} items/s")
                bulk_insert = []

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

            #if id > 10000:
            #    break

    es.indices.refresh(index='eng-cat')
    res = es.indices.stats(index='eng-cat')
    docs = res['indices']['eng-cat']['total']['docs']['count']
    size_in_bytes = res['indices']['eng-cat']['primaries']['store']['size_in_bytes']
    size_in_GB = size_in_bytes / 1024/1024/1024

    s = 'Time used: {0}'.format(datetime.datetime.now() - start_time)
    print(f"documents indexed {docs}, size in bytes {size_in_bytes} ({size_in_GB:.2f} GB)")
    print(s)

if __name__ == "__main__":
    main()
