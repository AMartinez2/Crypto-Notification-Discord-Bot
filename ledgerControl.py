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
#     "running_average": 20,0,
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
import urllib.request
import datetime
import dateutil.parser as dateparser


API_KEY = open('_API_KEY', 'r').read().rstrip()
CONFIG = json.load(open('.config'))
LEDGER_INIT_TEMPLATE = {
    "currency": "ETH",
    "running_average": 0.0,
    "record": [],
}


# Ledger processing globals
MIN_PRICE = sys.float_info.max
MAX_PRICE = -1.0
MAX_NOTIF_BUFFER = 0
MAX_NOTIF_BUFFER_COUNT = 0
MIN_NOTIF_BUFFER = 0
MIN_NOTIF_BUFFER_COUNT = 0
MIN_NOTIF_LIMITER_COUNT = CONFIG['notificationLimiter']
MAX_NOTIF_LIMITER_COUNT = CONFIG['notificationLimiter']


def ledgerFileExists():
    recentFile = Path('ledger')
    return recentFile.is_file()


def verifyLedgerRecord(recordList):
    verified = True
    for i in recordList:
        verified = (
            isinstance(i, dict)
            and 'price' in i
            and isinstance(i['price'], float)
            and 'price_timestamp' in i
            and isinstance(dateparser.parse(i['price_timestamp']), datetime.date)
        )
        if (verified == False): break
    return verified


# Really dirty verification. Make sure everything exists and is the correct type
def verifyLedger():
    ledger = loadLedger()
    return (
        isinstance(ledger, dict)
        and 'currency' in ledger
        and isinstance(ledger['currency'], str)
        and 'running_average' in ledger
        and isinstance(ledger['running_average'], float)
        and verifyLedgerRecord(ledger['record'])
    )


def initLedger():
    f = open("ledger", "w")
    json.dump(LEDGER_INIT_TEMPLATE, f)
    f.close()


def normicsApiCall():
    apiURL = 'https://api.nomics.com/v1/currencies/ticker?key='+API_KEY+'&ids=ETH&interval=1h&convert=USD'
    data = urllib.request.urlopen(apiURL)
    return json.load(data)


# Takes user input and change settings
def processInput(command):
    if (command == "waffles"):
        print("I like waffles")


# Call to api and update ledger file
def loadLedger():
    if (not ledgerFileExists()):
        print('Loading ledger FAILED. Initializing new ledger...')
        initLedger()
    return json.load(open('ledger'))


# Increment notification rate limiters
def limiterStep():
    global MIN_NOTIF_LIMITER_COUNT
    global MAX_NOTIF_LIMITER_COUNT
    if (MIN_NOTIF_LIMITER_COUNT < CONFIG['notificationLimiter']):
        MIN_NOTIF_LIMITER_COUNT += 1
    if (MAX_NOTIF_LIMITER_COUNT < CONFIG['notificationLimiter']):
        MAX_NOTIF_LIMITER_COUNT += 1


# TODO::This function is getting too long. Refractor
# Not too worried about efficiency here, as there is a reasonable upper limit
def interpretLedger(ledger):
    global MIN_PRICE
    global MAX_PRICE
    global MIN_NOTIF_LIMITER_COUNT
    global MAX_NOTIF_LIMITER_COUNT
    notificationList = []
    print('start process')
    if (not ledgerFileExists()):
        print('Processing ledger FAILED: Ledger not found. Initializing new ledger...')
        notificationList.append('Processing ledger FAILED: Ledger not found. Initializing new ledger...')
        initLedger()
        return notificationList
    apiData = normicsApiCall()[0]
    currPrice = float(apiData['price'])
    if (len(ledger['record']) >= 1440):
        popped = ledger['record'].pop(0)
        # If popped value is the min or max, we must reset and find new values
        if (popped == MIN_PRICE):
            MIN_PRICE = sys.float_info.max
        if (popped == MAX_PRICE):
            MAX_PRICE = -1
    ledger['record'].append({"price":currPrice, "price_timestamp":apiData['price_timestamp']})
    #
    # TODO::do all the ledger checks here
    #
    # Create a list from `price` fields in the ledger's `record` list
    priceList = [float(price['price']) for price in ledger['record']]
    ledger['running_average'] = sum(priceList)/len(ledger['record'])
    if (currPrice < MIN_PRICE):
        MIN_PRICE = currPrice
        if (MIN_NOTIF_LIMITER_COUNT == CONFIG['notificationLimiter']):
            MIN_NOTIF_LIMITER_COUNT = 0
            notificationList.append(
                'MIN PRICE HIT! ----' + str(currPrice) + ' ---- ' + str(apiData['price_timestamp'])
            )
    if (currPrice > MAX_PRICE):
        MAX_PRICE = currPrice
        if (MAX_NOTIF_LIMITER_COUNT == CONFIG['notificationLimiter']):
            MAX_NOTIF_LIMITER_COUNT = 0
            notificationList.append(
                'MAX PRICE HIT! ----' + str(currPrice) + ' ---- ' + str(apiData['price_timestamp'])
            )
    ledgerFile = open('ledger', 'w')
    ledgerFile.write(json.dumps(ledger))
    limiterStep()
    return notificationList


def ledgerProcess():
    print('time')
    ledger = loadLedger()
    return interpretLedger(ledger)
