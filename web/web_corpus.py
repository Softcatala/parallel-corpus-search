#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2022 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from flask import Flask, Response
from elasticsearch import Elasticsearch
import logging
import logging.handlers
import os
import time
import json

app = Flask(__name__)

HTTP_OK = 200
HTTP_ERROR = 500

def init_logging():
    logfile = 'web_corpus.log'

    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logger = logging.getLogger()
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes=1024*1024, backupCount=1)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(LOGLEVEL)

    console = logging.StreamHandler()
    console.setLevel(LOGLEVEL)
    logger.addHandler(console)


# API calls
def json_answer(data):
    resp = Response(data, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

def json_answer_status(data, status):
    resp = json_answer(data)
    resp.status = str(status)
    return resp

@app.route('/search/<word>', methods=['GET'])
def search_api(word):
    start_time = time.time()

    try:

        #http://localhost:9200
        es = Elasticsearch('es01:9200', timeout=30)

        query_body = {
          "query": {
              "match": {
                  "src": f"{word}"
              }
          }
        }

        start_time = time.time()

        res = es.search(index="eng-cat", body=query_body)
        num_results = 0
        elapsed_time = time.time() - start_time
        logging.debug(f"/search for '{word}': {num_results} results, time: {elapsed_time:.2f}s")

        hits = res['hits']['hits']
        results = []
        for hit in hits:
            item = {}
            item['src'] = hit['_source']['src']
            item['trg'] = hit['_source']['trg']
            results.append(item)

        status = HTTP_OK

    except Exception as e:
        err = str(e)
        logging.error(f"Error: {err}")
        results = {}
        results['error'] = err
        status = HTTP_ERROR

    json_results = json.dumps(results, indent=4)
    return json_answer_status(json_results, status)


if __name__ == '__main__':
    init_logging()
    app.debug = True
    app.run()

if __name__ != '__main__':
    init_logging()
