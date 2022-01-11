IMAGE_NAME=docker.elastic.co/elasticsearch/elasticsearch:7.16.2

bash download.sh

sudo sysctl -w vm.max_map_count=262144
docker pull $IMAGE_NAME

docker stop es_build || true
docker run --rm --name es_build -d -p 9200:9200 --env-file env.list $IMAGE_NAME 
id=$(docker ps -aqf "name=es_build")
echo Copying files
docker cp insert.py $id:/opt/
docker cp inside.sh $id:/opt/
docker cp src.txt $id:/opt/
docker cp tgt.txt $id:/opt/
docker cp requirements.txt $id:/opt/

echo Exec
docker exec -it $id bash -c "/opt/inside.sh"


rm -r -f data && mkdir data
docker cp $id:/usr/share/elasticsearch/data/ .

docker stop es_build

docker build -t elasticsearch-static . -f dockerfile
docker image ls | grep elasticsearch-static
