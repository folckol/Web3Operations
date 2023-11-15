import threading
import time

from web3 import Web3
from web3.auto import w3

from utils import *

def send_eth(private_key, to_address, amount):


    gas_price = web3.eth.gas_price
    if chain == '4':
        gas = 1000000
    elif chain == '1':
        gas = 21000
    elif chain == '2':
        gas = 21000

    my_address = web3.eth.account.from_key(private_key).address

    if amount.lower() == 'all':
        amount = web3.eth.get_balance(my_address)
        # print(amount)

    nonce = web3.eth.get_transaction_count(my_address)

    txn = {
        'chainId': web3.eth.chain_id,
        'from': my_address,
        'to': web3.to_checksum_address(to_address),
        'value': amount-(gas * gas_price),
        'nonce': nonce,
        'gasPrice': gas_price,
        'gas': gas
    }

    # print(int(gas) * int(gas_price) + amount-(gas * gas_price))


    signed_txn = web3.eth.account.sign_transaction(txn, private_key)
    txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return txn_hash.hex()

def send_erc20(contract_address, private_key, to_address, amount):

    my_address = web3.eth.account.privateKeyToAccount(private_key).address

    if amount.lower() == 'all':
        amount = web3.eth.get_balance(my_address, web3.to_checksum_address(contract_address))

    dict_transaction = {
        'chainId': web3.eth.chain_id,
        'from': my_address,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(my_address),
    }

    contract = get_contract(web3, contract_address)
    decimals = contract.functions.decimals().call()
    balance_of_token = int_to_decimal(amount, decimals)

    transaction = contract.functions.transfer(
        web3.to_checksum_address(to_address), balance_of_token
    ).buildTransaction(dict_transaction)

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return txn_hash.hex()

if __name__ == '__main__':

    FromAddresses = []
    ToAddresses = []
    with open('AddressesTo.txt', 'r') as file:
        for i in file:
            ToAddresses.append(i.strip('\n'))
    with open('PrivatesFrom.txt', 'r') as file:
        for i in file:
            FromAddresses.append(i.strip('\n'))

    coin = input("Укажите актив, который будете перекидывать (номер монеты):\n\n"
                 "1 - ETH\n"
                 "2 - BNB\n"
                 "3 - USDT\n"
                 "4 - BUSD\n"
                 "5 - USDC\n\n")

    chain = input("Укажите сеть, в который будете перекидывать (номер сети):\n\n"
                  "1 - Ethereum\n"
                  "2 - Binance Smart Chain\n"
                  "3 - Optimism\n"
                  "4 - Arbitrum\n\n")

    # amount = input('Введите количество токенов для перевода: ')
    #
    # try:
    #     int(amount)
    # except:
    #     print('Введите количество числом')
    #     exit(1)

    if chain == '1':
        web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
    elif chain == '2':
        web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org'))
    elif chain == '3':
        web3 = Web3(Web3.HTTPProvider('https://endpoints.omniatech.io/v1/op/mainnet/public'))
    elif chain == '4':
        web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/arbitrum'))
    else:
        print('Неправильный код Сети')
        input()
        exit(1)

    if coin == '1':
        if chain == '1':
            contract_address = ''
        elif chain == '2':
            contract_address = '0x2170ed0880ac9a755fd29b2688956bd959f933f8'
        elif chain == '3':
            contract_address = ''
        elif chain == '4':
            contract_address = ''

    elif coin == '2':
        if chain == '1':
            contract_address = '0xb8c77482e45f1f44de1745f52c74426c631bdd52'
        elif chain == '2':
            contract_address = ''
        elif chain == '3':
            contract_address = ''
        elif chain == '4':
            contract_address = ''

    elif coin == '3':
        if chain == '1':
            contract_address = '0xdac17f958d2ee523a2206206994597c13d831ec7'
        elif chain == '2':
            contract_address = '0x55d398326f99059ff775485246999027b3197955'
        elif chain == '3':
            contract_address = '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58'
        elif chain == '4':
            contract_address = '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58'

    elif coin == '4':
        if chain == '1':
            contract_address = '0x4Fabb145d64652a948d72533023f6E7A623C7C53'
        elif chain == '2':
            contract_address = '0xe9e7cea3dedca5984780bafc599bd69add087d56'
        elif chain == '3':
            contract_address = ''
        elif chain == '4':
            contract_address = ''

    elif coin == '5':
        if chain == '1':
            contract_address = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
        elif chain == '2':
            contract_address = '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d'
        elif chain == '3':
            contract_address = '0x7f5c764cbc14f9669b88837ca1490cca17c31607'
        elif chain == '4':
            contract_address = '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8'

    else:
        print('Неправильный код Монеты')
        input()
        exit(1)

    amount = input('Введите значение перевода (all, если весь баланс): ')

    for i in range(len(FromAddresses)):

        try:
            if coin == '1':
                tx = send_eth(FromAddresses[i], ToAddresses[i], amount)
            elif coin == '2' and chain == '2':
                tx = send_eth(FromAddresses[i], ToAddresses[i], amount)
            else:
                tx = send_erc20(contract_address, FromAddresses[i], ToAddresses[i], amount)
        except:
            print(i, '-', 'Error')

        print(i, '-', tx)
        # input()
    input()