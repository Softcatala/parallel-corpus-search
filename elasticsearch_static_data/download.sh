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
