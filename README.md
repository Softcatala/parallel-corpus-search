# parallel-corpus-search

A service that allows to query parallel corpus built on top of ElasticSearch for internal using within Softcatalà

# How it works (locally)

1. We need to build a ElasticSearch Docker image with all the static data pre-loaded

This is done by running ``./build.sh``

2. We need to build a the webservice

This is done by running ``./web/docker/build-docker.sh``

3. Run ``docker-compose up``

4. URLs when running

* web-service Check ``http://localhost:8200/search/?source=hacker``

