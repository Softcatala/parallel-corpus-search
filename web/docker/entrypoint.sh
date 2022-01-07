#/bin/sh
cd /srv/
gunicorn web_corpus:app -b 0.0.0.0:8000 --workers=8
