from threading import Thread
import sys
from queue import Queue
import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError

concurrent = 20

def doWork():
    while True:
        url = q.get()
        status = getStatus(url)
        doSomethingWithResult(status, url)
        q.task_done()

def getStatus(url):
    try:
        req = Request(url)
        x =  urlopen(req, timeout=10)
        return 200
    except HTTPError as e:
        logging.error(f"{url} - {e}")
        return e.code
    
    except Exception as e:
        logging.error(f"{url} - {e}")
        return 523

def doSomethingWithResult(status, url):
    print (status, url)

q = Queue(concurrent * 2)
for i in range(concurrent):
    t = Thread(target=doWork)
    t.daemon = True
    t.start()
try:
    start_time = datetime.datetime.now()
    with open('words.txt', 'r') as fh:
        lines = fh.readlines()
    
    for word in lines[:200]:
#        print(word)
        word = word.strip()
        url = f'http://localhost:8000/search/{word}'
        q.put(url.strip())

    q.join()
    s = 'Time used: {0}'.format(datetime.datetime.now() - start_time)
    print(s)
except KeyboardInterrupt:
    sys.exit(1)
