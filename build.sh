docker build -t elasticsearch-static . -f elasticsearch_static_data/dockerfile
docker image ls | grep elasticsearch-static
