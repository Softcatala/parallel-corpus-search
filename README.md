# parallel-corpus-search

A service that allows to query parallel corpus built on top of ElasticSearch for internal using within Softcatalà

# How it works (locally)

1. We need to build a ElasticSearch Docker image with all the static data pre-loaded

This is done by running ``make build-all``

2. Run ``make docker-run``

3. URLs when running

* web-service Check ``http://localhost:8200/search/?source=hacker``

