from threading import Thread
import sys
from queue import Queue
import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import logging

CONCURRENT = 20

def doWork():
    while True:
        url = q.get()
        status = getStatus(url)
        doSomethingWithResult(status, url)
        q.task_done()

def getStatus(url):
    try:
        req = Request(url)
        handler = urlopen(req, timeout=10)
        handler.close()
        return handler.status
    except HTTPError as e:
        logging.error(f"{url} - {e}")
        return e.code
    
    except Exception as e:
        logging.error(f"{url} - {e}")
        return 523

def doSomethingWithResult(status, url):
    pass
    #print (status, url)

REQUESTS = 200


q = Queue(CONCURRENT * 2)
for i in range(CONCURRENT):
    t = Thread(target=doWork)
    t.daemon = True
    t.start()
try:
    start_time = datetime.datetime.now()
    with open('words.txt', 'r') as fh:
        lines = fh.readlines()

    for word in lines[:REQUESTS]:
        word = word.strip()
        url = f'https://api.softcatala.org/parallel-corpus-search/v1/search/{word}'
        q.put(url.strip())

    q.join()
    t = format(datetime.datetime.now() - start_time)
    s = f'Time used: {t} for {REQUESTS} requests ({CONCURRENT} concurrent)'
    print(s)
except KeyboardInterrupt:
    sys.exit(1)
