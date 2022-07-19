from datetime import datetime
import requests
import asyncio
import nest_asyncio
nest_asyncio.apply()


def get_key_and_url(chain: str):
    if chain == 'eth':
        key = '92KN8VPM8UFJW2CP6PR6G4S9DJBDBM1TA5'
        url = 'https://api.etherscan.io/api'
    if chain == 'bsc':
        key = 'EV41IX58376FTWQM37PW9T3ADJV18HSPZN'
        url = 'https://api.bscscan.com/api'
    if chain == 'polygon':
        key = '1UTUPVDHPG2J7TAKTXB6SS1GF9S2155Z5A'
        url = 'https://api.polygonscan.com/api'

    return (key, url)

#############################################################################################
############################### SIMPLE CHECK ################################################
#############################################################################################


async def get_liquidity_of_token(token: str):
    url = 'https://api.pancakeswap.info/api/v2/tokens/' + token
    response = requests.get(url).json()
    try:
        data = response['data']
        price_USD = data['price']
    except:
        return 0
    return float(price_USD)


async def get_total_supply(url, key, token_address):
    params = {
        'module': 'stats',
        'action': 'tokensupply',
        'apikey': key,
        'contractaddress': token_address
    }

    response = requests.get(url, params=params).json()
    try:
        return int(response.get('result', 0))
    except:
        return 0


async def get_circulating_supply(url, key, token_address):
    params = {
        'module': 'stats',
        'action': 'tokenCsupply',
        'apikey': key,
        'contractaddress': token_address
    }

    response = requests.get(url, params=params).json()
    try:
        return int(response.get('result', 0))
    except:
        return 0


async def get_account_balance(url, key, token_address, account_address):
    params = {
        'module': 'account',
        'action': 'tokenbalance',
        'apikey': key,
        'contractaddress': token_address,
        'address': account_address
    }

    response = requests.get(url, params=params).json()
    try:
        return int(response.get('result', 0))
    except:
        return 0


async def find_token_owner(url, key, address):
    params = {
        'module': 'account',
        'action': 'txlist',
        'apikey': key,
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'page': 1,
        'offset': 100,
        'sort': 'asc'
    }
    response = requests.get(url, params=params).json()
    result = response.get('result', [])
    if len(result) > 0:
        for transaction in result:
            if transaction['to'] == '':
                return transaction['from']


async def get_contract_abi(url, key, contract_address):
    params = {
        'module': 'contract',
        'action': 'getabi',
        'apikey': key,
        'address': contract_address
    }

    response = requests.get(url, params=params).json()
    return response.get('result', None)


async def get_owner_balance(url, key, contract_address, owner_address):
    return get_account_balance(url, key, contract_address, owner_address)

#############################################################################################
###################### COMPLEX CHECK ########################################################
#############################################################################################


def get_all_transaction(url, key, address, mode: str):
    result = []
    params = {
        'module': 'account',
        'action': 'tokentx',
        'apikey': key,
        'contractaddress': address,
        'startblock': 0,
        'endblock': 99999999,
        'page': 1,
        'offset': 10000,
        'sort': mode
    }
    while True:

        response = requests.get(url, params=params).json()
        trans = response.get('result', [])
        if trans is not None:
            print(len(trans))
        else:
            break
        for transaction in trans:
            result.append({
                'timestamp': transaction['timeStamp'],
                'from': transaction['from'],
                'to': transaction['to'],
                'value': transaction['value'],
            })
        params['page'] += 1
        if len(trans) < 10000:
            break
    return result


def get_all_holder_balance(url, key, contract_address, transactions):
    print('processing all holder balance')

    holders_count = dict()
    self_transfer = 0
    for transaction in transactions:
        if transaction['from'] == transaction['to']:
            self_transfer += 1
        holders_count[transaction['from']] = holders_count.get(
            transaction['from'], 0) + 1
        holders_count[transaction['to']] = holders_count.get(
            transaction['to'], 0) + 1

    list_holders_count = list(holders_count.items())
    list_holders_count.sort(key=lambda x: x[1], reverse=True)

    if len(list_holders_count) > 100:
        top = 10
    else:
        top = len(list_holders_count)//10 + 1

    # check top persons who have most send and receive transaction
    top_transfer_person = []
    total_supply = get_total_supply(url, key, contract_address)
    for i in range(top):
        top_transfer_person.append((list_holders_count[i][0], 100*get_account_balance(
            url, key, contract_address, list_holders_count[i][0])/total_supply))

    # check top value transactions' holder balance
    top_transfer_volume = []
    for i in range(top):
        value = 0
        for transaction in transactions:
            if transaction['from'] == list_holders_count[i][0] or transaction['to'] == list_holders_count[i][0]:
                value += int(transaction['value'])
        top_transfer_volume.append(
            (list_holders_count[i][0], 100*value/total_supply))

    return {
        'self_transfer': self_transfer,
        'holders_count': list_holders_count[:10],
        'top_holder': top_transfer_person,
        'top_transfer_volume': top_transfer_volume
    }


