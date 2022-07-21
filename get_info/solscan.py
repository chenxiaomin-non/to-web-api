import json
import os
from pprint import pprint
import requests
from fp.fp import FreeProxy
# test token addr = StepAscQoEioFxxWGnh2sLBDFp9d8rvKz2Yp39iDpyT
# ratioMVg27rSZbSvBopUvsdrGUzeALUfFma61mpxc8J
url = 'http://public-api.solscan.io/'
total_supply = {}

def get_token_metadata(token_address: str):
    gurl = url + 'token/meta?tokenAddress={}'.format(token_address)
    r = requests.get(gurl).text
    total_supply[token_address] = r.get('supply')
    return r


def get_top_100_holder(token_address: str):
    params = {
        'tokenAddress': token_address,
        'limit': 100
    }
    gurl = url + 'token/holders'
    r = requests.get(gurl, params=params).json()

    total_holders = r.get('total') 
    result = {
        'total_holders': total_holders,
        'more_than_20': 0,
        'more_than_10': 0,
        'more_than_5': 0,
        'more_than_1': 0,
        'total_of_more_than_20': 0,
        'total_of_more_than_10': 0,
        'total_of_more_than_5': 0,
        'total_of_more_than_1': 0,
    }
    try:
        token_sp = total_supply[token_address]
    except KeyError:
        get_token_metadata(token_address)
        token_sp = total_supply[token_address]

    for holder in r.get('data'):
        balance = holder.get('amount')
        if balance > 20 * token_sp / 100:
            result['more_than_20'] += 1
            result['total_of_more_than_20'] += balance
        if balance > 10 * token_sp / 100:
            result['more_than_10'] += 1
            result['total_of_more_than_10'] += balance
        if balance > 5 * token_sp / 100:
            result['more_than_5'] += 1
            result['total_of_more_than_5'] += balance  
        if balance > 1 * token_sp / 100:
            result['more_than_1'] += 1
            result['total_of_more_than_1'] += balance


    return result


def get_price_info(token_address: str):
    gurl = url + 'market/token/{}' .format(token_address)
    r = requests.get(gurl).json()
    return r




# pprint(get_token_metadata('StepAscQoEioFxxWGnh2sLBDFp9d8rvKz2Yp39iDpyT'))
