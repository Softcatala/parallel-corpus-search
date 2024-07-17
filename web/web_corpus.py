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

from flask import Flask, request, Response
from elasticsearch import Elasticsearch
import logging
import logging.handlers
import os
import time
import json
from datetime import datetime


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

@app.route('/hello', methods=['GET'])
def hello_api():
    data={"data":"Hello World"}
    return data

def get_query(field, word, size):
    query_body = {
        "query": {
            "function_score": {
                "query": {
                    "match" : {
                        f"{field}": f"{word}"
                    },
                },
                "field_value_factor": {
                    "field" : "prio",
                    "modifier": "reciprocal"
                }
            }
        },
       "highlight": {
            "fields": {
                f"{field}": {"fragment_size" : 1024}
                }
        },
        "size": size,
    }
    return query_body

@app.route('/index_stats/', methods=['GET'])
def index_stats_api():

    results = {}
    status = HTTP_OK

    try:
        INDEX_NAME = 'eng-cat'

        es = Elasticsearch('es01:9200', timeout=30)

        res = es.indices.stats(index=INDEX_NAME)
        docs = res['indices'][INDEX_NAME]['total']['docs']['count']
        size_in_bytes = res['indices'][INDEX_NAME]['primaries']['store']['size_in_bytes']
        size_in_GB = size_in_bytes / 1024/1024/1024

        index_info = es.indices.get(index=INDEX_NAME)
        creation_date = index_info[INDEX_NAME]["settings"]["index"]["creation_date"]
        ts = int(creation_date) / 1000
        creation_date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        results["indexed_docs"] = docs
        results["index_size"] = f"{size_in_GB:.2f}GB"
        results["creation_date"] = creation_date

    except Exception as e:
        err = str(e)
        logging.error(f"Error: {err}")
        results = {}
        results['error'] = err
        status = HTTP_ERROR

    json_results = json.dumps(results, indent=4)
    return json_answer_status(json_results, status)
    

@app.route('/search/', methods=['GET'])
def search_api():
    start_time = time.time()
    source = request.args.get('source')
    target = request.args.get('target')
    results = request.args.get('results')

    if source is not None and len(source) > 0:
        field = "src"
        word = source
    elif target is not None and len(target) > 0:
        field = "trg"
        word = target
    else:
        return "Invalid parameters", 400

    if results is not None and len(results) > 0:
        size = int(results)
        size = min(size, 500)
    else:
        size = 10

    try:

#        es = Elasticsearch('http://localhost:9200', timeout=30)
        es = Elasticsearch('es01:9200', timeout=30)

        query_body = get_query(field, word, size)
        res = es.search(index="eng-cat", body=query_body)
        elapsed_time = time.time() - start_time

        hits = res['hits']['hits']
        results = []
        for hit in hits:
            item = {}
            item['src'] = hit['_source']['src']
            item['trg'] = hit['_source']['trg']
            item['prio'] = hit['_source']['prio']
            item['license'] = hit['_source']['license']
            item['project'] = hit['_source']['project']
            item['highlight'] = hit['highlight']
            results.append(item)

        status = HTTP_OK
        logging.debug(f"/search for '{word}': {len(results)} results, time: {elapsed_time:.2f}s")

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
