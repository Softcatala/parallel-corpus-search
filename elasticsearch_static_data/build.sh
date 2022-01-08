IMAGE_NAME=docker.elastic.co/elasticsearch/elasticsearch:7.16.2

if [ ! -f src.txt ]
then
    echo "Not found src.txt"
    wget https://www.softcatala.org/pub/softcatala/parallel-corpus-search/eng-cat.eng.zip
    unzip eng-cat.eng.zip
fi

if [ ! -f tgt.txt ]
then
    echo "Not found tgt.txt"
    wget https://www.softcatala.org/pub/softcatala/parallel-corpus-search/eng-cat.cat.zip
    unzip eng-cat.cat.zip
fi

rm -r -f static_data
mkdir static_data

sudo sysctl -w vm.max_map_count=262144
docker pull $IMAGE_NAME

docker run --rm --name es_build -d -p 9200:9200 -v "$(pwd)/elasticsearch.yml":/usr/share/elasticsearch/config/elasticsearch.yml \
-v "$(pwd)/static_data":/usr/share/elasticsearch/data -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" $IMAGE_NAME 

echo "Starts inserting"
python3 insert.py

docker stop es_build

docker build -t elasticsearch-static . -f dockerfile
docker image ls | grep elasticsearch-static
