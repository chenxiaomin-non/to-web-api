from pprint import pprint
import requests

# test token addr = StepAscQoEioFxxWGnh2sLBDFp9d8rvKz2Yp39iDpyT
# ratioMVg27rSZbSvBopUvsdrGUzeALUfFma61mpxc8J
url = 'https://public-api.solscan.io/'


def get_token_metadata(token_address: str):
    params = {
        'tokenAddress': token_address
    }
    gurl = url + 'token/meta'
    r = requests.get(gurl, params=params).text
    return r

def get_top_100_holder(token_address: str):
    params = {
        'tokenAddress': token_address,
        'limit': 100
    }

    gurl = url + 'token/holders'
    r = requests.get(gurl, params=params).json()

pprint(get_token_metadata('StepAscQoEioFxxWGnh2sLBDFp9d8rvKz2Yp39iDpyT'))