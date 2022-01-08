# parallel-corpus-search

A service that allows to query parallel corpus built on top of ElasticSearch


# How it works

1. We need to build a ElasticSearch Docker image with all the static data pre-loaded

This is done at ``/elasticsearch_static_data`` using ``build.sh``

2. Run ``docker-compose up``

3. URLs when running

* web-service Check ``http://localhost:8000/search/hacker``

