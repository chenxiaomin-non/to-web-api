import pprint
import requests

API_KEY = 'ckey_0f2abb4c094440d390362f1f9ea'
base_url = 'https://api.covalenthq.com/v1/'

chain_dict = {
    'eth': 1,
    'bsc': 56,
    'matic': 137
}


def get_top_100_balance(chain: str, token_address: str):
    params = {
        'key': API_KEY,
        'page-size': 100
    }

    url = '{}{}/tokens/{}/token_holders/'.format(
        base_url, chain_dict[chain], token_address)

    response = requests.get(url, params=params).json()
    if response.get('data', None) is None and response.get('data', None).get('items', None) is None:
        return None
    else:
        result = []
        for item in response['data']['items']:
            address = item['address']
            balance = 100*int(item['balance'])/int(item['total_supply'])
            result.append((address, balance))

        return_obj = {}
        temp = 0
        number_of_little_wallet_equals = 0
        for item in result:
            if item[1] > 20:
                return_obj['more_than_20'] = return_obj.get('more_than_20', 0) + 1
                return_obj['total_of_more_than_20'] = return_obj.get('total_of_more_than_20', 0) + item[1]
            if item[1] > 10:
                return_obj['more_than_10'] = return_obj.get('more_than_10', 0) + 1
                return_obj['total_of_more_than_10'] = return_obj.get('total_of_more_than_10', 0) + item[1]
            if item[1] > 5:
                return_obj['more_than_5'] = return_obj.get('more_than_5', 0) + 1
                return_obj['total_of_more_than_5'] = return_obj.get('total_of_more_than_5', 0) + item[1]
            if item[1] > 1:
                return_obj['more_than_1'] = return_obj.get('more_than_1', 0) + 1
                return_obj['total_of_more_than_1'] = return_obj.get('total_of_more_than_1', 0) + item[1]
            
            if item[1] != temp:
                temp = item[1]
            else:
                number_of_little_wallet_equals += 1
        return_obj['number_of_little_wallet_equals'] = number_of_little_wallet_equals

    return result


# pprint.pprint(get_top_100_balance(
#     'eth', '0xff71cb760666ab06aa73f34995b42dd4b85ea07b'))
# print('---------')
# pprint.pprint(get_top_100_balance(
#     'bsc', '0x9085B4d52c3e0B8B6F9AF6213E85A433c7D76f19'))
