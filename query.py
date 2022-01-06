from datetime import datetime
from elasticsearch import Elasticsearch
import datetime


def main():

    print("Insert corpus")

    es = Elasticsearch('http://localhost:9200', timeout=30)

    query_body = {
      "query": {
          "match": {
              "src": "displayed"
          }
      }
    }

    start_time = datetime.datetime.now()

    res = es.search(index="eng-cat", body=query_body)
    print("Got %d Hits:" % res['hits']['total']['value'])
    for hit in res['hits']['hits']:
        print("%(timestamp)s %(author)s: %(src)s" % hit["_source"])

    s = 'Time: {0}'.format(datetime.datetime.now() - start_time)
    print(s)

if __name__ == "__main__":
    main()
