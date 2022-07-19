import get_info.moralis as moral_scan
import get_info.cryptorank as uni_scan
import get_info.ethplorer as eth_scan
import get_info.covalenthq as cova_scan
import database as cmc_info
import sys
import os
sys.path.append(os.path.dirname(__file__))


def get_moralis_info(token_address: str):
    result = moral_scan.get_moralis_metadata_erc20(token_address)
    cmc_result = cmc_info.get_database_info(token_address)

    return_obj = {
        "Basic Metadata": [],
        "Price and Liquidity": [],
        "Transactions": []
    }

    if cmc_result[0] is None:
        return_obj["Basic Metadata"] \
            .append(("CMC", "ERR", "There's no infomation about this token in the Coin Marketcap database! Maybe this token has no value or haven't been published yet!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("CMC", "OK", "This token has been published in the Coin Marketcap database!"))
        
        if cmc_result[1] is None:
            return_obj["Basic Metadata"] \
                .append(("CMC_Price", "ERR", "We can't get the infomation about the price of this token in the Coin Marketcap database! Maybe this token has no value!"))
        else:
            return_obj["Basic Metadata"] \
                .append(("CMC_Price", "OK", "This token currently is being sold on the Coin Marketcap!"))

    if result[1] is None:
        return_obj["Basic Metadata"] \
            .append(("Name", "ERR", "Token name not found by our tools!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("Name", "OK", "Token name: %s" % result[1]))

    if result[2] is None:
        return_obj["Basic Metadata"] \
            .append(("Symbol", "ERR", "Token symbol not found by our tools!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("Symbol", "OK", "Token symbol: %s" % result[2]))

    if result[3] is None:
        return_obj["Basic Metadata"] \
            .append(("Decimal", "ERR", "Token decimals not found by our tools!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("Decimal", "OK", "Token decimals: %s" % result[3]))

    if result[5] is None or result[5] == 0:
        return_obj["Price and Liquidity"] \
            .append(("Price", "ERR", "This token has no value to hold!"))
    else:
        return_obj["Price and Liquidity"] \
            .append(("Price", "OK", "Token value: %s" % result[5]))

    if result[6] is None or result[6] <= 100:
        return_obj["Transactions"] \
            .append(("TxCount", "ERR", "This token has no transaction or less than 100 transactions!"))
    elif result[6] <= 1000:
        return_obj["Transactions"] \
            .append(("TxCount", "WARN", "This token has less than 1000 transactions!"))
    else:
        return_obj["Transactions"] \
            .append(("TxCount", "OK", "This token has more than 1000 transactions!"))

    return result[0], result[1], return_obj


def get_cryptorank_info(chain: str, token_address: str):
    result = uni_scan.get_more_info(chain, token_address)

    return_obj = {
        "Basic Metadata": [],
        "Price and Liquidity": [],
        "Transactions": []
    }

    if result[0] is None or result[0] == 0:
        return_obj["Basic Metadata"] \
            .append(("TSupply", "ERR", "Total supply of the token is 0 or we can't successfully get the infomation!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("TSupply", "OK", "Total supply of the token: %s" % result[0]))

    if result[1] is None or result[1] == 0:
        return_obj["Basic Metadata"] \
            .append(("CSupply", "ERR", "Total circulating supply is 0! Maybe this token is not circulated yet!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("CSupply", "OK", "Total circulating supply: %s" % result[1]))

    if result[2] is None or result[2] == 0:
        return_obj["Price and Liquidity"] \
            .append(("Liquidity", "ERR", "We can't get the infomation about total liquidity of this token! Maybe this token has no value or haven't been published yet!"))
    else:
        return_obj["Price and Liquidity"] \
            .append(("Liquidity", "OK", "Total liquidity: %s" % result[2]))

    if result[3] is None:
        return_obj["Basic Metadata"] \
            .append(("Owner", "ERR", "We can't get the infomation about the owner of this token!"))

    if result[4] is None:
        return_obj["Basic Metadata"] \
            .append(("ContractVerified", "ERR", "This token contract hasn't been verified yet by any exchange! Maybe the token has some problem or the owner still doesn't want to publish the token!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("ContractVerified", "OK", "This token contract has been verified by exchanges!"))

    if result[5] is None:
        return_obj["Basic Metadata"] \
            .append(("OwnerHold", "ERR", "We can't get the infomation about the owner balance!"))
    elif result[5] > 20:
        return_obj["Basic Metadata"] \
            .append(("OwnerHold", "ERR", "This token owner has more than 10% total supply of this tokens!"))
    elif result[5] > 5:
        return_obj["Basic Metadata"] \
            .append(("OwnerHold", "WARN", "This token owner has more than 5% total supply of this tokens!"))
    elif result[5] > 1:
        return_obj["Basic Metadata"] \
            .append(("OwnerHold", "WARN", "This token owner has more than 1% total supply of this tokens!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("OwnerHold", "OK", "This token owner has less than 1% total supply of this tokens!"))

    return return_obj


def get_ethplorer_info(token_address: str):
    result = eth_scan.get_info_from_ethplorer(token_address)

    return_obj = {
        "Basic Metadata": [],
        "Price and Liquidity": [],
        "Transactions": []
    }

    if result.get("countOps", 0) < 1000:
        return_obj["Transactions"] \
            .append(("TxCount", "ERR", "This token has less than 1000 transactions!"))
    elif result.get("countOps", 1) < 5000:
        return_obj["Transactions"] \
            .append(("TxCount", "WARN", "This token has less than 5000 transactions!"))
    else:
        return_obj["Transactions"] \
            .append(("TxCount", "OK", "This token has more than 5000 transactions!"))

    if result.get("holdersCount", 0) < 100:
        return_obj["Basic Metadata"] \
            .append(("holdersCount", "ERR", "This token has less than 100 holders!"))
    elif result.get("holdersCount", 1) < 500:
        return_obj["Basic Metadata"] \
            .append(("holdersCount", "WARN", "This token has less than 500 holders!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("holdersCount", "OK", "This token has more than 500 holders!"))

    if result.get("image", None) is None:
        return_obj["Basic Metadata"] \
            .append(("icon", "ERR", "This token has no icon data!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("icon", "OK", "This token has icon data!"))

    if result.get("is_mintable", 0) == 0:
        return_obj["Basic Metadata"] \
            .append(("mint", "ERR", "This token is mintable!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("mint", "OK", "This token is not mintable!"))

    list_of_problemable_word = ['test', 'testing', 'tested', 'malicious']
    listword_on_description: str = result.get('description', None)
    if listword_on_description is None:
        return_obj["Basic Metadata"] \
            .append(("decription", "ERR", "This token has no description!"))
    elif any(word in listword_on_description.split(' ') for word in list_of_problemable_word):
        return_obj["Basic Metadata"] \
            .append(("decription", "ERR", "This token has problematic description!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("decription", "OK", "This token has good description!"))

    if result.get('issuancesCount', 0) > 6:
        return_obj["Basic Metadata"] \
            .append(("issue", "ERR", "This token has more than 6 time issuance!"))
    elif result.get('issuancesCount', 0) > 1:
        return_obj["Basic Metadata"] \
            .append(("issue", "WARN", "This token has more than 1 time issuance!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("issue", "OK", "This token has issuanced exactly one time!"))

    if result.get('lastUpdated', 10000000000) > 60*60*24*10:  # 10 days
        return_obj["Basic Metadata"] \
            .append(("lastUpdated", "ERR", "This token has been updated more than 10 days ago!"))
    elif result.get('lastUpdated', 10000000000) > 60*60*24*3:  # 3 days
        return_obj["Basic Metadata"] \
            .append(("lastUpdated", "WARN", "This token has been updated more than 3 days ago!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("lastUpdated", "OK", "This token has been updated less than 3 days ago!"))

    if result.get('more_than_20', 0) == 1:
        return_obj["Basic Metadata"] \
            .append(("bigHolders", "ERR", "There's a holder hold more than 20% of total supply!"))
    elif result.get('more_than_10', 0) - result.get('more_than_20', 0) >= 1:
        return_obj["Basic Metadata"] \
            .append(("bigHolders", "WARN", "There's a holder hold 10-20% of total supply!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("bigHolders", "OK", "No holder each hold more than 10% of total supply!"))

    if result.get('more_than_5', 0) - result.get('more_than_10', 0) > 1:
        return_obj["Basic Metadata"] \
            .append(("5bigHolders", "ERR", "2 or more than 2 holders each hold 5-10% of total supply!"))
    elif result.get('more_than_5', 0) - result.get('more_than_10', 0) == 1:
        return_obj["Basic Metadata"] \
            .append(("5bigHolders", "WARN", "1 holder each hold 5-10% of total supply!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("5bigHolders", "OK", "No holder each hold 5-10% of total supply!"))

    if result.get('more_than_1', 0) - result.get('more_than_5', 0) > 4:
        return_obj["Basic Metadata"]\
            .append(("1bigHolders", "ERR", "5 or more than 5 holders each hold 1-5% of total supply!"))
    elif result.get('more_than_1', 0) - result.get('more_than_5', 0) >= 2:
        return_obj["Basic Metadata"] \
            .append(("1bigHolders", "WARN", "2 or more than 2 holders each hold 1-5% of total supply!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("1bigHolders", "OK", "1 or no holders at all each hold 1-5% of total supply!"))

    if result.get('price', None) is not None:
        return_obj["Price and Liquidity"] \
            .append(("price", "OK", "This token has some value!"))
    else:
        return_obj["Price and Liquidity"] \
            .append(("price", "ERR", "This token has no value!"))

    if result.get('price', None) is not None:
        if result['price'].get('diff', None) is None:
            return_obj["Price and Liquidity"] \
                .append(("diff", "ERR", "This token has no price data!"))
        elif result['price'].get('diff', None) < 0.0001:
            return_obj["Price and Liquidity"] \
                .append(("diff", "WARN", "This token has low diffentation in it price! Maybe this token has no transaction in recent time!"))
        elif result["price"].get('diff', None) > 0.05:
            return_obj["Price and Liquidity"] \
                .append(("diff", "ERR", "The price of the token has too much volatility!"))
        elif result["price"].get('diff', None) > 0.03:
            return_obj["Price and Liquidity"] \
                .append(("diff", "WARN", "This token has high diffentation in it price!"))
        else:
            return_obj["Price and Liquidity"] \
                .append(("diff", "OK", "This token has good diffentation in it price!"))

    if result.get('website', None) is not None:
        return_obj["Basic Metadata"] \
            .append(("web", "OK", "This token has website for it! But you also need to aware that maybe a scam website"))
    else:
        return_obj["Basic Metadata"] \
            .append(("web", "ERR", "This token has no website for it!"))

    if result.get('total_of_more_than_20') >= 50 or result.get('total_of_more_than_10') >= 50 \
            or result.get('total_of_more_than_5') >= 50 \
            or result.get('total_of_more_than_1') >= 50:
        return_obj["Basic Metadata"] \
            .append(("bigHold", "ERR", "There's a group of top holder hold more than 50% of total supply!"))
    elif result.get('total_of_more_than_20') >= 20 or result.get('total_of_more_than_10') >= 20 \
            or result.get('total_of_more_than_5') >= 20 \
            or result.get('total_of_more_than_1') >= 20:
        return_obj["Basic Metadata"] \
            .append(("bigHold", "WARN", "There's a group of top holder hold more than 20% of total supply!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("bigHold", "OK", "A group of top holder hold less than 20% of total supply!"))

    return return_obj


def get_other_of_eth_top_holder(token_address: str, chain: str):
    result = cova_scan.get_top_100_balance(chain, token_address)

    return_obj = {
        "Basic Metadata": [],
        "Price and Liquidity": [],
        "Transactions": []
    }

    if result.get('more_than_20', 0) == 1:
        return_obj["Basic Metadata"] \
            .append(("bigHolders", "ERR", "There's a holder hold more than 20% of total supply!"))
    elif result.get('more_than_10', 0) - result.get('more_than_20', 0) >= 1:
        return_obj["Basic Metadata"] \
            .append(("bigHolders", "WARN", "There's a holder hold 10-20% of total supply!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("bigHolders", "OK", "No holder each hold more than 10% of total supply!"))

    if result.get('more_than_5', 0) - result.get('more_than_10', 0) > 1:
        return_obj["Basic Metadata"] \
            .append(("5bigHolders", "ERR", "2 or more than 2 holders each hold 5-10% of total supply!"))
    elif result.get('more_than_5', 0) - result.get('more_than_10', 0) == 1:
        return_obj["Basic Metadata"] \
            .append(("5bigHolders", "WARN", "1 holder each hold 5-10% of total supply!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("5bigHolders", "OK", "No holder each hold 5-10% of total supply!"))

    if result.get('more_than_1', 0) - result.get('more_than_5', 0) > 4:
        return_obj["Basic Metadata"]\
            .append(("1bigHolders", "ERR", "5 or more than 5 holders each hold 1-5% of total supply!"))
    elif result.get('more_than_1', 0) - result.get('more_than_5', 0) >= 2:
        return_obj["Basic Metadata"] \
            .append(("1bigHolders", "WARN", "2 or more than 2 holders each hold 1-5% of total supply!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("1bigHolders", "OK", "1 or no holders at all each hold 1-5% of total supply!"))

    if result.get('total_of_more_than_20') >= 50 or result.get('total_of_more_than_10') >= 50 \
            or result.get('total_of_more_than_5') >= 50 \
            or result.get('total_of_more_than_1') >= 50:
        return_obj["Basic Metadata"] \
            .append(("bigHold", "ERR", "There's a group of top holder hold more than 50% of total supply!"))
    elif result.get('total_of_more_than_20') >= 20 or result.get('total_of_more_than_10') >= 20 \
            or result.get('total_of_more_than_5') >= 20 \
            or result.get('total_of_more_than_1') >= 20:
        return_obj["Basic Metadata"] \
            .append(("bigHold", "WARN", "There's a group of top holder hold more than 20% of total supply!"))
    else:
        return_obj["Basic Metadata"] \
            .append(("bigHold", "OK", "A group of top holder hold less than 20% of total supply!"))

    return return_obj