def process_time_of_transaction(transactions, mode: str):
    print('processing time of transaction')
    time_list = []
    for transaction in transactions:
        temp = int(transaction['timestamp'])
        time_list.append(temp)

    now = int(datetime.now().timestamp())
    if mode == 'asc':
        create_at = now - time_list[0]
        oldest_transaction = now - time_list[1]
        latest_transaction = now - time_list[-1]
    else:
        create_at = now - time_list[-1]
        oldest_transaction = now - time_list[-2]
        latest_transaction = now - time_list[0]

    for i in range(len(time_list) - 1):
        if mode == 'asc':
            time_list[i] = time_list[i + 1] - time_list[i]
        else:
            time_list[i] = time_list[i] - time_list[i + 1]

    time_list.remove(time_list[-1])

    average = sum(time_list) / len(time_list)
    sigma = 0
    for i in range(len(time_list)):
        sigma += (time_list[i] - average) ** 2
    sigma = sigma / len(time_list)
    sigma = sigma ** 0.5
    result = {
        'average': average,
        'sigma': sigma,
        's/a': sigma / average,
        'latest': latest_transaction,
        'oldest': oldest_transaction,
        'create_at': create_at
    }

    return result


def process_value_of_transaction(url, key, contract_address, transactions, circulating_supply: int):
    print('processing value of transaction')
    value_list = []
    sum = 0
    top_value_transaction = []
    # count number of transactions which have value exceed
    # 5%, 2%, 0.5%, 0.1% circulation supply

    count = [0, 0, 0, 0, 0]
    for transaction in transactions:
        temp = int(transaction['value'])
        sum += temp
        value_list.append(temp)

        if temp > circulating_supply * 0.01:
            top_value_transaction.append(transaction)

        if temp > circulating_supply * 0.05:
            count[0] += 1
        if temp > circulating_supply * 0.02:
            count[1] += 1
        if temp > circulating_supply * 0.005:
            count[2] += 1
        if temp > circulating_supply * 0.001:
            count[3] += 1
        count[4] += 1

    big_transfer_person = set()
    for transaction in top_value_transaction:
        big_transfer_person.add(transaction['from'])
        big_transfer_person.add(transaction['to'])
    

    # async def get_balance(url, key, contract_address, persons: set):
    #     gather = await asyncio.gather(
    #         *[(person, get_account_balance(url, key, contract_address, person)) 
    #             for person in persons])
    #     return gather
         
    # top_big_transfer_person = asyncio.run(get_balance(url, key, contract_address, big_transfer_person))

    average = sum / len(value_list)
    sigma = 0
    for i in range(len(value_list)):
        sigma += (value_list[i] - average) ** 2
    sigma = sigma / len(value_list)
    sigma = sigma ** 0.5

    result = {
        'average': average,
        'sigma': sigma,
        's/a': sigma / average,
        'count_5': 100*count[0]/count[4],
        'count_2': 100*count[1]/count[4],
        'count_0.5': 100*count[2]/count[4],
        'count_0.1': 100*count[3]/count[4],
        'count_all': count[4]
    }

    return result


###########################################################################################
####### CALL TO SUMMARY FUNCTION ##########################################################
###########################################################################################


def get_more_info(chain: str, token_address):

    key, url = get_key_and_url(chain)

    async def concurrency_get_info(key, url, token_address):
        gather = await asyncio.gather(
            get_total_supply(url, key, token_address),
            get_circulating_supply(url, key, token_address),
            get_liquidity_of_token(token_address),
            find_token_owner(url, key, token_address),
            get_contract_abi(url, key, token_address)
        )
        return gather

    result = asyncio.run(concurrency_get_info(key, url, token_address))

    async def owner_balance(url, key, token_address, owner):
        gather = await asyncio.gather(
            get_account_balance(url, key, token_address, owner)
        )
        return gather

    owner_balance = asyncio.run(owner_balance(url, key, token_address, result[3]))
    owner_hold = 100 * owner_balance[0]/result[0]

    return (result[0], result[1], result[2], result[3], result[4], owner_hold)


def process_all_transaction(chain, contract_address):
    key, url = get_key_and_url(chain)
    result = {}
    print('start to get all transaction')

    async def get_ts(url, key, contract_address):
        gather = await asyncio.gather(
            get_total_supply(url, key, contract_address)
        )
        return gather
    total_supply = asyncio.run(get_ts(url, key, contract_address))[0]

    

    from multiprocessing.pool import ThreadPool
    pool = ThreadPool(processes=2)
    transactions_desc = pool.apply_async(get_all_transaction, (
        url, key, contract_address, 'desc'))
    transactions_asc = pool.apply_async(get_all_transaction, (
        url, key, contract_address, 'asc'))

    transactions_desc = transactions_desc.get()

    import multiprocessing
    p_pool = multiprocessing.Pool(processes=2)
    time_p = p_pool.apply_async(process_time_of_transaction, (
        transactions_desc, 'desc'))
    value_p = p_pool.apply_async(process_value_of_transaction, (
        url, key, contract_address, transactions_desc, total_supply))

    result['time'] = time_p.get()
    result['value'] = value_p.get()

    transactions_asc = transactions_asc.get()
    time_p = p_pool.apply_async(process_time_of_transaction, (
        transactions_asc, 'asc'))
    value_p = p_pool.apply_async(process_value_of_transaction, (
        url, key, contract_address, transactions_asc, total_supply))

    result['time_asc'] = time_p.get()
    result['value_asc'] = value_p.get()

    pool.close()
    p_pool.close()
    print('finish to get all transaction')
    return result


#   'holders': get_all_holder_balance(url, key, contract_address, transactions_desc),

# print(get_more_info('eth', '0x423b5F62b328D0D6D44870F4Eee316befA0b2dF5'))
# print(process_all_transaction('eth', '0x423b5F62b328D0D6D44870F4Eee316befA0b2dF5'))
###########################################################################################
############################### TEST CASE #################################################
###########################################################################################


# pprint.pprint(process_all_transaction(
#    'eth', '0x76974c7b79dc8a6a109fd71fd7ceb9e40eff5382'))
