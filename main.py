#1440 minutes in a day

# 'https://api.nomics.com/v1/currencies/ticker?key='+API_KEY+'&ids=BTC,ETH,XRP&interval=1d,30d&convert=EUR'

    # "currency": "BTC",
    # "id": "BTC",
    # "price": "8451.36516421",
    # "price_date": "2019-06-14T00:00:00Z",
    # "price_timestamp": "2019-06-14T12:35:00Z",
    # "symbol": "BTC",
    # "circulating_supply": "17758462",
    # "max_supply": "21000000",
    # "name": "Bitcoin",
    # "logo_url": "https://s3.us-east-2.amazonaws.com/nomics-api/static/images/currencies/btc.svg",
    # "market_cap": "150083247116.70",
    # "transparent_market_cap": "150003247116.70",
    # "rank": "1",
    # "high": "19404.81116899",
    # "high_timestamp": "2017-12-16",
    # "1d": {}


# {
#     "currency": "ETH",
#     "running_average": 20,
#     "record": [
#         {
#             "price":8451.36516421,
#             "price_timestamp": "2019-06-14T12:35:00Z",
#         }
#     ],
# }

import threading
import time
import sys
import os.path
import json
from pathlib2 import Path


API_KEY = open('_API_KEY', 'r').read()
CONFIG = json.load(open('.config'))
LEDGER_INIT_TEMPLATE = {
    "currency": "ETH",
    "running_average": 0,
    "record": [],
}
STOP_THREADS = False
PREV_TIME = time.time()


# Force print for threading
def threadedPrint(message):
    print(message)
    sys.stdout.flush()


def ledgerFileExists():
    recentFile = Path('ledger')
    return recentFile.is_file()


def initLedger():
    f = open("ledger", "w")
    json.dump(LEDGER_INIT_TEMPLATE, f)
    f.close()


# Takes user input and change settings
def processInput(command):
    if (command == "waffles"):
        threadedPrint("I like waffles")


# Call to api and update ledger file
def loadLedger():
    if (not ledgerFileExists()):
        threadedPrint ('Loading ledger FAILED. Initializing new ledger...')
        initLedger()
    return json.load(open('.config'))


def processLedger():
    if (not ledgerFileExists()):
        threadedPrint ('Processing ledger FAILED. Initializing new ledger...')
        initLedger()
        return
    ledger = loadLedger()


def ledgerThread():
    global STOP_THREADS
    global PREV_TIME
    while True:
        # threadedPrint('thread running')
        if STOP_THREADS:
            break
        # threadedPrint(time.time() - PREV_TIME)
        if (time.time() - PREV_TIME > 5):
            threadedPrint('time')
            PREV_TIME = time.time()
            loadLedger()
            processLedger()


def inputThread():
    global STOP_THREADS
    while True:
        q = input()
        if (q == 'q'):
            STOP_THREADS = True
            break
        processInput(q)


if (__name__ == '__main__'):
    if (not ledgerFileExists()):
        initLedger()
    t1 = threading.Thread(target=ledgerThread)
    t2 = threading.Thread(target=inputThread)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    threadedPrint('shutting off')
