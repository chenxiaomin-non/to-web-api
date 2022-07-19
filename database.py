import asyncio
import aiomysql
import nest_asyncio
nest_asyncio.apply()
import os

user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')
port = int(os.environ.get('DB_PORT'))
db_name = os.environ.get('DB_NAME')

def get_connection(loop):
    return aiomysql.connect(
        host='localhost',
        port=port,
        user=user,
        password=password,
        db=db_name,
        loop=loop
    )

class ResultBag:
    index = 0
    result_bag = {}

    def __init__(self):
        self.index = 0
        self.result_bag = {}
    
    def get_new_index(self):
        self.index += 1
        return self.index
    
    def add_result(self, index, result):
        self.result_bag[index] = result

    def get_result(self, index):
        return self.result_bag[index]
    
result_bag = ResultBag()

async def get_token_info(token_address: str, loop, index: int):
    conn = await get_connection(loop)
    async with conn.cursor() as cur:
        await cur.execute('''SELECT * FROM cmc_metadata WHERE token_address = %s''', (token_address,))
        result = await cur.fetchone()
    conn.close()

    result_bag.add_result(index, result)


async def get_token_price_info(id: str, loop, index: int):
    conn = await get_connection(loop)
    async with conn.cursor() as cur:
        await cur.execute('''SELECT * FROM cmc_price WHERE id = %s''', (id,))
        result = await cur.fetchone()
    conn.close()

    result_bag.add_result(index, result)

def get_database_info(token_address: str):
    loop = asyncio.get_event_loop()
    index = result_bag.get_new_index()
    
    loop.run_until_complete(get_token_info(token_address, loop, index))
    cmc_info = result_bag.get_result(index)
    if cmc_info is None:
        return None, None
    
    id = cmc_info[0]
    loop.run_until_complete(get_token_price_info(id, loop, index))
    cmc_price = result_bag.get_result(index)
    
    return cmc_info, cmc_price

# print(get_database_info('0x2e98a6804e4b6c832ed0ca876a943abd3400b224'))