from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

def main():

    print("Insert corpus")

    es = Elasticsearch('http://localhost:9200', timeout=30)

    BULK_ITEMS = 100
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
                'src': src,
                'trg': trg,
                'timestamp': datetime.now()
            }
            bulk_insert.append(doc)
            id += 1
            bulk_buffer += 1

            if bulk_buffer < BULK_ITEMS:
                continue

            helpers.bulk(es, bulk_insert)
            bulk_buffer = 0
            bulk_insert = []

#            print(doc)
#            resp = es.index(index="eng-cat", id=id, document=doc)
#            print(resp['result'])

            if id % 100 == 0:
                print(f"Inserted {id}")

#            if id > 100:
#                break

if __name__ == "__main__":
    main()
