from pprint import pprint
import requests

key = 'EK-uDfYa-gg79hJE-fh19j'

######################################################################
############# USE ETHPLORER API TO GET INFO ##########################
######################################################################

# one api call -> to get all info needed
# doc: https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API#get-address-transactions
#

def lazy_get_token_info(token_address):
    url = 'https://api.ethplorer.io/getTokenInfo/' + token_address
    params = {
        'apiKey': key
    }
    response = requests.get(url, params=params).json()
    if response.get('error') is not None:
        return None

    return response


def get_top_holder_info(token_address):
    url = 'https://api.ethplorer.io/getTopTokenHolders/' + token_address
    params = {
        'apiKey': key,
        'limit': 100
    }
    response = requests.get(url, params=params).json()
    if response.get('error') is not None:
        return None

    return response


def is_mintable_token(token_address):
    url = 'https://api.ethplorer.io/getTokenHistory/' + token_address
    params = { 
        'apiKey': key,
        'type': 'mint'
    }
    response = requests.get(url, params=params).json()
    if response.get('error') is not None:
        return 98
    if len(response.get('operations')) != 0:
        for operation in response.get('operations'):
            if operation.get('type') == 'mint':
                return 98
        return 0
    else:
        return 0

def get_price_history(token_address):
    url = 'https://api.ethplorer.io/getTokenPriceHistoryGrouped/' + token_address
    params = {
        'apiKey': key,
        'period': 10
    }
    response = requests.get(url, params=params).json()
    if response.get('error') is not None:
        return None
    return response.get('history')

######################################################################
############# INTERFACE FUNCTION TO GET INFO #########################
######################################################################

def get_info_from_ethplorer(token_address):
    result = {}
    result.update(lazy_get_token_info(token_address))
    top_token_info = get_top_holder_info(token_address)
    holders_info = {
        "more_than_20": 0,
        "more_than_10": 0,
        "more_than_5": 0,
        "more_than_1": 0,
        "total_of_more_than_20": 0,
        "total_of_more_than_10": 0,
        "total_of_more_than_5": 0,
        "total_of_more_than_1": 0,
    }
    for holder in top_token_info.get('holders'):
        if holder.get('share') > 20:
            holders_info['more_than_20'] += 1
            holders_info['total_of_more_than_20'] += holder.get('share')
        if holder.get('share') > 10:
            holders_info['more_than_10'] += 1
            holders_info['total_of_more_than_10'] += holder.get('share')
        if holder.get('share') > 5:
            holders_info['more_than_5'] += 1
            holders_info['total_of_more_than_5'] += holder.get('share')
        if holder.get('share') > 1:
            holders_info['more_than_1'] += 1
            holders_info['total_of_more_than_1'] += holder.get('share')
    result.update(holders_info)
    result.update({'is_mintable': is_mintable_token(token_address)})
    return result

# pprint(get_info_from_ethplorer('0xff71cb760666ab06aa73f34995b42dd4b85ea07b'))
# print(is_mintable_token('0xff71cb760666ab06aa73f34995b42dd4b85ea07b'))
#print(get_top_holder_info('0xff71cb760666ab06aa73f34995b42dd4b85ea07b'))
# pprint.pprint(get_price_history('0x48c80f1f4d53d5951e5d5438b54cba84f29f32a5'))




