from elasticsearch import Elasticsearch
from elasticsearch import helpers
from urllib.request import Request, urlopen
import time
import datetime
import threading

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
              "type": "elision",
              "articles": ["d", "l", "m", "n", "s", "t"],
              "articles_case": True
            },
            "catalan_stop": {
              "type": "stop",
              "stopwords": "_catalan_"
            },
            "catalan_keywords": {
              "type": "keyword_marker",
              "keywords": ["example"]
            },
            "catalan_stemmer": {
              "type": "stemmer",
              "language": "catalan"
            }
          },
          "analyzer": {
            "rebuilt_catalan": {
              "tokenizer": "standard",
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
                        "ignore_above": 256
                   }
              },
              "analyzer": "rebuilt_catalan"
            }
        }
    }

    es.indices.put_mapping(index=index_name, body=mappings)

def generate_bulk_actions(filename):
    with open(filename, "r") as source:
        id = 1
        for line in source:
            components = line.strip().split("\t")
            if len(components) == 5:
                yield {
                    '_index': "eng-cat",
                    '_id': id,
                    'src': components[0],
                    'trg': components[1],
                    'prio': int(components[2]),
                    'license': components[3],
                    'project': components[4],
                    'timestamp': datetime.datetime.now()
                }
                id += 1

def main():
    print("Insert corpus")

    URL = 'http://localhost:9200'
    wait_for_elastic_search(URL)

    es = Elasticsearch(URL, timeout=60)
    create_index(es, "eng-cat")

    start_time = datetime.datetime.now()

    actions = generate_bulk_actions("corpus.tsv")
    successes, failures = 0, 0

    for success, info in helpers.parallel_bulk(es, actions, chunk_size=1000):
        if success:
            successes += 1
        else:
            failures += 1

    es.indices.refresh(index='eng-cat')
    res = es.indices.stats(index='eng-cat')
    docs = res['indices']['eng-cat']['total']['docs']['count']
    size_in_bytes = res['indices']['eng-cat']['primaries']['store']['size_in_bytes']
    size_in_GB = size_in_bytes / 1024 / 1024 / 1024

    print(f"Successes: {successes}, Failures: {failures}")
    print(f"documents indexed {docs}, size in bytes {size_in_bytes} ({size_in_GB:.2f} GB)")
    print('Time used:', datetime.datetime.now() - start_time)

if __name__ == "__main__":
    main()

