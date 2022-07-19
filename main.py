import datetime
import json
import os
from fastapi import FastAPI
import collect_info as ci
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
cwd = os.getcwd()

origin = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost",
    "https://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_old_json_info(token_address: str, step: int):
    try:
        data = json.load(
            open(f'{cwd}/json_old_result/{step}_{token_address}.json'))

        ts = data.get('timestamp')
        curr_ts = datetime.datetime.now().timestamp()
        if curr_ts - ts > 60*60*24:
            return None
        return data.get('data')
    except Exception:
        return None


def save_new_json_result(token_address: str, step: int, data: dict):
    save_data = {
        'timestamp': datetime.datetime.now().timestamp(),
        'data': data
    }
    json.dump(save_data, open(
        f'{cwd}/json_old_result/{step}_{token_address}.json', 'w'))


def validate_input(token_address: str):
    for char in token_address:
        if char.isalnum() is False:
            return False
    return True


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/step1/{token_address}')
async def step1(token_address: str):
    if validate_input(token_address) is False:
        return {
            'status': 'error',
            'message': 'Invalid token address'
        }

    data = get_old_json_info(token_address, 1)
    if data is not None:
        return data

    chain, name, data = ci.get_moralis_info(token_address)
    save_new_json_result(token_address, 1, {
        'token_address': token_address,
        'chain': chain,
        'name': name,
        'data': data
    })
    return {
        'token_address': token_address,
        'chain': chain,
        'name': name,
        'data': data
    }


@app.get("/step2/{chain}/{token_address}")
async def step2(chain: str, token_address: str):
    if validate_input(token_address) is False:
        return {
            'status': 'error',
            'message': 'Invalid token address'
        }

    data = get_old_json_info(token_address, 2)
    if data is not None:
        return data
    data = ci.get_cryptorank_info(chain, token_address)

    save_new_json_result(token_address, 2, {
        'token_address': token_address,
        'chain': chain,
        'data': data
    })
    return {
        'token_address': token_address,
        'chain': chain,
        'data': data
    }


@app.get("/step3/{chain}/{token_address}")
async def step3(chain: str, token_address: str):
    if validate_input(token_address) is False:
        return {
            'status': 'error',
            'message': 'Invalid token address'
        }

    data = get_old_json_info(token_address, 3)
    if data is not None:
        return data

    if chain == 'eth':
        data = ci.get_ethplorer_info(token_address)
    else:
        data = ci.get_other_of_eth_top_holder(token_address, chain)

    save_new_json_result(token_address, 3, {
        'token_address': token_address,
        'chain': chain,
        'data': data
    })
    return {
        'token_address': token_address,
        'chain': chain,
        'data': data
    }
