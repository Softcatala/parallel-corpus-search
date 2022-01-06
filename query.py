from datetime import datetime
from elasticsearch import Elasticsearch


def main():

    print("Insert corpus")

    es = Elasticsearch('http://localhost:9200', timeout=30)

    query_body = {
      "query": {
          "match": {
              "src": "GNOME"
          }
      }
    }

    res = es.search(index="eng-cat", body=query_body)
    print("Got %d Hits:" % res['hits']['total']['value'])
    for hit in res['hits']['hits']:
        print("%(timestamp)s %(author)s: %(src)s" % hit["_source"])

if __name__ == "__main__":
    main()
