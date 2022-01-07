#/bin/sh
cd srv/web/
mkdir -p /var/log/parallel-corpus-search/
gunicorn web_corpus:app -b 0.0.0.0:8000 --error-logfile /var/log/parallel-corpus-search/gnuicorn.log --workers=8
