.PHONY: docker-elasticsearch docker-build-parallel-corpus-search

build-all: docker-elasticsearch docker-build-parallel-corpus-search

docker-elasticsearch:
	docker build -t elasticsearch-static . -f elasticsearch_static_data/dockerfile;

docker-build-parallel-corpus-search:
	docker build -t parallel-corpus-search . -f web/docker/dockerfile;

docker-run:
	docker-compose -f local.yml up;

