from pprint import pprint
import requests
from fp.fp import FreeProxy
# test token addr = StepAscQoEioFxxWGnh2sLBDFp9d8rvKz2Yp39iDpyT
# ratioMVg27rSZbSvBopUvsdrGUzeALUfFma61mpxc8J
url = 'http://public-api.solscan.io/'


def get_token_metadata(token_address: str):
    gurl = url + 'token/meta?tokenAddress={}'.format(token_address)
    r = requests.get(gurl).text
    return r


def get_top_100_holder(token_address: str):
    params = {
        'tokenAddress': token_address,
        'limit': 100
    }

    gurl = url + 'token/holders'
    r = requests.get(gurl, params=params).json()

    return r


def get_price_info(token_address: str):
    gurl = url + 'market/token/{}' .format(token_address)
    r = requests.get(gurl).json()
    return r


pprint(get_token_metadata('StepAscQoEioFxxWGnh2sLBDFp9d8rvKz2Yp39iDpyT'))
