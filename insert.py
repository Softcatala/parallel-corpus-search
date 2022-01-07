from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch import helpers
import datetime

def main():

    print("Insert corpus")


    start_time = datetime.datetime.now()

    # Veure: https://techoverflow.net/2021/08/03/how-to-set-index-setting-using-python-elasticsearch-client/
    es = Elasticsearch('http://localhost:9200', timeout=30)

    settings_body = {
      "transient": { "cluster.routing.allocation.disk.threshold_enabled": "false" },
      "index.blocks.read_only_allow_delete": "null",
    }

    es.cluster.put_settings(settings_body)

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
