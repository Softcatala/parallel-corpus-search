docker build --no-cache -t elasticsearch-static . -f elasticsearch_static_data/dockerfile
docker image ls | grep elasticsearch-static
